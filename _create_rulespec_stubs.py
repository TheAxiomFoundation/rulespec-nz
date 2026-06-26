import os

base = r'C:\Users\60217257\OneDrive - Flinders\repos\legal-nz\rulespec-nz'

files['policies/common/demographics.yaml'] = """format: rulespec/v1
module:
  summary: |-
    Common demographic predicates used across NZ benefit and tax programs.
    Official-source encoding pending from Citizenship Act 1977,
    Immigration Act 2009, Social Security Act 2018.
  source_verification:
    corpus_citation_paths:
      - nz/statute/act/public/1977/0061
      - nz/statute/act/public/2009/0051
      - nz/statute/act/public/2018/0032
    oracle_links:
      - openfisca-aotearoa
      - nztaxmicrosim
rules: []
"""
files = {}