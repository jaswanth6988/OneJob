# OneJob implementation plan

Acceptance is measured per capability, not an invented product-completion percentage.

1. Architecture and reproducible setup — documented modules, environment contract, install/test commands.
2. Account lifecycle — real authentication, refresh, ownership and explicit failures.
3. Profile integrity — persist actual candidate fields, never invent application identity.
4. Search correctness — combined literal filters, paging, stable ordering and expiry.
5. Saved workspace — account-backed shortlist and saved-search persistence.
6. Ingestion quality — source identity, deduplication and truthful task status.
7. Resume pipeline — upload, parse, edit, download and explainable structure checks.
8. Evidence retrieval — grounded resume passages, isolated by account.
9. AI contracts — validate structured outputs, reject fabricated fallback scores.
10. Matching — per-account results, thresholds and job-specific explanations.
11. Interview preparation — questions, answer feedback and provider failure states.
12. Application preflight — owned resume, real profile, URL validation and readiness.
13. Application execution — no fabricated fields, distinct dry-run state, submission evidence.
14. Application reliability — duplicate protection, no blind resubmission, worker ownership.
15. Premium interface — coherent typography, restrained borders, themes and mobile layouts.
16. Quality gates — API and service tests, production build, documented live-test gaps.
17. Handoff — complete source ZIP, architecture and verification notes.

Live provider and external website acceptance require credentials and permitted test targets. Those gates remain explicitly separate from local implementation/testing.
