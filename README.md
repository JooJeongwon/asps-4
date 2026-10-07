# GCS-PULSE · GWS · NeoFirm 과제

GCS-PULSE MCP/CLI 비교, GWS Calendar 예약 Skill, NeoFirm 자료 조사·AI Agent 토론·발표자료 생성을 한 저장소에 정리한 프로젝트다.

현재 상태:

- **1.1 MCP·CLI 비교:** Team A 기준 3개 시나리오를 MCP·CLI 각각 3회씩 실행해 18/18 성공. 다른 팀 계정 비교는 미완료.
- **1.2 예약 Skill:** GCS 예약, GWS Calendar 일정, `sendUpdates=all` 초대, 재조회·보상 취소 로직과 실제 실행 증거 완료.
- **2. NeoFirm:** NotebookLM 조사 3회, 독립 Codex Agent 9회 토론과 종합, 11장 PPTX/PDF·대본 생성 완료. 공식 과제 공지 대조와 실제 리허설은 남음.

핵심 문서는 [1.1 비교](docs/1-1-comparison.md), [1.2 결과](1.2.md), [2번 과제 답변](2.md), [로드맵](ROADMAP.md)이다.

## 최종 산출물

NeoFirm 최종 발표는 현재 확보한 자료와 임시 7분 조건으로 작성했다.

- [최종 발표 PPTX](output/neofirm-20261007T032143604608Z/neofirm-final.pptx)
- [최종 발표 PDF](output/neofirm-20261007T032143604608Z/neofirm-final.pdf)
- [발표 대본](output/neofirm-20261007T032143604608Z/speaker-notes.md)
- [슬라이드 미리보기](output/neofirm-20261007T032143604608Z/contact-sheet.png)

보고서 PDF, NotebookLM 인증 상태, `.env`, 원격 실행 로그와 원본 입력은 개인정보·자격증명·자료 권한 보호를 위해 공개 저장소에 포함하지 않는다. 로컬 실행 증거는 `runs/`에 남기며 `.gitignore`로 제외한다. 보고서의 공개 출처와 인용 위치는 [NeoFirm 증거](docs/2-neofirm-evidence.md)에 정리했다.

## 준비

- Python 3.10 이상. 현재 검증 환경은 Python 3.14.7이다. GCS 기능은 외부 Python 패키지가 필요 없고, NeoFirm은 아래 별도 가상환경을 사용한다.
- 첨부 명세는 `openapi.json`이다. API 호스트 후보 `https://api.1000.school`은 인증 없는 요청의 401 응답으로 확인했다.
- 수업에서 제공한 CLI/MCP가 발견되면 우선 그것을 사용하고 이 어댑터 사용 여부를 다시 결정한다.
- **인증 헤더 이름과 값은 아직 확인되지 않았다.** 서비스 안내나 허용된 테스트 계정으로 확인한 뒤 셸의 비밀 환경 변수에 설정한다. 값은 헤더에 보낼 전체 문자열이다. `.env`나 인증 파일은 커밋하지 않는다.

```sh
cp .env.example .env
# .env에서 PULSE_AUTH_HEADER와 PULSE_AUTH_VALUE를 입력한 뒤 실행
python3 -m scripts.check_pulse_auth
# CLI와 MCP 클라이언트는 프로젝트 루트의 `.env`를 읽는다. 셸 환경 변수는 `.env`보다 우선한다.
python3 -m pulse.cli meeting-rooms list
python3 -m pulse.cli reservations list --room-id 1 --date 2026-10-07
python3 -m pulse.cli students search --query '<검색어>'
```

`PULSE_AUTH_VALUE`에는 서버에 보낼 전체 값을 넣는다. 현재 사용자 환경의 설정으로 회의실 목록 14개 조회가 한 번 성공했다. 인증 헤더의 공식 문서 근거는 아직 없다.

`python3 -m scripts.check_pulse_auth`는 실제 예약에 필요한 `/meeting-rooms`, 오늘(Asia/Seoul) 기준 모든 방의 예약 목록, 개인정보 없는 학생 검색을 읽는다. `/auth/me`는 브라우저 세션 전용일 수 있어 인증 관문으로 사용하지 않는다. 출력에는 성공 여부와 개수만 남기며 실패 시 추가 형식으로 재시도하지 않는다.

CLI는 JSON 한 줄을 출력한다. 학생 이메일은 비교 로그에 남지 않도록 제외한다. 오류는 표준 오류에 종류와 상태만 남기고 종료 코드 1을 반환한다. HTTP 오류 종류: `auth_failed`, `forbidden`, `invalid_input`, `conflict`, `network_uncertain`, `invalid_response` 등.

MCP 서버는 프로젝트 루트에서 `python3 -m pulse.mcp`로 실행한다. `meeting_rooms_list`, `reservations_list`, `students_search` 세 도구를 제공한다. Codex 연결 시 설치 버전의 `codex mcp add --help`를 확인한 뒤 프로젝트 루트에서 다음 명령을 사용한다. 비밀값은 Codex 설정에 기록하지 않고 클라이언트가 프로젝트 `.env`에서 읽는다. 이 명령은 인증이 준비된 뒤 실행한다. 서버는 현재 2025-11-25/2025-06-18 MCP 초기화 방식을 구현했다. 첫 Codex 통합 시도는 인증 환경 전달 문제로 실패했으며 수정 후 재실행해야 한다.

```sh
codex mcp add gcs-pulse --env "PYTHONPATH=$(pwd)" -- python3 -m pulse.mcp
```

## 로컬 검증

```sh
python3 -m unittest discover -s tests -v
python3 -m pulse.cli --help
```

## 1.1 사전 점검

네트워크 접근이 가능한 사용자 환경에서 `ROOM_ID`, `DATE`, `QUERY`를 실제 테스트 값으로 정해 두 프로세스의 결과를 비교한다. 스크립트가 `.env`를 읽으며, 출력은 일치 여부뿐이고 학생 이름·이메일·회의실 정보는 표시하지 않는다.

```sh
python3 -m scripts.check_pulse_parity --room-id "$ROOM_ID" --date "$DATE" --query "$QUERY"
```

이 점검이 성공해도 1.1은 끝나지 않는다. 각 팀의 새 Codex 세션에서 MCP/CLI를 같은 3개 시나리오로 실행하고 `codex exec --json` 이벤트, 토큰·시간·도구 호출 수, 익명화한 결과를 [비교 기록](docs/1-1-comparison.md)에 채워야 한다. 현재 샌드박스의 `codex exec`는 `Operation not permitted`로 초기화에 실패한다.

GCS 인증이 준비되면 같은 계정·날짜·회의실·검색어로 CLI와 MCP를 각각 새 Codex 세션에서 호출하고, 민감정보를 제거한 `codex exec --json` 로그로 토큰·시간·호출 횟수를 집계한다. `GET /users/me/token-usage`는 이 지표로 사용하지 않는다. 실제 실행 결과는 [비교 기록](docs/1-1-comparison.md)에 추가한다.

## 1.1 실서버 측정 러너

네트워크와 Codex 설정 파일을 쓸 수 있는 사용자 터미널에서 실행한다. `codex mcp add`에는 비밀값을 넣지 않으며, CLI와 MCP 클라이언트가 프로젝트 `.env`를 직접 읽는다.

```sh
codex mcp add gcs-pulse --env "PYTHONPATH=$(pwd)" -- python3 -m pulse.mcp
python3 -m scripts.run_1_1_comparison \
  --room-id "$ROOM_ID" --date "$DATE" --query "$QUERY" \
  --team team-a --repeats 3
```

셸 변수를 정하지 않았다면 빈 문자열이 전달되므로 아래처럼 고정된 읽기 전용 시험값을 직접 넣는다. `2`가 해당 계정에서 읽을 수 있는 실제 room ID인지 먼저 확인하고, 필요하면 같은 형식으로 교체한다. `__no_match__`는 학생 개인정보를 조회하지 않도록 선택한 검색어다.

```sh
python3 -m scripts.run_1_1_comparison \
  --room-id 2 --date 2026-10-07 --query '__no_match__' \
  --team team-a --repeats 3
```

`runs/1-1-*/summary.json`에는 토큰·초·도구 호출 수·성공 여부·결과 해시만 저장된다. 함께 저장되는 JSONL/로그는 토큰·검색어·학생 이메일·학생 이름을 마스킹한다. 기본 모델은 `gpt-5.6-luna`이며 MCP와 CLI에서 동일하게 사용한다.

러너는 CLI 명령의 네트워크 접근을 위해 두 경로 모두 Codex `workspace-write` 샌드박스와 `sandbox_workspace_write.network_access=true`를 사용한다. 실제 프롬프트는 GCS 읽기 한 번만 허용한다. 한 Codex 세션이 기본 120초를 넘기면 해당 회차를 `codex_exec_timeout`으로 기록하고 다음 회차로 넘어간다. 필요하면 `--timeout-seconds`로 조정한다.

## 1.2 예약 Skill

자세한 호출 순서와 중단·보상 규칙은 [`skills/gcs-meeting-booker/SKILL.md`](skills/gcs-meeting-booker/SKILL.md)에 있다. 스크립트는 기본적으로 읽기 전용 preview를 실행하고, 사용자가 확인한 뒤 `--confirm`을 붙여 GCS 예약과 Calendar 이벤트를 생성한다. GWS Calendar insert에는 `sendUpdates=all`이 들어간다.

가장 간단한 실행은 다음 한 줄이다. 제목·시간·방·참석자만 대화형으로 입력하면 마지막에 한 번 확인하고 예약한다.

```sh
python3 scripts/book_meeting.py --interactive
```

```sh
python3 scripts/book_meeting.py \
  --title '프로젝트 회의' \
  --start '2026-10-07T14:00:00+09:00' \
  --end '2026-10-07T15:00:00+09:00' \
  --room-id 2 \
  --student-query '정확한 팀원 이름'

# preview 확인 후 같은 명령에 --confirm 추가
```

지원 CLI는 `python3 -m pulse.cli reservations create/cancel`과 `gws calendar events list/insert/get/delete`다. GWS의 실제 계정 인증과 Discovery가 준비되지 않았으므로 현재 문서의 실행 결과는 fixture/preview 증거이며 라이브 예약 성공을 의미하지 않는다.

## 2. NeoFirm — Codex + NotebookLM CLI

참고 보고서의 로컬 PDF가 `inputs/ChatGPT-2026-NeoFirm-Report.pdf`에 있어야 한다. 이번 요청은 Codex를 사용하며 Claude Code는 필요 없다. 과제 공지가 따로 없으므로 보고서 p.18–20을 기준으로 NDA 서비스 제안·7분 발표를 구성한다. 조건이 다르면 `--topic`, `--minutes`와 요구사항 문서를 수정한다.

새 환경에서 설치 및 최초 Google 로그인:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-neofirm.txt
sh scripts/login-neofirm.sh
```

시스템 Chrome이 필요하다. 로그인은 비공식 `notebooklm-py 0.8.4`를 사용한다. 로그인 스크립트는 기존 전용 프로필을 보존하고 Google 로그인 창에서 최대 5분 기다린다. 열린 창에서 Google 로그인 후 NotebookLM 노트북 목록을 연다. Google 세션 확인 후 창이 닫혔다가 CLI 저장용으로 다시 열릴 수 있다. 최종 `AUTH OK: status=ok, token_fetch=true`가 나와야 인증 성공이다. URL 도착이나 `Authentication saved`만으로는 성공이 아니다. `.local/notebooklm/`의 쿠키·브라우저 프로필을 공유하거나 Git에 넣지 않는다. Codex CLI도 설치·로그인돼 있어야 하며, 네트워크와 Codex app-server가 작동하는 사용자 터미널에서 실행한다.

인증 후 자동 실행:

```sh
sh scripts/run-neofirm.sh
# 필요할 때만 발표 조건이나 모델을 지정한다.
sh scripts/run-neofirm.sh --minutes 7 --topic '한국 B2B 표준 NDA 검토 결과 서비스'
```

보고서·일차자료의 NotebookLM 등록 → 근거 포함 조사 3회 → 독립 Codex 세션 3역할×3라운드 → 종합 → 슬라이드 JSON → 독립 내용 검증 → PDF 렌더링·PPTX·대본 순서로 실행한다. 각 라운드의 3개 역할은 병렬로 실행하고 다음 라운드는 모두 끝난 후 시작한다. 기본 모델은 사용자 Codex 설정을 사용하며 필요하면 `--model`을 명시한다. 최초 인증을 제외하고 중간 프롬프트를 수동 입력하지 않는다.

`runs/neofirm-<run-id>/`에 `state.json`, 조사·출처·토론·결론·구성안·프롬프트·익명화된 로그를 남긴다. 성공한 실행만 `output/neofirm-<run-id>/`로 복사한다. PPTX 본문은 한글·배치를 보존한 이미지이고 발표자 노트는 텍스트다. `quality.json`에 한글 추출, 잘림, 인용 ID·위치, 파일 재열림, 시간 합계를 기록한다. 대본 시간은 초당 한글 약 7자 가정이며 실제 리허설을 대신하지 않는다.

실패 후 같은 입력·옵션으로 이어서 실행:

```sh
sh scripts/run-neofirm.sh --resume runs/neofirm-<run-id>
```

완료 단계와 성공한 세션을 재사용한다. 조사에서는 NotebookLM 기본 숫자 인용과 실제 `references`를 사용한다. 빈 답변·인용 없는 응답은 `research-N-rejected-K.json`으로 보존하고, 해당 질문을 최대 두 번 새로 요청한다. 두 번 모두 실패하면 토론·발표로 넘어가지 않는다. 기존 실패 응답을 캐시 성공으로 취급하지 않으며 대화 삭제 옵션 `--new`도 사용하지 않는다.

발표는 형식·페이지·시간을 먼저 검사하고 독립 내용 검사를 수행한다. 거부되면 이전 슬라이드와 구체적 지적을 생성기에 전달해 수정·재검사하며 한 실행에 최대 3개 후보를 시도한다. 실패는 성공으로 바꾸지 않으며, 모두 거부되면 최종 파일을 제출하지 않고 중단한다. 각 후보의 원본 출력·검사·로그는 `presentation-attempts/<시각>/`에 보존한다. 기존 거부 후보도 재개 시 수정 근거로 사용한다. 사실/자기보고는 실제 근거가 필수이고, 제안·미확인은 확인 범위·검증 방법을 구별해 적는다. 토론 수정·철회는 보고서 대신 실제 claim_id로 추적한다.

원격 쓰기 결과가 불확실하면 목록에서 노트북 제목·source ID/URL을 대조한다. 생성 여부가 끝내 확인되지 않으면 재생성하지 않고 `state.json`의 `pending_notebook`/`pending_write`를 남겨 중단한다. 이 경우 NotebookLM에서 해당 대상 상태를 확인한 뒤에만 pending 상태를 수동 정리하고 재시도한다. 입력·실행 코드·모델/시간/주제를 바꾸면 원칙적으로 새 run을 시작해야 한다. 2026-10-07 인용·발표 복구에 한해 `neofirm-20261007T032143604608Z`는 입력·옵션 불변과 수정 대상 단계를 확인하고 코드 hash를 갱신했다(`state.json/resume_updates`). 이 실행은 같은 `--resume` 명령으로 이어가며 노트북·자료를 재생성하지 않고 성공한 조사·토론을 재사용한다.

Google/LLM 호출 없는 준비·검증:

```sh
sh scripts/run-neofirm.sh --prepare
.venv/bin/python -m unittest discover -s tests -p test_neofirm.py -v
```

구조화된 검사 응답은 글자 수가 아니라 JSON 필드·타입으로 검증한다. 동일 프롬프트의 실제 `turn.completed` 기록과 검사 대기 후보를 복구해 재개한다. 조사 완료 후 발표 재개에는 NotebookLM 인증·source 재조회가 필요 없고, 전체 완료 후 재실행은 모델 호출 없이 기존 최종 파일을 다시 게시한다.

검토용 발표 초안과 실제 라이브 실행의 구분은 [NeoFirm 증거](docs/2-neofirm-evidence.md)에 기록한다. NotebookLM 인증 누락을 성공으로 처리하지 않는다.
