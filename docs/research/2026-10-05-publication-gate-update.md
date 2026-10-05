# 승인된 재배포 게이트 갱신과 후속 자료 조사

작업일: 2026-10-05. 사용자가 승인한 변경안에 따라 제한된 두 출처의 재배포 검토를 설정에 반영했다. 신규 collector는 추가하지 않았다. 연결된 18개국 / 미연결 9개국을 유지한다.

## 적용 범위

| 대상 | 승인 범위 | 근거 | 아직 남은 조건 |
|---|---|---|---|
| PRT | 직접 BPstat dataset `690b7b36fd36c0dbe249c48cbbc39524`, 단일 `series_ids=12099457` | [BPstat 법적 고지](https://bpstat.bportugal.pt/avisos-legais) | collector·시리즈 등록, 수익률 정의 검증 |
| HRV | 카탈로그에 연결된 정확한 크로아티아어 G8b resource UUID `1f79bc1c-dfb5-17fd-1571-cdd52a4a9619` | [공식 카탈로그](https://data.gov.hr/ckan/api/3/action/package_show?id=711cb511-fbfc-49c3-a6c3-7ae40cca5bdf), [Croatian Open Licence](https://narodne-novine.nn.hr/eli/sluzbeni/2017/67/1577) | collector·시리즈 등록, 단위·언어별 방법론 상충 검증 |

BPstat는 Banco de Portugal 출처를 표시하고 원자료를 정확히 재현하며 계산·분류가 파생 결과임을 명시한다. HRV는 제공기관·자료·라이선스 링크, 실제 공급자 수정일, 파생 계산과 공식 보증 없음 고지를 표시한다. 공급자 수정일은 관측일이나 검토일로 대체하지 않는다.

두 country route의 `redistribution=allowed`는 특정 출처의 재사용 검토 승인이다. `adapter=unavailable`, 빈 `series`, `baseline_compatible=false`는 그대로다. 영문 G8b, 다른 BPstat 시리즈·상품, AUT 거래소 자료에는 확대 적용하지 않는다. IMF fiscal과 ECB FX는 계속 `pending`이다.

`publication.py`가 실제 수집 관측값의 URL·단일 쿼리 시리즈·설정 시리즈·ISO3·관측별 재배포 상태를 검사한다. 해당 행에 10년 관측이 있으면 그것도 통과해야 한다. 범위·근거·고지 또는 필수 provenance가 없으면 전체 행 수치와 regime을 기존 방식으로 redaction한다. 승인된 고지는 동일 summary model에서 CLI / Markdown / HTML로 렌더링한다.

점수식, 가중치, stale·tenor·unit·definition 검사, 실패 후 캐시 미사용, demo 처리, Adjusted 비활성화는 바꾸지 않았다. 이 변경으로 DATA_HOLD를 READY로 승격하지 않는다.

## 검증

- `python -m unittest discover -s tests -v`: **98개 통과**. 기존 88개와 새 재배포 범위 회귀 테스트 10개.
- URL/host/query/시리즈 불일치, 미승인 두 번째 tenor, 누락 근거·고지, malformed scope, 공급자 수정일 누락은 redaction을 유지한다.
- private 점수 동일성, stale/단위/정의/만기 거부, default scoped source의 synthetic 값 미공개, 세 summary renderer의 고지 표시를 검증했다.
- `python -m sovereign_macro demo --output results/demo --public-output`: `DATA_HOLD`, `SAFE_TO_USE=FALSE`, `SYNTHETIC DEMO`, Baseline `0/27`, Adjusted `0/27`. 실사용 순위나 pending 원자료 수치는 표시하지 않는다.
- 최초 전체 테스트의 실행 환경에는 requests가 없어 import 오류가 있었다. 프로젝트의 기존 의존성을 editable 설치한 뒤 위 전체 검증을 완료했다. 프로젝트 의존성 정의는 변경하지 않았다.

## 실제 run 검증

`python -m sovereign_macro run --output results/local`도 완료했다. 실행 ID
`20261005T004342-9ed17f72`, as-of `2026-10-05`.

```text
GLOBAL STATUS          DATA_HOLD
SAFE_TO_USE            FALSE
USAGE MODE             PARTIAL BASELINE
5Y routes registered   UNKNOWN
5Y observations parsed 17
Baseline usable        6 / 27
Adjusted usable        0 / 27
PARTIAL BASELINE        AVAILABLE
FULL COMPARISON         DATA_HOLD
ADJUSTED MODEL          DATA_HOLD
```

부분 순위는 NOR, CAN, NLD, DEU, GBR, FRA 순이었다. 이 실행은 private 모드이며
커뮤니티 배포용 public 수치 승인으로 해석하지 않는다. SWE 수집은
`HTTP_FAILURE:ReadTimeout`으로 실패했고 부분 랭킹에서 제외됐다. PRT/HRV는
여전히 `SOURCE_NOT_IMPLEMENTED_OR_UNVERIFIED`다. CZE/ISR frequency,
SVK/ITA stale, BEL contract HOLD가 그대로 표시됐다. 등록 경로 count는 result에
정확한 메타데이터가 없어 `UNKNOWN`을 유지하며 설정의 18개를 주입하지 않았다.
실제 수집물이나 private 보고서 수치는 저장소에 커밋하지 않는다.

## 자료 조사 계속: LTU

추가 확인한 [재무부 2024 영문 PDF](https://finmin.lrv.lt/public/canonical/1739534778/24406/VSP%202024%20EN.pdf)는 국내 등록·발행 국채의 가중평균 연 수익률이라는 제목 아래 명목 만기와 잔존 만기를 별도로 표시한다. 5년 열과 % 표시는 확인했다. 5년 열이 있다는 사실만으로 secondary-market benchmark 또는 constant-maturity 5Y로 대체하지 않는다.

[2025 PDF](https://finmin.lrv.lt/public/canonical/1767330300/26238/VSP%202025Q.pdf)와 [2026Q2 PDF](https://finmin.lrv.lt/public/canonical/1783409314/27578/VSP%202026Q2.pdf)도 각각 명목/잔존 만기별 가중평균 표와 % 단위를 확인했다. 최신 표 제목은 2024년의 등록·발행 표현보다 짧다. 따라서 2024년 제목을 그대로 최신 데이터의 계산 방법이라고 단정하지 않는다. 최신 표의 원천, 가중치, 시장 종류와 실제 관측일 정의가 필요하다. 공식 PDF 검색 서비스 추출을 확인했으며 원본 바이트 다운로드 완료나 callable API 확보로 집계하지 않는다.

검색 중 공식 도메인 지정에도 탄소배출권 등 무관한 결과가 반환된 질의가 있었다. 그 결과는 근거로 사용하지 않았고, 앞선 검색에서 확인한 공식 PDF를 직접 추출했다.

## 자료 조사 계속: HRV

추가 [크로아티아어 Bulletin 299](https://www.hnb.hr/documents/20182/5311265/hbilt299.pdf/f9d14c06-d824-a7eb-7fae-07a4a52027d0?download=true&t=1748266549818&version=4.0)의 인쇄 40쪽 G8b와 41쪽 방법론을 확인했다. 방법론 역시 잔존 만기를 ±0.5년 구간으로 묶고 365일 기준을 설명한다. 월별 값은 일별 값 평균이며 국내시장·외국시장 계산 원천이 다르다.

추출된 G8b 표 헤더에서 5년 열의 직접적인 % 단위 선언은 찾지 못했다. 방법론의 % 설명은 LTIR를 대상으로 하므로 5년 열에 옮겨 쓰지 않는다. 영문 360일 / 현지어 365일 상충과 단위 확인 과제는 유지한다. Bulletin 자체는 이번 XLSX resource 재배포 승인 범위에 추가하지 않았다.

후속 작업은 LTU 최신 표의 계산 계약, HRV 단위·방법론, 그리고 나머지 7개국의 현행 5년 수익률 및 자동접근·재배포 근거 확보다. 이번 조사에서 새 연결은 0개다.
