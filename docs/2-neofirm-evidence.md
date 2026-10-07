# 2. NeoFirm — 실행 증거

확인일: 2026-10-07 KST. 사용자의 최신 요청은 **Codex + NotebookLM CLI**이며 Claude Code를 요구하지 않는다.

## 현재 완료 범위

Phase 4–7 자동 실행은 **현재 입력·임시 7분 기준 완료**다. 사용자 Mac에서 NotebookLM source 6개 등록, 인용 포함 조사 3회, 독립 Codex CLI 3역할×3라운드와 종합, 발표 생성·실제 독립 내용 검사까지 수행했다. 마지막 정상 검사 응답을 공통 CLI 어댑터가 잘못 거부했던 오류를 수정하고 실제 완료 trace를 복구해 최종 PPTX/PDF를 렌더링·게시했다. 별도 공식 공지 대조와 실제 육성 리허설은 아직 없다.

## 최신 최종 파일과 완료 증거

- 실행 ID: `neofirm-20261007T032143604608Z`. [최종 PPTX](../output/neofirm-20261007T032143604608Z/neofirm-final.pptx), [PDF](../output/neofirm-20261007T032143604608Z/neofirm-final.pdf), [발표 대본](../output/neofirm-20261007T032143604608Z/speaker-notes.md), [전체 미리보기](../output/neofirm-20261007T032143604608Z/contact-sheet.png).
- 실제 재개 명령 `sh scripts/run-neofirm.sh --resume runs/neofirm-20261007T032143604608Z`는 exit 0, `COMPLETE output/neofirm-20261007T032143604608Z`. [state.json](../runs/neofirm-20261007T032143604608Z/state.json)의 status는 complete이며 inputs/research/debate/presentation이 완료됐다. 완료 후 동일 명령 재실행도 추가 모델·NotebookLM 호출 없이 성공했다.
- [quality-review.json](../runs/neofirm-20261007T032143604608Z/quality-review.json)은 실제 CLI 완료 답변의 `passed=true`, `issues=[]`다. 원본은 `presentation-attempts/20261007T041132259214Z/logs/quality-review.json`의 exit 0 JSONL이다. 동일 후보와 검사 프롬프트의 일치를 확인했으며 값을 강제로 통과시키지 않았다.
- 최종 11장, 시간 배분 420초, 대본 공백 제외 2,506자. [quality.json](../output/neofirm-20261007T032143604608Z/quality.json)의 한글·잘림·PPTX 재열기 검사를 통과하고 실제 contact sheet·페이지를 열어 확인했다. 시간은 배분·발화 속도 가정이며 실제 발표 측정이 아니다. PPTX 본문은 페이지 이미지여서 텍스트 편집이 불가하고 발표자 노트는 텍스트다.
- 전체 테스트 25개 통과. 공통 CLI 어댑터의 짧은 정상 JSON·완료 trace 복구·실패 거부, CLI JSONL 경계부터 실제 PPTX/PDF 렌더링·게시까지의 통합 검사를 포함한다. 통합 fixture의 모델 응답은 가짜 테스트 데이터이며, 위 최종 실물과 실제 완료 trace의 증거와 구별한다. Python 컴파일·shell 구문 검사도 통과했다.

## 이전 실패·복구 이력

2026-10-07 로그인 복구: 초기 인증 파일의 SID·PSIDTS 누락을 확인하고 로그인 대기·서버 검사를 수정했다. 사용자 Mac의 `AUTH OK`와 최신 `neofirm-20261007T032143604608Z/logs/auth-notebooklm.json` exit 0으로 실제 복구를 확인했다. 전용 브라우저 프로필은 삭제하지 않았다.

2026-10-07 조사 복구: 최초 `research-1.json`은 인용이 없어 거부·보존했다. 사용자 Mac 재개 후 최신 세 질문의 실제 references는 24·7·14개이며 source ID 매핑을 확인했다. 조사 수정의 실제 성공을 확인했고, 역할별 9회와 종합 1회 CLI JSONL에서도 `turn.completed`를 확인했다.

2026-10-07 초기 발표 복구 시점: `quality-review.json`은 공급자 매출 구조 누락, 토론 변경의 claim_id 연결 누락, 미확인 항목의 확인 범위를 지적했다. 생성과 검사 프롬프트를 맞추고 실제 지적을 다음 후보에 전달하는 최대 3회 수정 흐름을 구현했다. 당시 테스트 23개가 통과했지만 공통 CLI 어댑터를 대체한 테스트여서 정상 JSON을 80자 미만이라고 거부하는 오류를 잡지 못했다. 최종 수정은 출력 계약·완료 trace·검사 대기 재개를 공통 어댑터까지 검증하며, `p.19 … 100건`의 100을 페이지로 읽는 오류도 수정했다. 실패 후보·검사·JSONL과 코드 hash 갱신 이력은 그대로 보존했다. [결정 기록](decisions.md) 참조.

| 항목 | 실제 증거 | 남은 조건 |
|---|---|---|
| Phase 0 도구 준비 | Codex 0.160.1, 비공식 notebooklm-py 0.8.4 설치·도움말; 사용자 Mac 서버 인증·CLI preflight 성공 | 인증 만료 시 재확인 |
| Phase 4 입력·조사 | 22페이지 보고서·일차자료 5개 등록; 실제 조사 3회와 인용 24·7·14개, research.md·source 매핑 | 현재 입력 기준 완료; 별도 공식 공지 확보 시 대조 |
| Phase 5 자동 토론 | NotebookLM 조사 기반 독립 CLI 9회+종합 1회, 토론·수정·JSONL 확인 | 현재 입력 기준 완료 |
| Phase 6 발표 | 최신 라이브 후보 11장·실제 독립 내용 검사 통과·PPTX/PDF 렌더링·최종 게시 완료 | 공식 공지 대조·실제 리허설 |
| Phase 7 구현 | 한 명령 러너, 실행별 상태·로그·재개, 전체 25개 검사·최종 COMPLETE 및 멱등 재실행 | 현재 입력 기준 완료 |

## 실행 ID와 산출물

원문 기반 선행 검토: `runs/neofirm-20261007T030820373716Z/`.

- `report.md`, `primary-research.md`, `research.md`, `sources.json`: 실제 열람한 원문·요약·출처. **NotebookLM 조사 결과가 아니다.** S1은 제공 보고서, S2–S6은 원문 열람 자료이며 원격 source ID는 아직 없다.
- `round-{1,2,3}-{market,execution,skeptic}.md`, `debate.md`, `conclusion.md`: 실제 독립 Agent 발언과 claim_id별 반박·수정. 각 역할은 라운드 1에 다른 역할의 입장을 받지 않았고 후속 라운드는 직전 전체 라운드를 읽었다.
- `debate-provenance.json`: 실제 Agent task 경로와 토론 프로토콜. 원본 task 메시지는 이 Codex 대화 기록에 있다. 이 파일을 `codex exec` 원본 JSONL이라고 주장하지 않는다.
- `slides.json`, `slides-outline.md`, `speaker-notes.md`, `neofirm-review.pptx`, `neofirm-review.pdf`, `contact-sheet.png`, `quality.json`, `quality-review.json`.

공유하기 쉬운 검토용 묶음은 [`output/neofirm-review/`](../output/neofirm-review/)에 있다. [PPTX](../output/neofirm-review/neofirm-review.pptx), [PDF](../output/neofirm-review/neofirm-review.pdf), [대본](../output/neofirm-review/speaker-notes.md), [토론](../output/neofirm-review/debate.md).

라이브 러너 실패 기록: `runs/neofirm-20261007T031742014417Z/state.json`, `logs/auth-notebooklm.json` — `failed_stage=auth`, 종료 1. Google 인증 파일이 없어 source 등록이나 원격 노트북 생성까지 진행하지 않았다. 이전 확인 실행 `neofirm-20261007T031108916293Z`도 동일 auth 실패였으며 전체 성공 로그가 아니다.

## 초기 준비 실행한 명령과 결과(당시 기록)

```sh
.venv/bin/notebooklm --version
env NOTEBOOKLM_HOME="$PWD/.local/notebooklm" .venv/bin/notebooklm login --help
env NOTEBOOKLM_HOME="$PWD/.local/notebooklm" .venv/bin/notebooklm auth check --help
env NOTEBOOKLM_HOME="$PWD/.local/notebooklm" .venv/bin/notebooklm source add --help
env NOTEBOOKLM_HOME="$PWD/.local/notebooklm" .venv/bin/notebooklm source wait --help
env NOTEBOOKLM_HOME="$PWD/.local/notebooklm" .venv/bin/notebooklm ask --help
sh scripts/run-neofirm.sh --prepare
.venv/bin/python scripts/render_neofirm.py runs/neofirm-20261007T030820373716Z --draft
.venv/bin/python -m unittest discover -s tests -v
sh scripts/run-neofirm.sh
```

도움말·입력 추출·초안 렌더링 성공. 전체 로컬 테스트 **20개 통과**(NeoFirm 5개 + 기존 GCS 15개). Python 컴파일과 두 shell 스크립트 구문 검사도 통과했다. fixture는 출처 누락/범위 밖 페이지 거부, 불확실한 원격 생성의 재조회·중복 방지, 조사 인용 매핑·재시도, 독립 라운드 전달, 실패 응답 재사용 금지, 내용검사 실패 시 발표 미생성을 검증한다. fixture에 Google·LLM 실제 호출은 없다.

`sh scripts/run-neofirm.sh`는 NotebookLM 인증 단계에서 실패했다. 별도 읽기 검사 `list --json`은 `AUTH_REQUIRED`였고, 별도 `codex exec --skip-git-repo-check --ephemeral --sandbox read-only --json ...`는 app-server 초기화 `Operation not permitted`로 실패했다. 안전장치 해제나 인증값 복사로 우회하지 않았다.

## 선행 검토용 초안 검사와 실질적 제한

12페이지 모두 scale=1.0, 잘림 없음, 한글 제목 추출 검사 통과. PDF를 렌더링한 각 페이지와 전체 contact sheet를 실제 확인했다. PPTX 재열기 및 슬라이드 수 검사 통과. PPTX는 PDF 페이지 이미지와 텍스트 발표자 노트로 구성해 배치를 보존하며 **본문 텍스트는 편집 불가**다.

계획 시간 합은 420초, 대본은 공백 제외 2,074자다. 시간은 발표 배분과 초당 한글 약 7자 가정으로 점검한 것이며 실제 육성 리허설 시간은 측정하지 않았다. 공식 발표 시간은 미확인이다.

반대/검증 Agent가 출처·A/B/C 7항목·수치·단위·원가식·토론 반영을 별도로 점검해 `quality-review.json`의 `passed=true`, `issues=[]`를 기록했다. 이 통과는 **원문 기반 검토용 초안**에 한정되며 NotebookLM 실행 성공이나 사업의 안전성·적법성 검증이 아니다.

가격 10만원·전문가 20분·공헌이익 4만원은 시뮬레이션 가정이다. 전문가 40분이면 가정 공헌이익은 0원이며 순마진이 아니다. 국내 고객 지출·보험·사업구조 적합성·데이터 권리·장기 품질은 미확인이다. 품질 100건과 유료 100건은 설계 제안이며 실제 고객 시험·예약·초대·외부 연락은 수행하지 않았다. GCS/Calendar ID는 해당 없음.

## 다음 한 단계

**최종 파일로 실제 7분 리허설을 한다.** 완료 조건은 육성 소요 시간 측정, 한글·인용 최종 확인과 공식 공지 확보 시 조건 대조다. 최종 생성 명령은 이미 성공했으므로 다시 실행할 필요가 없다. 일반적인 원문/코드/옵션 변경은 새 run을 요구하며 이번 현재 실행의 단계별 호환성 갱신만 근거를 별도 기록했다. 이번 수정에서 GCS 예약·Calendar·외부 자료 등록은 하지 않았으며 해당 ID는 없다.
