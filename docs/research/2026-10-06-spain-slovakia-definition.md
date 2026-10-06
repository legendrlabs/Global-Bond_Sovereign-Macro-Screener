# Spain research proxy and Slovakia definition hold

Scope: research ranking and trends, accepting existing seven-calendar-day freshness limits. No formula, quote conversion, redistribution or Adjusted approval changes.

## Spain

- Exact series: `D_G0B1F0ZO`, alias `TI_1_3.10`, daily percentages.
- CSV description: unstripped State bonds, 5 years, market as a whole, outright spot transactions.
- [Official daily table 1.3](https://www.bde.es/webbe/en/estadisticas/compartido/datos/pdf/ti_1_3e.pdf) explicitly shows the government-bond 5Y column. Monthly entries are end-of-period, not monthly averages.
- [Table 22.7](https://www.bde.es/webbe/en/estadisticas/compartido/datos/pdf/a2207e.pdf) reports monthly averages and separate turnover buckets. A turnover interval is not proof of the daily 5Y yield selection rule.
- [Chapter 22 notes](https://www.bde.es/webbe/en/estadisticas/compartido/docs/notcp22.pdf) do not settle issue selection or weighting. Mortgage reference rates for 2–6Y debt and auction rates are different series and were not substituted.
- Decision: permit the existing daily official observation as an explicitly disclosed research proxy. Preserve its original definition and unresolved methodological limits.

## Slovakia

- [Current NBS estimated-curve page](https://nbs.sk/en/statistics/financial-markets/interest-rates/estimated-yield-curve/) identifies sovereign zero-coupon estimates using Nelson–Siegel–Svensson, daily observations published weekly. It describes limited market liquidity and estimation uncertainty.
- [2017 NBS analytical note](https://nbs.sk/dokument/d10cacbd-a4fe-4990-b465-134c75a25e33/stiahnut?force=false) explains that zero-coupon and ordinary bond yields can differ by tens of basis points. Its historical uncertainty tests are not a calibrated confidence interval for today's observation.
- [2015 IFP methodology](https://www.mfsr.sk/files/archiv/priloha-stranky/4398/44/ZeroCouponCurveManual.pdf), equation 6, uses exponential discounting in the model. Introductory equation 2 uses discrete discounting. The current NBS page cites this manual with two estimation modifications; this does not independently settle the current workbook output convention.
- A par coupon could be derived from matched discount factors at every coupon payment date after conventions are verified. A lone 5Y zero rate is insufficient. No par calculation has been implemented or represented as an official published value.
- Decision: retain the raw displayed estimate and Baseline exclusion, adding a source-backed explanation. Official-first selection remains unchanged.

No new market collection is claimed by these source-document checks. Provider values and private cached downloads are not bundled in this document.
