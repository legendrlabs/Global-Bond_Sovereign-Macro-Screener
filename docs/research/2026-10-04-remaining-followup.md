# 남은 국가 후속 조사 — 2026-10-04 KST

## HRV: 공식 파일과 방법론 확보, 어댑터는 아직 미연결

- [정부 공개 데이터 카탈로그 API](https://data.gov.hr/ckan/api/3/action/package_show?id=711cb511-fbfc-49c3-a6c3-7ae40cca5bdf): 무인증 HTTP 200.
- 카탈로그의 G8b 리소스가 [HNB 공식 XLSX](https://www.hnb.hr/documents/20182/1f79bc1c-dfb5-17fd-1571-cdd52a4a9619)를 가리킨다. 직접 HTTP 200, HRV 시트, 마지막 월은 2026년 8월이다.
- 헤더는 외국시장 USD / 외국시장 EUR / 국내시장 EUR로 분리되며 각 그룹마다 5 g. 열이 있다. 5년 숫자를 하나 찾았다고 다른 통화·시장 열을 같은 계열로 합치지 않는다.
- 국내시장 EUR 5년 열은 2026년 1~6월 `-` 결측이고 7~8월에만 값이 있다. 이를 장기 완전 시계열로 기록하거나 외국시장 EUR 값으로 자동 보충하지 않는다.
- [공식 Bulletin 298의 G8b 방법론](https://www.hnb.hr/c/document_library/get_file?groupId=20182&p_auth=57KypLaM&uuid=6bc0fe19-aff3-0de0-f3f0-8c93fd56787c)은 월별/연별 평균과 잔존 만기를 정수 연수로 묶은 수익률을 설명한다. 따라서 고정만기 일별 5Y 곡선과 같은 정의라고 승인하지 않는다.
- [공식 Bulletin 282 방법론](https://www.hnb.hr/documents/20182/4575178/ebilt282.pdf/e19c5e46-71d9-881f-33f9-36bd9a5ebc2e)은 국내시장 거래가격과 외국시장 Bloomberg bid를 구분하고, 국내시장은 거래 없는 날에도 마지막 평균가격으로 수익률을 계산한다고 설명한다. 공급자 자체의 가격 유지와 우리 파이프라인의 결측 보충을 혼동하지 않는다. 서로 다른 판본의 일수 기준이 달라 현행 방법론 대조는 남아 있다.
- 카탈로그 license_id는 `open-license`, license_url은 [열린 이용허락 페이지](https://data.gov.hr/id/licence/otvorena-dozvola-rh)이다. 이번 조회에서는 이용허락 본문을 읽지 못해 범위·귀속 조건과 외부 데이터 예외까지 확인한 것은 아니다. `redistribution: allowed`로 변경하지 않는다.

## PRT: 공식 직접 API 여전히 차단

[BPstat 공식 dataset 요청](https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?lang=EN&series_ids=12099457&last_n=5)을 다시 한 번 무인증 직접 요청했다. HTTP 403이다. 우회하거나 검색 서비스가 본 값을 배포 런타임 직접 수집 성공으로 기록하지 않는다.

## 나머지 유럽 국가 검색에서 제외한 후보

- [AUT OeNB UDRB](https://www.oenb.at/en/Statistics/Standardized-Tables/interest-rates-and-exchange-rates/austrian-government-bond-yields/average-government-bond-yields-weighted-by-outstanding-amounts-daily-averages.html)는 잔존 1년 초과 고정금리 국채의 발행잔액 가중 평균이다. 5년물 대체 계열로 쓰지 않는다.
- [AUT 국제 장기금리](https://www.oenb.at/en/Statistics/Standardized-Tables/interest-rates-and-exchange-rates/Euro-Area-Money-Market-Interest-Rates-and-Eurosystem-Interest-Rates/international-long-term-government-bond-yields.html)는 약 10년 잔존 만기다.
- [SVN 공식 PXWeb 수렴 장기금리](https://px.bsi.si/pxweb/en/serije_ang/serije_ang__20_obrestne_mere__40_OBR_MERE_KONV/I2_3_1E.px/)도 월평균 약 10년물이다.
- [LTU 중앙은행 경매 결과](https://www.lb.lt/vvp/Results.asp?lang=e)는 발행/경매 수익률과 종목 만기다. 일별 유통시장 고정 5년물 확보가 아니다.
- [DNK 중앙은행 경매 결과](https://www.nationalbanken.dk/en/government-debt/trading-and-data/auction-results-government-bonds)는 종목별 경매 결과이며, 물가연동채의 실질수익률도 포함한다. DKK 명목 일별 5년물로 자동 대체하지 않는다.
- IRL 공식 기관을 대상으로 한 이번 추가 검색에서는 직접 수집 가능한 5Y 계열을 새로 확인하지 못했다. 자료 부재의 증명은 아니다.

현재 남은 10개국을 연결 완료로 바꾸는 근거는 이 조사에서 추가되지 않았다.
