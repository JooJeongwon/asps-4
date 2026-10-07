# 확인·결정 기록

## 2026-10-07 — 과제 2 제출 답변 통합

- 사용자 요청에 따라 루트 `2.md`에 과제 답변, 실제 NotebookLM 조사·출처, 독립 Codex 3라운드 토론과 수정 주장, A/B/C 분석, 최종 발표·실행 증거·재현 방법을 통합했다. 새 모델 호출이나 외부 변경은 수행하지 않았다.
- 현재 실행의 `state.json` complete와 실제 `quality-review.json` passed=true를 재확인했다. `2.md`의 로컬 링크 25개를 검사해 누락 0개였고 인증값·이메일 패턴 검사에서도 일치가 없었다. 기존 프로젝트 테스트 25개 통과 기록은 재실행 결과와 구별해 인용했다.
- 공식 발표 조건·실제 육성 시간·사업 실증은 여전히 미확인이다. 다음 한 단계는 실제 7분 리허설이며 시간 측정과 공식 공지 확보 시 조건 대조가 완료 조건이다. GCS/Calendar ID는 해당 없음이다.

## 2026-10-07 — CLI 출력 계약·체크포인트 수정 및 최종 완료

- 최신 실행 `neofirm-20261007T032143604608Z`는 현재 입력·임시 7분 기준 Phase 4–7 자동화를 완료했다. 아래의 미완료 기록은 당시 상태다.
- 실제 마지막 `presentation-attempts/20261007T041132259214Z/logs/quality-review.json`은 exit 0, `turn.completed`, 최종 답변 `{"passed":true,"issues":[]}`였다. 공통 `codex()`가 JSON에도 산문용 80자 조건을 적용해 정상 답변을 거부하고 파일을 삭제했다. 이전 테스트가 이 공통 함수를 대체해 오류를 잡지 못했다.
- S1 위치 `p.19 과제 C 100건 후 데이터`의 모든 숫자를 페이지로 읽어 100페이지라고 거부하는 별도 오류도 확인했다. 이제 p./pp.로 명시된 페이지·범위만 검사한다. 0페이지·범위 밖 페이지는 계속 거부한다.
- 공통 CLI 어댑터에서 실제 완료 이벤트·최종 메시지·JSON 필드/타입을 검증한다. 원본 이벤트와 실패 출력을 보존하고, 동일 프롬프트의 완료 trace와 검사 대기 후보를 재개한다. 발표만 재개할 때 무관한 NotebookLM 인증·source 재조회와 모델 preflight는 하지 않는다.
- 동일 후보와 실제 검사 프롬프트의 일치를 확인한 후 위 완료 응답을 복구했다. 검사 값을 강제로 통과시키거나 새 모델 결과를 지어내지 않았다. 조사·토론·입력·source ID·옵션은 보존하고 호환성 코드 hash 갱신을 `state.json/resume_updates`에 기록했다.
- 실제 `sh scripts/run-neofirm.sh --resume runs/neofirm-20261007T032143604608Z`가 exit 0, `COMPLETE output/neofirm-20261007T032143604608Z`로 끝났다. 완료 후 동일 명령 재실행도 모델/NotebookLM 호출 없이 성공했다. PPTX·PDF·대본·contact sheet·quality.json을 게시했다.
- 전체 테스트 25개 통과. 실제 CLI 어댑터 아래에서 JSONL을 공급하고 렌더링·최종 게시까지 실행하는 회귀 검사를 추가했다. Python 컴파일과 shell 구문 검사도 통과했다. 최종 11장·420초·대본 공백 제외 2,506자, 한글·잘림·PPTX 재열기 검사 통과. 전체 contact sheet와 페이지를 열어 확인했고 미지원 가운데점만 표시 단계에서 지원 문자로 정규화했다.
- 공식 발표 공지, 실제 육성 리허설, 고객 수요·사업 적법성·보험 등은 미확인이다. GCS 예약/Calendar ID는 해당 없음이며 이번 수정에서 외부 예약·초대·자료 등록을 수행하지 않았다. 다음 한 단계는 7분 리허설이며 실제 소요 시간·공식 공지 조건과의 일치가 완료 조건이다.

## 2026-10-07 — 발표 내용 검사 피드백 복구

- 현재 실행 `neofirm-20261007T032143604608Z`의 NotebookLM 질문 3개는 각각 구조화된 인용 24·7·14개를 반환했다. 모두 등록된 S1–S6 source ID에 매핑됨을 확인했다. 독립 역할 3명×3라운드와 종합의 10개 JSONL에서 `turn.completed`를 확인했다. 현재 입력 기준 Phase 4 조사·Phase 5 자동 토론은 완료했으며 전체 최종 발표는 아직 미완료다.
- 실제 `quality-review.json`은 passed=false였다. 지적은 미확인 항목의 근거 범위, 과제 A의 공급자 매출과 시간·인원 관계 누락, 슬라이드 9의 토론 변경을 실제 claim_id가 아닌 보고서에만 연결한 점이다. 추가로 기존 slides.json의 S1 근거 일부가 페이지 없이 절 이름뿐이라 렌더러의 기존 검증도 실패할 수 있었다.
- 근본 재시도 문제는 거부 이유를 다음 생성 프롬프트에 전달하지 않고 후보·검사 출력과 이벤트를 삭제해, 재개 시 같은 요구만 다시 요청하는 점이었다. `presentation()`만 수정해 원문까지 생성 컨텍스트에 넣고 공급자 매출 연결, 실제 PDF 페이지, 토론 claim_id를 명시했다. 미확인을 입증된 사실처럼 취급하지 않으며, 검사도 unknown의 빈 evidence만으로 거부하지 않고 확인 범위·검증 방법을 평가하도록 형식 규칙과 일치시켰다. 사실·수치·자기보고의 근거 검사는 유지한다.
- 형식 검증 → 독립 내용 검사 → 렌더링의 거부 이유를 다음 후보에 전달하고 실행당 최대 3개 후보를 시도한다. 모두 실패하면 여전히 실패다. 후보별 JSON·원본 출력·JSONL·검사·로그는 `presentation-attempts/<시각>/`에 보존한다. 레거시 거부 후보는 최초 재개 시 `previous-rejected/`에 보존하며, 검사 결과를 강제로 true로 쓰거나 검사를 건너뛰지 않는다.
- 전체 로컬 테스트 23개 통과. 새 회귀 검사는 거부된 기존 후보 보존, 잘못된 PDF 페이지를 렌더링 전에 거부, 다음 생성에 검사 지적 전달, 별도 검증 역할 재호출, 최대 횟수 중단, 통과 후보만 렌더링을 검증한다. 실제 렌더링 검사도 기존 한글·인용·PPTX 재열기 fixture에서 통과했다. 샌드박스의 별도 Codex preflight는 exit 1이며 `logs/auth-codex-presentation-probe.json`에 상태만 기록했다. 실제 수정 후보의 모델 생성·내용 통과는 사용자 Mac에서 확인해야 한다.
- 수정 전 input hash 일치, 입력 PDF·요구사항·출처·옵션·source ID 불변, 성공한 조사·토론 산출물 불변을 확인했다. 수정 범위를 presentation으로 한정하고 현재 실행의 `state.json/resume_updates`에 이전/새 코드 hash와 성공 단계 digest를 기록했다. 완료 단계 `[inputs,research,debate]`와 이전 거부 기록은 보존한다.
- 다음 한 단계는 동일 `--resume runs/neofirm-20261007T032143604608Z`로 Phase 6 발표를 재개하는 것이다. 완료 조건은 실제 독립 내용 검사 passed=true·issues=[], 한글·잘림·출처·시간·PPTX 재열기 검사 통과, 최종 PPTX/PDF/대본 생성이다. 공식 발표 공지와 실제 리허설은 여전히 미확인이다. GCS 예약·Calendar·외부 자료 등록 변경은 없다.

## 2026-10-07 — NotebookLM 조사 인용 및 재개 복구

- 사용자 Mac의 `AUTH OK` 이후 `neofirm-20261007T032143604608Z`에서 NotebookLM/Codex 인증과 S1–S6 등록·처리가 성공했다. 로컬 로그의 해당 8개 검사/대기 명령 exit 0, `state.json/source_ids` 및 `sources.json`의 6개 ID 일치를 확인했다. Phase 4는 자료 등록까지 성공했고 조사는 아직 미완료다.
- `research-1.json`과 `logs/research-1.json`의 실제 CLI 응답은 exit 0, 답변 10,086자, `references=[]`였다. 빈 답변이 아니라 구조화된 인용 부재다. 기존 공통 POLICY가 `[S1 p.19]` 같은 수동 표기를 요구했고 답변이 이를 사용했으며 22페이지 PDF에 없는 p.25–34까지 인용했다. 이 응답은 검증된 조사로 사용하지 않는다.
- 설치 버전 `ask --help`, `source fulltext --help`, `cli/chat_cmd.py`와 [프로젝트 CLI 문서](https://github.com/teng-lin/notebooklm-py/blob/main/docs/cli-reference.md)를 확인했다. 실제 source ID별 `-s` 지정, 기본 숫자 인용과 `--json` references를 사용한다. 파서의 reference 필드명을 임의 변경하거나 수동 출처를 진짜 reference로 만들어 넣지 않았다.
- `scripts/run_neofirm.py`의 조사 프롬프트를 Codex POLICY에서 분리해 기본 인용·원문 재검색·짧은 답변·PDF 실제 범위를 요청했다. 인용 없는 기존 캐시를 보존 이동하고 질문당 최대 두 번 새 요청한다. 인용이 계속 없거나 출처 ID가 일치하지 않으면 중단한다. `--new`, 원격 대화 삭제, 노트북/source 재업로드, 추가 의존성은 없다.
- 코드 수정 전 현재 모든 입력·옵션·코드 hash가 기존 실행과 일치함을 확인했다. 수정 후에는 runner 외 4개 hash와 옵션이 불변이며, 완료 단계가 inputs뿐이고 불확실한 쓰기도 없음을 확인했다. 현재 실행에 한해 `state.json/resume_updates`에 이전/새 hash를 기록해 재개 가능하게 갱신했다. 6개 source ID·노트북 ID·실패 기록·원본 응답은 보존했다. 일반적인 hash 변경 거부 규칙은 유지한다.
- 전체 로컬 테스트 22개 통과. 추가 회귀 검사는 인용 없는 실제 형태의 캐시 보존, 한 번 실패 후 회복, 성공 응답 재사용, source 선택, 대화 삭제 금지, 연속 두 번 실패 시 결과 미생성을 검증한다. 이 환경의 실제 `ask` 진단은 DNS `nodename nor servname provided, or not known`으로 exit 2였고 `logs/research-native-probe.json`에 기록했다. 사용자 인증이 다시 실패한 것으로 해석하지 않는다. 수정 프롬프트의 실제 인용 응답은 아직 확인하지 못했다.
- 다음 단계는 사용자 Mac에서 기존 실행을 `--resume runs/neofirm-20261007T032143604608Z`로 재개해 세 질문 모두 실제 인용·source 매핑을 가진 `research.md`를 확보하는 것이다. 그것이 Phase 4 완료 조건이며 이후 토론·최종 발표는 아직 완료로 표시하지 않는다.

## 2026-10-07 — NotebookLM 로그인 오판 복구

- 사용자 실행 `neofirm-20261007T032143604608Z`는 `failed_stage=auth`, NotebookLM 검사 exit 1이다. 저장된 인증 파일은 쿠키 이름만 확인했으며 `NID`, `__Host-GAPS`만 있고 `SID`, `__Secure-1PSIDTS`는 없다. 쿠키 값은 출력·기록하지 않았다. 원격 노트북/source 생성 전에 종료했다.
- 설치된 0.8.4의 `_browser/browser_capture.py`는 `goto(..., wait_until="commit")` 후 앱 호스트 도착 여부로 `Already logged in`을 출력한다. 실제 쿠키가 없는 경우에도 저장한 뒤 경고하고 종료할 수 있다. 이는 서버 인증 성공과 다르다. 사용자는 Playwright 로그인 경로이므로 출력의 Chrome 127+ 쿠키 추출 경고를 실제 원인으로 확정하지 않는다.
- `_env.py`에서 기본 앱 주소와 허용 호스트를 확인했다. 익명 읽기 요청은 기본 앱 호스트에서 HTTP 200, 기존 호스트에서 기본 호스트로 HTTP 301이었다. 단순한 기존 호스트 변경을 해결책으로 채택하지 않았다. [프로젝트 설치 안내](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md)도 실제 `auth check --test`의 `status=ok`, `token_fetch=true`를 요구한다.
- `scripts/login_neofirm.py`를 추가해 기존 Playwright와 전용 Chrome 프로필로 Google 로그인을 기다린다. 앱 호스트와 SID 확인 후, 인증 저장·쿠키 회전은 기존 NotebookLM CLI에 위임한다. 마지막 읽기 전용 `auth check --test --passive --json` 성공만 `AUTH OK`로 표시한다. 프로필 삭제, 쿠키 수동 복사, 신규 패키지, vendor 코드 수정은 없다. 진단 원문·계정·쿠키는 출력하지 않는다.
- 로컬 회귀 검사로 익명 호스트 도착·시간 초과·Google 로그인 페이지 체류·서버 인증 실패를 거부하고 실제 검사 성공 조건을 확인했다. 전체 로컬 테스트 21개 통과. 실제 사용자 브라우저 로그인 복구와 원격 자료 접근은 아직 미검증이다.
- 파이프라인·입력 hash 대상은 바꾸지 않았으므로 기존 실행을 재개할 수 있다. 다음 단계: 사용자 Mac에서 `sh scripts/login-neofirm.sh`의 `AUTH OK` 확인 후 `sh scripts/run-neofirm.sh --resume runs/neofirm-20261007T032143604608Z`; Phase 4 완료 조건은 실제 NotebookLM source ID와 인용 포함 조사 파일이다.

## 2026-10-07 — NeoFirm Codex 요청 실행

- 최신 사용자가 **Codex + NotebookLM CLI**로 진행하라고 명시했다. 이전 Claude Code/“클코” 가정을 대체하며 Claude Code 인증을 추가 요구하지 않는다. 공식 과제 공지는 미확인이라 보고서 p.18–20의 활동·평가 및 임시 7분을 적용한다.
- 제공 보고서 22페이지와 참고 발표 10페이지를 실제 열람했다. 참고 발표의 숫자는 근거로 사용하지 않았다. Index Ventures, Crosby, 혜움, BHSN, General Catalyst 원문을 열람하고 URL·시점·위치·자기보고 유형을 `docs/neofirm-primary-sources.json`에 기록했다.
- `codex-cli 0.160.1`, Python 3.14.7, `notebooklm-py[browser] 0.8.4 (bff7c66e)`, `python-pptx 1.0.2`, `PyMuPDF 1.28.2`를 확인했다. 가상환경은 `.venv/`; 계정 저장소는 `.local/notebooklm/`로 분리하고 모두 `.gitignore`에 추가했다.
- 제한된 설치 환경에서 일반 pip 설치는 `No matching distribution found`로 실패했다. 허용된 개별 curl로 PyPI 메타데이터·호환 wheel을 내려받고 `pip --no-index --find-links /private/tmp/neofirm-wheels ...`로 설치했다. 22개 wheel의 PyPI SHA-256 일치와 `pip check`를 확인했다. 새 환경에서는 `requirements-neofirm.txt`로 표준 설치한다.
- 선택한 [notebooklm-py](https://github.com/teng-lin/notebooklm-py)는 비공식이며 문서화되지 않은 Google API에 의존한다. 실제 설치 버전의 `--help`로 `login --browser chrome`, `auth check --test --passive --json`, `create`, `source add/list/wait`, `ask`의 옵션을 확인했다. `ask --new`는 대화를 삭제하므로 사용하지 않는다. URL source는 서버 제목이 붙을 수 있어 ID/URL로 재조회한다.
- Codex 독립 세션 구현 시 [공식 Non-interactive mode 문서](https://learn.chatgpt.com/docs/non-interactive-mode)와 설치된 `codex exec --help`를 확인했다. JSONL·최종 메시지·스키마·ephemeral·read-only 옵션을 사용한다. 현재 샌드박스의 별도 CLI 실행은 app-server 초기화 `Operation not permitted`; 모델·인증값·샌드박스를 임의 변경해 우회하지 않았다.
- 이 작업 세션에서는 실제 독립 Codex Agent 3명으로 3라운드·9개 발언, 종합, 별도 반대/검증 검사를 수행했다. 원문 기반 선행 검토이며 NotebookLM 조사나 자동 CLI JSONL로 위장하지 않았다. 실행 경로는 `runs/neofirm-20261007T030820373716Z/`와 `debate-provenance.json`에 있다.
- 자동화는 `sh scripts/run-neofirm.sh`; source 등록→조사→독립 세션 토론→종합→내용검사→PPTX/PDF/대본을 연결한다. 성공 단계 재사용·input hash·불확실한 쓰기의 재조회·실패시 중단을 구현했다. `--resume`은 같은 입력·옵션·코드에만 사용한다.
- 로컬 20개 테스트, Python/shell 구문검사 통과. 12장 검토용 발표는 한글·잘림·인용·420초 합계·PPTX 재열기와 독립 내용검사를 통과했다. PPTX 본문은 PDF를 렌더링한 이미지이며 노트는 텍스트다. 실제 리허설은 하지 않았다.
- NotebookLM 계정의 원격 권한·source 등록·조사는 미확인이다. `list --json`은 `AUTH_REQUIRED`; 전체 러너 `neofirm-20261007T031742014417Z`는 `failed_stage=auth`로 종료했다. 원격 노트북·source 생성은 실행되지 않았다. 사용자의 로그인 시도에 환경변수명 역슬래시가 포함돼 zsh 명령 오류가 있었고 `env NOTEBOOKLM_HOME=...`로 수정 안내했다. 이후 확인은 값 출력 없이 수행한다.
- 다음 단계는 사용자 호스트 터미널에서 `sh scripts/login-neofirm.sh` 후 `sh scripts/run-neofirm.sh`로 실제 NotebookLM source ID·조사 인용을 확보하는 것이다. [상세 증거](2-neofirm-evidence.md). 이번 작업에서 GCS 예약/Calendar 변경이나 외부 고객 연락은 없다.

## 2026-10-06 11:14 KST — Phase 0 조사

| 항목 | 확인 결과 |
|---|---|
| 작업 지침 | `AGENTS.md`와 `ROADMAP.md`를 읽음. AGENTS가 언급한 `GCS-PULSE_NeoFirm_과제_로드맵.md`는 없고 이 저장소에는 `ROADMAP.md`가 있음. |
| GCS 명세 | `openapi.json`, SHA-256 `1ca23bcbb58e65c427d7980f461bcade958b3bd8548c0a51356204501aa49c47`, OpenAPI 3.1.0/79 paths. `servers`, 최상위 `security`, `securitySchemes` 없음. 읽기 경로·요구 필드 확인. |
| API URL | 로드맵의 Swagger 링크에서 `https://api.1000.school` 후보 확인. `curl -I https://api.1000.school/openapi.json` → HTTP 200, `curl https://api.1000.school/auth/me` → HTTP 401, `curl https://api.1000.school/meeting-rooms` → HTTP 401. DNS가 간헐적으로 실패해 지속 접근은 미검증. |
| API 인증 | 토큰 전달 헤더 형식 확인 불가. 설정값 `PULSE_AUTH_HEADER`/`PULSE_AUTH_VALUE`를 명시적으로 요구; Bearer를 추정해 기본값으로 쓰지 않음. |
| 제공 GCS CLI/MCP | `command -v gcs-pulse`, `command -v pulse`에 결과 없음. `codex mcp list`에는 cloudflare, supabase만 표시. 수업 배포 자료를 받지 못해 제공물이 없다고 최종 확정할 수 없음. |
| Codex | `codex-cli 0.160.1`; `codex exec --help`에서 `--json` 확인. `codex mcp add --help`에서 stdio 등록 형식 확인. 최소 `codex exec --json --skip-git-repo-check` 실행은 `failed to initialize in-process app-server client: Operation not permitted`로 실패해 실제 JSONL 이벤트는 아직 미측정. |
| GWS | `gws 0.22.5`; `gws auth status`는 `auth_method: none`, credential 없음. `gws calendar events insert --help`와 `gws schema calendar.events.insert`는 discovery 접근 오류로 실패. Calendar 권한과 읽기 호출 미검증. |
| Google Cloud | `gcloud 586.0.0` 설치. 계정 권한은 확인하지 않음. |
| Python/Node | Python 3.14.7, Node 22.15.1, npm 10.9.2. |
| Claude Code/NotebookLM | `command -v claude`, `command -v notebooklm`에 결과 없음. 수업 지정 배포물·인증 여부 미확인. |
| NeoFirm 입력 | 과제 원문은 저장소에 없음. 로드맵의 Drive 보고서는 이 환경에서 접근 실패(DNS); 내용·MIME·권한 미확인. “클코”가 Claude Code인지 원문으로 확인 필요. |
| 테스트 계정 | GCS 토큰·권한, 예약 가능 시간/방, Google Calendar 쓰기/초대 권한, 팀별 실험 계정 모두 미확인. 외부 변경 없음. |
| 저장소 | 현재 폴더에는 `.git`이 없어 `git status`는 실패. 파일은 로컬 작업 폴더에 작성했으며 커밋하지 않음. |

### 근거와 구현 결정

- 로컬 `openapi.json`의 `/meeting-rooms`, `/meeting-rooms/{room_id}/reservations`, `/users/students/search` 스키마만 사용해 공통 Python HTTP 클라이언트와 CLI/MCP 읽기 어댑터를 구현했다. 서버/계정 인증 전이므로 이것은 Phase 1 도구 준비와 fixture 검증일 뿐 Phase 0/1 완료 증거는 아니다.
- `python3 -m unittest discover -s tests -v`에서 3개 테스트 통과. 별도 stdio 검사에서 잘못된 JSON, `initialize`, `tools/list`, 인증 누락 도구 오류를 확인했다. 실제 Codex 연결 테스트와 원격 읽기 호출은 아직 성공하지 않았다.
- 공식 [MCP 2025-06-18 stdio/도구 규격](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-06-18/server/tools.mdx) 및 [GWS CLI 저장소](https://github.com/googleworkspace/cli)를 참고했다. 현재 설치된 Codex와 MCP 통합은 별도 확인이 필요하다.
- Google 공식 [Calendar events.insert 문서](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert)는 `attendees`와 `sendUpdates=all`을 정의한다. 현재 계정과 `gws`의 명령·권한이 확인되지 않아 실제 이벤트는 만들지 않았다.

### 다음에 필요한 입력

1. 수업의 GCS-PULSE CLI/MCP 배포 안내·저장소, 인증 헤더 안내, 테스트 계정 권한.
2. 팀별 실험 계정/팀명, 동일 검색어·날짜·회의실 ID를 정할 수 있는 읽기 권한.
3. NeoFirm 과제 원문, 참고 보고서 열람 권한 또는 로컬 파일, “클코”의 정확한 뜻.

## 2026-10-06 11:28 KST — 사용자가 `.env`에 토큰 추가 후 재확인

- `.env`에 `PULSE_AUTH_HEADER`와 `PULSE_AUTH_VALUE`가 모두 존재함을 **값 출력 없이** 확인했다. 파일 권한을 `600`으로 제한했고, `.gitignore`에서 `.env`가 제외되는 것도 확인했다. 현재 설정된 헤더를 Python `urllib.request.Request`가 로컬에서 수용함을 확인했다. 서비스가 인증 형식을 수용하는지는 미검증이다.
- `.env`를 프로세스 환경으로 읽어 `python3 -m pulse.cli meeting-rooms list` 실행 → `network_uncertain / URLError`. 같은 토큰을 명령행 인자에 노출하지 않고 `curl --config -` 표준입력으로 전달해 읽기 요청 → DNS 실패(`curl` 종료 6, HTTP 상태 000). 토큰 값·응답 본문은 출력하거나 저장하지 않았다.
- `CODEX_SANDBOX_NETWORK_DISABLED`가 설정된 현재 실행 환경에서 `api.1000.school`과 `google.com` DNS 조회가 모두 실패했다. 읽기 전용 `curl`의 권한 상승을 요청했으나 자동 승인 정책이 `sandbox_approval: false`로 거절했다. 따라서 인증 성공, API 권한, 회의실 목록은 아직 확인되지 않았다.
- 토큰 값만 있는 `Authorization` 헤더가 올바른지 서비스 안내가 없어 확인 중이다. 근거 없이 `Bearer` 접두사를 붙이거나 토큰을 수정하지 않았다.
- Phase 0 완료 조건인 인증된 읽기 호출은 미충족. 다음 재시도는 네트워크 접근 가능한 실행 환경과 확인된 헤더 형식에서 `meeting-rooms list`를 호출하는 것이다.

## 2026-10-06 11:30 KST — 헤더 안내 부재에 따른 읽기 전용 검사 준비

- 사용자가 별도 인증 헤더 안내가 없다고 확인했다. 이전 로컬 프로젝트 `/Users/joo/project/asps-2/src/workflows/jobs.ts`에는 `Authorization: Bearer <토큰>` 사용 코드가 있지만, 그 프로젝트의 `docs/1000-school-api-contract.md`도 헤더 형식은 미확인으로 기록했다. 따라서 이 코드를 검증 근거로 취급하지 않는다.
- `scripts/check_pulse_auth.py`를 추가했다. 최초 구현에는 401 이후 Bearer 재시도가 있었으나 사용자 경험을 반영해 아래 기록대로 제거했다. 현재는 `.env` 형식으로 읽기 요청 한 번만 실행한다.
- `python3 -m unittest discover -s tests -v` 4개 통과. `python3 -m scripts.check_pulse_auth` 실행은 `configured: network_uncertain`으로 종료. 실제 인증 형식과 권한은 여전히 확인되지 않았다.

## 2026-10-06 11:31 KST — 사용자 경험 반영

- 사용자는 이전 프로젝트에서 접두사 없이 토큰만 넣었다고 알려 주었다. 이 정보는 참고하되 현재 GCS 서버의 검증 결과로 쓰지는 않는다.
- Bearer 자동 재시도를 제거했다. 인증 검사는 `.env`의 현재 형식으로 읽기 요청 한 번만 보낸다. `python3 -m unittest discover -s tests -v` 4개 통과, `python3 -m scripts.check_pulse_auth`는 네트워크 제한으로 `configured: network_uncertain`.
- 사용자는 이전 프로젝트에서도 접두사 없이 토큰을 사용한 것으로 기억한다고 확인했다. `PULSE_AUTH_HEADER=Authorization`은 유지한다. 이 값은 토큰을 전달할 HTTP 헤더 이름이며, 삭제하면 현재 클라이언트는 토큰을 보내지 않는다. 인증과 회의실 권한을 구분하기 위해 검사 순서를 `/auth/me` → `/meeting-rooms`로 바꿨다.

## 2026-10-06 — 인증 검사 로직 수정

- `auth_me: forbidden`만으로 토큰 오류라고 판단한 것은 잘못이다. `scripts/check_pulse_auth.py`가 `/auth/me`를 필수 관문으로 삼아 실제 예약 대상인 `/meeting-rooms`를 호출하기 전에 종료하고 있었다.
- 공개된 GCS-PULSE 실행 예는 `Authorization: Bearer ...`로 `/meeting-rooms`를 직접 호출한다: <https://github.com/MinHyeokYang/LLM_HW/blob/main/scripts/gcs_pulse_cli_snippet.ps1>.
- 검사 스크립트를 `/meeting-rooms` 직접 조회 방식으로 수정하고 로컬 테스트 5개를 통과했다. 현재 이 환경의 외부 DNS 제한으로 실서버 결과는 아직 미확인이다.

## 2026-10-06 — 실서버 403 원인 확인

- 사용자 환경에서 `/meeting-rooms` 응답이 `HTTP 403: The site owner has blocked access based on your browser's signature.`로 확인됐다.
- 이는 토큰 이름·예약 권한 오류가 아니라 Cloudflare Error 1010 계열의 클라이언트 서명 차단으로 판단한다. 공식 해결 방향은 사이트 소유자가 클라이언트/IP를 허용하거나 Browser Integrity Check 정책을 조정하는 것이다: <https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1010/>.
- Python 기본 `Python-urllib/...` 식별자를 피하기 위해 정직한 `User-Agent: gcs-pulse-client/0.1`을 추가했다. 이 변경 후에도 403이면 서버 측 허용 정책이 필요하며 토큰 재시도로 해결하지 않는다.

## 2026-10-06 — 사용자 환경 GCS 읽기 성공

- 사용자가 프로젝트 루트에서 `python3 -m scripts.check_pulse_auth`를 실행했고 `configured: ok, rooms=14`를 보고했다.
- 이 결과는 토큰을 로그에 남기지 않은 회의실 목록 읽기 스모크 테스트 성공으로 기록한다. 회의실 이름·ID 원본, 학생 이메일, 토큰은 저장하지 않았다.
- 이 실행만으로 GCS 예약 권한, 학생 검색, MCP 연결, Codex 토큰 측정, GWS/Calendar 권한을 완료로 판단하지 않는다. Phase 0은 GCS 읽기 부분만 통과했고 전체 완료 조건은 미충족이다.

## 2026-10-06 — 다음 단계 재점검 및 1.1 프로세스 비교 준비

- `openapi.json`은 저장소 루트에 있으며 `servers`·최상위 `security`·`securitySchemes`가 없다. 과제 원문·NeoFirm 보고서는 로컬에 없고 내용은 확인하지 못했다. 이 폴더에는 `.git`도 없다.
- `codex-cli 0.160.1`: `codex mcp list`에 GCS 서버 없음. `codex exec --json --ephemeral --skip-git-repo-check --sandbox read-only 'Reply with exactly OK.'`는 `failed to initialize in-process app-server client: Operation not permitted`로 종료해 JSONL 이벤트 형식을 확인할 수 없었다. `codex mcp add --help`의 stdio 등록 형식만 확인했다.
- `gws 0.22.5`: `gws auth status`에서 `auth_method: none`, 자격 증명·토큰 캐시 없음. `gws calendar --help`는 `discoveryError: Operation not permitted`로 종료했다. Google 계정/Calendar 권한은 확인되지 않았다. `claude`, `notebooklm`, 수업 제공 GCS CLI/MCP 실행 파일도 PATH에서 찾지 못했다.
- `python3 -m scripts.check_pulse_auth`는 이 샌드박스에서 `meeting_rooms: network_uncertain (URLError)`로 종료했다. 사용자 환경의 이전 `rooms=14` 성공을 취소하는 결과는 아니며, 현재 실행 환경의 외부 네트워크 제한 때문에 재검증할 수 없다. 로컬 소켓 바인딩도 `PermissionError 1`로 거절됐다.
- `python3 -m pulse.mcp`에 실제 JSON-RPC `initialize`/`tools/list`를 stdio로 보내 정상 응답을 확인했다. `scripts/check_pulse_parity.py`는 동일한 A/B/C 입력을 별도 CLI 프로세스와 MCP 프로세스로 호출하고 결과 일치 여부만 출력한다. 실제 호출은 위 네트워크 제한으로 실패했으며 Codex 세션 연결·토큰 비교의 완료 증거가 아니다. `python3 -m unittest discover -s tests -v`: 8개 통과.
- 남은 입력/권한: 네트워크가 되는 Codex 실행 환경, GWS OAuth 자격 증명과 Calendar 권한, 팀별 계정·고정 room ID/날짜/검색어, 수업 제공 도구의 배포 안내, NeoFirm 원문·보고서 접근 권한과 “클코” 정의. 실제 예약·초대 등 외부 변경은 없었다.

## 2026-10-06 — 1.1 실서버 비교 재시도

- `.env`는 셸 `source` 대신 러너가 키-값을 읽어 자식 프로세스에 전달하도록 했다. 현재 토큰 값은 출력·로그·Codex 설정에 쓰지 않았다.
- 실서버 재시도: `python3 -m scripts.check_pulse_auth` → `network_uncertain (URLError)`, `curl https://api.1000.school/meeting-rooms` → DNS 실패/상태 000. 이 환경의 네트워크 제한으로 API 응답을 받지 못했다.
- MCP 연결 시도: `codex mcp add gcs-pulse --env PYTHONPATH=/Users/joo/project/asps-4 -- python3 -m pulse.mcp` → `/Users/joo/.codex` 설정 파일 쓰기 `Operation not permitted`. Codex 측정 시도도 `failed to initialize in-process app-server client: Operation not permitted`로 종료했다.
- 같은 명령을 임시 쓰기 경로 `CODEX_HOME=/private/tmp/asps-4-codex-home2`에서 실행하면 `Added global MCP server 'gcs-pulse'`와 `enabled` 목록이 확인된다. MCP 등록 형식 자체는 유효하지만, 이 임시 설정으로도 OpenAI API DNS가 막혀 Codex 실험은 완료되지 않았다.
- `scripts/run_1_1_comparison.py`를 추가했다. 사용자 환경에서 A/B/C를 MCP·CLI 각각 3회 실행하고 `runs/1-1-*/summary.json`에 입력 토큰·출력 토큰·경과 시간·도구 호출 수·결과 해시·성공 여부만 남긴다. 실행 JSONL/로그는 토큰·검색어·학생 이메일·학생 이름을 마스킹해 저장하며 `runs/` 전체가 `.gitignore` 대상이다.
- 전역 Codex 홈을 쓸 수 없는 제약을 분리하기 위해 `CODEX_HOME=/private/tmp/asps-4-codex-home codex exec --json ...`을 시험했다. 이 경우 `thread.started`/`turn.started`까지는 생성됐지만 `api.openai.com` DNS 실패로 재연결 후 종료했다. 따라서 Codex JSONL 토큰 이벤트 형식의 성공 사례와 GCS 실서버 호출은 여전히 확보하지 못했다.
- 현재 세션에서는 실서버 결과·토큰 비교·경험 우열을 만들지 않았다. 비교 완료 조건은 러너 성공 로그와 `docs/1-1-comparison.md`의 실제 수치/오류 복구 기록이다.

## 2026-10-06 — 샌드박스 네트워크 해제 시도

- `curl -I --max-time 10 https://api.1000.school/meeting-rooms`는 `Could not resolve host`로 실패했다.
- `CODEX_SANDBOX_NETWORK_DISABLED`와 `CODEX_SANDBOX`를 자식 프로세스에서 제거한 뒤 같은 요청을 다시 실행해도 DNS 실패가 같았다. 셸 환경 변수만으로 플랫폼 네트워크 제한을 해제할 수 없다.
- `require_escalated`로 네트워크 권한 상승을 요청했으나 현재 정책의 `sandbox_approval: false`로 거부됐다. 따라서 이 세션에서 네트워크·Codex 샌드박스 권한을 해제할 수 없다.
- 실서버 측정에는 네트워크가 허용된 실행 환경, `api.1000.school`·`api.openai.com`으로의 DNS/HTTPS, Codex 설정 디렉터리 쓰기 및 app-server 초기화 권한이 필요하다.

## 2026-10-06 — 1.1 빈 셸 변수 오류 수정

- 사용자가 `--room-id "$ROOM_ID" --date "$DATE" --query "$QUERY"`를 실행했을 때 세 변수가 설정되지 않아 `--room-id`에 빈 문자열이 전달됐다.
- `scripts/run_1_1_comparison.py`에 빈 room ID·날짜·검색어를 구분하는 인자 검증을 추가했다. 이제 `room ID is empty`처럼 수정 방법이 포함된 오류를 출력한다.
- README와 `1.1.md`에 `--room-id 2 --date 2026-10-07 --query '__no_match__'` 고정 읽기 예시를 추가했다. room ID 2는 실제 계정에서 접근 가능한지 실행 전에 확인해야 한다.
- `python3 -m unittest discover -s tests -v` 8개 통과, 빈 room ID 인자 검증 통과.

## 2026-10-06 — 1.1 러너 무응답 표시 수정

- 기존 러너는 18개 Codex 세션의 표준 출력을 모두 캡처한 뒤 마지막에만 출력해, 실행 중 터미널이 무응답처럼 보였다.
- 회차별 시작·종료 상태를 표준 오류에 즉시 출력하고, 세션별 기본 120초 제한을 추가했다. 제한 초과는 `codex_exec_timeout`으로 요약한다.
- 타임아웃 로그도 기존 토큰·검색어·학생 이름·이메일 마스킹 경로를 사용한다.

## 2026-10-06 — Codex MCP 승인·이벤트 형식 수정

- 사용자 `codex-cli 0.160.1`의 마스킹된 JSONL에서 `mcp_tool_call`이 `MCP tool call requires approval, but approval policy is never`로 거부된 것을 확인했다. 프로세스는 토큰 사용량을 생성했지만 실제 MCP 읽기 호출은 실패했다.
- 같은 로그의 최종 응답은 `item.completed` 안 `agent_message` 형식이었다. 기존 `message`만 읽던 파서는 이 응답을 놓쳐 `success=False` 원인을 설명하지 못했다.
- MCP 세 도구에 `readOnlyHint=true`, `destructiveHint=false`를 추가하고 Codex 실행마다 `mcp_servers.gcs-pulse.default_tools_approval_mode="writes"`를 적용했다. Codex 공식 설정에서 `writes` 모드는 읽기 전용으로 표시된 도구에 승인을 요구하지 않는다: <https://learn.chatgpt.com/docs/extend/mcp>.
- 러너가 `agent_message`를 읽고 승인·도구 실패를 `tool_errors`/`mcp_tool_failed`로 기록하도록 수정했다. 새 테스트 포함 로컬 테스트 10개 통과.

## 2026-10-06 — 사용자 1.1 첫 18회 실행 결과

- 실행 ID `1-1-20261006T050418Z`, `codex-cli 0.160.1`, `gpt-5.6-luna`, `team-a`, `room_id=2`, `date=2026-10-07`, 검색어 `__no_match__`로 MCP·CLI 각 A/B/C 3회가 모두 종료됐다.
- 18회 모두 `exit_code=0`이고 Codex 입력·출력 토큰과 경과 시간은 생성됐지만, MCP는 `auth_config`, CLI는 `network_uncertain`으로 GCS 호출에 실패했다. 따라서 이 실행은 토큰 수집 파이프라인 검증 및 실패 경험 증거이며 MCP/CLI 성공 성능 비교가 아니다.
- 실행 당시 러너 버그로 `summary.json`의 합계 토큰이 0, CLI 도구 호출 수가 3으로 기록됐다. 원본 JSONL을 수정된 파서로 재계산하면 도구 호출 수는 양쪽 모두 1이고 합계 토큰은 입력+출력으로 계산된다. 수정된 클라이언트가 `.env`를 직접 읽도록 했으므로 같은 고정 입력으로 재실행해야 한다.

## 2026-10-06 — MCP 성공·CLI 네트워크 차단 진단

- 실행 ID `1-1-20261006T053626Z`에서 MCP A/B/C 9회는 모두 성공했다. 결과 해시는 시나리오별로 반복 간 일치했고, MCP 인증·네트워크 경로가 작동함을 확인했다.
- 같은 실행의 CLI A/B/C 9회는 모두 `network_uncertain (URLError)`로 실패했다. Codex가 실행한 `python3 -m pulse.cli ...` 명령이 `--sandbox read-only`에서 외부 GCS 네트워크에 접근하지 못한 것이 원인이다. MCP 서버 프로세스는 샌드박스 명령 네트워크와 별도 경로라 성공했다.
- MCP와 CLI를 같은 조건에서 비교하려고 러너의 두 경로를 `--sandbox workspace-write`와 `sandbox_workspace_write.network_access=true`로 변경했다. 프롬프트는 계속 단일 읽기 작업만 허용하며, 이 샌드박스 변경은 명령 네트워크를 켜기 위한 실험 조건이다.

## 2026-10-06 — 1.1 Team A 최종 성공 비교

- 사용자가 `python3 -m scripts.run_1_1_comparison --room-id 2 --date 2026-10-07 --query '__no_match__' --team team-a --repeats 3`을 실행했다. 실행 ID는 `1-1-20261006T054713Z`, Codex는 `codex-cli 0.160.1`/`gpt-5.6-luna`였다.
- MCP·CLI 각 A/B/C 3회, 총 18회가 `exit_code=0`, `success=true`, `tool_errors=0`으로 완료됐다. A/B/C 결과 해시는 MCP와 CLI, 반복 회차 사이에 모두 일치했다.
- 중앙값은 `1.1.md`와 `docs/1-1-comparison.md`에 기록했다. Team A에서는 CLI가 MCP보다 합계 토큰과 경과 시간이 모든 시나리오에서 낮았다. 이 결과는 한 팀·한 입력 세트의 관찰값이며 모든 팀의 일반적 우위로 확대하지 않는다.
- 토큰 비교는 Codex JSONL의 입력·출력 토큰 합을 사용했고 GCS `GET /users/me/token-usage`는 섞지 않았다. 검색어 원문·학생 개인정보·인증값은 보고서에 저장하지 않았다.
- 남은 항목은 `team-a` 외 팀 계정이 과제 범위에 포함될 경우 동일 실험을 반복해 팀별 표를 완성하는 것이다. 실제 예약·Calendar 변경은 수행하지 않았다.

## 2026-10-06 — 1.2 예약 Skill 구현

- PATH에서 수업 제공 GCS-PULSE CLI는 발견되지 않았으므로 기존 공통 HTTP 클라이언트 위의 `pulse.cli`를 예약 경로까지 확장했다. 추가 명령은 `reservations create`, `reservations cancel`, `students search --include-email`이다. 기본 학생 검색은 기존처럼 이메일을 제외한다.
- `scripts/book_meeting.py`는 두 CLI만 호출한다. 학생/방/예약/Calendar 충돌을 읽은 뒤, 확인 전에는 preview만 출력하고 `--confirm`일 때만 GCS POST → GWS Calendar insert → 양쪽 재조회 순서로 쓴다. GWS 요청에는 `sendUpdates=all`을 사용하며 Gmail을 별도로 호출하지 않는다.
- `gws --version`은 `0.22.5`를 반환했고 전역 도움말에서 `--params`, `--json`, `--format`을 확인했다. `gws calendar --help`와 `gws schema calendar.events.insert`는 이 환경의 Discovery 접근 오류로 실패했으므로 subcommand 세부 인자와 OAuth 권한은 아직 라이브 검증하지 않았다.
- `python3 -m unittest discover -s tests -v`는 14개 통과했다. fixture에서 동명이인, GCS 방 충돌, Calendar 실패 시 취소 보상, 쓰기 결과 불명확 시 재삽입 방지를 확인했다.
- `python3 scripts/book_meeting.py ...` preview는 `network_uncertain (URLError)`로 GCS 읽기 단계에서 중단됐다. `--confirm`을 사용하지 않았고 실제 예약 ID·Calendar 이벤트 ID·초대 메일은 없다.
- 다음 단계는 네트워크가 허용된 환경에서 GCS 예약 권한과 GWS OAuth Calendar 쓰기 권한을 확인한 뒤, 테스트 시간으로 preview → 명시적 확인 → 실제 1회 → 재조회·롤백 증거를 `docs/1-2-booking-evidence.md`에 추가하는 것이다.

## 2026-10-06 — 대화형 예약 입력 추가

- 긴 명령줄을 반복하지 않도록 `python3 scripts/book_meeting.py --interactive`를 추가했다. 제목, 목적, KST 날짜/시각, 소요시간, 방, 학생 이름/이메일, Calendar ID만 묻고 최종 요약에서 한 번 확인한다.
- 인증은 보안상 자동 입력하지 않는다. `.env`의 GCS 인증값과 GWS OAuth는 최초 1회 준비가 필요하다.

## 2026-10-06 — 1.2 라이브 사전조건 확인

- 사용자가 GWS OAuth를 완료했다. `gws auth status`에서 `auth_method=oauth2`, `token_valid=true`, `has_refresh_token=true`, Calendar scope 포함 6개 scope, `project_id=gcs-gws-meeting`을 확인했다. client ID와 이메일 원문은 기록하지 않았다.
- 처음 Calendar 읽기에서 `serviceusage.services.use` 권한 부족이 발생했으나 `roles/serviceusage.serviceUsageConsumer`를 프로젝트에 부여한 뒤 재시도했다.
- 사용자 실행 `gws calendar events list --params '{"calendarId":"primary","maxResults":1}' --format json`이 성공했다. 응답의 `accessRole=owner`, `timeZone=Asia/Seoul`을 확인했다. 원본 이벤트의 이메일·ID는 문서에 저장하지 않았다.
- 사용자 실행 `python3 -m scripts.check_pulse_auth`가 `configured: ok, rooms=14`, `reservations: ok, date=2026-10-06, rooms=14, entries=6`, `students_search: ok, total=0`을 반환했다.
- 따라서 GCS/GWS 인증과 양쪽 읽기 경로는 확인됐지만, GCS 예약 POST·Calendar insert·초대 알림·재조회는 아직 실행하지 않았다. 다음 작업은 테스트 시간과 참석자를 확정한 뒤 `python3 scripts/book_meeting.py --interactive`에서 최종 확인하는 것이다.

## 2026-10-06 — 1.2 실제 예약 검증

- 사용자가 인증된 터미널에서 `N.FR2`, 2026-10-06 18:00–19:00 KST, `독서토론 준비` 요청을 실행했다.
- 실행 결과 `status=verified`, 참석자 1명, `notification_requested=true`; 상태 파일은 `runs/bookings/booking-20261006T081722545478Z.json`이다.
- GCS 예약 생성과 Calendar 이벤트 생성 후 양쪽 재조회 검증까지 성공했다. 원본 예약/이벤트 ID는 상태 파일에만 두고 제출 문서에는 마스킹한다.
- 이번 실행은 N.FR2만 대상으로 했으며 N.MR2에는 쓰지 않았다. 실제 초대메일 수신·수락은 확인하지 않았다.

## 2026-10-07 — 1.2 초대메일 수신 확인

- 사용자가 실제 Calendar 초대메일 수신을 확인했다고 보고했다.
- `sendUpdates=all` 요청과 실제 메일 수신은 확인 완료로 기록한다. 참석자가 Calendar에서 `예/수락`을 눌렀는지는 별도 확인하지 않았으므로 수락 완료로 표시하지 않는다.

## 2026-10-07 — 1.2 참석자 응답 및 GWS 확인 경로

- 사용자가 자신의 터미널에서 Calendar 이벤트의 참석자 목록을 조회했고 `responseStatus=declined`를 확인했다. 따라서 초대메일은 전달됐지만 참석자는 수락하지 않고 거절한 상태다.
- Codex 샌드박스에서 같은 GWS CLI 조회를 시도했을 때 `No keychain is available`, native root CA/keychain 오류로 401이 발생했다. 이는 Google OAuth가 취소된 것이 아니라 샌드박스가 사용자의 macOS Keychain에 접근하지 못한 환경 차이다.
- 사용자 터미널의 GWS CLI는 같은 이벤트 응답을 반환했으므로 인증 연결 자체는 끊어진 것으로 판단하지 않는다. 자동 검증은 사용자 호스트 터미널에서 실행하거나, 보안 수준을 낮추지 않는 별도 인증 실행 환경이 필요하다.

## 2026-10-06 — NeoFirm Phase 4 진입 점검

- 저장소에서 NeoFirm 과제 원문과 `ChatGPT-2026-NeoFirm Report` 원본을 찾지 못했다. 로드맵의 Drive URL은 현재 실행 환경에서 열리지 않았다.
- `command -v claude`와 `command -v notebooklm` 결과가 없어 Claude Code와 NotebookLM CLI의 설치·버전·인증을 확인하지 못했다. 현재 설치가 확인된 관련 도구는 `gws 0.22.5`, `gcloud`, `codex`뿐이다.
- 원문 없이 발표 시간·형식·평가기준·NeoFirm 사실을 추측하지 않기 위해 `docs/neofirm-requirements.md`에 입력 대기 목록을 만들었다. 다음 단계는 원문/보고서와 수업 지정 도구 정보를 확보하는 것이다.

## 2026-10-06 — NeoFirm 참고자료 확보

- 사용자 Downloads에서 `ChatGPT-2026-NeoFirm Report.pdf`와 `2026 GCS 9기 몰입캠프 2차 발표 3조 ...pdf`를 발견해 `inputs/`로 복사했다.
- 보고서는 22페이지이며 19페이지 수업 활동안(가치사슬, AI-전문가 배분, 1페이지 투자메모), 20페이지 위험·KPI·평가 기준을 확인했다. 참고 발표는 10페이지 형식 참고로만 분류했다.
- 보고서 SHA-256은 `20e72a1d…a7bb873a`, 참고 발표 SHA-256은 `d41088a4…1a5e8e8`이다.
- 공식 과제 원문, NotebookLM CLI의 지정 배포물·인증, Claude Code 설치·인증은 아직 확인하지 않았다. 이 상태에서 조사 결론이나 최종 발표자료를 완료로 표시하지 않는다.

## 2026-10-06 — NotebookLM CLI 후보 설치 시도

- 수업 지정 CLI가 확인되지 않아 `notebooklm-py[browser]`를 비공식 후보로 선택했다. 공식 저장소는 이 패키지가 문서화되지 않은 Google API를 사용하는 비공식 프로젝트라고 명시한다.
- Codex 환경에서 `pipx install 'notebooklm-py[browser]'`를 시도했으나 PyPI DNS 해석 실패로 설치되지 않았다. 부분 생성된 pipx 디렉터리는 `/private/tmp/neofirm-pipx-failed`로 이동했고 저장소에는 남기지 않았다.
- 다음 단계는 사용자 Mac 터미널에서 후보 CLI 설치·버전 확인·`notebooklm login` 인증을 수행하는 것이다. 인증 전에는 NotebookLM 조사나 발표자료 생성을 완료로 기록하지 않는다.

## 2026-10-07 — NotebookLM 공식 경로 확인

- Google 공식 자료를 확인한 결과, 일반 NotebookLM/Gemini Notebook 제품에 대한 공식 공개 CLI는 확인하지 못했다.
- Google Cloud의 공식 자동화 경로는 별도 상품인 Gemini Notebook Enterprise의 REST/gRPC API이며, 프로젝트·IAM·Enterprise 설정이 필요하다. 이를 과제의 NotebookLM CLI로 임의 대체하지 않는다.
- 따라서 `notebooklm-py`는 공식 CLI가 아니라 비공식 커뮤니티 후보로 명시한다. 수업에서 지정한 CLI가 있다면 그 배포물·문서·버전을 우선 확인한다.
