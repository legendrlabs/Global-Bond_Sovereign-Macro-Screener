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

## 현재 구현 범위

- 27개국 고정 목록과 통화·금리 정의별 검증 구조
- IMF Fiscal Monitor / WEO 발행판 일치 확인, 완전한 재정·CPI 기간 검증
- 같은 발행판 Table A8 PDF의 API 대조 후 순부채 결측 보완
- ECB 환율의 KRW 교차환율, 1Y/3Y 변동성, 최대낙폭
- 17개국 5Y 수집 경로(일별 16개국·월평균 1개국) 및 미국 10Y 감시 경로
- 원본 Baseline, 부분 유효 국가 순위, Adjusted 계산 인터페이스
- 실패 격리, 날짜·만기·결측·음수금리·자료권리 상태 표시
- 로컬 HTML, CSV·JSON·Markdown, 주간 GitHub Actions

2026-10-03 실제 점검: 13개국 5Y 원자료 파싱, 이탈리아는 관측일이 오래되어 제외하고 벨기에는 단위 검증 보류, 정의가 호환되는 7개국 Baseline만 순위 사용 가능. 전체는 **DATA_HOLD**입니다. 2026-10-04에 ISL·ESP·SVK·ISR 공식 어댑터를 추가해 미연결 슬롯은 10개국으로 줄었습니다. ISR은 월평균이며 일별 검사에서 제외되고, SVK는 주간 배포와 최신성 검사를 유지합니다. 추가 4개국은 금리 정의 호환성 및 재배포 승인 대기 상태입니다. [추가 연결 검증](docs/research/2026-10-04-connected-sources.md)을 참고하세요. Market Quality의 검증된 입력이 없어 Adjusted는 모두 비어 있습니다. [데이터 경로](docs/data-sources.md), [방법론](docs/methodology.md), [조사 기록](docs/data-source-feasibility-2026-10-03.md)을 참고하세요.

## 품질과 자동 실행

기준 연도는 실행 시 서울 날짜를 따릅니다. `--as-of YYYY-MM-DD`는 현재 가져온 자료의 관측일 필터이며 당시 발행판을 재현하는 백테스트 기능이 아닙니다. `--require-complete`는 DATA_HOLD 보고서를 기록한 뒤 종료 코드 2를 반환합니다. 기본 명령은 진단 보고서 작성에 성공하면 DATA_HOLD에서도 코드 0을 반환합니다. 설정·파일 기록 자체가 실패하면 정상 완료로 처리하지 않습니다.

결과 폴더는 실행별로 분리되며 `current.json`만 원자적으로 교체됩니다. 독자는 이 포인터가 지정하는 **한 실행의 파일만** 읽어야 합니다. `last_success.json`은 전체 Baseline 품질 통과 실행만 가리키며 현재 실패가 과거 성공으로 대체되지 않습니다.

테스트는 네트워크 없는 `python -m unittest discover -s tests -v`로 실행합니다. GitHub Actions는 일요일 11:15 UTC(한국 20:15)에 공개 모드로 수집합니다. 원자료 캐시는 업로드하지 않으며 수집 작업은 읽기 권한, 보고서 게시 작업만 쓰기 권한을 사용합니다. 보호된 브랜치나 Actions 쓰기 권한 설정은 자동 게시를 막을 수 있으며 그런 경우 해당 작업이 실패로 남습니다.

## 보강 순서

1. 미연결 10개국의 공식 5Y 자료와 단위·주기·만기 검증
2. benchmark / par / interpolated / fixed residual 정의의 비교 가능성 확정
3. 공급자별 커뮤니티 재배포 조건 확인
4. Market Quality의 실제 자료·정규화 기준 연결
5. 정식 라이선스를 확보한 실제 April 2026 회귀 자료 추가

국가를 추가하거나 경로를 바꿀 때 숫자 예외를 넣지 말고 `config/`의 메타데이터 계약과 원자료 파서를 보강하세요. 설치 배포본의 `src/sovereign_macro/defaults/`도 함께 갱신해야 합니다.
