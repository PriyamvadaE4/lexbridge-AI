from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import answer_question, get_language
from app.services.speech_service import text_to_speech

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(req: QuestionRequest):
    language = get_language()

    answer = answer_question(req.question)

    audio_file = None
    if answer.strip():
        audio_file = text_to_speech(answer, language)

    return {
        "language": language,
        "answer": answer,
        "audio_file": audio_file
    }