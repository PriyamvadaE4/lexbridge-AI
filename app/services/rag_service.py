from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
from dotenv import load_dotenv
import os
from deep_translator import GoogleTranslator

load_dotenv()


LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Marathi": "mr"
}
model = SentenceTransformer("all-MiniLM-L6-v2")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chunks: list[str] = []
index = None
current_language = "English"


def set_language(language: str):
    global current_language
    current_language = language


def get_language() -> str:
    return current_language


def translate_to_english(text: str, source_language: str) -> str:
    if source_language == "English":
        return text

    source_code = LANGUAGE_CODES.get(source_language, "auto")

    try:
        return GoogleTranslator(source=source_code, target="en").translate(text)
    except Exception:
        return text


def translate_from_english(text: str, target_language: str) -> str:
    if target_language == "English":
        return text

    target_code = LANGUAGE_CODES.get(target_language, "en")

    try:
        return GoogleTranslator(source="en", target=target_code).translate(text)
    except Exception:
        return text
    
def store_document(text: str):
    global chunks, index

    if not text or not text.strip():
        chunks = []
        index = None
        return

    chunk_size = 500

    chunks = [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]

    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)


def retrieve(question: str) -> str:
    global index, chunks

    if index is None or not chunks:
        return "No document uploaded."

    question_embedding = model.encode([question])
    question_embedding = np.array(question_embedding).astype("float32")

    k = min(3, len(chunks))
    distances, indices = index.search(question_embedding, k)

    context_parts = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            context_parts.append(chunks[idx])

    return "\n".join(context_parts)


def answer_question(question: str) -> str:
    language = get_language()

    # convert question to English before retrieval
    english_question = translate_to_english(question, language)

    context = retrieve(english_question)

    if context == "No document uploaded.":
        return translate_from_english("No document uploaded.", language)

    prompt = f"""
Answer ONLY using the provided context.

If the answer is not present in the context, say exactly:
Information not found in the uploaded document.

Context:
{context}

Question:
{english_question}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    answer_en = response.choices[0].message.content.strip()

    # translate final answer back to selected language
    final_answer = translate_from_english(answer_en, language)

    return final_answer