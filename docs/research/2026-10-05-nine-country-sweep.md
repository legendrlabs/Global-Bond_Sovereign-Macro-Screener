# 미연결 9개국 재조사

조사일: 2026-10-05 KST. 범위는 자료 조사이며 collector/config/scoring/quality/public-output은 변경하지 않았다. Exa로 국가별 및 공통 공식 소스·권리 조건을 21회 검색했다(요청 결과 슬롯 105개, 중복 포함; 고유 소스 수가 아님). 후보는 공식 원문 및 가능한 직접 다운로드로 대조했다. 이전 판단은 [정의·접근 조건 조사](2026-10-05-official-source-contracts.md)와 함께 읽는다.

## 결론과 다음 확인 사항

| 국가 | 이번 조사에서 확인한 경로 | 현재 연결을 막는 사항 | 다음 작업 |
|---|---|---|---|
| PRT 포르투갈 | BPstat **직접 획득 정보의 재현·배포 허용 조건** 원문 확보. 기존 12099457 일별 잔존 5년 API 후보 유지 | 이번 직접 API는 403. 기존 응답의 잔존 만기 정의와 국가 계약 대조 필요 | 우선순위 1: 접근 재현성 및 series/dimensions/정의 검증. 포털 이용허락 근거를 권리 검토에 반영 |
| HRV 크로아티아 | G8b XLSX, Bulletin 304 방법론, G8b 카탈로그의 열린 이용허락 및 공식 법령 원문 확보 | 월평균 잔존 만기 구간형. 5Y 열 단위 명시가 아직 미확정; 국내 EUR 결측 존재 | 우선순위 2: 단위 근거 및 현행 계약 대조. 허용 조건은 dataset 범위로 검토 |
| NZL 뉴질랜드 | NZFMA의 무료/유료 benchmark 목록과 NZFBF의 NZGS 정의 확인. Treasury 자료 목록도 확인 | 정부채 실시간 benchmark는 유료 목록. 무료 목록에 국채는 없음. 기존 RBNZ 자동 접근 조건 및 제3자 권리 문제 유지 | 허용된 대체 공식 경로나 라이선스 검토. 무료 swap/거래량/경매를 5Y yield로 대체하지 않음 |
| LTU 리투아니아 | 중앙은행 **Occasional Paper 58/2025**의 합성 수익률곡선 연구 발견 | Bloomberg 및 은행 내부 호가를 이용한 연구이며 합성 10년 benchmark 중심. 공개 갱신형 5Y dataset은 미확보 | 연구 후속 데이터 공개 여부 조사. 우리가 자체 NSS 보간하여 입력을 만드는 것은 범위 밖 |
| BGR 불가리아 | BNB Q2 공식 XLSX 직접 다운로드 성공. 재무부 August 2026 bulletin 공지 확인 | 확보한 workbook의 경매/쿠폰/거래·보유 자료에서 유통시장 고정 5Y 시계열을 검증하지 못함. 최신 bulletin 직접 접근은 403 | bulletin 원본 및 별도 곡선 수치 공개 여부 확인 |
| DNK 덴마크 | 현재 공식 금융시장 테이블 목록 및 MPK100 확인. 2025 정부채무 보고서의 곡선 자료 출처 확인 | MPK100은 연별이고 만기 선택 축이 없음. DNRENTM 5Y는 기존에 확인한 2012년 종료 자료. 새 5Y 일별 경로 미확보 | 2/10/30년 on-the-run 및 Bloomberg 곡선과 구별되는 공식 5Y 후속 제공 경로 조사 |
| IRL 아일랜드 | NTMA의 benchmark 종목 목록·거래 플랫폼·primary dealer 자료 확인 | 종목의 쿠폰/만기/잔액 자료이지 5Y 일별 yield 다운로드가 아님. B.3 제외 판단 유지 | 별도 secondary-market yield 원본 조사. 특정 2031년 채권을 임의로 5Y 계열로 지정하지 않음 |
| AUT 오스트리아 | OeBFA bond market 페이지, OeKB auction-agent 자료 경로 확인 | OeBFA는 UDRB와 약 10년 장기금리 연결. OeKB는 benchmark 목록·경매·strip 가격 안내; 정확한 공개 5Y yield 시계열 미확보 | benchmark 원본에 명시적 5Y yield/갱신·권리 조건이 있는지 추가 확인 |
| SVN 슬로베니아 | 중앙은행 금리 통계 범위와 Ljubljana 거래소 개별 국채 metadata 확인 | 중앙은행 interests 직접 요청 403. 거래소 개별 종목 쿠폰/가격은 표준화된 5Y yield와 다름 | API 실제 schema 및 다른 공식 만기별 수익률 파일 조사 |

## PRT: 이전 재배포 미확정 판단에 추가된 직접 근거

공식 고지: https://bpstat.bportugal.pt/avisos-legais

`Direitos de autor` 절은 BPstat에서 직접 얻은 정보를 자유롭게 이용할 수 있으며, 재현·배포는 정확하게 하고 Banco de Portugal를 출처로 표시하며, 사용자가 수정한 경우 명시하도록 안내한다. 이 원문에서 해당 절의 제3자 시리즈 예외는 확인되지 않았다. 따라서 기존 기록의 단순한 '재배포 허가 미확정'보다 강한 **포털 직접 정보의 조건부 이용허락 근거**를 확보했다. 이를 LSEG의 다른 상품이나 외부 링크 데이터 전체에 확대 적용하지 않는다. 데이터에 출처 LSEG가 있다는 사실만으로 이 포털의 허용 문구를 무시하거나, 반대로 모든 LSEG 데이터 권리가 해결됐다고 주장하지 않는다.

API 자동화 안내는 기존에 확보했다:
https://bpstat.bportugal.pt/api/media/files/scripts/menu/api.html?control_kebab=1

이번 직접 요청 결과:

- `https://bpstat.bportugal.pt/data/v1/series/?series_ids=12099457&lang=EN`: HTTP 403.
- `https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?lang=EN&series_ids=12099457`: HTTP 403.
- 법적 고지 직접 urllib 요청도 403. 고지 본문은 검색·본문 조회 서비스로 확인했으며, 이를 배포 런타임 직접 수집 성공으로 집계하지 않는다.

IGCP의 공식 July 2026 bulletin은 5/10년 PGB 및 yield curve 차트를 제공하지만 이 부분의 원출처는 Bloomberg다:
https://www.igcp.pt/sites/default/files/2026-07/BM_jul26.pdf

차트 제목과 축은 공개 수치 시계열을 확보한 것과 다르다. 차트 픽셀에서 금리를 추출하거나 IGCP의 chart permission을 BPstat 데이터에 전이하지 않았다.

## HRV: 이용허락 본문 확보, 정의와 단위는 별도 검증

공식 카탈로그 API:
https://data.gov.hr/ckan/api/3/action/package_show?id=711cb511-fbfc-49c3-a6c3-7ae40cca5bdf

- HTTP 200, 11,335 bytes; SHA-256 `9d12fa323196a3e5852a08f09261efa25027f7dd0af331b24ad418f116e24e35`.
- license_id=`open-license`, license_url=`https://data.gov.hr/id/licence/otvorena-dozvola-rh`.
- G8b resource id=`e8900684-dbb8-4193-9686-e4627925bf5a`, URL=`https://www.hnb.hr/documents/20182/1f79bc1c-dfb5-17fd-1571-cdd52a4a9619`.
- resource 설명도 월·연평균 yield to maturity를 명시한다. 카탈로그 변경일을 원본 관측일로 사용하지 않는다.

license_url은 이번에도 200이나 1,291-byte JS shell이었다. 대신 공식 관보의 **NN 67/2017-1577**, Articles 4–5 및 Annex I을 읽었다:
https://narodne-novine.nn.hr/eli/sluzbeni/2017/67/1577

관보 직접 HTTP 200, 67,335 bytes; SHA-256 `5e5a145ab525d71a976359e3eddf9afbedd32ec06cf13ecd41b351f21690ada2`.

열린 이용허락은 상업/비상업 사용, 재현·배포·제3자 제공·가공·프로그램 통합을 허용한다. 출처·dataset 링크·이용허락 표시 및 링크, 제공자가 지정한 마지막 변경일, 사용자가 한 변경의 표시가 요구되며 공식 지지처럼 표현하면 안 된다. G8b resource에 해당 라이선스가 표시되는 사실과 법령 본문을 함께 확보했다. 다른 HNB 자료 전체나 Bloomberg 원시 호가에 대한 포괄 이용허락으로 확대하지 않는다. 이번 조사로 config의 redistribution 상태를 변경하지 않았다.

방법론 원본 Bulletin 304:
https://www.hnb.hr/c/document_library/get_file?groupId=20182&uuid=4035b189-5c84-202c-a7bb-6313e55271d1

- HTTP 200, 1,697,233 bytes; SHA-256 `61142c772d6d231347f1345d4c16c2095a8cdf2a0aab3848a9a4215ea46e70da`.
- 인쇄 페이지 44는 G8b 표, 45는 방법론. 월평균은 일별 yield 단순평균, 연평균은 월평균 단순평균이다.
- 잔존 만기를 t±0.5년 구간으로 묶고 1년=360일을 가정한다.
- 국내시장 가격은 Zagreb 거래소 거래가격의 가중평균이다. 무거래일에는 가장 최근 평균가격을 공급자 자신이 유지한다. 국내 공휴일에는 일별 yield를 계산하지 않는다.
- 해외시장은 Bloomberg의 가장 최근 bid quote 기반이다. 결측 일별 값을 월평균에서 제외한다.
- 명시적 percentages per annum 문구는 LTIR 설명에 있다. 이를 별도의 G8b 국내 EUR 5Y 열의 단위 증명으로 확대하지 않는다. G8b 표 제목/열과 XLSX shared strings에서도 5Y용 명시적 단위를 확보하지 못했다.

English G8b XLSX:
https://www.hnb.hr/documents/20182/0ce7cb2f-ed3a-2b11-38d3-f1b34afc08de

HTTP 200, 77,639 bytes; SHA-256 `49c64ae3aca6b72193dd54810c5b586fd199db1de5481b72f856826b3385d55b`. 이전 조사 원본과 동일 hash다. 이전에 확인한 August 2026 말미 및 국내 EUR 5Y 결측은 새로 보충하지 않았다. Bulletin 304를 가장 최신 판본이라고 단정하지 않는다.

## NZL: 원공급자 무료 범위 확인

원공급자: https://www.nzfma.org/nzdata/

무료 목록은 지연 BKBM, transaction reports, 1/3년 swaps, OCR compound index, TWI 및 NZDFIX다. Government Bonds는 유료 실시간 데이터 목록에 있다. 이것은 지연 국채 데이터가 모든 경로에서 유료라는 증명이 아니라, 이 페이지에서 무료 국채 경로를 찾지 못했다는 뜻이다.

관리자 정의: https://www.nzfbf.co.nz/benchmarks/closing-rates/nzgs

NZGS는 현지 시장에서 거래되는 선택한 정부채 만기의 outright closing mid-yield다. 2026년 운영 지침은 Bloomberg ALLQ의 16:32 NZST 실행 가능한 양방향 호가를 입력으로 설명한다. RBNZ의 기존 5:10pm indicative close 설명과 차이가 있으므로 같은 현재 계산 과정이라고 임의로 합치지 않는다.

운영 지침:
https://www.nzfbf.co.nz/files/benchmark-documents/NZFBF-Closing-Rates---Operating-Guidelines-and-Principles-January-2026.pdf

Treasury 공식 자료 목록:
https://debtmanagement.treasury.govt.nz/investor-resources/data

이 목록은 tender history, securities outstanding, repurchases, secondary-market turnover, inflation-indexed factors, syndication 등을 제공한다. 여기서 5Y secondary yield 원본은 확인하지 못했다. RBNZ 자동 접근 조건을 피하려고 다른 URL을 통해 동일 원본을 수집하지 않았다.

## LTU: 곡선 연구의 내용과 한계

정확한 원본은 **Occasional Paper 58/2025**다. 저자별 목록 페이지의 주변 논문 번호/날짜를 해당 논문에 연결하지 않는다:
https://www.lb.lt/uploads/publications/docs/55832_371c002e2c970249464badf7dad66c40.pdf

원문은 Bloomberg의 Lithuanian/Latvian bond quotes 및 Lithuanian commercial banks의 내부 호가를 사용하여 NSS를 일별로 추정하고 합성 10년 benchmark를 연구한다. 공개 경매 정보는 primary/secondary spread 연구에도 사용한다. 연구 결과와 공개 최신 5Y 시계열은 다르며, 연구자가 사적 입력으로 합성할 수 있다는 것을 프로젝트의 보간 허가로 취급하지 않는다. 이번 조사에서는 공개 갱신형 5Y 관측값/모델 계수 다운로드를 확보하지 못했다. 원본 PDF의 직접 요청은 403이었고 내용은 본문 조회 서비스로 확인했다.

## BGR: 실제 workbook 재확보

https://www.bnb.bg/bnbweb/groups/public/documents/bnb_download/gssm_2026_06_a1_en.xlsx

HTTP 200, 568,043 bytes; SHA-256 `6765dd163c14ba1c9c57c98a41ca13c29a02c43b7becb6c3df6d402d6d40bca5`.

16개 sheet를 확인했다. PRI-0은 경매 결과, PRI-2/3은 유통 종목/쿠폰, PRI-4는 경매 판매 내역의 가격·annual yield다. Sec-5의 1–3/4–7/8일 이상 열을 1/3/5년 국채 만기로 읽지 않는다. 일부 secondary sheet는 그림 또는 빈 cell 형태여서 openpyxl의 셀만으로 관측값이 없다고 단정하지 않는다. 검증된 정확한 유통시장 고정 5Y 시계열은 여전히 미확보다. 이미지에서 숫자를 추정하지 않았다.

August bulletin의 공식 발표(2026-09-30):
https://www.minfin.bg/en/news/2026-09-30/13523

catalogue: https://www.minfin.bg/en/statistics/20

직접 catalogue 요청은 403. 본문 조회 서비스가 보여주는 catalogue는 오래된 게시물 범위여서 이를 현재 bulletin 미존재의 근거로 사용하지 않는다.

## DNK / IRL / AUT / SVN: 범위가 다른 자료의 제외 근거

- DNK 현재 금융시장 목록 `https://m.statbank.dk/Tables/3448`: 직접 200. MPK100 `https://m.statbank.dk/TableInfo/MPK100`: 직접 200, 27,220 bytes, SHA-256 `c6301c92f5bf0597e662a4655188d2e64e8f75d112b49e30a86e0fa8b58c88b1`. Country와 연도(1989–2025)만 선택 축이며 만기는 미지정이다. 일별 정확한 5Y 후보로 승인하지 않는다.
- DNK `https://www.nationalbanken.dk/media/q5cf5y2l/central-government-borrowing-and-debt-2025.pdf`: 2/10/30년 on-the-run 변화 및 fitted zero-coupon yield spreads를 논의하나 곡선 출처는 Bloomberg다. 공식 보고서에 차트가 있다는 사실만으로 재배포 가능한 국별 일별 5Y 파일을 확보한 것은 아니다.
- IRL `https://www.ntma.ie/business-areas/funding-and-debt-management/government-securities/government-bonds`: benchmark/non-benchmark ISIN·쿠폰·만기 및 거래 플랫폼/primary dealer 정보. 쿠폰은 yield가 아니다. 잔액 보고서의 일별 공개를 yield의 일별 공개로 취급하지 않는다. ISEQ Bond Index Services가 2019년 11월 종료됐다는 설명도 있으므로 그 지수를 현재 자료로 추정하지 않는다.
- AUT `https://www.oebfa.at/en/budget-und-schulden/anleihenmarkt.html`: UDRB와 약 10년 장기금리 제공 설명을 재확인. `https://www.oekb.at/en/capital-market-services/our-range-of-data-knowledge-creates-an-advantage/data-on-austrian-government-bonds.html`: benchmark 목록·경매 결과·strip의 이론적 발행가격 및 개별 data service 안내. 현재 5Y yield 다운로드 확인과 구분한다.
- SVN `https://www.bsi.si/en/interest-rates`: 예금/대출/정책금리/€STR/법정 관련 금리 및 convergence LTIR가 통계 범위에 있다. `https://www.bsi.si/en/api-documentation`는 interests에 날짜 필터를 안내하지만 5Y를 명시하지 않는다. `https://api.bsi.si/interests?date=2026-09` 직접 요청은 403이며 응답 schema 검증은 미완료다.
- SVN 거래소 `https://ljse.si/en/papir-311/310?isin=SI0002103990`는 개별 RS84 종목의 만기·쿠폰·가격 거래정보다. 2030년 만기 채권의 쿠폰을 5Y yield로 사용하거나 가격에서 별도 YTM을 계산하는 변경은 하지 않는다.
- 공통 ECB `FM.M.U2.EUR.4F.BB.U2_5Y.YLD` 및 YC의 5Y는 Euro area 범위다. 미연결 유로 국가에 같은 값을 복제하는 대체 소스로 승인하지 않는다.

## 변경 범위와 남은 상태

신규 연결 0. 기존 18개국 연결/9개국 미연결 유지. 이번에 원문 근거가 강화된 우선 후보는 PRT와 HRV다. 연구 문서 외 코드/설정/출력 수치/게이트는 수정하지 않았다. 문서 변경의 diff 검사를 수행하며 코드 테스트는 재실행하지 않는다. 직접 접근 실패를 우회하지 않았고, 검색 서비스의 조회를 배포 수집 성공으로 계산하지 않았다.

## 정의 후속 확인

[포르투갈·크로아티아 5년물 정의 후속 조사](2026-10-05-five-year-definition-followup.md)를 참조한다. 크로아티아의 360일 설명은 영문 근거이며, 현행 현지어 웹 방법론과 Bulletin 308에는 365일이 표시되어 상충한다. 어느 정의가 유효한지는 미확정이다. 포르투갈은 공식 역사 표의 단위·집계 및 원천 설명을 추가 확보했으나 현행 시리즈의 전체 산출 계약은 미확정이다.

[미연결국 대체 경로 탐색](2026-10-05-unconnected-alternative-routes.md): 오스트리아 공식 5년 benchmark와 동일 ISIN의 실제 YTM 필드를 확인했지만 사이트 자동수집·재현 조건 때문에 연결하지 않았다. 리투아니아 2026Q2 PDF에는 잔존 만기 표도 있으며, 그 전체 산출 계약은 추가 확인이 필요하다. 뉴질랜드는 2025년 제공 방식 변경, 포르투갈은 공식 `obs_last_n` 필터를 확인했다.
