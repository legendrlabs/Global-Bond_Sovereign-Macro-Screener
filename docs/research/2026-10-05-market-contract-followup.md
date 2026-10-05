# 미연결 자료 후속: 거래소 계약·관측일·역경매 원본

조사일: 2026-10-05 KST. 이전 [확대 탐색](2026-10-05-wide-market-routes.md)의 SVN MTS / LTU Nasdaq 후보를 좁혀 확인하고, 권리 검토가 된 PRT 및 HRV의 정의 근거도 재탐색했다.

Exa 검색 12회, 요청 슬롯 60개, 반환 URL 60개, 중복 제거 54개. 검색 건수는 원본 다운로드나 새 연결 수를 뜻하지 않는다. web open/click/find로 실제 페이지의 공식 링크를 따라가고 원문 스키마·계약을 확인했다. source 접근 오류와 도구의 형식 지원 오류를 구분했다.

이번 변경은 연구 문서만 추가한다. **신규 연결 0개 / 연결 18개국 / 미연결 9개국**. 점수식, 국가별 정의, freshness·tenor·unit·definition, cache-fallback 금지, public-output 및 Adjusted 게이트는 변경하지 않았다.

## 새 원본 후보: LTU 중앙은행 역경매 XLS

[Bank of Lithuania asset purchase programmes](https://www.lb.lt/en/asset-purchase-programmes)의 Reverse auctions of monetary policy portfolios 절이 실제 결과 파일을 연결한다. 페이지는 최소 월 1회의 경매와 공개 결과 링크를 안내하고 파일 크기를 538.5 KB로 표시한다. 이것은 페이지 표시값이며 직접 받은 파일 크기가 아니다.

원본 링크:
https://www.lb.lt/uploads/documents/files/musu-veikla/pinigu-politika/Turto_pirkimo_programos/MPP_aukcionu_rezultatai.xls

- 공식 페이지의 Results 링크를 따라가 XLS URL을 확인했다. URL을 추측해서 만든 것이 아니다.
- web fetch는 application/vnd.ms-excel 지원 문제로 읽지 못했다. Exa도 CRAWL_UNEXPECTED_CONTENT_TYPE을 반환했다.
- 일반 GET 1회, connect/read timeout 5/15초: **ReadTimeout**. 원본 bytes·SHA·sheet·열·실제 최신 관측일은 미확보다.
- 따라서 “538.5 KB 다운로드 완료”나 “2026년 새 수익률 확보”로 기록하지 않는다.
- 링크 존재는 공개 자료 경로의 진전이다. 역경매의 개별 yield를 국가 daily secondary-market 5Y로 대체하지 않는다. 날짜·ISIN·만기·unit·유효 행·권리 확인이 후속 과제다.
- 공식 안내가 별도로 연결하는 auction set-up 문서는 DOCX로, 이번 검색 도구에서는 읽지 못했다. 이를 소스 오류나 자료 부재로 해석하지 않는다.

[중앙은행 원문 연구](https://www.lb.lt/uploads/publications/docs/55832_371c002e2c970249464badf7dad66c40.pdf)의 data sources 절도 확인했다. 연구의 곡선은 Bloomberg 호가, 국내 상업은행의 bid/ask/mid 호가, 발행·통화정책 경매 자료를 결합한 NSS 추정이다. 공개 경매 원본을 찾았다는 사실이 비공개 은행 호가나 논문의 synthetic 10년 benchmark 재현에 필요한 모든 입력을 확보했다는 뜻은 아니다. 5년 수익률을 논문 그래프에서 읽거나 직접 NSS로 추정하지 않는다.

## LTU Nasdaq: 새 페이지 시각과 실제 관측값을 분리

- [2032 만기 개별 국채 trading](https://nasdaqbaltic.com/statistics/en/instrument/LT0000612012/trading)
- [공식 화면이 연결한 historical](https://nasdaqbaltic.com/statistics/en/instrument/LT0000612012/historical?date=2026-10-02)
- [정부채 목록](https://nasdaqbaltic.com/statistics/en/bonds)

LTGB03032A / LT0000612012를 확인했다. trading 페이지의 Last update 및 Information as of는 2026-10-05로 표시되지만 bid/ask, market depth, latest trades는 비어 있다. 페이지 수정 시각을 실제 yield 관측일로 사용하면 안 된다.

historical 링크는 date=2026-10-02를 포함하지만, 추출된 표는 2022~2026년 열을 표시하며 Open/High/Low/Last yield와 가격·거래량 항목이 모두 '-'였다. 이 화면에서 유효한 daily yield history를 확보하지 못했다. 해당 instrument 전체 역사나 Nasdaq 전체에 관측이 없다고 확대하지 않는다.

목록과 historical 화면에는 XLSX 다운로드 링크가 있지만, 목록의 XLSX를 읽는 도구는 Internal Error를 반환했다. 원본 다운로드·schema 검증 성공으로 집계하지 않는다. 권리 검토 후에 체계적인 다운로드를 반복하는 수집기를 만들지 않았다.

### Nasdaq 권리 조건을 구체화

- [현행 site disclaimer](https://nasdaqbaltic.com/disclaimer/)
- [Market Data Service](https://nasdaqbaltic.com/market-information/market-data-service/)
- [2019 Baltic Market Data Price List v1.1](https://www.nasdaq.com/docs/Baltic%20GIS%20Pricelist%201_1.pdf)

disclaimer는 사전 서면 동의, 법상 fair-use 예외, 개인 비상업적 사용을 위한 제한된 복사본을 구분한다. 개인이 읽는 허용을 공동체에 수치·DB·보고서를 재배포하는 허가로 해석하지 않는다. 별도 배포판 이용 허가는 확인하지 못했다.

공식 market-data 페이지는 quotes/trades/depth 제품과 pricing을 연결한다. 확보한 PDF는 **2019-07-24 유효 문서**이며 external/internal, delayed redistribution, end-of-day 내부 이용 등의 계약 구분을 설명한다. 2019 요금을 현재 가격이라고 쓰거나 “지연 데이터는 무료”라고 해석하지 않는다. 현행 정확한 상품·권리 범위가 필요하다.

## SVN: 채권 식별에는 진전, YTM 원본은 미확보

[Ljubljana Stock Exchange RS86 화면](https://ljse.si/en/papir-311/310?isin=SI0002104105)을 확인했다.

- ISIN SI0002104105, symbol RS86, FISN `RS/0.000 BD 20310212 GOVT GTD`, EUR 표시를 확인했다.
- 영어 날짜 문자열과 FISN 날짜 형식을 구분해서 기록한다. 화면의 날짜 형식을 한국식으로 추정해 파싱하지 않는다.
- 가격·거래량·instrument metadata는 있으나 추출 본문에서 직접적인 Yield 항목은 찾지 못했다.
- 0% Interest Rate는 coupon 필드이며 YTM으로 사용하지 않는다.
- 추출에는 Angular template 변수와 여러 trading-status 안내문이 함께 포함돼 있다. 단순히 “delisted”, “suspended”, “No transactions” 문구가 보인다는 이유로 실제 현재 상태를 판정하지 않는다.
- 이 ISIN 식별을 국가의 현행 5년 benchmark 선정 승인으로 처리하지 않는다.

[정부 debt-management 안내](https://www.gov.si/en/topics/borrowing-and-state-budget-debt-management/)도 확인했으나, 해당 화면에서 exact 5Y daily yield 다운로드를 확보하지 못했다. 국가 전체의 데이터 부재 판정은 아니다.

## MTS: 홈페이지 계약과 public fixing host의 범위를 구분

- [Market Data Documentation](https://www.mtsmarkets.com/en/data-analytics/market-data-documentation)
- [Legal](https://www.mtsmarkets.com/en/legal)
- [Legal 페이지가 연결한 August 2024 Website Terms PDF](https://static-prod.mtsmarkets.com/public/2024-08/Website%20Terms%20and%20Conditions%2008%202024_(v290824).pdf)
- [Slovenia fixing 후보](https://www.mtsdata.com/content/data/public/rsl/fixing/)

PDF의 본문 4쪽은 개인 비상업적 제한 복사와 그 밖의 재현·배포·체계적 수집을 구분한다. 별도 서면 허용 없이 공동체 배포용 자동수집 권한이 생긴다고 볼 근거가 없다.

중요한 범위: 문서가 정의하는 Website는 `www.mtsmarkets.com`이고 후보 fixing은 `www.mtsdata.com`이다. 이 PDF가 해당 fixing host의 모든 이용 조건을 자동으로 확정한다고 단정하지 않는다. market-data 계약 목록에는 delayed/reference/snapshot/derived data도 있으나 public fixing의 정확한 허용 조건은 계속 미확정이다. 따라서 기존 redistribution HOLD를 유지하며 host 차이를 허가 우회 근거로 사용하지 않는다.

## PRT / HRV 재탐색

**PRT**
- [수익률 표 484](https://bpstat.bportugal.pt/conteudos/quadros/484)
- [secondary-market metadata 472](https://bpstat.bportugal.pt/conteudos/metainformacao/472)

두 페이지의 검색 추출은 제목만 제공해 maturity selection/interpolation 규칙을 추가 확인하지 못했다. 페이지가 비었다거나 metadata가 없다고 판단하지 않는다.

승인된 BPstat direct 5년 series를 올바른 최근 관측 필터로 1회 요청:
https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?lang=EN&series_ids=12099457&obs_last_n=5

결과 **ReadTimeout**. 이전 HTTP 200 원본을 이번 최신 성공으로 쓰지 않는다. 실패가 과거 연구의 시리즈 존재·공개 근거를 무효화하는 것도 아니다. 검색의 São Tomé e Príncipe 계산 문서는 국가 불일치로 제외했다.

**HRV**
HNB 질의응답·통계 metadata·현지어 단위 검색을 추가 수행했다. 이번 결과에서도 G8b 5년 열의 직접 % 근거와 영문 360 / 현지어 365일 설명의 해소 자료를 확보하지 못했다. 재무부의 발행 coupon·만기 자료를 G8b unit 증거로 옮겨 쓰지 않는다. 앞서 승인한 정확한 Croatian G8b resource의 재배포 범위도 그대로다.

## 확인된 다음 작업

1. LTU 역경매 XLS: 원본 다운로드 성공, sheet/열·실제 기간·ISIN/만기·수익률 정의·rights 검증. 완료해도 daily 5Y와 별도 자료로 취급.
2. PRT BPstat: 기존 정확한 series를 안정적으로 받고 5년 선정 계약을 확정.
3. HRV: 직접 단위 근거 및 언어별 방법론 상충 해소.
4. SVN/LTU 거래소 자료는 배포 가능한 source contract가 확인될 때까지 미연결 유지.

연구 문서만 변경했으므로 코드 테스트는 재실행하지 않았다. 이전 98개 통과 결과와 승인된 gate 변경은 유지한다.

