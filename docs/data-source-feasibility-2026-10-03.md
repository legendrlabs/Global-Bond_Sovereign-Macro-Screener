# 공식·무인증 데이터 경로 조사

조사일: 2026-10-03 UTC. 승인된 설계: [2026-10-04 sovereign macro design](superpowers/specs/2026-10-04-sovereign-macro-design.md).

이 문서는 설계를 변경하지 않는 자료조사 결과다. 제품 코드·워크플로는 작성하지 않았다. 공개 HTTP 요청에 사용자 인증·API key를 넣지 않고 내려받은 자료와, 문서만 확인한 후보를 구분한다. 현재 수신 가능하다는 사실은 재배포 권한·향후 가용성·동일한 수익률 정의를 보장하지 않는다.

## 결론

- 재정·물가: IMF DataMapper v2가 공통 경로다. 순부채 API의 SVK 결측은 같은 April 2026 Fiscal Monitor 공식 부록 A8 표로 보완할 수 있다. 총부채로 대체할 필요가 없다.
- 5년물: 16개국에서 일별 5년물 자료 다운로드와 숫자·관측일을 확인했다. 이번 후속 조사에서 KOR와 ITA가 추가되었으나 ITA의 응답은 8월말까지만 포함하여 최신성 보류다. 단, SVK는 공식 추정 제로쿠폰 곡선이고 DEU/NLD/FRA/GBR는 Riksbank가 제공하는 Refinitiv 계열이다. 그대로 같은 정의의 Baseline 입력으로 승인된 것은 아니다.
- ISR: 월평균 명목 5년 제로쿠폰 자료까지 확인했다. HRV도 공식 월별 엑셀의 5년 열 숫자를 받았지만 정의·단위 대조가 남아 있다. 일별 기준 입력으로 바로 승인하지 않는다.
- NZL: 공식 일별 자료와 다운로드 주소는 찾았지만 직접 다운로드는 403이었다.
- PRT는 정확한 일별 계열과 숫자까지 연구용 대행 조회로 확인했지만 배포 환경의 직접 요청은 403이었다. 일별 원자료·경로가 아직 미확정인 국가는 9개국이다. 이는 공식 자료가 존재하지 않는다는 결론이 아니다.
- 시장품질: BIS 국채 잔액과 일부 국가의 거래량은 확보 가능하다. 27개국 공통 유동성·등급·자본통제 자료 및 하나의 완성된 점수는 확보하지 못했다. Adjusted의 해당 축을 임의 수치로 채우거나 가중치를 재배분하지 않는다.

## 1. 재정·물가: IMF

[공식 DataMapper API 안내](https://www.imf.org/external/datamapper/api/) — v2를 사용한다.

| 항목 | 정확한 지표 코드 | 확인 결과 |
|---|---|---|
| 일반정부 순부채 / GDP | GGXWDN_G01_GDP_PT | API에서 대상 26개국, SVK 없음 |
| 일반정부 전체 재정수지 / GDP | GGXCNL_G01_GDP_PT | 대상 27개국 키 확인 |
| 일반정부 총부채 / GDP | G_XWDG_G01_GDP_PT | 대상 27개국 키 확인 |
| 연평균 CPI 상승률 | PCPIPCH | 대상 27개국 키 확인 |

예: https://www.imf.org/external/datamapper/api/v2/GGXWDN_G01_GDP_PT

GGXONLB는 primary balance이므로 전체 재정수지 대체값으로 사용하지 않는다. API 국가 필터가 기대와 다르게 작동할 수 있으므로 응답을 정확한 ISO3로 선택하고 필수 연도를 검증한다. 대상 국가 키가 있다는 것과 모든 필수 연도가 유효하다는 것은 별도 검증 사항이다.

이번 확인 판본은 Fiscal Monitor / WEO April 2026, 전망 종단은 2031년이다. October 판본 등으로 갱신되면 이전 판본 PDF와 혼합하지 않는다. API 조회시각을 전망의 정보 기준일로 표기하지 않는다.

### SVK 순부채 결측 해소

[공식 IMF April 2026 부록 PDF](https://www.imf.org/-/media/files/publications/fiscal-monitor/2026/april/english/msa.pdf), Table A8, PDF 23번째 페이지에서 텍스트 추출과 표 이미지로 확인했다.

| 연도 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 |
|---|---:|---:|---:|---:|---:|---:|
| Slovakia 일반정부 순부채 / GDP (%) | 58.0 | 60.5 | 62.8 | 65.3 | 68.2 | 71.5 |

표는 0.1%p로 반올림되어 있다. PDF 값의 정밀도를 API와 같다고 표시하지 않는다. 부록의 정보 기준일은 2026-04-01이다.

구현에 넘길 공통 규칙: **같은 공급자·같은 판본·같은 지표·같은 연도의 공식 다운로드 표**만 API 결측 보완 후보로 허용한다. 모든 국가에 적용 가능한 원자료 우선순위이며 SVK 점수 예외가 아니다. 판본, 표 번호, 페이지, 파일 해시, 단위, 반올림 정밀도와 원자료 출처를 기록하고 API와 중복되는 국가를 대조한다. 공식 파일을 못 받거나 판본이 다르면 DATA_HOLD다.

## 2. 27개국 5년물 확인표

표의 값은 수집 경로 확인용 표본이다. 채권 추천이나 통일된 시점의 랭킹이 아니다. 확인 상태는 다음 의미다.

- **수신**: 인증 없이 실제 파일/API에서 5년 지표·값·관측일 확인.
- **조건부**: 수신했지만 주기·정의 차이 때문에 일별 Baseline에 바로 투입하지 않음.
- **후보**: 공식 페이지나 다운로드 경로만 확인했으며 파싱·가용성 미확정.
- **연구용 수신·직접 접근 보류**: 연구용 대행 조회에서 숫자를 받았지만 배포 환경의 무인증 직접 수집은 검증되지 않음.
- **미확정**: 이 조사에서 사용할 정확한 5년물 경로를 확정하지 못함.

| ISO3 | 국가 | 상태 | 공급자 / 정확한 식별자 | 확인 관측일·값 (%) / 남은 사항 |
|---|---|---|---|---|
| ISL | 아이슬란드 | 수신 | CBI FLV Excel, nominal par 5Y | 2026-10-01, 7.51; Excel 원값 0.0751은 백분율 포맷 |
| NOR | 노르웨이 | 수신 | Norges GOVT_GENERIC_RATES, TENOR=5Y, GBON | 2026-10-01, 4.71; 가장 가까운 만기 기준채권 정의 |
| AUS | 호주 | 수신 | RBA F2, FCMYGBAG5D | 2026-09-30, 4.983; 보간 고정만기 |
| NZL | 뉴질랜드 | 후보 | RBNZ B2 daily close workbook | 공식 화면 5Y 존재; 직접 파일 요청 403 |
| KOR | 한국 | 수신·조건 검증 진행 | KOFIA BISLastAskPrcROPSrchSO, listTrm, 3007 | 2026-10-02, 오후 4.129; 잔존 4년6월–5년; 재사용 조건 미확정 |
| CZE | 체코 | 후보 | CNB ARAD bond-yield metadata / REST | 월별 5년 basket은 잔존 3.5–6.5년; 일별 정확한 경로 미확정 |
| BGR | 불가리아 | 미확정 | BNB / 재무부 국채 자료 | 원래 5년 발행물의 재입찰 금리는 현재 고정 5년물이 아님 |
| CAN | 캐나다 | 수신 | BoC Valet BD.CDN.5YR.DQ.YLD | 2026-10-01, 3.62; benchmark bond |
| IRL | 아일랜드 | 미확정 | NTMA 발행·입찰 자료 | 개별 발행물 결과를 일별 5Y로 대체하지 않음 |
| DNK | 덴마크 | 후보 | Nationalbank secondary-market / MTS 공개 호가 | DNRENTD는 5Y 없음; MTS 종목별 호가는 고정5Y 아님·직접 403 |
| LTU | 리투아니아 | 미확정 | 재무부 시장 리뷰·입찰 | 리뷰 중단 / 개별 입찰; 고정만기 5Y 미확정 |
| SWE | 스웨덴 | 수신 | Riksbank SEGVB5YC | 2026-10-02, 2.948; 원천 Refinitiv |
| HRV | 크로아티아 | 후보·월표 수신 | HNB G8b XLSX, HRV 시트의 5 g. 열 | 2026-08, 국내 EUR 원값 3.02 / 해외 EUR 3.21; 월평균·만기 정의/단위 대조 필요 |
| NLD | 네덜란드 | 수신 | Riksbank NLGVB5Y | 2026-10-02, 3.3104; 원천 Refinitiv |
| SVN | 슬로베니아 | 미확정 | 중앙은행 / 재무부 후보 | 확인된 10Y convergence를 5Y로 대체하지 않음 |
| DEU | 독일 | 수신 | Riksbank DEGVB5Y | 2026-10-02, 3.1969; 원천 Refinitiv |
| SVK | 슬로바키아 | 조건부·일별 수신 | NBS Yields_SK, ZCY5Y | 2026-09-25, 3.86; NSS 추정 제로쿠폰, 주 1회 배포 |
| AUT | 오스트리아 | 후보·종목 식별 | OeKB benchmark 5Y: AT0000A2NW83 | 공식 기준종목은 식별; 표는 쿠폰·ISIN뿐이며 일별 시장수익률 미수신; UDRB 대체 금지 |
| PRT | 포르투갈 | 연구용 수신·직접 접근 보류 | Banco de Portugal BPstat 12099457, daily | 2026-10-01, 3.60; 일별·주간 갱신·LSEG 원천; 직접 403 |
| ISR | 이스라엘 | 조건부·월별 수신 | BOI ZCM, ZC_TSB_ZND_05Y_MA | 2026-09, 3.716070154; nominal zero-coupon 월평균 |
| ESP | 스페인 | 수신 | Banco de España TI_1_3, D_G0B1F0ZO | 2026-09-30, 3.645; secondary market 5 años |
| GBR | 영국 | 수신 | Riksbank GBGVB5Y | 2026-10-02, 4.932; 원천 Refinitiv; BoE curve는 정의 별도 |
| FRA | 프랑스 | 수신 | Riksbank FRGVB5Y | 2026-10-02, 4.2843; 원천 Refinitiv |
| ITA | 이탈리아 | 조건부·일별 수신·최신성 보류 | Banca d’Italia BMK0200, MFN_BMK.D.020.922.0.EUR.205 | 2026-08-31, 원값 3.50655; benchmark 5-year BTP; 최근 관측 미수신 |
| BEL | 벨기에 | 수신·검증 진행 | NBB DF_IROLOBE2, D.5Y.F | 2026-10-02, 원값 3.89; 고정 잔존만기 OLO; 단위·방법론 최종 확인 필요 |
| USA | 미국 | 수신 | US Treasury daily curve BC_5YEAR | 2026-10-02, 5.06; par constant maturity |
| JPN | 일본 | 수신 | MoF JGB constant maturity, 5年 | 2026-10-01, 2.407; 명목 국채 곡선 |

16개국 일별 직접 수신 = ISL NOR AUS KOR CAN SWE NLD DEU SVK ESP GBR FRA ITA BEL USA JPN. ITA는 실제 수신한 이력이 일별이라는 뜻이며 최신 관측을 확보한 것은 아니다.
월별 ISR까지 직접 수신은 17개국. PRT 연구용 대행 수신까지 숫자를 확인한 국가는 18개국이지만 PRT를 배포판의 직접 수집 성공 수에 포함하지 않는다. 나머지 일별 경로 미확정 9개국 = NZL CZE BGR IRL DNK LTU HRV SVN AUT. 후속 HRV 월별 표 숫자까지 포함하면 숫자를 본 국가 수는 19개국이지만, HRV의 정의 미확정·PRT의 대행 수신까지 합한 숫자이며 최신 일별 계산 입력 확보 수가 아니다. 수신 수는 전체 입력 검증 완료 수가 아니다.

### 인증 없이 수신한 주소와 파싱 주의

**ISL**
https://sedlabanki.is/library?itemid=4b7a7e67-a647-4e98-9190-0c1ca772179f

공식 databank의 공개 config에서 연결된 Excel이다. FLV 시트는 indexed/nominal 및 par/zero를 별도 열로 제공한다. nominal par 5년만 선택한다. 숫자 0.0751에 백분율 서식이 적용되어 있으므로 단위 변환 후 7.51로 사용한다. corrected flag·주석도 보존한다.

**NOR**
https://data.norges-bank.no/api/data/GOVT_GENERIC_RATES/?startPeriod=2026-09-25&format=csv

세미콜론 CSV. TENOR=5Y, INSTRUMENT_TYPE=GBON 등을 정확히 선택한다. 가장 가까운 만기 종목 기반이며 공식 zero-coupon 데이터셋과 혼동하지 않는다.

**AUS**
https://www.rba.gov.au/statistics/tables/csv/f2-data.csv

UTF-8 BOM, 여러 metadata 행 다음에 관측행. Series ID FCMYGBAG5D. Publication date=2026-10-02이나 마지막 유효 5Y 관측은 2026-09-30이었다. 파일 말미 빈 행을 최신 관측으로 사용하지 않는다.

**CAN**
https://www.bankofcanada.ca/valet/observations/BD.CDN.5YR.DQ.YLD/json?recent=3

[Valet 공식 안내](https://www.bankofcanada.ca/valet-api-how-to/): API key·등록 없이 사용 가능. 계열 metadata도 수신하여 5년 benchmark 여부를 검증한다.

**SWE / DEU / NLD / FRA / GBR**
https://api.riksbank.se/swea/v1/Series

관측 예:
https://api.riksbank.se/swea/v1/Observations/SEGVB5YC/2026-09-25/2026-10-02

SEGVB5YC, DEGVB5Y, NLGVB5Y, FRGVB5Y, GBGVB5Y를 각각 조회한다. USGVB5Y/JPGVB5Y도 수신됐지만 USA/JPN은 자국 공식 경로를 우선 후보로 둔다. EMGVB5Y는 유로권 집계이므로 개별국가를 채우는 데 쓰지 않는다.

[Riksbank API 안내](https://www.riksbank.se/en-gb/statistics/interest-rates-and-exchange-rates/retrieving-interest-rates-and-exchange-rates-via-api/): 무료·무등록 호출 가능하나 IP 제한이 있다. FRA/GBR 요청에서 429를 받은 뒤 시간 간격을 두고 재조회하자 200으로 받았다. 순차 호출·캐시·backoff를 사용하고 429를 우회하지 않는다. metadata의 원천은 Refinitiv이므로 정부기관 배포 자료라도 커뮤니티 재배포 조건을 확인해야 한다. 단순히 공공 웹사이트라고 unrestricted license로 표기하지 않는다.

**SVK**
[공식 페이지](https://nbs.sk/en/statistics/financial-markets/interest-rates/estimated-yield-curve/)
https://nbs.sk/dokument/b912f986-f5ab-4a02-9033-97976d6dc849/stiahnut?force=false

실제 파일은 XLSX, Yields_SK 시트, 연·월·일 열 및 ZCY5Y 열. 주 1회 월요일 배포하며 관측 자체는 일별이다. NBS가 계산한 제로쿠폰 곡선이지 발행물 YTM이 아니다. 공식 방법론의 얇은 시장·추정 오차 설명을 보존하고 원본 재현 모델의 수익률 정의와 호환되는지 별도로 판단한다.

**ISR**
https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/ZCM/1.0/ZC_TSB_ZND_05Y_MA?startPeriod=2026-08-01

SDMX XML. FREQ=M, NOMINAL_REAL=N, DATA_TYPE=ZC_YTM, TIME_TO_MATURITY=Y05T05. 날짜 필터를 9월25일부터 걸었을 때 일별 inflation target만 내려왔다. HTTP 200만으로 5Y 확보를 선언하지 않고 정확한 SERIES_CODE·주기·차원을 확인한다. 월자료를 9월말 일별 관측으로 바꾸지 않는다.

**ESP**
https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_3.csv

CP1252 CSV, metadata 6행, D_G0B1F0ZO=5 Años. D_G0B1F0ZE는 ‘2년 초과’이지 5년이 아니다. '_'은 결측. 마지막 유효 관측의 날짜를 사용한다.

**USA**
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2026

Atom XML의 BC_5YEAR. /resource-center-data-chart-center/ 형태의 잘못된 주소는 404였다. 올바른 /resource-center/data-chart-center/ 경로를 사용한다.

**JPN**
https://www.mof.go.jp/jgbs/reference/interest_rate/jgbcm.csv
https://www.mof.go.jp/jgbs/reference/interest_rate/data/jgbcm_all.csv

CP932 CSV, 헤더 5年, 일본 연호 R8.10.1=2026-10-01. 월별 최신 파일과 전체 이력을 구분한다. 공공 곡선과 Riksbank의 benchmark 계열 값이 다르므로 조용히 교체하지 않는다.

### 남은 경로에 대한 구체적 후속 조사

- NZL: [B2 공식 페이지](https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/wholesale-interest-rates), [daily close XLSX](https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx). 직접 요청 403은 인증필수라는 증거가 아니다. 사이트가 지원하는 공개 다운로드 방식·원천 NZFMA/LSEG 조건을 확인한다.
- CZE: [CNB bond metadata](https://www.cnb.cz/docs/ARADY/MET_LIST/cmir_en.pdf), [ARAD REST 문서](https://www.cnb.cz/docs/arad20/dokumentace/arad_rest_api_cs.pdf). API base https://www.cnb.cz/aradb/api/v1 . 월별 3.5–6.5년 basket과 정확한 일별 고정5Y를 구분한다.
- BEL: 공개 계열 D.5Y.F의 실제 일별 값은 수신했다. 단위·방법론·반복 수집 검증은 남아 있으며 상세 주소는 6절에 기록한다.
- KOR: ECOS key를 배포판에 내장하지 않는다. KOFIA 무인증 기간 조회는 수신 검증했으며 재사용 조건을 추가 확인한다. 협회 통계는 정부기관 통계와 출처 유형을 구분한다. 상세 요청은 7절에 기록한다.
- DNK/IRL/LTU/HRV/SVN/BGR/AUT: 공식 중앙은행·부채관리기관의 일별 5Y 파일 또는 공개 통계 계열을 추가 확인한다. PRT는 직접 접근·사용 조건, ITA는 최근 관측·공표 지연·사용 조건이 후속 검증 대상이다. 입찰금리, 10년 convergence yield, 정책금리, 원래 5년 만기로 발행된 오래된 종목, 만기구간 평균, 그래프 픽셀 판독은 대체 입력으로 승인하지 않는다.

## 3. 원화 FX

[ECB 전체 환율 XML](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml)은 무인증 HTTP 200, 7,106개 날짜, 마지막 날짜 2026-10-02를 받았다. EUR 기준 KRW와 각 통화를 같은 날짜로 결합하여 원화 교차환율을 계산할 수 있다. 수익률과 환율의 공통 관측일, 영업일, 결측 구간, 3년 창의 실제 길이를 검증한다.

이번 요청에서 eurofxref-hist.csv는 마지막 날짜가 2010-02-14인 응답을 반환했다. 이번 세션의 해당 CSV는 STALE로 거절한다. CSV가 항상 낡았다는 일반화는 하지 않는다.

BGR의 EUR 전환을 effective-dated currency metadata로 처리한다. 과거 BGN와 EUR를 이름만 바꿔 이어 붙이지 않는다. 환율은 기준 환율이며 실제 체결가격·헤지비용이 아니다.

## 4. 시장품질: 확보한 것과 남은 것

### BIS 국채 시장 규모

[공개 BIS SDMX](https://stats.bis.org/api/v1/dataflow/all/all/latest?references=none)의 WS_NA_SEC_DSS 자료를 실제 수신했다. 구조 NA_SEC의 18개 차원을 확인하고 issuer liabilities만 선택했다. 전체 금융부문 채권이나 정부가 보유한 채권자산을 국채시장으로 혼동하지 않는다.

확인 요청:

https://stats.bis.org/api/v1/data/WS_NA_SEC_DSS/Q.N.US+JP+KR+IS+NO+AU+NZ+CZ+BG+CA+IE+DK+LT+SE+HR+NL+SI+DE+SK+AT+PT+IL+ES+GB+FR+IT+BE.XW.S13+S1311.S1.N.L.LE.F3.T._Z.USD._T.N+F+M.V.N._T?startPeriod=2026-Q1&endPeriod=2026-Q2

- USD 단위, UNIT_MULT=9는 십억 달러.
- S13=일반정부, S1311=중앙정부. 서로 합산하지 않는다.
- ACCOUNTING_ENTRY=L=발행부채, STO=LE=기말잔액, F3=채무증권, MATURITY=T=전체 만기.
- VALUATION=N/F/M은 nominal/face/market. 국가마다 다른 값을 몰래 섞지 않는다.
- 서로 다른 sector·valuation을 포함한 전체 요청에서는 25개국, 92개 계열을 받았다. ISL/NZL은 이번 필터·기간에서 미수신.
- 동일 일반정부·nominal 조건은 21개국, 동일 일반정부·market 조건은 24개국. 따라서 ‘27개국 공통 동일기준 확보’가 아니다.
- 다수 최신 관측은 2026-Q1. 분기 자료의 정당한 공표 지연은 일별 수익률 freshness와 별도로 검증한다.

발행잔액은 규모 지표다. bid-ask spread, 회전율, 거래 체결 가능성 또는 등급 점수가 아니다.

### 거래량·신용등급·자본통제

[Norges 국채 secondary-market CSV](https://data.norges-bank.no/api/data/GOVT_SECONDARY_MARKET/?startPeriod=2026-08-01&format=csv)는 실제 수신했다. repo와 outright 거래, 지역·상대방·총계/세부내역을 분리해야 한다. 중복 합산 금지. NOR 자료 하나로 27개국 시장품질을 완성할 수 없다.

[OECD Global Debt Report 2026](https://www.oecd.org/en/publications/global-debt-report-2026_e9d80efd-en/full-report/sovereign-borrowing-outlook_4470147b.html)의 유동성 조사는 참고할 공식 후보지만 이 조사에서 27개국 공통 주간 기계판독 계열을 확보하지 못했다.

신용등급은 발행기관·등급기관의 공개 페이지를 날짜 있는 수동 metadata로 관리할 가능성이 있다. 이번에는 27개국 전체, 동일 기관·동일 등급유형·동일 기준일 자료와 재배포 조건을 검증하지 않았다. OECD 소속이라는 이유로 동일 등급을 배정하지 않는다.

[OECD country risk classification](https://www.oecd.org/en/topics/country-risk-classification.html)은 수출신용용 분류이며 일부 고소득 OECD/유로권 국가를 분류 대상에서 제외한다. 이를 sovereign rating 또는 누락=위험0으로 쓰지 않는다.

IMF AREAER 온라인 데이터베이스의 [접근 안내](https://www.elibrary-areaer.imf.org/Login/NoAccess.aspx?AppType=1)는 subscription 접근을 요구한다. 공통 무인증 코어 자료로 확정하지 않는다. OECD FDI 제한지수를 채권 자본통제로 바꾸어 쓰지 않는다.

**판정:** 시장규모 원자료는 부분 확보, 종합 MarketQuality는 UNAVAILABLE. 승인된 10% 축을 값 1.0으로 채우거나 나머지 축으로 재가중하지 않는다. 공개 수동 자료를 추가하려면 출처·기준일·정의·갱신 책임까지 명시해야 한다.

## 5. 구현 전에 남은 항목

1. 나머지 5Y 경로 및 사용 가능한 원자료를 확정한다. 보류 범위 문서화만으로 초기 자료 확보 완료 조건을 대신하지 않는다.
2. 수익률 정의의 primary/fallback 호환 규칙을 검사한다. 정부가 만든 공식 추정곡선과 개발자가 결측 채우려고 만든 추정값을 구분하되, 공식 곡선이라는 이유만으로 원본 YTM과 동등하게 취급하지 않는다.
3. Refinitiv/NZFMA/LSEG 등 제3자 원천 자료의 커뮤니티 재배포 조건을 확인한다. no-auth와 open redistribution은 별개다.
4. IMF 판본 고정과 PDF 반올림·교차대조를 검증한다.
5. 시장품질 미확정 상태를 그대로 출력한다. 모든 국가가 계산 가능한 완성 랭킹이라고 홍보하지 않는다.

조사 결과는 원자료 수집 구현의 근거다. 승인된 수식·가중치·결측 원칙은 유지한다. 자료가 없는 국가의 숫자를 추정해서 채우는 방식으로 ‘27개국 완성’을 주장하지 않는다.


## 6. 추가 조사 및 구현 착수 조건 (2026-10-04 KST)

사용자 지시: **자료 확보를 완료한 다음 구현한다.** 자료 미확보 상태에서 제품을 먼저 만들고 빈 항목을 나중에 채우는 방식은 사용하지 않는다. 승인된 설계의 DATA_HOLD는 향후 운영 중 장애·결측에 대한 보호 장치이며, 초기 자료 확보 완료의 대체 조건이 아니다.

현재 착수 상태: **BLOCKED — DATA ACQUISITION INCOMPLETE**.

### 추가로 수신한 벨기에 5Y

공식 Explorer https://dataexplorer.nbb.be/ 의 공개 설정에서 API base https://nsidisseminate-stat.nbb.be/rest 를 확인했다. 무인증 catalogue, structure 및 실제 자료를 받았다.

- dataflow: BE2, DF_IROLOBE2, 1.0
- dimension order: FREQ, IROLOBE2_MATUR, IROLOBE2_TYPE
- 정확한 key: D.5Y.F
- 자료: https://nsidisseminate-stat.nbb.be/rest/data/BE2,DF_IROLOBE2,1.0/D.5Y.F?startPeriod=2026-09-25
- 구조: https://nsidisseminate-stat.nbb.be/rest/datastructure/BE2/DSD_IROLOBE2/1.0?references=all
- F: fixed residual term을 기준으로 한 OLO reference rate. T는 전체 대출·채권 평균, A는 OLO 평균이므로 동일 key로 취급하지 않는다.
- 2026-10-02 원값 3.89, OBS_STATUS=A, DECIMALS=2. 요청에서 관측행이 날짜순으로 오지 않았으므로 최대 날짜를 명시적으로 고른다.
- 실제 수신은 완료했지만 단위·세부 방법론 대조 및 반복 수집 검증은 남아 있다.
- [공식 재사용 안내](https://www.nbb.be/en/statistics/contact-and-more-information/nbbstat-data-explorer): 별도 표시가 없으면 비상업적 재사용 및 출처 표시가 가능하다는 안내. 배포 방식·개별 데이터 예외를 최종 확인한다.

### 잘못된 후보 배제·정정

- CNB REST 문서 3.4.1: api_key는 필수이며 계정에서 생성. 공개 웹 데이터와 REST 무인증은 다르다. REST를 무인증 수집 후보로 확정하지 않는다. 월별 5년 basket에 들어갈 수 있는 개별채권 잔존만기 범위는 **3.5–6.5년**이며 이전 초안의 3–7년 표현을 정정했다.
- 실제 https://api.statbank.dk/v1/tableinfo/DNRENTD?format=JSON&lang=en 응답의 INSTRUMENT 목록에는 중앙은행 정책금리·DESTR·preDESTR 10개 계열만 있었다. 이 표는 현재 조사한 응답 기준으로 5Y 국채 공급원이 아니다.
- ECB 공개 5년 Euro Area benchmark 및 AAA/all-issuer 곡선은 유로권 집계. 개별 국가 5Y 결측을 채우는 데 쓰지 않는다.
- BPstat 공식 quadro 484는 10/5/2년 **월평균**을 명시한다. 이후 조사에서 별도 일별 계열 12099457과 숫자를 확인했다(7절). 월평균 표를 일별로 바꾼 것이 아니다. 배포 환경의 직접 수집은 여전히 403으로 미확정이다.
- NZL 다운로드 403은 남아 있다. KOFIA는 후속 조사에서 최신 5Y와 날짜가 있는 기간 조회를 직접 수신했다(7절). 재사용 조건 등 전체 검증 완료를 뜻하지 않는다.

### 착수 전 필수 확인 목록

- [x] 27개국 각각의 재정·물가 필수 전망연도 값과 동일 판본 확보 — 8절의 실제 연도별 수신 및 순부채 PDF 대조. 사용 조건·공표 달력의 후속 검증은 별도 항목이다.
- [ ] 27개국 각각의 5Y 원자료 수신, 정확한 명목/실질·만기·수익률 유형·단위 확인
- [ ] 필요한 원화 FX 이력과 통화 전환·공통 날짜·창 길이 검증
- [ ] MarketQuality의 규모·유동성·신용·접근성 원자료 및 공통 정의 확보
- [ ] 각 자료의 최신성·누락·파싱 가능성, 반복 수집과 호출 제한 확인
- [ ] 커뮤니티 배포에 맞는 사용·출처 표시·재배포 조건 확인
- [ ] 실제 수신 표본으로 전체 입력표를 채워 빈 필수 항목이 없는지 확인

문헌 조사·다운로드·진단용 파싱은 허용된 자료 검증 작업이다. 수집기 제품화, 점수 엔진, UI, 배포 workflow는 위 조건 충족 전 시작하지 않는다. 어떤 항목이 현재 조건으로 확보 불가능하면 그 근거와 영향부터 사용자에게 알리고, 동의 없이 국가·필수 축을 삭제하거나 다른 만기·자료로 대체하지 않는다.


## 7. 후속 실제 조회: KOR·PRT·ITA 및 배포 조건 (2026-10-04 KST)

이 절의 표본도 수집 검증용이다. 최신성·정의·재사용 조건을 모두 통과한 계산 입력이라는 의미가 아니다. 기존 판정은 새로운 증거가 있는 항목만 갱신한다.

### KOR: 협회 공개 조회에서 날짜가 있는 5Y 직접 수신

[금융투자협회 채권정보센터](https://www.kofiabond.or.kr/) 공개 화면의 XML·JavaScript를 확인해, 로그인·API key·인증 cookie 없이 실제 읽기 전용 조회를 수행했다. KOFIA는 정부 통계기관이 아니라 공식 협회 공시 주체다.

- 공개 화면 XML: /xml/bondint/lastrop/BISLastAskPrcDay.xml. 기간 조회의 listTrm 및 시간값은 실제 내려받은 공개 기간 XML에서 확인했다.
- 실제 dispatcher: POST https://www.kofiabond.or.kr/proframeWeb/XMLSERVICES/
- Content-Type: application/x-www-form-urlencoded; charset=UTF-8 이지만 본문은 공개 frontend와 같은 raw XML이다.
- proframeHeader: pfmAppName=BIS-KOFIABOND, pfmSvcName=BISLastAskPrcROPSrchSO.
- getExistMaxDate: 응답 val1=20261002.
- listDay: BISComDspDatDTO/val1=20261002. 국고채권(5년), val20=3007, 잔존만기 4년6월–5년, 오전 val3=4.152, 오후 val4=4.129.
- listDay를 20261001로 다시 조회하면 같은 국고채 5년 오후 값은 4.200. 날짜 파라미터가 실제 관측 선택에 반영된다.
- listTrm: val1=DD, val2=20260928, val3=20261002, val4=1530, val5=3007.
- 기간 응답의 val1은 날짜, val2는 선택한 첫 번째 채권의 값. 2026-10-02=4.129, 10-01=4.200, 09-30=4.203, 09-29=4.276, 09-28=4.345. 일자별 조회와 겹치는 값이 일치했다.

주의사항:

- 기간 조회의 오후 선택값은 공개 XML에 있는 **1530**이다. 실제 화면의 변경 후 공시시각은 오후 16시 안내가 있으므로 API 선택 토큰을 관측시각 15:30으로 해석하지 않는다.
- PM 문자열을 시간값으로 보내면 HTTP 200이어도 자료행을 받지 못했다. frontend의 정확한 선택값을 사용한다.
- 기간 응답의 최고·최저 요약행을 날짜별 관측으로 파싱하지 않는다. 선택하지 않은 열의 0.000도 새로운 국채값이 아니다.
- listDay의 val11/val12는 연중 최고/최저 발생일이다. 이번 관측일로 쓰지 않는다. 메인 화면 일부 응답의 날짜 필드가 비어 있으므로 날짜 있는 기간 조회를 우선 검증 경로로 둔다.
- 국민주택1종(5년)은 국고채권(5년)과 다른 행이다. 이름에 5년이 있다는 이유로 섞지 않는다.
- 공개 화면의 조회 경로이지 문서화된 안정적 외부 개발자 API로 확정한 것은 아니다. 반복 수집의 안정성·호출 제한·사용 및 재배포 조건은 남아 있다. 이번 무인증 수신 성공으로 허가된 재배포를 주장하지 않는다.

### PRT: 정확한 일별 계열 확인, 배포 환경 직접 접근은 보류

[BPstat domain 26](https://bpstat.bportugal.pt/dominios/26/), [공식 방법론](https://bpstat.bportugal.pt/conteudos/metainformacao/472), [프로그램 접근 안내](https://bpstat.bportugal.pt/data/docs/).

연구용 대행 조회에서 공개 metadata와 JSON-stat 관측을 받았다. 이 대행 조회는 배포판 의존성으로 채택하지 않는다. 동일한 공식 주소에 대한 이번 실행 환경의 직접 HTTP 요청은 403이었다. 인증필수라는 결론도, 직접 무인증 수집 가능하다는 결론도 아직 내리지 않는다.

| 식별 항목 | 확인 값 |
|---|---|
| domain | 26 |
| series ID | 12099457 |
| dataset ID | 690b7b36fd36c0dbe249c48cbbc39524 |
| 내용 | 포르투갈 고정금리 국채, 잔존만기 5년 수익률 |
| 주기 / 단위 | Daily / Percent |
| 공급 원천 | LSEG |
| metadata 갱신일 | 2026-10-02T16:00Z |
| 마지막 관측일 / 값 | 2026-10-01 / 3.60% |

metadata:
https://bpstat.bportugal.pt/data/v1/series/?series_ids=12099457&lang=EN

실제로 JSON-stat를 받은 연구 조회:
https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?lang=EN&series_ids=12099457&last_n=5

응답은 마지막 5개만이 아니라 전체 7,966개 관측이었다. 마지막 5영업일은 09-25=3.62, 09-28=3.66, 09-29=3.63, 09-30=3.58, 10-01=3.60. last_n 및 시험한 날짜 필터가 반영되었다고 가정하지 않는다. 공식 문서에서 지원하는 필터명을 추가 검증해야 한다. reference_date와 value를 응답의 정확한 index 순서로 결합한다.

공식 설명은 일별 관측을 주 단위로 갱신하는 구조다. 갱신일 10월2일을 관측일로 바꾸지 않는다. 월별 5년 계열 **12099462**는 다른 계열이며 daily 12099457과 교체하지 않는다. 공개 월보 그래프의 픽셀을 읽어 만든 값이 아니다. LSEG 원천의 사용·재배포 조건 및 배포 환경 직접 접근을 해결하기 전에는 확보 완료로 취급하지 않는다.

### ITA: 공식 무인증 ZIP 실제 수신, 최신성·재배포는 보류

[중앙은행 BDS 안내](https://www.bancaditalia.it/statistiche/basi-dati/bds/index.html), [공식 export 매뉴얼](https://infostat.bancaditalia.it/inquiry/GetDocumentFile?type=export_help), [May 2026 Financial Market 방법론](https://www.bancaditalia.it/pubblicazioni/metodi-e-fonti-note/metodi-note-2026/MFN_note-met_en_20260515.pdf?language_id=1).

- 일별 표: BMK0200.
- 정확한 계열: **MFN_BMK.D.020.922.0.EUR.205**.
- metadata: Daily, BTPs, Gross yield, EUR, 5 years; 설명은 Gross yield of benchmark 5-year BTP.
- ALL ZIP에서 DATA, DOMAIN, STRUCTURE, LEGEND CSV 네 파일을 실제 수신했다. CSV는 세미콜론 구분.
- ALL export:
  https://a2a.bancaditalia.it/infostat/dataservices/export/EN/CSV/ALL/CUBE/BANKITALIA/DIFF/BMK0200
- DATA export:
  https://a2a.bancaditalia.it/infostat/dataservices/export/EN/CSV/DATA/CUBE/BANKITALIA/DIFF/BMK0200
- 두 주소 모두 로그인·API key 없이 HTTP 200. 두 export의 실제 DATA CSV 내용이 동일함을 확인했다. DATA ZIP의 내부 이름은 생성시각을 포함하므로 고정 이름을 전제하지 않는다.
- 5Y 유효 관측 9,587개, 최초 1988-11-10, **마지막 2026-08-31, 원값 3.50655**. 이번 최신성 검증에서는 최근 9월말/10월초 관측이 없으므로 현재 주간 입력으로 보류한다.
- DATA에 달력 날짜별 빈 행이 포함된다. 마지막 배열 위치나 마지막 달력 날짜를 유효 관측으로 간주하지 않는다.
- metadata SCALA=-2는 소수점 정밀도 안내다. 임의로 값을 100배/100분의1로 바꾸지 않는다. UNMIS=NP라는 일반 단위 표기가 있으므로 공개 수익률 표의 percent 표기·월평균과 최종 단위 대조도 필요하다.

공식 방법론은 MTS 거래 기반이며 가장 활발히 거래되는 신규 발행물을 benchmark로 선택한다고 설명한다. metadata의 DURORI는 Original maturity다. 따라서 정확한 잔존만기 5년 보간곡선이라고 표시하지 않는다. 이것은 Rendistato의 전체 또는 만기구간 평균을 5년물로 대체한 것이 아니다. 비교 가능한 수익률 정의와 publication lag는 별도로 확인한다.

[공식 copyright](https://www.bancaditalia.it/footer/copyright)는 일반 사이트 자료의 복제·외부 정보시스템 게시를 제한하고, AgID open data에는 별도 CC BY 4.0 예외를 둔다. [공식 RDF catalogue](https://www.bancaditalia.it/footer/open-data/Open_Data_BdI.rdf)는 실제 수신했고 80개 Dataset을 확인했지만 이번 파일에서 BMK0200/BMK 또는 benchmark yield 항목과의 대응은 확인하지 못했다. 전체 BDS가 자동으로 CC BY 대상이라고 단정하지 않는다. **개별 BMK0200의 재사용 허용 근거는 미확정**이다.

### 사용 조건과 잘못된 대체 후보의 후속 판정

- [Riksbank 일반 open-data 조건](https://www.riksbank.se/en-gb/about-the-riksbank/about-the-website/open-data--information-available-for-re-use/): 별도 합의 없이 재사용 가능하다는 안내와 원자료의 기관·날짜 표시 조건을 확인했다. 가공한 통계를 Riksbank 출처로 표시하지 말라는 조건 및 공식 협업·제휴로 표현하지 말라는 조건도 있다. 원자료 provenance와 자체 계산 결과의 저자를 구분해야 한다. 이것은 SWESTR만의 조건을 5년물에 적용한 결론이 아니다. Refinitiv 원천 계열의 개별 예외 여부와 적용 범위는 추가 확인한다.
- [덴마크 공식 secondary-market 안내](https://www.nationalbanken.dk/en/government-debt/trading-and-data/secondary-market-data)는 MTS의 15분 지연 개별 국채 호가로 연결한다. 링크 https://www.mtsdata.com/content/data/public/dkk/best/ 및 https://www.mtsdata.com/content/data/public/dkk/fixing/fixing_dkk.html 는 직접 403이었다. 개별 종목 호가를 고정5Y 계열로 확보했다고 세지 않는다.
- [OECD Global Debt Report 2026](https://www.oecd.org/en/publications/global-debt-report-2026_e9d80efd-en/full-report/sovereign-borrowing-outlook_4470147b.html)의 유동성 부분을 추가 확인했다. 2025년 37개국 조사와 개선/악화 응답 집계는 27개국 각각의 유동성 수준·공통 점수 자료가 아니다. 10년물 변동성의 국가간 분위수도 bid-ask 또는 거래량을 대신하지 않는다. MarketQuality 확보 판정은 그대로 UNAVAILABLE다.

### 이번 회차 종료 상태

- 한국 5Y: 무인증 직접 수신 및 날짜·교차 조회 확인. 출처 유형·잔존만기 basket·재사용 조건은 별도 기록.
- 포르투갈 5Y: 정확한 계열·관측을 연구용 조회로 확인. 직접 수집은 403으로 보류.
- 이탈리아 5Y: 공식 일별 ZIP 두 방식으로 직접 수신. 최신 관측 부족 및 개별 사용 조건으로 보류.
- 원자료·경로 미확정 9개국과 ISR 월주기, ITA 최신성, PRT 직접 접근, 시장품질 및 각 자료의 사용 조건은 남아 있다.
- **BLOCKED — DATA ACQUISITION INCOMPLETE** 유지. 제품 구현은 시작하지 않았다.


## 8. 필수 연도·환율 이력 검증 및 남은 국가 후속 조사 (2026-10-04 KST)

### 재정·물가: 국가 키 확인에서 실제 27×6 입력 확인으로 진전

네 DataMapper 지표를 인증 없이 다시 내려받아 27개 ISO3 각각의 2026~2031년 값이 숫자이며 유한한지 검사했다. 승인된 설계의 ND_current 기준연도는 실행일의 서울 달력연도이므로 이번 검증은 2026년을 포함한다.

| 지표 | API 유효값 / 필수값 | 결측 | 공식 보완 후 상태 |
|---|---:|---|---|
| 순부채 GGXWDN_G01_GDP_PT | 156 / 162 | SVK의 2026~2031년 6개 | 같은 April 2026 PDF A8의 6개 값으로 162개 확보 |
| 전체 재정수지 GGXCNL_G01_GDP_PT | 162 / 162 | 없음 | 필수 전망연도 모두 수신 |
| 총부채 G_XWDG_G01_GDP_PT | 162 / 162 | 없음 | 필수 전망연도 모두 수신; 순부채 대체에 사용하지 않음 |
| 연평균 물가 PCPIPCH | 162 / 162 | 없음 | 필수 전망연도 모두 수신 |

순부채 PDF A8에서 API와 겹치는 **26개국 × 6년 = 156개 값**을 대조했다. PDF가 표시하는 0.1%p 정밀도로 반올림한 API 값과 **156개 전부 일치**, 차이 0개. SVK 보완은 이와 동일한 표의 58.0, 60.5, 62.8, 65.3, 68.2, 71.5다. PDF만의 반올림 정밀도를 유지하며 API 수준의 더 정밀한 숫자를 생성하지 않는다.

별도 indicators metadata 응답에서 재정 세 지표는 Fiscal Monitor (April 2026), 물가는 WEO (April 2026), projection-year=2026임을 다시 확인했다. 재정 단위는 % of GDP, 물가는 Annual percent change. indicators의 last-modified는 재정 2026-04-15, 물가 2026-04-08로 표시되어 있으며 조회시각·판본 공개일과 혼동하지 않는다.

이번 실제 응답의 SHA-256:

| 원자료 | SHA-256 |
|---|---|
| 순부채 JSON | 336d4184e7a73a26c8cff7767e14f3ba0223b7a241eaf76a0e1778eb7fbe9586 |
| 전체 재정수지 JSON | f5af1ba8b855973eddb50a1e174e8f2560134bffc19779ab8ae08cca88b22835 |
| 총부채 JSON | 78c4e05c7e313e551c134209be2b984d8db183c02544bea9751f8fbda418247d |
| 물가 JSON | 0c327da1a2f429c24bcaa79586509bb6358a43bf642067c925777318cc5cbc97 |
| 순부채 공식 부록 PDF | e928d3df31fc5f7848392d8bff61095a019985c50be0d9fd12c8f15fed1ad5e3 |

자료 확보 항목의 연도별 존재·판본 일치 확인은 완료했다. 향후 판본 변경·릴리스 달력 확인·사용 조건 및 운영 시 재조회 검증을 생략한다는 뜻은 아니다. 이번 작업에서 점수를 계산하거나 제품 수집기를 작성하지 않았다.

### FX: 필요한 주요 통화의 1년·3년 창 실제 점검

ECB 역사 XML을 다시 직접 수신했다. 이번 파일도 총 7,106개 날짜, 마지막 2026-10-02. 파일 SHA-256:
807ad53568c849e894f9ea496c91684f530f23f60afc564d96f46702be494ceb

- 검증 창: 2023-10-04~2026-10-02. 서울 기준 조사일 2026-10-04에서 3년 전 날짜를 시작으로, 제공자의 마지막 관측일까지 검사했다.
- 전체 제공 날짜: 765개. 중복 날짜 없음.
- ISK, NOK, AUD, NZD, KRW, CZK, CAD, DKK, SEK, ILS, GBP, USD, JPY 각각 KRW와 같은 날짜로 **765개 전부 연결**.
- 해당 통화 값은 모두 양수·유한하며 위 창 안에서 통화별 누락 날짜 없음.
- 연속 제공 날짜의 최대 간격은 5 **달력일**. 제공자 영업일 5일 기준과 같은 개념으로 표시하지 않는다.
- 1년 검증 창 2025-10-04~2026-10-02는 254개 날짜. 승인된 최소 200/600개 관측수 조건을 위 주요 통화가 충족한다.
- EUR는 기준통화 분모 1, KRW/KRW는 모든 날짜에서 정확히 1. 실제 통화 선택 및 개별 국가의 5Y 관측일과의 결합은 별도 검증한다.

BGR 전환은 근거와 원자료 형태까지 확인했다.

- [ECB의 2026-01-01 도입 공지](https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260101~c830245e42.en.html): 2026-01-01 EUR 도입, 1 EUR=1.95583 BGN.
- [ECB reference-rate 제거 안내](https://www.ecb.europa.eu/services/using-our-site/technical-updates/html/ecb.technical_update251211.en.html): 전환 이후 BGN 기준환율 계열을 제거한다고 명시.
- 실제 3년 창에서 BGN+KRW 짝은 572개, 마지막 2025-12-31. 2026-01-02부터 EUR 기간의 제공 날짜가 193개.
- 과거 XML의 BGN 기준환율은 1.9558로 표시된다. 공인 전환비율 1.95583과 표시 정밀도가 다르다. 정확한 전환비율로 EUR 단위에 환산하면 약 0.001534%의 표시 정밀도 차이가 생긴다. 이를 시장의 FX 충격이라고 해석하거나 설명 없이 이어 붙이지 않는다.
- effective-dated 통화 선택·고정 환산·정밀도 차이 처리·5Y 채권 통화와의 결합은 여전히 명시적 검증 대상이다. 이번 통화별 이력 점검만으로 27개국 FX 전체 완료 체크를 하지 않는다.

### HRV: 공개 데이터 catalogue에서 공식 월별 엑셀 수신

공식 Croatian open-data catalogue의 공개 CKAN 응답:
https://data.gov.hr/ckan/api/3/action/package_show?id=711cb511-fbfc-49c3-a6c3-7ae40cca5bdf

이 응답에 들어 있는 G8b resource e8900684-dbb8-4193-9686-e4627925bf5a의 실제 HNB 파일:
https://www.hnb.hr/documents/20182/1f79bc1c-dfb5-17fd-1571-cdd52a4a9619

- 직접 무인증 HTTP 200, XLSX, 83,373 bytes, HRV 시트.
- resource 설명은 **월·연평균**의 채권 만기수익률이라고 명시한다. 일별 자료가 아니다.
- 5 g. 열이 세 개다: 해외 발행 USD, 해외 발행 EUR, 국내 발행 EUR. 같은 국가라는 이유로 통화·발행시장을 섞지 않는다.
- 마지막 월 2026년 8월. 국내 EUR 5년 열 원값 3.02, 해외 EUR 5년 열 원값 3.21, 해외 USD 5년 열은 '-'.
- 국내 EUR 5년 열은 2026년 1~6월 결측, 7월 3.04, 8월 3.02. 없는 월을 해외 EUR 값으로 조용히 보완하지 않는다.
- 5 g.가 의미하는 만기 구분과 단위·계산방법을 최종 대조해야 한다. 최신 일별 5Y 입력으로 승인하지 않는다.
- catalogue의 license_id는 open-license였지만 실제 라이선스 문구와 HNB 원천의 적용 범위 대조는 남아 있다. 이 식별자만 보고 아무 조건 없는 재배포로 판단하지 않는다.

### AUT·CZE 및 공통 후보의 좁혀진 조사 결과

- [OeKB 공식 benchmark 목록](https://www.oekb.at/kapitalmarkt-services/unser-datenangebot/daten-zu-bundesanleihen-der-republik-oesterreich/benchmarks.html)을 직접 수신했다. 2026-07-31부터 5년 benchmark는 **AT0000A2NW83, 쿠폰 0.00%, 2021-2031/1**. 이 표는 ISIN·쿠폰·발행물 정보를 제공하며 현재 시장수익률은 없다. 쿠폰 0%를 국채 수익률 0%로 넣지 않는다. 기준종목 식별은 진전됐지만 수익률 확보는 아니다.
- CZE 공식 ARAD REST 문서는 등록 계정의 API key를 요구하고 자동 수집의 지원 경로가 REST라고 설명한다. API key 필수 경로를 무인증 경로라고 바꾸어 기록하지 않는다. 공개 화면의 수동 다운로드 가능성과 일별 5Y 존재는 따로 확인할 항목이다.
- [Czech MoF 2026 Q1 보고서](https://mf.gov.cz/assets/attachments/2026-04-17_Debt-Portfolio-Management-Quarterly-Report-2026-Q1.pdf)는 공식 Svensson par yield curve와 bid-offer/거래량 그림을 제공하는 후보지만, 이번에 정확한 최신 일별 5Y 수치 다운로드를 확보하지 못했다. 그래프 판독으로 채우지 않는다.
- ECB FM 구조 조회는 직접 요청과 연구용 조회 모두 timeout. 무인증 자료가 없다는 판정이 아니라 이 회차 미수신으로 기록한다. 확인한 euro-area 5년 집계나 국가별 10년 convergence를 결측에 적용하지 않는다.
- [AREAER 2023 eLibrary 서지](https://www.elibrary.imf.org/display/book/9798400260391/9798400260391.xml)에서 전체 PDF 안내와 [공개 Overview](https://www.elibrary.imf.org/fileasset/downloads/AEIEA2023001-S001.pdf) 후보를 확인했으나 직접 서지 요청은 403이었다. 서지상 4,938페이지라는 표시만으로 27개국 자본통제 본문을 수신했다고 선언하지 않는다. 온라인 DB의 subscription 요구, Overview와 전체 국가 보고서, 판본·기준일은 구분한다.

**착수 상태 유지: BLOCKED — DATA ACQUISITION INCOMPLETE.** 이번에 재정·물가 필수 연도 검증과 주요 통화 이력 점검은 진전됐지만, 일별 5Y 경로 미확정 9개국 및 기존 주기·최신성·직접 접근·정의 문제, MarketQuality와 사용 조건은 남아 있다.
