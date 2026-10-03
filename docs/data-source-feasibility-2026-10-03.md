# 공식·무인증 데이터 경로 조사

조사일: 2026-10-03 UTC. 승인된 설계: [2026-10-04 sovereign macro design](superpowers/specs/2026-10-04-sovereign-macro-design.md).

이 문서는 설계를 변경하지 않는 자료조사 결과다. 제품 코드·워크플로는 작성하지 않았다. 공개 HTTP 요청에 사용자 인증·API key를 넣지 않고 내려받은 자료와, 문서만 확인한 후보를 구분한다. 현재 수신 가능하다는 사실은 재배포 권한·향후 가용성·동일한 수익률 정의를 보장하지 않는다.

## 결론

- 재정·물가: IMF DataMapper v2가 공통 경로다. 순부채 API의 SVK 결측은 같은 April 2026 Fiscal Monitor 공식 부록 A8 표로 보완할 수 있다. 총부채로 대체할 필요가 없다.
- 5년물: 14개국에서 일별 5년물 자료 다운로드와 숫자·관측일을 확인했다. 단, SVK는 공식 추정 제로쿠폰 곡선이고 DEU/NLD/FRA/GBR는 Riksbank가 제공하는 Refinitiv 계열이다. 그대로 같은 정의의 Baseline 입력으로 승인된 것은 아니다.
- ISR: 월평균 명목 5년 제로쿠폰 자료까지 확인했다. 일별 기준의 최신성 요건에는 별도 보류가 필요하다.
- NZL: 공식 일별 자료와 다운로드 주소는 찾았지만 직접 다운로드는 403이었다.
- 11개국은 이 조사에서 사용할 수 있는 일별 무인증 수집 경로를 아직 확정하지 못했다. 이는 공식 자료가 존재하지 않는다는 결론이 아니다.
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
- **미확정**: 이 조사에서 사용할 정확한 5년물 경로를 확정하지 못함.

| ISO3 | 국가 | 상태 | 공급자 / 정확한 식별자 | 확인 관측일·값 (%) / 남은 사항 |
|---|---|---|---|---|
| ISL | 아이슬란드 | 수신 | CBI FLV Excel, nominal par 5Y | 2026-10-01, 7.51; Excel 원값 0.0751은 백분율 포맷 |
| NOR | 노르웨이 | 수신 | Norges GOVT_GENERIC_RATES, TENOR=5Y, GBON | 2026-10-01, 4.71; 가장 가까운 만기 기준채권 정의 |
| AUS | 호주 | 수신 | RBA F2, FCMYGBAG5D | 2026-09-30, 4.983; 보간 고정만기 |
| NZL | 뉴질랜드 | 후보 | RBNZ B2 daily close workbook | 공식 화면 5Y 존재; 직접 파일 요청 403 |
| KOR | 한국 | 미확정 | BOK ECOS / KOFIA 채권정보 후보 | ECOS key 요구; KOFIA의 무인증 자동수집 경로 미확정 |
| CZE | 체코 | 후보 | CNB ARAD bond-yield metadata / REST | 월별 5년 basket은 잔존 3.5–6.5년; 일별 정확한 경로 미확정 |
| BGR | 불가리아 | 미확정 | BNB / 재무부 국채 자료 | 원래 5년 발행물의 재입찰 금리는 현재 고정 5년물이 아님 |
| CAN | 캐나다 | 수신 | BoC Valet BD.CDN.5YR.DQ.YLD | 2026-10-01, 3.62; benchmark bond |
| IRL | 아일랜드 | 미확정 | NTMA 발행·입찰 자료 | 개별 발행물 결과를 일별 5Y로 대체하지 않음 |
| DNK | 덴마크 | 후보 | Nationalbank DNRENTD | 정확한 일별 5Y 계열 미확정; 10Y 대체 금지 |
| LTU | 리투아니아 | 미확정 | 재무부 시장 리뷰·입찰 | 리뷰 중단 / 개별 입찰; 고정만기 5Y 미확정 |
| SWE | 스웨덴 | 수신 | Riksbank SEGVB5YC | 2026-10-02, 2.948; 원천 Refinitiv |
| HRV | 크로아티아 | 미확정 | HNB / 재무부 후보 | 일별 5Y 미확정; 민간 ‘5-year’ 종목명만으로 식별 금지 |
| NLD | 네덜란드 | 수신 | Riksbank NLGVB5Y | 2026-10-02, 3.3104; 원천 Refinitiv |
| SVN | 슬로베니아 | 미확정 | 중앙은행 / 재무부 후보 | 확인된 10Y convergence를 5Y로 대체하지 않음 |
| DEU | 독일 | 수신 | Riksbank DEGVB5Y | 2026-10-02, 3.1969; 원천 Refinitiv |
| SVK | 슬로바키아 | 조건부·일별 수신 | NBS Yields_SK, ZCY5Y | 2026-09-25, 3.86; NSS 추정 제로쿠폰, 주 1회 배포 |
| AUT | 오스트리아 | 미확정 | OeNB / debt office 후보 | UDRB는 잔존 1년 초과 채권 가중평균이며 5Y 아님 |
| PRT | 포르투갈 | 후보 | IGCP 월보 / Banco de Portugal BPstat | 그래프는 있음; 정확한 기계판독 일별 5Y 미확정 |
| ISR | 이스라엘 | 조건부·월별 수신 | BOI ZCM, ZC_TSB_ZND_05Y_MA | 2026-09, 3.716070154; nominal zero-coupon 월평균 |
| ESP | 스페인 | 수신 | Banco de España TI_1_3, D_G0B1F0ZO | 2026-09-30, 3.645; secondary market 5 años |
| GBR | 영국 | 수신 | Riksbank GBGVB5Y | 2026-10-02, 4.932; 원천 Refinitiv; BoE curve는 정의 별도 |
| FRA | 프랑스 | 수신 | Riksbank FRGVB5Y | 2026-10-02, 4.2843; 원천 Refinitiv |
| ITA | 이탈리아 | 미확정 | Banca d’Italia / MEF 후보 | Rendistato 전체·만기구간 평균은 정확한 5Y 아님 |
| BEL | 벨기에 | 수신·검증 진행 | NBB DF_IROLOBE2, D.5Y.F | 2026-10-02, 원값 3.89; 고정 잔존만기 OLO; 단위·방법론 최종 확인 필요 |
| USA | 미국 | 수신 | US Treasury daily curve BC_5YEAR | 2026-10-02, 5.06; par constant maturity |
| JPN | 일본 | 수신 | MoF JGB constant maturity, 5年 | 2026-10-01, 2.407; 명목 국채 곡선 |

14개국 일별 수신 = ISL NOR AUS CAN SWE NLD DEU SVK ESP GBR FRA BEL USA JPN.
월별 ISR까지 15개국에서 실제 숫자를 받았다. 나머지 12개국 중 NZL은 공식 화면·다운로드 주소까지 확인, 11개국은 경로 또는 지표를 미확정 상태로 남긴다. 수신 수는 전체 입력 검증 완료 수가 아니다.

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
- BEL: [NBB 금융시장 통계](https://www.nbb.be/en/statistics/financial-markets/publications-and-figures), [Data Explorer 안내](https://www.nbb.be/en/statistics/contact-and-more-information/nbbstat-data-explorer). 실제 공개 계열 코드·주기를 찾기 전에는 확보 처리하지 않는다.
- KOR: ECOS key를 배포판에 내장하지 않는다. KOFIA 최종호가수익률의 공개 다운로드·재사용 조건을 우선 확인한다. 협회 통계는 정부기관 통계와 출처 유형을 구분한다.
- DNK/PRT/IRL/LTU/HRV/SVN/BGR/AUT/ITA: 공식 중앙은행·부채관리기관의 일별 5Y 파일 또는 공개 통계 계열을 추가 확인한다. 입찰금리, 10년 convergence yield, 정책금리, 원래 5년 만기로 발행된 오래된 종목, 만기구간 평균, 그래프 픽셀 판독은 대체 입력으로 승인하지 않는다.

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

1. 나머지 5Y 경로를 확정하거나 데이터 보류 범위를 문서화한다.
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
- BPstat 공식 quadro 484는 10/5/2년 **월평균**을 명시한다. 정확한 5년 계열 ID와 일별 가능 여부는 미확정이다. 공식 페이지 존재를 자동수집 확보로 계산하지 않는다.
- NZL 다운로드 403 및 KOFIA 공개 XML 접근은 확인했으나 최신 5Y 수집 경로가 검증 완료된 것은 아니다.

### 착수 전 필수 확인 목록

- [ ] 27개국 각각의 재정·물가 필수 전망연도 값과 동일 판본 확보
- [ ] 27개국 각각의 5Y 원자료 수신, 정확한 명목/실질·만기·수익률 유형·단위 확인
- [ ] 필요한 원화 FX 이력과 통화 전환·공통 날짜·창 길이 검증
- [ ] MarketQuality의 규모·유동성·신용·접근성 원자료 및 공통 정의 확보
- [ ] 각 자료의 최신성·누락·파싱 가능성, 반복 수집과 호출 제한 확인
- [ ] 커뮤니티 배포에 맞는 사용·출처 표시·재배포 조건 확인
- [ ] 실제 수신 표본으로 전체 입력표를 채워 빈 필수 항목이 없는지 확인

문헌 조사·다운로드·진단용 파싱은 허용된 자료 검증 작업이다. 수집기 제품화, 점수 엔진, UI, 배포 workflow는 위 조건 충족 전 시작하지 않는다. 어떤 항목이 현재 조건으로 확보 불가능하면 그 근거와 영향부터 사용자에게 알리고, 동의 없이 국가·필수 축을 삭제하거나 다른 만기·자료로 대체하지 않는다.
