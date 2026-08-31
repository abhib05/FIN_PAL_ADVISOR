# FinPal — Voice-First Financial Advisor

FinPal is a conversational financial advisor. Users chat (by text or voice)
with an AI advisor that asks about their income, expenses, and goals, then
runs deterministic financial calculators — budgeting, SIP projections, EMI
affordability, debt payoff strategy, emergency fund sizing, FI number,
subscription/BNPL trap audits — to give grounded, numeric advice instead of
guessed answers. A dashboard visualizes the resulting profile.

## How it works

The backend is a **tool-calling orchestrator**, not a chatbot that free-forms
numbers. An LLM (Groq/OpenRouter/Gemini, pluggable) drives the conversation
and decides when to call one of two tool types:

- `update_profile` — persist facts the user has shared (income, expenses,
  debts, goals) to the session's profile in the database.
- `run_calculation` — invoke a specific rules-engine function (e.g.
  `sip_projection`, `debt_payoff`, `emi`) with real numbers, so the advice
  the user receives is computed, not hallucinated.

The LLM never does the math itself — it collects inputs conversationally and
calls into `backend/app/rules_engine/` for every numeric answer.

```
frontend/  (static HTML/CSS/JS, no build step)
  index.html      landing page
  app.html        chat + voice advisor UI
  dashboard.html  profile/budget dashboard
  api.js          talks to the backend over REST + SSE

backend/
  app/main.py             FastAPI app entrypoint
  app/api/voice.py         session, chat (streaming), voice endpoints
  app/orchestrator/        system prompt, tool schemas, LLM conversation loop
  app/rules_engine/        pure calculators (budget, SIP, EMI, debt, FI number, …)
  app/voice/                Groq Whisper (STT) + Groq TTS wrappers
  app/db/                   SQLAlchemy models + session (Postgres or SQLite)
```

## Tech stack

**Backend**
- Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- SQLAlchemy 2.0 ORM, PostgreSQL (via `psycopg2`) — SQLite also works out of
  the box for local/dev use, just change `DATABASE_URL`
- LLM chat: [Groq](https://groq.com/) by default (`openai/gpt-oss-120b`),
  with optional routing to OpenRouter or Gemini for the tool-calling model
- Voice: Groq Whisper (`whisper-large-v3`) for speech-to-text, Groq
  Canopy Labs Orpheus TTS for speech-to-speech replies
- Server-Sent Events (SSE) for streaming chat responses
- `pydantic-settings` for typed env-based configuration

**Frontend**
- Plain HTML/CSS/JavaScript — no framework, no bundler, no build step
- `MediaRecorder`/`getUserMedia` for in-browser voice capture
- Google Fonts (Sora + Manrope), otherwise fully offline-capable

## Prerequisites

- Python 3.11 or newer (avoid MSYS/MinGW Python on Windows — it lacks
  prebuilt wheels for some dependencies; use a standard python.org/Windows
  Store build)
- PostgreSQL running locally (or swap `DATABASE_URL` for a SQLite file — the
  code auto-detects the scheme)
- A Groq API key ([console.groq.com](https://console.groq.com)) — required,
  no default

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/financial_advisor
# or, for zero-setup local dev:
# DATABASE_URL=sqlite:///./financial_advisor.db
```

If using Postgres, create the database once:

```bash
psql -U postgres -c "CREATE DATABASE financial_advisor;"
```

Tables are created automatically on startup (`Base.metadata.create_all`).

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Check it's up: `curl http://localhost:8000/health` → `{"status":"ok"}`

### 2. Frontend

In a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Open <http://localhost:5500/index.html>.

Since the frontend (`:5500`) and backend (`:8000`) run on different ports,
point the frontend at the API for local dev — either append
`?api=http://localhost:8000` to the URL, or add this line above
`<script src="api.js">` in each HTML file:

```html
<script>window.FINPAL_API_BASE = 'http://localhost:8000';</script>
```

(Not needed in production — see `frontend/README.md` for mounting the
frontend directly on the FastAPI app for a same-origin deploy with no CORS.)

## API surface

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/sessions` | create a new chat session |
| `POST` | `/api/sessions/{id}/chat/stream` | send a message, stream the reply (SSE) |
| `POST` | `/api/sessions/{id}/voice` | send audio, get transcript + spoken reply |
| `GET` | `/api/sessions/{id}/profile` | fetch the session's financial profile |
| `GET` | `/health` | liveness check |

## Notes

- Optional second Groq key (`GROQ_API_KEY_2`) is rotated in on rate limits.
- `CHAT_PROVIDER=openrouter` + `OPENROUTER_API_KEY`, or `CHAT_PROVIDER=gemini`
  + `GEMINI_API_KEY`, swap the conversation model while STT/TTS stay on Groq.
- See `frontend/README.md` for frontend design notes, accessibility details,
  and production (single-origin) deployment instructions.
