from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/health")
def health():
    return {"status": "ok"}
