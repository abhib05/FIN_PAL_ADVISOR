"""
Stage 2 — Groq audio round-trip test.
TTS (Orpheus) → wav → STT (Whisper) → accuracy + latency report.

Phrases chosen to stress-test number mishearing:
  "15" vs "50", "30k" vs "13k", multi-digit rupee amounts, decimal rates.

Usage:
    cd backend
    python test_stage2.py
"""
import io
import os
import sys
import time
from pathlib import Path

# UTF-8 output for Windows terminals
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from groq import Groq

GROQ_API_KEY  = os.environ["GROQ_API_KEY"]
TTS_MODEL     = os.environ.get("GROQ_TTS_MODEL", "canopylabs/orpheus-v1-english")
TTS_VOICE     = os.environ.get("GROQ_TTS_VOICE", "tara")
STT_MODEL     = os.environ.get("GROQ_STT_MODEL", "whisper-large-v3")

AUDIO_DIR = Path(__file__).parent / "audio_test"
AUDIO_DIR.mkdir(exist_ok=True)

client = Groq(api_key=GROQ_API_KEY)

DIVIDER = "=" * 65

# --- Test phrases ----------------------------------------------------------
# Each entry: (id, spoken_text, key_number_aliases)
# Aliases: list of (spoken_form, digit_form) tuples — Whisper normalises
# spelled-out numbers to digits, so both forms count as a correct transcription.
PHRASES = [
    (
        "rapport",
        "Nice to meet you! To get started, could you tell me what year of study you are in?",
        [],
    ),
    (
        "numbers_15k_vs_50k",
        "You get fifteen thousand rupees a month from your parents. Just confirming, fifteen thousand, not fifty thousand?",
        [("fifteen thousand", "15,000"), ("fifty thousand", "50,000")],
    ),
    (
        "numbers_30k_vs_13k",
        "Your hostel fees are thirteen thousand rupees, and your monthly expenses total thirty thousand rupees.",
        [("thirteen thousand", "13,000"), ("thirty thousand", "30,000")],
    ),
    (
        "emergency_fund_result",
        "Your emergency fund target is twenty-seven thousand five hundred rupees. That is about six months of essential expenses. You currently have a gap of fifteen thousand five hundred rupees.",
        [("twenty-seven thousand five hundred", "27,500"), ("fifteen thousand five hundred", "15,500"), ("six months", "six months")],
    ),
    (
        "sip_projection",
        "If you invest three thousand rupees every month at twelve percent annual returns, in five years you would have approximately two lakh forty-six thousand rupees.",
        [("three thousand", "3,000"), ("twelve percent", "12%"), ("five years", "5 years"), ("two lakh", "2 lakh")],
    ),
    (
        "emi_advice",
        "Your EMI works out to roughly fourteen thousand two hundred rupees per month on a five lakh principal at ten point five percent interest over forty-eight months.",
        [("fourteen thousand two hundred", "14,200"), ("five lakh", "5 lakh"), ("ten point five percent", "10.5%"), ("forty-eight months", "48 months")],
    ),
]

# ---------------------------------------------------------------------------

def word_tokens(text: str) -> list[str]:
    import re
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref = word_tokens(reference)
    hyp = word_tokens(hypothesis)
    if not ref:
        return 0.0
    # Simple edit-distance WER
    d = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
    for i in range(len(ref) + 1):
        d[i][0] = i
    for j in range(len(hyp) + 1):
        d[0][j] = j
    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)
    return round(d[len(ref)][len(hyp)] / len(ref), 3)


def check_key_numbers(original: str, transcribed: str, keys: list) -> dict:
    """Accept either the spoken form or the digit form as a correct transcription."""
    results = {}
    t_lower = transcribed.lower()
    for entry in keys:
        spoken, digit = entry
        hit = spoken.lower() in t_lower or digit.lower() in t_lower
        results[spoken] = hit
    return results


def run_tts(phrase_id: str, text: str) -> tuple[Path, float]:
    out = AUDIO_DIR / f"{phrase_id}.wav"
    t0 = time.time()
    resp = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
        response_format="wav",
    )
    resp.write_to_file(out)
    return out, round(time.time() - t0, 2)


def run_stt(audio_path: Path) -> tuple[str, float]:
    t0 = time.time()
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(audio_path.name, f),
            model=STT_MODEL,
            response_format="text",
        )
    return str(result).strip(), round(time.time() - t0, 2)


# ---------------------------------------------------------------------------

def main() -> None:
    print(f"\n{DIVIDER}")
    print(f"STAGE 2 — Groq Audio Round-Trip Test")
    print(f"  TTS: {TTS_MODEL} / voice: {TTS_VOICE}")
    print(f"  STT: {STT_MODEL}")
    print(DIVIDER)

    results = []

    for phrase_id, text, key_aliases in PHRASES:
        print(f"\n[{phrase_id}]")
        print(f"  Original : {text}")

        # TTS
        try:
            audio_path, tts_time = run_tts(phrase_id, text)
            size_kb = audio_path.stat().st_size // 1024
            print(f"  TTS      : {tts_time}s  ({size_kb} KB)")
        except Exception as e:
            print(f"  TTS ERROR: {e}")
            results.append({"id": phrase_id, "tts_ok": False})
            continue

        # STT
        try:
            transcript, stt_time = run_stt(audio_path)
            print(f"  STT      : {stt_time}s")
            print(f"  Heard    : {transcript}")
        except Exception as e:
            print(f"  STT ERROR: {e}")
            results.append({"id": phrase_id, "tts_ok": True, "stt_ok": False})
            continue

        wer = word_error_rate(text, transcript)
        key_hits = check_key_numbers(text, transcript, key_aliases)
        total_rt = round(tts_time + stt_time, 2)

        print(f"  WER      : {wer:.1%}   Round-trip: {total_rt}s")
        if key_aliases:
            for k, hit in key_hits.items():
                status = "PASS" if hit else "MISS"
                print(f"    [{status}] '{k}'")

        results.append({
            "id": phrase_id,
            "tts_ok": True,
            "stt_ok": True,
            "tts_time": tts_time,
            "stt_time": stt_time,
            "round_trip": total_rt,
            "wer": wer,
            "key_hits": key_hits,
            "key_aliases": key_aliases,
        })

    # Summary
    ok = [r for r in results if r.get("stt_ok")]
    print(f"\n{DIVIDER}")
    print("SUMMARY")
    print(DIVIDER)
    if ok:
        avg_tts = round(sum(r["tts_time"] for r in ok) / len(ok), 2)
        avg_stt = round(sum(r["stt_time"] for r in ok) / len(ok), 2)
        avg_rt  = round(sum(r["round_trip"] for r in ok) / len(ok), 2)
        avg_wer = round(sum(r["wer"] for r in ok) / len(ok), 3)
        all_keys = [hit for r in ok if r.get("key_aliases") for hit in r["key_hits"].values()]
        num_accuracy = sum(all_keys) / len(all_keys) if all_keys else None

        print(f"  Phrases tested : {len(PHRASES)}  /  completed: {len(ok)}")
        print(f"  Avg TTS latency: {avg_tts}s")
        print(f"  Avg STT latency: {avg_stt}s")
        print(f"  Avg round-trip : {avg_rt}s")
        print(f"  Avg WER        : {avg_wer:.1%}")
        if num_accuracy is not None:
            print(f"  Number accuracy: {num_accuracy:.0%}  ({sum(all_keys)}/{len(all_keys)} key numbers heard correctly)")
    else:
        print("  No successful round-trips.")

    failed = [r for r in results if not r.get("stt_ok")]
    if failed:
        print(f"\n  FAILED phrases: {[r['id'] for r in failed]}")

    print(f"\n  Audio files saved to: {AUDIO_DIR}")
    print(DIVIDER)


if __name__ == "__main__":
    main()
