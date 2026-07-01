# Source Evidence: Paid parental leave, child support, and family-related payments

## Track

- Track id: `32_paid_parental_leave_child_support_family_payments`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/57
- Policy family: Paid parental leave, child support, and family-related payments

## Official Source Family

- Act, regulation, order, or official agency table: Parental Leave and Employment Protection Act 1987; Child Support Act 1991; IRD child support guidance.
- Administering agency: Relevant administering agency.
- Source status: source inventory and legal scope were pinned during implementation.
- Publication state checked: yes.
- Core official references: Parental Leave and Employment Protection Act 1987; Child Support Act 1991; IRD parental leave and child support guidance.

## Corpus Evidence

- Corpus source manifest: not retained in this archive slice.
- Corpus citation path(s): recorded in the RuleSpec module `source_verification` entries.
- Source ingestion command or run id: implemented from official law and agency guidance during the track.
- Known extraction gaps: family scope remains intentionally partial to paid parental leave, child support, and related payment surfaces.

## RuleSpec Scope

- Rules: paid parental leave eligibility; paid parental leave rate and duration; transfer of entitlement; child support formula; liable parent and receiving carer tests.
- Parameters: thresholds, rate tables, and entitlement limits where applicable.
- Definitions: legal predicates and income-interface primitives where needed.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and threshold changes by effective date.
- Comparison oracles remain non-authoritative and must be recorded separately from legal source text.

## Current Implementation Slice

- paid parental leave transfer rules; child support applicable-rate and formula-assessment surfaces

## Companion Tests

- Scenario families: boundary, threshold, and date-effective cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly or annual amounts, and reduced or zero-payment outcomes.
- Edge cases: threshold crossings, term transitions, and dependent-status changes.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Pinned SHA or version: not applicable for this archived slice.
- Comparison role: non-authoritative only.
- Known divergences: none recorded for this archived slice.
- Upstream comparison guidance: see the track issue and archived source notes for comparison-only context.

## Residual Risk

- Interpretation questions: remaining family-payment coverage may still be expanded in later tracks, but this slice is complete as archived.
- Missing official evidence: none for this archived slice.
- Blockers: none for this archived slice; oracle comparison remains comparison-only.
