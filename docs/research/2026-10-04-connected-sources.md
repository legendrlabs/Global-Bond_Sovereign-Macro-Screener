# 공식 어댑터 추가 연결 — 2026-10-04 KST

사용자가 계속 진행을 요청하여 기존 설계 안에서 ISL·ESP·SVK·ISR를 연결했다.
API 키·계정·쿠키 없이 아래 공식 다운로드 네 개가 첫 병렬 요청에서 모두
HTTP 200을 반환했다. 원자료는 공개 저장소에 포함하지 않는다.

| 국가 | 공식 경로 / 계열 | 직접 받은 파일의 마지막 유효 기간 | 정의 및 처리 |
|---|---|---|---|
| ISL | [CBI FLV XLSX](https://sedlabanki.is/library?itemid=4b7a7e67-a647-4e98-9190-0c1ca772179f), nominal par 5Y | 2026-10-01 | FLV의 nominal par 그룹과 5년 열 선택; % Excel 서식 확인 후 소수 ×100; correction·note reference 보존 |
| ESP | [BdE TI_1_3 CSV](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_3.csv), D_G0B1F0ZO | 2026-09-30 | 국채 유통시장 5 Años, Porcentaje, DIARIA 메타데이터 검증; CP1252·스페인어 월·결측 `_` 처리 |
| SVK | [NBS YC_Data XLSX](https://nbs.sk/dokument/b912f986-f5ab-4a02-9033-97976d6dc849/stiahnut?force=false), Yields_SK / ZCY5Y | 2026-09-25 | 추정 제로쿠폰; 연·월·일 필드; % 서식이 없는 원래 백분율 수치 유지; 주 1회 배포를 일별 최신성으로 착각하지 않음 |
| ISR | [BOI ZCM SDMX](https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/ZCM/1.0/ZC_TSB_ZND_05Y_MA?startPeriod=2026-08-01) | 2026-09 | FREQ=M, NOMINAL_REAL=N, DATA_TYPE=ZC_YTM, TIME_TO_MATURITY=Y05T05, TIME_COLLECT=A, UNIT_MEASURE=PT, UNIT_MULT=0 검증 |

## 숫자를 넣기 전에 유지한 구분

- 모든 추가 국가의 baseline_compatible은 false, redistribution은 pending이다.
  연결했다는 이유로 금리 정의 호환성이나 공개 숫자 배포를 승인하지 않는다.
- [CBI 공식 설명](https://cb.is/statistics/interest-rates/)은 par와 zero,
  nominal과 inflation-indexed를 구분한다. 실제 발행 종목 YTM과 동일하지 않다.
- [NBS 공식 설명](https://nbs.sk/en/statistics/financial-markets/interest-rates/estimated-yield-curve/)
  은 NSS 추정 곡선·월요일 갱신·낮은 시장 유동성과 추정 오차를 설명한다.
  2026-10-04 기준 2026-09-25 관측은 기존 7일 최신성 기준에서 STALE이다.
- ISR 관측 기간을 `2026-09`로 보존한다. 이를 9월 말 일별 종가로 바꾸지 않는다.
  기존 일별 quality gate가 FREQUENCY_OR_DATE로 보류한다.
- 자료를 처음 직접 받은 뒤 동일한 공식 어댑터를 HttpClient로 재검증한 실행에서는
  ISL·SVK·ISR 읽기 타임아웃, ESP 정상 파싱이었다. 앞서 받은 다운로드의 성공과
  재요청 실패를 각각 기록하며, 실패 요청에 과거 캐시를 현재값으로 대체하지 않는다.

## 코드 및 검증 범위

합성 fixture는 다른 만기·명목/실질·par/zero·백분율 스케일·월주기·미래월·중복
기간·빈 값·공식 footer와 설명 문단/교정 열 혼동을 점검한다. 별도 검토에서
Excel의 문자 그대로 표시하는 `%` 서식을 배율 근거로 잘못 받아들일 위험을
발견해, 실제 확인한 배율 서식만 허용하도록 수정했다. 회귀 테스트 실패를
확인한 뒤 수정했으며 전체 **57개 테스트가 통과**했다.

공개 모드 전체 실행(2026-10-04 기준)은 27개 행과 보고서/품질 상태를 작성했다.
ISL·SVK는 첫 시도 타임아웃 뒤 200, ISR은 타임아웃 뒤 502, ESP는 타임아웃이었다.
IMF 재정 요청도 타임아웃으로 전체 DATA_HOLD이며 공개 보고서 파생 숫자는
모두 비어 있었다. 부분 성공을 완전한 최신 데이터 확보로 판정하지 않는다.

별도 검토의 경미한 후속 항목: ISL 교정·주석 헤더의 이름 변경이나 중복을
현재 명시적으로 오류 처리하지 않는다. 받은 원본·해시를 보존하고 현재 헤더에서는
교정 플래그가 정상 기록되지만, 주석 헤더 변경 감지는 후속 보강 대상이다.

어댑터 등록 국가: **17/27** (일별 16, 월평균 1). 미연결: **10/27** —
NZL, CZE, BGR, IRL, DNK, LTU, HRV, SVN, AUT, PRT.
이는 매 실행 성공 수나 점수 사용 가능 수가 아니다.

다음 조사 순서는 HRV 월별 공식 파일의 단위/정의, PRT 공식 API 직접 접근,
IRL·DNK·LTU·SVN·AUT의 국가별 5Y 계열이다. NZL 자동 수집 제한과 CZE
REST 인증 조건은 기존 [NZL/CZE/BGR 기록](2026-10-04-nzbcz.md)을 따른다.
