# Product Guide - NZ RuleSpec Encodings and Source Registry

## Initial Concept
A complete, source-grounded encoding of the Aotearoa New Zealand tax, transfer, social insurance, student support, family assistance, housing support, and related eligibility surfaces using the RuleSpec format.

## Product Vision
To establish an authoritative, full-country open-source registry of executable NZ legislation, regulations, and agency policies, validated against established comparison engines and reference datasets.

## Target Audience
- Policy analysts and modelers verifying EMTRs, disposable income, and policy diffusion.
- Developers building calculator-facing services requiring executable tax-benefit logic.
- Government agencies and researchers seeking source-grounded, verifiable policy specifications.

## Scope and Priority Areas
The initial focus covers the following core NZ legislation and policy domains:
- **Income Tax & Family Support**: Income Tax Act, Working for Families (WFF) tax credits, and Student Support/StudyLink eligibility.
- **Social Security & Benefits**: Social Security Act, welfare benefits, housing support, and New Zealand Superannuation.
- **Indirect Tax & levies**: Goods and Services Tax (GST) Act and Accident Compensation Corporation (ACC) levies.

## Comparison Oracles & References
- `nztaxmicrosim` (historical tax, WFF, benefits, and synthetic population logic)
- `openfisca-aotearoa` (OpenFisca variables, parameters, and ontology references)
- NZ Treasury IncomeExplorer (EMTR and disposable income reference)
- PolicyEngine NZ (for smoke/reference testing)
