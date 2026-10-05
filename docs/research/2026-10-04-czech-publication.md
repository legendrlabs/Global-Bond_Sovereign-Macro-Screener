# 체코 월간 공개 자료 연결 및 남은 국가 후속 조사

## CZE — 공식 월간 PDF 경로 추가

- [CNB 공식 월간 Bulletin 목록](https://www.cnb.cz/en/statistics/money_and_banking_stat/monetary-statistics-monthly-bulletin/index.html)은 현재 발행된 영문 PDF 링크를 제공한다. ARAD 계정/API 키 없이 일반 공개 간행물을 받는 별도 경로다.
- [2026년 9월 발행 PDF](https://www.cnb.cz/export/sites/cnb/en/statistics/.galleries/money_and_banking_stat/mon_bank_stat/2026/menstat_2026-09_EN.pdf)를 직접 무인증 HTTP 200으로 확보했다(1,492,164 bytes). 물리 페이지 5의 TABLE 2B는 `in %, monthly average`와 2/5/10년 Bond yields, Source Czech National Bank를 명시한다.
- 물리 페이지 6의 TABLE 1–2 commentary는 실제 기준월 **July 2026**과 **5Y bond 4.26%**를 명시한다. PDF 원본을 새 파서에 넣어 `2026-07, 4.26`을 검증했다. 2026-09를 관측월로 바꾸지 않는다.
- 잔존 만기 구간의 월평균 자료이며 고정만기 일별 값이 아니다. `frequency: monthly`, `baseline_compatible: false`, `redistribution: pending`으로 등록한다. 일별 최신성/순위 검사는 계속 거부한다.
- 현재 발행 목록의 최신 as-of 적격 링크만 선택한다. 파일 URL의 판본과 PDF 내부 판본을 대조하며, 단위·주기·5Y 표제·기준월·명시적 수익률 문장이 달라지거나 중복이면 오류다. 미래 기준월 또는 3개월 초과 발행 지연도 거부한다. 현행 PDF 다운로드 실패 시 과거 판본을 최신 자료처럼 사용하지 않는다.
- [CNB 일반 웹사이트 이용조건](https://www.cnb.cz/en/privacy-statement-and-disclaimer/disclaimer-copyright/)은 출처 표시 및 저자·이미지 예외, 원문 의미 보존 조건을 설명한다. 해당 수익률 자료의 배포 및 파생 지표 표시 조건을 종합 승인한 것은 아니므로 재배포 플래그는 유지한다.
- 어댑터는 PDF의 명시적 해설 문장을 사용하므로 향후 표현이 달라지면 수집이 중단될 수 있다. 장기 전체 시계열 다운로드가 아니라 해당 간행물 기준월 한 건을 연결한 것이다.

검증: 전체 단위 테스트 63개 통과. 직접 확보한 공식 PDF 파싱은 성공했지만, 실행용 HttpClient의 예산 2회·재시도 1회 제한 점검은 목록 요청에서 ReadTimeout으로 끝났다. 자동 수집의 현재 성공이나 안정성을 보장하지 않는다.

## 현재 미연결 9개국

| 국가 | 이번 확인과 남은 문제 |
|---|---|
| HRV | HNB G8b 국내시장 EUR 5Y 월평균 열과 2026-08 마지막 값 3.02 확보. 해외시장 EUR 5Y는 3.21로 다르다. 국내 2026-01~06은 결측. XLSX에 명시적 단위가 없고 LTIR의 % 단위를 모든 만기 열에 자동 적용하지 않아 미연결 유지. Bulletin 298 현행 방법론의 구간 만기는 360일 기준이며 예전 365일 설명과 혼합하지 않는다. |
| DNK | DNRENTDX / DNRENTD 공식 StatBank 변수 목록을 직접 HTTP 200으로 읽었다. 현재 목록은 정책/초단기·DESTR 계열이며 5Y 국채 열을 식별하지 못했다. API tableinfo 502는 자료 부재의 증거가 아니다. |
| BGR | [BNB 2026 Q2 XLSX](https://www.bnb.bg/bnbweb/groups/public/documents/bnb_download/gssm_2026_06_a1_en.xlsx) 직접 200, 568,043 bytes. 발행·경매 수익률, 만기/쿠폰과 유통·환매 거래 통계는 있지만 비교 가능한 유통시장 5Y 시계열을 식별하지 못했다. 경매 수익률로 대체하지 않는다. |
| NZL | RBNZ 자동 수집 이용조건 확인이 남아 무인 자동 수집을 확대하지 않았다. 공식 데이터 재공급 경로도 이번 검색에서 확보하지 못했다. |
| PRT | 앞선 BPstat 직접 호출 403 상태에서 새로운 성공 경로를 확보하지 못했다. |
| AUT | UDRB 잔존 1년 초과 가중평균·약 10Y 장기금리는 5Y 대체가 아니다. 종목 쿠폰/가격 표를 수익률로 취급하지 않는다. |
| IRL | 공식 기관 후보는 확인했지만 무인증 직접 5Y 시계열은 추가 확보하지 못했다. |
| LTU | 공식 경매 결과는 종목별 발행 수익률이며 일별 유통시장 5Y와 구분한다. |
| SVN | 공식 수렴 장기금리는 약 10Y 월평균이다. 국가별 5Y 경로 미확보. |

ECB 공통 유로존 5Y 곡선은 국가별 수익률 대체로 쓰지 않는다. 국가별 FM 조회는 일부 요청 오류/타임아웃으로 해결되지 않았으며 이것으로 해당 계열이 없다고 결론 내리지 않는다. Riksbank 전체 공개 series 목록도 대조했으나 나머지 국가를 연결할 계열을 찾지 못했다.

총 등록 경로는 **18개국(일별 16, 월별 2)**, 미연결은 **9개국**이다. 자료 확보, 실행 중 HTTP 성공, 정의 호환성, 재배포 허가는 각각 다른 상태다. 전체 제품은 여전히 DATA_HOLD다.

독립 리뷰에서 5Y 결측 문장 뒤의 10Y 값 오인과 15 years 표제 오인을 재현하는 테스트가 실패했다. 문장 경계·허용 문법 및 독립 만기 표제를 엄격하게 제한해 수정한 뒤 전체 63개 테스트와 실제 PDF 파싱을 다시 통과했다.
