# AI Job Apply Portal

A free, local-first, automated AI job-apply portal for personal use.

## Features

- **Resume Manager** — Store multiple resume variants, ATS scoring, keyword analysis, PDF/DOCX export
- **Job Discovery** — Crawl job sites, normalize, deduplicate, AI-powered scoring and matching
- **Auto-Apply** — Playwright-based automation with per-site adapters
- **Manual Review** — Intelligent fallback when automation fails, with AI-assisted recovery
- **AI Assistant** — Match explanations, resume suggestions, skill gaps, cover letters
- **Analytics** — Track applications, success rates, and improvement opportunities

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.11+, Pydantic v2 |
| Database | MongoDB 7 (Motor + Beanie ODM) |
| Cache/Queue | Redis 7, Celery |
| AI | Google Gemini API (free tier) |
| Automation | Playwright (Python) |

## Quick Start

### 1. Start Infrastructure

```bash
docker-compose up -d
```

### 2. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Configure

Copy `.env.example` to `.env` and update:
- `GEMINI_API_KEY` — Get from [Google AI Studio](https://aistudio.google.com/)
- `JWT_SECRET_KEY` — Generate a random 32+ char string
- `SECRET_KEY` — Generate a random 64+ char string

## Project Structure

```
ai-job-portal/
├── frontend/          # Next.js app (port 3000)
├── backend/           # FastAPI app (port 8000)
├── storage/           # Local file storage
│   ├── resumes/       # Uploaded resume files
│   ├── screenshots/   # Application screenshots
│   └── logs/          # Application logs
├── docker-compose.yml # MongoDB + Redis
├── .env               # Environment variables
└── README.md
```

## License

Personal use — not for distribution.
