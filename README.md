<p align="center">
  <img src="./banner.svg" alt="Updates in Progress" width="100%"/>
</p>

<h1 align="center">⚡ OneJob AI Portal</h1>
<p align="center">
  <b>AI-powered end-to-end job application platform — from resume to offer letter.</b><br/>
  <i>Intelligent matching · Automated applications · Interview prep · Resume intelligence</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active%20Development-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Stack-Python%20%7C%20React%20%7C%20MongoDB-blueviolet?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/AI-LLM%20Powered-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Deploy-Docker%20%7C%20Azure-blue?style=for-the-badge"/>
</p>

---

## 🧭 Overview

**OneJob** is a production-grade, AI-first job portal engineered to eliminate the friction of modern job hunting. Instead of manually tailoring resumes and tracking applications across dozens of platforms, OneJob provides a **unified intelligence layer** that handles:

- 🔍 **Semantic job discovery** — LLM-powered matching between your resume and live job postings
- 📝 **Resume intelligence** — AI-driven analysis, scoring, and tailoring per job description  
- 🤖 **1-click automated applications** — structured pipelines that submit applications on your behalf
- 🎯 **Interview preparation** — personalized question banks generated from the target JD and your profile
- 📊 **Application tracking** — real-time status board across all submitted applications

This is not a CRUD job board. OneJob is an **agentic platform** where AI agents work on your behalf to maximize shortlist probability.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        OneJob Platform                       │
├──────────────────┬──────────────────────┬───────────────────┤
│   React Frontend │    FastAPI Backend    │   AI Agent Layer  │
│   ─────────────  │   ────────────────   │  ───────────────  │
│  Job Dashboard   │  Auth (JWT/OAuth)    │  Resume Parser    │
│  Resume Editor   │  Job Matching API    │  JD Analyzer      │
│  Interview Prep  │  Application Engine  │  Q&A Generator    │
│  Status Tracker  │  WebSocket Events    │  Auto-Apply Bot   │
└──────────────────┴──────────────────────┴───────────────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │         Data Layer             │
              │  MongoDB · Redis Cache         │
              │  Vector Store (pgvector)       │
              │  File Storage (Azure Blob)     │
              └───────────────────────────────┘
```

---

## 🚀 Features (Current & Planned)

| Feature | Status |
|---|---|
| User auth (JWT + OAuth) | ✅ Implemented |
| Resume upload & parsing | ✅ Implemented |
| Job listing ingestion | ✅ Implemented |
| AI job-resume matching | 🔄 In Progress |
| 1-click automated apply | 🔄 In Progress |
| Interview Q&A generator | 🔄 In Progress |
| Real-time application tracker | 📋 Planned |
| Multi-platform scraping (LinkedIn, Naukri) | 📋 Planned |
| Resume optimization suggestions | 📋 Planned |
| Email notification pipeline | 📋 Planned |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, TailwindCSS, Vite |
| **Backend** | Python, FastAPI, REST APIs |
| **Database** | MongoDB (primary), Redis (caching), pgvector (embeddings) |
| **AI/ML** | LangChain, OpenAI GPT-4, HuggingFace Transformers |
| **Auth** | JWT, OAuth2 (Google) |
| **DevOps** | Docker, Docker Compose, Azure Container Services |
| **Storage** | Azure Blob Storage |

---

## 📁 Project Structure

```
OneJob/
├── backend/
│   ├── api/              # FastAPI route handlers
│   ├── agents/           # AI agent definitions (resume, apply, interview)
│   ├── core/             # Config, auth, database connections
│   ├── models/           # MongoDB schema models (Pydantic)
│   ├── services/         # Business logic layer
│   └── main.py           # Application entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route-level page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API client layer
│   │   └── store/        # Global state (Zustand)
│   └── vite.config.ts
├── storage/              # File handling utilities
├── docker-compose.yml    # Full-stack local orchestration
└── .env.example          # Environment variable template
```

---

## ⚙️ Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- MongoDB (or use Docker Compose)

### 1. Clone & Configure
```bash
git clone https://github.com/jaswanth6988/OneJob.git
cd OneJob
cp .env.example .env
# Fill in your OPENAI_API_KEY, MONGODB_URI, etc.
```

### 2. Run with Docker (Recommended)
```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`

### 3. Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT |
| `POST` | `/resume/upload` | Upload and parse resume |
| `GET` | `/jobs/match` | Get AI-matched jobs for current user |
| `POST` | `/apply/{job_id}` | Trigger automated application |
| `GET` | `/applications` | List all submitted applications |
| `POST` | `/interview/prep/{job_id}` | Generate personalized interview Q&A |

Full interactive API documentation available at `/docs` when running locally.

---

## 🔐 Environment Variables

```env
# App
SECRET_KEY=your-secret-key
DEBUG=True

# Database
MONGODB_URI=mongodb://localhost:27017/onejo

# AI
OPENAI_API_KEY=sk-...

# Azure (Production)
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_CONTAINER_NAME=onejo-storage
```

---

## 🗺️ Roadmap

```
Q3 2026  ──► Core platform + Auth + Resume parsing       [✅ Done]
Q4 2026  ──► AI job matching + Auto-apply pipeline       [🔄 Active]
Q1 2027  ──► Multi-platform scraper + Interview AI       [📋 Next]
Q2 2027  ──► Mobile app + SaaS launch                   [📋 Future]
```

---

## 🤝 Contributing

This project is in active development. Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create your feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feat/your-feature`
5. Open a Pull Request

---

## 👨‍💻 Author

**N V K Jaswanth Srighakollapu**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/n-v-k-jaswanth-srighakollapu)
[![GitHub](https://img.shields.io/badge/GitHub-jaswanth6988-black?style=flat&logo=github)](https://github.com/jaswanth6988)

---

<p align="center"><i>Built with ❤️ and a lot of LLM tokens. Production deployment coming soon.</i></p>
