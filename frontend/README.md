# FinPal frontend — drop-in static package

Plain HTML, CSS and JavaScript. No build step, no framework, no bundler, no CDN
JavaScript. Drop the folder into the existing FastAPI project and serve it.

```
frontend/
  index.html      landing page
  app.html        AI advisor (chat + voice)
  dashboard.html  financial dashboard
  styles.css      the whole design system
  api.js          API layer + shared helpers
  README.md       this file
```

The only external request is the Google Fonts stylesheet for Sora and Manrope.
Remove the two `<link>` tags in each page's `<head>` if you want a fully offline
build — the CSS falls back to system sans-serif.

---

## 1. Install

Replace the existing `frontend/` directory with this one:

```bash
rm -rf frontend && unzip finpal-frontend.zip
```

No Python code changes are required.

---

## 2. Run it in development

Serve the folder over HTTP — **do not open the files with `file://`** if you
want the microphone, because `getUserMedia` requires a secure context
(`https://` or `http://localhost`).

Terminal 1 — the backend:

```bash
cd backend && .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000
```

Terminal 2 — the static files:

```bash
cd frontend && python -m http.server 5500
```

Then open <http://localhost:5500/index.html>.

The pages are served from `:5500` and the API lives on `:8000`, so this is a
cross-origin setup. It already works: `backend/app/main.py` registers
`CORSMiddleware` with `allow_origins=["*"]`. If you tighten that for production,
list your real origin explicitly and keep `POST`, `GET` and `Content-Type`
allowed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://finpal.example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Pointing the pages at a different API

`api.js` resolves the API base in this order, first match wins:

| Order | Source | Example |
|---|---|---|
| 1 | `window.FINPAL_API_BASE`, set before `api.js` loads | `<script>window.FINPAL_API_BASE='http://localhost:8000'</script>` |
| 2 | `?api=` in the query string | `app.html?api=http://192.168.1.7:8000` |
| 3 | `file://` pages | falls back to `http://localhost:8000` |
| 4 | **default** | same origin — production needs no configuration |

For the two-terminal setup above, either append `?api=http://localhost:8000`
once (it survives navigation between pages only if you keep re-adding it), or
add this line above `<script src="api.js">` in the three HTML files while
developing:

```html
<script>window.FINPAL_API_BASE = 'http://localhost:8000';</script>
```

Delete that line before deploying — same-origin is the production default.

---

## 3. Serve it from FastAPI in production (single origin, no CORS)

Mount the folder in `backend/app/main.py`, after `app.include_router(voice_router)`:

```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
```

Notes:

- Mount **last**. `StaticFiles` at `/` is a catch-all; anything mounted after it
  is unreachable, and `/api/...` must stay ahead of it.
- `html=True` serves `index.html` at `/` and resolves `app.html` and
  `dashboard.html` by name.
- Adjust `parents[2]` if you relocate the folder. From `backend/app/main.py`
  that resolves to `<project>/frontend`.

With this mount everything is same-origin, `api.js` needs no configuration, and
CORS becomes irrelevant.

---

## 4. Backend contract used

Unchanged from `backend/app/api/voice.py`:

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `/api/sessions` | — | `{ session_id, user_id }` |
| `POST` | `/api/sessions/{id}/chat/stream` | `{ "message": "…" }` | SSE `data:` lines — `{type:"token",text}`, `{type:"done",profile,user_text}`, `{type:"error",text}` |
| `POST` | `/api/sessions/{id}/voice` | multipart, field `audio` | `{ user_text, advisor_text, audio_b64, profile }` |
| `GET` | `/api/sessions/{id}/profile` | — | the profile object |

`POST /api/sessions/{id}/chat` (non-streaming) is left untouched and unused; the
UI streams instead.

### Sessions

The session id lives in the URL as `?session=<id>` and nowhere else — no
`localStorage`, no cookie. That preserves the "clear session on every page load"
behaviour: a fresh visit to `app.html` creates a new session, while
`app.html?session=<id>` resumes an existing one. `app.html` writes the new id
into the address bar with `history.replaceState`, so reloading keeps the thread
and the nav links carry the id between the three pages.

If a `?session=` id no longer exists (the API answers 404), `app.html` says so
and starts a fresh session rather than failing; `dashboard.html` shows a
"session unavailable" notice with a link back to the advisor.

### Voice

`api.js` negotiates the recording format in this order, taking the first that
`MediaRecorder.isTypeSupported` accepts: `audio/webm;codecs=opus`, `audio/webm`,
`audio/ogg;codecs=opus`, `audio/ogg`, `audio/mp4`. The filename extension is set
to match, which is what the backend's `_EXT_MAP` uses to name the temp file for
Whisper. If none is supported the browser default is used.

Blocked or missing microphones, browsers without `MediaRecorder`, and blocked
autoplay of the TTS reply are all handled: the status line explains what
happened and the text composer keeps working.

---

## 5. Design

- **Direction:** compact snapshot hero — a real numbers panel above the fold on
  every page, not decoration.
- **Palette:** Ink `#101F1A`, Pine `#17594A`, Mint `#6FD6A6`, Mist `#EFF4F1`,
  plus white surfaces and a `#D5E1DB` border. Signal colours stay in family.
- **Type:** Sora for headings, Manrope for body.
- **Alignment:** everything is centred — buttons, headings, labels, metrics,
  body copy, profile values and chat messages.
- **Shape:** flat fills, 1px borders, radii of 4/6/8px, nothing larger.
- **Layout:** responsive bento grids via `repeat(auto-fit, minmax(...))`. Long
  rupee figures and labels wrap rather than overflow (`overflow-wrap: anywhere`,
  `min-width: 0` on grid children), and the column charts scroll horizontally
  inside their own box.

### Performance and accessibility

Removed from the previous build: GSAP and ScrollTrigger, the hero canvas,
particles, cursor tracking, 3D tilt, decorative timers and heavy blur. What
remains is a `120ms` colour/border transition and a 1px press offset on direct
interaction only.

- `prefers-reduced-motion: reduce` cuts every transition to ~0ms.
- The transcript uses `scroll-behavior: auto` and is scrolled by assignment —
  streamed tokens never trigger smooth scrolling.
- Semantic `<button>`, `<form>`, `<nav>`, `<section>`; every control is
  keyboard-operable and has a visible `:focus-visible` ring.
- The transcript is `role="log" aria-live="polite"`; the status line is
  `role="status"`, so connecting / ready / recording / thinking / speaking /
  error states are announced.
- The DOM charts carry `role="img"` with an `aria-label` listing the values.
- All user and model text is inserted with `textContent`, never `innerHTML`.

---

## 6. Checked before packaging

Served over `http://localhost` against the live FastAPI backend:

- landing → advisor → dashboard navigation, with the session id carried through
- session creation, streamed chat tokens, and the profile panel updating on `done`
- `dashboard.html?session=<id>` rendering the profile-derived snapshot
- `dashboard.html` with no `?session` and with an unknown id
- desktop (1280px) and mobile (375px) layouts, no horizontal page scroll
- browser console clean — no errors or warnings
