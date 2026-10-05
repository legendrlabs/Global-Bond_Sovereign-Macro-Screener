# 미연결국 대체 경로 탐색

조사일: 2026-10-05 KST / UTC. Exa 검색 19회, 요청 결과 슬롯 95개, 반환 URL 95개를 중복 제거하면 83개다. 이는 83개 원본 다운로드 완료를 뜻하지 않는다. 유망한 공식 자료는 본문을 추가 확인하고 일부는 일반 HTTP 요청으로 검증했다.

신규 collector 연결은 0개다. 미연결 9개국과 기존 DATA_HOLD, scoring, 국가 정의, freshness, redistribution 및 public-output 게이트를 유지한다. 이번 변경은 연구 문서뿐이다.

## 핵심 결과

| 국가 | 이번에 추가 확인한 내용 | 연결 판단 |
|---|---|---|
| AUT | OeKB의 공식 5년 benchmark ISIN과 동일 채권의 거래소 gross YTM·기준일 필드를 직접 확인 | 접근은 가능하지만 사이트가 체계적 다운로드·재현을 제한. 공개 자동수집에 미연결 |
| NZL | RBNZ의 2025-08-25 제공 방식 변경 공지 확인: 장중 호가에서 전일 종가로 변경 | 역사 구간의 정의와 시차를 구분해야 함. 기존 접근·권리 조건 미해소 |
| LTU | 2026Q2 공식 PDF에 명목 만기와 잔존 만기별 표가 모두 존재 | 잔존 만기 표도 발견했으나 유통시장 고정 5년 시계열 계약은 미검증 |
| SVN | Monthly Bulletin의 Government Securities Rates 표 본문 확인 | 개별 채권 발행 조건·쿠폰 표이므로 5년 시장수익률 후보에서 제외 |
| BGR | 2026-09-28 5년물 재개방 경매 공식 공지 확인 | 경매 수익률이며 유통시장 5년 시계열로 대체하지 않음 |
| DNK | 국채 경매표와 2025년 정부부채 보고서 확인 | 경매 수익률·여러 만기의 발행 평균·2/10년 benchmark 자료. 현행 5년 경로 미확보 |
| IRL | 공식 데이터 포털, ECB/Eurostat 역사 자료, 중앙은행 통계 후보 재검색 | 보유량·과거 통계·10년물 결과. 새 현행 5년 경로 미확보 |
| HRV | G8b 단위 근거 재검색 | 앞선 영문 360일/현지어 365일 상충과 단위 확인 과제 유지 |
| PRT | 공식 API 전체 문서에서 최근 n개 필터 이름 확인 | `obs_last_n`이 문서화된 이름. 올바른 필터로 요청했으나 HTTP 403 |

## AUT: benchmark 식별에서 실제 YTM 필드까지 확인

OeKB 공식 benchmark 목록:
https://www.oekb.at/en/capital-market-services/our-range-of-data-knowledge-creates-an-advantage/data-on-austrian-government-bonds/benchmark-government-bonds-of-the-republic-of-austria.html

2026-08-31 기준 5년 benchmark로 `AT0000A2NW83`을 표시한다. 표의 숫자 열은 Coupon이며 수익률이 아니다. 해당 ISIN은 발행자 측 공식 benchmark 분류의 근거로만 사용한다. 정확히 잔존 5년인 constant-maturity 값이라는 의미로 확대하지 않는다.

동일 ISIN의 Borsa Italiana / MOT 페이지:
https://www.borsaitaliana.it/borsa/obbligazioni/mot/euro-obbligazioni/scheda/AT0000A2NW83-MOTX.html?lang=en

인증 없는 일반 요청 HTTP 200으로 실제 페이지를 확인했다. `Effective Yields`에 gross/net yield to maturity, modified duration, reference price 및 reference price date 필드가 있다. 직접 받은 페이지의 기준일은 2026-10-02였다. 제공자로 Skipper Informatica Srl을 표시한다. 이는 채권별 계산 YTM이며 정부 통계 시리즈나 과거 일별 5년 benchmark 연결 완료가 아니다.

구형 ISIN URL의 검색 추출은 2026년 3월 값, MOTX URL의 검색 결과는 9월 값, 직접 응답은 10월 기준일이었다. 검색 날짜나 페이지 제목으로 관측 최신성을 결정하면 안 된다는 사례다. 숫자를 비교하여 보정하거나 과거 검색 값을 최신값처럼 쓰지 않는다.

공식 사이트 이용 조건:
https://www.borsaitaliana.it/varie/disclaimer/disclaimer.en.htm

개인 연구 목적의 제한적인 이용과 체계적 다운로드·콘텐츠 재현을 구분한다. 후자는 허용된 자동수집/재배포 경로로 간주할 수 없고, 재현에는 사전 명시적 동의가 필요하다고 설명한다. 비상업적 커뮤니티 공유라는 이유만으로 이 조건을 해소하지 않는다. 공개 연구 문서에는 해당 페이지의 시장 수치·원본 HTML을 첨부하지 않는다. 별도 허용된 자료 경로 또는 명시적 라이선스 확보가 필요하다.

직접 응답 식별 기록:

| 자료 | HTTP | bytes | SHA-256 |
|---|---|---:|---|
| OeKB 데이터 안내 | 200 | 60,543 | `7dabd7440085f8eb038bd32e78d8b2676ba0fcb58c255f033accfa2ac848a7fe` |
| OeKB benchmark 목록 | 200 | 59,237 | `33c7c6010442f8843c827727e45ec30e5a5e2f4fac4ade181f178f96832226fa` |
| MOTX ISIN 페이지 | 200 | 58,975 | `4cb578c7c9291f9c27da1acd983372896ed18d5a3b9c4405a21d48d8be2453f7` |

## NZL: 공식 공지로 확인한 시계열 정의 변경

RBNZ 공지, 게시 2025-08-22 / 적용 2025-08-25:
https://www.rbnz.govt.nz/statistics/stats-alerts-and-updates/2025/sa-04

1·2·5·10년 benchmark를 포함한 정부채 자료가 장중 indicative mid-rate에서 NZFMA 전일 종가와 1일 발표 지연 방식으로 변경됐다고 설명한다. 이전 시각은 11:10am이다. 공지는 역사 자료와 이후 공개분도 전일 종가 및 발표 시차 방식으로 제공한다고 설명한다. 그러나 모든 과거 기간이 같은 정의로 재작성되었다는 범위나 연속성까지 확정하지 않는다.

공지가 안내한 대체 XLSX는 Daily close (2018-current), Monthly close (2018-current)다. 현재 B2 페이지의 benchmark 교체 표도 별도 확인 대상이다:
https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/wholesale-interest-rates

이번 공지 직접 요청은 403이었고 공식 URL의 검색 추출 본문으로 내용을 확인했다. XLSX 다운로드·권리 승인·자동수집 연결을 완료한 것으로 집계하지 않는다. 앞선 RBNZ 자동 접근 조건과 NZFMA 권리 과제는 유지한다.

## LTU: 잔존 만기 표도 있으나 수익률 계약 검증은 남음

공식 재무부 2026Q2 PDF:
https://finmin.lrv.lt/public/canonical/1783409314/27578/VSP%202026Q2.pdf

본문에 명목 만기별 표와 잔존 만기별 표가 모두 있다. 5년 열과 % 단위를 명시하고, 국내 등록 채권·외국 예탁기관 등록 Eurobond·저축채 제외 합계·저축채를 나눈다. 잔존 만기 표까지 존재하므로 자료 전체를 단순히 original maturity 표라고 배제해서는 안 된다.

다만 본문에서 현행 유통시장 관측값의 원천·가중치·만기 구간 처리·날짜 정의를 확정하지 못했다. 월별·분기별 발행 집계와 같은 시장의 일별 5년 금리를 혼동하지 않는다. `-` 및 아직 비어 있는 향후 월을 추정하지 않는다. 검색 서비스의 공식 PDF 추출로 본문을 확인했고 원본 직접 다운로드 성공으로 집계하지 않는다.

재무부 안내:
https://finmin.lrv.lt/en/competence-areas/state-debt-management/reviews-and-statistics/government-securities-market-reviews-and-average-weighted-yields/

여기서 2018년부터 중단됐다고 설명하는 것은 Government Securities Market Reviews다. 별도로 이어지는 yield PDF까지 중단됐다는 결론으로 확대하지 않는다.

중앙은행 Capital market review 2025:
https://www.lb.lt/uploads/publications/docs/67019_1fc43a73e2b4b84c08dbac4e080f96fe.pdf

2025-12-31 기준 잔존 만기별 국채 YTM 그래프가 있다. 그래프에서 읽은 값으로 입력을 생성하지 않는다. 별도 수치 원본의 공개 여부가 다음 후보이며, 직접 요청은 403이었다.

공식 금융시장 통계는 국채 경매 결과와 국채 지수를 별도로 연결한다:
https://www.lb.lt/en/financial-markets-statistics

국채 지수의 weighted average yield도 고정 5년 수익률로 승격하지 않는다. 지수에 yield 필드가 있다는 발견과 만기별 국가 금리 시계열 확보는 구분한다.

## SVN: 제목만으로 수익률 후보를 확정하지 않음

2025년 12월 Monthly Bulletin, 표 2.5 / 통계편 II-38:
https://www.bsi.si/storage/uploads/ab88bdc3-fc77-41dd-a56b-8a0143f848f3/bil_2025_12.pdf

본문 열은 채권명·발행일·만기일·금리·발행잔액·발행/지급 통화·원금 연동이다. 발행일 이후 적용되는 금리 설명도 있어 정부채 행은 계약 쿠폰 정보로 판별된다. 이 표의 이름이나 % 표시만으로 secondary-market 5Y YTM 자료라고 판단하지 않는다.

직접 PDF 요청은 403이었으나 공식 URL의 전체 추출 본문을 확인했다. 원본 바이트·SHA 확보는 미완료다. 이전 interests API 403을 회피하기 위해 다른 미검증 endpoint를 생성하지 않았다.

## BGR / DNK / IRL: 사용 가능한 종류를 구분

BGR 5년물 재개방 공식 공지:
https://www.minfin.bg/en/news/2026-09-30/13521

2026-09-28 경매에서 2031-01-28 만기 EUR 채권을 재개방했다고 설명한다. 쿠폰과 경매 평균 수익률은 별도 항목이다. 새 발행 가격에서 얻은 경매 금리를 국가 유통시장 5년 금리로 대체하지 않는다.

DNK 공식 경매 결과:
https://www.nationalbanken.dk/en/government-debt/trading-and-data/auction-results-government-bonds

2025년 정부부채 보고서:
https://www.nationalbanken.dk/media/q5cf5y2l/central-government-borrowing-and-debt-2025.pdf

여러 만기를 섞은 연간 발행 평균은 5년물이 아니다. 2·10년 benchmark 자료나 국채 경매표를 현행 5년 데이터의 근거로 바꾸지 않는다.

IRL 공식 보유량 dataset:
https://opendata.centralbank.ie/en_GB/dataset/holders-of-long-term-irish-government-bonds

이 자료는 만기 1년 초과 정부채의 부문별 보유량이다. 다운로드 파일 이름에 Government Bonds가 있어도 금리 자료가 아니다. 추가 검색에서 현행 무인증 5년 수익률 경로는 확보하지 못했다.

## PRT: API 최근 관측 필터 이름 검증

공식 API 문서:
https://bpstat.bportugal.pt/data/docs

Get Dataset의 문서화된 최근 n개 관측 필터는 `obs_last_n`이다. 이전 후보 URL의 `last_n`과 구분한다. 날짜 필터 두 개의 문서 설명은 이름과 방향이 직관적으로 맞지 않아 직접 응답 검증 없이 적용하지 않는다.

정확한 필터를 사용한 한 번의 제한된 일반 요청:
https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?lang=EN&series_ids=12099457&obs_last_n=5

이번 응답은 HTTP 403이다. 접근 실패를 series 부재로 판정하지 않고, 과거 성공 응답으로 최신 관측을 대체하지 않는다. 문서 안내상 rate-limit 응답은 429이므로 이번 403을 rate-limit으로 확정하지 않는다. 보호 장치 우회나 반복 요청은 하지 않았다.

## 다음 조사 우선순위

1. AUT: 동일 공식 benchmark의 수익률을 허용된 공식/개방 경로에서 제공하는지 확인. MOT 페이지는 자료 존재 확인용으로만 유지.
2. LTU: 잔존 만기 표의 source·가중치·만기 분류 및 발행/유통시장 정의 확인. 중앙은행 그래프의 별도 수치 자료 공개 여부 탐색.
3. PRT: 허용된 API 접근 재현성과 전체 산출 계약 확인. 최근 n개 필터는 공식 문서의 `obs_last_n` 사용.
4. HRV: 이전 후속 문서의 단위·360/365일 상충 과제 유지. NZL은 발표 시차·benchmark 교체·접근 권리 구분.

관련 선행 기록: [9개국 조사](2026-10-05-nine-country-sweep.md), [5년물 정의 후속](2026-10-05-five-year-definition-followup.md).

문서만 변경했으며 테스트는 재실행하지 않았다. 변경 파일 범위 및 `git diff --check`로 공백 오류를 검증했다.
