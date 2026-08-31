import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.db.models import Base
from app.db.session import engine
from app.api.voice import router as voice_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Voice Financial Advisor API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)

# -----------------------------------------------------------------
# Serve the frontend static package
# Resolve the frontend/ directory relative to this file's location:
#   backend/app/main.py  →  ../../frontend
# -----------------------------------------------------------------
_FRONTEND = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)

if os.path.isdir(_FRONTEND):
    # Mount assets so styles.css, api.js etc. load from the same root
    app.mount("/frontend-assets", StaticFiles(directory=_FRONTEND), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def index_page():
        return FileResponse(os.path.join(_FRONTEND, "index.html"))

    @app.get("/app.html", include_in_schema=False)
    def advisor_page():
        return FileResponse(os.path.join(_FRONTEND, "app.html"))

    @app.get("/dashboard.html", include_in_schema=False)
    def dashboard_page():
        return FileResponse(os.path.join(_FRONTEND, "dashboard.html"))

    @app.get("/styles.css", include_in_schema=False)
    def styles():
        return FileResponse(os.path.join(_FRONTEND, "styles.css"),
                            media_type="text/css")

    @app.get("/api.js", include_in_schema=False)
    def api_js():
        return FileResponse(os.path.join(_FRONTEND, "api.js"),
                            media_type="application/javascript")


@app.get("/health")
def health():
    return {"status": "ok"}
