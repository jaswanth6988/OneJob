# Architecture and verification map

## Modules

- `frontend/src/app`: route-level screens; `components`: shared controls and layout; `lib/api.ts`: same-origin API client and single-flight session refresh.
- `backend/api`: authenticated HTTP endpoints and account ownership checks.
- `backend/models`: MongoDB persistence; `schemas`: request/response contracts.
- `backend/services`: parsing, explainable rating, evidence retrieval, AI matching and coaching.
- `backend/connectors`: source-specific ingestion adapters.
- `backend/automation/policy.py`: independently testable readiness and profile mapping.
- `backend/automation/engine.py`: browser form execution, request destination checks, dry-run and confirmation handling.
- `backend/workers`: queued background tasks with account-specific record resolution.

## Important behavior

The application worker atomically claims a queued attempt before execution. Redelivery does not repeat a claimed attempt. If execution is interrupted, manual review is required rather than blind retry. A dry run is `DRY_RUN_COMPLETE`, never `SUBMITTED`. Submission text detection is a conservative generic adapter, not proof of compatibility with every ATS. Unknown forms, authentication and CAPTCHA require handoff. Duplicate preflight checks reduce duplicate requests but are not a cross-request transaction; production deployment still needs a unique active-attempt constraint or distributed lock.

Resume evidence retrieval uses deterministic lexical passage ranking, with stable passage references. This is lightweight retrieval grounding, not embeddings or a vector database. LangChain/LangGraph were not added solely to increase framework count. The explicit API/worker/state separation remains readable; a persistent graph orchestrator can replace it when workflow branching warrants the dependency.

## Gates

- 38 automated API/service cases passed in the current suite.
- Next.js production build/type checking passed with the final API session-refresh change.
- MongoDB API behavior uses mongomock-motor in tests. No real MongoDB/Redis services were available in the execution host.
- Browser preview remains blocked by managed launcher/Next CLI incompatibility; visual quality is implemented but not browser-verified.
- Live Gemini, source crawling, and third-party submissions remain unverified without service credentials and permitted test targets.

## Changes in this iteration

A 17-part implementation plan, redesigned overview and real onboarding metrics, profile persistence, private resume evidence grounding, source-aware deduplication, application readiness checks, real identity mapping, distinct dry-run status, confirmation-based submission classification, destination request filtering, worker account isolation, redelivery claim protection, screening-answer honesty, and session renewal.

## Remaining release work

Do not describe this as 90% production-complete: no defensible denominator or live acceptance result exists. Remaining major gates include real browser regression tests and accessibility checks, production database/queue integration, source connector acceptance, per-ATS adapter testing, schema-validated AI evaluations, dependency security audit, password reset/email verification, rate limiting, transactional application deduplication, operational monitoring, deployment configuration and incident recovery.
