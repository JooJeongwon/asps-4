"""Run the fixed GCS-PULSE MCP/CLI comparison and write a redacted summary."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


SCENARIOS = ("A", "B", "C")


def parse_room_id(value):
    """Parse a room ID with an actionable error for empty shell variables."""
    if not value.strip():
        raise argparse.ArgumentTypeError(
            "room ID is empty; set ROOM_ID or pass a numeric --room-id"
        )
    try:
        room_id = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("room ID must be an integer") from exc
    if room_id <= 0:
        raise argparse.ArgumentTypeError("room ID must be positive")
    return room_id


def parse_nonempty(value):
    """Reject empty shell variables while preserving the supplied text."""
    if not value.strip():
        raise argparse.ArgumentTypeError(
            "value is empty; set the shell variable or pass a concrete value"
        )
    return value


def load_dotenv(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("\"'")
    return values


def prompt(mode, scenario, room_id, date, query, mcp_name):
    if scenario == "A":
        operation = "list every accessible meeting room"
        expected = '{"scenario":"A","rooms":[{"id":1,"name":"..."}]}'
        cli = "python3 -m pulse.cli meeting-rooms list"
        mcp = f'call the configured MCP server "{mcp_name}" tool meeting_rooms_list with {{}}'
    elif scenario == "B":
        operation = f"list reservations for room_id={room_id} on date={date}"
        expected = '{"scenario":"B","reservations":[{"id":1,"start_at":"...","end_at":"..."}]}'
        cli = f"python3 -m pulse.cli reservations list --room-id {room_id} --date {date}"
        mcp = f'call the configured MCP server "{mcp_name}" tool reservations_list with {json.dumps({"room_id": room_id, "date": date}, ensure_ascii=False)}'
    else:
        operation = f"search students for query {json.dumps(query, ensure_ascii=False)} with limit=20"
        expected = '{"scenario":"C","total":0,"items":[{"student_user_id":1,"student_name":"...","team_name":"..."}]}'
        cli = f"python3 -m pulse.cli students search --query {json.dumps(query, ensure_ascii=False)} --limit 20"
        mcp = f'call the configured MCP server "{mcp_name}" tool students_search with {json.dumps({"query": query, "limit": 20}, ensure_ascii=False)}'
    action = cli if mode == "CLI" else mcp
    return f"""Use GCS-PULSE for exactly one read-only operation: {operation}.
Use this access path only: {action}
Do not call another API or tool. Do not create, update, or delete anything. Do not print API tokens or student email addresses.
Normalize sorting by id for rooms and by start_at then id for reservations. Return exactly one compact JSON object, with no markdown or explanation, matching this shape: {expected}
The scenario letter must be {scenario}."""


def normalize_usage(value):
    if not isinstance(value, dict):
        return None
    input_tokens = value.get("input_tokens")
    output_tokens = value.get("output_tokens")
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        return None
    total_tokens = value.get("total_tokens")
    if not isinstance(total_tokens, int):
        total_tokens = input_tokens + output_tokens
    return {"input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens}


def usage_from(obj):
    if not isinstance(obj, dict):
        return None
    info = obj.get("info") if isinstance(obj.get("info"), dict) else None
    if info:
        value = info.get("last_token_usage") or info.get("total_token_usage")
        normalized = normalize_usage(value)
        if normalized:
            return normalized
    keys = ("turn_token_usage", "usage") if obj.get("type") == "token_usage_record" else ("usage", "last_token_usage", "turn_token_usage")
    for key in keys:
        normalized = normalize_usage(obj.get(key))
        if normalized:
            return normalized
    return None


def collect_json_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from collect_json_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from collect_json_objects(child)


def parse_jsonl(text):
    return [json.loads(line) for line in text.splitlines() if line.lstrip().startswith("{") and _is_json(line)]


def _is_json(line):
    try:
        json.loads(line)
    except json.JSONDecodeError:
        return False
    return True


def summarize(raw):
    objects = parse_jsonl(raw)
    selected = None
    priority = -1
    texts = []
    tool_calls = 0
    tool_errors = 0
    for root in objects:
        root_kind = root.get("type")
        root_item = root.get("item") if isinstance(root.get("item"), dict) else {}
        if root_kind == "item.started" and root_item.get("type") in {"tool_call", "mcp_tool_call", "function_call", "custom_tool_call", "command_execution", "CommandExecution"}:
            tool_calls += 1
        elif root_kind in {"tool_call", "function_call", "custom_tool_call", "command_execution", "CommandExecution"}:
            tool_calls += 1
        if root_kind == "item.completed" and root_item.get("type") in {"tool_call", "mcp_tool_call", "function_call", "custom_tool_call", "command_execution", "CommandExecution"} and (root_item.get("error") or root_item.get("status") == "failed"):
            tool_errors += 1
        for obj in collect_json_objects(root):
            kind = obj.get("type")
            if kind == "turn.completed" and usage_from(obj):
                selected, priority = usage_from(obj), 3
            elif kind == "token_usage_record" and usage_from(obj) and priority < 2:
                selected, priority = usage_from(obj), 2
            elif kind == "token_count" and usage_from(obj) and priority < 1:
                selected, priority = usage_from(obj), 1
            if kind == "message" and obj.get("role") == "assistant":
                for content in obj.get("content", []):
                    if isinstance(content, dict) and isinstance(content.get("text"), str):
                        texts.append(content["text"])
            if kind == "item.completed" and isinstance(obj.get("item"), dict) and obj["item"].get("type") == "agent_message":
                if isinstance(obj["item"].get("text"), str):
                    texts.append(obj["item"]["text"])
    canonical = None
    for text in reversed(texts):
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("scenario") in {"A", "B", "C"}:
            canonical = value
            break
    result_hash = None
    if canonical is not None:
        result_hash = hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
    return {
        "input_tokens": selected.get("input_tokens") if selected else None,
        "output_tokens": selected.get("output_tokens") if selected else None,
        "total_tokens": selected.get("total_tokens") if selected else None,
        "tool_calls": tool_calls,
        "tool_errors": tool_errors,
        "result_hash": result_hash,
        "success": canonical is not None and tool_errors == 0,
    }


def redact(text, secret, query):
    text = text.replace(secret, "<redacted-token>").replace(query, "<redacted-query>")
    text = re.sub(r'("student_email"\s*:\s*)"[^"]*"', r'\1"<redacted-email>"', text)
    text = re.sub(r'("student_name"\s*:\s*)"[^"]*"', r'\1"<redacted-student>"', text)
    return text


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def run_one(mode, scenario, args, env, run_dir, repeat):
    raw_path = run_dir / f"{mode.lower()}-{scenario}-{repeat}.jsonl"
    err_path = run_dir / f"{mode.lower()}-{scenario}-{repeat}.log"
    command = [
        "codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check",
        # Codex's legacy read-only sandbox blocks command networking. Both paths
        # use the same workspace-write sandbox with network enabled so CLI can
        # reach GCS; the prompt still permits exactly one read-only API call.
        "--sandbox", "workspace-write", "--color", "never", "--model", args.model,
        "-c", "sandbox_workspace_write.network_access=true",
        "-c", 'mcp_servers.gcs-pulse.default_tools_approval_mode="writes"',
        prompt(mode, scenario, args.room_id, args.date, args.query, args.mcp_name),
    ]
    started = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(
            command,
            cwd=args.cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=args.timeout_seconds,
        )
        raw = as_text(result.stdout)
        error_log = as_text(result.stderr)
        exit_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        raw = as_text(exc.stdout)
        error_log = as_text(exc.stderr)
        error_log += f"\nrunner timeout after {args.timeout_seconds}s\n"
        exit_code = None
    elapsed = time.monotonic() - started
    raw_path.write_text(redact(raw, env["PULSE_AUTH_VALUE"], args.query))
    err_path.write_text(redact(error_log, env["PULSE_AUTH_VALUE"], args.query))
    measured = summarize(raw)
    measured.update({
        "mode": mode,
        "scenario": scenario,
        "repeat": repeat,
        "seconds": round(elapsed, 3),
        "exit_code": exit_code,
        "error": "codex_exec_timeout" if timed_out else (None if exit_code == 0 and not measured["tool_errors"] else ("codex_exec_failed" if exit_code != 0 else f"{mode.lower()}_tool_failed")),
    })
    return measured


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--room-id", type=parse_room_id, required=True)
    parser.add_argument("--date", type=parse_nonempty, required=True, help="Fixed Asia/Seoul date, YYYY-MM-DD")
    parser.add_argument("--query", type=parse_nonempty, required=True, help="Fixed student search query")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--team", default="team-a")
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--mcp-name", default="gcs-pulse")
    parser.add_argument("--cwd", default=str(Path.cwd()))
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--output-root", default="runs")
    parser.add_argument("--timeout-seconds", type=float, default=120, help="Per Codex session timeout")
    args = parser.parse_args(argv)
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    if not dt.date.fromisoformat(args.date).isoformat() == args.date:
        parser.error("--date must be YYYY-MM-DD")
    env = os.environ.copy()
    env.update(load_dotenv(Path(args.env_file)))
    if not env.get("PULSE_AUTH_HEADER") or not env.get("PULSE_AUTH_VALUE"):
        parser.error(f"{args.env_file} must contain PULSE_AUTH_HEADER and PULSE_AUTH_VALUE")
    env["PYTHONPATH"] = str(Path(args.cwd).resolve()) + os.pathsep + env.get("PYTHONPATH", "")
    print("[준비] MCP 설정 확인 중", file=sys.stderr, flush=True)
    mcp_list = subprocess.run(["codex", "mcp", "list"], capture_output=True, text=True, check=False)
    if mcp_list.returncode != 0 or args.mcp_name not in mcp_list.stdout:
        parser.error(f'MCP server "{args.mcp_name}" is not configured; run codex mcp add first')
    run_id = dt.datetime.now(dt.timezone.utc).strftime("1-1-%Y%m%dT%H%M%SZ")
    run_dir = Path(args.output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    results = []
    total_runs = len(("MCP", "CLI")) * len(SCENARIOS) * args.repeats
    run_number = 0
    for mode in ("MCP", "CLI"):
        for scenario in SCENARIOS:
            for repeat in range(1, args.repeats + 1):
                run_number += 1
                print(
                    f"[{run_number}/{total_runs}] {mode} {scenario} 회차 {repeat} 시작",
                    file=sys.stderr,
                    flush=True,
                )
                row = run_one(mode, scenario, args, env, run_dir, repeat)
                results.append(row)
                print(
                    f"[{run_number}/{total_runs}] {mode} {scenario} 회차 {repeat} "
                    f"완료: success={row['success']} seconds={row['seconds']} error={row['error'] or '-'}",
                    file=sys.stderr,
                    flush=True,
                )
    summary = {
        "run_id": run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "team": args.team,
        "codex_model": args.model,
        "codex_version": subprocess.run(["codex", "--version"], capture_output=True, text=True, check=False).stdout.strip(),
        "fixed_inputs": {"room_id": args.room_id, "date": args.date, "query_sha256": hashlib.sha256(args.query.encode()).hexdigest()[:16], "query_length": len(args.query)},
        "results": results,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    for row in results:
        print(json.dumps({k: row[k] for k in ("mode", "scenario", "repeat", "input_tokens", "output_tokens", "seconds", "tool_calls", "tool_errors", "result_hash", "success", "exit_code", "error")}, ensure_ascii=False))
    print(f"summary={run_dir / 'summary.json'}")
    return 0 if all(row["success"] and row["exit_code"] == 0 for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
