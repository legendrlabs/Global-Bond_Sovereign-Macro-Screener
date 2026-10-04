# Global Bond · Sovereign Macro Screener

한국 투자자의 KRW 기준 비교를 위한 **공식 공개 데이터 기반 연구용 스크리너**입니다. API 키 없이 수집하고, 원자료 관측일·발행판·만기·결측과 계산 가능 여부를 함께 기록합니다.

초기 구현은 실행 가능한 구조입니다. 아직 27개국 완전 수집이나 Adjusted 모델 준비 완료를 의미하지 않습니다. 결측을 임의로 채우거나 가중치를 재분배하지 않습니다.

## 실행

Python 3.11 이상:

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

첫 시험판 `v0.1.0-preview.1`은 `release-preview/v0.1.0-preview.1` 브랜치의 검증된 커밋에서 별도로 게시합니다. `Preview program release`가 wheel 설치·테스트·공개 demo를 통과한 뒤 wheel, 설치 안내가 포함된 소스 ZIP, SHA-256 목록을 올립니다. GitHub에서 반드시 프리릴리스로 표시하며 main 병합을 요구하지 않습니다. 시험판 내부 패키지 버전은 `0.1.0`이며 자동 업데이트는 시험판을 설치하지 않습니다. 후속 시험판은 직접 설치하고, 정식 버전으로 자동 전환할 때는 더 높은 패키지 버전을 사용합니다.

## 확보된 국가부터 사용하기

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
- 18개국 5Y 수집 경로(일별 16개국·월평균 2개국) 및 미국 10Y 감시 경로
- 원본 Baseline, 부분 유효 국가 순위, Adjusted 계산 인터페이스
- 실패 격리, 날짜·만기·결측·음수금리·자료권리 상태 표시
- 로컬 HTML, CSV·JSON·Markdown, 주간 GitHub Actions

현재 등록 경로는 18개국이며 미연결은 9개국입니다. ISR·CZE는 월평균 자료라 일별 순위에서 제외하고, SVK는 주간 배포와 실제 관측일에 대한 최신성 검사를 유지합니다. 추가 ISL·ESP·SVK·ISR·CZE는 정의 호환성과 재배포 승인 대기 상태입니다. 연결 수는 최신 수집 성공이나 점수 사용 가능 수와 다릅니다.

전체는 **DATA_HOLD**입니다. 2026-10-03 최초 점검에서 정의가 호환되는 7개국만 Baseline 순위에 사용할 수 있었고, 이탈리아는 오래된 관측일, 벨기에는 단위 검증 보류로 제외했습니다. Market Quality의 검증된 입력이 없어 Adjusted는 모두 비어 있습니다. [추가 연결 검증](docs/research/2026-10-04-connected-sources.md), [체코 및 남은 국가 조사](docs/research/2026-10-04-czech-publication.md), [데이터 경로](docs/data-sources.md), [방법론](docs/methodology.md)을 참고하세요.

## 품질과 자동 실행

기준 연도는 실행 시 서울 날짜를 따릅니다. `--as-of YYYY-MM-DD`는 현재 가져온 자료의 관측일 필터이며 당시 발행판을 재현하는 백테스트 기능이 아닙니다. `--require-complete`는 DATA_HOLD 보고서를 기록한 뒤 종료 코드 2를 반환합니다. 기본 명령은 진단 보고서 작성에 성공하면 DATA_HOLD에서도 코드 0을 반환합니다. 설정·파일 기록 자체가 실패하면 정상 완료로 처리하지 않습니다.

결과 폴더는 실행별로 분리되며 `current.json`만 원자적으로 교체됩니다. 독자는 이 포인터가 지정하는 **한 실행의 파일만** 읽어야 합니다. `last_success.json`은 전체 Baseline 품질 통과 실행만 가리키며 현재 실패가 과거 성공으로 대체되지 않습니다.

테스트는 네트워크 없는 `python -m unittest discover -s tests -v`로 실행합니다. GitHub Actions는 일요일 11:15 UTC(한국 20:15)에 공개 모드로 수집합니다. 원자료 캐시는 업로드하지 않으며 수집 작업은 읽기 권한, 보고서 게시 작업만 쓰기 권한을 사용합니다. 보호된 브랜치나 Actions 쓰기 권한 설정은 자동 게시를 막을 수 있으며 그런 경우 해당 작업이 실패로 남습니다.

## 보강 순서

1. 미연결 9개국의 공식 5Y 자료와 단위·주기·만기 검증
2. benchmark / par / interpolated / fixed residual 정의의 비교 가능성 확정
3. 공급자별 커뮤니티 재배포 조건 확인
4. Market Quality의 실제 자료·정규화 기준 연결
5. 정식 라이선스를 확보한 실제 April 2026 회귀 자료 추가

국가를 추가하거나 경로를 바꿀 때 숫자 예외를 넣지 말고 `config/`의 메타데이터 계약과 원자료 파서를 보강하세요. 설치 배포본의 `src/sovereign_macro/defaults/`도 함께 갱신해야 합니다.
