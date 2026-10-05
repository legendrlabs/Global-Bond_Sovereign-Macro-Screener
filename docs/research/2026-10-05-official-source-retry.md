# 출력 개선 후 공식 자료 재조사

범위: 연구 기록만 추가. 이번 조사 결과로 collector/config/점수/게이트를 변경하지 않았다.

## 포르투갈 — 기존 403 경로가 200으로 응답

공식 시리즈 화면: https://bpstat.bportugal.pt/serie/12099457

실제 무인증 데이터 요청:
https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?lang=EN&series_ids=12099457&last_n=5

- HTTP 200, 177,531 bytes, JSON-stat 2.0.
- SHA-256 `2c130f200b3d1268e40567c396164842cb39ef2c1c7a948c17e76916cf66e4a5`.
- series id 12099457。label: Yield on Treasury bonds with fixed rate and residual maturity of 5 years.
- dimension labels: Source=LSEG; Prices; Yield on TB; Average; Daily; Residual maturity=5 years; Reference territory=Portugal; Unit of measure=Percentage.
- Bank of Portugal가 공개하는 데이터이지만 원공급자는 LSEG로 표시된다. 공개 접속 성공을 재배포 허가로 취급하지 않는다.
- observation update 시각 `2026-10-02T16:00:00Z`, 마지막 reference date `2026-10-01`. 7,966개 관측 값과 날짜가 반환됐다. `last_n=5`가 기대한 5개 제한으로 작동하지 않았으므로 후속 구현에서는 응답 길이와 날짜 필터를 검증해야 한다.
- extension의 num_series=14와 달리 응답의 series 메타데이터는 선택한 1개이며, reference_date 외 8개 dimension size가 모두 1이다. future parser는 series id와 모든 dimension/category를 명시적으로 검증해야 한다.
- 별도 시리즈 메타데이터도 무인증 200, 671 bytes:
  https://bpstat.bportugal.pt/data/v1/series/?series_ids=12099457&lang=EN
- 고정금리 잔존 만기 5년 수익률이라는 정의를 benchmark 또는 constant-maturity와 임의로 동일시하지 않는다. 실제 수집 경로가 열린 점은 확인됐으나, country definition 계약과 재배포 검토 및 parser 검증 전 새 연결로 집계하지 않는다.

## 아일랜드 — B.3 원본 경로가 다음 조사 후보

공식 목록:
https://www.centralbank.ie/statistics/data-and-analysis/credit-and-banking-statistics/retail-interest-rates

검색/페이지 자료에서 Table B.3 Official and Selected Interest Rates (XLS)를 확인했다. 과거 월간 통계에는 대표 2/5/10년 정부증권 수익률이 있었으므로 현재 B.3의 실제 열·정의·관측일을 확인하는 것이 다음 후보이다. 목록의 최신 retail interest release는 July 2026이며, 이 사실만으로 B.3의 5년물 최신성이나 존재를 확정하지 않는다.

직접 공식 목록 요청은 첫 시도와 재시도 모두 ReadTimeout. XLS 원본을 확보하지 못해 IRL 연결 유지 보류. 보유액 통계와 경매 결과를 5년 secondary-market yield로 대체하지 않는다.

## 슬로베니아 — 공식 API 목록 확인, 실제 요청 타임아웃

문서: https://www.bsi.si/sl/api-dokumentacija

문서가 inflation, interests, daily/monthly/client FX endpoint를 안내한다. `https://api.bsi.si/interests?date=2026-09`는 두 차례 ReadTimeout. 응답을 확인하지 못했으므로 interests에 5년 국채가 있다고 판단하지 않는다. 공개 PxWeb convergence 장기 금리 역시 특정 5년물로 대체하지 않는다.

## 불가리아·리투아니아·나머지

- BNB Q2 공식 XLSX https://www.bnb.bg/bnbweb/groups/public/documents/bnb_download/gssm_2026_06_a1_en.xlsx 재시도 포함 두 차례 ReadTimeout. 기존 원본 조사와 구별해서 기록.
- 리투아니아 중앙은행의 정부증권 경매 목록은 수익률 %, ISIN, 실제 잔존일수를 제공한다. 약 5년 발행물이라도 일별 잔존 5년 benchmark 시계열로 대체하지 않는다. 공식 금융시장 목록 https://www.lb.lt/en/financial-markets-statistics 에서는 경매 결과 및 Government Securities Index를 확인했으며, 지수의 weighted yield를 5년물로 사용할 근거는 확보하지 못했다.
- 덴마크·오스트리아·NZ의 추가 검색에서는 새 검증된 무인증 공식 5년 경로를 확보하지 못했다. RBNZ의 NZFMA/LSEG 원공급자 및 benchmark 정의 설명은 후속 권리 검토 근거로 남긴다. 허용 조건이 미확정인 RBNZ 무인 자동 다운로드는 실행하지 않았다.
- 크로아티아 정부 라이선스 URL은 200이나 짧은 JS 페이지 응답이므로 권리 확정 근거로 추가하지 않았다.

요청마다 connect/read timeout 5/15초, 막힌 공식 경로는 재시도 1회 후 중단했다. 403 우회나 실패를 데이터 부재로 단정하지 않았다. 다음 우선순위는 PRT 원공급자/정의/재배포 계약 확인과 IRL B.3 원본 확보이다.
