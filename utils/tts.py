"""
Text-to-Speech utility using gTTS (Google Text-to-Speech).
Falls back gracefully if gTTS is unavailable.
"""

import base64
import io
import logging

logger = logging.getLogger(__name__)

# Language code mapping for gTTS
LANG_CODE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Arabic": "ar",
    "Mandarin": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Italian": "it",
}


def text_to_speech_base64(text: str, language: str = "English") -> str | None:
    """
    Convert text to speech and return as base64-encoded MP3 string.
    Returns None if TTS is unavailable.
    """
    lang_code = LANG_CODE_MAP.get(language, "en")

    # Try gTTS first
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_bytes = buf.read()
        return base64.b64encode(audio_bytes).decode("utf-8")
    except ImportError:
        logger.warning("gTTS not installed. Run: pip install gtts")
    except Exception as e:
        logger.warning(f"gTTS failed: {e}")

    # Try pyttsx3 as fallback (offline TTS)
    try:
        import pyttsx3
        import tempfile
        import os

        engine = pyttsx3.init()
        engine.setProperty("rate", 165)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        engine.save_to_file(text, tmp_path)
        engine.runAndWait()

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)

        return base64.b64encode(audio_bytes).decode("utf-8")
    except ImportError:
        logger.warning("pyttsx3 not installed either.")
    except Exception as e:
        logger.warning(f"pyttsx3 failed: {e}")

    return None  # TTS unavailable – UI handles None gracefully
