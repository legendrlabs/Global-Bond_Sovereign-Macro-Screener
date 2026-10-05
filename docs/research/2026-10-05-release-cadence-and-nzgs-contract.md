# PRT 게시 주기 및 NZGS 산출·접근 계약 보강

조사 시점: 2026-10-05 17시 이후 KST. 연구 문서만 변경했다. 신규 연결 0개, 기존 18개 연결 / 9개 미연결 유지. scoring·수집기·국가별 정의·freshness·publication gate는 변경하지 않았다.

## PRT: 일별 관측과 게시 주기 구분

공식 2026 게시 일정:
https://bpstat.bportugal.pt/api/media/files/Calendario_BPstat_dominio.html

일별 secondary-market 영역은 매주 첫 영업일 및 매월 둘째 영업일에 업데이트한다고 안내한다. 일별 관측 시계열이라는 표시는 매 영업일 게시된다는 뜻이 아니다. 향후 수집 계약에서 observation date, provider update time, collection time, 예정 게시일을 각각 보존할 근거다. 이번에 stale 한도나 실패 시 과거 캐시 대체 규칙을 바꾸지는 않았다.

공식 수정 일정:
https://bpstat.bportugal.pt/api/media/files/calendario-revisoes.html

Mercado Secundário 수정은 제공자 LSEG의 관행을 따른다고 설명한다. 이를 5년물 대표채권·보간 알고리즘의 증거로 확대하지 않는다.

월별 후보 [12099462](https://bpstat.bportugal.pt/serie/12099462)의 공식 검색 추출에서 월평균 잔존 5년 고정금리 국채 설명, % 표시, 2026-10-02 갱신 및 마지막 관측 2026년 8월을 확인했다. 해당 추출의 관측 시점과 2026 일정표가 가리키는 월별 게시 계획을 동일시하지 않는다. 직접 최신 API 수집 성공으로도 집계하지 않는다. 기존 승인된 publication scope는 일별 12099457이므로 월별 12099462를 자동 추가하지 않는다.

[메타정보 472](https://bpstat.bportugal.pt/conteudos/metainformacao/472)는 Exa에서 제목만 추출됐고 다른 공식 검색 도구에서는 JavaScript 필요 메시지가 나왔다. 본문 방법론은 미확보다. [방법론 목록](https://bpstat.bportugal.pt/documentacao-metodologica)에서 해당 항목의 존재는 확인했지만 목록 자체로 상세 계약을 채우지 않았다. 이전 실패한 직접 API URL은 이번에 반복 요청하지 않았다.

## NZL: 데이터 제공·재이용·자동 접근을 구별

[RBNZ B2 페이지](https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/wholesale-interest-rates)는 통계를 복제·배포·가공할 수 있다는 안내와 copyright 조건 링크를 제공한다.

[현재 이용 조건](https://www.rbnz.govt.nz/about-our-site/terms-of-use)은 은행 저작물의 정확한 재현 및 출처 표시를 조건으로 재이용을 설명하고, 제3자 저작물에는 해당 허용이 확장되지 않는다고 명시한다. 제3자가 원천 제공자라는 사실만으로 저작권 표시 여부를 확정하지 않는다. 반대로 B2의 재이용 안내만으로 NZFMA의 모든 원자료 이용허락을 확보했다고도 단정하지 않는다. 현재 pending 상태를 유지한다.

별도의 자동 접근 규정은 공공 검색엔진 예외 또는 RBNZ의 사전 서면허가를 요구한다. 허용된 bot에 대해 하루 7,000 / 시간당 291 요청 상한도 명시한다. 이 상한은 사전허가 없이 요청해도 된다는 허용이 아니다. 이번에는 공개 문서의 검색 서비스 추출을 검토했고 RBNZ XLSX를 직접 자동 수집하거나 allow-list 폼을 제출하지 않았다.

## NZGS: 정상 산출 및 장애 시 규칙

공식 [NZGS Closing Rate Methodology, January 2026](https://www.nzfbf.co.nz/files/benchmark-documents/NZGS-Closing-Rates---Methodology-January-2026.pdf), 특히 PDF 3~5쪽의 2.2~2.7절을 검토했다.

| 계약 요소 | 방법론에서 확인한 내용 | 스크리너 적용 한계 |
|---|---|---|
| 입력 | 승인된 price-maker의 Bloomberg ALLQ 양방향 호가 | 원자료 다운로드·재배포 권한 아님 |
| snap | 16:32 NZT, 그 전 16:15~16:30 구간의 추가 snap 및 14:00 snap | RBNZ의 17:10 설명과 자동 동일시하지 않음 |
| 정상 계산 | 유효 bid 평균과 유효 offer 평균의 평균 | 개별 security/tenor 산출이며 5년 benchmark 매핑을 새로 만들지 않음 |
| 정상 유효성 | 양방향, 마감 전 30분 내 갱신, 허용 bid/offer spread 준수; 최소 2개 유효 호가 | 우리 stale·missing 게이트를 완화하는 규칙 아님 |
| 반올림 | 소수점 4자리 및 0.25 basis point 단위 | 임의 yield 생성에 사용하지 않음 |
| 거래량 | bid/offer volume은 산출 결과에 가중치로 반영하지 않음 | 거래량 가중평균이라고 설명하지 않음 |
| 스트레스 상황 | spread 기준 일부 예외가 있으나 stale·일방향 호가는 제외 | 제공자 예외와 프로그램 예외를 구별 |
| 일반 장애 | 같은 날 pre-close snap, 연장 절차 및 price-maker 응답, 14:00 snap을 순서대로 검토; 확보 불가 시 산출하지 않음 | 이전 날짜의 성공 캐시를 최신으로 쓰는 fallback 근거가 아님 |
| 배포 | security별 만기순 목록, vendor XML 및 구독자 Excel | 공개 다운로드 endpoint 확보 아님 |

이 문서에는 별도 final-stage expert-opinion 절차도 존재한다. 이번에는 정상 규칙과 일반 장애 절차를 확인한 것이며, 문서 전체가 항상 순수 시장 관측만으로 산출된다고 단정하지 않는다. 최종 단계의 과거 자료·모형 사용 가능성을 우리 프로그램의 결측 추정 허용으로 옮기지 않는다.

RBNZ의 5년 benchmark 매핑 표에서는 2025-11-17부터 May 2031 채권을 사용한다고 재확인했다. 이는 기존 조사와 같은 매핑이며 새 연결 발견이 아니다. 발행채별 NZGS close의 산출 규칙만으로 RBNZ 시계열의 exact constant-maturity 5년 보간을 주장하지 않는다.

기존 [2025-08-22 변경 공지](https://www.rbnz.govt.nz/statistics/stats-alerts-and-updates/2025/sa-04)는 2025-08-25부터 NZFMA 원천으로 변경하고, 장중에서 종가로 전환 및 하루 지연 게시한다고 명시한다. 원천 변경 전후를 동일 측정 과정으로 합치지 않는다.

## 조사 및 변경 검증

Exa 검색 8회, 요청 결과 슬롯 40개. 슬롯 수는 원본 확보·검증 성공 건수가 아니다. 공식 검색 서비스 검색 3개와 공식 URL 열람을 추가 수행했다. 검색에서 섞여 나온 swap·Euribor·예금 기준금리·일반 채권 계산기는 해당 국가 5년 국채 계약 근거에서 제외했다.

문서만 변경해 실행 테스트를 재실행하지 않았다. `git diff --check`와 변경 범위를 확인한다. 앞선 구현의 98개 테스트 통과는 이전 검증 기록이다. 원자료 수익률 표나 XLSX/PDF 바이트를 저장소에 올리지 않았다.
