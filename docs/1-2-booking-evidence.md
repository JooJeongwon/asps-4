# 1.2 예약 Skill 증거

확인일: 2026-10-06 KST

상태: 구현·fixture 검증, 실제 N.FR2 예약/Calendar 생성·초대메일 수신 및 참석자 응답 확인 완료. 참석자 응답은 `declined`.

## 구현 증거

- [`skills/gcs-meeting-booker/SKILL.md`](../skills/gcs-meeting-booker/SKILL.md): 입력 계약, 두 CLI 호출 순서, `sendUpdates=all`, 충돌 중단, Calendar 실패 보상, 중복 재시도 방지.
- [`scripts/book_meeting.py`](../scripts/book_meeting.py): 학생/방/예약/Calendar 조회, 예약 생성, 이벤트 생성, 양쪽 재조회와 상태 기록.
- `python3 scripts/book_meeting.py --interactive`: 긴 옵션 없이 필요한 값만 입력하는 대화형 경로. 마지막 요약에서 `예`를 입력해야 쓰기 단계로 넘어간다.
- `pulse/cli`: `reservations create`, `reservations cancel`, `students search --include-email` 추가.
- 요청 JSON은 실행 중에만 사용하고 `runs/bookings/*.json`에는 이메일을 저장하지 않는다.

## 실행한 검증

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile pulse/client/__init__.py pulse/cli/__main__.py scripts/book_meeting.py
python3 scripts/book_meeting.py --help
```

결과: unittest 15개 통과, Python 컴파일 통과, CLI 도움말 출력 성공.

Fixture로 다음을 확인했다.

| 사례 | 결과 |
|---|---|
| 학생 검색 동명이인 | `student_ambiguous`로 중단, 임의 이메일 선택 없음 |
| GCS 방 예약 충돌 | `[start, end)` 겹침을 찾아 `room_conflict`로 중단 |
| Calendar 생성 실패 + `can_cancel=true` | 먼저 Calendar 재조회 후 없을 때만 GCS 취소 호출 |
| Calendar 쓰기 결과 불명확 | 재조회에서 `reservation_id` 이벤트를 찾으면 `reconciled`, 재삽입하지 않음 |

## 현재 환경의 비라이브 실행

실제 변경 없이 preview 명령을 실행했다.

```sh
python3 scripts/book_meeting.py \
  --title 'fixture booking probe' \
  --start '2026-10-07T14:00:00+09:00' \
  --end '2026-10-07T15:00:00+09:00' \
  --room-id 2 --attendee-email 'fixture@example.test'
```

결과: `network_uncertain (URLError)`로 GCS 읽기 단계에서 중단. `--confirm`을 사용하지 않아 예약 POST, Calendar insert, 초대 메일은 발생하지 않았다.

대화형 smoke test도 `python3 scripts/book_meeting.py --interactive`에 fixture 입력을 공급해 같은 `network_uncertain (URLError)` 분류를 확인했다. 입력 형식과 확인 전 중단 경로는 동작했으며, 외부 변경은 없었다.

## 실제 라이브 실행

사용자가 인증된 환경에서 `N.FR2`, 2026-10-06 18:00–19:00 KST, `독서토론 준비` 요청을 실행했다.

결과는 `status=verified`, `attendee_count=1`, `notification_requested=true`였다. 상태 파일은 [`runs/bookings/booking-20261006T081722545478Z.json`](../runs/bookings/booking-20261006T081722545478Z.json)이며 마스킹된 증거 ID는 GCS 예약 `***787`, Calendar 이벤트 `e2sa…3kccq0`이다. 사용자가 실제 초대메일 수신을 확인했고, GWS CLI 조회에서 참석자 `responseStatus=declined`를 확인했다. N.MR2에는 쓰기를 수행하지 않았다.

## 라이브 완료 조건

네트워크가 허용되고 GCS 예약 권한과 GWS OAuth Calendar 쓰기 권한이 확인된 환경에서 다음을 다시 실행해야 한다.

1. 같은 입력으로 preview 실행 후 사용자의 명시적 확인을 받는다.
2. `--confirm` 실행 결과의 예약 ID와 Calendar 이벤트 ID를 마스킹해 기록한다.
3. 두 시스템 재조회에서 시간·방·참석자를 대조한다.
4. Calendar 요청의 `sendUpdates=all`을 확인하고, 요청/처리와 실제 메일 수신·수락은 별도로 보고한다.

현재 실제 실행 ID: 상태 파일에 기록됨. 실제 예약·이벤트 생성, Calendar 초대 요청, 초대메일 수신 및 참석자 응답 `declined`가 확인됨.
