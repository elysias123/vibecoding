"""Exact-command retry guard for Codex and Claude Code command hooks."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile


LIMIT = 2
DEFAULT_DATABASE = Path(tempfile.gettempdir()) / "vibecoding-retry-guard" / "state.sqlite3"


def digest(*parts):
    return hashlib.sha256(json.dumps(parts, ensure_ascii=True).encode("utf-8")).hexdigest()


def directory_key(directory, base=None):
    if not isinstance(directory, str) or not directory:
        raise ValueError("missing working directory")
    if not os.path.isabs(directory):
        if not isinstance(base, str) or not os.path.isabs(base):
            raise ValueError("missing absolute working directory")
        directory = os.path.join(base, directory)
    return os.path.normcase(os.path.realpath(directory))


def command_key(host, session_id, directory, command):
    if host not in ("codex", "claude"):
        raise ValueError("unsupported host")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("missing session id")
    if not isinstance(command, str) or not command:
        raise ValueError("missing command")
    return digest(host, session_id, directory, command)


def warning(code):
    return {"systemMessage": "Retry guard degraded: " + code + "; this event was not enforced or counted."}


def denial(count, exit_code):
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"The same command has failed {count} consecutive times (last exit code {exit_code}). "
            "Analyze the original error or change the execution method. After a concrete fix or an "
            "explicit retry request, reset only this command's record with a reason."
        ),
    }}


def open_database(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=2)
    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS failures (
                command_key TEXT PRIMARY KEY,
                count INTEGER NOT NULL,
                exit_code INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS calls (
                call_key TEXT PRIMARY KEY,
                command_key TEXT NOT NULL,
                allowed INTEGER NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            );
        """)
    except sqlite3.Error:
        connection.close()
        raise
    return connection


def explicit_exit(response):
    """Only accept host metadata, never scan stdout or stderr for failures."""
    if not isinstance(response, dict):
        return None
    if response.get("interrupted") or response.get("is_interrupt"):
        return None
    if response.get("status") in ("running", "pending", "unknown"):
        return None
    if any(response.get(field) is not None for field in ("session_id", "backgroundTaskId", "task_id")):
        return None
    for field in ("exit_code", "exitCode"):
        value = response.get(field)
        if type(value) is int:
            return value
    return None


def codex_exit(event):
    # Codex versions returning only stdout cannot expose a trustworthy exit code.
    return explicit_exit(event.get("tool_response"))


def claude_exit(event):
    if event.get("is_interrupt"):
        return None
    if event["hook_event_name"] == "PostToolUseFailure":
        error = event.get("error")
        if not isinstance(error, str):
            return None
        match = re.match(r"\AExit code (-?\d+)(?:\r?\n|\Z)", error)
        return int(match[1]) if match and int(match[1]) != 0 else None
    return explicit_exit(event.get("tool_response"))


def running_result(event):
    response = event.get("tool_response")
    if event.get("is_interrupt"):
        return True
    if isinstance(response, dict):
        return bool(response.get("interrupted") or response.get("is_interrupt") or
                    response.get("status") in ("running", "pending") or
                    any(response.get(field) is not None
                        for field in ("session_id", "backgroundTaskId", "task_id")))
    return False


def handle_event(event, host, database=DEFAULT_DATABASE):
    """Normalize the host event, then apply the shared transactional counter."""
    try:
        if not isinstance(event, dict):
            raise ValueError("invalid event")
        tools = {"codex": ("Bash",), "claude": ("Bash", "PowerShell")}
        if host not in tools:
            raise ValueError("unsupported host")
        if event.get("tool_name") not in tools[host]:
            return None
        name = event.get("hook_event_name")
        supported = ("PreToolUse", "PostToolUse", "PostToolUseFailure") if host == "claude" else ("PreToolUse", "PostToolUse")
        if name not in supported:
            return None
        session = event.get("session_id")
        call_id = event.get("tool_use_id")
        if not isinstance(session, str) or not session or not isinstance(call_id, str) or not call_id:
            raise ValueError("missing invocation identity")
        call = digest(host, session, call_id)
        if name == "PreToolUse":
            inputs = event.get("tool_input")
            if not isinstance(inputs, dict):
                raise ValueError("invalid command input")
            raw_directory = inputs.get("workdir") or inputs.get("cwd") or event.get("cwd")
            directory = directory_key(raw_directory, event.get("cwd"))
            key = command_key(host, session, directory, inputs.get("command"))
            exit_code = None
        else:
            exit_code = codex_exit(event) if host == "codex" else claude_exit(event)
            if exit_code is None:
                return None if running_result(event) else warning("unknown completion protocol")
        connection = open_database(database)
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                if name == "PreToolUse":
                    previous = connection.execute("SELECT command_key FROM calls WHERE call_key=?", (call,)).fetchone()
                    if previous and previous[0] != key:
                        raise ValueError("conflicting invocation identity")
                    row = connection.execute("SELECT count, exit_code FROM failures WHERE command_key=?", (key,)).fetchone()
                    blocked = row is not None and row[0] >= LIMIT
                    connection.execute(
                        "INSERT INTO calls(call_key,command_key,allowed) VALUES(?,?,?) "
                        "ON CONFLICT(call_key) DO UPDATE SET allowed=excluded.allowed", (call, key, int(not blocked)))
                    return denial(*row) if blocked else None
                row = connection.execute("SELECT command_key,allowed,completed FROM calls WHERE call_key=?", (call,)).fetchone()
                if row is None:
                    return warning("missing original invocation")
                key, allowed, completed = row
                if not allowed or completed:
                    return None
                if exit_code == 0:
                    connection.execute("DELETE FROM failures WHERE command_key=?", (key,))
                else:
                    connection.execute(
                        "INSERT INTO failures(command_key,count,exit_code) VALUES(?,1,?) "
                        "ON CONFLICT(command_key) DO UPDATE SET count=count+1,exit_code=excluded.exit_code", (key, exit_code))
                connection.execute("UPDATE calls SET completed=1 WHERE call_key=?", (call,))
        finally:
            connection.close()
        return None
    except (ValueError, TypeError, OSError, sqlite3.Error) as error:
        return warning(type(error).__name__)


def reset_record(host, session_id, directory, command, reason, database=DEFAULT_DATABASE):
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reset requires a repair reason or explicit retry request")
    key = command_key(host, session_id, directory_key(directory), command)
    connection = open_database(database)
    try:
        with connection:
            # Keep completion tombstones so delayed duplicate results cannot restore old failures.
            connection.execute("DELETE FROM failures WHERE command_key=?", (key,))
    finally:
        connection.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=("reset", "path"))
    parser.add_argument("--host", choices=("codex", "claude"))
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--session-id")
    parser.add_argument("--cwd")
    parser.add_argument("--reason")
    args = parser.parse_args(argv)
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if args.action == "path":
        print(args.database)
        return 0
    if not args.host:
        parser.error("--host is required")
    try:
        raw = sys.stdin.read()
        if args.action == "reset":
            try:
                command = json.loads(raw)
            except ValueError:
                command = raw
            if not isinstance(command, str):
                command = raw
            reset_record(args.host, args.session_id, args.cwd, command, args.reason, args.database)
            print("Retry guard: target record reset.")
        else:
            result = handle_event(json.loads(raw), args.host, args.database)
            if result:
                print(json.dumps(result, ensure_ascii=True))
    except (ValueError, TypeError, OSError, sqlite3.Error) as error:
        if args.action == "reset":
            print("Retry guard reset failed: " + type(error).__name__, file=sys.stderr)
            return 1
        print(json.dumps(warning(type(error).__name__)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
