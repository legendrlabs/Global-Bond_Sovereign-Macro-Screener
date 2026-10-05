# 미연결국 통계 메타데이터·별도 원본 경로 후속 조사

조사일 2026-10-05 KST. [PRT·HRV 재확보](2026-10-05-prt-hrv-retry.md)의 후속이다. 신규 연결 0개, 기존 18개 연결 / 9개 미연결 유지. 자료 조사만 수행했으며 수집기, 점수식, 국가 정의 및 publication/data gate는 변경하지 않았다.

## 조사 범위와 집계

Exa 검색 21회, 요청 결과 슬롯 105개, 실제 URL 항목 101개, URL 문자열 기준 중복 제거 후 93개. 이 수치는 검색 후보 수이며 원본 다운로드 성공 건수나 검증 완료 자료 수가 아니다. 검색 요약을 검토하고 유망한 공식 경로는 본문·원본·메타데이터를 추가 확인했다. 단순 제목만으로 관측값·재배포 허용을 확정하지 않았다. 추가 공식 검색 서비스 검색 3개 및 본문 열람도 수행했다.

검색 축은 HRV 단위·방법론·SDDS·API, DNK 일별 통계·곡선 산출, LTU 중앙은행 통계·국채 지수·자본시장 보고서, SVN 통계청·중앙은행, AUT 중앙은행, BGR 정부채권 시장 보고서, NZL benchmark 제공 조건, IRL 현행 국채 통계다. PRT의 앞선 403 URL은 이번에 반복 요청하지 않았다.

## HRV: SDDS의 % 설명은 G8b 단위 근거가 아니었다

공식 SDDS 페이지:
https://www.hnb.hr/static/statistika/sdds/h-SDDS-podaci.html

직접 HTTP 200, 43,766 bytes, SHA-256 `2997896ab7c1da4a3ba2f590f63cc4b85e50e87a25131085e7d23029e139bc29`. 직접 HTML의 표시 갱신일은 2026-10-02 09:00이다. 검색 추출은 2026-02-20, 다른 검색 서비스는 2026-09-04로 표시해 추출본 시점 차이가 있었다. 이 페이지 날짜를 다른 파일의 관측일 또는 출처 고지용 수정일로 사용하지 않는다.

금리 섹션의 해외시장 발행 국채 항목은 연간 % 단위를 표시한다. 그러나 HTML에서 실제 연결된 원본은 다음 별도 XLS다:
https://www.hnb.hr/documents/20182/246479/gb-hrv.xls

직접 HTTP 200, 28,672 bytes, SHA-256 `3ba15dfebbc38c0c70161aede80a77b294ea66359fc2c9940a4ae841869a9102`. OLE XLS 원본을 xlrd로 읽어 Sheet1의 41행·4열과 Sheet2/3의 빈 상태를 확인했다. 헤더는 발행일, 통화, 발행명목금액, 이자율(%)이다. 마지막 비어 있지 않은 발행일은 2023-06-06이다. 이는 쿠폰/발행 조건 목록으로, 관측일별 잔존 5년 시장수익률 시계열이 아니다. SDDS의 % 설명을 G8b 국내 EUR 5년 열에 전용하지 않는다.

SDDS에서 연결된 [IMF 금리 메타데이터](https://dsbb.imf.org/sdds/dqaf-base/country/HRV/category/INR00)는 추출에서 일반 DSBB 제목만 확인되어 상세 정의를 확보하지 못했다.

[HNB REST API 문서](https://api.hnb.hr/)에서 확인한 공개 endpoint는 환율 API v1/v2/v3다. 이 문서에서 G8b endpoint는 확인하지 못했다. `api.hnb.hr`에 다른 HNB 웹페이지가 검색된다는 이유만으로 국채 API의 존재를 가정하지 않는다. 다른 서비스를 포함한 전체 HNB API 부재 판정도 아니다.

## DNK: 현재 일별 변수 목록 재확인

공식 tableinfo:
https://api.statbank.dk/v1/tableinfo/DNRENTD?format=JSON&lang=en

직접 HTTP 200, 437,640 bytes, SHA-256 `386f51670bb09e3e7470582def23cf6ae2781ae741aff8448f928945b838bd5b`. INSTRUMENT 10개는 정책금리 4개, DESTR 4개, preDESTR 2개다. LAND는 DK 하나이며 시간 축 마지막 항목은 2026-10-01이다. 이 날짜는 메타데이터의 시간 축이며 국채 관측 성공으로 집계하지 않는다. 현재 목록에 5년 국채 항목은 없다. 이전 DNRENTD 조사 결과를 재확인한 것이며 신규 발견이 아니다.

Nationalbank 곡선 논문·BIS 2005 기술 문서·과거 발행 보고서도 검색됐지만 현행 인증 없는 5년물 파일을 새로 확보하지 못했다. [2022 economic memo](https://www.nationalbanken.dk/media/0nfg1ivf/economic-memo-no-7.pdf)의 곡선/기간프리미엄 자료에는 외부 가격 제공자와 자체 계산이 포함된다. 논문 모형을 새 입력값 생성에 사용하지 않는다.

## LTU: 별도 중앙은행 도표 발견, 현행 5년 시계열 미확보

2025 자본시장 보고서의 공식 원본:

- [영문](https://www.lb.lt/uploads/publications/docs/67019_1fc43a73e2b4b84c08dbac4e080f96fe.pdf)
- [현지어](https://www.lb.lt/uploads/publications/docs/67027_757ed5b2b877bec4cfc3f3a75e5c6c19.pdf)

공식 URL 본문 추출에서 2025-12-31 기준 잔존 만기별 국채 수익률·잔액 도표와 여러 만기 범주를 확인했다. 추출 텍스트에 5년 및 5–10년·10–20년·20년 초과 표기가 있으나 첫 범주의 정확한 경계 및 집계 계약은 확정하지 않았다. 정확한 constant-maturity 5년 관측으로 취급하지 않는다. 2025년 말 스냅샷 자체도 현행 입력 대체가 아니다. 영문 PDF 직접 다운로드는 HTTP 403; 원본 바이트·해시를 확보했다고 기록하지 않는다. 원문 추출과 다운로드 성공을 구분한다.

[중앙은행 predefined tables](https://www.lb.lt/en/predefined-tables)에 국채 지수 및 입찰 결과 항목이 표시되지만 이번 직접 요청은 HTTP 403이었다. 지수 수준을 수익률로 바꾸거나 입찰 수익률을 secondary market 5년으로 대체하지 않는다.

[재무부 시장리뷰 페이지](https://finmin.lrv.lt/en/competence-areas/state-debt-management/reviews-and-statistics/government-securities-market-reviews-and-average-weighted-yields/)는 Government Securities Market Reviews가 2018년부터 중단되었다고 명시한다. 이는 해당 리뷰의 중단 설명이며 별도 국채 지수나 모든 5년물 자료의 종료 판정이 아니다.

## 다른 탐색 축의 분류

| 국가 | 공식 또는 제공자 근거 | 이번 판정 |
|---|---|---|
| SVN | [SiStat 0314989S](https://pxweb.stat.si/SiStatData/pxweb/en/Data/-/0314989S.px/), 정부 총부채의 내재금리, 연간·% | 5년 시장수익률 아님. 표의 최근 갱신일만으로 입력으로 채택하지 않음 |
| AUT | [OeNB UDRB 정의](https://www.oenb.at/en/Statistics/Standardized-Tables/interest-rates-and-exchange-rates/austrian-government-bond-yields/average-government-bond-yields-weighted-by-outstanding-amounts-daily-averages.html) | EUR 고정금리 국채 중 잔존 1년 초과의 가중평균. 기존 제외 근거 재확인; 5년 아님 |
| BGR | [2026 Q2 공식 시장보고서](https://www.bnb.bg/bnbweb/groups/public/documents/bnb_publication/gssm_2026_06_en.pdf), 2025 Q4/Q3 및 2024 Q4도 검색 | 경매수익률·repo 및 거래량과 정확한 secondary 5년을 구분. 새 연결 원본 없음 |
| NZL | [NZFMA NZdata 조건](https://www.nzfma.org/nzdata/), [NZFBF 정부채 closing 정의](https://www.nzfbf.co.nz/benchmarks/closing-rates/nzgs) | 정부채 closing 실시간 자료는 유료 구독 목록에 포함. 선택된 발행 만기의 outright yield라는 설명은 확인; 무료 커뮤니티 재배포 권한을 추가 확보하지 못함 |
| IRL | [NTMA 정부채](https://www.ntma.ie/business-areas/funding-and-debt-management/government-securities/government-bonds), ECB/FRED 검색 | 기존 발행/잔액 자료, 유로지역 aggregate 5년 및 아일랜드 10년을 구별. 새 아일랜드 현행 5년 원본 없음 |

검색된 commercial API 광고, 과거 학술 시계열, swap, 쿠폰, 발행금리, 채무 내재금리 및 가격 지수는 새로운 국가 연결로 집계하지 않았다. 403·추출 불완전·검색 결과 부재를 국가 데이터의 절대 부재로 단정하지 않는다.

## 다음 확인 / 검증

HRV는 여전히 G8b 5년 열의 직접 단위 선언과 영문 360일/현지어 365일 상충 해소가 필요하다. LTU는 도표의 근원 자료 또는 현행 국채 지수의 실제 정의·원본 경로 확인이 다음 후보지만, 직접 다운로드나 단위/만기 계약을 확보하기 전에는 연결하지 않는다.

문서만 변경해 테스트를 재실행하지 않았다. `git diff --check`와 변경 파일 범위를 확인한다. 기존 98개 테스트 통과 기록은 앞선 구현 검증 결과이며 이번 새 실행 결과가 아니다. 원본 XLS/PDF·시장수익률 숫자는 저장소에 올리지 않았다.
