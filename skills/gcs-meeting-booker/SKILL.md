# gcs-meeting-booker

Use this skill when a user asks to reserve a GCS-PULSE meeting room and create one Google Calendar event with team members invited.

This skill runs the repository's GCS-PULSE CLI and the installed GWS CLI. It does not call the APIs directly and does not send a separate Gmail message: `sendUpdates=all` on the Calendar insert requests Google Calendar to notify guests.

## Required input

- meeting title and purpose
- absolute start and end times with an offset; use `Asia/Seoul` for Korean user input
- one `--room-id` or exact `--room-name`
- each attendee as a verified email or an exact student-name query
- Google Calendar ID, only when it is not `primary`

Reject missing/ambiguous student searches, invalid or past times, `start >= end`, unknown rooms, room conflicts, and Calendar conflicts. Never guess an email or silently choose between duplicate rooms or people.

## Run

Run from the repository root. The script performs read-only checks first and writes a redacted state file under `runs/bookings/`.

For the shortest input, use interactive mode. It asks for the title, purpose, KST date/time, duration, room ID/name, attendees, and Calendar ID, then shows one summary. Enter `예` or `y` at the final prompt to perform the writes.

```sh
python3 scripts/book_meeting.py --interactive
```

This is equivalent to the explicit form below:

```sh
python3 scripts/book_meeting.py \
  --title '프로젝트 회의' \
  --start '2026-10-07T14:00:00+09:00' \
  --end '2026-10-07T15:00:00+09:00' \
  --room-id 2 \
  --student-query '정확한 팀원 이름' \
  --attendee-email 'verified@example.com'
```

Without `--interactive`, the first run is a preview. Show the returned title, KST interval, room, attendee count, Calendar ID, and state-file path to the user. Do not show student emails. Ask for confirmation before adding `--confirm` and running the same command again.

The confirmed run performs this order:

1. `python3 -m pulse.cli students search --include-email` for each name query.
2. `python3 -m pulse.cli meeting-rooms list` and `reservations list` for the selected room/date.
3. `gws calendar events list` for the organizer's Calendar and requested interval.
4. `python3 -m pulse.cli reservations create` and records the returned reservation ID.
5. `gws calendar events insert --params '{"calendarId":"...","sendUpdates":"all"}' --json '...'` with the room, times, reservation ID, and attendees.
6. Re-read the GCS reservation and Calendar event by ID and compare times, room, title, and attendees.

The script makes exactly one reservation POST and one Calendar insert. A failed or ambiguous Calendar insert is reconciled with a Calendar list before any retry. If no event exists and the GCS response says `can_cancel: true`, it cancels the reservation. If reconciliation or cancellation is uncertain, stop and report the reservation ID for manual cleanup. Never blindly retry either write.

## Verification and cleanup

The script's success output contains the full IDs needed for cleanup; evidence documents must mask them. `notification_requested: true` means the Calendar request used `sendUpdates=all`; it does not prove delivery, acceptance, or inbox receipt.

```sh
python3 -m pulse.cli reservations cancel --reservation-id 123
gws calendar events delete --params '{"calendarId":"primary","eventId":"EVENT_ID"}'
```

Only delete an event after checking that it is the event created by this run. Do not add a second Gmail call unless the Calendar CLI/API behavior is explicitly shown to be insufficient.

## Preconditions and reporting

Before a real write, confirm that `.env` contains the verified GCS auth header/value and that `gws 0.22.5` is authenticated. The repository currently has no live GWS credential, so fixture tests and preview checks must be reported as non-live. Report the masked reservation ID, masked Calendar event ID, whether `sendUpdates=all` was requested, and any unverified permission or delivery status.
