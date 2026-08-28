import struct
from pathlib import Path
from groq import Groq
from app.config import get_settings

_settings = get_settings()
_client = Groq(api_key=_settings.groq_api_key)


def _fix_wav_header(path: Path) -> None:
    """
    Groq Orpheus streams WAV with placeholder sizes (0xFFFFFFFF) because
    the final file size isn't known during streaming.  Walk the RIFF chunks
    to find the actual offsets of the RIFF and data size fields, then patch
    them from the real file size.  Works regardless of how many metadata
    chunks (LIST, etc.) sit between fmt and data.
    """
    raw = bytearray(path.read_bytes())
    file_size = len(raw)

    # Fix RIFF chunk size at byte 4
    struct.pack_into("<I", raw, 4, file_size - 8)

    # Walk chunks starting after the 12-byte RIFF/WAVE header
    offset = 12
    while offset + 8 <= file_size:
        chunk_id   = raw[offset:offset + 4]
        chunk_size = struct.unpack_from("<I", raw, offset + 4)[0]
        if chunk_id == b"data":
            struct.pack_into("<I", raw, offset + 4, file_size - offset - 8)
            break
        # Advance past this chunk (header + body, padded to even boundary)
        body = chunk_size if chunk_size != 0xFFFFFFFF else 0
        offset += 8 + body + (body % 2)

    path.write_bytes(raw)


def synthesize(text: str, output_path: str | Path) -> Path:
    """Convert text to speech using Groq Orpheus TTS. Returns the output path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = _client.audio.speech.create(
        model=_settings.groq_tts_model,
        voice=_settings.groq_tts_voice,
        input=text,
        response_format="wav",
    )
    response.write_to_file(output_path)
    _fix_wav_header(output_path)
    return output_path
