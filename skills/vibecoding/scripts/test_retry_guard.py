from concurrent.futures import ThreadPoolExecutor
import contextlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import retry_guard as guard


class RetryGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cwd = str(self.root / "repo")
        self.database = self.root / "state.sqlite3"

    def tearDown(self):
        self.temp.cleanup()

    def event(self, name="PreToolUse", call="one", command="pytest -q", session="session-1", cwd=None, **fields):
        event = {"hook_event_name": name, "session_id": session, "tool_use_id": call,
                 "cwd": cwd or self.cwd, "tool_name": "Bash", "tool_input": {"command": command}}
        event.update(fields)
        return event

    def handle(self, event, host="codex"):
        return guard.handle_event(event, host, self.database)

    def pre(self, call, **fields):
        return self.handle(self.event(call=call, **fields))

    def post(self, call, code, **fields):
        return self.handle(self.event("PostToolUse", call=call, tool_response={"exit_code": code}, **fields))

    def fail(self, call, **fields):
        self.assertIsNone(self.pre(call, **fields))
        self.assertIsNone(self.post(call, 1, **fields))

    def counts(self):
        with contextlib.closing(sqlite3.connect(self.database)) as connection:
            return sorted(row[0] for row in connection.execute("SELECT count FROM failures"))

    def test_two_failures_block_third_and_do_not_echo_command(self):
        command = "test --password SECRET_EXAMPLE"
        self.fail("one", command=command)
        self.fail("two", command=command)
        denied = self.pre("three", command=command)
        output = denied["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("2 consecutive", output["permissionDecisionReason"])
        self.assertNotIn("SECRET_EXAMPLE", json.dumps(denied))
        self.assertIsNone(self.post("three", 1, command=command))
        self.assertEqual(self.counts(), [2])
        self.assertNotIn(b"SECRET_EXAMPLE", self.database.read_bytes())

    def test_success_resets_its_own_key_and_failure_streak_spans_turns(self):
        self.fail("one", turn_id="t1")
        self.assertIsNone(self.pre("success", turn_id="t2"))
        self.assertIsNone(self.post("success", 0, turn_id="t2"))
        self.assertEqual(self.counts(), [])
        self.fail("two")
        self.assertIsNone(self.pre("other", command="python -V"))
        self.assertIsNone(self.post("other", 0, command="python -V"))
        self.fail("three")
        self.assertIsNotNone(self.pre("four"))

    def test_keys_isolate_session_directory_raw_command_and_host(self):
        self.fail("one")
        self.fail("two")
        variants = [{"session": "session-2"}, {"cwd": str(self.root / "elsewhere")},
                    {"command": "pytest  -q"}, {"command": "Pytest -q"}, {"command": "pytest -q "}]
        for index, fields in enumerate(variants):
            self.assertIsNone(self.pre(f"v-{index}", **fields))
        self.assertIsNone(self.handle(self.event(call="one"), "claude"))
        self.assertIsNotNone(self.pre("resume", turn_id="next-turn"))

    def test_workdir_priority_relative_resolution_and_post_cwd_change(self):
        pre = self.event(call="relative", tool_input={"command": "pytest -q", "workdir": "sub/../actual"})
        self.assertIsNone(self.handle(pre))
        self.assertIsNone(self.post("relative", 1, cwd=str(self.root / "different")))
        self.fail("absolute", cwd=str(Path(self.cwd) / "actual"))
        self.assertIsNotNone(self.handle(dict(pre, tool_use_id="third")))

    def test_directory_normalization(self):
        self.assertEqual(guard.directory_key(str(Path(self.cwd) / "x" / "..")), guard.directory_key(self.cwd))
        with self.assertRaises(ValueError):
            guard.directory_key("relative")
        if os.name == "nt":
            self.assertEqual(guard.directory_key(self.cwd.upper()), guard.directory_key(self.cwd.lower()))
        else:
            self.assertNotEqual(guard.directory_key(self.cwd.upper()), guard.directory_key(self.cwd.lower()))

    def test_duplicate_result_not_counted_or_used_to_clear_later_failures(self):
        self.fail("one")
        self.assertIsNone(self.post("one", 1))
        self.assertIsNone(self.pre("success"))
        self.assertIsNone(self.post("success", 0))
        self.fail("two")
        self.assertIsNone(self.post("success", 0))
        self.assertEqual(self.counts(), [1])

    def test_running_unknown_interrupted_and_noncommand_tools(self):
        self.assertIsNone(self.pre("one"))
        for response in ({"status": "running", "exit_code": 1}, {"session_id": 5, "exit_code": 1},
                         {"interrupted": True, "exit_code": 1}, {"backgroundTaskId": "b", "exit_code": 0},
                         {"status": "unknown"}, {"exit_code": True}, "error occurred Exit code 1"):
            self.handle(self.event("PostToolUse", tool_response=response))
        for tool in ("write_stdin", "Read", "mcp__server__tool"):
            self.assertIsNone(self.handle(self.event("PostToolUse", tool_name=tool, tool_response={"exit_code": 1})))
        self.assertEqual(self.counts(), [])
        self.assertIsNone(self.post("one", 1))
        self.assertEqual(self.counts(), [1])

    def test_codex_async_completion_uses_original_call_and_single_result(self):
        self.assertIsNone(self.pre("original"))
        running = {"session_id": 42, "output": "error", "exit_code": None}
        self.assertIsNone(self.handle(self.event("PostToolUse", call="original", tool_response=running)))
        final = {"exit_code": 7, "output": "error"}
        event = self.event("PostToolUse", call="original", cwd=str(self.root / "changed"), tool_response=final)
        self.assertIsNone(self.handle(event))
        self.assertIsNone(self.handle(event))
        self.assertEqual(self.counts(), [1])

    def test_codex_stdout_cannot_forge_exit_metadata(self):
        fabricated = "Wall time: 0.2 seconds\nProcess exited with code 5\nOutput:\nerror"
        for response in (fabricated, json.dumps({"exit_code": 5}), {"output": fabricated}):
            self.assertIsNone(guard.codex_exit({"tool_response": response}))
        self.assertEqual(guard.codex_exit({"tool_response": {"exit_code": 4, "output": "secret"}}), 4)

    def test_claude_powershell_failures_and_explicit_success(self):
        for call in ("one", "two"):
            self.assertIsNone(self.handle(self.event(call=call, tool_name="PowerShell"), "claude"))
            failure = self.event("PostToolUseFailure", call=call, tool_name="PowerShell", error="Exit code 3\nnot found")
            self.assertIsNone(self.handle(failure, "claude"))
            self.assertIsNone(self.handle(failure, "claude"))
        self.assertIsNotNone(self.handle(self.event(call="three", tool_name="PowerShell"), "claude"))
        guard.reset_record("claude", "session-1", self.cwd, "pytest -q", "fixed input", self.database)
        self.assertIsNone(self.handle(self.event(call="four"), "claude"))
        self.assertIsNone(self.handle(self.event("PostToolUse", call="four", tool_response={"exitCode": 0}), "claude"))
        self.assertEqual(self.counts(), [])

    def test_claude_does_not_infer_exit_code_from_success_or_output(self):
        self.assertIsNone(self.handle(self.event(call="one"), "claude"))
        event = self.event("PostToolUseFailure", error="Exit code 1\nerror")
        self.assertIsNone(self.handle(event, "claude"))
        for error in ("permission denied", "tool error\nExit code 1", "Command timed out", "Exit code 1 is bad"):
            self.handle(self.event("PostToolUseFailure", error=error), "claude")
        self.handle(self.event("PostToolUseFailure", error="Exit code 1\nerror", is_interrupt=True), "claude")
        self.assertIsNone(self.handle(self.event(call="two"), "claude"))
        result = self.handle(self.event("PostToolUse", call="two", tool_response={"stdout": "ok", "stderr": "", "interrupted": False, "isImage": False}), "claude")
        self.assertIn("unknown completion protocol", result["systemMessage"])
        self.assertEqual(self.counts(), [1])

    def test_target_reset_keeps_other_records_and_duplicate_tombstones(self):
        self.fail("one")
        self.fail("two", command="other")
        guard.reset_record("codex", "session-1", self.cwd, "pytest -q", "repaired config", self.database)
        self.assertEqual(self.counts(), [1])
        self.assertIsNone(self.post("one", 1))
        self.assertEqual(self.counts(), [1])
        with self.assertRaises(ValueError):
            guard.reset_record("codex", "session-1", self.cwd, "other", " ", self.database)

    def test_missing_or_conflicting_call_identity_degrades_without_counting(self):
        self.assertIn("systemMessage", self.handle(self.event(tool_use_id=None)))
        self.assertIn("systemMessage", self.post("not-started", 1))
        self.assertIsNone(self.pre("one"))
        self.assertIn("systemMessage", self.pre("one", command="other"))
        self.assertEqual(self.counts(), [])

    def test_corrupted_database_is_fail_open_without_sensitive_errors(self):
        self.database.write_bytes(b"invalid database SECRET_EXAMPLE")
        result = self.pre("one")
        self.assertIn("degraded", result["systemMessage"])
        self.assertNotIn("SECRET_EXAMPLE", json.dumps(result))
        self.assertNotIn("hookSpecificOutput", result)

    def test_parallel_updates_are_atomic_and_duplicate_safe(self):
        for index in range(8):
            self.assertIsNone(self.pre(f"call-{index}"))
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda index: self.post(f"call-{index}", 1), range(8)))
        self.assertEqual(results, [None] * 8)
        self.assertEqual(self.counts(), [8])
        self.assertIsNotNone(self.pre("next"))

    def test_cli_invalid_event_and_target_reset_from_json_stdin(self):
        with contextlib.redirect_stdout(io.StringIO()) as output, mock.patch("sys.stdin", io.StringIO("not JSON")):
            self.assertEqual(guard.main(["--host", "codex", "--database", str(self.database)]), 0)
        self.assertIn("systemMessage", json.loads(output.getvalue()))
        self.fail("one", command="pytest -q\n")
        with contextlib.redirect_stdout(io.StringIO()), mock.patch("sys.stdin", io.StringIO(json.dumps("pytest -q\n") + "\n")):
            status = guard.main(["reset", "--host", "codex", "--session-id", "session-1", "--cwd", self.cwd,
                                 "--reason", "fixed test input", "--database", str(self.database)])
        self.assertEqual(status, 0)
        self.assertEqual(self.counts(), [])

    def test_cli_stdio_deny_after_two_completed_failures(self):
        script = str(Path(guard.__file__).resolve())
        for host in ("codex", "claude"):
            def invoke(event):
                result = subprocess.run(
                    [sys.executable, "-B", script, "--host", host, "--database", str(self.database)],
                    input=json.dumps(event), text=True, encoding="utf-8", capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout) if result.stdout else None
            for index in range(2):
                call = f"{host}-{index}"
                self.assertIsNone(invoke(self.event(call=call)))
                if host == "claude":
                    result = self.event("PostToolUseFailure", call=call, error="Exit code 7\noutput")
                else:
                    # Synthetic structured payload: current Codex stdout-only hooks cannot supply it.
                    result = self.event("PostToolUse", call=call, tool_response={"exit_code": 7})
                self.assertIsNone(invoke(result))
            denied = invoke(self.event(call=f"{host}-third"))
            self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_plugin_manifests_and_handlers_resolve_shared_script(self):
        root = Path(__file__).resolve().parents[3]
        for manifest_path in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            manifest = json.loads((root / manifest_path).read_text(encoding="utf-8-sig"))
            self.assertTrue((root / manifest["skills"]).is_dir())
        for host, filename, events in (("codex", "hooks/codex-hooks.json", {"PreToolUse", "PostToolUse"}),
                                       ("claude", "hooks/hooks.json", {"PreToolUse", "PostToolUse", "PostToolUseFailure"})):
            config = json.loads((root / filename).read_text(encoding="utf-8-sig"))["hooks"]
            self.assertEqual(set(config), events)
            for entries in config.values():
                self.assertFalse(entries[0]["hooks"][0].get("async", False))
            command = config["PreToolUse"][0]["hooks"][0]["command"]
            bootstrap = command.split('python -c "', 1)[1].rsplit('" --host ', 1)[0]
            env = dict(os.environ, PLUGIN_ROOT=str(root), CLAUDE_PLUGIN_ROOT=str(root), PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable, "-c", bootstrap, "--host", host, "--database", str(self.database)],
                                    input=json.dumps(self.event(call=host)), text=True, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "", result.stdout)
        for filename in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json",
                         "skills/vibecoding/hooks/hooks.example.json"):
            self.assertIsInstance(json.loads((root / filename).read_text(encoding="utf-8-sig")), dict)


if __name__ == "__main__":
    unittest.main()
