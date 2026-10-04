# 공식 자료 정의·접근 조건 후속 조사

조사 시점: 2026-10-04 UTC / 2026-10-05 KST. 연구 문서만 추가하며 collector, 국가 정의, 점수, 품질 및 재배포 게이트는 변경하지 않았다. 이전 조사 기록은 [공식 자료 재조사](2026-10-05-official-source-retry.md)를 참조한다.

## 포르투갈: 자동 수집 지원 확인, 특정 시리즈 재배포는 미확정

공식 API 사용 안내:
https://bpstat.bportugal.pt/api/media/files/scripts/menu/api.html?control_kebab=1

안내는 JSON-stat API를 이용한 프로그램 연동, 자동 수집, 반복 업데이트를 명시적으로 지원한다. 필요한 데이터만 요청하고 가능한 필터를 적용하도록 안내한다. 따라서 API 자동 접근을 지원하는 공식 근거를 확보했다. 이 안내만으로 원공급자 LSEG의 특정 시리즈를 커뮤니티 배포 결과에 재배포할 권리가 확인되는 것은 아니다.

이전에 실제 HTTP 200으로 확보한 series 12099457은 고정금리 국채의 잔존 만기 5년 수익률이다. benchmark 또는 constant-maturity 정의와 동일하다고 단정하지 않는다. 당시 응답 SHA와 dimensions는 이전 기록에 있다. 안내의 필터 지원은 dataset에 따라 달라지며, `last_n` 지원은 이 안내에서 확인하지 못했다.

이번 직접 재요청은 HTTP 403이었다. 기존의 성공 기록을 지우거나 403을 데이터 부재로 해석하지 않는다. 접근 우회는 시도하지 않았다. 정의 계약과 시리즈 재배포 조건이 다음 확인 사항이다.

## 아일랜드: B.3 CSV 확보, 5년 국채 후보에서 제외

공식 정부 카탈로그:
https://data.gov.ie/dataset/official-and-selected-interest-rates

카탈로그 API:
https://data.gov.ie/api/3/action/package_show?id=official-and-selected-interest-rates

카탈로그는 Central Bank of Ireland를 발행자로, CC-BY-4.0을 라이선스로 표시한다. 범위는 정책금리, 은행간 금리, 아일랜드 은행 우대금리이며 월별 자료이다. 이 라이선스를 다른 중앙은행 데이터 전체에 확대 적용하지 않는다.

실제 CSV 다운로드 URL:
https://opendata.centralbank.ie/dataset/d3e0af62-a51e-4930-924b-a95a3f4e7e04/resource/1f1d07aa-8cd3-46ce-86a3-dac04da3eae0/download/b.3.csv

- 일반 다운로드 요청 HTTP 200, 16,558 bytes. 리다이렉트된 임시 서명 URL은 저장하지 않는다.
- SHA-256: `42a353642e660eb4e35f46467f011fde2ba59f745de40da9da92016fa1d92966`.
- cp1252로 해석한 CSV는 헤더 1행과 데이터 300행. 마지막 Reporting Date는 `29/12/2023`.
- 날짜 외 열은 marginal lending facility, deposit facility, main refinancing operations, €STR, Eonia overnight, 1/3/12개월 Euribor, Irish clearing banks prime rates이다.
- 국채 수익률이나 5년물 열이 없다. 이전 기록의 B.3 후보는 이 원본 검사로 제외한다. 별개의 과거 월간 통계에 정부증권 수익률이 있었다는 사실은 현재 B.3의 내용으로 전이하지 않는다.

추가로 공식 카탈로그 `package_search?q=government%20bond&rows=20`는 8개 결과를 반환했지만 보유액·부채 구성·만기 구조·증권 발행/보유 자료였다. 이 제한된 검색에서 5년 수익률 원본을 확보하지 못한 것이며, 아일랜드 전체 공식 자료에 해당 시계열이 없다는 결론은 아니다.

## 덴마크: 공식 5년물 항목은 확인, 2012년 종료

월별 공식 테이블 메타데이터:
https://m.statbank.dk/TableInfo/DNRENTM

중앙정부 bullet 국채 5년 만기 수익률 항목이 있으나 표시 기간은 1987년 1월부터 2012년 11월까지다. 월평균/월말 방법을 제공하는 역사 자료 후보이며, 현재 5년물 입력으로 사용할 수 없다. 같은 목록의 5년 swap fixing은 국채가 아니므로 대체하지 않는다. 이번에는 메타데이터를 확인했으며 관측값 다운로드를 완료했다고 집계하지 않는다.

일별 테이블:
https://m.statbank.dk/TableInfo/DNRENTD

확인한 항목 목록에는 중앙은행 정책금리 및 DESTR 관련 항목이 있으며 국채 5년물은 없다. 다른 덴마크 테이블 전체에 대한 부재 판정은 하지 않는다. 후속 조사에서는 DNRENTM의 종료 항목을 반복 검색하기보다 후속 제공 경로나 별도 공식 채권 자료를 찾는다.

## 오스트리아: UDRB는 특정 5년물과 정의가 다름

공식 정의와 방법 설명:
https://www.oenb.at/en/daten-und-forschung/datenangebot/zinssaetze-wechselkurse/renditen-oesterreichischer-bundesanleihen.html

UDRB는 오스트리아 법에 따라 발행된 유로화 고정금리 중앙정부 국채 중 잔존 만기 1년 초과 채권의 발행잔액 가중평균 수익률이다. 공식 설명은 여러 잔존 만기가 섞여 있고 만기 구성에 영향을 받는다고 명시한다. 그러므로 일별 값을 제공해도 국가 5년물 입력으로 대체하지 않는다. 거래일 값은 전주분을 매주 금요일 공개한다고 설명하며, 일별 관측 빈도를 즉시 일별 공개와 혼동하지 않는다.

국제 장기 국채 금리 공식 표 역시 약 10년 잔존 만기를 설명한다:
https://www.oenb.at/en/daten-und-forschung/datenangebot/zinssaetze-wechselkurse/eurosystem-und-eurogeldmarktzinsen/10-6-renditen-langfristiger-schuldverschreibungen-im-internationalen-vergleich.html

국가별 5년 수익률 계약을 만족하는 추가 경로는 아직 미확보다.

## 슬로베니아 및 다음 조사 순서

`https://api.bsi.si/interests?date=2026-09`는 이번 요청에서 HTTP 403이었다. 이전 timeout과 구분한다. 실제 응답 본문을 검증하지 못했으므로 5년 국채 존재 여부는 여전히 미확정이다.

다음 우선순위:

1. PRT 잔존 5년 정의 계약 및 해당 LSEG 시리즈 재배포 조건.
2. DNK 종료된 역사 통계의 후속 공식 경로.
3. IRL B.3 이외 국채 시장 수익률 원본.
4. AUT 특정 만기별 공식 시계열과 SVN API의 실제 응답 정의.

연결 현황은 기존 18개국 연결, 9개국 미연결로 유지한다. 이번 조사에서 수집기 추가나 DATA_HOLD 완화는 없었다. 문서만 변경했으므로 코드 테스트는 재실행하지 않았다.
