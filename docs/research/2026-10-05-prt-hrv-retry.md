# 포르투갈·크로아티아 원본 재확보 및 정부 계산 근거

조사일: 2026-10-05 KST. 사용자의 재조사 요청에 따라 두 후보의 직접 다운로드와 5년물 단위 근거를 재점검했다. 신규 연결 0개, 미연결 9개국 유지. 수집기·점수식·국가 정의·freshness·publication gate는 변경하지 않았다.

## 직접 요청 결과

일반 urllib GET, 각 URL 한 번, 인증 없음. 접근 실패를 우회하거나 과거 성공 응답으로 대체하지 않았다.

| 대상 | 결과 | 원본 증거 |
|---|---|---|
| [PRT series 12099457 metadata](https://bpstat.bportugal.pt/data/v1/series/?series_ids=12099457&lang=EN) | HTTP 403 | 현행 직접 응답 확보 실패 |
| [PRT dataset / last 5 observations](https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?lang=EN&series_ids=12099457&obs_last_n=5) | HTTP 403 | 최신 수집 성공으로 집계하지 않음 |
| [HRV G8b Croatian XLSX](https://www.hnb.hr/documents/20182/1f79bc1c-dfb5-17fd-1571-cdd52a4a9619) | HTTP 200 / 83,373 bytes | SHA-256 `8239a191f31cccd9570ccf88c4b8d38b66b739a6de0c4fa50fd56d1e89e5923e` |
| [HRV official CKAN catalog](https://data.gov.hr/ckan/api/3/action/package_show?id=711cb511-fbfc-49c3-a6c3-7ae40cca5bdf) | HTTP 200 / 11,335 bytes | SHA-256 `9d12fa323196a3e5852a08f09261efa25027f7dd0af331b24ad418f116e24e35` |

크로아티아 XLSX 해시는 앞선 확보 원본과 같다. 새 파일 갱신이나 신규 시리즈 발견으로 집계하지 않는다. BPstat 검색 서비스 추출에서는 기존 series/dataset 식별자와 `obs_updated_at=2026-10-02T16:00:00Z`를 확인했지만 이는 직접 수집 성공이나 관측 기준일을 뜻하지 않는다.

## HRV 원본 구조 재확인

- 시트 하나 `HRV`, visible, 385행·51열. 국내시장 EUR는 AG5/AG6 헤더, AJ7은 `5 g.`이다.
- 국내 EUR 5년 AJ열의 2026년 1~6월은 문자열 `-`; 7·8월은 숫자 관측값이다. 최근 관측 월 2026년 8월을 재확인했다. 결측을 다른 만기나 외국시장 EUR로 채우지 않는다.
- XML 텍스트, defined names, header/footer, 셀 형식을 추가 점검했으나 5년 열에 직접 적용되는 `%` 또는 단위 설명을 확보하지 못했다. 값 있는 셀 형식은 General, 일반 소수, 연도 표시다. 숨김 행은 없고 머리말·꼬리말도 비어 있다.
- XLSX core modified 시각은 `2026-09-01T14:18:29Z`. 문서 속성 시각은 관측 월이나 제공기관의 실제 게시 수정일과 다르다. publication notice에 필요한 `source_date`로 자동 전용하지 않는다.
- G8b CKAN resource `e8900684-dbb8-4193-9686-e4627925bf5a`의 `last_modified=null`, `metadata_modified=2026-05-08T14:29:44.290133`, `datastore_active=false`. 카탈로그 메타데이터 날짜도 원본 관측일·게시 수정일로 사용하지 않는다.
- 카탈로그는 custom `open-license` 및 공식 개방 라이선스 URL을 표시하면서 `isopen=false`도 반환한다. 이 플래그의 원인은 미확인이다. 플래그만으로 기존의 명시적 라이선스 검토를 철회하거나 재배포 범위를 확대하지 않는다. 기존 정확한 G8b URL 범위와 notice 요구를 유지한다.

## 새 근거: 정부 문서의 역사적 G8b 5년물 사용

크로아티아 정부의 주택저축 보조금 결정안 설명 자료 두 개를 직접 다운로드했다. 최종 공포 법령으로 간주하지 않는다.

| 공식 문서 | 확인 위치 | HTTP / bytes / SHA-256 |
|---|---|---|
| [2019 cabinet paper](https://vlada.gov.hr/UserDocsImages/2016/Sjednice/2019/136%20sjednica%20VRH/136%20-%208.pdf) | PDF 2쪽 Fs 정의, 3쪽 G8b 원천 명시, 6쪽 G8b 표 | 200 / 750,496 / `5e4bd9e7fb88763a193b22e2ff228096eac2a25dccd4ad5e34c7145a2a2bafd2` |
| [2016 cabinet paper](https://vlada.gov.hr/UserDocsImages/2016/Sjednice/2016/14%20sjednica%2014%20Vlade/14%20-%2012.pdf) | PDF 2쪽 Fs 정의, 3쪽 G8b 원천 명시, 4쪽 G8b 표 | 200 / 350,147 / `4acc22401decf4bb25665af88ca44e121c2f4bb6a849f17bc229bd5067120564` |

두 설명 자료는 HNB의 잔존 5년 국채 수익률 평균의 절반을 Fs로 사용하고, 예금금리 Kp와 더해 보조금 비율을 계산한다. 당시 대상은 HRK 발행·EUR 통화조항 국채이며 현행 국내 EUR 발행 열과 동일한 상품 정의라고 단정하지 않는다.

**추론으로 한정:** 이 계산 구조는 당시 G8b 수치가 퍼센트 규모로 사용되었다는 역사적 근거다. 현재 XLSX 5년 열의 직접 단위 선언은 아니다. 2019 문서의 명시적인 연간 퍼센트 제목은 G1c 표에 붙어 있으므로 G8b 단위 제목으로 잘못 인용하지 않는다.

정부의 보조금 공식에는 5년 관측 부재 시 더 긴 만기의 가까운 채권을 사용하는 규칙과 결측 월 제외 규칙이 있다. 이는 별도 정책 계산 규칙이다. 스크리너의 결측·만기 게이트에 적용하지 않는다. 원본 수익률 숫자나 전체 표는 저장소에 재배포하지 않았다.

## 남은 연결 조건 / 검증

1. PRT: 현행 직접 응답, 단위 및 5년 대표채권·보간·만기 구간 계약 확인 필요. 검색 추출 시각은 최신 수집 대체가 아니다.
2. HRV: 현행 5년 열 단위의 직접 근거, 기존 영문 360일/현지어 365일 방법론 상충 해소 필요. 구간 평균을 constant-maturity 5년으로 승격하지 않는다.
3. 재배포는 [승인된 범위와 출처 고지](2026-10-05-publication-gate-update.md)를 유지한다. IMF·FX 등의 pending 상태 및 public-output redaction도 그대로다.

문서만 변경했으며 테스트를 재실행하지 않았다. `git diff --check`로 문서 공백 오류를 확인한다. 앞선 구현의 98개 테스트 통과는 이전 검증 기록이다.
