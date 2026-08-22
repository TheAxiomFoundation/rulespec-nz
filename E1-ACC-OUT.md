# E1-ACC — ACC earners' levy dependency cone

## Outcome

The RuleSpec implementation is complete on branch
`encode/acc-earners-levy-cone`. The former request-supplied
`acc_earnings_for_earners_levy` scalar is now a derived rule built from
employee, self-employed, and shareholder-employee components. The standard
levy formulas consume that derived base, and the two bearing instruments have
encoded rules.

This is a v3 certificate candidate, not a certification announcement. The
read-only oracles closure producers still need to adopt the spine
classifications below, replace the old dependency-disposition leaf with the
new boundary facts, and recompute `closed`. CERTIFIED.md also requires an
adversarial audit and Max's explicit approval before any certification claim.

## Receipts

- Base: local `origin/main` at
  `3aa72d053ea8f98d2c4742609269bedf078d9c76`.
- Implementation commit:
  `4699e05ac1b5825b9efe79b1fef0268536590a10`.
- Module SHA-256:
  `ef73a62ef9a1651dc2b98bbd91ecbb62e316c1a121ca29850f98fe85ba185e4b`.
- Companion SHA-256:
  `bec994546df43092d007655ede16f9e57b29251ce3eb9150b37f55ea7278a4a3`.
- Pinned corpus release: `nz-rulespec-2026-07-25`; content SHA-256
  `fec362b985739f27910f0e950fc03e298528a42cdff6f694b19c9ed0850c8405`;
  corpus commit `2d077803ee17f921c30014b9e98ae9ee3b612512`.
- Regression engine pin:
  `05eac9d2f89dabe5c6673176260762cef3a58f47`.
- Companion runner pin:
  `a9987a4bc6a58e3f0407972f2e5726b7092b9c4b`.

The report itself is a follow-up commit, so its own commit SHA cannot be
embedded without changing that SHA. The exact final branch SHA is supplied in
the handoff accompanying this file.

## Rules added and changed

The module now has 33 rules: 9 parameters and 24 derived rules. This is a net
addition of 21 rules (2 parameters and 19 derived rules) to the prior 12-rule
module.

| Surface | Rules | Legal provisions |
| --- | --- | --- |
| Employee earnings | `acc_employee_section_11_excluded_payments`, `acc_employee_paye_income_payments_before_statutory_exclusions`, `acc_spouse_or_partner_service_payments_included`, `acc_employee_earnings_for_earners_levy` | Accident Compensation Act 2001 ss 6, 9-13; Income Tax Act 2007 s YA 1 |
| Self-employed earnings | `acc_self_employed_earnings_for_earners_levy` | Accident Compensation Act 2001 ss 6 and 14 |
| Shareholder-employee gates and amounts | `acc_person_is_shareholder_employee`, the RD 3B/RD 3C applicability and PAYE/non-PAYE amount rules, subsection (2)/(3) amount rules, and `acc_shareholder_employee_earnings_for_earners_levy` | Accident Compensation Act 2001 ss 6 and 15; Income Tax Act 2007 ss RD 3B-RD 3C |
| Combined levy base | `acc_earnings_for_earners_levy` | Accident Compensation Act 2001 s 6; Accident Compensation (Earners' Levy) Regulations 2025 reg 4 |
| Low self-employed interaction | `acc_employee_earnings_for_low_self_employed_formula` and rewired existing minimum-levy formula | Accident Compensation Act 2001 ss 9-13; Earners' Levy Regulations reg 6 |
| GST relationship | `acc_gst_standard_rate`, `acc_earners_levy_rate_including_gst_before_administrative_rounding` | Earners' Levy Regulations regs 4 and 8; Goods and Services Tax Act 1985 ss 5(6EC)-(6EE), 8(1), and 10 |
| Collection timing | `acc_earners_levy_deduction_required_at_payment`, `acc_earners_levy_rate_including_gst_on_pay_date` | Accident Compensation Act 2001 s 221; Inland Revenue, *Deductions from salary and wages* |
| RD 3B threshold | `acc_rd3b_regular_salary_annual_gross_income_threshold` | Income Tax Act 2007 s RD 3B(1)(ab) |

The existing reg 4/5 standard levy and cap outputs retain their names and
values but now consume the derived base. The existing reg 6, 7, and 9 surfaces
remain covered. Section 12 was encoded as an interpretive boundary: its
first-week and weekly-compensation exclusion is expressly limited to the Work
Account levy under s 168, so those payments remain in the earners' levy base.

## Spine dispositions

Encoded: ss 6, 9, 10, 11, 12, 13, 14, 15, and 221.

Classified rather than encoded for this computed surface:

- **s 25 (Accident):** its operative text begins “Accident means any of the
  following kinds of occurrences”. It defines covered occurrence/causation,
  not earnings, the liable-earnings cap, rate, GST factor, or collection.
- **s 26 (Personal injury):** its operative text begins “Personal injury
  means”. It defines injury categories and exclusions, with no input into the
  earners' levy calculation.
- **s 103 (incapacity for a claimant who was an earner):** the question it
  determines is whether injury prevents the claimant from engaging in the
  employment held when injured. That bears on incapacity/weekly-compensation
  entitlement, not the levy computation.
- **s 105 (incapacity for certain other claimants):** the question it
  determines is whether injury prevents work suited by experience, education,
  or training. It likewise bears on incapacity/weekly compensation, not this
  levy surface.

Those four rows are in the cross-program 174-root audit because of the
incapacity/weekly-compensation and in-work-tax-credit dependency spine. They
have no path into the ACC earners' levy's base, cap, rate, GST relationship,
or deduction timing, so inventing levy rules for them would be misleading.
The external ledger was intentionally left read-only.

## Bearing instruments

1. **Inland Revenue — Deductions from salary and wages.** The module now
   derives whether a deduction is required at payment under s 221 and selects
   the rate effective on the pay date. Proofs use the pinned guidance statements
   that new rates apply on the pay date and that PAYE can include the ACC
   earners' levy.
2. **Goods and Services Tax Act 1985.** The module now derives the exact
   pre-administrative-rounding relationship
   `exclusive_rate * (1 + 0.15)`, grounded in the deemed-supply, 15% rate, and
   value-of-supply provisions plus reg 8's GST-exclusive instruction.

## Tests and proof receipts

- One companion file, 9 cases, all passing with the pinned runner.
- Every case assigns all 51 unresolved local `#input` facts. All 18 Boolean
  facts are assigned explicitly, including every `false` state.
- The cases exercise the salary/cap/negative branches, both s 10 spouse
  routes, all s 11 exclusions, weekly and first-week compensation, private
  domestic workers, s 14 A-minus-B, s 15 including RD 3B and RD 3C plus the
  Corporation override, low-self-employed and weekly-purchase formulas, the
  invoice threshold, and both sides of the pay-date timing rule.
- Coverage includes all 24 derived outputs and all 9 parameters.
- Exact pinned companion result: `success=true`, 1 test file, 9 cases,
  1 compiled program, 0 failures. The compiled module contains 24 derived
  rules and remains fast-path compatible.
- 95/95 proof atoms are verbatim substrings resolved across 23 unique
  `corpus_citation_path` rows in the pinned release. The change adds 65
  resolved atoms; the repository ledger is now 1,305 total, 1,280 resolved,
  and 25 pre-existing blocked atoms.
- The monetary-proof audit reports 0 missing atoms across 7 monetary
  obligation rules.
- The repository's immutable known-gap audit reproduces the exact expected
  fingerprint
  `sha256:34601fe501652a6c5a7699bc3a2e2c92411bf085a8d76bd80bd2d001ddc4e87e`.
  Its only findings are the three pre-existing operational rounded rates
  `0.0167`, `0.0175`, and `0.0183`; no new validation gap was introduced.

## Oracle regression

The workflow-pinned engine replayed the prior supplied-scalar artifact and
the new derived-base artifact over all 104 ACC comparison cells (11 scenarios,
24 distinct weekly wage values). For the new artifact, annual salary/wages was
set to `weekly_wage * 365 / 7` and every other new fact was explicitly zero or
false.

- Old versus new annual levy: 0 numeric mismatches and 0 serialized-text
  mismatches.
- New result versus the statutory annual-cent formula: 0/104 mismatches.
- New result versus fixture-implied annual cents: 0/104 mismatches.
- Weekly conversion: 0 differences above the oracle's `1e-36` tolerance.
  Eleven wage-555 cells retain a pre-existing serialization-only difference
  with maximum magnitude `1E-39`.
- `scripts/nz_incomeexplorer.py --check` passed in the read-only oracles
  worktree.

There are no cap-binding cells in the oracle fixtures; the companion suite
contains the cap case.

## Repository gates

- Pytest task equivalent: 280 passed, 1 skipped. The skipped test is the
  pre-existing live GitHub publication audit, which requires API access.
- Ruff lint: passed.
- Ruff format check: passed (45 files already formatted).
- Rust offline test: 2 passed; doc tests 0.
- Roadmap/coverage synchronization: passed.
- `make scorecard`: 40 modules, 36 with rules, 4 deferred, 782 rules.
- ACC inventory exactly matches rule extraction; direct proof count matches
  the provenance ledger; `git diff --check` passed.
- Regenerated `data/coverage/rulespec-rule-inventory.json` and
  `data/coverage/rulespec-scorecard.json`.
- No changes to `.axiom/toolchain.toml`, workflows, CODEOWNERS,
  `known-validation-gaps.yaml`, or `PROGRESS.md`.

## Honest limits and environment deviations

- The pinned release proves the exact GST calculation, but it does not contain
  a provision or guidance row stating the PAYE-facing four-decimal
  administrative rounded rates. Those existing parameters were retained so
  every oracle value remains identical. They remain covered by the unchanged
  repository waiver; claiming those literals as newly proved would be false.
- The local environment has neither `pixi` nor `basedpyright`, so the aggregate
  `pixi run quality` wrapper and its typecheck member could not be launched.
  Its pytest, Ruff, and Rust members were run directly and passed. No Python
  implementation code changed; the only Python edit updates proof-ledger count
  assertions.
- The protected proof-validation supervisor/signing broker is unavailable in
  this sandbox. The exact release-aware substantive verifier, companion runner,
  money-proof audit, and known-gap audit all passed, but a signed proof receipt
  must be produced by CI.
- Full Schedule 4 payroll-table computation is outside this brief's encoded
  s 221 surface; this change encodes the requested deduction obligation and
  pay-date rate mechanics. The annual levy amount remains the computed amount
  used by the certificate comparison.
- The 51 new boundary inputs are payment, filing/election, corporate decision,
  status, and ledger facts. Because the oracles worktree was read-only, its
  v3 leaf-grounding rows were not rewritten here. The closure producer must
  explicitly type and audit those leaves before it can compute `closed=true`.
- `git fetch origin -q` could not reach GitHub (`Could not resolve host`), so
  the worktree uses the already-present local `origin/main` ref. Sandbox policy
  also denied the requested sibling worktree and ops out-file locations. Work
  was isolated in the same git worktree under an allowed path, and this report
  uses the authorized worktree-root fallback.

No push or pull request was created.
