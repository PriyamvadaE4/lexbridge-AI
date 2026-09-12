import json
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_CANDIDATES = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]


def safe_truncate(text: str, max_chars: int = 20000) -> str:
    return text[:max_chars]


def summarize_document(document_text: str) -> dict:
    document_text = safe_truncate(document_text)

    prompt = f"""
You are an expert assistant helping farmers understand documents.

Return ONLY valid JSON.
Do not return markdown.
Do not wrap the output in ```json.
Do not add explanation before or after the JSON.

Use simple language suitable for farmers.

If the document is not related to farming, still analyze it correctly and fill the same JSON structure based on the document content.

JSON format:
{{
  "document_type": "",
  "simple_summary": [],
  "important_clauses": [],
  "risks": [],
  "financial_details": [],
  "important_dates": [],
  "farmer_responsibilities": [],
  "farmer_rights": [],
  "final_recommendation": {{
    "overall_risk": "",
    "advice": ""
  }}
}}

Document:
{document_text}
"""

    last_error = None

    for model in MODEL_CANDIDATES:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document analysis assistant. Always return strict JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )

            text = response.choices[0].message.content

            if text is None or not text.strip():
                raise ValueError("Empty Groq response")

            text = text.strip()

            # remove markdown fences if model still returns them
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            return json.loads(text)

        except Exception as e:
            last_error = e
            continue

    print(f"Groq Error: {last_error}")

    return {
        "document_type": "Unknown",
        "simple_summary": ["Groq service unavailable"],
        "important_clauses": [],
        "risks": [],
        "financial_details": [],
        "important_dates": [],
        "farmer_responsibilities": [],
        "farmer_rights": [],
        "final_recommendation": {
            "overall_risk": "Unknown",
            "advice": f"Groq failed: {str(last_error)}"
        }
    }