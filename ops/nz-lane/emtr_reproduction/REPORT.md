# Treasury IncomeExplorer EMTR reproduction audit

## Headline

> RuleSpec does not reproduce the pinned BEFU25 dollar levels—only 3 of 32 weekly net-income points are within $1 (maximum gap $77.62)—although all 32 EMTRs are within 0.45 percentage points, with the material level gaps traced mainly to later-enacted rates for 2026/27 that post-date the forecast vintage.

This is a comparison against the pinned output of Treasury's raw `R/emtr.R#emtr` function, not against the IncomeExplorer UI wrapper. The final matrix has 640 primary cells: 4 scenarios × 8 wage points × 19 dollar/control columns plus EMTR.

## What we can honestly say

> We cannot claim an end-to-end reproduction of IncomeExplorer; this audit provides a reproducible, pointwise comparison of RuleSpec's enacted 2026/27 amount rules against a pinned TY27 BEFU25 output of Treasury's raw `emtr()` function for four stylised families, conditional on explicit host-side eligibility assumptions.

The numerical result is: RuleSpec does not reproduce the pinned BEFU25 dollar levels—only 3 of 32 weekly net-income points are within $1 (maximum gap $77.62)—although all 32 EMTRs are within 0.45 percentage points, with the material level gaps traced mainly to later-enacted rates for 2026/27 that post-date the forecast vintage.

## Result summary

| Measure | Result |
|---|---:|
| Exact numeric matches | 298 / 640 |
| Additional matches inside six-decimal snapshot envelope | 100 |
| Differences outside six-decimal snapshot envelope | 242 / 640 |
| Weekly Net Income within $1 | 3 / 32 |
| Maximum weekly Net Income absolute delta | $77.622294 at `single_parent_three_children_area1_rent`, wage $740 |
| EMTR within 0.5 percentage point | 32 / 32 |
| Maximum EMTR absolute delta | 0.447260 percentage points |
| Remaining class-(a) encoding bugs | 0 |
| Genuinely unexplained class-(d) cells | 0 |

Scenario-level summary:

| Scenario | NI within $1 | Max weekly NI |Δ| | Max EMTR |Δ| (pp) | (b) cells | (c) cells | (a)+(d) |
|---|---:|---:|---:|---:|---:|---:|
| `single_parent_three_children_area1_rent` | 0 / 8 | $77.622294 | 0.447260 | 59 | 17 | 0 |
| `couple_two_children_area2_mortgage` | 0 / 8 | $69.643625 | 0.447260 | 51 | 17 | 0 |
| `couple_one_child_partner_10h_area3_rent` | 0 / 8 | $59.536776 | 0.080137 | 43 | 21 | 0 |
| `single_no_children_area2_no_housing_costs` | 3 / 8 | $2.950000 | 0.004795 | 21 | 13 | 0 |

The comparison treats an absolute delta of at most `0.0000005` as a match because the pinned JSON generator rounded every numeric output to six decimals. Raw deltas are retained in [comparison.csv](comparison.csv) and [comparison.json](comparison.json); they are not zeroed.

## Discrepancy classification

| Class | Cells | Conclusion |
|---|---:|---|
| match | 398 | Exact or within the oracle's six-decimal rounding envelope. |
| (a) our encoding bug | 0 | No class-(a) residual remains in the final matrix. |
| (b) BEFU25 vs enacted law | 174 | Prescribed benefit/credit levels or their downstream effects. |
| (c) unit/period convention | 68 | Annual-cent or complete-dollar statutory arithmetic viewed through a weekly $1 interval. |
| (d) unexplained | 0 | No difference outside the snapshot envelope is assigned class (d) under the documented classification. |

Two genuine class-(a) defects were found during the audit and corrected before this final run. First, the lone-parent Accommodation Supplement cutout initially used the staged SPS/JSS-with-children test; Treasury's source-defined branch combines the lone-parent JSS base with the flat JSS scale. That correction follows Social Security Act 2018 Schedule 2 Income Tests 1 and 3 and is checkpointed in local audit commit `3364877`. Second, the initial AS primary retained Treasury's host conventions for delegated inputs. The final statutory primary instead follows Social Security Regulations 2018 reg 17 (annual eldest FTC divided by 52) and reg 18 (the exact income that extinguishes JSS). Treasury's `365/7` divisor and annual-dollar ceiling are now a labeled diagnostic only. The final sweep's class-(a) count is 0.

Observed reason codes:

| Code | Class | Cells | Evidence |
|---|:---:|---:|---|
| `B_AS_UPSTREAM_VINTAGE` | b | 11 | Accommodation Supplement compound difference, primary vintage — A Treasury-host-aligned diagnostic establishes a BEFU25-versus-enacted benefit/FTC effect. The statutory primary also retains smaller reg 17–18 host conventions: FTC divided by 52 and the exact JSS cutout. |
| `B_BENEFIT_GROSSUP_TAX` | b | 6 | Benefit-vintage tax interaction — Treasury taxes wages incrementally above its forecast-vintage grossed benefit. The enacted benefit rate changes that tax base before the same Schedule 1 tax rates are applied. |
| `B_BENEFIT_VINTAGE` | b | 7 | Main-benefit forecast vintage — Treasury's BEFU25 TY27 rate differs from the enacted 1 April 2026 rate under Social Security Act 2018 Schedule 4 as amended by the Social Security (Rates of Benefits and Allowances) Order 2026 cl 5. |
| `B_COMPOUND_NET_INCOME` | b | 58 | Compound forecast-vintage level difference — At least one material component of net income is a class-(b) benefit or tax-credit vintage difference; smaller class-(c) rounding effects may also be present. |
| `B_WFF_VINTAGE` | b | 92 | Working for Families forecast vintage — The BEFU25 FTC, IWTC, MFTC, or Best Start prescribed amount differs from the amount enacted for 2026/27 under Income Tax Act 2007 ss MD 3, MD 10, ME 1, or MG 2. |
| `C_ACC_ANNUAL_CENTS` | c | 12 | ACC period/rounding convention — Treasury applies an unrounded weekly 1.75% levy. RuleSpec applies the annual including-GST levy and its whole-cent rounding, then converts the result by 365/7 weeks. |
| `C_EMTR_DISCRETE_ROUNDING` | c | 32 | EMTR discrete rounding convention — Both sides use the same weekly $1 forward interval. The residual is caused by RuleSpec's annual-cent ACC rounding and, where applicable, the complete-dollar WFF abatement base before conversion back to a week, with any remaining amount bounded by the oracle's six-decimal display envelope. |
| `C_NET_WAGE_ROUNDING` | c | 24 | Net-wage rounding propagation — The net-wage residual is the propagation of annual-cent ACC rounding through a weekly value (and, for partner wages, the same conversion). |
| `MATCH_SNAPSHOT_PRECISION` | match | 398 | Match at oracle precision — The absolute difference is at most half of the snapshot's six-decimal rounding unit. |

### Class (b): pinned forecast vintage versus enacted 2026/27 law

Treasury commit `741a6ca4f5d27b1dc00b43dc395e39ffc4040a4b` (12 August 2025) pins `TY27_BEFU25.yaml`. RuleSpec selects law effective 1 April 2026. These are different vintages, not errors on either side.

| Parameter | Treasury BEFU25 | RuleSpec enacted | Signed delta | Unit | Statutory source |
|---|---:|---:|---:|---|---|
| Sole Parent Support / lone-parent JSS | 517.39 | 521.52 | 4.13 | NZD/week | Social Security Act 2018 Sch 4 pt 2 cl 1 (SPS) and pt 1 cl 1(f) (lone-parent JSS); Social Security (Rates of Benefits and Allowances) Order 2026 cl 5; `nz/statute/act/public/2018/0032/schedule/4/part/2/clause/lms118467; nz/statute/act/public/2018/0032/schedule/4/part/1/clause/lms118447` |
| JSS partnered with children, each adult | 332.05 | 334.70 | 2.65 | NZD/week | Social Security Act 2018 Sch 4 pt 1 cl 1(g)(ii); Social Security (Rates of Benefits and Allowances) Order 2026 cl 5; `nz/statute/act/public/2018/0032/schedule/4/part/1/clause/lms118447` |
| JSS single, no children | 369.60 | 372.55 | 2.95 | NZD/week | Social Security Act 2018 Sch 4 pt 1 cl 1(d); Social Security (Rates of Benefits and Allowances) Order 2026 cl 5; `nz/statute/act/public/2018/0032/schedule/4/part/1/clause/lms118447` |
| Family Tax Credit, eldest child | 7524.00 | 7921.00 | 397.00 | NZD/year | Income Tax Act 2007 s MD 3(4)(a); Income Tax (Tax Credit) Order 2025 cl 4; `nz/statute/act/public/2007/0097/section/md-3` |
| Family Tax Credit, subsequent child | 6130.00 | 6454.00 | 324.00 | NZD/year | Income Tax Act 2007 s MD 3(4)(b); Income Tax (Tax Credit) Order 2025 cl 4; `nz/statute/act/public/2007/0097/section/md-3` |
| In-Work Tax Credit, base | 5070.00 | 7670.00 | 2600.00 | NZD/year | Income Tax Act 2007 s MD 10(3)(a); Taxation (Annual Rates for 2025-26, Compliance Simplification, and Remedial Measures) Act 2026 ss 2, 105; `nz/statute/act/public/2026/0008/section/105` |
| Minimum Family Tax Credit prescribed amount | 36504.00 | 36604.00 | 100.00 | NZD/year | Income Tax Act 2007 s ME 1(3)(a); Income Tax (Tax Credit) Order 2025 cl 5; `nz/statute/act/public/2007/0097/section/me-1` |
| Best Start prescribed amount, each eligible child | 3838.00 | 4041.00 | 203.00 | NZD/year | Income Tax Act 2007 s MG 2(2)(a); Income Tax (Tax Credit) Order 2025 cl 6; `nz/statute/act/public/2007/0097/section/mg-2` |

The benefit evidence is Social Security Act 2018 Schedule 4 Parts 1–2, as amended by the Social Security (Rates of Benefits and Allowances) Order 2026 clause 5. The WFF evidence is Income Tax Act 2007 ss MD 3, MD 10, ME 1, and MG 2. The [Income Tax (Tax Credit) Order 2025](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2025/260/en/latest/) cls 4–6 establishes the post-snapshot 2026/27 FTC, MFTC, and Best Start amounts. The 2026/27 IWTC $7,670 base is enacted by the Taxation (Annual Rates for 2025-26, Compliance Simplification, and Remedial Measures) Act 2026 ss 2 and 105. Local evidence bundles are:

- `data/corpus/provisions/nz/statute/2026-06-17-social-security-main-benefit-rates.jsonl`
- `data/corpus/provisions/nz/statute/2026-06-17-wff-tax-credits.jsonl`

Accommodation Supplement maxima themselves do not explain the 11 AS differences outside the envelope. Each AS row is decomposed into (1) the BEFU25-versus-enacted difference under Treasury's own host conventions and (2) the additional statutory host-convention difference: reg 17 divides annual eldest FTC by 52, while raw Treasury divides by `365/7`; reg 18 uses the exact JSS vanishing point, while raw Treasury applies an annual-dollar ceiling. A row is class (b) only when its Treasury-host-aligned diagnostic independently has a vintage difference; the smaller class-(c) component is disclosed rather than folded into the vintage claim. The primary matrix uses RuleSpec's statutory inputs before reg 19 whole-dollar rounding. All components and the legally rounded payment are preserved in [as_rounding_diagnostic.csv](as_rounding_diagnostic.csv).

### Class (c): period and rounding convention

The engine performs no automatic period conversion. The harness uses these explicit alignments:

| Component | RuleSpec source period | Treasury comparison |
|---|---|---|
| Main benefits | Weekly amount (despite a legacy `period: Year` label) | No conversion |
| Income tax, ACC, FTC, Best Start, IETC | Annual | Divide by `365/7` |
| IWTC base and MFTC | Annual rules expressed over weekly periods | Divide by `52` |
| IWTC abatement | Annual | Divide by `365/7`, then subtract from the `/52` base |
| WFF total | Mixed | Add converted FTC and IWTC components; do not divide the aggregate once |
| Winter Energy Payment | Per-winter total | Divide by `365/7` to match Treasury's annual-average snapshot convention |
| Accommodation Supplement | Weekly; reg 17 annual FTC input is divided by 52 | No output conversion; compare the statutory-input pre-round amount and emit a Treasury-host-aligned diagnostic |

Treasury applies ACC as an unrounded weekly 1.75%. RuleSpec applies the annual including-GST PAYE levy and whole-cent rounding before weekly conversion. The RuleSpec source is Accident Compensation (Earners' Levy) Regulations 2025 regs 4, 5, and 8 plus Inland Revenue's 1.75% PAYE-facing rate; local evidence is `data/corpus/provisions/nz/regulation/2026-06-17-acc-earners-levy-2025-formulas.jsonl` and `data/corpus/provisions/nz/agency/2026-06-17-ird-acc-levy-rates.jsonl`.

All 32 EMTR residuals fall into 4 source-consistent numerical patterns. For each interval the harness calculates the RuleSpec annual-cent ACC component and MD 13 complete-dollar WFF component; any remainder must fit inside the oracle's six-decimal envelope before this report is written:

| RuleSpec − Treasury EMTR | Percentage points | Points | WFF-affected | Max display remainder | Decomposition |
|---:|---:|---:|---:|---:|---|
| -0.000801369863 | -0.080136986 | 5 | 5 | 0.000000000000 | ACC annual-cent rounding plus MD 13 complete-dollar WFF arithmetic and at most six-decimal oracle display rounding |
| -0.000047945205 | -0.004794520 | 23 | 0 | 0.000000000000 | ACC annual-cent rounding and at most six-decimal oracle display rounding |
| -0.000047548557 | -0.004754856 | 2 | 0 | 0.000000396648 | ACC annual-cent rounding and at most six-decimal oracle display rounding |
| 0.004472602740 | 0.447260274 | 2 | 2 | 0.000000000000 | ACC annual-cent rounding plus MD 13 complete-dollar WFF arithmetic and at most six-decimal oracle display rounding |

The 7 WFF-affected intervals are consistent with the interaction between Income Tax Act 2007 s MD 13's complete-dollar abatement base and a $1 weekly step (`365/7` annual dollars). The other 25 intervals have no computed WFF component. The maximum remainder after ACC and WFF decomposition is `0.000000396648044692737430169178082191779`, within the six-decimal JSON envelope. This calculation supports class (c) for the EMTR rows; any interval outside that envelope would be classified (d).

## Method

1. Verify the pinned oracle commit, parameter-file hash, RuleSpec SHA, engine SHA, composition hash, and clean tracked RuleSpec and engine source trees.
2. Compile the ten-module composition from scratch in a temporary directory and execute every query in engine `explain` mode.
3. Map each stylised profile to explicit person, child, and family inputs. The compiled program has no relations, so aggregation is performed transparently in the host harness.
   Treasury's raw branch threshold `1226.7 / 52.2 = $23.50/week` is retained host-side: when the pinned model enables IWTC and disallows IWTC to beneficiaries, that branch zeroes benefit amounts. This is a disclosed raw-source flow convention, not a RuleSpec policy parameter.
   Wage tax is calculated as tax on grossed taxable benefit plus wages minus tax on grossed taxable benefit, matching raw `emtr()` rather than taxing wages in isolation.
4. Evaluate the eight displayed weekly wages plus each hidden `w+1` endpoint and `$1,499`.
5. Calculate `EMTR = 1 - (NetIncome(w+1) - NetIncome(w))`. At the $1,500 display point, carry the `$1,499 → $1,500` interval, exactly matching Treasury's `zoo::na.locf` endpoint convention.
6. Compare RuleSpec against Treasury without replacing or tuning any RuleSpec parameter. Signed deltas are always RuleSpec minus Treasury; the report matrix shows absolute and relative deltas.

Treasury's app does something different: its server calls `calculate_income()`, whose `WFF_or_Benefit: Max` wrapper may select between transfers. The pinned snapshot explicitly calls raw `emtr()` and bypasses that wrapper, so this audit does too.

## Coverage gaps

This is a conditional amount comparison, not a legal entitlement determination. The snapshot supplies only partnered status, an hourly wage, child ages, partner wage/hours, housing costs/type, and AS area. It does not supply all facts required by the statutes.

- Main-benefit residence, immigration, work availability, medical, student, strike, concurrent-benefit, and other entitlement facts are not established. Adult age 25 and other profile facts are host assumptions. The amount schedules are evaluated conditionally.
- FTC and Best Start use full-year entitlement days and full care for the listed children. Full principal-caregiver, residence, shared-care, date-of-birth/due-date, and parental-leave conditions are not established.
- IWTC's statutory eligibility closure is populated with explicit stylised assumptions because the snapshot omits those facts. MFTC full-time/no-benefit eligibility is inferred from the raw model's profile convention.
- IETC residence and disqualifying-support conditions are assumed, not evidenced by the snapshot.
- Winter Energy Payment uses the RuleSpec per-winter rate, host-gated only when the RuleSpec-side reconstruction has positive net benefit (mirroring Treasury's raw gate), and annual-averaged. Full legal entitlement, election, absence, and care-facility rules under Social Security Act 2018 ss 71–75 and 220 are not evaluated.
- Accommodation Supplement compares the amount formula before legal rounding and assumes eligibility/takeup. Assets, social housing, student allowance, residential/disability care, duplicate partner claims, and other ss 65–69 exclusions are not evaluated.
- The lone-parent profile in this grid has children aged 0, 1, and 10. The harness does not generalise Treasury's separate lone-parent JSS branch for a youngest child aged 14 or over.
- The only profile with two Best Start-aged children remains below the $79,000 abatement threshold throughout the requested grid. This audit therefore does not test Treasury's aggregate-child abatement against RuleSpec's per-child composition above that threshold.
- RR and PTR are computed and emitted in [secondary_rates.csv](secondary_rates.csv), but are outside the requested dollar-plus-EMTR validation matrix.
- Person/child/family aggregation is host-side because the compiled composition has no relations.

Treasury itself describes the UI profiles as theoretical, assumes full AS take-up, omits the AS asset test, and excludes NZ Super, FamilyBoost, Supported Living Payment, youth payments, IRRS/TAS, KiwiSaver, student loans/allowances, paid parental leave, and child support pass-on. Those programs are not silently filled in here.

## Provenance and reproducibility

| Item | Verified value |
|---|---|
| Oracle snapshot SHA-256 | `3f4ea311825b316d63910ce37c18e5980ef256df89d1eb5ec8442b4d1351c3c5` |
| Treasury commit | `741a6ca4f5d27b1dc00b43dc395e39ffc4040a4b` |
| Treasury parameter SHA-256 | `de89898c78989e057bde7d006b725fed4615ff32731ad008b96148c5a74b683c` |
| RuleSpec commit | `89a7d25dc03a4d045348620283332de10b1047da` |
| Engine source checkout commit | `d59969b53430ae2fd97eb4349d44ad23ce930d85` |
| Executed engine binary SHA-256 | `56fbffea1e0e32c52b6fcbddbca76223bb185b33b49368c288e0c7213b0126e1` |
| Composition SHA-256 | `af2ce73f1b16a74603965db1da92991545838748e943f3ed81cef394d469c3b0` |
| Compiled artifact SHA-256 | `b1d72c1f4840a1774aefbddc9692e22a79ced26cde6c44efb4c01fc394a15c33` |
| Compiled derived outputs | 176 total (174 imported + 2 bridge rules) |
| Compiled parameters | 129 |
| Compiled input slots | 328 |
| Engine evaluations in one fresh pass | 377 |
| Tax-year interval | `2026-04-01` to `2027-03-31` |

Run from the Foundation workspace:

```sh
python3 ops/nz-lane/emtr_reproduction/run.py
```

The command performs two independent fresh compilations and evaluations in temporary directories, compares every generated artifact byte-for-byte, and only then writes the output files. `SHA256SUMS` covers every report/data artifact. No network access or manual intermediate file is required.

This should not yet graduate into `rulespec-nz` as a claim of Treasury reproduction. After the entitlement closures and the forecast-vintage/enacted-law baseline are made explicit product choices, the pinned matrix would be valuable as a dual-vintage regression test.

## Full comparison matrix

Values are weekly unless the unit says annual. `|Δ|` is the absolute delta; relative delta is `|RuleSpec − Treasury| / |Treasury|`. An exact zero-over-zero match is shown as `0%`; otherwise a zero Treasury denominator is `n/a`. The exact signed deltas and unrounded engine decimals are in [comparison.csv](comparison.csv).

### `single_parent_three_children_area1_rent`

Single parent, children aged 0, 1, and 10, Area 1 rent.

| Wage | Metric | Unit | Treasury | RuleSpec | Abs delta | Relative | Class |
|---:|---|---|---:|---:|---:|---:|---|
| 0 | `gross_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `hours1` | hours/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage1_annual` | NZD/year | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_tax` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_ACC_levy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_benefit` | NZD/week | 517.390000 | 521.520000 | 4.130000000 | 0.798237% | (b) `B_BENEFIT_VINTAGE` |
| 0 | `FTC_abated` | NZD/week | 379.419178 | 399.460274 | 20.041095973 | 5.282046% | (b) `B_WFF_VINTAGE` |
| 0 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `WinterEnergy` | NZD/week | 13.424658 | 13.424658 | 0.000000466 | 0.000003% | match |
| 0 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 0 | `AS_Amount` | NZD/week | 304.204969 | 302.076788 | 2.128180538 | 0.699588% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 0 | `WFF_abated` | NZD/week | 379.419178 | 399.460274 | 20.041095973 | 5.282046% | (b) `B_WFF_VINTAGE` |
| 0 | `Net_Income` | NZD/week | 1361.649764 | 1391.478980 | 29.829216242 | 2.190667% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `Net_Income_annual` | NZD/year | 71000.309107 | 72555.689684 | 1555.380577066 | 2.190667% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `EMTR` | ratio | 0.192500 | 0.192452 | 0.000047945 | 0.024907% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 160 | `gross_wage1` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 160 | `hours1` | hours/week | 8.648649 | 8.648649 | 0.000000351 | 0.000004% | match |
| 160 | `gross_wage1_annual` | NZD/year | 8342.857143 | 8342.857143 | 0.000000143 | 0.000000% | match |
| 160 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_tax` | NZD/week | 16.800000 | 16.800000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_ACC_levy` | NZD/week | 2.800000 | 2.800000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage1` | NZD/week | 140.400000 | 140.400000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage` | NZD/week | 140.400000 | 140.400000 | 0.000000000 | 0.000000% | match |
| 160 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `FTC_abated` | NZD/week | 379.419178 | 399.460274 | 20.041095973 | 5.282046% | (b) `B_WFF_VINTAGE` |
| 160 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 160 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 160 | `AS_Amount` | NZD/week | 304.204969 | 302.076788 | 2.128180538 | 0.699588% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 160 | `WFF_abated` | NZD/week | 476.919178 | 546.960274 | 70.041095973 | 14.686156% | (b) `B_WFF_VINTAGE` |
| 160 | `Net_Income` | NZD/week | 1068.735106 | 1144.434323 | 75.699216708 | 7.083066% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `Net_Income_annual` | NZD/year | 55726.901964 | 59674.075398 | 3947.173434352 | 7.083066% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `EMTR` | ratio | 0.122500 | 0.122452 | 0.000047945 | 0.039139% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 250 | `gross_wage1` | NZD/week | 250.000000 | 250.000000 | 0.000000000 | 0.000000% | match |
| 250 | `hours1` | hours/week | 13.513514 | 13.513514 | 0.000000486 | 0.000004% | match |
| 250 | `gross_wage1_annual` | NZD/year | 13035.714286 | 13035.714286 | 0.000000286 | 0.000000% | match |
| 250 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_tax` | NZD/week | 26.250000 | 26.250000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_ACC_levy` | NZD/week | 4.375000 | 4.375096 | 0.000095890 | 0.002192% | (c) `C_ACC_ANNUAL_CENTS` |
| 250 | `net_wage1` | NZD/week | 219.375000 | 219.374904 | 0.000095890 | 0.000044% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_wage` | NZD/week | 219.375000 | 219.374904 | 0.000095890 | 0.000044% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `FTC_abated` | NZD/week | 379.419178 | 399.460274 | 20.041095973 | 5.282046% | (b) `B_WFF_VINTAGE` |
| 250 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 250 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 250 | `AS_Amount` | NZD/week | 304.204969 | 302.076788 | 2.128180538 | 0.699588% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 250 | `WFF_abated` | NZD/week | 476.919178 | 546.960274 | 70.041095973 | 14.686156% | (b) `B_WFF_VINTAGE` |
| 250 | `Net_Income` | NZD/week | 1147.710106 | 1223.409227 | 75.699120818 | 6.595666% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `Net_Income_annual` | NZD/year | 59844.884107 | 63792.052541 | 3947.168434209 | 6.595666% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `EMTR` | ratio | 0.122500 | 0.122452 | 0.000047945 | 0.039139% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 370 | `gross_wage1` | NZD/week | 370.000000 | 370.000000 | 0.000000000 | 0.000000% | match |
| 370 | `hours1` | hours/week | 20.000000 | 20.000000 | 0.000000000 | 0.000000% | match |
| 370 | `gross_wage1_annual` | NZD/year | 19292.857143 | 19292.857143 | 0.000000143 | 0.000000% | match |
| 370 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `wage1_tax` | NZD/week | 43.807534 | 43.807534 | 0.000000247 | 0.000001% | match |
| 370 | `wage1_ACC_levy` | NZD/week | 6.475000 | 6.475096 | 0.000095890 | 0.001481% | (c) `C_ACC_ANNUAL_CENTS` |
| 370 | `net_wage1` | NZD/week | 319.717466 | 319.717370 | 0.000096137 | 0.000030% | (c) `C_NET_WAGE_ROUNDING` |
| 370 | `net_wage` | NZD/week | 319.717466 | 319.717370 | 0.000096137 | 0.000030% | (c) `C_NET_WAGE_ROUNDING` |
| 370 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `FTC_abated` | NZD/week | 379.419178 | 399.460274 | 20.041095973 | 5.282046% | (b) `B_WFF_VINTAGE` |
| 370 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 370 | `MFTC` | NZD/week | 375.807534 | 377.730611 | 1.923077170 | 0.511719% | (b) `B_WFF_VINTAGE` |
| 370 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 370 | `AS_Amount` | NZD/week | 304.204969 | 302.076788 | 2.128180538 | 0.699588% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 370 | `WFF_abated` | NZD/week | 476.919178 | 546.960274 | 70.041095973 | 14.686156% | (b) `B_WFF_VINTAGE` |
| 370 | `Net_Income` | NZD/week | 1623.860106 | 1701.482304 | 77.622197741 | 4.780104% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `Net_Income_annual` | NZD/year | 84672.705536 | 88720.148695 | 4047.443159055 | 4.780104% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `EMTR` | ratio | 1.017500 | 1.017452 | 0.000047945 | 0.004712% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 555 | `gross_wage1` | NZD/week | 555.000000 | 555.000000 | 0.000000000 | 0.000000% | match |
| 555 | `hours1` | hours/week | 30.000000 | 30.000000 | 0.000000000 | 0.000000% | match |
| 555 | `gross_wage1_annual` | NZD/year | 28939.285714 | 28939.285714 | 0.000000286 | 0.000000% | match |
| 555 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `wage1_tax` | NZD/week | 76.182534 | 76.182534 | 0.000000247 | 0.000000% | match |
| 555 | `wage1_ACC_levy` | NZD/week | 9.712500 | 9.712548 | 0.000047945 | 0.000494% | (c) `C_ACC_ANNUAL_CENTS` |
| 555 | `net_wage1` | NZD/week | 469.104966 | 469.104918 | 0.000048192 | 0.000010% | (c) `C_NET_WAGE_ROUNDING` |
| 555 | `net_wage` | NZD/week | 469.104966 | 469.104918 | 0.000048192 | 0.000010% | (c) `C_NET_WAGE_ROUNDING` |
| 555 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `FTC_abated` | NZD/week | 379.419178 | 399.460274 | 20.041095973 | 5.282046% | (b) `B_WFF_VINTAGE` |
| 555 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 555 | `MFTC` | NZD/week | 223.182534 | 225.105611 | 1.923077170 | 0.861661% | (b) `B_WFF_VINTAGE` |
| 555 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 555 | `AS_Amount` | NZD/week | 304.204969 | 302.076788 | 2.128180538 | 0.699588% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 555 | `WFF_abated` | NZD/week | 476.919178 | 546.960274 | 70.041095973 | 14.686156% | (b) `B_WFF_VINTAGE` |
| 555 | `Net_Income` | NZD/week | 1620.622606 | 1698.244852 | 77.622245686 | 4.789656% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `Net_Income_annual` | NZD/year | 84503.893036 | 88551.338695 | 4047.445659055 | 4.789656% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `EMTR` | ratio | 1.017500 | 1.017452 | 0.000047945 | 0.004712% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 740 | `gross_wage1` | NZD/week | 740.000000 | 740.000000 | 0.000000000 | 0.000000% | match |
| 740 | `hours1` | hours/week | 40.000000 | 40.000000 | 0.000000000 | 0.000000% | match |
| 740 | `gross_wage1_annual` | NZD/year | 38585.714286 | 38585.714286 | 0.000000286 | 0.000000% | match |
| 740 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `wage1_tax` | NZD/week | 108.557534 | 108.557534 | 0.000000247 | 0.000000% | match |
| 740 | `wage1_ACC_levy` | NZD/week | 12.950000 | 12.950000 | 0.000000000 | 0.000000% | match |
| 740 | `net_wage1` | NZD/week | 618.492466 | 618.492466 | 0.000000247 | 0.000000% | match |
| 740 | `net_wage` | NZD/week | 618.492466 | 618.492466 | 0.000000247 | 0.000000% | match |
| 740 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `FTC_abated` | NZD/week | 379.419178 | 399.460274 | 20.041095973 | 5.282046% | (b) `B_WFF_VINTAGE` |
| 740 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 740 | `MFTC` | NZD/week | 70.557534 | 72.480611 | 1.923077170 | 2.725545% | (b) `B_WFF_VINTAGE` |
| 740 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 740 | `AS_Amount` | NZD/week | 304.204969 | 302.076788 | 2.128180538 | 0.699588% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 740 | `WFF_abated` | NZD/week | 476.919178 | 546.960274 | 70.041095973 | 14.686156% | (b) `B_WFF_VINTAGE` |
| 740 | `Net_Income` | NZD/week | 1617.385106 | 1695.007400 | 77.622293631 | 4.799246% | (b) `B_COMPOUND_NET_INCOME` |
| 740 | `Net_Income_annual` | NZD/year | 84335.080536 | 88382.528695 | 4047.448159055 | 4.799246% | (b) `B_COMPOUND_NET_INCOME` |
| 740 | `EMTR` | ratio | 1.017500 | 1.017452 | 0.000047945 | 0.004712% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1000 | `gross_wage1` | NZD/week | 1000.000000 | 1000.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `hours1` | hours/week | 54.054054 | 54.054054 | 0.000000054 | 0.000000% | match |
| 1000 | `gross_wage1_annual` | NZD/year | 52142.857143 | 52142.857143 | 0.000000143 | 0.000000% | match |
| 1000 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `wage1_tax` | NZD/week | 154.057534 | 154.057534 | 0.000000247 | 0.000000% | match |
| 1000 | `wage1_ACC_levy` | NZD/week | 17.500000 | 17.500000 | 0.000000000 | 0.000000% | match |
| 1000 | `net_wage1` | NZD/week | 828.442466 | 828.442466 | 0.000000247 | 0.000000% | match |
| 1000 | `net_wage` | NZD/week | 828.442466 | 828.442466 | 0.000000247 | 0.000000% | match |
| 1000 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `FTC_abated` | NZD/week | 341.220548 | 361.266164 | 20.045616384 | 5.874680% | (b) `B_WFF_VINTAGE` |
| 1000 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 1000 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 1000 | `AS_Amount` | NZD/week | 278.991271 | 278.333931 | 0.657339681 | 0.235613% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 1000 | `WFF_abated` | NZD/week | 438.720548 | 508.766164 | 70.045616384 | 15.965885% | (b) `B_WFF_VINTAGE` |
| 1000 | `Net_Income` | NZD/week | 1693.365243 | 1770.539822 | 77.174578730 | 4.557468% | (b) `B_COMPOUND_NET_INCOME` |
| 1000 | `Net_Income_annual` | NZD/year | 88296.901964 | 92321.004990 | 4024.103026188 | 4.557468% | (b) `B_COMPOUND_NET_INCOME` |
| 1000 | `EMTR` | ratio | 0.717500 | 0.721973 | 0.004472603 | 0.623359% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1500 | `gross_wage1` | NZD/week | 1500.000000 | 1500.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `hours1` | hours/week | 81.081081 | 81.081081 | 0.000000081 | 0.000000% | match |
| 1500 | `gross_wage1_annual` | NZD/year | 78214.285714 | 78214.285714 | 0.000000286 | 0.000000% | match |
| 1500 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `wage1_tax` | NZD/week | 300.869863 | 300.869863 | 0.000000014 | 0.000000% | match |
| 1500 | `wage1_ACC_levy` | NZD/week | 26.250000 | 26.250000 | 0.000000000 | 0.000000% | match |
| 1500 | `net_wage1` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `net_wage` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `FTC_abated` | NZD/week | 203.720548 | 223.763151 | 20.042602685 | 9.838282% | (b) `B_WFF_VINTAGE` |
| 1500 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 1500 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `BestStart_Total` | NZD/week | 147.210959 | 154.997260 | 7.786301274 | 5.289213% | (b) `B_WFF_VINTAGE` |
| 1500 | `AS_Amount` | NZD/week | 153.991271 | 153.333931 | 0.657339681 | 0.426868% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 1500 | `WFF_abated` | NZD/week | 301.220548 | 371.263151 | 70.042602685 | 23.252930% | (b) `B_WFF_VINTAGE` |
| 1500 | `Net_Income` | NZD/week | 1775.302914 | 1852.474479 | 77.171565264 | 4.346952% | (b) `B_COMPOUND_NET_INCOME` |
| 1500 | `Net_Income_annual` | NZD/year | 92569.366250 | 96593.312133 | 4023.945883046 | 4.346952% | (b) `B_COMPOUND_NET_INCOME` |
| 1500 | `EMTR` | ratio | 0.872500 | 0.871699 | 0.000801370 | 0.091848% | (c) `C_EMTR_DISCRETE_ROUNDING` |

### `couple_two_children_area2_mortgage`

Couple, children aged 2 and 15, partner not working, Area 2 mortgage.

| Wage | Metric | Unit | Treasury | RuleSpec | Abs delta | Relative | Class |
|---:|---|---|---:|---:|---:|---:|---|
| 0 | `gross_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `hours1` | hours/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage1_annual` | NZD/year | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_tax` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_ACC_levy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_benefit` | NZD/week | 664.100000 | 669.400000 | 5.300000000 | 0.798073% | (b) `B_BENEFIT_VINTAGE` |
| 0 | `FTC_abated` | NZD/week | 261.857534 | 275.684932 | 13.827397507 | 5.280504% | (b) `B_WFF_VINTAGE` |
| 0 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `WinterEnergy` | NZD/week | 13.424658 | 13.424658 | 0.000000466 | 0.000003% | match |
| 0 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 0 | `AS_Amount` | NZD/week | 220.000000 | 220.000000 | 0.000000000 | 0.000000% | match |
| 0 | `WFF_abated` | NZD/week | 261.857534 | 275.684932 | 13.827397507 | 5.280504% | (b) `B_WFF_VINTAGE` |
| 0 | `Net_Income` | NZD/week | 1232.987671 | 1256.008219 | 23.020548178 | 1.867054% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `Net_Income_annual` | NZD/year | 64291.500000 | 65491.857143 | 1200.357142857 | 1.867054% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `EMTR` | ratio | 0.192500 | 0.192452 | 0.000047945 | 0.024907% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 160 | `gross_wage1` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 160 | `hours1` | hours/week | 8.648649 | 8.648649 | 0.000000351 | 0.000004% | match |
| 160 | `gross_wage1_annual` | NZD/year | 8342.857143 | 8342.857143 | 0.000000143 | 0.000000% | match |
| 160 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_tax` | NZD/week | 16.800000 | 16.800000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_ACC_levy` | NZD/week | 2.800000 | 2.800000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage1` | NZD/week | 140.400000 | 140.400000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage` | NZD/week | 140.400000 | 140.400000 | 0.000000000 | 0.000000% | match |
| 160 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `FTC_abated` | NZD/week | 261.857534 | 275.684932 | 13.827397507 | 5.280504% | (b) `B_WFF_VINTAGE` |
| 160 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 160 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 160 | `AS_Amount` | NZD/week | 220.000000 | 220.000000 | 0.000000000 | 0.000000% | match |
| 160 | `WFF_abated` | NZD/week | 359.357534 | 423.184932 | 63.827397507 | 17.761530% | (b) `B_WFF_VINTAGE` |
| 160 | `Net_Income` | NZD/week | 793.363014 | 861.083562 | 67.720547644 | 8.535884% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `Net_Income_annual` | NZD/year | 41368.214286 | 44899.357143 | 3531.142856857 | 8.535884% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `EMTR` | ratio | 0.122500 | 0.122452 | 0.000047945 | 0.039139% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 250 | `gross_wage1` | NZD/week | 250.000000 | 250.000000 | 0.000000000 | 0.000000% | match |
| 250 | `hours1` | hours/week | 13.513514 | 13.513514 | 0.000000486 | 0.000004% | match |
| 250 | `gross_wage1_annual` | NZD/year | 13035.714286 | 13035.714286 | 0.000000286 | 0.000000% | match |
| 250 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_tax` | NZD/week | 26.250000 | 26.250000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_ACC_levy` | NZD/week | 4.375000 | 4.375096 | 0.000095890 | 0.002192% | (c) `C_ACC_ANNUAL_CENTS` |
| 250 | `net_wage1` | NZD/week | 219.375000 | 219.374904 | 0.000095890 | 0.000044% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_wage` | NZD/week | 219.375000 | 219.374904 | 0.000095890 | 0.000044% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `FTC_abated` | NZD/week | 261.857534 | 275.684932 | 13.827397507 | 5.280504% | (b) `B_WFF_VINTAGE` |
| 250 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 250 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 250 | `AS_Amount` | NZD/week | 220.000000 | 220.000000 | 0.000000000 | 0.000000% | match |
| 250 | `WFF_abated` | NZD/week | 359.357534 | 423.184932 | 63.827397507 | 17.761530% | (b) `B_WFF_VINTAGE` |
| 250 | `Net_Income` | NZD/week | 872.338014 | 940.058466 | 67.720451753 | 7.763098% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `Net_Income_annual` | NZD/year | 45486.196429 | 49017.334286 | 3531.137856714 | 7.763098% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `EMTR` | ratio | 0.122500 | 0.122452 | 0.000047945 | 0.039139% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 370 | `gross_wage1` | NZD/week | 370.000000 | 370.000000 | 0.000000000 | 0.000000% | match |
| 370 | `hours1` | hours/week | 20.000000 | 20.000000 | 0.000000000 | 0.000000% | match |
| 370 | `gross_wage1_annual` | NZD/year | 19292.857143 | 19292.857143 | 0.000000143 | 0.000000% | match |
| 370 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `wage1_tax` | NZD/week | 43.807534 | 43.807534 | 0.000000247 | 0.000001% | match |
| 370 | `wage1_ACC_levy` | NZD/week | 6.475000 | 6.475096 | 0.000095890 | 0.001481% | (c) `C_ACC_ANNUAL_CENTS` |
| 370 | `net_wage1` | NZD/week | 319.717466 | 319.717370 | 0.000096137 | 0.000030% | (c) `C_NET_WAGE_ROUNDING` |
| 370 | `net_wage` | NZD/week | 319.717466 | 319.717370 | 0.000096137 | 0.000030% | (c) `C_NET_WAGE_ROUNDING` |
| 370 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `FTC_abated` | NZD/week | 261.857534 | 275.684932 | 13.827397507 | 5.280504% | (b) `B_WFF_VINTAGE` |
| 370 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 370 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 370 | `AS_Amount` | NZD/week | 220.000000 | 220.000000 | 0.000000000 | 0.000000% | match |
| 370 | `WFF_abated` | NZD/week | 359.357534 | 423.184932 | 63.827397507 | 17.761530% | (b) `B_WFF_VINTAGE` |
| 370 | `Net_Income` | NZD/week | 972.680479 | 1040.400932 | 67.720452507 | 6.962251% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `Net_Income_annual` | NZD/year | 50718.339286 | 54249.477143 | 3531.137856857 | 6.962251% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `EMTR` | ratio | 0.192500 | 0.192452 | 0.000047945 | 0.024907% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 555 | `gross_wage1` | NZD/week | 555.000000 | 555.000000 | 0.000000000 | 0.000000% | match |
| 555 | `hours1` | hours/week | 30.000000 | 30.000000 | 0.000000000 | 0.000000% | match |
| 555 | `gross_wage1_annual` | NZD/year | 28939.285714 | 28939.285714 | 0.000000286 | 0.000000% | match |
| 555 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `wage1_tax` | NZD/week | 76.182534 | 76.182534 | 0.000000247 | 0.000000% | match |
| 555 | `wage1_ACC_levy` | NZD/week | 9.712500 | 9.712548 | 0.000047945 | 0.000494% | (c) `C_ACC_ANNUAL_CENTS` |
| 555 | `net_wage1` | NZD/week | 469.104966 | 469.104918 | 0.000048192 | 0.000010% | (c) `C_NET_WAGE_ROUNDING` |
| 555 | `net_wage` | NZD/week | 469.104966 | 469.104918 | 0.000048192 | 0.000010% | (c) `C_NET_WAGE_ROUNDING` |
| 555 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `FTC_abated` | NZD/week | 261.857534 | 275.684932 | 13.827397507 | 5.280504% | (b) `B_WFF_VINTAGE` |
| 555 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 555 | `MFTC` | NZD/week | 223.182534 | 225.105611 | 1.923077170 | 0.861661% | (b) `B_WFF_VINTAGE` |
| 555 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 555 | `AS_Amount` | NZD/week | 220.000000 | 220.000000 | 0.000000000 | 0.000000% | match |
| 555 | `WFF_abated` | NZD/week | 359.357534 | 423.184932 | 63.827397507 | 17.761530% | (b) `B_WFF_VINTAGE` |
| 555 | `Net_Income` | NZD/week | 1345.250514 | 1414.894091 | 69.643576622 | 5.176997% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `Net_Income_annual` | NZD/year | 70145.205357 | 73776.620440 | 3631.415082560 | 5.176997% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `EMTR` | ratio | 1.017500 | 1.017452 | 0.000047945 | 0.004712% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 740 | `gross_wage1` | NZD/week | 740.000000 | 740.000000 | 0.000000000 | 0.000000% | match |
| 740 | `hours1` | hours/week | 40.000000 | 40.000000 | 0.000000000 | 0.000000% | match |
| 740 | `gross_wage1_annual` | NZD/year | 38585.714286 | 38585.714286 | 0.000000286 | 0.000000% | match |
| 740 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `wage1_tax` | NZD/week | 108.557534 | 108.557534 | 0.000000247 | 0.000000% | match |
| 740 | `wage1_ACC_levy` | NZD/week | 12.950000 | 12.950000 | 0.000000000 | 0.000000% | match |
| 740 | `net_wage1` | NZD/week | 618.492466 | 618.492466 | 0.000000247 | 0.000000% | match |
| 740 | `net_wage` | NZD/week | 618.492466 | 618.492466 | 0.000000247 | 0.000000% | match |
| 740 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `FTC_abated` | NZD/week | 261.857534 | 275.684932 | 13.827397507 | 5.280504% | (b) `B_WFF_VINTAGE` |
| 740 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 740 | `MFTC` | NZD/week | 70.557534 | 72.480611 | 1.923077170 | 2.725545% | (b) `B_WFF_VINTAGE` |
| 740 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 740 | `AS_Amount` | NZD/week | 220.000000 | 220.000000 | 0.000000000 | 0.000000% | match |
| 740 | `WFF_abated` | NZD/week | 359.357534 | 423.184932 | 63.827397507 | 17.761530% | (b) `B_WFF_VINTAGE` |
| 740 | `Net_Income` | NZD/week | 1342.013014 | 1411.656639 | 69.643624567 | 5.189490% | (b) `B_COMPOUND_NET_INCOME` |
| 740 | `Net_Income_annual` | NZD/year | 69976.392857 | 73607.810440 | 3631.417582560 | 5.189490% | (b) `B_COMPOUND_NET_INCOME` |
| 740 | `EMTR` | ratio | 1.017500 | 1.017452 | 0.000047945 | 0.004712% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1000 | `gross_wage1` | NZD/week | 1000.000000 | 1000.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `hours1` | hours/week | 54.054054 | 54.054054 | 0.000000054 | 0.000000% | match |
| 1000 | `gross_wage1_annual` | NZD/year | 52142.857143 | 52142.857143 | 0.000000143 | 0.000000% | match |
| 1000 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `wage1_tax` | NZD/week | 154.057534 | 154.057534 | 0.000000247 | 0.000000% | match |
| 1000 | `wage1_ACC_levy` | NZD/week | 17.500000 | 17.500000 | 0.000000000 | 0.000000% | match |
| 1000 | `net_wage1` | NZD/week | 828.442466 | 828.442466 | 0.000000247 | 0.000000% | match |
| 1000 | `net_wage` | NZD/week | 828.442466 | 828.442466 | 0.000000247 | 0.000000% | match |
| 1000 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `FTC_abated` | NZD/week | 223.658904 | 237.490822 | 13.831917918 | 6.184381% | (b) `B_WFF_VINTAGE` |
| 1000 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 1000 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 1000 | `AS_Amount` | NZD/week | 220.000000 | 220.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `WFF_abated` | NZD/week | 321.158904 | 384.990822 | 63.831917918 | 19.875494% | (b) `B_WFF_VINTAGE` |
| 1000 | `Net_Income` | NZD/week | 1443.206849 | 1510.931918 | 67.725068808 | 4.692679% | (b) `B_COMPOUND_NET_INCOME` |
| 1000 | `Net_Income_annual` | NZD/year | 75252.928571 | 78784.307143 | 3531.378571857 | 4.692679% | (b) `B_COMPOUND_NET_INCOME` |
| 1000 | `EMTR` | ratio | 0.467500 | 0.471973 | 0.004472603 | 0.956706% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1500 | `gross_wage1` | NZD/week | 1500.000000 | 1500.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `hours1` | hours/week | 81.081081 | 81.081081 | 0.000000081 | 0.000000% | match |
| 1500 | `gross_wage1_annual` | NZD/year | 78214.285714 | 78214.285714 | 0.000000286 | 0.000000% | match |
| 1500 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `wage1_tax` | NZD/week | 300.869863 | 300.869863 | 0.000000014 | 0.000000% | match |
| 1500 | `wage1_ACC_levy` | NZD/week | 26.250000 | 26.250000 | 0.000000000 | 0.000000% | match |
| 1500 | `net_wage1` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `net_wage` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `FTC_abated` | NZD/week | 86.158904 | 99.987808 | 13.828904219 | 16.050464% | (b) `B_WFF_VINTAGE` |
| 1500 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 1500 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `BestStart_Total` | NZD/week | 73.605479 | 77.498630 | 3.893151137 | 5.289214% | (b) `B_WFF_VINTAGE` |
| 1500 | `AS_Amount` | NZD/week | 122.180822 | 124.071429 | 1.890606571 | 1.547384% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 1500 | `WFF_abated` | NZD/week | 183.658904 | 247.487808 | 63.828904219 | 34.754048% | (b) `B_WFF_VINTAGE` |
| 1500 | `Net_Income` | NZD/week | 1552.325342 | 1621.938004 | 69.612661914 | 4.484412% | (b) `B_COMPOUND_NET_INCOME` |
| 1500 | `Net_Income_annual` | NZD/year | 80942.678571 | 84572.481633 | 3629.803061653 | 4.484412% | (b) `B_COMPOUND_NET_INCOME` |
| 1500 | `EMTR` | ratio | 0.872500 | 0.871699 | 0.000801370 | 0.091848% | (c) `C_EMTR_DISCRETE_ROUNDING` |

### `couple_one_child_partner_10h_area3_rent`

Couple, child aged 9, partner working 10 hours, Area 3 rent.

| Wage | Metric | Unit | Treasury | RuleSpec | Abs delta | Relative | Class |
|---:|---|---|---:|---:|---:|---:|---|
| 0 | `gross_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `hours1` | hours/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage1_annual` | NZD/year | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_tax` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_ACC_levy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage` | NZD/week | 162.337500 | 162.337548 | 0.000047945 | 0.000030% | (c) `C_NET_WAGE_ROUNDING` |
| 0 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `FTC_abated` | NZD/week | 144.295890 | 151.909589 | 7.613699041 | 5.276449% | (b) `B_WFF_VINTAGE` |
| 0 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 0 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `AS_Amount` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 0 | `WFF_abated` | NZD/week | 241.795890 | 299.409589 | 57.613699041 | 23.827410% | (b) `B_WFF_VINTAGE` |
| 0 | `Net_Income` | NZD/week | 564.133390 | 621.747137 | 57.613746986 | 10.212788% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `Net_Income_annual` | NZD/year | 29415.526786 | 32419.672143 | 3004.145356857 | 10.212788% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `EMTR` | ratio | 0.122500 | 0.122452 | 0.000047945 | 0.039139% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 160 | `gross_wage1` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 160 | `hours1` | hours/week | 8.648649 | 8.648649 | 0.000000351 | 0.000004% | match |
| 160 | `gross_wage1_annual` | NZD/year | 8342.857143 | 8342.857143 | 0.000000143 | 0.000000% | match |
| 160 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_tax` | NZD/week | 16.800000 | 16.800000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_ACC_levy` | NZD/week | 2.800000 | 2.800000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage1` | NZD/week | 140.400000 | 140.400000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage` | NZD/week | 302.737500 | 302.737548 | 0.000047945 | 0.000016% | (c) `C_NET_WAGE_ROUNDING` |
| 160 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `FTC_abated` | NZD/week | 144.295890 | 151.909589 | 7.613699041 | 5.276449% | (b) `B_WFF_VINTAGE` |
| 160 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 160 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `AS_Amount` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 160 | `WFF_abated` | NZD/week | 241.795890 | 299.409589 | 57.613699041 | 23.827410% | (b) `B_WFF_VINTAGE` |
| 160 | `Net_Income` | NZD/week | 704.533390 | 762.147137 | 57.613746986 | 8.177575% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `Net_Income_annual` | NZD/year | 36736.383929 | 39740.529286 | 3004.145356714 | 8.177575% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `EMTR` | ratio | 0.122500 | 0.122452 | 0.000047945 | 0.039139% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 250 | `gross_wage1` | NZD/week | 250.000000 | 250.000000 | 0.000000000 | 0.000000% | match |
| 250 | `hours1` | hours/week | 13.513514 | 13.513514 | 0.000000486 | 0.000004% | match |
| 250 | `gross_wage1_annual` | NZD/year | 13035.714286 | 13035.714286 | 0.000000286 | 0.000000% | match |
| 250 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_tax` | NZD/week | 26.250000 | 26.250000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_ACC_levy` | NZD/week | 4.375000 | 4.375096 | 0.000095890 | 0.002192% | (c) `C_ACC_ANNUAL_CENTS` |
| 250 | `net_wage1` | NZD/week | 219.375000 | 219.374904 | 0.000095890 | 0.000044% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_wage` | NZD/week | 381.712500 | 381.712452 | 0.000047945 | 0.000013% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `FTC_abated` | NZD/week | 144.295890 | 151.909589 | 7.613699041 | 5.276449% | (b) `B_WFF_VINTAGE` |
| 250 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 250 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `AS_Amount` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 250 | `WFF_abated` | NZD/week | 241.795890 | 299.409589 | 57.613699041 | 23.827410% | (b) `B_WFF_VINTAGE` |
| 250 | `Net_Income` | NZD/week | 783.508390 | 841.122041 | 57.613651096 | 7.353291% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `Net_Income_annual` | NZD/year | 40854.366071 | 43858.506429 | 3004.140357571 | 7.353291% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `EMTR` | ratio | 0.122500 | 0.122452 | 0.000047945 | 0.039139% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 370 | `gross_wage1` | NZD/week | 370.000000 | 370.000000 | 0.000000000 | 0.000000% | match |
| 370 | `hours1` | hours/week | 20.000000 | 20.000000 | 0.000000000 | 0.000000% | match |
| 370 | `gross_wage1_annual` | NZD/year | 19292.857143 | 19292.857143 | 0.000000143 | 0.000000% | match |
| 370 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 370 | `wage1_tax` | NZD/week | 43.807534 | 43.807534 | 0.000000247 | 0.000001% | match |
| 370 | `wage1_ACC_levy` | NZD/week | 6.475000 | 6.475096 | 0.000095890 | 0.001481% | (c) `C_ACC_ANNUAL_CENTS` |
| 370 | `net_wage1` | NZD/week | 319.717466 | 319.717370 | 0.000096137 | 0.000030% | (c) `C_NET_WAGE_ROUNDING` |
| 370 | `net_wage` | NZD/week | 482.054966 | 482.054918 | 0.000048192 | 0.000010% | (c) `C_NET_WAGE_ROUNDING` |
| 370 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `FTC_abated` | NZD/week | 144.295890 | 151.909589 | 7.613699041 | 5.276449% | (b) `B_WFF_VINTAGE` |
| 370 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 370 | `MFTC` | NZD/week | 210.232534 | 212.155611 | 1.923077170 | 0.914738% | (b) `B_WFF_VINTAGE` |
| 370 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `AS_Amount` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 370 | `WFF_abated` | NZD/week | 241.795890 | 299.409589 | 57.613699041 | 23.827410% | (b) `B_WFF_VINTAGE` |
| 370 | `Net_Income` | NZD/week | 1094.083390 | 1153.620118 | 59.536728019 | 5.441699% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `Net_Income_annual` | NZD/year | 57048.633929 | 60153.049011 | 3104.415081989 | 5.441699% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `EMTR` | ratio | 1.017500 | 1.017452 | 0.000047945 | 0.004712% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 555 | `gross_wage1` | NZD/week | 555.000000 | 555.000000 | 0.000000000 | 0.000000% | match |
| 555 | `hours1` | hours/week | 30.000000 | 30.000000 | 0.000000000 | 0.000000% | match |
| 555 | `gross_wage1_annual` | NZD/year | 28939.285714 | 28939.285714 | 0.000000286 | 0.000000% | match |
| 555 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 555 | `wage1_tax` | NZD/week | 76.182534 | 76.182534 | 0.000000247 | 0.000000% | match |
| 555 | `wage1_ACC_levy` | NZD/week | 9.712500 | 9.712548 | 0.000047945 | 0.000494% | (c) `C_ACC_ANNUAL_CENTS` |
| 555 | `net_wage1` | NZD/week | 469.104966 | 469.104918 | 0.000048192 | 0.000010% | (c) `C_NET_WAGE_ROUNDING` |
| 555 | `net_wage` | NZD/week | 631.442466 | 631.442466 | 0.000000247 | 0.000000% | match |
| 555 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `FTC_abated` | NZD/week | 144.295890 | 151.909589 | 7.613699041 | 5.276449% | (b) `B_WFF_VINTAGE` |
| 555 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 555 | `MFTC` | NZD/week | 57.607534 | 59.530611 | 1.923077170 | 3.338239% | (b) `B_WFF_VINTAGE` |
| 555 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `AS_Amount` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 555 | `WFF_abated` | NZD/week | 241.795890 | 299.409589 | 57.613699041 | 23.827410% | (b) `B_WFF_VINTAGE` |
| 555 | `Net_Income` | NZD/week | 1090.845890 | 1150.382666 | 59.536775964 | 5.457854% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `Net_Income_annual` | NZD/year | 56879.821429 | 59984.239011 | 3104.417581989 | 5.457854% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `EMTR` | ratio | 1.017500 | 1.017452 | 0.000047945 | 0.004712% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 740 | `gross_wage1` | NZD/week | 740.000000 | 740.000000 | 0.000000000 | 0.000000% | match |
| 740 | `hours1` | hours/week | 40.000000 | 40.000000 | 0.000000000 | 0.000000% | match |
| 740 | `gross_wage1_annual` | NZD/year | 38585.714286 | 38585.714286 | 0.000000286 | 0.000000% | match |
| 740 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 740 | `wage1_tax` | NZD/week | 108.557534 | 108.557534 | 0.000000247 | 0.000000% | match |
| 740 | `wage1_ACC_levy` | NZD/week | 12.950000 | 12.950000 | 0.000000000 | 0.000000% | match |
| 740 | `net_wage1` | NZD/week | 618.492466 | 618.492466 | 0.000000247 | 0.000000% | match |
| 740 | `net_wage` | NZD/week | 780.829966 | 780.830014 | 0.000047699 | 0.000006% | (c) `C_NET_WAGE_ROUNDING` |
| 740 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `FTC_abated` | NZD/week | 126.722260 | 134.336712 | 7.614452329 | 6.008773% | (b) `B_WFF_VINTAGE` |
| 740 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 740 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `AS_Amount` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 740 | `WFF_abated` | NZD/week | 224.222260 | 281.836712 | 57.614452329 | 25.695242% | (b) `B_WFF_VINTAGE` |
| 740 | `Net_Income` | NZD/week | 1165.052226 | 1222.666726 | 57.614500027 | 4.945229% | (b) `B_COMPOUND_NET_INCOME` |
| 740 | `Net_Income_annual` | NZD/year | 60749.151786 | 63753.336429 | 3004.184642571 | 4.945229% | (b) `B_COMPOUND_NET_INCOME` |
| 740 | `EMTR` | ratio | 0.467500 | 0.466699 | 0.000801370 | 0.171416% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1000 | `gross_wage1` | NZD/week | 1000.000000 | 1000.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `hours1` | hours/week | 54.054054 | 54.054054 | 0.000000054 | 0.000000% | match |
| 1000 | `gross_wage1_annual` | NZD/year | 52142.857143 | 52142.857143 | 0.000000143 | 0.000000% | match |
| 1000 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `wage1_tax` | NZD/week | 154.057534 | 154.057534 | 0.000000247 | 0.000000% | match |
| 1000 | `wage1_ACC_levy` | NZD/week | 17.500000 | 17.500000 | 0.000000000 | 0.000000% | match |
| 1000 | `net_wage1` | NZD/week | 828.442466 | 828.442466 | 0.000000247 | 0.000000% | match |
| 1000 | `net_wage` | NZD/week | 990.779966 | 990.780014 | 0.000047699 | 0.000005% | (c) `C_NET_WAGE_ROUNDING` |
| 1000 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `FTC_abated` | NZD/week | 55.222260 | 62.837466 | 7.615205753 | 13.790102% | (b) `B_WFF_VINTAGE` |
| 1000 | `IWTC_abated` | NZD/week | 97.500000 | 147.500000 | 50.000000000 | 51.282051% | (b) `B_WFF_VINTAGE` |
| 1000 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `AS_Amount` | NZD/week | 140.930822 | 142.821429 | 1.890606571 | 1.341514% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 1000 | `WFF_abated` | NZD/week | 152.722260 | 210.337466 | 57.615205753 | 37.725480% | (b) `B_WFF_VINTAGE` |
| 1000 | `Net_Income` | NZD/week | 1284.433048 | 1343.938908 | 59.505860023 | 4.632850% | (b) `B_COMPOUND_NET_INCOME` |
| 1000 | `Net_Income_annual` | NZD/year | 66974.008929 | 70076.814490 | 3102.805560796 | 4.632850% | (b) `B_COMPOUND_NET_INCOME` |
| 1000 | `EMTR` | ratio | 0.717500 | 0.716699 | 0.000801370 | 0.111689% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1500 | `gross_wage1` | NZD/week | 1500.000000 | 1500.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `hours1` | hours/week | 81.081081 | 81.081081 | 0.000000081 | 0.000000% | match |
| 1500 | `gross_wage1_annual` | NZD/year | 78214.285714 | 78214.285714 | 0.000000286 | 0.000000% | match |
| 1500 | `gross_wage2` | NZD/week | 185.000000 | 185.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `wage1_tax` | NZD/week | 300.869863 | 300.869863 | 0.000000014 | 0.000000% | match |
| 1500 | `wage1_ACC_levy` | NZD/week | 26.250000 | 26.250000 | 0.000000000 | 0.000000% | match |
| 1500 | `net_wage1` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `net_wage` | NZD/week | 1335.217637 | 1335.217685 | 0.000047932 | 0.000004% | (c) `C_NET_WAGE_ROUNDING` |
| 1500 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `IWTC_abated` | NZD/week | 15.222260 | 72.839726 | 57.617466027 | 378.507962% | (b) `B_WFF_VINTAGE` |
| 1500 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `AS_Amount` | NZD/week | 15.930822 | 17.821429 | 1.890606571 | 11.867602% | (b) `B_AS_UPSTREAM_VINTAGE` |
| 1500 | `WFF_abated` | NZD/week | 15.222260 | 72.839726 | 57.617466027 | 378.507962% | (b) `B_WFF_VINTAGE` |
| 1500 | `Net_Income` | NZD/week | 1366.370719 | 1425.878840 | 59.508120530 | 4.355196% | (b) `B_COMPOUND_NET_INCOME` |
| 1500 | `Net_Income_annual` | NZD/year | 71246.473214 | 74349.396633 | 3102.923418653 | 4.355196% | (b) `B_COMPOUND_NET_INCOME` |
| 1500 | `EMTR` | ratio | 0.872500 | 0.871699 | 0.000801370 | 0.091848% | (c) `C_EMTR_DISCRETE_ROUNDING` |

### `single_no_children_area2_no_housing_costs`

Single adult, no children, no qualifying housing costs.

| Wage | Metric | Unit | Treasury | RuleSpec | Abs delta | Relative | Class |
|---:|---|---|---:|---:|---:|---:|---|
| 0 | `gross_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `hours1` | hours/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage1_annual` | NZD/year | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_tax` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `wage1_ACC_levy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage1` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_wage` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `net_benefit` | NZD/week | 369.600000 | 372.550000 | 2.950000000 | 0.798160% | (b) `B_BENEFIT_VINTAGE` |
| 0 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `WinterEnergy` | NZD/week | 8.630137 | 8.630137 | 0.000000014 | 0.000000% | match |
| 0 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 0 | `Net_Income` | NZD/week | 378.230137 | 381.180137 | 2.949999986 | 0.779948% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `Net_Income_annual` | NZD/year | 19722.000000 | 19875.821429 | 153.821428571 | 0.779948% | (b) `B_COMPOUND_NET_INCOME` |
| 0 | `EMTR` | ratio | 0.192500 | 0.192452 | 0.000047945 | 0.024907% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 160 | `gross_wage1` | NZD/week | 160.000000 | 160.000000 | 0.000000000 | 0.000000% | match |
| 160 | `hours1` | hours/week | 8.648649 | 8.648649 | 0.000000351 | 0.000004% | match |
| 160 | `gross_wage1_annual` | NZD/year | 8342.857143 | 8342.857143 | 0.000000143 | 0.000000% | match |
| 160 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_tax` | NZD/week | 28.000000 | 28.000000 | 0.000000000 | 0.000000% | match |
| 160 | `wage1_ACC_levy` | NZD/week | 2.800000 | 2.800000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage1` | NZD/week | 129.200000 | 129.200000 | 0.000000000 | 0.000000% | match |
| 160 | `net_wage` | NZD/week | 129.200000 | 129.200000 | 0.000000000 | 0.000000% | match |
| 160 | `net_benefit` | NZD/week | 369.600000 | 372.550000 | 2.950000000 | 0.798160% | (b) `B_BENEFIT_VINTAGE` |
| 160 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `WinterEnergy` | NZD/week | 8.630137 | 8.630137 | 0.000000014 | 0.000000% | match |
| 160 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 160 | `Net_Income` | NZD/week | 507.430137 | 510.380137 | 2.949999986 | 0.581361% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `Net_Income_annual` | NZD/year | 26458.857143 | 26612.678571 | 153.821428429 | 0.581361% | (b) `B_COMPOUND_NET_INCOME` |
| 160 | `EMTR` | ratio | 0.892500 | 0.892452 | 0.000047945 | 0.005372% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 250 | `gross_wage1` | NZD/week | 250.000000 | 250.000000 | 0.000000000 | 0.000000% | match |
| 250 | `hours1` | hours/week | 13.513514 | 13.513514 | 0.000000486 | 0.000004% | match |
| 250 | `gross_wage1_annual` | NZD/year | 13035.714286 | 13035.714286 | 0.000000286 | 0.000000% | match |
| 250 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_tax` | NZD/week | 43.750000 | 43.750000 | 0.000000000 | 0.000000% | match |
| 250 | `wage1_ACC_levy` | NZD/week | 4.375000 | 4.375096 | 0.000095890 | 0.002192% | (c) `C_ACC_ANNUAL_CENTS` |
| 250 | `net_wage1` | NZD/week | 201.875000 | 201.874904 | 0.000095890 | 0.000047% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_wage` | NZD/week | 201.875000 | 201.874904 | 0.000095890 | 0.000047% | (c) `C_NET_WAGE_ROUNDING` |
| 250 | `net_benefit` | NZD/week | 306.600000 | 309.550000 | 2.950000000 | 0.962166% | (b) `B_BENEFIT_VINTAGE` |
| 250 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `WinterEnergy` | NZD/week | 8.630137 | 8.630137 | 0.000000014 | 0.000000% | match |
| 250 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 250 | `Net_Income` | NZD/week | 517.105137 | 520.055041 | 2.949904096 | 0.570465% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `Net_Income_annual` | NZD/year | 26963.339286 | 27117.155714 | 153.816428286 | 0.570465% | (b) `B_COMPOUND_NET_INCOME` |
| 250 | `EMTR` | ratio | 0.892500 | 0.892452 | 0.000047945 | 0.005372% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 370 | `gross_wage1` | NZD/week | 370.000000 | 370.000000 | 0.000000000 | 0.000000% | match |
| 370 | `hours1` | hours/week | 20.000000 | 20.000000 | 0.000000000 | 0.000000% | match |
| 370 | `gross_wage1_annual` | NZD/year | 19292.857143 | 19292.857143 | 0.000000143 | 0.000000% | match |
| 370 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `wage1_tax` | NZD/week | 61.217590 | 61.448316 | 0.230726369 | 0.376896% | (b) `B_BENEFIT_GROSSUP_TAX` |
| 370 | `wage1_ACC_levy` | NZD/week | 6.475000 | 6.475096 | 0.000095890 | 0.001481% | (c) `C_ACC_ANNUAL_CENTS` |
| 370 | `net_wage1` | NZD/week | 302.307410 | 302.076588 | 0.230822260 | 0.076353% | (b) `B_BENEFIT_GROSSUP_TAX` |
| 370 | `net_wage` | NZD/week | 302.307410 | 302.076588 | 0.230822260 | 0.076353% | (b) `B_BENEFIT_GROSSUP_TAX` |
| 370 | `net_benefit` | NZD/week | 222.600000 | 225.550000 | 2.950000000 | 1.325247% | (b) `B_BENEFIT_VINTAGE` |
| 370 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `WinterEnergy` | NZD/week | 8.630137 | 8.630137 | 0.000000014 | 0.000000% | match |
| 370 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 370 | `Net_Income` | NZD/week | 533.537547 | 536.256725 | 2.719177726 | 0.509651% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `Net_Income_annual` | NZD/year | 27820.172087 | 27961.957789 | 141.785702306 | 0.509651% | (b) `B_COMPOUND_NET_INCOME` |
| 370 | `EMTR` | ratio | 0.837751 | 0.837703 | 0.000047549 | 0.005676% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 555 | `gross_wage1` | NZD/week | 555.000000 | 555.000000 | 0.000000000 | 0.000000% | match |
| 555 | `hours1` | hours/week | 30.000000 | 30.000000 | 0.000000000 | 0.000000% | match |
| 555 | `gross_wage1_annual` | NZD/year | 28939.285714 | 28939.285714 | 0.000000286 | 0.000000% | match |
| 555 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `wage1_tax` | NZD/week | 83.464098 | 83.694825 | 0.230726749 | 0.276438% | (b) `B_BENEFIT_GROSSUP_TAX` |
| 555 | `wage1_ACC_levy` | NZD/week | 9.712500 | 9.712548 | 0.000047945 | 0.000494% | (c) `C_ACC_ANNUAL_CENTS` |
| 555 | `net_wage1` | NZD/week | 461.823402 | 461.592627 | 0.230774695 | 0.049970% | (b) `B_BENEFIT_GROSSUP_TAX` |
| 555 | `net_wage` | NZD/week | 461.823402 | 461.592627 | 0.230774695 | 0.049970% | (b) `B_BENEFIT_GROSSUP_TAX` |
| 555 | `net_benefit` | NZD/week | 93.100000 | 96.050000 | 2.950000000 | 3.168636% | (b) `B_BENEFIT_VINTAGE` |
| 555 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `WinterEnergy` | NZD/week | 8.630137 | 8.630137 | 0.000000014 | 0.000000% | match |
| 555 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 555 | `Net_Income` | NZD/week | 563.553538 | 566.272764 | 2.719226292 | 0.482514% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `Net_Income_annual` | NZD/year | 29385.291650 | 29527.079852 | 141.788202354 | 0.482514% | (b) `B_COMPOUND_NET_INCOME` |
| 555 | `EMTR` | ratio | 0.837751 | 0.837703 | 0.000047549 | 0.005676% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 740 | `gross_wage1` | NZD/week | 740.000000 | 740.000000 | 0.000000000 | 0.000000% | match |
| 740 | `hours1` | hours/week | 40.000000 | 40.000000 | 0.000000000 | 0.000000% | match |
| 740 | `gross_wage1_annual` | NZD/year | 38585.714286 | 38585.714286 | 0.000000286 | 0.000000% | match |
| 740 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `wage1_tax` | NZD/week | 108.557534 | 108.557534 | 0.000000247 | 0.000000% | match |
| 740 | `wage1_ACC_levy` | NZD/week | 12.950000 | 12.950000 | 0.000000000 | 0.000000% | match |
| 740 | `net_wage1` | NZD/week | 618.492466 | 618.492466 | 0.000000247 | 0.000000% | match |
| 740 | `net_wage` | NZD/week | 618.492466 | 618.492466 | 0.000000247 | 0.000000% | match |
| 740 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `IETC_abated` | NZD/week | 9.972603 | 9.972603 | 0.000000260 | 0.000003% | match |
| 740 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 740 | `Net_Income` | NZD/week | 628.465068 | 628.465068 | 0.000000493 | 0.000000% | match |
| 740 | `Net_Income_annual` | NZD/year | 32769.964286 | 32769.964286 | 0.000000286 | 0.000000% | match |
| 740 | `EMTR` | ratio | 0.192500 | 0.192452 | 0.000047945 | 0.024907% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1000 | `gross_wage1` | NZD/week | 1000.000000 | 1000.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `hours1` | hours/week | 54.054054 | 54.054054 | 0.000000054 | 0.000000% | match |
| 1000 | `gross_wage1_annual` | NZD/year | 52142.857143 | 52142.857143 | 0.000000143 | 0.000000% | match |
| 1000 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `wage1_tax` | NZD/week | 154.057534 | 154.057534 | 0.000000247 | 0.000000% | match |
| 1000 | `wage1_ACC_levy` | NZD/week | 17.500000 | 17.500000 | 0.000000000 | 0.000000% | match |
| 1000 | `net_wage1` | NZD/week | 828.442466 | 828.442466 | 0.000000247 | 0.000000% | match |
| 1000 | `net_wage` | NZD/week | 828.442466 | 828.442466 | 0.000000247 | 0.000000% | match |
| 1000 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `IETC_abated` | NZD/week | 9.972603 | 9.972603 | 0.000000260 | 0.000003% | match |
| 1000 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1000 | `Net_Income` | NZD/week | 838.415068 | 838.415068 | 0.000000493 | 0.000000% | match |
| 1000 | `Net_Income_annual` | NZD/year | 43717.357143 | 43717.357143 | 0.000000143 | 0.000000% | match |
| 1000 | `EMTR` | ratio | 0.192500 | 0.192452 | 0.000047945 | 0.024907% | (c) `C_EMTR_DISCRETE_ROUNDING` |
| 1500 | `gross_wage1` | NZD/week | 1500.000000 | 1500.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `hours1` | hours/week | 81.081081 | 81.081081 | 0.000000081 | 0.000000% | match |
| 1500 | `gross_wage1_annual` | NZD/year | 78214.285714 | 78214.285714 | 0.000000286 | 0.000000% | match |
| 1500 | `gross_wage2` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `wage1_tax` | NZD/week | 300.869863 | 300.869863 | 0.000000014 | 0.000000% | match |
| 1500 | `wage1_ACC_levy` | NZD/week | 26.250000 | 26.250000 | 0.000000000 | 0.000000% | match |
| 1500 | `net_wage1` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `net_wage` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `net_benefit` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `FTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `IWTC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `MFTC` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `IETC_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `WinterEnergy` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `BestStart_Total` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `AS_Amount` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `WFF_abated` | NZD/week | 0.000000 | 0.000000 | 0.000000000 | 0.000000% | match |
| 1500 | `Net_Income` | NZD/week | 1172.880137 | 1172.880137 | 0.000000014 | 0.000000% | match |
| 1500 | `Net_Income_annual` | NZD/year | 61157.321429 | 61157.321429 | 0.000000429 | 0.000000% | match |
| 1500 | `EMTR` | ratio | 0.347500 | 0.347452 | 0.000047945 | 0.013797% | (c) `C_EMTR_DISCRETE_ROUNDING` |
