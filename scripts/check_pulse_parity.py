"""Compare the three read-only CLI and MCP calls without printing API data."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from scripts.run_1_1_comparison import load_dotenv


def run_cli(arguments, env):
    result = subprocess.run(
        [sys.executable, "-m", "pulse.cli", *arguments],
        capture_output=True, text=True, check=False, env=env,
    )
    if result.returncode:
        raise RuntimeError("CLI call failed; run it separately to inspect the error")
    return json.loads(result.stdout)


def run_mcp(calls, env):
    messages = [
        {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "parity-check", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]
    messages += [{"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}} for i, (name, args) in enumerate(calls, 1)]
    result = subprocess.run(
        [sys.executable, "-m", "pulse.mcp"],
        input="".join(json.dumps(message) + "\n" for message in messages),
        capture_output=True, text=True, check=False, env=env,
    )
    if result.returncode:
        raise RuntimeError("MCP process failed")
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    if len(responses) != len(calls) + 1 or responses[0].get("id") != 0 or "error" in responses[0]:
        raise RuntimeError("MCP initialize failed")
    values = []
    for i, response in enumerate(responses[1:], 1):
        if response.get("id") != i or "error" in response or response.get("result", {}).get("isError"):
            raise RuntimeError(f"MCP call {i} failed")
        values.append(json.loads(response["result"]["content"][0]["text"]))
    return values


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--room-id", type=int, required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD in Asia/Seoul")
    parser.add_argument("--query", required=True)
    args = parser.parse_args(argv)
    env = os.environ.copy()
    env.update(load_dotenv(Path(".env")))
    if not env.get("PULSE_AUTH_HEADER") or not env.get("PULSE_AUTH_VALUE"):
        parser.error(".env must contain PULSE_AUTH_HEADER and PULSE_AUTH_VALUE")
    scenarios = [
        ("rooms", ["meeting-rooms", "list"], ("meeting_rooms_list", {})),
        ("reservations", ["reservations", "list", "--room-id", str(args.room_id), "--date", args.date], ("reservations_list", {"room_id": args.room_id, "date": args.date})),
        ("students", ["students", "search", "--query", args.query], ("students_search", {"query": args.query})),
    ]
    try:
        cli_values = [run_cli(command, env) for _, command, _ in scenarios]
        mcp_values = run_mcp([call for _, _, call in scenarios], env)
    except (RuntimeError, ValueError, KeyError, IndexError) as exc:
        print(f"parity check failed: {exc}", file=sys.stderr)
        return 1
    for (name, _, _), left, right in zip(scenarios, cli_values, mcp_values):
        print(f"{name}: {'match' if left == right else 'mismatch'}")
    return 0 if cli_values == mcp_values else 1


if __name__ == "__main__":
    raise SystemExit(main())
