# GCS-PULSE × Google Calendar × NeoFirm 과제 실행 로드맵

> 기준일: 2026-10-07 · 시간대: `Asia/Seoul`  
> 상태: **진행 중**. 1.1 Team A 비교와 1.2 실제 예약·Calendar 초대는 완료했다. 과제 2는 최신 요청의 **Codex + NotebookLM CLI**로 현재 입력·임시 7분 기준 조사 → 독립 CLI 토론 → 최종 PPTX/PDF 생성까지 완료했다. 다른 팀 비교, 공식 발표 공지 대조와 실제 리허설은 남았다.

**2026-10-07 범위 변경:** 사용자가 Codex 사용을 명시했다. 아래의 과거 Claude Code/“클코” 전제는 이번 실행에서 Codex 독립 Agent/CLI 세션으로 대체한다. 공식 공지가 없어 참고 보고서 p.18–20 및 임시 7분을 적용하며, 별도 공지가 확보되면 그 조건을 우선한다.

## 현재 진척과 증거

| Phase | 상태 | 증거·남은 조건 |
|---|---|---|
| Phase 0 환경/인증 | 부분 완료 | GCS/GWS 권한은 사용자 환경에서 확인했다. `codex-cli 0.160.1`, `.venv/bin/notebooklm 0.8.4` 설치·도움말 확인. 사용자 Mac에서 NotebookLM 서버 인증·Codex preflight 및 자료 6개 등록 성공. 이번 과제 2에 Claude Code는 사용하지 않는다. |
| Phase 1 도구 준비 | 준비 완료 | `pulse/client`, `pulse/cli`, `pulse/mcp` 구현, stdio MCP 초기화 확인, 로컬 테스트 10개 통과. 프로세스 비교 스크립트와 Codex 측정 러너 준비. 초기 실패 로그와 `team-a` 최종 성공 로그를 확보했다. |
| Phase 1 비교 | 부분 완료 | 사용자 환경의 `1-1-20261006T054713Z`에서 `team-a`의 A/B/C를 MCP·CLI 각각 3회, 총 18회 성공 실행했다. 결과 해시·토큰·시간 중앙값은 `1.1.md`와 `docs/1-1-comparison.md`에 기록했다. 다른 팀 계정의 동일 실행은 아직 없다. |
| Phase 2–3 예약/Skill | 완료 | 사용자 환경에서 2026-10-06 18:00–19:00 KST `N.FR2` 예약, Calendar 생성·참석자 초대 요청·양쪽 재조회를 성공했다. [`1.2.md`](1.2.md), [`docs/1-2-booking-evidence.md`](docs/1-2-booking-evidence.md) 참조. |
| Phase 4–7 NeoFirm | 완료(현재 입력·임시 7분 기준) | NotebookLM 조사 3회·인용 24/7/14개, 독립 CLI 9회+종합, 실제 내용 검사 통과, 11장 PPTX/PDF·대본 생성 및 `COMPLETE` 확인. 전체 로컬 테스트 25개 통과. 공식 공지 대조·실제 리허설은 남음. [증거](docs/2-neofirm-evidence.md) 참조. |

## 0. 과제 범위와 최종 제출물

| 과제 | 해야 하는 일 | 검증 가능한 결과 |
|---|---|---|
| 1.1 | **각 팀별로** Codex에서 GCS-PULSE를 MCP와 CLI 방식으로 각각 사용하고 토큰 사용량·경험 비교 | 동일 시나리오 실행 기록, 토큰 집계, 팀별 비교표와 결론 |
| 1.2 | **GCS-PULSE CLI + GWS CLI**로 회의실 예약, Calendar 일정 등록, 팀원 초대와 초대 메일을 한 번에 처리하는 Skill 제작 | 실행 가능한 `SKILL.md`, 호출 코드/스크립트, 실제 또는 허용된 테스트 실행 결과 |
| 2 | 몰입캠프 2일차 **NeoFirm 과제의 정확한 지시사항**과 제공된 보고서를 기반으로, 클코(우선 Claude Code로 해석) + NotebookLM CLI를 써서 조사 → AI Agent 토론 → 최종 발표자료를 한 번의 실행 흐름으로 생성 | 원문·추가 출처, 조사 노트, 역할별 토론 기록, 결론, 발표 파일, 자동 실행 로그 |

**제출 기준:** 각 과제의 결과뿐 아니라 재현 절차, 버전, 로그, 실패·복구 기록을 남긴다. 과제 2의 실제 주제·평가 기준은 별도 과제 원문으로 먼저 확정한다. 지금까지 제공된 내용만으로 NeoFirm에 관한 사실이나 발표 결론을 미리 정하지 않는다.

## 1. 현재 확인된 사실과 첫날 확인할 사항

### 1.1 첨부 `openapi.json`에서 확인된 GCS-PULSE API

Swagger 문서 주소는 <https://api.1000.school/docs#/>. 첨부 명세는 OpenAPI 3.1.0이며 아래 경로와 자료형을 정의한다.

| 목적 | 메서드·경로 | 핵심 입출력 |
|---|---|---|
| 현재 사용자 확인 | `GET /auth/me` | 인증 상태·사용자 확인용 조회 후보 |
| API 토큰 생성 | `POST /auth/tokens` | `{"description":"..."}`; 응답의 원문 `token`은 **한 번만** 반환. 선택적 `Idempotency-Key` 헤더 |
| 토큰 목록/폐기 | `GET /auth/tokens`; `DELETE /auth/tokens/{token_id}` | 발급 토큰의 메타데이터 조회·폐기 |
| 회의실 목록 | `GET /meeting-rooms` | `id`, `name`, `location` 등 |
| 날짜별 예약 목록 | `GET /meeting-rooms/{room_id}/reservations?date=YYYY-MM-DD` | `start_at`, `end_at`, `can_cancel` 등을 가진 예약 목록 |
| 예약 생성 | `POST /meeting-rooms/{room_id}/reservations` | 본문: `start_at`, `end_at` 필수; `purpose` 선택. 응답에 예약 `id` |
| 예약 취소 | `DELETE /meeting-rooms/reservations/{reservation_id}` | 실패 보상용. 응답의 `can_cancel`도 확인 |
| 학생 검색 | `GET /users/students/search?q=...&limit=20` | `items[]` 안에 `student_user_id`, `student_name`, `student_email`, `team_name`; 동명이인 가능 |
| 학생 목록 | `GET /users/students?limit=100&offset=0` | 페이지 단위 조회 |

예약 본문 형태:

```json
{
  "start_at": "2026-10-07T14:00:00+09:00",
  "end_at": "2026-10-07T15:00:00+09:00",
  "purpose": "프로젝트 회의"
}
```

**명세의 한계:** 최상위 `servers`와 `security`, `components.securitySchemes`가 비어 있다. 따라서 서비스 주소는 Swagger URL의 호스트를 후보로 삼되 실제 환경에서 확인하고, **API 토큰을 어떤 헤더로 보내는지**는 인증 안내/실제 허용된 조회 호출로 검증한다. 예약 충돌 응답 코드, 예약 가능 시간, 권한, 정원, 변경 API는 명세만으로 단정하지 않는다. 예약 생성에 `Idempotency-Key`가 정의된 것은 아니므로 네트워크 오류 직후 POST를 무조건 재시도하지 않는다.

### 1.2 확인되지 않은 의존성: 작업 시작 전에 해결

1. 수업에서 배포한 **GCS-PULSE CLI와 MCP 서버/저장소/설치 안내**가 있는지 팀 공지·강의자료에서 확인한다. 현재 PATH와 Codex MCP 설정에서는 발견되지 않아 로컬 최소 어댑터를 준비했지만, Swagger는 API 명세이지 CLI 배포 증거가 아니다.
2. 배포물이 없다면 OpenAPI의 필요한 경로만 호출하는 작은 CLI와 MCP 어댑터를 직접 만든다. 두 어댑터는 같은 HTTP 클라이언트·인증·응답 정규화 코드를 공유한다. 1.1에서 이 구현 사실을 공개하고 두 인터페이스를 비교한다.
3. GCS 계정의 회의실 예약 권한, API 토큰 발급 권한, 테스트용 예약을 해도 되는 시간/회의실을 확인한다.
4. Google 계정의 Calendar 쓰기 권한과 팀원 이메일 접근 범위를 확인한다. 학생 검색 결과에 없는 외부 인원은 별도 검증된 주소를 입력받는다.
5. [NeoFirm 참고 보고서](https://drive.google.com/file/d/1KcP6DBSkAqmGOTyu85zpXhAuKzR3nnYh/view?usp=drive_link)의 열람 권한·파일 형식 및 **몰입캠프 2일차 과제 원문**을 확보한다. 이 로드맵 작성 환경에서는 해당 Drive 파일 내용을 열람하지 못했다.
6. “클코”가 **Claude Code**를 뜻하는지 수업 문구에서 확인한다. 다른 도구라면 2번의 오케스트레이터만 교체한다.

## 2. 프로젝트 폴더와 원칙

```text
assignment/
├── README.md                         # 재현 절차, 환경/버전, 실행 명령
├── docs/
│   ├── 1-1-comparison.md             # MCP·CLI 측정값과 해석
│   ├── 1-2-booking-evidence.md       # 예약/일정 검증(개인정보 가림)
│   ├── neofirm-requirements.md        # 과제 원문에서 추출한 요구사항
│   └── decisions.md                   # 확인 결과와 결정 변경 이력
├── pulse/
│   ├── client/                        # 공통 HTTP 호출·인증·에러 처리
│   ├── cli/                           # 제공 CLI가 없을 때만 제작
│   └── mcp/                           # 제공 MCP가 없을 때만 제작
├── skills/gcs-meeting-booker/SKILL.md
├── scripts/                           # 비교 실험·예약·NeoFirm 실행
├── fixtures/                          # 가짜 API 응답, 테스트 입력
├── inputs/                            # 과제 원문, 허용된 참고자료
├── runs/                              # 실행별 로그·중간 산출물
└── output/                            # 발표자료·PDF·최종 보고서
```

- 비밀값은 OS 키체인 또는 제외된 로컬 환경 변수/인증 저장소에 둔다. API 토큰·Google 쿠키·OAuth 자격 증명·학생 이메일이 Git/실행 로그/발표자료에 들어가지 않게 한다.
- 기록에는 실행 시각(KST), CLI 버전, 모델, 호출 경로, 마스킹된 결과 ID를 남긴다. 원본 개인정보는 제출 증거에서 가린다.
- 현재 없는 CLI 명령을 미리 사실처럼 쓰지 않는다. 제공 도구가 있으면 `--help`와 해당 버전의 문서로 실제 명령과 인자를 채운다.

## 3. 단계별 실행

### Phase 0 — 환경 및 인증 준비

**작업**

1. Codex CLI, GCS-PULSE CLI/MCP(제공 여부 확인), GWS CLI, Claude Code, 선택한 NotebookLM CLI의 설치 경로·버전·도움말을 `docs/decisions.md`에 기록한다.
2. GCS 웹에 정상 로그인한 계정에서 API 토큰을 발급하고 1회 반환된 원문을 안전하게 보관한다. 토큰 사용 헤더를 **읽기 전용 호출**로 확인한다. `GET /meeting-rooms`와 `GET /users/students/search`가 작동하면 스모크 테스트 통과.
3. GWS: 공식 저장소의 해당 버전 설치 지침에 따라 설치하고 `gws auth setup`(필요한 `gcloud`가 없다면 수동 OAuth 설정) → `gws auth login`으로 Calendar 권한을 부여한다. `gws calendar --help`, Calendar 읽기 명령으로 계정/시간대를 확인한다. 1.2는 **GWS MCP가 아닌 CLI**를 사용한다.
4. NotebookLM CLI는 수업에서 지정한 배포물이 있으면 그것을 사용한다. 없으면 `notebooklm-py` 같은 커뮤니티 CLI를 **명시적으로 선택·버전 고정**하고 로그인 및 읽기 조회를 검증한다. 이 구현은 비공식·문서화되지 않은 API에 의존하므로 변경 시 막힐 수 있다.
5. Claude Code의 비대화형 실행 및 Agent 기능을 사용할 수 있는지 확인한다. 과제 2는 클코를 실제로 실행해야 하므로 Codex의 내장 토론만으로 대체하지 않는다.

**현재 증거:** 사용자가 `.env`를 읽는 `python3 -m scripts.check_pulse_auth`를 실행해 `configured: ok, rooms=14`를 확인했다. 이는 GCS 회의실 목록 읽기 1회 성공 증거이며 네 도구군 전체의 Phase 0 완료는 아니다.

**완료 조건:** 비밀값 노출 없이 네 도구군(GCS CLI, GCS MCP, GWS CLI, Claude Code + NotebookLM CLI)의 버전/인증/읽기 호출을 재현할 수 있다. 제공 GCS 도구가 없다면 Phase 1의 구현 경로로 넘어간다.

### Phase 1 — 1.1 GCS-PULSE MCP vs CLI 비교

**1단계: 도구 준비.** 제공 CLI/MCP가 있으면 그대로 사용한다. 둘 중 하나/둘 다 없으면 `meeting-rooms list`, `reservations list --room-id ... --date ...`, `students search --query ...`에 해당하는 최소 기능을 구현한다. MCP는 같은 기능의 좁은 도구 3개를 노출한다. 실제 이름·옵션은 구현 후 README에 확정한다.

**2단계: 동일한 읽기 전용 작업 3개를 양쪽에서 각각 실행.**

| 사례 | 동일 입력 프롬프트의 요지 | 동일해야 할 답 |
|---|---|---|
| A | 내 계정으로 접근 가능한 GCS 회의실 이름과 ID 목록 | 목록과 정렬 규칙 |
| B | 지정 날짜/회의실의 예약 시간대 | 동일 날짜·ID의 예약 구간 |
| C | 지정 학생 이름의 검색 결과(동명이인 포함) | 결과 수·이름·팀 정보(제출 시 이메일 마스킹) |

측정 직전 날짜, room ID, 검색어를 고정한다. 양쪽 모두 같은 계정, 동일 모델·프롬프트·환경·응답 형식, **새 세션**, 같은 API 응답 조건을 사용한다. 변하는 데이터라면 짧은 시간에 교차 실행하거나 공통 응답 fixture로 재현성을 확보한다. 설정·인증 단계의 비용과 실제 작업 비용은 따로 집계하고, 냉시작과 반복 호출도 구분한다. 가능하면 사례별 3회 반복 후 중앙값을 쓴다.

**3단계: 측정.** Codex CLI에서 `codex exec --json`으로 실행 이벤트(JSONL)를 저장하고 `turn.completed`의 `usage.input_tokens`, `usage.output_tokens`를 집계한다(현재 설치 버전의 이벤트 형식 확인). 시작·종료 시각, 도구 호출 횟수, 성공·오류, 재질문 횟수도 기록한다. `GET /users/me/token-usage`는 **GCS-PULSE 자체 사용량**이고 Codex LLM 토큰 수가 아니다. 두 수치를 혼합하지 않는다.

| 팀/사례/반복 | 방식 | 입력 토큰 | 출력 토큰 | 합계 | 초 | 호출 수 | 결과 일치 | 추가 조치/오류 |
|---|---|---:|---:|---:|---:|---:|---|---|
| 팀 A / A / 1 | MCP |  |  |  |  |  |  |  |
| 팀 A / A / 1 | CLI |  |  |  |  |  |  |  |

**해석 기준:** 인터페이스의 도구 정의/초기 컨텍스트, 명령 탐색, 출력 길이, 오류 복구가 차이에 기여했는지 실행 기록으로 설명한다. 결과가 같지 않으면 효율 숫자만 비교하지 않는다. 팀마다 시행했음을 보여주는 팀별 로그/표와 전체 요약을 함께 제출한다.

**산출물/완료:** `docs/1-1-comparison.md`, 원본 실행 기록(민감정보 제거본), 팀별 재현 명령. 두 방식이 같은 3개 작업을 성공하고 숫자와 경험 평가가 모두 채워져야 완료.

### Phase 2 — 1.2 두 CLI의 단독 동작 확인

**GCS-PULSE CLI:** 목록 조회 → 날짜별 예약 조회 → 테스트 가능 시간 슬롯 선택 → 예약 생성 → 예약 ID 재조회/검증 → 필요 시 취소. 무료 구간 판정은 각 기존 예약과 `[start, end)` 구간이 겹치는지 비교한다. 예비 조회 직후 다른 사람이 예약할 수 있으므로 **POST 응답으로 최종 성공 여부**를 판단한다. 네트워크가 끊겼다면 원격 상태부터 재조회해 중복 생성 여부를 확인한다.

**GWS CLI:** 캘린더 읽기/충돌 확인 → 테스트 이벤트 생성 → 참석자 이메일 포함 → 초대 알림 설정 → ID로 재조회 → 테스트 이벤트 정리. Calendar API의 `events.insert`는 `sendUpdates=all`로 전체 게스트 알림을 요청할 수 있다. GWS CLI의 실제 버전에서 `gws calendar events insert --help`, `gws schema calendar.events.insert`, `--dry-run`으로 인자와 요청을 확인한다. 예시 형태는 아래와 같되 실행 전 도움말과 생성 결과로 검증한다.

```bash
gws calendar events insert \
  --params '{"calendarId":"primary","sendUpdates":"all"}' \
  --json '{"summary":"프로젝트 회의","start":{"dateTime":"2026-10-07T14:00:00+09:00","timeZone":"Asia/Seoul"},"end":{"dateTime":"2026-10-07T15:00:00+09:00","timeZone":"Asia/Seoul"},"attendees":[{"email":"verified@example.com"}],"location":"GCS 회의실 이름"}' \
  --dry-run
```

`--dry-run`은 요청 확인용이다. 실제 초대 여부는 실행 후 이벤트의 참석자·상태를 확인한다. **API가 초대 알림을 요청/처리했다는 것과 메일 수신자가 받거나 수락했다는 것은 다르다.** Calendar 이벤트에 회의실의 Google resource 주소를 참석자로 추가하는 방식은 GCS 회의실 예약과 별개이며 해당 리소스가 실제로 존재할 때만 검토한다.

**완료 조건:** 각 CLI의 실사용 경로를 별도로 검증하고 예약 ID, Calendar 이벤트 ID 및 롤백 명령을 확보한다.

### Phase 3 — 1.2 `gcs-meeting-booker` Skill 완성

**입력 계약:** 회의명/목적, 시작 시각·종료 또는 소요시간, 참석자 이름/이메일, 회의실 선호. 상대 날짜(`내일`)는 `Asia/Seoul` 기준 절대 시각으로 변환하고 과거 시각·시작≥종료를 거부한다. 참석자 검색에서 0명 또는 여러 명이 나오면 정확한 사람/이메일을 확인한 뒤 진행한다.

**Skill의 실행 순서**

1. 사용자 요청을 정규화하고 계정·시간대·Calendar ID를 확인한다.
2. GCS CLI로 학생을 검색하고 이메일/팀을 검증한다. 중복 결과는 임의 선택하지 않는다.
3. GCS CLI로 후보 회의실과 해당 날짜 예약을 읽고 구간 겹침을 계산한다. Calendar 주최자 일정의 겹침도 조회한다.
4. 시작 전 최종 요약(회의명, 시간, 방, 참석자)을 기록하고 GCS 예약을 생성한다. 반환된 예약 ID를 안전하게 저장한다.
5. GWS CLI로 Calendar 이벤트를 생성한다. `sendUpdates=all`, 참석자·시각·장소·예약 식별자를 넣는다. 생성된 이벤트 ID를 저장한다.
6. GCS 예약과 Calendar 이벤트를 각각 재조회해 시각·방·참석자·ID를 대조한 뒤 성공 결과를 보고한다.

**부분 실패 처리:** GCS 예약 성공 뒤 Calendar 생성 실패 시, 먼저 Calendar에 이벤트가 생성됐는지 재조회한다. 없고 GCS 예약 취소 권한(`can_cancel`)이 확인되면 예약 취소를 시도한다. 취소 불가/상태 불명확이면 예약 ID를 알려 주고 수동 처리로 올린다. Calendar가 이미 생성됐거나 초대가 발송됐으면 임의로 다시 POST하지 않는다. 보상 작업도 실패할 수 있으므로 단계별 상태를 남긴다. 빈 방이 없으면 대안 시간/방을 제시한다.

**구현물:** `skills/gcs-meeting-booker/SKILL.md`에는 호출 조건·필수 입력·CLI 호출 순서·중단 조건·검증·복구 지침을, `scripts/`에는 반복 가능한 파싱·조회·예약 로직을 둔다. Skill 본문만으로 구현했다고 주장하지 않는다. 가짜 응답으로 동명이인·충돌·Calendar 실패·중복 재시도 4개를 점검한 뒤 허용된 계정에서 실제 1회 흐름을 실행한다.

**완료 조건:** 한 자연어 요청에서 두 **CLI**가 실제 호출되고, GCS 예약 ID 및 Calendar 이벤트 ID가 일치하며 참석자/초대 알림 설정을 확인한다. `docs/1-2-booking-evidence.md`에 재현 방법과 마스킹된 증거를 기록한다.

### Phase 4 — 과제 2 입력·NotebookLM 조사

**현재 진입 상태:** 보고서와 참고 발표를 실제 열람하고 일차자료 5개를 대조했다. 비공식 `notebooklm-py 0.8.4`는 설치됐지만 최초 인증은 미완료다. 공식 과제 공지는 미확인이라 보고서 p.18–20·임시 7분을 적용한 검토용 초안을 만들었다. NotebookLM 조사·source 등록은 완료로 표시하지 않는다.

1. 과제 원문을 `docs/neofirm-requirements.md`로 옮겨 발표 시간, 팀별 관점, 필수 분석틀, 제출 형식, 평가 기준을 체크리스트로 만든다. 참고 보고서는 **참고자료**로 취급하고 사실 검증을 생략하지 않는다.
2. 보고서 Drive 권한과 MIME 유형을 확인한다. 선택한 NotebookLM CLI 버전에서 접근 가능한 PDF라면 `source add-drive ... --mime-type pdf` 또는 로컬로 적법하게 받은 PDF를 `source add ./inputs/report.pdf`로 넣는다. URL만 보고 내용을 읽었다고 기록하지 않는다.
3. NotebookLM 노트북을 새로 만들고 보고서와 추가 출처를 source ID로 기록한다. 질문을 분리해 **핵심 주장 / 근거 / 시점 / 반례 / 확인할 공백**을 JSON 결과와 함께 추출한다. 웹 리서치가 필요하면 일차자료(기업·공공 통계·원문 보고서)를 우선 추가한다.
4. `runs/<run-id>/research.md`와 `sources.json`에 모든 수치·주장에 대한 원문 링크/문서 위치·조회일·신뢰도를 남긴다. 확인되지 않은 것은 `미확인`으로 표기한다. 출처가 없는 단정적 숫자는 슬라이드에 넣지 않는다.

**NotebookLM CLI 예시(선택한 구현의 실제 도움말로 확인):** `notebooklm create "NeoFirm" --json`, `notebooklm source add ./inputs/report.pdf -n <notebook-id> --json`, `notebooklm ask "핵심 주장과 원문 근거는?" -n <notebook-id> --json`. 초기 인증은 대화형 1회 작업이며 이후 자동 실행 단계에서 재사용한다. 비공식 CLI의 인증이 만료되면 자동 작업을 실패 처리하고 재인증한다.

**완료 조건:** 원문과 추가 자료의 접근 권한이 검증되고, 근거를 역추적할 수 있는 조사 파일이 생성된다.

### Phase 5 — Codex에서 AI Agent 토론 자동화

Codex 실행 흐름이 같은 `research.md`와 과제 요구사항을 **서로 독립된 역할**에 전달한다. 원문 기반 선행 토론은 실제 실행했고 NotebookLM 조사부터 연결하는 CLI 실행은 대기 중이다.

| 역할 | 산출할 질문 |
|---|---|
| 시장/고객 Agent | 문제의 실재성, 고객·시장 규모 근거, 지불 의사 |
| 실행/기술 Agent | 구현·운영 가능성, 제약, 필요한 검증 |
| 반대/검증 Agent | 약한 근거, 과장, 반례, 잠재 비용 |
| 종합 Agent | 쟁점별 판단, 합의·이견·남는 실험 |

**최소 토론 프로토콜:** ① 각 Agent 독립 입장문 → ② 다른 Agent의 구체적 주장에 대한 근거 있는 반박 → ③ 재반론/수정 → ④ 종합. 각 주장에는 `claim_id`, 근거 source ID, 불확실성을 붙인다. 순차적인 단일 모델 요약을 “Agent 토론”으로 포장하지 않는다. Claude Code의 실제 Agent/서브에이전트 기능 또는 명시적 독립 세션을 쓰고 프롬프트·실행 로그를 보존한다.

**완료 조건:** `debate.md`에 화자와 라운드가 남고, `conclusion.md`의 결론·미해결 쟁점이 원문 근거/토론 주장에 연결된다. 다수결보다 근거와 반론 처리의 질을 평가한다.

### Phase 6 — 발표자료 생성 및 검사

1. `research.md` + `debate.md` + `conclusion.md` + 과제 요구사항으로 발표 핵심 메시지와 장별 역할을 먼저 정한다.
2. `slides-outline.md`를 만든다: 각 슬라이드의 **제목/핵심 한 문장/수치·시각자료/출처/발표 멘트**. 필요한 장수는 과제 원문의 발표 시간에 맞춘다(임의로 10장 고정하지 않는다).
3. Codex가 슬라이드 JSON을 생성하고 독립 검증 세션·로컬 렌더러가 `output/<run-id>/neofirm-final.pptx`와 PDF·대본을 만든다. 이번 최소 구현의 PPTX 본문은 PDF 이미지이고 발표자 노트는 텍스트다. 한글·출처·배치를 검사하고 편집 가능성의 한계를 명시한다.
4. 실제 렌더링을 확인한다: 잘린 텍스트, 글꼴 대체, 표·그래프 값, 읽을 수 있는 글자 크기, 인용/출처, 발표 시간. 발표자 노트 또는 대본에 Agent 토론으로 인해 바뀐 결론을 반영한다.

**완료 조건:** 발표 파일이 열리고 모든 슬라이드의 핵심 사실이 조사 파일의 출처로 추적된다. 자료조사와 토론 기록 없이 PPT만 만든 경우는 미완료다.

### Phase 7 — 한 번에 재실행하고 제출

`sh scripts/run-neofirm.sh`로 최초 인증 후 `입력 검사 → NotebookLM source 확인/추가 → 조사 → Codex 독립 세션 토론 → 스토리라인 → 내용 검증 → PPT/PDF 렌더링`을 수행한다. 입력 해시·run ID·버전·source ID·단계 상태를 기록하며 `--resume`으로 이어서 실행한다. 불확실한 쓰기는 원격 목록으로 대조하고 끝내 확인하지 못하면 중단한다. 인증·자료 접근 실패를 성공으로 처리하지 않는다.

**완료 조건:** 사람이 중간 프롬프트를 붙여넣지 않아도 입력에서 최종 발표 파일까지 한 번에 도달하는 성공 실행 로그가 있다. 첫 OAuth/권한 승인과 평가자의 최종 품질 검토는 별도로 기록한다.

## 4. 바로 실행할 순서와 점검표

- [ ] 공식 과제 원문, GCS-PULSE CLI/MCP 배포 여부, “클코” 의미 확인
- [ ] 도구 버전/인증/읽기 요청 검증; API 토큰 헤더 형식 확인 (GCS 회의실 목록만 사용자 환경에서 성공)
- [x] 제공 CLI/MCP가 없을 때 공통 클라이언트와 두 어댑터 최소 구현 (현재 환경에서 제공물 미발견; 로컬 fallback 구현)
- [ ] 모든 팀에서 동일 시나리오 3개, MCP/CLI 각 3회 실행·JSONL 저장·토큰 집계 (`team-a` 완료, 다른 팀 미실행)
- [x] `team-a` 1.1 비교표와 오류·사용 경험 작성
- [x] GCS 예약과 Google Calendar 이벤트를 각각 단독 검증
- [x] Skill 구현, 부분 실패 처리, fixture 테스트와 비라이브 preview 증거 확보
- [x] 허용된 계정으로 GCS 예약·Calendar 이벤트·초대 알림 요청·실제 초대메일 수신·참석자 응답을 1회 검증 (응답: `declined`)
- [ ] NotebookLM CLI 설치·인증 및 보고서 source 등록·조사·출처 추적
- [x] 원문 기반 Codex Agent 독립 분석·반박·재반론·종합 (3역할×3라운드; NotebookLM 연계 실행은 대기)
- [ ] 슬라이드/대본 생성, 렌더링과 출처 점검
- [ ] 한 명령 재실행, 로그와 제출 파일 정리

## 5. Work에서 프로젝트를 시작할 때 사용할 요청

> 이 로드맵을 기준으로 과제 1.1부터 순서대로 진행해줘. 먼저 강의에서 제공한 GCS-PULSE CLI/MCP가 있는지와 첨부 OpenAPI의 인증 방식을 확인하고, 제공물이 없다면 공통 HTTP 클라이언트 위에 최소 CLI/MCP를 구현해줘. 각 단계가 끝나면 이 문서의 완료 조건과 증거 파일을 채우고 다음 단계로 진행해줘. 1.2는 GCS-PULSE **CLI와 GWS CLI**를 사용하고, 2번은 NeoFirm 과제 원문·보고서를 확보한 뒤 **Claude Code와 NotebookLM CLI**를 실제로 호출해 조사, Agent 토론, 발표자료를 생성해줘. 모르는 명령·권한·보고서 내용은 추측하지 말고 확인 결과를 기록해줘.

## 6. 참고 문서 및 판단 근거

- 프로젝트에 첨부된 `openapi.json`: API 경로/스키마에 관한 이 문서의 기준. Swagger: <https://api.1000.school/docs#/>
- [Google Workspace CLI 공식 저장소](https://github.com/googleworkspace/cli): 설치, `auth setup`/`auth login`, CLI 명령 및 `--dry-run`. 명령은 현재 설치 버전의 `--help`로 다시 확인.
- [Google Calendar `events.insert` 공식 문서](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert): `attendees`와 `sendUpdates=all` 알림 동작.
- [Codex 실행 기록 측정 예](https://developers.openai.com/blog/eval-skills): `codex exec --json` JSONL, `turn.completed` 토큰 사용량.
- [Claude Code CLI 공식 문서](https://code.claude.com/docs/en/cli-usage): 비대화형 `claude -p`, JSON 출력 및 실행 옵션.
- [notebooklm-py 저장소](https://github.com/teng-lin/notebooklm-py) 및 [CLI 명령 참고](https://github.com/teng-lin/notebooklm-py/blob/main/docs/cli-reference.md): 지정 CLI가 없을 때의 **비공식** 후보. 설치/인증과 명령은 고정 버전 문서로 재검증.

**과거 안내의 정정:** “GCS-PULSE CLI/MCP가 이미 제공된다”는 주장은 확인되지 않았다. 또한 GWS MCP 연결은 과제 1.2의 필수 경로가 아니다. 회의실의 Google Calendar resource 이메일도 이 OpenAPI에서 확인되지 않았다.
