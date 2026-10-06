# 제미나이 보완 경로 검증 — 2026-10-06

이 문서는 당시 조사 상태를 기록한다. 이후 공식 등급 수집기 구현과 검증은
[2026-10-07 확인 기록](2026-10-07-issuer-credit-source-check.md)을 참조한다.

검증 범위: 독일 잔존만기 약 5년 국채 호가, 한국 국채 호가 접근 경로,
ADB 스프레드 자료 및 재무부·국채청 신용등급 페이지.
공개 페이지와 공식 저장소를 확인했다. 유료 피드나 증권사 인증 API는 호출하지 않았다.

## 채택한 신용등급 보완 경로

통합 평가사 목록에 접근하지 못하면 각국 재무부·국채청의 공식 등급 페이지를
보완 출처로 사용한다. 평가사, 장기/단기, 자국통화/외화, 전망, 평가·보고서 날짜를
구분하고 수집 시각 및 홈페이지 수정일과 따로 보관한다.

| 국가 | 확인한 공식 출처 | 확인 범위와 남은 조건 |
| --- | --- | --- |
| 프랑스 | [AFT](https://www.aft.gouv.fr/en/frances-credit-ratings) | 평가사별 등급·전망·검토 일정. 요약에서 통화·기간 분류가 명확하지 않아 평가사 원문 대조 필요. 재조회 중 503 오류도 관측. |
| 독일 | [Finanzagentur](https://www.deutsche-finanzagentur.de/en/federal-funding/government-as-issuer/ratings) | 장기·단기 등급, 전망, 보고서 날짜와 원문 PDF 링크. 요약에서 통화 분류가 분리되지 않아 원문 대조 필요. |
| 뉴질랜드 | [NZDM / Treasury](https://debtmanagement.treasury.govt.nz/investor-resources/credit-ratings) | 국내통화·외화 등급, 전망, 평가사별 갱신일을 별도 표시. 홈페이지 하단 수정일 대신 해당 행의 날짜 사용. |

프로젝트의 `credit.candidate_sources` 및 보고서의 연구 링크 표에 세 출처를
등록했다. `RESEARCH_LINK`, `usable_for_scoring=false`이며 실제 등급 수집기는
아직 연결하지 않았다. 등급 숫자, 신용 점수 또는 Adjusted를 생성하지 않는다.
이 변경은 개발 소스에 반영한 상태이며 배포된 v0.1.4 패키지를 교체하지 않았다.

## 독일 종목과 실제 양방향 호가

[발행기관 종목 명세](https://www.deutsche-finanzagentur.de/en/federal-securities/factsheet/isin/DE000BU25075)에서
`DE000BU25075`는 Bundesobligation Series 194, 표면금리 2.90%,
만기 2031-10-08로 확인했다. 2026-10-06 기준 잔존만기 약 5년이다.

아래 값은 검색 엔진의 과거 캐시가 아니라 같은 날 원본 HTML을 직접 읽은 표본이다.
가격은 각 페이지 게시 단위 그대로 기록했다. 원본 HTML 해시는 아래에 보관했다.

| 거래소 | Bid | Ask | 페이지 시각 | 수집 시각 UTC | 시간 해석 |
| --- | ---: | ---: | --- | --- | --- |
| [Tradegate BSX](https://www.tradegatebsx.com/orderbuch.php?lang=en&isin=DE000BU25075) | 98.417 | 98.418 | 2026-10-06 14:17:32 | 12:17:32.724549 | 페이지에 CEST(UTC+2) 명시. `Last Update`는 페이지 갱신 시각이며 개별 호가 생성 시각과 같다고 확정하지 않는다. |
| [Stuttgart](https://www.boerse-stuttgart.de/de-de/produkte/anleihen/stuttgart/bu2507-bundesrep-deutschland-bundesobl-ser-194-v-2026-31/) | 98.421 | 98.422 | 06.10. 14:17:05 | 12:17:32.012507 | 양방향 호가 옆 시각. 별도 `Kurszeit`는 14:06:50으로, 최종 가격 시각과 다르다. 원문 시각 문자열을 보존한다. |

Tradegate의 양쪽 잔량 표시는 각각 250,000이었다.
Stuttgart는 양쪽 각각 10,000,000 Nom.을 표시했다.
두 거래소의 스프레드는 게시 가격 단위로 0.001이었다.
가격 차이를 곧바로 **수익률 bp**로 기록하면 안 된다.
수익률 스프레드는 동일한 결제일·쿠폰·경과이자·일수 규칙으로 양쪽 YTM을
계산한 뒤 `10,000 × (YTM_bid − YTM_ask)`로 산출한다(YTM은 소수 단위).
`(Ask − Bid) / Duration`만으로 bp로 바꾸는 방식은 가격 정규화와 단위가 빠져 있다.

한 종목·한 거래소의 순간 호가는 국가 전체 국채시장 유동성이 아니다.
국가 비교에는 만기, 지표물 여부, 거래 장소, 시각, 호가 잔량과 집계 기간을 맞춰야 한다.
이번 확인으로 두 웹페이지의 공개 호가 존재를 검증했지만 일별 수집기의 안정성과
27개국 비교 자료 확보까지 검증한 것은 아니다.

원본 HTML SHA-256:

- Tradegate: `a0485beba90c3b2443f5450a22aff8640172ee9ac1b2d961ed2051295ea9c5d7`
- Stuttgart: `f8cc9f17163592d0e90d63b33a74c0c16697dafe2e53cdebbc37c76d5a309cb2`

### Frankfurt와 Borsa Italiana에 대한 정정

- Frankfurt의 `Bid=0 / Ask=0`만으로 장외시간 또는 스페셜리스트 호가 공백을
  원인으로 단정할 수 없다. 표시·피드·종목 상태 등 원인은 추가 확인이 필요하다.
- [Frankfurt 공식 거래시간](https://cashmarket.deutsche-boerse.com/cash-en/trading/trading-calendar-and-trading-hours)의
  현지 08:00–17:30은 서머타임 CEST에 한국 15:00–익일 00:30,
  표준시 CET에는 한국 16:00–익일 01:30에 해당한다.
- [Borsa의 실제 해당 종목 페이지](https://www.borsaitaliana.it/borsa/obbligazioni/mot/euro-obbligazioni/scheda/DE000BU25075-MOTX.html?lang=en)는
  확인했다. 제시된 All Data 경로에는 `mic=MOTX`가 포함된 링크가 있다.
  공개 응답에서 거래·수익률 정보는 보였지만 실제 5단계 양방향 호가·잔량은
  확보하지 못했다. 페이지 제목의 `Real Time Quotes`만으로 무료 5단계 호가창을
  검증했다고 볼 수 없다.

## 한국 호가 경로

| 주장 | 검증 결과 |
| --- | --- |
| KRX 국채전문유통시장 일별매매정보 API에 Bid/Ask 필드 없음 | 확인. 기준일 `basDd` 입력, 가격·수익률 시고저종 및 거래량·거래대금 출력. 앞서 제시된 BEST_BID/ASK 등은 명세에 없다. |
| 무료 KRX 웹페이지 어디에도 양방향 채권 호가가 없음 | 범위를 과도하게 넓힌 주장. KRX BondsAll 공개 Today Price 화면에는 양방향 가격·수익률 항목이 있다. 일반채권시장과 국채전문유통시장은 구분해야 하며, 실제 5년 지표물의 유효 관측값은 아직 확보하지 않았다. |
| KIS 장내채권 호가 API 존재 | 공식 저장소에서 확인. 실제 한국 5년 지표물의 응답·양방향 호가·시장 범위는 인증 후 검증해야 한다. |
| 키움에서도 같은 방식으로 5년 국채 호가 확보 가능 | 이번 조사에서 공식 TR과 실제 종목 응답을 확인하지 못했다. |

KRX 공식 근거:

- [국채전문유통시장 일별매매정보 명세](https://openapi.krx.co.kr/contents/OPP/USES/service/OPPUSES004_S2.cmd?BO_ID=CEnOyORzHgXWpdbUfWyf)
- [BondsAll Today Price](https://bond.krx.co.kr/contents/GLB/05/0504/0504040201/GLB0504040201.jsp)
- [KRX 채권시장 구분](https://bond.krx.co.kr/contents/GLB/02/0201/0201020000/GLB0201020000.jsp)

KIS 공식 근거:
[한국투자증권 open-trading-api](https://github.com/koreainvestment/open-trading-api/blob/main/examples_user/domestic_bond/domestic_bond_functions.py)
의 `inquire_asking_price` 함수.

```text
GET /uapi/domestic-bond/v1/quotations/inquire-asking-price
TR_ID: FHKBJ773401C0
FID_COND_MRKT_DIV_CODE: B
FID_INPUT_ISCD: 실제 조회 대상 채권 종목코드
```

공식 예제의 채권 코드는 특정 한국 5년 국채 지표물 검증 결과가 아니다.
제미나이가 반복한 ISIN도 만기·종류·상장 시장을 확인하기 전에는 사용하지 않는다.
일반 장내채권 API의 존재가 국채전문유통시장(D-Bond) 호가 접근을 입증하지 않는다.
무료 제공 범위, 계정 조건, 종목 지원과 관측시각 필드는 실제 인증 응답으로 별도 확인한다.

## ADB 한국 5년물 스프레드 주장

“한국 5년 온더런 스프레드의 월·분기 시계열 엑셀을 무료 다운로드”한다는
구체적 경로·파일·열 정의는 이번에도 확인하지 못했다.
[2026년 3월 ADB 공식 시장 보고서](https://asianbondsonline.adb.org/documents/abm/abm_mar_2026_bond_market_developments_4qtr_2025.pdf)의
국채 스프레드 자료와 기존 분기 국채 회전율 자료를 5년물 관측으로 바꾸어 부르면 안 된다.
파일 원문에서 국가·만기·단위·관측주기와 원천을 확인할 때까지 해당 주장은 미확인으로 남긴다.

## 다음 검증 대상

1. Stuttgart 또는 Tradegate의 개별 호가 시각 의미, 가격 단위 및 장중 반복 관측.
2. KIS에서 만기·시장까지 확인한 한국 5년 지표물의 실제 양방향 응답.
3. 추가 국가의 공식 등급 페이지를 같은 평가사·장기 자국통화 기준으로 확장.
4. ADB 한국 5년 스프레드라는 주장을 뒷받침할 실제 원본 파일.

앞선 신용등급 보완 작업에서는 확인한 신용등급 연구 링크를 보고서에 연결했다.
독일 호가 및 KIS API를 자동 수집하거나 시장 품질 점수에 넣지는 않았다.

## 추가 검증: 무료·키 없는 자동 수집 후보

### AOFM: 유효한 추가 후보지만 2026년 파일과 범위를 다시 확인해야 함

[Data Hub](https://www.aofm.gov.au/data-hub)의 기존
`turnover - treasury bonds.xlsx`는 2016년 7월–2025년 12월의 과거 자료다.
2026년 자료는 `new turnover - treasury bonds.xlsx` 링크를 확인해야 한다.
물가연동채권 자료는 별도 파일이다.
공식 페이지의 갱신 일정은 매년 2·5·8·11월 마지막 영업일이며 2개월 시차다.

[2026년 5월 공식 설명](https://www.aofm.gov.au/investors/wholesale-investors/investor-insights/recent-trends-ags-investor-base)은
2026년 3월 분기부터 상대방 분류와 보고 체계를 바꾸는 새 데이터셋을 안내한다.
따라서 기존 파서와 완벽히 호환된다고 단정할 수 없다.
이 실행 환경의 직접 페이지 요청은 timeout/502로 실패하여 실제 최신 엑셀의
시트·열·단위·관측 분기 및 자동 다운로드 성공까지는 확인하지 못했다.
공식 웹 문서에서 파일의 존재와 설명만 확인했다.

AOFM을 호주 `liquidity.candidate_sources`에 연구 링크로 등록했다.
수집값이나 회전율을 만들지 않았다. 거래액을 회전율로 바꾸려면 같은 범위·단위·기간의
잔액과 분모 산식이 필요하다. NY Fed 주간 일평균 거래량, JSDA 월간 매도·매수 합계,
ADB 정부채 분기 회전율과 네 국가의 동일 정의 회전율로 묶으면 안 된다.
무료 공개 파일의 존재는 영구 갱신이나 무중단 자동 수집을 보장하지 않는다.

### EIOPA: 실제 ZIP·엑셀 확인, 국채 Bid–Ask 대체 자료로 사용하지 않음

2026-10-05 공개한 2026-09-30 기준
[실제 ZIP](https://www.eiopa.europa.eu/document/download/cc358405-6419-4ffe-8cb3-55cf3c842f84_en?filename=EIOPA_RFR_20260930.zip)을
키·로그인 없이 다운로드하고 네 개 엑셀의 시트 구조를 확인했다.
수집 시각은 2026-10-06 12:30:26 UTC(21:30:26 KST), 크기는 3,282,086 바이트,
SHA-256은 `db690574d573f55d8148e76da1d90586c5a3ec2997cecd54e94abd206aa7af66`이다.

- `EIOPA_RFR_20260930_Term_Structures.xlsx`
- `EIOPA_RFR_20260930_PD_CoD.xlsx`
- `EIOPA_RFR_20260930_Qb_SW.xlsx`
- `EIOPA_RFR_20260930_VA_portfolios.xlsx`

`RFR_spot_no_VA` 시트의 국가명·커브 정의 행을 읽었다.
한국·KRW 및 뉴질랜드는 해당 목록에 없다.
미국·일본은 `OIS`, 호주·독일·프랑스·이탈리아는 `SWP` 기반으로 표시된다.
독일·프랑스·이탈리아와 Euro의 기본 5년 RFR 값이 같은 것도 확인했다.
국가 이름이 붙은 열이 있어도 그 나라 국채의 관측 수익률이라는 뜻이 아니다.

[공식 기술 문서](https://www.eiopa.europa.eu/document/download/f7fca58f-4d24-4441-ac60-de562bf26d77_en?filename=EIOPA-BoS-25-599+-+RFR+Technical+Documentation.pdf)의
5.3절은 스왑·국채를 사용하는 구성 방식을, 7.2절은 신용위험 조정을,
10.2절은 기준 포트폴리오의 위험 조정 스프레드에서 산출하는 VA를 설명한다.
RFR은 보험부채 평가용이고 CRA·VA는 매수·매도 호가 차이가 아니다.
월별 RFR은 기존의 7일 최신성 규칙을 적용하는 일별 5년 국채 금리 입력으로도
그대로 대체할 수 없다. 만기 1–30년의 실제 국채 호가 패널이라는 주장은 부정확하다.

자동 수집 자체는 가능한 자료다. 공식 페이지는
[월별 기술 파일 RSS](https://www.eiopa.europa.eu/feed/53/rss_en)도 안내하므로
향후 RFR 전용 용도에는 RSS로 판본을 찾고 ZIP 해시·실제 기준일·재공표를 추적할 수 있다.
이 스크리너의 국채 호가·유동성 수집 후보에는 연결하지 않는다.

### ETF 및 FTSE 후보의 사용 범위

ETF 호가 스프레드는 해당 ETF 주식의 거래비용 진단이다.
국가 전체 국채시장 또는 단일 5년 지표물 스프레드와 동일하지 않다.
만기·듀레이션·환헤지·거래소·관측시간이 다른 ETF를 국가 유동성 점수로
직접 비교하는 방식은 채택하지 않는다.
[SEC 투자자 안내](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-24)는
ETF 운용사 웹사이트에 중앙값 호가 스프레드가 공개됨을 설명한다.
추가 조사에는 Yahoo 실시간 스크래핑의 무중단 동작을 가정하기보다 운용사 공시를
우선하며, 국가·기초자산 범위 및 관측 기간을 확인한다. 특정 ETF 목록은 아직 선정하지 않았다.

FTSE 시장 접근성은 기존 조사 경로를 유지한다. 확인한 발표판·유효일·국가별
분류 근거를 함께 저장하고 반기 검토 때 갱신한다. 원문을 확인하지 않은 Level을
설정 파일에 임의로 기입하거나 등급 자체를 유동성 관측값으로 사용하지 않는다.

현 단계의 우선순위는 AOFM 최신 파일 접근·명세 검증, 공식 국가 등급 페이지 확장,
이미 양방향 호가를 확인한 독일 페이지의 시각·단위·반복 관측 검증이다.
