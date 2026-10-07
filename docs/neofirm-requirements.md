# NeoFirm 과제 입력 요구사항

확인일: 2026-10-07 KST

상태: **원문 열람·Codex 독립 토론 실행·자동화 구현; NotebookLM 최초 로그인 대기**

## 현재 확인된 과제 문장

사용자가 제공한 요지는 다음과 같다.

> 몰입캠프 2일차 과제(NeoFirm)의 자료 조사, AI Agent 간 토론, 최종 발표 자료를 Codex와 NotebookLM CLI를 이용해 완전 자동으로 만든다. 참고자료는 `ChatGPT-2026-NeoFirm Report`다.

2026-10-07 사용자가 **Codex + NotebookLM CLI**를 명시해 진행을 요청했다. 이전 문서의 Claude Code 요구는 이번 실행에 적용하지 않는다. 별도 공지가 없어 보고서 18–20페이지의 활동 A/B/C와 평가기준으로 검토용 발표를 만들고, 발표 시간은 임시 7분으로 설정한다. 공식 과제 공지와 다른 조건이 나오면 이를 우선한다.

## 확보한 자료

| 자료 | 위치 | 확인 내용 |
|---|---|---|
| `ChatGPT-2026-NeoFirm Report` | [`inputs/ChatGPT-2026-NeoFirm-Report.pdf`](../inputs/ChatGPT-2026-NeoFirm-Report.pdf) | 22페이지. 네오펌 정의, 사례, 수업 활동안, 위험·평가 기준 |
| 참고 학생 발표 | [`inputs/reference-immersive-camp-presentation-team3.pdf`](../inputs/reference-immersive-camp-presentation-team3.pdf) | 10페이지. 형식 참고용이며 공식 평가 기준이나 사실 출처로 사용하지 않음 |

SHA-256:

- 보고서: `20e72a1db36e4fe6650985fdbe584076e24d5de694fd7b491047d959a7bb873a`
- 참고 발표: `d41088a42d5abbae962b9254867bf778b672bfda8831a1b0b1d75f074e1a5e8e`

## 보고서에서 확인한 수업 요구

`ChatGPT-2026-NeoFirm-Report.pdf` 19페이지의 수업 활동안에는 다음을 요구한다.

- 기존 전문서비스 가치사슬 해부: 고객 결과, 단계별 담당자·시간·오류, 공급자 매출 구조, 대기·재작업·불확실성
- AI와 전문가의 작업 배분: 정상 반복작업, 검증 가능한 초안, 모호·고위험 판단, 금지 작업
- 1페이지 투자메모: 시장·현재 지출, 좁은 첫 업무, 결과 단위·가격, 전문가 개입률·품질지표, 책임·보험·규제, 100건 후 데이터, 직접 서비스 이유

20페이지는 품질·책임·데이터 권리·규제·모델 상품화·서비스 함정·인수통합·결과과금 왜곡 위험과 고객/품질/경제성/학습 KPI를 제시한다.

보고서 19–20페이지는 참고 보고서의 수업 활동·평가 기준으로 기록했으며, 공식 과제 원문이 확보되면 우선순위를 다시 대조한다.

## 확보가 필요한 입력

- [ ] 몰입캠프 2일차 NeoFirm 과제 원문
- [x] `ChatGPT-2026-NeoFirm Report` 원본 파일 확보 및 SHA-256 기록
- [ ] NotebookLM에 넣을 수 있는 계정·인증 권한
- [ ] 공식 발표 시간과 제출 형식(`.pptx`, `.pdf`, 대본 등)
- [ ] 평가 기준과 필수 분석 프레임
- [x] 이번 실행 도구: 사용자가 Codex + NotebookLM CLI로 명시 (Claude Code 불필요)
- [ ] 수업에서 지정한 NotebookLM CLI 이름·설치 방법·버전 및 인증
- [ ] 추가 조사가 허용되는 출처 범위와 인용 형식

## 확보 후 생성할 산출물

1. `runs/<run-id>/research.md`
2. `runs/<run-id>/sources.json`
3. `runs/<run-id>/debate.md`
4. `runs/<run-id>/conclusion.md`
5. `runs/<run-id>/slides-outline.md`
6. `output/neofirm-final.pptx` 및 필요 시 PDF·발표 대본

각 주장과 수치는 source ID와 원문 위치로 추적하고, 확인하지 못한 내용은 `미확인`으로 표시한다.

## 도구 상태

- `codex-cli 0.160.1` 설치. 이 작업 세션에서 3명의 독립 Codex Agent를 실제 실행했다. 샌드박스에서 별도 `codex exec`는 app-server 초기화 `Operation not permitted`로 실패한다. 한 명령 파이프라인의 CLI 세션 실행은 사용자 호스트 터미널에서 검증해야 한다.
- `.venv/bin/notebooklm`: 비공식 `notebooklm-py[browser] 0.8.4 (bff7c66e)` 설치 완료. 실제 도움말에서 `login --browser chrome`, `create --json`, `source add/list/wait -n ... --json`, `ask -n ... --json`을 확인했다. 초기 인증 파일은 없고 `list --json`은 `AUTH_REQUIRED`로 종료했다.
- [프로젝트 저장소](https://github.com/teng-lin/notebooklm-py)는 비공식·문서화되지 않은 API 사용을 명시한다. 버전을 `requirements-neofirm.txt`에 고정했고 상위 서비스/API 변경 시 재검증이 필요하다. Google 공식 일반 NotebookLM CLI로 소개하지 않는다.

## 이번 검토의 범위와 출처

- 주제(작성 가정): 한국 B2B 표준 NDA 검토 결과 서비스. NeoFirm은 보고서의 전문서비스 분석 개념이며 특정 기업명이 아니다.
- 제출 형식(작성 가정): 16:9 PPTX + PDF + 발표 대본. PPTX는 PDF를 렌더링한 이미지 슬라이드와 텍스트 발표자 노트로 구성해 한글·배치가 동일하게 보인다. 슬라이드 본문은 편집 가능한 텍스트가 아니다.
- 참고 학생 발표는 형식만 열람했다. 수치·가격·효과의 출처로 쓰지 않았다.
- 추가 일차자료: `docs/neofirm-primary-sources.json`의 Index Ventures, Crosby, 혜움, BHSN, General Catalyst. 기업/투자자 자기보고와 검증된 성과를 구별한다.
- 국내 시장규모·현재 고객지출·지불의사·책임보험·법률 적합성은 미확인이다. 가격·원가·100건 시험은 설계 제안이며 실제 거래·시험 실적이 아니다.
