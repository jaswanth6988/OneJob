# OneJob upgrade — review build

This ZIP contains the full project source, preserving the existing Next.js / FastAPI / MongoDB / Celery architecture. It is a substantial functional upgrade, not a claim of parity with mature commercial job platforms.

## Start on Windows (PowerShell)

Use Node 22, Python 3.12 and Docker Desktop. From the extracted OneJob directory:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements-dev.txt
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put that generated value into JWT_SECRET_KEY in `.env`; generate a different SECRET_KEY. Set GEMINI_API_KEY and a GEMINI_MODEL available to your account for live AI. Configure the original connector credentials as required. Do not commit `.env`.

```powershell
docker compose up -d
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a second activated terminal:

```powershell
python -m celery -A backend.core.celery_app worker --pool=solo --loglevel=info
```

In a third terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000 and create an account. Existing records associated with the old shared `dev@example.com` bypass account are not automatically reassigned; back up the database before any deliberate migration. Public job records remain available. The frontend proxies `/api` to port 8000; set API_INTERNAL_URL for a different backend address.

## What changed

- Literal multi-keyword search, combined location/company/skills/source/work-mode/seniority/industry/recency/salary-disclosure filters; stable server pagination; expired listings excluded by default.
- Live source facets instead of a three-source hard-coded menu. Filters persist in the URL. Search operates on available jobs; discovery is a separate background action with status/error reporting.
- Account-backed saved jobs, browser-local account-scoped saved searches, 85%/90% personal match filters. Saved searches do not send email alerts.
- Responsive search layout, mobile navigation, light/dark/system themes, keyboard focus states, reduced-motion support, error/empty/loading states.
- Real registration and login instead of shared dummy authentication; refresh-token validation, ownership checks, private resume downloads and application screenshots.
- Real resume detail/edit view replaces static sample content. Resume structure rating has a visible, deterministic checklist; it is not a commercial ATS score or hiring probability.
- AI interview/tailoring failures no longer produce arbitrary ratings. Personal match scores are isolated per account. External job descriptions no longer execute arbitrary HTML.
- Worker queue failures return an error instead of claiming that an application started. Automatic application remains dependent on each external site's forms and credentials.
- Linux import capitalization, missing Badge variants, Next.js route parameter types and API types corrected so production builds succeed.

## Verification and limits

Run `python -m pytest -q` at the root and `npm run build` inside frontend. API tests use the real FastAPI routes and Beanie models with an in-memory Mongo-compatible test double, not a live MongoDB server. They cover filter intersections and literal special characters, expiry, sorting/pagination, invalid input, authentication, refresh-token types, saved-job isolation, resume ownership and personal score isolation, plus rejection of fabricated AI fallback scores.

Browser visual/interaction QA is NOT verified: this execution environment's managed preview launcher passes Vite-only flags to Next.js. The production compilation and type checks are separately verified. Test desktop/mobile layouts on your machine before publishing.

Live Gemini requests, live crawlers, Redis/Celery execution, real MongoDB behavior, and external application submissions are NOT verified in this environment. No live applications were submitted. No provider credentials were supplied. The legacy automation engine still needs site-by-site acceptance testing; use dry-run mode and review evidence before live submission. No accuracy percentage or universal application success rate is claimed.

Remaining product work: normalized currency/annual salary and numeric experience filtering across connectors; verified employer feeds; deduplication quality benchmarking; email alerts; password reset and email verification; rate limits and production session hardening; complete browser accessibility and visual review; production observability and backup/restore testing. Some retained secondary screens use theme compatibility styles rather than the fully rewritten search design. The existing dependency versions should undergo a security update/audit before public deployment.

## Manual acceptance checklist

1. Register two accounts; verify neither can see the other's resumes, saved jobs or application evidence.
2. Upload your own PDF/DOCX; inspect parsed text, structure checklist, edit and download the original.
3. Start worker and discover jobs. Check real source success/failure logs.
4. Combine React + a location + Remote + a source, then reset; reload the URL and paginate.
5. Save a job and search; reload and verify persistence. Switch all three themes and test a 390px mobile viewport.
6. With a working AI key, score a job, test 85/90 filters, tailor a resume, generate interview questions and evaluate an answer. Disable the key and verify explicit failure rather than invented scores.
7. Dry-run one permitted application form; inspect application logs and private screenshots. Live submission requires your deliberate selection and external site validation.

Do not overwrite a production checkout blindly. Extract to a new folder, compare changes, preserve your `.env` and storage/database, and push your reviewed source from your own Git checkout. Dependencies, builds, caches, `.git` and secrets are excluded from this ZIP.

## Second implementation iteration

Read IMPLEMENTATION_PLAN.md and ARCHITECTURE.md for the 17-part plan and actual gate status. The source now includes grounded resume passage retrieval, application preflight, truthful dry-run classification, worker claim protection, real profile mappings, and an updated overview design. Run `python -m playwright install chromium` before local browser automation if neither Edge nor Chrome is installed. Do not test live submission against jobs you do not intend to apply for. The generic adapter cannot guarantee compatibility with every external form.
