import json

obj = {
  "track_id": "15_openfisca_follow_on_reconciliation",
  "generated_at": "2026-06-26",
  "purpose": "Verifies PCO bulk XML corpus extracts for each deferred OpenFisca Aotearoa surface. No axiom-corpus fallback required.",
  "extraction_baseline": {
    "corpus_ref": "d7c53d21a6616e15e2e4e5176267ae93622b79bd",
    "corpus_date": "2026-06-16-pco-latest",
    "source_map": "data/corpus/inventory/nz/tax-benefit-pco-locators.json"
  },
  "verification_results": [
    {
      "surface_id": "demographics-and-common-predicates",
      "extraction_approach": "multi_source",
      "sources": [
        {"source_name": "Citizenship Act 1977", "pco_status": "exact_match", "source_document_id": "act/public/1977/61", "provision_count": 46},
        {"source_name": "Immigration Act 2009", "pco_status": "exact_match", "source_document_id": "act/public/2009/51", "provision_count": 604},
        {"source_name": "Social Security Act 2018", "pco_status": "exact_match", "source_document_id": "act/public/2018/32", "provision_count": 650}
      ],
      "blockers": ["Program-specific statutory definitions require per-program extraction."]
    },
    {
      "surface_id": "citizenship-and-immigration",
      "extraction_approach": "pco_corpus",
      "sources": [
        {"source_name": "Citizenship Act 1977", "pco_status": "exact_match", "source_document_id": "act/public/1977/61", "provision_count": 46},
        {"source_name": "Immigration Act 2009", "pco_status": "exact_match", "source_document_id": "act/public/2009/51", "provision_count": 604}
      ]
    },
    {
      "surface_id": "relationship-status-and-family-law-predicates",
      "extraction_approach": "pco_corpus",
      "sources": [
        {"source_name": "Civil Union Act 2004", "pco_status": "exact_match", "source_document_id": "act/public/2004/102", "provision_count": 34},
        {"source_name": "Marriage Act 1955", "pco_status": "exact_match", "source_document_id": "act/public/1955/92", "provision_count": 80},
        {"source_name": "Property (Relationships) Act 1976", "pco_status": "exact_match", "source_document_id": "act/public/1976/166", "provision_count": 102},
        {"source_name": "Social Security Act 2018", "pco_status": "exact_match", "source_document_id": "act/public/2018/32", "provision_count": 650}
      ]
    },
    {
      "surface_id": "student-allowance",
      "extraction_approach": "pco_corpus",
      "sources": [
        {"source_name": "Student Allowances Regulations 1998", "pco_status": "exact_match", "source_document_id": "secondary-legislation/pco-drafted/1998/277", "provision_count": 82},
        {"source_name": "Education and Training Act 2020", "pco_status": "exact_match", "source_document_id": "act/public/2020/38", "provision_count": 760}
      ],
      "blockers": ["StudyLink guidance is external agency material."]
    },
    {
      "surface_id": "rates-rebates",
      "extraction_approach": "pco_corpus",
      "sources": [
        {"source_name": "Rates Rebate Act 1973", "pco_status": "exact_match", "source_document_id": "act/public/1973/5", "provision_count": 23},
        {"source_name": "Rates Rebate Regulations 1973", "pco_status": "exact_match", "source_document_id": "secondary-legislation/pco-drafted/1973/260", "provision_count": 8}
      ],
      "blockers": ["DIA rates rebate guidance is external agency material."]
    },
    {
      "surface_id": "parental-leave",
      "extraction_approach": "pco_corpus",
      "sources": [
        {"source_name": "Parental Leave and Employment Protection Act 1987", "pco_status": "exact_match", "source_document_id": "act/public/1987/129", "provision_count": 199}
      ],
      "blockers": ["Employment.govt.nz guidance is external agency material."]
    },
    {
      "surface_id": "housing-restructuring-and-social-housing",
      "extraction_approach": "pco_corpus",
      "sources": [
        {"source_name": "Housing Restructuring and Tenancy Matters Act 1992", "pco_status": "exact_match_via_amendments", "source_document_id": "act/public/1992/76", "provision_count": 201}
      ],
      "blockers": ["MSD rent guidance and Kainga Ora policy are external agency materials."]
    },
    {
      "surface_id": "acc-and-weekly-compensation",
      "extraction_approach": "pco_corpus",
      "sources": [
        {"source_name": "Accident Compensation Act 2001", "pco_status": "exact_match", "source_document_id": "act/public/2001/49", "provision_count": 630}
      ],
      "blockers": ["ACC guidance and levy rate tables are external agency materials."]
    },
    {
      "surface_id": "health-and-community-services",
      "extraction_approach": "pco_corpus_with_existing_provision_extracts",
      "note": "Community Services Card provisions already extracted at data/corpus/provisions/nz/regulation/2026-06-17-community-services-card-health-entitlement-regulations.jsonl.",
      "sources": [
        {"source_name": "Pae Ora (Healthy Futures) Act 2022", "pco_status": "exact_match", "source_document_id": "act/public/2022/30", "provision_count": 189},
        {"source_name": "Health Entitlement Cards Regulations 1993", "pco_status": "exact_match", "source_document_id": "secondary-legislation/pco-drafted/1993/169", "provision_count": 34}
      ],
      "blockers": ["Ministry of Health service coverage guidance is external agency material."]
    }
  ],
  "extraction_summary": {
    "total_surfaces": 9,
    "pco_corpus_available": 9,
    "exact_match_primary_sources": 14,
    "external_agency_blockers": 6,
    "fallback_required": False,
    "next_step": "Proceed to Phase 3 RuleSpec stubs and inventory update."
  }
}

path = r"C:\Users\60217257\OneDrive - Flinders\repos\legal-nz\rulespec-nz\data\coverage\openfisca-aotearoa-extraction-verification.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(obj, f, indent=2)
print(f"Written {path}")