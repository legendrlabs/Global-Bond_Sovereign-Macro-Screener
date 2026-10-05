# 공통 플랫폼 검증 — 2026-10-04 KST

사용자 제공 후보를 실제 조회 가능성, 5Y 정의, 시계열 접근, 재배포 권리로 분리한다. 이 문서는 경로 조사 기록이며 수집 어댑터 연결 완료 판정이 아니다.

## Investing.com

- 사용자 URL: https://kr.investing.com/rates-bonds/world-government-bonds
- 검색 서비스의 공개 페이지 조회에서 미연결 14개국의 5년물 표기 중 ISL/NZL/CZE/BGR/IRL/DNK/LTU/HRV/SVN/SVK/AUT/PRT/ISR 항목을 확인했다. ESP 확인은 기존 표기와 개별 링크를 후속 대조한다.
- 일반 requests GET(접속5초/읽기15초)은 ReadTimeout. 검색 서비스의 페이지 조회 성공을 배포 런타임 직접 수집 성공으로 기록하지 않는다.
- 페이지 시간 열의 DD/MM이나 HH:MM만으로 연도·거래일·시간대·공식 종가를 확정하지 않는다. 5년이라는 화면 이름만으로 constant-maturity/par/zero/benchmark 중 어느 것인지 확정하지 않는다.
- 페이지 하단 리스크 고지는 사전 서면 허가 없이 데이터 사용·저장·복제·표시·수정·송신·배포를 금지한다고 설명한다. 배포판의 무인증 자동 수집·숫자 재배포에 대한 허가를 확보한 것은 아니다.
- 이번 조사에서는 국가/만기 존재를 확인하는 탐색용으로 활용한다. 제공자 금리나 과거 시계열을 이 저장소에 복사하지 않는다.
- Historical Data 무료 조회/CSV 다운로드가 모두 무로그인 API라는 사용자 제안은 아직 검증되지 않았다. 접근성과 권리 모두 별도 확인 대상.

## 사용자 후보에서 정정할 부분

- BGR 현재 통화는 BGN이 아니라 EUR: 2026-01-01 채택. 기존 config의 EUR 및 전환일은 유지한다. 근거: https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260101~c830245e42.en.html
- OECD 일반 Long-term interest rates는 10년 만기 정부채를 정의한다. 일괄 API 접근이 가능해도 이 지표를 5년물로 넣지 않는다. 근거: https://www.oecd.org/en/data/indicators/long-term-interest-rates.html
- OECD 공식 회원/파트너 안내에서 HRV도 accession 상태다. “BGR만 제외한13개국 모두 회원”이라는 설명은 현재 상태와 맞지 않는다. 비회원 통계도 있을 수 있으므로 회원 여부와 실제 5Y 수집 가능 여부는 별도로 판단한다. 근거: https://www.oecd.org/en/about/members-partners.html
- ECB 유로존 통합 곡선과 국가별 5년물은 다른 계열이다. 국가 차원·발행주체·만기·계열 코드를 직접 확인하기 전에는 유로존 국가8곳 모두 확보라고 판정하지 않는다.

## 조사 분담과 중단 기준

루나 조사 담당 세 개가 파일 경로 ISL/ESP/SVK/PRT/ISR, 유럽 IRL/DNK/LTU/HRV/SVN/AUT, NZL/CZE/BGR를 나눠 진행한다. 성공뿐 아니라 HTTP 상태, 인증 요구, 주기·정의 불일치와 권리 제한도 남긴다. 워크 실행 종료 시까지 확보한 자료를 기록하며 실행 종료 이후의 자동 지속을 약속하지 않는다.

## World Government Bonds

- https://www.worldgovernmentbonds.com/ 공개 조회에서 본문은 받았지만 Last Update는 날짜 플레이스홀더였다.
- https://www.worldgovernmentbonds.com/country/bulgaria/ 및 /bond-historical-data/bulgaria/5-years/ 페이지가 존재한다. 이번 검색 서비스 조회의 금리·시계열 기간·관측 시각은 빈 플레이스홀더였다. 14개국의 실제 5Y 수신 완료를 의미하지 않는다.
- NZL 5Y 과거자료 페이지도 같은 결과: https://www.worldgovernmentbonds.com/bond-historical-data/new-zealand/5-years/
- Credits에 Investing.com 및 TradingEconomics.com이 명시된다. 별도의 독립 공식 원자료나 자유로운 재배포 권리가 생겼다고 추정하지 않는다.
- 5Y CDS는 5년물 국채금리와 다른 지표다. 연말 곡선 이력표도 일별 5Y 시계열과 다르다. 이 페이지의 만기 명칭만으로 constant-maturity 정의는 확정하지 않는다.
- https://www.worldgovernmentbonds.com/terms-privacy-policy/ 는 주로 개인정보 설명이다. 데이터 자동 수집·재배포를 명시적으로 허용하는 라이선스는 이번 읽기에서 확인하지 못했다. 권리 검토 상태는 미확인이다.

## Trading Economics

- https://tradingeconomics.com/bonds 는 Major10Y 및 Government Bond10y라고 명시한다. 이 표를 5Y 입력으로 사용하지 않는다. 별도 5Y 상품이 존재하는지는 별도 조사다.
- https://docs.tradingeconomics.com/get_started/ 의 공식 Authentication 설명은 플랜 가입과 API 키 취득을 안내한다. 이 API를 인증 없는 일괄 수집 경로라고 기록하지 않는다.
- 웹 조회, API 접근, 데이터 재배포 권리는 각각 검토한다.
