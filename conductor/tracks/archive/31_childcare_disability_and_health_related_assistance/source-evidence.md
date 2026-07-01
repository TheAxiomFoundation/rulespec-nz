# Source Evidence: Childcare, disability, and health-related assistance

## Track

- Track id: `31_childcare_disability_and_health_related_assistance`
- Upstream issue: https://github.com/TheAxiomFoundation/rulespec-nz/issues/56
- Policy family: Childcare, disability, and health-related assistance

## Official Source Family

- Act, regulation, order, or official agency table: Social Security Act 2018; Social Security Regulations 2018; Health Entitlement Cards Regulations 1993; Pae Ora (Healthy Futures) Act 2022; MSD and health guidance.
- Administering agencies: Ministry of Social Development; Health NZ / legacy health entitlement card administration.
- Source status: source inventory recorded in the module-level `source_verification` blocks.
- Publication state checked: yes.
- Core official references:
  - `nz/statute/act/public/2018/0032/section/77`
  - `nz/regulation/regulation/public/2018/0202/regulation/21`
  - `nz/regulation/regulation/public/2018/0202/regulation/22`
  - `nz/regulation/regulation/public/2018/0202/regulation/23`
  - `nz/regulation/regulation/public/2018/0202/regulation/24`
  - `nz/regulation/regulation/public/2018/0202/regulation/30`
  - `nz/regulation/regulation/public/2018/0202/regulation/31`
  - `nz/regulation/regulation/public/2018/0202/regulation/32`
  - `nz/regulation/regulation/public/2018/0202/regulation/33`
  - `nz/regulation/regulation/public/2018/0202/regulation/34`
  - `nz/regulation/regulation/public/2018/0202/regulation/35`
  - `nz/regulation/regulation/public/2018/0202/regulation/36`
  - `nz/regulation/regulation/public/2018/0202/regulation/38`
  - `nz/regulation/regulation/public/2018/0202/regulation/39`
  - `nz/regulation/regulation/public/2018/0202/regulation/40`
  - `nz/regulation/regulation/public/2018/0202/regulation/41`
  - `nz/regulation/regulation/public/2018/0202/regulation/42`
  - `nz/regulation/regulation/public/2018/0202/regulation/44`
  - `nz/regulation/regulation/public/2018/0202/schedule/2`
  - `nz/statute/act/public/2018/0032/section/78`
  - `nz/statute/act/public/2018/0032/section/79`
  - `nz/statute/act/public/2018/0032/section/80`
  - `nz/statute/act/public/2018/0032/section/81`
  - `nz/statute/act/public/2018/0032/section/82`
  - `nz/statute/act/public/2018/0032/section/83`
  - `nz/statute/act/public/2018/0032/schedule/4/part/9`
  - `nz/regulation/regulation/public/2018/0202/regulation/49`
  - `nz/statute/act/public/2018/0032/section/84`
  - `nz/statute/act/public/2018/0032/section/85`
  - `nz/statute/act/public/2018/0032/section/86`
  - `nz/statute/act/public/2018/0032/section/87`
  - `nz/statute/act/public/2018/0032/section/88`
  - `nz/statute/act/public/2018/0032/schedule/3/clause/19`
  - `nz/statute/act/public/2018/0032/schedule/4/part/9/clause/2`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/1`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/3`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/4`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/5`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/5A`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/6`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/7`
  - `nz/statute/act/public/1993/0169/regulation/8/subclause/8`
  - `nz/statute/act/public/1993/0169/regulation/9`

## Corpus Evidence

- Corpus source manifest: recorded in the module-level source verification blocks.
- Corpus citation paths: recorded above in the module files and companion tests.
- Source ingestion command or run id: official corpus extraction already reflected in the module sources and tests.
- Known extraction gaps: none blocking for this track.

## RuleSpec Scope

- Rules: Childcare Subsidy; Out of School Care and Recreation Subsidy; Child Disability Allowance; Disability Allowance; Community Services Card; home help; primary care copayment settings.
- Parameters: thresholds, rate tables, and entitlement limits where applicable.
- Definitions: legal predicates and income-interface primitives where needed.
- Eligibility predicates: entitlement and exclusion conditions.
- Date-effective surfaces: rate and threshold changes by effective date.
- Comparison oracles remain non-authoritative and are recorded separately from legal source text.

## Current Implementation Slice

- `nz/regulations/social_security/childcare_assistance/core.yaml`
- `nz/regulations/social_security/childcare_assistance/core.test.yaml`
- `nz/statutes/social_security/child_disability_allowance/core.yaml`
- `nz/statutes/social_security/child_disability_allowance/core.test.yaml`
- `nz/statutes/social_security/disability_allowance/core.yaml`
- `nz/statutes/social_security/disability_allowance/core.test.yaml`
- `nz/regulations/health_entitlement_cards/community_services_card/core.yaml`
- `nz/regulations/health_entitlement_cards/community_services_card/core.test.yaml`

## Companion Tests

- Scenario families: boundary, threshold, and date-effective cases.
- Expected outputs: entitlement holds / not_holds predicates, weekly or annual amounts, and reduced or zero-payment outcomes.
- Edge cases: threshold crossings, term transitions, and dependent-status changes.
- Historical/date-effective cases: required.

## Oracle Comparison

- Oracle/reference: nztaxmicrosim; OpenFisca Aotearoa where pinned.
- Comparison role: non-authoritative only.
- Known divergences: tracked separately from legal source text.
- Upstream comparison guidance: https://github.com/TheAxiomFoundation/rulespec-nz/issues/32#issuecomment-4828717845

## Residual Risk

- Comparison manifests remain separate from legal authority.
- Future oracle reconciliation can be handled in the dedicated comparison track.
