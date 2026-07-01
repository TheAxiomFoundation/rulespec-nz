# Roadmap Snapshot

This repo currently has no active conductor tracks. The completed work is
archived in `conductor/tracks.md`, and the remaining planning surface should be
treated as a forward-looking roadmap rather than a live queue.

## Current state

- Active conductor tracks: none.
- Archived legislation and support tracks: complete.
- Current repo focus: maintain the completed registry, keep the project-ledger
  metadata consistent, and only add new tracks when a genuinely new backlog is
  identified.

## Historical sequencing

The prior next-step sequence was:

1. Paid parental leave, child support, and family-related payments.
2. Rates rebates and local-government-adjacent assistance.
3. Residency, citizenship, and immigration predicates.
4. Payroll deductions and savings interfaces.
5. GST and indirect-tax interfaces.

That ordering is now historical only because those tracks are already archived in
the registry.

## Support-track sequencing

The prior support-track order was:

1. Corpus citation pinning and provenance QA.
2. Oracle comparison and historical rule reconciliation.
3. Dynamic simulation and research extensions.

That ordering is also historical only because those tracks are already archived.

## Forward-looking guidance

- Keep future tracks small and source-grounded.
- Reuse the existing income-interface and tax-surface primitives instead of
  re-encoding shared abstractions.
- Treat the NLP pipeline as helpful for extraction, but not as a dependency for
  maintaining the current registry truth.
- When a new backlog appears, update this file first so it reflects the live
  planning order before creating new conductor tracks.

## Ledger alignment

- Keep the roadmap issue, project board, and conductor registry aligned on the
  same current-state message.
- Preserve the distinction between archived work and any newly proposed track
  family.
