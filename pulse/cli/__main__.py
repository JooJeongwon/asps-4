import argparse
import json
import sys

from pulse.client import PulseError, cancel_reservation, create_reservation, meeting_rooms, reservations, students


def main():
    parser = argparse.ArgumentParser(prog="python3 -m pulse.cli")
    group = parser.add_subparsers(dest="resource", required=True)
    rooms = group.add_parser("meeting-rooms")
    rooms.add_argument("action", choices=["list"])
    bookings = group.add_parser("reservations")
    bookings.add_argument("action", choices=["list", "create", "cancel"])
    bookings.add_argument("--room-id", type=int)
    bookings.add_argument("--date")
    bookings.add_argument("--start-at")
    bookings.add_argument("--end-at")
    bookings.add_argument("--purpose")
    bookings.add_argument("--reservation-id", type=int)
    people = group.add_parser("students")
    people.add_argument("action", choices=["search"])
    people.add_argument("--query", required=True)
    people.add_argument("--limit", type=int, default=20)
    people.add_argument("--include-email", action="store_true")
    args = parser.parse_args()
    try:
        if args.resource == "meeting-rooms":
            result = meeting_rooms()
        elif args.resource == "reservations" and args.action == "list":
            if args.room_id is None or not args.date:
                parser.error("reservations list requires --room-id and --date")
            result = reservations(args.room_id, args.date)
        elif args.resource == "reservations" and args.action == "create":
            if args.room_id is None or not args.start_at or not args.end_at:
                parser.error("reservations create requires --room-id, --start-at, and --end-at")
            result = create_reservation(args.room_id, args.start_at, args.end_at, args.purpose)
        elif args.resource == "reservations" and args.action == "cancel":
            if args.reservation_id is None:
                parser.error("reservations cancel requires --reservation-id")
            result = cancel_reservation(args.reservation_id)
        else:
            result = students(args.query, args.limit, include_email=args.include_email)
        print(json.dumps(result, ensure_ascii=False))
    except PulseError as exc:
        print(json.dumps({"error": exc.kind, "message": str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
