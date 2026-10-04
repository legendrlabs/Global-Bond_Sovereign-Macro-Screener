# Executive Summary 출력 개선 검증

범위: v0.1.0-preview.1의 수집·점수·게이트를 유지하는 presentation change.

## 구현

- `summary.py`: redaction 이후 result를 받는 pure summary builder와 text/Markdown/HTML formatter. 상태는 quality, 순위는 기존 usable_baseline과 baseline_rank에서 파생.
- `cli.py`: 기본 3줄 대신 summary 출력. 보고서와 current pointer 경로 유지.
- `report.py`: latest.md 상단 summary, 기존 전체 진단 테이블 유지. HTML 카드 아래 summary 삽입, 검색은 기존 전체 국가 행에만 적용. executive_summary.json 저장 및 manifest 해시 포함.
- `interactive.py`: 갱신을 거절하거나 최신 저장 보고서를 열 때 같은 저장 summary 표시. 구버전 보고서는 기존 안내 유지. 모드와 demo를 검증한 보고서만 사용.
- `pipeline.py`: 실제 bundle의 국가별 5년물 관측 수만 coverage 메타데이터에 추가. 관측이 파싱됐어도 stale/definition/frequency gate에서 제외될 수 있으므로 Baseline 사용 가능 수와 구분. 등록 경로 메타데이터가 없으면 UNKNOWN.
- 공개 모드 숫자·분류 복원 없음. demo는 실사용 랭킹과 AVAILABLE Decision을 표시하지 않음. Adjusted 점수/순위 생성 없음.

## 검증

- `python -m unittest discover -s tests -v`: 기존 75 + 신규 13 = 88개 통과.
- 신규 테스트: partial/full/zero/demo 판정, rank 누락·제외·정렬, 실제 오류 표시, ranked 국가의 보조 축 HOLD, public redaction, renderer 일관성, HTML escaping, 실제 parsed count와 stale 분리, app 갱신 거절.
- `python -m sovereign_macro demo --output results/demo --public-output`: SYNTHETIC DEMO, 0/27, 실사용 순위 없음, 모든 Decision SYNTHETIC DEMO.
- `python -m sovereign_macro run --output results/local`: 실제 수집 성공。상태 표시와 ranked-country HOLD 수정 후 재실행 `20261004T164307-07c4ac98`: DATA_HOLD / SAFE_TO_USE FALSE / PARTIAL BASELINE, 실제 파싱 16개, Baseline 6/27, Adjusted 0/27. 순위 NOR, CAN, SWE, NLD, DEU, GBR. CZE ReadTimeout과 FRA HTTP_FAILURE:429를 포함한 실제 오류 표시. 후속 KRW 표의 5Y·실질금리 병기는 같은 저장 summary 모델을 최신 formatter로 재렌더링해 검증.
- v0.1.0-preview.1에 대응하는 이전 pipeline과 현재 pipeline을 public/private, demo/live 평가, 완전/결측 bundle의 8가지 조합으로 비교: coverage 메타데이터 제외 전체 result 동일.
- 독립 리뷰에서 ranked 국가의 FX/CPI/10Y 오류 누락을 발견해 회귀 테스트를 먼저 실패시킨 후 수정. 재검토에서 잔여 blocker 없음.

점수식, scoring.yaml, 국가별 정의, source collector, 재배포 및 최신성 게이트 변경 없음. 기존 프리릴리스 파일은 변경하지 않고 PR의 후속 코드에 반영한다.
