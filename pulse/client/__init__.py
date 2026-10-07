"""Shared GCS-PULSE HTTP client."""

import datetime as dt
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request


class PulseError(Exception):
    def __init__(self, kind, message):
        self.kind = kind
        super().__init__(message)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise PulseError("network_uncertain", "Redirect refused; check the configured API URL")


def _local_env():
    values = {}
    candidates = [Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"]
    for path in candidates:
        try:
            lines = path.read_text().splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                values.setdefault(key.strip(), value)
    return values


def _request(path, query=None, method="GET", body=None, base_url=None, auth_header=None, auth_value=None):
    local_env = _local_env()
    base_url = base_url or os.environ.get("PULSE_BASE_URL") or local_env.get("PULSE_BASE_URL", "https://api.1000.school")
    auth_header = auth_header or os.environ.get("PULSE_AUTH_HEADER") or local_env.get("PULSE_AUTH_HEADER")
    auth_value = auth_value or os.environ.get("PULSE_AUTH_VALUE") or local_env.get("PULSE_AUTH_VALUE")
    if not auth_header or not auth_value:
        raise PulseError("auth_config", "Set PULSE_AUTH_HEADER and PULSE_AUTH_VALUE from verified service instructions")
    if not re.fullmatch(r"[A-Za-z0-9-]+", auth_header):
        raise PulseError("auth_config", "Invalid PULSE_AUTH_HEADER")
    if not base_url.startswith("https://") and not base_url.startswith("http://127.0.0.1:"):
        raise PulseError("auth_config", "PULSE_BASE_URL must use HTTPS (or localhost for tests)")
    url = base_url.rstrip("/") + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    payload = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        url,
        data=payload,
        headers={auth_header: auth_value, "Accept": "application/json", "User-Agent": "gcs-pulse-client/0.1", **({"Content-Type": "application/json"} if payload is not None else {})},
        method=method,
    )
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=10) as response:
            if response.status != 200:
                raise PulseError("http_error", f"Unexpected HTTP {response.status}")
            if "application/json" not in response.headers.get("Content-Type", ""):
                raise PulseError("invalid_response", "Expected JSON response")
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        kind = {400: "invalid_input", 401: "auth_failed", 403: "forbidden", 404: "not_found", 409: "conflict", 422: "invalid_input"}.get(exc.code, "http_error")
        detail = _http_detail(exc)
        raise PulseError(kind, f"HTTP {exc.code}" + (f": {detail}" if detail else "")) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise PulseError("network_uncertain", type(exc).__name__) from None
    except (UnicodeError, json.JSONDecodeError):
        raise PulseError("invalid_response", "Malformed JSON response") from None
    return data


def _fields(item, fields):
    if not isinstance(item, dict) or any(name not in item or not isinstance(item[name], kind) or (kind is int and isinstance(item[name], bool)) for name, kind in fields.items()):
        raise PulseError("invalid_response", "Missing or invalid response field")


def _http_detail(exc):
    try:
        payload = json.load(exc)
    except (UnicodeError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    detail = payload.get("detail") or payload.get("message")
    return " ".join(detail.split())[:200] if isinstance(detail, str) else None


def auth_me(**kwargs):
    data = _request("/auth/me", **kwargs)
    if not isinstance(data, dict) or not isinstance(data.get("authenticated"), bool):
        raise PulseError("invalid_response", "Invalid auth status response")
    if not data["authenticated"]:
        raise PulseError("auth_failed", "API reports unauthenticated")
    return {"authenticated": True}


def meeting_rooms(**kwargs):
    data = _request("/meeting-rooms", **kwargs)
    if not isinstance(data, list):
        raise PulseError("invalid_response", "Expected room list")
    for item in data:
        _fields(item, {"id": int, "name": str, "created_at": str, "updated_at": str})
        if item.get("location") is not None and not isinstance(item["location"], str):
            raise PulseError("invalid_response", "Invalid room location")
    return [{"id": item["id"], "name": item["name"], "location": item.get("location")} for item in data]


def reservations(room_id, date, **kwargs):
    if isinstance(room_id, bool) or not isinstance(room_id, int) or room_id <= 0:
        raise PulseError("invalid_input", "room_id must be a positive integer")
    try:
        if dt.date.fromisoformat(date).isoformat() != date:
            raise ValueError
    except (TypeError, ValueError):
        raise PulseError("invalid_input", "date must be YYYY-MM-DD") from None
    data = _request(f"/meeting-rooms/{room_id}/reservations", {"date": date}, **kwargs)
    if not isinstance(data, list):
        raise PulseError("invalid_response", "Expected reservation list")
    result = []
    for item in data:
        _fields(item, {"id": int, "meeting_room_id": int, "reserved_by_user_id": int, "start_at": str, "end_at": str, "created_at": str, "updated_at": str})
        if item["meeting_room_id"] != room_id:
            raise PulseError("invalid_response", "Reservation belongs to another room")
        times = []
        for key in ("start_at", "end_at"):
            try:
                value = dt.datetime.fromisoformat(item[key])
                if value.utcoffset() is None:
                    raise ValueError
                times.append(value)
            except ValueError:
                raise PulseError("invalid_response", "Reservation time needs an explicit offset") from None
        if times[0] >= times[1]:
            raise PulseError("invalid_response", "Reservation end must follow start")
        value = {key: item[key] for key in ("id", "meeting_room_id", "start_at", "end_at")}
        if "can_cancel" in item:
            if not isinstance(item["can_cancel"], bool):
                raise PulseError("invalid_response", "Invalid reservation can_cancel")
            value["can_cancel"] = item["can_cancel"]
        result.append(value)
    return result


def _reservation_times(start_at, end_at):
    values = []
    for value in (start_at, end_at):
        try:
            parsed = dt.datetime.fromisoformat(value)
            if parsed.utcoffset() is None:
                raise ValueError
        except (TypeError, ValueError):
            raise PulseError("invalid_input", "Reservation times need an explicit offset") from None
        values.append(parsed)
    if values[0] >= values[1]:
        raise PulseError("invalid_input", "Reservation end must follow start")
    return values


def create_reservation(room_id, start_at, end_at, purpose=None, **kwargs):
    if isinstance(room_id, bool) or not isinstance(room_id, int) or room_id <= 0:
        raise PulseError("invalid_input", "room_id must be a positive integer")
    _reservation_times(start_at, end_at)
    if purpose is not None and not isinstance(purpose, str):
        raise PulseError("invalid_input", "purpose must be a string")
    data = _request(
        f"/meeting-rooms/{room_id}/reservations",
        method="POST",
        body={"start_at": start_at, "end_at": end_at, "purpose": purpose},
        **kwargs,
    )
    _fields(data, {"id": int, "meeting_room_id": int, "reserved_by_user_id": int, "start_at": str, "end_at": str, "created_at": str, "updated_at": str})
    if data["meeting_room_id"] != room_id:
        raise PulseError("invalid_response", "Reservation belongs to another room")
    _reservation_times(data["start_at"], data["end_at"])
    if "can_cancel" in data and not isinstance(data["can_cancel"], bool):
        raise PulseError("invalid_response", "Invalid reservation can_cancel")
    return {
        "id": data["id"],
        "meeting_room_id": data["meeting_room_id"],
        "start_at": data["start_at"],
        "end_at": data["end_at"],
        "purpose": data.get("purpose"),
        "can_cancel": data.get("can_cancel", False),
    }


def cancel_reservation(reservation_id, **kwargs):
    if isinstance(reservation_id, bool) or not isinstance(reservation_id, int) or reservation_id <= 0:
        raise PulseError("invalid_input", "reservation_id must be a positive integer")
    data = _request(f"/meeting-rooms/reservations/{reservation_id}", method="DELETE", **kwargs)
    _fields(data, {"message": str})
    return {"message": data["message"]}


def students(query, limit=20, include_email=False, **kwargs):
    if not isinstance(query, str) or not query.strip() or isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise PulseError("invalid_input", "Provide a nonempty query and limit 1..100")
    data = _request("/users/students/search", {"q": query, "limit": limit}, **kwargs)
    _fields(data, {"total": int})
    if not isinstance(data.get("items"), list):
        raise PulseError("invalid_response", "Expected student items")
    for item in data["items"]:
        _fields(item, {"student_user_id": int, "student_name": str, "student_email": str})
    items = []
    for item in data["items"]:
        value = {"student_user_id": item["student_user_id"], "student_name": item["student_name"], "team_name": item.get("team_name")}
        if include_email:
            value["student_email"] = item["student_email"]
        items.append(value)
    return {"total": data["total"], "items": items}
