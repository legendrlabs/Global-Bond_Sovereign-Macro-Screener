# Iceland and Australia disclosed 5Y research proxies

The user approved exploratory Baseline inclusion after the official definitions were checked on 2026-10-06 KST. This changes eligibility, not observations, yields, compounding, scoring formulas or source precedence. Both development and packaged contracts must agree.

## Iceland

https://sedlabanki.is/gagnatorg/vextir/

The central bank explicitly describes daily synthetic 3Y/5Y/10Y par rates as constant maturity treasury (CMT) rates. Nominal and indexed, par and zero-coupon series are distinct. Keep the existing nominal par 5Y selector `FLV:nominal:par:5Y` and percent-format unit validation. Its research inclusion follows the disclosed US par-CMT comparison policy; it does not assert an executable single-bond YTM or harmonized annual-effective convention.

## Australia

https://www.rba.gov.au/statistics/tables/csv/f2-data.csv
https://www.rba.gov.au/statistics/tables/changes-to-tables.html

The official CSV metadata identifies `FCMYGBAG5D` as Australian Government 5 year bond; its description is government bonds, interpolated, 5 years maturity, daily and per cent per annum. RBA's F2 notice describes assessed closing yields informed by market participants, intended for academic research, explicitly not RBA-administered financial benchmarks. Preserve `interpolated_constant_maturity`, actual observation date and source assessments. Weekly publication with a delay does not turn publication time into a daily market observation.

## Remaining holds

https://nbs.sk/en/statistics/financial-markets/interest-rates/estimated-yield-curve/
https://www.bde.es/webbe/en/estadisticas/compartido/datos/pdf/ti_1_3e.pdf

Slovakia `ZCY5Y` is an NSS-estimated zero-coupon curve with documented limited-liquidity estimation uncertainty. Spain `D_G0B1F0ZO` has an official 5Y secondary-market column but exact constituent/maturity-selection methodology is not yet confirmed. These contracts remain unapproved for Baseline. Do not override valid official observations with WGB merely to gain ranking eligibility.

## Verification

Regression tests exercise actual ranking and definition disclosures for Iceland/Australia, preserve Slovakia/Spain exclusion, and reject stale, wrong-unit or wrong-definition observations after approval. Existing public/demo redaction and Adjusted hold rules remain unchanged. A saved same-run input replay can compare 23 to 25 eligible countries; it is not a new live download.
