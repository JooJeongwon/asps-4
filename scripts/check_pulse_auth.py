"""Read-only auth probe. Prints status only, never credentials or room data."""

import os
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

from pulse.client import PulseError, meeting_rooms, reservations, students


def check(header, value, base_url):
    auth = {"base_url": base_url, "auth_header": header, "auth_value": value}
    try:
        rooms = meeting_rooms(**auth)
    except PulseError as exc:
        print(f"meeting_rooms: {exc.kind} ({exc})")
        return 1
    print(f"configured: ok, rooms={len(rooms)}")

    date = dt.datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()
    try:
        reservation_count = sum(len(reservations(room["id"], date, **auth)) for room in rooms)
    except PulseError as exc:
        print(f"reservations: {exc.kind} ({exc})")
        return 1
    print(f"reservations: ok, date={date}, rooms={len(rooms)}, entries={reservation_count}")

    try:
        result = students("__gcs_pulse_validation_no_match__", limit=1, **auth)
    except PulseError as exc:
        print(f"students_search: {exc.kind} ({exc})")
        return 1
    print(f"students_search: ok, total={result['total']}")
    return 0


def main():
    values = {}
    for line in Path(".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key.strip()] = value
    header, value = values.get("PULSE_AUTH_HEADER"), values.get("PULSE_AUTH_VALUE")
    if not header or not value:
        print("auth_config: missing PULSE_AUTH_HEADER or PULSE_AUTH_VALUE")
        return 1
    return check(header, value, values.get("PULSE_BASE_URL") or os.environ.get("PULSE_BASE_URL", "https://api.1000.school"))


if __name__ == "__main__":
    raise SystemExit(main())
