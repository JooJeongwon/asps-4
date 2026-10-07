import io
import json
import unittest
import urllib.error
import datetime as dt
from types import SimpleNamespace
from unittest.mock import patch

from pulse.client import PulseError, auth_me, cancel_reservation, create_reservation, meeting_rooms, reservations, students
from pulse.mcp.__main__ import handle
from scripts.check_pulse_auth import check
from scripts.check_pulse_parity import main as check_parity
from scripts.book_meeting import BookingError, event_conflict, interactive_args, recover_after_calendar_failure, resolve_attendees, reservation_conflict
from scripts.run_1_1_comparison import redact, summarize


class Response(io.BytesIO):
    status = 200
    headers = {"Content-Type": "application/json"}


class PulseTest(unittest.TestCase):
    def test_auth_me_validates_authenticated_status(self):
        response = Response(b'{"authenticated":true,"user":null}')
        with patch("pulse.client.urllib.request.build_opener") as opener:
            opener.return_value.open.return_value = response
            self.assertEqual(auth_me(auth_header="X-Test", auth_value="secret"), {"authenticated": True})
        with patch("pulse.client._request", return_value={"authenticated": False}):
            with self.assertRaises(PulseError) as error:
                auth_me(auth_header="X-Test", auth_value="secret")
        self.assertEqual(error.exception.kind, "auth_failed")

    def test_three_read_scenarios_share_validated_results(self):
        cases = [
            (meeting_rooms, {}, [{"id": 2, "name": "A", "location": "2F", "created_at": "2026-10-01T10:00:00+09:00", "updated_at": "2026-10-01T10:00:00+09:00"}], [{"id": 2, "name": "A", "location": "2F"}]),
            (reservations, {"room_id": 2, "date": "2026-10-07"}, [{"id": 3, "meeting_room_id": 2, "reserved_by_user_id": 7, "start_at": "2026-10-07T10:00:00+09:00", "end_at": "2026-10-07T11:00:00+09:00", "created_at": "2026-10-01T10:00:00+09:00", "updated_at": "2026-10-01T10:00:00+09:00"}], [{"id": 3, "meeting_room_id": 2, "start_at": "2026-10-07T10:00:00+09:00", "end_at": "2026-10-07T11:00:00+09:00"}]),
            (students, {"query": "Kim"}, {"total": 1, "items": [{"student_user_id": 5, "student_name": "Kim", "student_email": "private@example.test", "team_name": "T"}]}, {"total": 1, "items": [{"student_user_id": 5, "student_name": "Kim", "team_name": "T"}]}),
        ]
        for function, args, payload, expected in cases:
            with self.subTest(function=function.__name__):
                response = Response(json.dumps(payload).encode())
                with patch("pulse.client.urllib.request.build_opener") as opener:
                    opener.return_value.open.return_value = response
                    result = function(**args, auth_header="X-Test", auth_value="secret")
                    self.assertEqual(result, expected)
                    self.assertEqual(opener.return_value.open.call_args.args[0].get_header("X-test"), "secret")
                    self.assertEqual(opener.return_value.open.call_args.args[0].get_header("User-agent"), "gcs-pulse-client/0.1")

    def test_errors_are_explicit_and_do_not_echo_credentials(self):
        http_error = urllib.error.HTTPError("https://api.1000.school/meeting-rooms", 401, "bad secret", {}, None)
        with patch("pulse.client.urllib.request.build_opener") as opener:
            opener.return_value.open.side_effect = http_error
            with self.assertRaises(PulseError) as error:
                meeting_rooms(auth_header="X-Test", auth_value="secret")
        http_error.close()
        self.assertEqual(error.exception.kind, "auth_failed")
        self.assertNotIn("secret", str(error.exception))
        with patch("pulse.client._request", return_value={"total": 1}):
            with self.assertRaises(PulseError) as error:
                students("Kim")
        self.assertEqual(error.exception.kind, "invalid_response")
        with self.assertRaises(PulseError):
            reservations(2, "tomorrow")

        http_error = urllib.error.HTTPError("https://api.1000.school/meeting-rooms", 403, "forbidden", {}, io.BytesIO(b'{"detail":"API token rejected"}'))
        with patch("pulse.client.urllib.request.build_opener") as opener:
            opener.return_value.open.side_effect = http_error
            with self.assertRaises(PulseError) as error:
                meeting_rooms(auth_header="X-Test", auth_value="secret")
        self.assertEqual(str(error.exception), "HTTP 403: API token rejected")
        self.assertNotIn("secret", str(error.exception))
        http_error.close()

    def test_booking_writes_validate_and_use_json_methods(self):
        payload = {"id": 8, "meeting_room_id": 2, "reserved_by_user_id": 7, "start_at": "2026-10-07T10:00:00+09:00", "end_at": "2026-10-07T11:00:00+09:00", "created_at": "2026-10-01T10:00:00+09:00", "updated_at": "2026-10-01T10:00:00+09:00", "can_cancel": True}
        with patch("pulse.client.urllib.request.build_opener") as opener:
            opener.return_value.open.return_value = Response(json.dumps(payload).encode())
            result = create_reservation(2, payload["start_at"], payload["end_at"], "test", auth_header="X-Test", auth_value="secret")
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(result["id"], 8)
            self.assertEqual(request.method, "POST")
            self.assertEqual(json.loads(request.data), {"start_at": payload["start_at"], "end_at": payload["end_at"], "purpose": "test"})
        with patch("pulse.client._request", return_value={"message": "cancelled"}) as request:
            self.assertEqual(cancel_reservation(8, auth_header="X-Test", auth_value="secret"), {"message": "cancelled"})
            self.assertEqual(request.call_args.kwargs["method"], "DELETE")

    def test_booking_fixtures_cover_ambiguity_and_conflict(self):
        with patch("scripts.book_meeting.pulse", return_value={"items": [{"student_email": "a@example.test"}, {"student_email": "b@example.test"}]}):
            with self.assertRaisesRegex(BookingError, "exactly one") as error:
                resolve_attendees(["동명이인"], [])
        self.assertEqual(error.exception.kind, "student_ambiguous")
        start = dt.datetime.fromisoformat("2026-10-07T10:00:00+09:00")
        end = dt.datetime.fromisoformat("2026-10-07T11:00:00+09:00")
        conflict = reservation_conflict([{"id": 4, "start_at": "2026-10-07T10:30:00+09:00", "end_at": "2026-10-07T11:30:00+09:00"}], start, end)
        self.assertEqual(conflict["id"], 4)
        self.assertIsNotNone(event_conflict([{"start": {"dateTime": "2026-10-07T10:30:00+09:00"}, "end": {"dateTime": "2026-10-07T11:30:00+09:00"}}], start, end))

    def test_calendar_failure_compensates_only_when_cancel_is_allowed(self):
        with patch("scripts.book_meeting.list_calendar", return_value=[]), patch("scripts.book_meeting.pulse", return_value={"message": "cancelled"}) as pulse:
            with self.assertRaises(BookingError) as error:
                recover_after_calendar_failure("gws", "primary", dt.datetime.now(dt.timezone.utc), dt.datetime.now(dt.timezone.utc), 8, True, BookingError("cli_failed", "insert failed"))
        self.assertEqual(error.exception.kind, "compensated")
        self.assertEqual(pulse.call_args.args[0:3], ("reservations", "cancel", "--reservation-id"))

    def test_calendar_reconciliation_prevents_duplicate_retry(self):
        existing = {"id": "event-1", "description": "GCS-PULSE reservation_id=8"}
        with patch("scripts.book_meeting.list_calendar", return_value=[existing]), patch("scripts.book_meeting.pulse") as pulse:
            event, status = recover_after_calendar_failure("gws", "primary", dt.datetime.now(dt.timezone.utc), dt.datetime.now(dt.timezone.utc), 8, True, BookingError("network_uncertain", "unknown"))
        self.assertEqual((event, status), (existing, "reconciled"))
        pulse.assert_not_called()

    def test_interactive_input_builds_kst_interval_and_attendees(self):
        args = SimpleNamespace(title=None, purpose=None, start=None, end=None, room_id=None, room_name=None, student_query=[], attendee_email=[], calendar_id="primary")
        answers = iter(["팀 회의", "논의", "2026-10-07", "14:00", "45", "2", "김철수", "guest@example.test", "primary"])
        with patch("builtins.input", side_effect=lambda _: next(answers)):
            result = interactive_args(args)
        self.assertEqual(result.start, "2026-10-07T14:00:00+09:00")
        self.assertEqual(result.end, "2026-10-07T14:45:00+09:00")
        self.assertEqual(result.room_id, 2)
        self.assertEqual(result.student_query, ["김철수"])
        self.assertEqual(result.attendee_email, ["guest@example.test"])

    def test_mcp_tool_output_matches_client_and_hides_email(self):
        payload = {"total": 1, "items": [{"student_user_id": 5, "student_name": "Kim", "team_name": "T"}]}
        with patch("pulse.mcp.__main__.students", return_value=payload):
            result = handle({"method": "tools/call", "params": {"name": "students_search", "arguments": {"query": "Kim"}}})
        self.assertEqual(json.loads(result["content"][0]["text"]), payload)

    def test_auth_probe_uses_booking_endpoint_and_hides_token(self):
        with patch("scripts.check_pulse_auth.meeting_rooms", return_value=[]) as rooms, \
             patch("scripts.check_pulse_auth.reservations", return_value=[]) as reservations, \
             patch("scripts.check_pulse_auth.students", return_value={"total": 0, "items": []}) as students:
            with patch("builtins.print") as output:
                self.assertEqual(check("Authorization", "secret", "https://api.1000.school"), 0)
        self.assertEqual(rooms.call_count, 1)
        self.assertEqual(reservations.call_count, 0)
        self.assertEqual(students.call_count, 1)
        self.assertEqual(rooms.call_args.kwargs["auth_value"], "secret")
        self.assertNotIn("secret", str(output.call_args_list))

    def test_parity_probe_compares_process_outputs_without_printing_data(self):
        values = [[{"id": 2, "name": "Private room"}], [], {"total": 0, "items": []}]
        mcp_lines = [json.dumps({"id": 0, "result": {"protocolVersion": "2025-11-25"}})]
        mcp_lines += [json.dumps({"id": i, "result": {"content": [{"text": json.dumps(value)}]}}) for i, value in enumerate(values, 1)]
        outputs = [SimpleNamespace(returncode=0, stdout=json.dumps(value)) for value in values]
        outputs.append(SimpleNamespace(returncode=0, stdout="\n".join(mcp_lines)))
        with patch("scripts.check_pulse_parity.subprocess.run", side_effect=outputs) as run, patch("builtins.print") as printed:
            self.assertEqual(check_parity(["--room-id", "2", "--date", "2026-10-07", "--query", "__no_match__"]), 0)
        self.assertEqual(run.call_count, 4)
        self.assertEqual([call.args[0] for call in printed.call_args_list], ["rooms: match", "reservations: match", "students: match"])

    def test_comparison_parser_uses_latest_turn_usage_and_hashes_result(self):
        raw = "\n".join([
            json.dumps({"type": "token_usage_record", "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3}, "turn_token_usage": {"input_tokens": 12, "output_tokens": 4, "total_tokens": 16}}),
            json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": {"last_token_usage": {"input_tokens": 10, "output_tokens": 3, "total_tokens": 13}}}}),
            json.dumps({"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": '{"scenario":"A","rooms":[]}' }]}),
        ])
        result = summarize(raw)
        self.assertEqual(result["input_tokens"], 12)
        self.assertEqual(result["output_tokens"], 4)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["result_hash"]), 16)

    def test_comparison_parser_reads_codex_agent_message_and_tool_failure(self):
        raw = "\n".join([
            json.dumps({"type": "item.started", "item": {"type": "mcp_tool_call"}}),
            json.dumps({"type": "item.completed", "item": {"type": "mcp_tool_call", "status": "failed", "error": {"message": "approval"}}}),
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": '{"scenario":"A","rooms":[]}'}}),
        ])
        result = summarize(raw)
        self.assertEqual(result["tool_calls"], 1)
        self.assertEqual(result["tool_errors"], 1)
        self.assertFalse(result["success"])

    def test_comparison_parser_counts_cli_tool_once_and_adds_total_tokens(self):
        raw = "\n".join([
            json.dumps({"type": "item.started", "item": {"type": "command_execution"}}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution", "status": "completed"}}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 3}}),
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": '{"scenario":"A","rooms":[]}'}}),
        ])
        result = summarize(raw)
        self.assertEqual(result["tool_calls"], 1)
        self.assertEqual(result["tool_errors"], 0)
        self.assertEqual(result["total_tokens"], 13)
        self.assertTrue(result["success"])

    def test_comparison_logs_redact_secret_and_student_fields(self):
        value = redact('{"student_email":"a@example.com","student_name":"Kim","query":"Kim"}', "secret", "Kim")
        self.assertNotIn("secret", value)
        self.assertNotIn("a@example.com", value)
        self.assertNotIn('"Kim"', value)


if __name__ == "__main__":
    unittest.main()
