"""Narrow stdio MCP server, legacy 2025-11-25 handshake for Codex compatibility."""

import json
import sys

from pulse.client import PulseError, meeting_rooms, reservations, students


READ_ONLY = {"readOnlyHint": True, "destructiveHint": False}

TOOLS = [
    {"name": "meeting_rooms_list", "description": "List GCS-PULSE meeting rooms", "inputSchema": {"type": "object", "properties": {}}, "annotations": READ_ONLY},
    {"name": "reservations_list", "description": "List reservations on one date", "inputSchema": {"type": "object", "properties": {"room_id": {"type": "integer"}, "date": {"type": "string"}}, "required": ["room_id", "date"]}, "annotations": READ_ONLY},
    {"name": "students_search", "description": "Search students; email is omitted", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 20}}, "required": ["query"]}, "annotations": READ_ONLY},
]


def handle(message):
    method = message.get("method")
    if method == "initialize":
        version = message.get("params", {}).get("protocolVersion", "2025-11-25")
        if version not in ("2025-11-25", "2025-06-18"):
            version = "2025-11-25"
        return {"protocolVersion": version, "capabilities": {"tools": {}}, "serverInfo": {"name": "gcs-pulse-readonly", "version": "0.1.0"}}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        params = message.get("params", {})
        name, args = params.get("name"), params.get("arguments", {})
        if not isinstance(args, dict):
            raise PulseError("invalid_input", "Tool arguments must be an object")
        try:
            if name == "meeting_rooms_list":
                result = meeting_rooms()
            elif name == "reservations_list":
                result = reservations(args.get("room_id"), args.get("date"))
            elif name == "students_search":
                result = students(args.get("query"), args.get("limit", 20))
            else:
                raise PulseError("invalid_input", "Unknown tool")
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
        except PulseError as exc:
            return {"content": [{"type": "text", "text": json.dumps({"error": exc.kind, "message": str(exc)})}], "isError": True}
    raise PulseError("invalid_input", "Unknown method")


def main():
    for line in sys.stdin:
        message = None
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise PulseError("invalid_input", "Expected a JSON-RPC object")
            if "id" not in message:  # notifications/initialized and other notifications
                continue
            result = {"jsonrpc": "2.0", "id": message["id"], "result": handle(message)}
        except (ValueError, TypeError, PulseError) as exc:
            result = {"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None, "error": {"code": -32602, "message": str(exc)}}
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
