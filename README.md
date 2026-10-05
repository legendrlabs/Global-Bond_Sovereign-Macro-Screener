# Global Bond · Sovereign Macro Screener

한국 투자자의 KRW 기준 비교를 위한 **공식 자료 우선 연구용 스크리너**입니다. API 키 없이 수집하고, 공식 경로가 실패하거나 유효하지 않으면 WorldGovernmentBonds(WGB)로 보완합니다. 원자료 관측일·발행판·만기·결측과 계산 가능 여부를 함께 기록합니다.

v0.1.1은 preview.5의 검수된 기능을 포함한 연구용 사용판입니다. 실행 완료와 27개국 전체 비교 가능 여부는 구분합니다. Market Quality 종합 점수와 Adjusted 모델은 아직 준비되지 않았습니다. 결측을 임의로 채우거나 가중치를 재분배하지 않습니다.

## 실행

Python 3.11 이상. [v0.1.1 릴리스](https://github.com/legendrlabs/Global-Bond_Sovereign-Macro-Screener/releases/tag/v0.1.1)에서 wheel과 SHA256SUMS.txt를 다운로드하고 파일 해시를 확인한 뒤 설치합니다. API 키 등록은 필요하지 않습니다.

```bash
python -m pip install sovereign_macro_screener-0.1.1-py3-none-any.whl
python -m sovereign_macro app
```

`app`은 새 프로그램 확인과 자료 갱신을 각각 묻습니다. 무입력 실행은 아래 `run`을 사용합니다. 이전 시험판 내부 버전은 0.1.0이므로 정식 0.1.1 업데이트를 구분할 수 있습니다.

소스에서 설치하려면:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install .
python -m sovereign_macro run --output results
```

`results/current.json`의 `path`가 가리키는 폴더에서 `index.html`을 열면 국가 검색과 원자료 근거를 확인할 수 있습니다. 같은 폴더에 아래 여섯 파일이 생성됩니다.

| 파일 | 내용 |
|---|---|
| latest.md | 현재 실행 요약 |
| sovereign_scores.csv | Baseline / Adjusted 및 각각의 순위 |
| country_details.csv | 재정·금리·환율·품질·원자료 근거 |
| macro_regime.csv | 재정 추세·실질금리·FX·carry·discount 분류 |
| quality.json | 실행 품질, 범위, safe_to_use |
| run_manifest.json | 발행판·원본 해시·관측일·보고서 해시 |

네트워크 없이 화면과 계산 흐름을 확인하려면:

```bash
python -m sovereign_macro demo --output results/demo
```

**demo는 합성 자료**이며 순위와 safe_to_use가 비활성화됩니다. 실제 April 2026 회귀 검증과 구별합니다.

커뮤니티 공유 파일을 만들려면:

```bash
python -m sovereign_macro run --output results/public --public-output
```

재배포 조건이 `pending`인 공급자의 수치와 파생 분류는 공개 모드에서 숨깁니다. 현재 기본 설정은 모두 검토 대기 상태라 공개 보고서는 수치보다 연결·품질 진단을 보여줍니다. 로컬 수집 가능 여부와 공개 재배포 허용 여부는 별도입니다. `data/`의 원본 캐시나 로컬 연구 보고서를 공개 저장소에 올리지 마세요.

## 대화형 실행과 자동 업데이트 확인

`run`의 기본 터미널 출력과 `latest.md`·HTML 보고서 상단은 공통 Executive Summary를 사용합니다. 전체 GLOBAL STATUS / SAFE_TO_USE, 커버리지, 사용 가능한 부분 Baseline 순위, 수집·품질 HOLD 사유, 기존 거시 지표와 KRW 기준 FX 분류, 데이터 사용 가능성 Decision을 순서대로 표시합니다. 전체 DATA_HOLD에서도 사용 가능한 부분 순위는 표시하지만, 전체 국가 비교가 준비됐다는 뜻은 아닙니다. `app`에서 갱신을 거절하면 기존 보고서의 수집 시점과 함께 저장된 summary를 보여줍니다. 이전 버전 보고서에 summary 파일이 없으면 기존 안내를 유지합니다.

랭킹은 `usable_baseline=True`이고 기존 `baseline_rank`가 있는 행만 표시합니다. demo는 SYNTHETIC DEMO로 표시하고 실사용 랭킹을 보여주지 않습니다. 공개 모드 summary도 redaction 이후 결과만 사용합니다. 5Y observations parsed는 실제 수집 bundle에 존재한 5년물 관측 수이며, 최신성·정의 등 검증을 통과한 수와 다릅니다. 등록 경로 수처럼 정확한 실행 메타데이터가 없는 값은 UNKNOWN입니다. `executive_summary.json`은 같은 내용을 저장하며 실행 manifest의 해시 목록에 포함됩니다. 원래 전체 국가 테이블·CSV·근거 상세도 유지합니다.

```bash
python -m sovereign_macro app
# 명령을 생략해도 app으로 실행
python -m sovereign_macro
```

실행 시 GitHub의 새 정식 프로그램 버전을 확인하고, 설치 전에 `프로그램을 업데이트할까요? [y/N]`로 묻습니다. 자료 보고서가 없거나 기준일이 달라졌거나 마지막 수집 후 24시간이 지났으면 `국채·거시 자료를 새로 수집할까요? [y/N]`를 별도로 묻습니다. Enter·거절·입력 종료는 적용하지 않습니다. 거절하면 저장된 결과의 수집 시점과 기준일을 표시하고 기존 보고서를 엽니다. 새 프로그램 설치를 승인한 경우에는 설치 후 종료하며 다시 실행해야 새 코드로 자료를 갱신합니다.

Windows에서는 최초 설정 후 저장소 폴더의 `start-screener.bat`을 더블클릭할 수 있습니다:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install .
```

프로그램 설치는 이 저장소의 정식 GitHub Release에 올라온 정확한 버전의 wheel만 사용하며 SHA-256·크기·패키지 이름·버전을 검사합니다. 공개 릴리스가 아직 없으면 현재 프로그램을 사용합니다. 프로그램 확인 통신이 실패해도 자료 갱신 선택은 계속할 수 있습니다. 개발용 editable 설치는 자동으로 바꾸지 않으며, 배포용 일반 설치를 권장합니다.

`app --public-output`은 공개 모드 보고서를 생성·조회합니다. 이전 결과가 개인 모드 또는 demo이면 공개 모드에서 대신 열지 않습니다. `--no-open`은 브라우저 자동 열기를 끕니다. HTML 파일 자체는 정적 결과이며 업데이트 질문은 Python의 대화형 실행에서 나타납니다. 업데이트 확인은 실행 시 수행하며, 종료된 프로그램이 백그라운드에서 계속 확인하지는 않습니다.

터미널 입력이 없는 환경에서는 `app`이 설치·수집을 건너뜁니다. 기존 `run`/`demo`와 주간 GitHub Actions는 명시적으로 요청된 비대화형 작업이므로 확인 질문을 넣지 않았습니다. 자료 갱신 승인 뒤 수집이 일부 실패하면 새 진단 보고서에 DATA_HOLD를 기록하며, 이전 자료를 최신 값으로 대체하지 않습니다.

배포 관리자는 main에 병합된 버전에 대해 `pyproject.toml`과 `__version__`을 함께 올린 뒤 `vX.Y.Z` 태그를 게시합니다. `Stable program release`가 main 포함 여부·버전 일치·설치 wheel 테스트를 검증한 후 설치 파일을 GitHub Release에 올립니다.

첫 시험판 `v0.1.0-preview.1`은 `release-preview/v0.1.0-preview.1` 브랜치의 검증된 커밋에서 별도로 게시합니다. `Preview program release`가 wheel 설치·테스트·공개 demo를 통과한 뒤 wheel, 설치 안내가 포함된 소스 ZIP, SHA-256 목록을 올립니다. GitHub에서 반드시 프리릴리스로 표시하며 main 병합을 요구하지 않습니다. 시험판 내부 패키지 버전은 `0.1.0`이며 자동 업데이트는 시험판을 설치하지 않습니다. 후속 시험판은 직접 설치하고, 정식 버전으로 자동 전환할 때는 더 높은 패키지 버전을 사용합니다. `v0.1.0-preview.3`부터 IMF DataMapper에는 `curl-cffi` 브라우저 호환 전송을 우선 적용하고 기존 `requests` fallback을 유지합니다.

## 확보된 국가부터 사용하기

### 전 국가 공식 우선 / WGB 보완

기존 공식 5Y 경로 18개국을 우선 사용하고, 모든 27개국에 WGB 보완 경로를 등록했습니다. 미국 10Y 감시 자료도 같은 선택 정책을 사용합니다. 유효한 공식 자료가 2~3일 전 값이라도 우선 유지하며, WGB가 더 최신이라는 이유만으로 출처를 바꾸지 않습니다. 공식 자료 요청 실패·미연결·월별 자료·단위 오류·7일 초과 관측이면 같은 국가와 만기의 WGB 자료를 검증합니다. 두 경로 모두 실패하면 해당 값은 결측입니다.

최신성은 **실제 관측일로부터 7일(달력 기준)**입니다. WGB 곡선표와 역사 자료의 금리가 표시 정밀도 내에서 같고 날짜만 다르면, 더 오래된 확인 가능한 관측일로 사용하고 `WGB_DATE_DISCREPANCY`를 표시합니다. 역사 API는 주말에도 값이 이월될 수 있어 마지막 시계열 날짜만으로 최신 시장 관측일을 주장하지 않습니다. 금리값 불일치, 미래 날짜, 비정상 숫자, 중복 충돌, 다른 국가·만기·단위, 중단된 시리즈는 계속 차단합니다.

HTML·요약·국가 상세 CSV에서 선택된 출처, 관측일, 경과일, WGB 보완 여부와 공식 경로 실패 사유를 확인할 수 있습니다. 국가 코드와 통화는 패키지 설정에 포함되어 외부 `countries_ref.csv`나 브라우저 화면 검증 파일이 필요하지 않습니다. WGB 내부 데이터 응답의 표·시계열을 직접 교차검증하고 응답 원본과 SHA-256은 로컬 캐시에 보관합니다.

WGB는 `annualized_government_yield`라는 별도 정의로 기록합니다. 프로젝트 정책상 검증된 WGB 금리는 Baseline 금리 입력으로 사용합니다. 다만 WGB를 다른 공급자의 benchmark/par/zero-coupon 정의로 이름을 바꾸거나 공식 재배포 승인을 상속하지는 않습니다. 기본 WGB 설정은 `baseline_compatible=true`, `redistribution=pending`입니다. 공개 모드에서는 WGB 수치와 값이 포함된 교차검증 메모를 계속 숨깁니다. 점수 공식과 Adjusted 가중치는 바꾸지 않았습니다.

`config/sources.yaml`의 `yield_fallback.enabled=false`로 공식 경로만 사용할 수 있습니다. 기본 HTTP 요청 예산은 재시도까지 포함해 240회로 제한합니다. 공개 모드에서는 WGB의 수치·파생 결과와 금리가 들어 있는 교차검증 메모를 숨기며 공식 자료의 출처별 재배포 승인을 WGB에 적용하지 않습니다.

27개국이 모두 연결될 때까지 기다리지 않고, 로컬 `run` 결과에서 `usable_baseline=True`인 국가끼리 부분 순위를 사용할 수 있습니다. `baseline_rank`가 빈 국가는 순위 대상이 아닙니다. 미연결·요청 실패·오래된 관측일·월별 자료·단위 또는 정의 미승인은 그대로 제외하며 계산식은 바꾸지 않습니다. 전체 `safe_to_use=False`와 부분 국가의 `usable_baseline`은 서로 다른 검사입니다.

```bash
python -m sovereign_macro run --output results/local
```

부분 결과를 볼 때는 `--require-complete`를 붙이지 않습니다. 진단 보고서는 전체 DATA_HOLD에서도 생성됩니다. Adjusted는 Market Quality 확보 전까지 비워 둡니다. 커뮤니티에 공유할 때는 기존 `--public-output` 모드를 사용합니다.

2026-10-04 실제 실행은 등록 경로 18개국 중 14개국의 5Y 원자료를 파싱했고, 6개국의 Baseline 부분 순위를 계산했습니다. 프랑스는 HTTP 429로 이번 순위에서 제외했습니다. 실행마다 성공 국가가 달라질 수 있으므로 고정 6개국 목록을 강제하지 않습니다. [첫 부분 실행 기록](docs/research/2026-10-04-available-first.md)을 참고하세요.

## 현재 구현 범위

- 27개국 고정 목록과 통화·금리 정의별 검증 구조
- IMF Fiscal Monitor / WEO 발행판 일치 확인, 완전한 재정·CPI 기간 검증
- 같은 발행판 Table A8 PDF의 API 대조 후 순부채 결측 보완
- ECB 환율의 KRW 교차환율, 1Y/3Y 변동성, 최대낙폭
- 18개국 공식 5Y 경로(일별 16개국·월평균 2개국), 27개국 WGB 보완 경로 및 미국 10Y 감시 경로
- 원본 Baseline, 부분 유효 국가 순위, Adjusted 계산 인터페이스
- 실패 격리, 날짜·만기·결측·음수금리·자료권리 상태 표시
- 로컬 HTML, CSV·JSON·Markdown, 주간 GitHub Actions

현재 공식 경로는 18개국이며 공식 미연결 9개국에도 WGB 보완 경로가 있습니다. ISR·CZE의 월평균 공식 자료가 일별 최신성 검사를 통과하지 못하면 WGB 보완을 시도하고, SVK도 실제 관측일로 최신성을 검사합니다. 정의 호환성과 재배포 승인 상태는 출처별로 유지합니다. 연결 수는 최신 수집 성공이나 점수 사용 가능 수와 다릅니다.

전체는 **DATA_HOLD**입니다. 2026-10-03 최초 점검에서 정의가 호환되는 7개국만 Baseline 순위에 사용할 수 있었고, 이탈리아는 오래된 관측일, 벨기에는 단위 검증 보류로 제외했습니다. Market Quality의 검증된 입력이 없어 Adjusted는 모두 비어 있습니다. [추가 연결 검증](docs/research/2026-10-04-connected-sources.md), [체코 및 남은 국가 조사](docs/research/2026-10-04-czech-publication.md), [데이터 경로](docs/data-sources.md), [방법론](docs/methodology.md)을 참고하세요.

## 품질과 자동 실행

기준 연도는 실행 시 서울 날짜를 따릅니다. `--as-of YYYY-MM-DD`는 현재 가져온 자료의 관측일 필터이며 당시 발행판을 재현하는 백테스트 기능이 아닙니다. `--require-complete`는 DATA_HOLD 보고서를 기록한 뒤 종료 코드 2를 반환합니다. 기본 명령은 진단 보고서 작성에 성공하면 DATA_HOLD에서도 코드 0을 반환합니다. 설정·파일 기록 자체가 실패하면 정상 완료로 처리하지 않습니다.

결과 폴더는 실행별로 분리되며 `current.json`만 원자적으로 교체됩니다. 독자는 이 포인터가 지정하는 **한 실행의 파일만** 읽어야 합니다. `last_success.json`은 전체 Baseline 품질 통과 실행만 가리키며 현재 실패가 과거 성공으로 대체되지 않습니다.

테스트는 네트워크 없는 `python -m unittest discover -s tests -v`로 실행합니다. GitHub Actions는 일요일 11:15 UTC(한국 20:15)에 공개 모드로 수집합니다. 원자료 캐시는 업로드하지 않으며 수집 작업은 읽기 권한, 보고서 게시 작업만 쓰기 권한을 사용합니다. 보호된 브랜치나 Actions 쓰기 권한 설정은 자동 게시를 막을 수 있으며 그런 경우 해당 작업이 실패로 남습니다.

## 보강 순서

1. 미연결 9개국의 공식 5Y 자료와 단위·주기·만기 검증
2. benchmark / par / interpolated / fixed residual 정의의 비교 가능성 확정
3. 공급자별 커뮤니티 재배포 조건 확인
4. Market Quality 입력 표의 BIS 분기 규모 수집 경로를 검증하고, 신용·유동성·접근성 자료 및 정규화 기준 연결. 규모는 중앙정부·명목가·전체 통화의 발행잔액(십억 달러)이며 유동성 점수나 5년물 거래 가능성이 아닙니다. WGB 5년물 보완 수집에 성공한 국가는 같은 응답의 S&P 등급·전망·최근 조치일을 참고 정보로 표시합니다. 등급의 통화·장기 여부는 미확인이므로 점수에는 사용하지 않으며, 공식 금리를 선택한 국가는 등급이 비어 있을 수 있습니다. 미연결 항목과 수집 실패는 별도로 표시하며 Adjusted는 계속 비워 둡니다.
5. 정식 라이선스를 확보한 실제 April 2026 회귀 자료 추가

국가를 추가하거나 경로를 바꿀 때 숫자 예외를 넣지 말고 `config/`의 메타데이터 계약과 원자료 파서를 보강하세요. 설치 배포본의 `src/sovereign_macro/defaults/`도 함께 갱신해야 합니다.

### IMF 발표판 저장본 재사용

IMF 재정·물가 자료는 최신 API 조회를 먼저 시도합니다. 연결 실패(`HTTP_FAILURE`) 시에는 검증된 발표판 원본을 다시 파싱해 사용합니다. HTML·요약·CSV·실행 manifest에 발표판, 저장본 사용 여부, 최초 수집 시각, 수집 경과일, 최신 발표판 확인 실패 사유를 표시합니다. `FISCAL_SNAPSHOT_USED`는 경고이며 그 자체로 전체 점수를 보류시키지 않습니다. 새 실행 시각을 원자료 수집 시각으로 바꾸지 않습니다.

IMF DataMapper는 Python 기본 HTTP 지문을 차단할 수 있어 `curl-cffi`의 브라우저 호환 전송을 IMF 도메인에만 우선 사용합니다. 해당 전송이 없거나 실패하면 기존 `requests`로 보완하며, 실제 전송수단과 요청 결과는 캐시·원자료 provenance에 기록합니다. IMF 요청 timeout은 `(10, 30)`으로 적용하고 다른 공급자 요청의 기본 timeout은 바꾸지 않습니다.

저장본은 같은 `--cache` 디렉터리의 `fiscal-snapshots/`에 보관합니다. 지표 목록, 네 가지 IMF 시계열, 필요한 같은 발표판 PDF를 원본 SHA-256과 함께 저장하고, 사용 시 다시 검증합니다. 기존 HTTP 캐시도 원본 해시·발표판·단위·시리즈별 메타데이터·동일 수집 회차·PDF 대조를 통과하면 저장본으로 승격할 수 있습니다. IMF 이외의 HTTP 캐시에는 이 재사용 규칙을 적용하지 않습니다.

기본 `fiscal.snapshot_max_age_days=210`은 금리의 7일 규칙과 별도로, 반기 발표 자료에 맞춘 보관 한도입니다. 재사용 시 예측 시작 연도가 실행 기준 연도와 같아야 하며, 원본이 손상됐거나 수집 시각이 미래이거나 범위가 바뀌면 사용하지 않습니다. 부분 조회에서 새 발표판이나 같은 발표판의 개정을 확인한 경우에도 이전 저장본으로 돌아가지 않습니다. API가 유효하지 않은 단위·정의·발표판을 반환한 경우에는 연결 장애로 간주하지 않습니다.

`fiscal.snapshot_enabled=false`로 재사용을 끌 수 있습니다. 첫 실행이고 검증된 원본이 전혀 없으면 접속 실패를 복구할 수 없어 기존처럼 결측을 표시합니다. 로컬 실행은 같은 캐시 폴더를 유지해야 하며, 임시 CI 실행 환경에서도 재사용하려면 비공개 원자료 보관을 별도로 유지해야 합니다. 원자료는 Git이나 공개 보고서에 포함하지 않으며 기존 공개 모드의 수치 숨김 규칙을 유지합니다.
