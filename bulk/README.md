# Bulk encode (NZ)

A durable queue for bulk RuleSpec encoding of New Zealand Income Tax Act 2007
provisions. Each entry is a corpus citation the encoder resolves and encodes with
`axiom-encode encode <citation> --apply`; the queue is the seed for whenever the
NZ bulk dispatcher + governance are armed.

This is the `rulespec-nz` seed of the `rulespec-be`/`rulespec-ca` bulk system.
The encoder and the CI gates own correctness. This system is **plumbing**: it
never edits or invents generated values. Its only judgement is *which* provisions
to queue.

## Corpus source (unblocked 2026-07-08)

The NZ corpus was **empty** (0 rows) — the blocker to any NZ bulk generation. The
Income Tax Act 2007 (Public Act 2007 No 97 = `nz/statute/act/public/2007/0097`)
was ingested at version `2026-07-08`:

```
download-nz-legislation-api --legislation-type act --search-term "Income Tax Act 2007"
  -> extract-nz-legislation (PCO XML, 4134 provisions)
  -> sign-ingest-manifest (ed25519, key-id axiom-corpus-ingest-v1)
  -> sync-r2 (bucket axiom-corpus)
  -> load-supabase --synthesize-missing-parents  (release_scope nz/statute v2026-07-08 published)
```

`corpus.current_provisions` now returns **4135** `nz` rows (4134 sections + 1
synthesized act container). Every worklist `citation` was verified present by
exact `citation_path` after the ingest — the encoder never invents NZ numbers.

### Scoping caveats carried from the ingest

- Only `section/<id>`-form paths are queued. The extractor emits
  `.../<kind>/<single-token>` and does **not** emit nested `schedule/1/part/B`,
  `subpart/HM`, `subpart/RE`, `part/N`, `schedule/N/definition/*`, or
  `.../subclause/*` paths that some hand-built modules cite — those need a
  converter enhancement or re-pointing at the enclosing section.
- `nz/agency/ird/*` and `nz/secondary-legislation/pco-drafted/*` pseudo-cites in
  the hand-built modules have **no** legislation source and are not ingestable
  from PCO XML — out of scope here.
- Token drift is possible (label "RD 3" → `RD-3` vs a module citing `RD3`);
  confirm emitted paths before queueing letter+number sections outside subpart MD/ME/MG.

## Pieces

| File | Role |
| --- | --- |
| `bulk/worklist.yaml` | The durable queue. One entry per section. Committed. |
| `bulk/compute_matrix.py` | Worklist → selection / status lookups; single source of truth. |
| `bulk/roots_for.py` | Maps an applied module path to `guard-generated --roots` (`nz`). |

## Not yet armed (remaining, deprioritized behind the corpus ingest)

This seed intentionally does **not** include the GitHub dispatcher workflow,
branch protection, `allow_auto_merge`, or the `BULK_ENCODE_TOKEN` secret. Arm
them by mirroring `rulespec-be` before draining: required `validate / validate`
check (`strict: false`), repo "Allow auto-merge", the dispatcher port, and the
two Actions secrets. Until then, the drain **never** uses `--admin`, never
bypasses a red check, and never merges directly — the same safety model as the
sibling repos.
