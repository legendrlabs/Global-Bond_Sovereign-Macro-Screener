# 첫 프리릴리스와 공식 자료 후속 수집

검증 시각: 2026-10-04 UTC / 2026-10-05 KST.

## 배포 검증

- 공개 시험판: https://github.com/legendrlabs/Global-Bond_Sovereign-Macro-Screener/releases/tag/v0.1.0-preview.1
- 대상 커밋 `8b7427253ae790ce0ce9573f7f26769c9c294277`; GitHub API에서 `prerelease=true`, `draft=false` 확인.
- 로컬 75개 테스트와 공개 demo 통과. GitHub의 Preview program release 빌드·게시 작업도 성공.
- wheel, 소스 ZIP, SHA256SUMS.txt를 공개 URL로 실제 다운로드해 크기와 GitHub asset digest 일치 확인.
- wheel SHA-256: `b016f2bfd471ab377ca61ffd4f59d20238641fdf8e984b36c243ff3bca3fedff`.
- 소스 ZIP SHA-256: `566aafd68e618c73d4c9751c210492fa57046ae61a484b5b5591561fcceae4a0`.
- main 병합 없이 시험판 전용 브랜치에서 게시. 자동 프로그램 업데이트는 정식 릴리스만 확인한다. Python 3.11+ 필요.

## 실제 자료 재수집

`python -m sovereign_macro run --as-of 2026-10-05 --output results/prerelease-followup`

- run_id: `20261004T161032-9781a0a4`; 완료 시각 `2026-10-04T16:10:32.053479+00:00`.
- Baseline 사용 가능: NOR, CAN, SWE, NLD, DEU, GBR, 총 6/27. Adjusted 0/27. 전체 DATA_HOLD.
- 42회 HTTP 기록: 200 응답 18회, 304 응답 3회. 304는 기존 해시가 검증된 캐시만 재사용한다.
- IMF 공식 API 수집 성공. FX, ISL, KOR, ISR, USA, JPN은 최종 타임아웃; FRA는 429. 실패 값을 과거 값이나 다른 만기로 채우지 않았다.
- 미연결 9개국 NZL, BGR, IRL, DNK, LTU, HRV, SVN, AUT, PRT는 그대로 유지.
- 개인 보고서와 원자료 캐시는 릴리스 및 git에 포함하지 않는다.

## 크로아티아: 영문 원본과 최신 방법론 확보

공식 영문 안내:
https://www.hnb.hr/en/statistics/statistical-data/general-government/general-government-debt

이번에 확인한 영문 XLSX:
https://www.hnb.hr/documents/20182/0ce7cb2f-ed3a-2b11-38d3-f1b34afc08de

- 인증 없이 HTTP 200, 77,639 bytes. SHA-256 `49c64ae3aca6b72193dd54810c5b586fd199db1de5481b72f856826b3385d55b`.
- 안내 페이지의 G8b 갱신일 2026-09-10. 국내 시장 EUR / 5 years는 AJ열(1-based 36). 외국 시장 EUR / 5 years와 별개.
- 국문 원본도 HTTP 200, 83,373 bytes; SHA-256 `8239a191f31cccd9570ccf88c4b8d38b66b739a6de0c4fa50fd56d1e89e5923e`.
- 월별·연별 평균이며, 월별 값은 일별 만기수익률의 단순 평균. 잔존 만기 t±0.5년 구간, 360일 기준으로 그룹화한다. 국내 시장은 Zagreb 거래소 가격, 거래 없는 날에는 최근 가격을 사용한다. 해외 발행은 Bloomberg bid 가격을 사용한다.
- 영문 XLSX는 Year 숫자와 영문 Month를 사용한다. 연별 행은 Month가 없어 월별 행과 구분 가능. 2026년 국내 EUR 5년 구간은 1~6월 결측, 7~8월 관측이 있다. 결측은 유지해야 한다.
- **단위는 여전히 미확정:** 영문 XLSX에도 percent/% 표기가 없고, 안내의 percentages per annum 설명은 약 10년 LTIR에만 명시되어 있다. 이를 전체 G8b 5년 열의 단위로 확장하지 않았다. 단위 근거 확보 전 HRV 연결 보류. 확보하더라도 월별 잔존 만기 바스켓이므로 기존 일별 benchmark gate를 충족한다고 처리하지 않는다.

정부 카탈로그:
https://data.gov.hr/ckan/api/3/action/package_show?id=711cb511-fbfc-49c3-a6c3-7ae40cca5bdf

인증 없이 200. G8b XLSX와 월별·연별 정의 확인. 카탈로그가 `open-license`와 https://data.gov.hr/id/licence/otvorena-dozvola-rh 를 표시하지만, 재배포 판단은 아직 pending이다.

## 불가리아 및 남은 조사

https://www.minfin.bg/en/statistics/20 재시도는 HTTP 403. 우회하지 않았다. BNB 기존 자료는 경매 수익률과 2차 시장 5년 시계열을 구별해 계속 검토해야 한다.

다음 보강은 HRV 5년 열 단위의 명시적 공식 근거, BGR 월보의 2차 시장 5년 구간, 나머지 국가의 무인증 공식 재공급 경로를 우선한다. 이번 수집에서 새 국가 연결을 확정하지 않았다. 이 문서의 완료 기록은 지속 실행 중인 백그라운드 작업을 의미하지 않는다.
