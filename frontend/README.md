# FinPal Frontend

Framework-free, build-step-free static package for the FinPal FastAPI backend.

---

## File map

| File | Purpose |
|---|---|
| `index.html` | Landing page — compact financial snapshot, budget breakdown, feature list, advisor preview |
| `app.html` | AI financial advisor — streamed chat, voice input, live profile panel |
| `dashboard.html` | Student finance dashboard — snapshot, budget, expenses, emergency fund, debt, goals, SIP projection, recommendations |
| `styles.css` | Single shared stylesheet — dark charcoal/cyan theme, all CSS custom properties defined in `:root` |
| `api.js` | API layer — session management, streaming SSE chat, voice upload, microphone helpers, audio playback, formatting utilities |
| `README.md` | This file |

---

## Where to put the files

Copy the entire `frontend/` directory into the FastAPI repository root:

```
your-repo/
  backend/
    app/
      main.py          ← Python backend (do not modify)
  frontend/            ← copy here
    index.html
    app.html
    dashboard.html
    styles.css
    api.js
    README.md
```

---

## Mounting and serving the static files

Add the following to [`backend/app/main.py`](backend/app/main.py) **after** the router is included:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Resolve path from this file's location
_FRONTEND = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')

# Mount /static so individual assets can be referenced
app.mount('/static', StaticFiles(directory=_FRONTEND), name='static')

# Route the three pages explicitly so their canonical paths work
@app.get('/', include_in_schema=False)
def root():
    return FileResponse(os.path.join(_FRONTEND, 'index.html'))

@app.get('/app.html', include_in_schema=False)
def advisor_page():
    return FileResponse(os.path.join(_FRONTEND, 'app.html'))

@app.get('/dashboard.html', include_in_schema=False)
def dashboard_page():
    return FileResponse(os.path.join(_FRONTEND, 'dashboard.html'))
```

Install the static-files dependency if it is not already present:

```bash
pip install aiofiles
```

All three pages reference `styles.css` and `api.js` with relative paths (`href="styles.css"`, `src="api.js"`), so they resolve correctly whether the files are served from the root or from any other path prefix.

---

## Development: different origins (CORS)

The backend already has a wide CORS policy (`allow_origins=["*"]`), so cross-origin requests from a browser dev-server work without further changes.

If you narrow that policy in future, add your frontend origin explicitly:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-deployed-site.com"],
    ...
)
```

---

## Setting the API base URL

### Production (same origin)

No change needed. `api.js` defaults to same-origin requests (`BASE = ''`).

### Development (different ports)

**Option 1 — query string (no code change):**
```
http://localhost:5173/app.html?api=http://localhost:8000
```

**Option 2 — set before the script loads:**
```html
<script>window.FINPAL_API_BASE = 'http://localhost:8000';</script>
<script src="api.js"></script>
```

All three HTML files already contain this line pointing to `http://localhost:8000`. Remove or change it before deploying to production.

**Priority order** (first match wins):
1. `window.FINPAL_API_BASE` set before `api.js` loads
2. `?api=<base>` query parameter
3. `file://` protocol → `http://localhost:8000`
4. Same origin (production default)

---

## Session ID flow

Sessions are keyed by a UUID created server-side on `POST /api/sessions`.

The session ID travels through the UI via the `?session=<id>` query parameter:

1. `app.html` creates (or continues) a session on load, then calls `history.replaceState` to put the ID in the URL without a page reload.
2. Navigation links on every page are updated in JS to carry `?session=<id>` forward.
3. `dashboard.html` reads `?session=<id>` and calls `GET /api/sessions/{id}/profile` to populate the page.
4. If the session parameter is missing or the session has expired, each page shows a clear empty/error state and links back to `app.html`.

---

## Backend response fields the UI expects

### `POST /api/sessions` → `{ session_id, user_id }`

| Field | Type | Used for |
|---|---|---|
| `session_id` | string (UUID) | stored in URL, passed to all subsequent calls |

### `POST /api/sessions/{id}/chat/stream` ← `{ message: string }`

Server-Sent Events, one JSON payload per `data:` line:

| Event type | Payload | Used for |
|---|---|---|
| `token` | `{ type: "token", text: string }` | append to the current assistant bubble |
| `done` | `{ type: "done", profile: object, user_text: string }` | refresh the profile panel |
| `error` | `{ type: "error", text: string }` | show an error bubble |

### `POST /api/sessions/{id}/voice` ← multipart `audio` field

| Field | Type | Used for |
|---|---|---|
| `user_text` | string | display the transcribed user message |
| `advisor_text` | string | display the advisor reply |
| `audio_b64` | string (base64 WAV) | play the TTS response |
| `profile` | object | refresh the profile panel |

### `GET /api/sessions/{id}/profile` → profile object

Top-level keys used by the dashboard:

| Key | Sub-keys accessed |
|---|---|
| `money_in` | `family_support_amount`, `gig_income_amount`, `scholarship_stipend_amount`, `income_stability` |
| `expenses` | `housing.amount`, `commute.amount`, `food_beyond_mess`, `split_shared_expenses`, `subscriptions`, `bnpl_usage.apps_used`, `bnpl_usage.typical_monthly_amount`, `bnpl_usage.missed_or_min_only`, `discretionary` |
| `safety_net` | `personal_savings_amount`, `health_insurance_cover` |
| `academic` | `year_of_study`, `expected_graduation_year` |
| `debt` | array of `{ type, name, amount, outstanding, apr, interest_rate }` |
| `credit` | `cards`, `total_limit`, `typical_utilization_pct` |
| `goals` | array of `{ name, goal, target_amount, amount, saved_amount, current_amount, timeline, by }` |
| `conversation_phase` | string label shown in the eyebrow badge |

---

## Design notes

- The dark charcoal/cyan palette is defined entirely as CSS custom properties in `styles.css` under `:root`. Change the tokens there to retheme every page at once.
- Fonts are loaded from Google Fonts (Sora for headings, Manrope for body). Both declarations include system-font fallbacks (`ui-sans-serif, system-ui, 'Segoe UI', Roboto, Arial, sans-serif`) so the UI remains readable if the remote fonts are unavailable.
- All visualisations (budget bars, spending columns, goal progress) are built with plain HTML `div` elements and CSS. No `<canvas>`, no third-party chart libraries.
- No continuous animations, no canvas loops, no scroll-triggered effects. All transitions are direct-interaction only (hover/focus/active) and are suppressed for users who prefer reduced motion.
- The screenshot referenced in the design brief was used as a structural composition reference only; it is not embedded in the website and is not required at runtime.

---

## Validation checklist

Before deploying, verify locally against the running FastAPI backend:

- [ ] Session creation (`POST /api/sessions`) succeeds and the URL updates with `?session=<id>`
- [ ] Streamed text chat delivers tokens word-by-word and the profile panel updates on `done`
- [ ] Profile loading (`GET /api/sessions/{id}/profile`) populates the dashboard
- [ ] Voice upload sends a multipart `audio` field, transcription appears, TTS audio plays
- [ ] Navigating index → app → dashboard → app carries the session ID throughout
- [ ] Session continuation: close and reopen `app.html?session=<id>`, see "Welcome back"
- [ ] Desktop and narrow mobile: all cards centre-aligned, no horizontal overflow
- [ ] Dark palette passes WCAG AA contrast for body text on card backgrounds
- [ ] User (cyan) and assistant (dark surface) chat bubbles remain visually distinct
- [ ] No console errors, no canvas loops, no network requests after the page is idle
