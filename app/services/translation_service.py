from typing import Any
from deep_translator import GoogleTranslator

LANGUAGE_CODES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Marathi": "mr"
}


def translate_value(value: Any, target_lang: str) -> Any:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value

        try:
            return GoogleTranslator(
                source="auto",
                target=target_lang
            ).translate(text)
        except Exception:
            return value

    if isinstance(value, list):
        return [translate_value(item, target_lang) for item in value]

    if isinstance(value, dict):
        return {
            key: translate_value(val, target_lang)
            for key, val in value.items()
        }

    return value


def translate_json(data: dict, language: str) -> dict:
    target_lang = LANGUAGE_CODES.get(language)

    if not target_lang:
        raise ValueError(f"Unsupported language: {language}")

    return translate_value(data, target_lang)