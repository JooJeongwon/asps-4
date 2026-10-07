"""Book one GCS-PULSE room and one Google Calendar event through both CLIs."""

import argparse
import datetime as dt
import json
import re
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
KST = ZoneInfo("Asia/Seoul")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class BookingError(Exception):
    def __init__(self, kind, message):
        self.kind = kind
        super().__init__(message)


def parse_time(value, label):
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() is None:
            raise ValueError
        parsed = parsed.astimezone(KST)
    except (AttributeError, TypeError, ValueError):
        raise BookingError("invalid_input", f"{label} must be ISO 8601 with an offset") from None
    return parsed.replace(microsecond=0)


def normalize_times(start_value, end_value, now=None):
    start, end = parse_time(start_value, "--start"), parse_time(end_value, "--end")
    if start >= end:
        raise BookingError("invalid_input", "start must be before end")
    if now is not None and start <= now.astimezone(KST):
        raise BookingError("invalid_input", "start must be in the future")
    return start, end


def overlaps(start, end, other_start, other_end):
    return start < other_end and other_start < end


def reservation_conflict(items, start, end):
    for item in items:
        if overlaps(start, end, parse_time(item["start_at"], "reservation start"), parse_time(item["end_at"], "reservation end")):
            return item
    return None


def event_times(event):
    start, end = event.get("start", {}), event.get("end", {})
    if "dateTime" in start and "dateTime" in end:
        return parse_time(start["dateTime"], "calendar start"), parse_time(end["dateTime"], "calendar end")
    if "date" in start and "date" in end:
        return dt.datetime.fromisoformat(start["date"]).replace(tzinfo=KST), dt.datetime.fromisoformat(end["date"]).replace(tzinfo=KST)
    return None


def event_conflict(items, start, end):
    for item in items:
        times = event_times(item)
        if times and overlaps(start, end, *times):
            return item
    return None


def _safe_error(value):
    return re.sub(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b", "<redacted-email>", value).strip()[:240]


def run_json(command):
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False)
    except FileNotFoundError:
        raise BookingError("tool_missing", f"command not found: {command[0]}") from None
    except subprocess.TimeoutExpired:
        raise BookingError("network_uncertain", f"timed out: {command[0]}") from None
    if result.returncode:
        try:
            payload = json.loads(result.stderr)
        except (json.JSONDecodeError, TypeError):
            payload = None
        if isinstance(payload, dict) and isinstance(payload.get("error"), str) and isinstance(payload.get("message"), str):
            raise BookingError(payload["error"], _safe_error(payload["message"]))
        detail = _safe_error(result.stderr or result.stdout or f"exit {result.returncode}")
        raise BookingError("cli_failed", f"{command[0]}: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise BookingError("invalid_response", f"{command[0]} returned non-JSON output") from None


def pulse(*args):
    return run_json([sys.executable, "-m", "pulse.cli", *map(str, args)])


def gws(gws_bin, method, params, body=None):
    command = [gws_bin, "calendar", "events", method, "--params", json.dumps(params), "--format", "json"]
    if body is not None:
        command += ["--json", json.dumps(body, ensure_ascii=False)]
    return run_json(command)


def resolve_attendees(queries, emails):
    result = []
    seen = set()
    for email in emails:
        if not EMAIL.fullmatch(email):
            raise BookingError("invalid_input", "attendee email is invalid")
        if email.casefold() not in seen:
            seen.add(email.casefold())
            result.append(email)
    for query in queries:
        data = pulse("students", "search", "--query", query, "--limit", 20, "--include-email")
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, list):
            raise BookingError("invalid_response", "student search did not return items")
        if len(items) != 1:
            kind = "student_not_found" if not items else "student_ambiguous"
            raise BookingError(kind, "each student query must resolve to exactly one result")
        email = items[0].get("student_email")
        if not isinstance(email, str) or not EMAIL.fullmatch(email):
            raise BookingError("invalid_response", "student search returned an invalid email")
        if email.casefold() not in seen:
            seen.add(email.casefold())
            result.append(email)
    if not result:
        raise BookingError("invalid_input", "provide --attendee-email or --student-query")
    return result


def select_room(rooms, room_id, room_name):
    if room_id is not None:
        matches = [room for room in rooms if room.get("id") == room_id]
    elif room_name:
        matches = [room for room in rooms if room.get("name", "").casefold() == room_name.casefold()]
    else:
        raise BookingError("invalid_input", "provide --room-id or --room-name")
    if len(matches) != 1:
        raise BookingError("room_not_found" if not matches else "room_ambiguous", "room selection did not resolve to one room")
    return matches[0]


def list_calendar(gws_bin, calendar_id, start, end):
    data = gws(gws_bin, "list", {"calendarId": calendar_id, "timeMin": start.isoformat(), "timeMax": end.isoformat(), "singleEvents": True, "orderBy": "startTime"})
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise BookingError("invalid_response", "calendar list did not return items")
    return items


def build_event(title, purpose, room, start, end, reservation_id, attendees):
    location = room["name"]
    if room.get("location"):
        location += f" ({room['location']})"
    return {
        "summary": title,
        "description": f"{purpose}\nGCS-PULSE reservation_id={reservation_id}",
        "location": location,
        "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Seoul"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Asia/Seoul"},
        "attendees": [{"email": email} for email in attendees],
    }


def verify_event(event, title, room, start, end, attendees):
    if not isinstance(event, dict) or not isinstance(event.get("id"), str) or event.get("summary") != title:
        raise BookingError("invalid_response", "calendar event is missing its ID or title")
    times = event_times(event)
    expected = (start, end)
    if not times or any(actual != wanted for actual, wanted in zip(times, expected)):
        raise BookingError("verification_failed", "calendar event time does not match request")
    if room["name"] not in (event.get("location") or ""):
        raise BookingError("verification_failed", "calendar event location does not match room")
    actual = {item.get("email", "").casefold() for item in event.get("attendees", [])}
    if not set(attendees).issubset(actual):
        raise BookingError("verification_failed", "calendar attendees do not match request")


def verify_reservation(items, reservation_id, start, end):
    matches = [item for item in items if item.get("id") == reservation_id]
    if len(matches) != 1:
        raise BookingError("verification_failed", "GCS reservation was not found exactly once")
    item = matches[0]
    if parse_time(item["start_at"], "reservation start") != start or parse_time(item["end_at"], "reservation end") != end:
        raise BookingError("verification_failed", "GCS reservation time does not match request")
    return item


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def recover_after_calendar_failure(gws_bin, calendar_id, start, end, reservation_id, can_cancel, error):
    try:
        existing = [item for item in list_calendar(gws_bin, calendar_id, start, end) if f"reservation_id={reservation_id}" in item.get("description", "")]
    except BookingError as reconcile_error:
        raise BookingError("manual_recovery", f"calendar result uncertain; reservation_id={reservation_id}; {reconcile_error}") from None
    if len(existing) == 1:
        return existing[0], "reconciled"
    if len(existing) > 1:
        raise BookingError("manual_recovery", f"multiple calendar events found; reservation_id={reservation_id}")
    if not can_cancel:
        raise BookingError("manual_recovery", f"calendar failed and GCS cancellation is unavailable; reservation_id={reservation_id}")
    try:
        pulse("reservations", "cancel", "--reservation-id", reservation_id)
    except BookingError as cancel_error:
        raise BookingError("manual_recovery", f"calendar failed; cancel failed; reservation_id={reservation_id}; {cancel_error}") from None
    raise BookingError("compensated", f"calendar failed and GCS reservation was cancelled; {error}")


def _ask(label, default=None):
    suffix = f" [{default}]" if default is not None else ""
    try:
        value = input(f"{label}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        raise BookingError("input_cancelled", "interactive booking cancelled") from None
    return value or ("" if default is None else str(default))


def interactive_args(args):
    tomorrow = (dt.datetime.now(KST) + dt.timedelta(days=1)).date().isoformat()
    args.title = _ask("회의 제목")
    args.purpose = _ask("목적", args.title)
    date = _ask("날짜(YYYY-MM-DD)", tomorrow)
    start_time = _ask("시작 시각(HH:MM)", "14:00")
    try:
        duration = int(_ask("시간(분)", "60"))
        if duration <= 0:
            raise ValueError
    except ValueError:
        raise BookingError("invalid_input", "duration must be a positive number of minutes") from None
    start = parse_time(f"{date}T{start_time}:00+09:00", "start")
    args.start = start.isoformat()
    args.end = (start + dt.timedelta(minutes=duration)).isoformat()
    room_value = _ask("회의실 ID 또는 정확한 이름")
    if room_value.isdigit():
        args.room_id, args.room_name = int(room_value), None
    else:
        args.room_id, args.room_name = None, room_value
    names = _ask("학생 이름(쉼표 구분, 없으면 Enter)")
    emails = _ask("직접 초대할 이메일(쉼표 구분, 없으면 Enter)")
    args.student_query = [value.strip() for value in names.split(",") if value.strip()]
    args.attendee_email = [value.strip() for value in emails.split(",") if value.strip()]
    args.calendar_id = _ask("Calendar ID", args.calendar_id)
    return args


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interactive", action="store_true", help="prompt for booking details and ask once before writing")
    parser.add_argument("--title")
    parser.add_argument("--start", help="ISO 8601 with offset")
    parser.add_argument("--end", help="ISO 8601 with offset")
    parser.add_argument("--purpose")
    room = parser.add_mutually_exclusive_group()
    room.add_argument("--room-id", type=int)
    room.add_argument("--room-name")
    parser.add_argument("--attendee-email", action="append", default=[])
    parser.add_argument("--student-query", action="append", default=[])
    parser.add_argument("--calendar-id", default="primary")
    parser.add_argument("--gws", default="gws")
    parser.add_argument("--confirm", action="store_true", help="perform reservation and Calendar writes")
    parser.add_argument("--state-dir", default="runs/bookings")
    args = parser.parse_args(argv)

    try:
        if args.interactive:
            args = interactive_args(args)
        elif not args.title or not args.start or not args.end or (args.room_id is None and not args.room_name) or (args.room_id is not None and args.room_name):
            parser.error("non-interactive mode requires --title, --start, --end, and exactly one of --room-id/--room-name")
        start, end = normalize_times(args.start, args.end, dt.datetime.now(KST))
        attendees = resolve_attendees(args.student_query, args.attendee_email)
        rooms = pulse("meeting-rooms", "list")
        selected = select_room(rooms, args.room_id, args.room_name)
        reservations = pulse("reservations", "list", "--room-id", selected["id"], "--date", start.date())
        if (conflict := reservation_conflict(reservations, start, end)):
            raise BookingError("room_conflict", f"GCS room is already reserved: {conflict['id']}")
        calendar_items = list_calendar(args.gws, args.calendar_id, start, end)
        if event_conflict(calendar_items, start, end):
            raise BookingError("calendar_conflict", "Calendar has an overlapping event")

        run_id = dt.datetime.now(dt.timezone.utc).strftime("booking-%Y%m%dT%H%M%S%fZ")
        state_path = ROOT / args.state_dir / f"{run_id}.json"
        state = {"run_id": run_id, "status": "preview" if not args.confirm else "ready", "attendee_count": len(attendees), "room_id": selected["id"], "calendar_id": args.calendar_id, "notification_requested": False}
        save_state(state_path, state)
        plan = {"status": state["status"], "state_file": str(state_path.relative_to(ROOT)), "title": args.title, "start": start.isoformat(), "end": end.isoformat(), "room_id": selected["id"], "room_name": selected["name"], "attendee_count": len(attendees), "calendar_id": args.calendar_id, "notification_requested": False}
        if args.interactive and not args.confirm:
            print(f"\n예약 요약: {args.title} / {start.isoformat()}–{end.isoformat()} / {selected['name']} / 참석자 {len(attendees)}명")
            if _ask("예약·Calendar 초대 진행", "아니오").casefold() not in {"y", "yes", "예", "진행"}:
                print(json.dumps(plan, ensure_ascii=False))
                return 0
            args.confirm = True
            state.update({"status": "ready"})
            save_state(state_path, state)
        if not args.confirm:
            print(json.dumps(plan, ensure_ascii=False))
            return 0

        reservation = pulse("reservations", "create", "--room-id", selected["id"], "--start-at", start.isoformat(), "--end-at", end.isoformat(), "--purpose", args.purpose or args.title)
        reservation_id = reservation.get("id")
        if not isinstance(reservation_id, int):
            raise BookingError("invalid_response", "GCS reservation response has no ID")
        state.update({"status": "gcs_reserved", "reservation_id": reservation_id, "can_cancel": reservation.get("can_cancel", False)})
        save_state(state_path, state)
        event = build_event(args.title, args.purpose or args.title, selected, start, end, reservation_id, attendees)
        try:
            created = gws(args.gws, "insert", {"calendarId": args.calendar_id, "sendUpdates": "all"}, event)
            verify_event(created, args.title, selected, start, end, attendees)
        except BookingError as error:
            try:
                created, recovery = recover_after_calendar_failure(args.gws, args.calendar_id, start, end, reservation_id, reservation.get("can_cancel", False), error)
            except BookingError as recovery_error:
                state.update({"status": recovery_error.kind})
                save_state(state_path, state)
                raise
            verify_event(created, args.title, selected, start, end, attendees)
            state.update({"status": "calendar_reconciled", "calendar_event_id": created["id"], "notification_requested": True, "recovery": recovery})
        else:
            state.update({"status": "calendar_created", "calendar_event_id": created["id"], "notification_requested": True})
        save_state(state_path, state)
        verified_reservation = verify_reservation(pulse("reservations", "list", "--room-id", selected["id"], "--date", start.date()), reservation_id, start, end)
        verified_event = gws(args.gws, "get", {"calendarId": args.calendar_id, "eventId": created["id"]})
        verify_event(verified_event, args.title, selected, start, end, attendees)
        state.update({"status": "verified"})
        save_state(state_path, state)
        print(json.dumps({"status": "verified", "state_file": str(state_path.relative_to(ROOT)), "reservation_id": verified_reservation["id"], "calendar_event_id": verified_event["id"], "attendee_count": len(attendees), "notification_requested": True}, ensure_ascii=False))
        return 0
    except BookingError as error:
        print(json.dumps({"status": "failed", "error": error.kind, "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
