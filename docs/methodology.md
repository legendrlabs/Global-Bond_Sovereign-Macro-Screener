# Version 0.1.0-provisional methodology

The fixed universe is the 27 ISO3 countries in `config/countries.yaml`. Results are a research comparison, not orders or allocation advice.

## Baseline

With net debt ND in percentage points of GDP and nominal 5Y yield Y in percentage points:

```
CurrentDebt = 15 * logistic((70 - ND_current) / 15)
FutureDebt  = 25 * logistic((70 - ND_future) / 15)
Balance     = clip(10 + mean(overall balances), 0, 10)
F           = CurrentDebt + FutureDebt + Balance
R           = 25 * (sqrt(1 + Y) - 1)
Baseline    = 2 * sqrt(F * R)
```

Use the Seoul reference year's net debt and the edition's global terminal year. Overall balances include every year from metadata projection-year through that terminal year. A missing intermediate/terminal value does not shorten the period. A reference-year rollover against an older forecast start is flagged and blocks ranking. Negative Y is `BASELINE_DOMAIN_ERROR`; zero Y produces zero, and the formula's top end is not clipped to 100. Gross debt is reported separately and never substitutes for net debt.

An incompatible yield definition can have a provisional formula value for inspection, but `usable_baseline=false` and no rank. Rank eligibility additionally requires a finite current daily observation no older than 7 calendar days, matching country, currency and tenor. Ties use competition ranks 1, 1, 3. Partial-country ranks can exist while global DATA_HOLD remains active.

## Adjusted and FX

Expected inflation is the arithmetic mean of five consecutive WEO forecasts after the reference year. Require all five and the same edition as the fiscal inputs. Real yield is nominal Y minus expected inflation, an approximation with an explicitly different forecast period.

```
FiscalNorm = F / 50
RealYieldNorm = logistic((RealYield - 1.0) / 1.5)
FXNorm = exp(-(FXVol_1y / 0.15)^2)
Adjusted = 100 * FiscalNorm^0.40 * RealYieldNorm^0.30
               * FXNorm^0.20 * MarketQualityNorm^0.10
```

These normalization parameters are provisional, versioned, and not empirically calibrated. All four axes must be present. A missing Market Quality axis leaves Adjusted unavailable; weights remain 0.40 / 0.30 / 0.20 / 0.10. No empirical Market Quality normalization or accepted input pipeline exists yet.

ECB gives currency units per EUR; `KRW_per_currency = KRW_per_EUR / currency_per_EUR`. KRW has identity zero risk. Use sample standard deviation of valid log returns times sqrt(252), in decimal units. A 1Y window requires 200 matched observations; 3Y requires 600. Never forward-fill. Missing currency observations spanning more than five returned provider dates invalidate the window. A conservative weekday bound also rejects gaps longer than five weekdays across the entire response; an exact provider holiday calendar is not yet implemented. Latest currency data older than seven calendar days invalidate FX metrics. Maximum drawdown uses the KRW-per-currency path. Bulgaria's 2026 currency switch is unavailable pending a verified continuity policy; 3Y windows cannot cross an unverified currency start.

## Regimes and availability

Fiscal trend uses ND_future minus ND_current: <= -5 improving, >= 5 deteriorating, otherwise stable. Balance trajectory is separately terminal balance minus starting balance. Real yield: <0 low, 0–2 neutral, >2 high. FX: <8% low, 8–15% medium, >15% high.

Carry requires debt trend, real yield and FX. Negative real yield is unattractive; real yield >2 with low FX risk and non-deteriorating debt is attractive; otherwise neutral. Discount classification requires debt, real yield, and matching 5Y/10Y observations: <0 easing, 0–1 neutral, >1–3 restrictive, >3 highly restrictive. Both nominal yields >=5 with deteriorating debt raise the level once, capped at highly restrictive. Missing required inputs produce UNAVAILABLE.

`safe_to_use` requires all 27 Baseline rows, finite forecast-based real yields and 1Y FX risk for every row, required watch-market 10Y inputs, and no collection errors. It is separate from `safe_to_use_adjusted`. The current release intentionally remains DATA_HOLD. Public-mode rights gates further restrict display/ranks. The data's source date, actual observation date, retrieval time and fiscal edition are distinct fields. A successful HTTP response is not sufficient to pass freshness.

Tests use synthetic examples and literal formula expectations. They are not an authentic April 2026 regression archive. Raw licensed observations plus independently checked expectations must be supplied for that acceptance criterion.
