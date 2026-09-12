from gtts import gTTS
import uuid
import os

os.makedirs("audio", exist_ok=True)

GTTS_LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Marathi": "mr"
}


def text_to_speech(text: str, language: str) -> str:
    if not text or not text.strip():
        raise ValueError("No text provided for speech generation")

    lang_code = GTTS_LANGUAGE_CODES.get(language, "en")

    filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join("audio", filename)

    tts = gTTS(text=text, lang=lang_code)
    tts.save(output_path)

    return output_path