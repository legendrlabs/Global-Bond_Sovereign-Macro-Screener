# 미연결 9개국: 거래소·원공급자·공식 API 확대 탐색

조사일: 2026-10-05 KST. 사용자의 “이곳저곳” 확대 조사 요청에 따라 기존 중앙은행·재무부 경로 외에 거래소, 시장 원공급자, 공식 통계 API, 발행기관 자료와 benchmark 관리자 방법론을 탐색했다.

Exa 검색 30회 × 요청 결과 5개 = 150개 결과 슬롯. 실제 반환 URL도 150개이며 중복 제거하면 127개다. 이 숫자는 다운로드 성공이나 데이터 계약 검증 완료 수가 아니다. 후보별 공식·원공급자 URL 18개는 본문/JSON 추출까지 추가 확인했다. 일반 HTTP로 요청한 4개 URL은 모두 ReadTimeout이었다. 검색 서비스의 추출과 실제 프로그램에서 사용할 다운로드 성공을 구분한다.

[검색 URL·질의 목록](2026-10-05-wide-route-inventory.json). 원자료 수치·거래소 보고서 원본은 저장소에 첨부하지 않는다.

## 이번에 새로 좁힌 경로

| 국가 | 확대 조사 결과 | 현재 판단 |
|---|---|---|
| SVN | MTS Slovenia fixing에 개별 채권 Mid Yield, 날짜, 만기, Duration 필드가 있음 | 유통시장 후보. 잔존 5년 국가 시리즈·최신 자동접근·재배포는 미검증 |
| LTU | Nasdaq Baltic 국채 목록에 Ask/Bid Yield와 만기·거래량 필드가 있음 | 개별 호가. 원래 5년 발행물과 현재 잔존 5년을 구분해야 함 |
| DNK | Nasdaq Copenhagen의 평균 수익률 계산 방법론을 확인 | 3년 초과~5년 이하 구간이며 큰 그룹에 정부 외 기관 채권도 포함. 정확한 5년물 대체 불가 |
| IRL | CSO FIM09·FIM05 JSON-stat 원문 스키마 확인; MTS 채권 목록과 Euronext 만기 구간 YTM도 확인 | CSO 두 테이블은 5년 국채가 아님. 시장 후보는 범위·권리 미검증 |
| NZL | NZFBF closing rate 방법론과 NZFMA 무료/유료 구분 확인 | 정부채 close 원천을 명확히 함. 무료 delayed 목록에 정부채가 있다고 확대 해석하지 않음 |
| AUT | Vienna Exchange의 동일 benchmark ISIN 가격 화면, OeKB strips 안내 확인 | 가격·세무용 이론가격을 수익률 관측값으로 바꾸지 않음 |
| PRT | IGCP July 2026 Bulletin의 secondary-market 5/10년 그래프 확인 | Bloomberg 원천 그래프. BPstat 특정 시리즈 승인 범위와 별개 |
| BGR | BNB Q2 2026 PDF secondary-market 절의 필드 확인 | 거래량·구성 자료. 경매 yield를 유통시장 yield로 대체하지 않음 |
| HRV | HANFA·ZSE·HNB metadata·공식 개방 카탈로그까지 확대 검색 | G8b 5년 열의 직접 단위 근거·360/365 상충 해소 자료는 새로 확보하지 못함 |

새 collector 연결은 **0개**다. 기존 **18개국 연결 / 9개국 미연결**, scoring, 국가별 정의, stale·unit·tenor·definition, public-output 및 Adjusted 게이트를 유지한다. 이 변경은 연구 문서만 추가한다.

## SVN: MTS의 개별 채권 fixing

- [MTS Slovenia fixing](https://www.mtsdata.com/content/data/public/rsl/fixing/)
- [같은 시장의 bond list](https://www.mtsdata.com/content/data/public/rsl/anagraph/index.php)
- [MTS Fixings 설명](https://www.mtsmarkets.com/en/mts-fixings)
- [MTS market-data 계약 문서 안내](https://www.mtsmarkets.com/en/data-analytics/market-data-documentation)

fixing 본문에 Date, Bond Code, Maturity, Mid Price, Mid Yield, Duration이 있다. H1100 (CET) snapshot이며 이번 검색 추출의 날짜는 2026-09-22였다. 10월 5일의 최신 관측으로 취급하지 않는다. 일반 HTTP 요청은 ReadTimeout으로 끝나 직접 응답 해시·현재 fixing 날짜를 검증하지 못했다.

시장 운영자의 설명은 MTS Cash reference price에 11:00 / 16:00 CET 시점과 firm quotes·executed trades 원천을 안내한다. 일반 제품 설명만으로 특정 Slovenia snapshot의 모든 계산·결측 처리 계약을 확정하지 않는다. 화면에 표시된 Mid Yield를 다른 국가의 constant-maturity 5년 시리즈와 동일시하지 않는다.

MTS의 계약 안내는 실시간뿐 아니라 delayed, reference price/data, snapshot 및 파생 데이터도 별도 라이선스 대상으로 연결한다. 공개 fixing 화면을 읽을 수 있다는 사실만으로 자동수집·배포 권한을 승인하지 않는다. 이 안내 자체가 해당 public URL의 모든 사용을 금지한다는 확정 판정도 하지 않는다. 필요한 것은 public fixing에 적용되는 구체적인 허용 조건이다.

후속: 정확한 국가 5년 benchmark 선정 계약, 실제 관측일의 최신성, 공식 공개 파일/시계열 경로, 해당 경로의 자동접근 및 재배포 조건을 확인한다. 가장 가까운 만기 채권을 임의로 선택하거나 가격에서 YTM을 새로 계산하지 않는다.

## LTU: 거래소에는 yield 열이 있지만, 이름이 현재 만기를 뜻하지 않음

- [Nasdaq Baltic bond list](https://nasdaqbaltic.com/statistics/en/bonds)
- [개별 정부채의 historical 화면 예](https://www.nasdaqbaltic.com/statistics/en/instrument/LT0000630105/historical?date=2026-07-31)
- [별도 2032 만기 정부채 trading 화면](https://nasdaqbaltic.com/statistics/en/instrument/LT0000612012/trading)
- [공식 경매표](https://nasdaqbaltic.com/statistics/en/auctions_vln/govdebt)

국채 목록의 열에 Ask Yield, Bid Yield, 만기, 발행일, 거래량, 마지막 clean/dirty 가격이 있다. 이번 추출에는 Lithuanian Gov. 5Y Bond 65008 / LTGB23027B의 발행일 2022-07-13과 만기 2027-07-13이 표시됐다. 따라서 이름의 5Y는 현재 잔존 5년의 증거가 아니다. 그 행의 yield/price 필드는 '-'였다.

목록의 Last trading day 열은 미래 날짜도 포함하므로 최근 체결일로 사용하지 않는다. 일부 다른 행에 호가가 있어도 미관측 국가 5년 값을 대체하는 근거가 되지 않는다. historical 화면에는 Open/High/Low/Last yield 열 이름이 있지만, 이번 조사로 채워진 현행 5년 daily history를 확보했다고 집계하지 않는다.

경매표의 Average weighted yield of approved bids는 secondary-market close와 구분한다. 앞선 재무부 명목/잔존 만기 PDF와도 별도 계약이다. 후속은 잔존 5년 시리즈/benchmark의 공식 정의와 실제 호가·체결 데이터의 날짜·누락 처리·다운로드·권리 검증이다.

## DNK: Nasdaq 평균 수익률의 정확한 범위

- [현재 Average Bond Yield 안내](https://www.nasdaq.com/european-market-activity/fixed-income/average-bond-yield)
- [January 2016 yield calculation guidelines, §6 / 문서 17쪽](https://www.nasdaq.com/docs/guidelines-for-yield-calculation-january-2016.pdf)

확인한 방법론의 큰 그룹 중 하나는 Danish government bonds와 Danmarks Fiskeribank, Færøernes Realkreditinstitut를 함께 포함한다. 하위 구간은 ≤3년, >3~≤5년, >5~≤15년 등이다. 시리즈별 유통잔액의 시장가치로 평균 가중치를 계산한다. 역사 가격/수익률 시리즈는 평균에서 제외하고, 미대표 또는 비어 있는 하위 그룹은 0으로 표시한다고 설명한다.

따라서 5년 상한 구간, 그룹 평균 또는 표시 0을 현행 정부 5년 benchmark 관측으로 해석하면 안 된다. 이 방법론은 2016년 문서이므로 현재 모든 제품 정의가 그대로라는 결론도 내리지 않는다. 새로운 정의 문서와 실제 report 파일이 있어야 현재 계약을 확정할 수 있다. 이번 직접 Nasdaq 안내 요청은 ReadTimeout이었다.

기존 DNRENTM의 2012-11 종료 시리즈나 mortgage·swap을 대체 입력으로 연결하지 않는다. 새 검색에 나온 DNVPDKS는 증권 잔액/보유 등 자료이며 만기 구간이 있어도 5년 yield 확보를 뜻하지 않는다.

## IRL: 공식 API 두 테이블을 내용으로 제외

| API | 실제 스키마 | 기간 dimension | 결론 |
|---|---|---|---|
| FIM09 JSON-stat 1.0 | 중앙은행 재할인율, Exchequer bills 평균 yield, building-society mortgage rate | 1975M01~2008M03, 399개월 | 특정 5년 국채 없음 |
| FIM05 JSON-stat 2.0 | 주가 지수 및 무역가중 실효환율 지수 | 1974M01~1998M12, 300개월 | 정부채 yield 없음 |

- [FIM09 원문 API](https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/FIM09/JSON-stat/1.0/en)
- [FIM09 공식 카탈로그 resource / CC-BY-4.0 표시](https://data.gov.ie/dataset/708eea1b-7450-4e33-9f7a-22d487de6af7/resource/a07d289f-05b1-42af-8e9b-e4a6bcbb67b2)
- [FIM05 원문 API](https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/FIM05/JSON-stat/2.0/en)
- [CSO 공식 API 안내](https://data.cso.ie/)

JSON 원문을 파싱해서 dimension·category를 확인했다. 기간의 마지막 label과 마지막 유효 관측일은 구분한다. FIM09 일반 요청은 ReadTimeout이므로 프로그램 수집 성공으로 집계하지 않는다. 카탈로그의 open licence가 자료 정의의 불일치를 해결하지 않는다.

시장 경로:
- [NTMA 현재 채권 안내](https://www.ntma.ie/business-areas/funding-and-debt-management/government-securities/government-bonds)
- [MTS Ireland bond list](https://www.mtsdata.com/content/data/public/irl/anagraph/index.php)
- [Euronext Ireland GR factsheet](https://live.euronext.com/sites/default/files/documentation/index-fact-sheets/Euronext_MTS_EGB_Ireland_GR_Index_Factsheet.pdf)
- [검색에서 반복 반환한 2019-10-03 Daily Bond Index Report](https://www.ntma.ie/uploads/general/Daily_Bond_Index_Rpt_2019-10-03.pdf)

NTMA와 MTS 목록에서 2031-10-18 만기의 IE00BMQ5JL65를 확인했다. 이는 정확한 benchmark/YTM 시리즈 확보가 아니라 개별 채권 식별 근거다. outstanding report의 일별 잔액을 일별 yield로 혼동하지 않는다.

Euronext factsheet는 3~5년, 5~7년 등 구간별 Yield to Maturity 열을 포함한다. 정확한 5년 관측값이 아니다. 사전 서면 허가 없이 재배포·복제할 수 없다는 문서 고지도 확인했다. 시장 수치나 원본 factsheet를 저장소에 복제하지 않으며, 해당 수치를 public summary에 넣지 않는다. 반복 반환되는 2019 보고서를 최신 2026 자료로 처리하지 않는다.

## NZL: benchmark 원천과 무료 제공 범위를 구분

- [NZFBF closing-rate 방법론 안내](https://www.nzfbf.co.nz/benchmarks/closing-rates/)
- [NZFMA 데이터 제공 범위](https://www.nzfma.org/nzdata/)
- [NZFMA 무료 search 안내](https://www.nzfma.org/nzdata/search)
- [NZDM 자료 목록](https://debtmanagement.treasury.govt.nz/investor-resources/data)
- [Stats NZ Infoshare 안내](https://www.stats.govt.nz/tools/stats-infoshare/)

NZFBF는 적격 도구·tenor의 close mid-rate를 사업일 16:32 NZST의 Bloomberg ALLQ two-way quotation에서 얻는다고 설명한다. NZGS는 정부 발행물의 선택된 만기에 대한 outright yield다. 문서가 사용하는 시간대 표기를 그대로 기록하며 별도의 현재 UTC 변환이나 실제 공개 시차를 임의로 생성하지 않는다.

NZFMA의 무료 24시간 지연 목록에는 BKBM, bank-bill transaction report, 일부 swap, OCR compound index가 있다. 정부채를 포함하는 유료 realtime 목록과 다르다. 이 목록만으로 모든 delayed 정부채 이용이 금지된다고 단정하지 않지만, 정부채 무료 제공·재배포 승인의 증거로는 부족하다. benchmark administrator의 감독기관 licence와 사용자의 데이터 재배포 권한도 다른 것이다.

NZDM의 XLSX 목록은 tender history·발행잔액·repurchase·IIB factor 등을 안내한다. secondary-market 5Y close 파일을 새로 확보한 것은 아니다. Stats NZ의 Export Direct 지원도 확인했으나 정확한 정부채 5년 identifier는 찾지 못했다. 지원되는 다운로드 기능과 필요한 시리즈 존재를 구분한다.

## AUT / PRT / BGR / HRV의 추가 판별

**AUT**
- [Vienna Exchange: 기존 OeKB benchmark ISIN AT0000A2NW83의 가격 화면](https://www.wienerborse.at/en/market-data/bonds/quote/?cHash=20e4bb996c9e621d96408c168a47b38d&ID_NOTATION=322041840&ISIN=AT0000A2NW83)
- [OeKB strips와 이론 발행가격 안내](https://www.oekb.at/en/capital-market-services/government-bond-and-atb-auctions/stripping-of-government-bonds-of-the-republic-of-austria.html)

가격·bid/ask·historical 화면 발견과 직접적인 YTM 시리즈 확보는 다르다. OeKB의 strips 이론 발행가격은 세무 목적의 계산값이며 secondary-market 5년 수익률 관측으로 대체하지 않는다. 기존 UDRB의 혼합 만기 정의 및 거래소 자료 권리 과제는 그대로다. 비공식 Bonds API 후보도 검색에 나타났지만 원천·키·권리 계약을 검증하지 않아 연결하지 않았다.

**PRT**
- [IGCP July 2026 Monthly Bulletin](https://www.igcp.pt/sites/default/files/2026-07/BM_jul26.pdf)

secondary-market 절의 5/10년 PGB yield 그래프는 % 단위이며 Bloomberg source 표시가 있다. 그래프의 픽셀·축·선에서 관측 숫자를 만들지 않는다. July 발행물을 October 최신값으로 사용하지 않는다. 이 상품은 앞서 승인한 직접 BPstat 12099457 범위에 추가하지 않았다. BPstat monthly 12099462와 daily 10년 12099459 검색 결과도 승인된 daily 5년 series를 확장하는 근거가 아니다.

**BGR**
- [BNB Q2 2026 영어 원본 PDF](https://www.bnb.bg/bnbweb/groups/public/documents/bnb_publication/gssm_2026_06_en.pdf)

secondary-market 절은 frozen securities의 volume/structure, OTC·MTF E-Bond·BSE 거래량을 설명한다. 거래량에는 매매·repo·고객 거래가 포함된다. 이 내용을 특정 5년 secondary yield table로 해석하지 않는다. 초반 경매의 가격·yield와 후반 거래량 절을 섞어 시계열을 만들지 않는다. PDF의 2026년 BGN 발행분 환산 설명도 현재 EUR 통화 설정을 변경할 이유가 아니다. Bangladesh·India의 유사 제목 결과는 나라 불일치로 제외했다.

**HRV**
- [HNB Standard presentation format 카탈로그](https://data.gov.hr/ckan/dataset/standardni-prezentacijski-format)
- [HNB 현행 G8b 방법론](https://www.hnb.hr/en/statistics/statistical-data/general-government/general-government-debt)

카탈로그의 마지막 SPF가 2022-11이라는 안내가 검색에서 확인됐으며 현행 5년 daily 대체로 쓰지 않는다. ZSE·HANFA·HNB securities metadata까지 검색했으나 G8b 5년 열의 직접적인 % 단위 근거와 언어별 360/365 상충 해소 증거는 이번에도 확보하지 못했다. 해당 정의를 승인하거나 다른 HNB resource에 G8b의 라이선스를 확장하지 않는다.

## 직접 접근 기록

기본 GET, 인증 없이 connect/read timeout 5/15초로 각 URL을 한 번 요청했다. 네 요청 모두 ReadTimeout이어서 성공 응답 bytes·SHA를 기록하지 않았다. 실패를 통계 부재나 사이트 전체 금지로 해석하지 않고, 다른 host·비공개 endpoint·자격 증명으로 우회하지 않았다.

- CSO FIM09 JSON-stat URL
- Nasdaq Denmark Average Bond Yield URL
- MTS Slovenia fixing URL
- NTMA Government Bonds 안내 URL

위 URL들은 본문의 링크와 동일하다. 호출 재시도나 오래된 검색 수치를 최신 입력으로 채우는 처리는 없다.

## 다음 탐색 우선순위

1. SVN MTS public fixing의 적용 이용 조건, 정확한 5년 benchmark/시리즈, 현행 원문 접근.
2. LTU 거래소의 잔존 만기별 공식 지표 또는 수치 원본, 비어 있는 호가·관측일·권리 계약.
3. PRT 이미 발견한 BPstat direct 5년 series의 정의 계약과 안정적인 실제 수집.
4. IRL 정확한 benchmark의 current daily YTM 원본. 과거 보고서와 잔액·구간 지수는 제외.
5. HRV 단위 및 언어별 방법론 상충. DNK/AUT/NZL/BGR는 현행 5년 관측·접근·권리를 함께 만족하는 새 경로.

문서만 변경했으므로 코드 테스트는 재실행하지 않는다. 승인된 PRT·HRV scoped publication gate와 앞선 98개 테스트 통과 결과는 [이전 구현 기록](2026-10-05-publication-gate-update.md)에 있다.

