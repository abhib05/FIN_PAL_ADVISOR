import asyncio
import base64
import json as _json
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, status
from groq import RateLimitError as GroqRateLimitError
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.db.models import ConversationSession, User
from app.db.session import get_db
from app.orchestrator.conversation import run_turn
from app.orchestrator.tools import default_profile
from app.voice.stt import transcribe
from app.voice.tts import synthesize

router = APIRouter(prefix="/api", tags=["voice"])

_EXT_MAP = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".mp4",
    "audio/wav": ".wav",
    "audio/mpeg": ".mp3",
}


def _get_or_create_session(session_id: str, db: Session) -> ConversationSession:
    session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions")
def create_session(db: Session = Depends(get_db)):
    user_id = str(uuid.uuid4())
    user = User(id=user_id)
    db.add(user)
    session = ConversationSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        financial_profile=default_profile(user_id),
        messages=[],
    )
    db.add(session)
    db.commit()
    return {"session_id": session.id, "user_id": user_id}


@router.post("/sessions/{session_id}/voice")
async def voice_turn(
    session_id: str,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    session = _get_or_create_session(session_id, db)

    # Save uploaded audio to temp file
    audio_bytes = await audio.read()
    content_type = (audio.content_type or "audio/webm").split(";")[0]
    suffix = _EXT_MAP.get(content_type, ".webm")

    tmp_in = Path(tempfile.mktemp(suffix=suffix))
    tmp_in.write_bytes(audio_bytes)

    # STT
    try:
        user_text = await run_in_threadpool(transcribe, tmp_in)
    finally:
        tmp_in.unlink(missing_ok=True)

    if not user_text.strip():
        raise HTTPException(status_code=422, detail="Could not transcribe audio — please try again")

    # Conversation brain
    advisor_text, updated_profile, updated_messages = await run_in_threadpool(
        run_turn,
        user_text,
        session.financial_profile,
        session.messages,
    )

    # Persist session
    session.financial_profile = updated_profile
    session.messages = updated_messages
    flag_modified(session, "financial_profile")
    flag_modified(session, "messages")
    db.commit()

    # TTS
    tmp_out = Path(tempfile.mktemp(suffix=".wav"))
    try:
        await run_in_threadpool(synthesize, advisor_text, tmp_out)
        audio_b64 = base64.b64encode(tmp_out.read_bytes()).decode()
    finally:
        tmp_out.unlink(missing_ok=True)

    return {
        "user_text": user_text,
        "advisor_text": advisor_text,
        "audio_b64": audio_b64,
        "profile": updated_profile,
    }


class ChatRequest(BaseModel):
    message: str


@router.post("/sessions/{session_id}/chat")
async def text_turn(
    session_id: str,
    body: ChatRequest,
    db: Session = Depends(get_db),
):
    """Text fallback — same pipeline as voice but skips STT and TTS."""
    session = _get_or_create_session(session_id, db)

    try:
        advisor_text, updated_profile, updated_messages = await run_in_threadpool(
            run_turn,
            body.message,
            session.financial_profile,
            session.messages,
        )
    except GroqRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="The advisor is a little busy right now — please wait a moment and try again.",
        )

    session.financial_profile = updated_profile
    session.messages = updated_messages
    flag_modified(session, "financial_profile")
    flag_modified(session, "messages")
    db.commit()

    return {
        "user_text": body.message,
        "advisor_text": advisor_text,
        "profile": updated_profile,
    }


@router.post("/sessions/{session_id}/chat/stream")
async def text_turn_stream(
    session_id: str,
    body: ChatRequest,
    db: Session = Depends(get_db),
):
    """Streaming version of text_turn — tokens arrive word by word via SSE."""
    session = _get_or_create_session(session_id, db)

    try:
        advisor_text, updated_profile, updated_messages = await run_in_threadpool(
            run_turn,
            body.message,
            session.financial_profile,
            session.messages,
        )
    except GroqRateLimitError:
        async def _rate_limit_event():
            yield f"data: {_json.dumps({'type': 'error', 'text': 'The advisor is a little busy — please wait a moment and try again.'})}\n\n"
        return StreamingResponse(_rate_limit_event(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    session.financial_profile = updated_profile
    session.messages = updated_messages
    flag_modified(session, "financial_profile")
    flag_modified(session, "messages")
    db.commit()

    async def _generate():
        words = advisor_text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield f"data: {_json.dumps({'type': 'token', 'text': chunk})}\n\n"
            await asyncio.sleep(0.04)
        yield f"data: {_json.dumps({'type': 'done', 'profile': updated_profile, 'user_text': body.message})}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/sessions/{session_id}/profile")
def get_profile(session_id: str, db: Session = Depends(get_db)):
    session = _get_or_create_session(session_id, db)
    return session.financial_profile
