# 5년물 정의 후속 조사: 포르투갈·크로아티아

조사 시점: 2026-10-04~05 UTC / 2026-10-05 KST. 연구 기록만 변경했다. 수집기, 국가별 정의, scoring, freshness, public-output 및 재배포 게이트는 변경하지 않았다. 신규 연결은 0개이며 미연결 9개국은 그대로다.

이 문서는 [9개국 전체 조사](2026-10-05-nine-country-sweep.md)의 후속이다. 특히 기존 영문 HNB 방법론의 360일 설명은 아래 언어별 상충 근거와 함께 읽어야 한다.

## 포르투갈: 역사 자료의 산출 원천과 단위 확인

공식 2008년 6월 통계 부록:
https://www.bportugal.pt/sites/default/files/anexos/pdf-boletim/suplemento-2-2008.pdf

3.3절은 국채의 잔존 만기에 따른 일별·월별 수익률을 공개한다고 설명한다. 각주 13은 Reuters가 MEDIP 거래를 기반으로 계산·발표한다고 명시한다. 이는 공식 기관이 설명한 당시 원천이다. 현재 LSEG 시리즈의 알고리즘이 그대로라는 증거는 아니다.

공식 2020년 2월 통계 Bulletin, 표 B.10.3.3 / 인쇄 116쪽:
https://www.bportugal.pt/sites/default/files/anexos/befev20_en.pdf

표에서 확인한 계약 요소:

| 요소 | 공식 표에 표시된 내용 | 한계 |
|---|---|---|
| 상품 | 고정금리 국채 | 특정 대표 채권 선정 규칙 미확인 |
| 만기 | 잔존 만기 2·3·4·5·7·10년 | 정확한 5년 보간 또는 구간 처리 규칙 미확인 |
| 단위 | % | 현행 API 응답 단위와 별도 대조 필요 |
| 집계 | 단순평균 | 표에 월별·일별 값이 함께 있으므로 모든 빈도의 산출 알고리즘으로 확대하지 않음 |
| 원천 | Reuters | 현행 LSEG 정의와 동일하다고 단정하지 않음 |

두 PDF의 직접 urllib 다운로드는 HTTP 403이었다. 공식 URL의 검색 서비스 추출 본문으로 해당 절·각주·표를 확인했다. 직접 원본 바이트나 PDF SHA를 확보했다고 집계하지 않는다. 2020 자료는 과거 관측값이며 최신 입력이나 수집 실패 대체 캐시로 쓰지 않는다.

현행 조사 후보:

- 일별 series 12099457: 이전 직접 성공 응답 기록이 존재하나 이후 재요청은 403. 이전 성공을 현재 연결 성공으로 집계하지 않는다.
- 월별 series 12099462: https://bpstat.bportugal.pt/serie/12099462 — 제목에서 잔존 5년 고정금리 국채 확인. 이번에 현행 관측값 다운로드는 완료하지 못했다.
- 방법론 후보: https://bpstat.bportugal.pt/conteudos/metainformacao/472 — 검색 추출은 제목 수준이며 직접 요청 403. 본문 검증 미완료.
- 공식 표 후보: https://bpstat.bportugal.pt/conteudos/quadros/484

BPstat 재이용 조건은 앞선 9개국 조사에서 확보했다. 이번 남은 조건은 현행 응답 확보와 빈도·보간/대표채권·만기 구간·단위 계약 확인이다. 역사 자료의 Reuters 원천만을 이유로 앞서 확보한 BPstat 재이용 근거를 무효화하지 않는다. 다른 LSEG 제품에 BPstat 조건을 확대하지도 않는다.

## 크로아티아: 공식 영문과 현지어의 연 기준 상충

현행 공식 방법론:

- 영문: https://www.hnb.hr/en/statistics/statistical-data/general-government/general-government-debt
- 현지어: https://hnb.hr/statistika/statisticki-podaci/opca-drzava/dug-opce-drzave

둘 다 G8b에서 잔존 만기를 t±0.5년 구간으로 묶는 방법을 설명한다. 영문은 1년을 360일, 크로아티아어는 365일로 설명한다. 두 웹 방법론의 표시 수정일은 2023-05-10이다. 날짜만으로 어느 설명이 유효한지 정할 수 없다.

같은 차이를 Bulletin에서도 확인했다:

| 자료 | 확인한 연 기준 | 위치 |
|---|---|---|
| 영문 Bulletin 304 | 360일 | 인쇄 45쪽 방법론 |
| 크로아티아어 Bulletin 308 | 365일 | 인쇄 47쪽 방법론 |

Bulletin 308 공식 원본:
https://www.hnb.hr/c/document_library/get_file?groupId=20182&uuid=ec396dd8-2b80-fde1-bdfe-ecc9f0556e35

따라서 이번 증거는 언어·자료 간 정의 상충이다. 실제 계산이 시간에 따라 360→365일로 바뀌었다거나 영문이 오역이라고 단정하지 않는다. 5년 구간 평균을 constant-maturity 5년으로 승격하지 않는다.

### 두 언어 XLSX 확보 및 관측 범위 대조

- 영문 G8b: https://www.hnb.hr/documents/20182/0ce7cb2f-ed3a-2b11-38d3-f1b34afc08de
- 현지어 G8b: https://www.hnb.hr/documents/20182/1f79bc1c-dfb5-17fd-1571-cdd52a4a9619

인증 없는 일반 다운로드로 두 파일 모두 HTTP 200을 확보했다. 각각 `ENG`, `HRV` 시트의 7행에서 외국시장 USD, 외국시장 EUR, 국내시장 EUR의 만기별 열을 확인했다. EUR 외국시장 5년은 Q열, 국내시장 5년은 AJ열이다. 연도는 이후 월 행에서 생략될 수 있으므로 날짜를 읽을 때 연도 문맥이 필요하다.

두 파일 모두 관측 월은 2026년 8월까지다. 마지막 월의 두 EUR 5년 셀을 대조했으며 두 언어 파일 간 일치했다. 이는 전체 역사 시계열 동일성 검증이나 방법론 상충 해소를 뜻하지 않는다. 국내 EUR 5년에는 실제 `-` 결측 구간이 있으며 다른 만기로 보완하지 않는다.

XLSX의 값 있는 셀 형식은 General 또는 일반 소수 표시다. 5년물 단위를 명시한 % 서식·셀 주석은 확보하지 못했다. LTIR에 대한 % 설명이나 수치 크기를 근거로 5년 열의 단위를 확정하지 않는다. 공식 단위 근거와 360/365 설명의 해소가 계속 필요하다. 재이용 조건은 앞선 조사에서 확인한 정확한 G8b 카탈로그와 개방 라이선스 범위로 한정한다.

### 직접 확보한 바이트의 증거

| 원본 | bytes | SHA-256 |
|---|---:|---|
| 영문 G8b XLSX | 77,639 | `49c64ae3aca6b72193dd54810c5b586fd199db1de5481b72f856826b3385d55b` |
| 현지어 G8b XLSX | 83,373 | `8239a191f31cccd9570ccf88c4b8d38b66b739a6de0c4fa50fd56d1e89e5923e` |
| 크로아티아어 Bulletin 308 | 1,789,044 | `5755119cce29f1e7889a775b99c1347c8ae943475461a20dab0d851ee666db56` |
| 영문 Bulletin 304 | 1,697,233 | `61142c772d6d231347f1345d4c16c2095a8cdf2a0aab3848a9a4215ea46e70da` |

## 덴마크·아일랜드 및 국가 간 경로 교차 확인

DFBF 공식 benchmark 목록과 과거 자료:
https://dfbf.dk/dfbf-benchmarks/
https://dfbf.dk/dfbf-benchmarks/previous-data/

확인한 목록은 CIBOR, CITA, SWAP, Tom/Next 관련 자료다. 5년 SWAP은 국채 5년물이 아니므로 후보에서 제외한다. 이 결과는 모든 덴마크 공식 자료의 부재 판정이 아니다.

Riksbank 공식 API 시리즈 목록:
https://www.riksbank.se/en-gb/statistics/interest-rates-and-exchange-rates/retrieving-interest-rates-and-exchange-rates-via-api/series-for-the-api/

외국 5년물 Group 99에는 미국·일본·독일·네덜란드·프랑스·영국·유로 지역 계열이 표시된다. 현재 미연결 9개국은 해당 목록에 없다. 덴마크 10년물을 5년물로 대체하거나 존재가 검증되지 않은 5년 시리즈 코드를 만들지 않는다.

아일랜드 추가 검색은 과거 중앙은행 통계 Bulletin으로 이어졌다. 2011년 공식 Quarterly Bulletin 후보는 다음과 같지만 현행 5년물 자동 수집 경로는 확보하지 못했다:
https://www.centralbank.ie/docs/default-source/publications/quarterly-bulletins/qb-archive/2011/qb1-2011.pdf?sfvrsn=6

현행 시리즈의 종료 시점·중단 공지는 이번 증거로 확정하지 않는다. 과거 자료를 최신 입력으로 사용하는 일도 없다.

## 다음 확인 사항

1. PRT: 현행 API에서 날짜·빈도·단위와 대표채권/보간/만기 구간 규칙 확보. 역사 표의 설명은 참고 근거로만 유지.
2. HRV: 5년물 단위의 직접 공식 근거와 영문 360일/현지어 365일 상충 해소. 국내 EUR·외국시장 EUR를 구분.
3. DNK·IRL: 이미 배제한 swap·10년물·과거 종료 자료의 반복 검색 대신 현행 공개 국채 통계의 후속 제공 경로 탐색.

이번 변경은 문서뿐이므로 실행 테스트는 재실행하지 않았다. 문서 diff의 공백 오류와 변경 범위를 검사했다. 기존 구현의 88개 테스트 통과 기록은 이전 구현 검증 결과이며 이번에 새로 실행한 결과가 아니다.
