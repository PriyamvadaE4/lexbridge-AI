from fastapi import APIRouter, UploadFile, Form
from typing import Literal
import shutil
import os

from app.services.pdf_extractor import extract_text
from app.services.groq_service import summarize_document
from app.services.translation_service import translate_json
from app.services.rag_service import store_document, set_language
from app.services.speech_service import text_to_speech

router = APIRouter()

os.makedirs("uploads", exist_ok=True)


def extract_text_from_section(analysis: dict, section: str) -> str:
    data = analysis.get(section)

    if data is None:
        return ""

    if isinstance(data, list):
        parts = []
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    parts.append(f"{key}: {value}")
            else:
                parts.append(str(item))
        return ". ".join(parts)

    if isinstance(data, dict):
        parts = []
        for key, value in data.items():
            parts.append(f"{key}: {value}")
        return ". ".join(parts)

    return str(data)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile,
    language: Literal[
        "English",
        "Telugu",
        "Hindi",
        "Tamil",
        "Kannada",
        "Marathi"
    ] = Form(...),
    speech_section: Literal[
        "simple_summary",
        "important_clauses",
        "risks",
        "financial_details",
        "important_dates",
        "farmer_responsibilities",
        "farmer_rights",
        "final_recommendation"
    ] = Form("simple_summary")
):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1) Extract full original text from PDF
    document_text = extract_text(file_path)

    # 2) Store ORIGINAL text in RAG for /ask
    store_document(document_text)

    # 3) Save selected language for /ask
    set_language(language)

    # 4) Analyze original document with Groq
    analysis = summarize_document(document_text)

    # 5) Translate analysis JSON only for response/speech
    if language == "English":
        translated_analysis = analysis
    else:
        translated_analysis = translate_json(analysis, language)

    # 6) Generate speech from translated analysis section
    speech_text = extract_text_from_section(translated_analysis, speech_section)

    audio_file = None
    if speech_text.strip():
        audio_file = text_to_speech(speech_text, language)

    return {
        "filename": file.filename,
        "selected_language": language,
        "analysis": analysis,
        "translated_analysis": translated_analysis,
        "speech_section": speech_section,
        "speech_text": speech_text,
        "audio_file": audio_file
    }