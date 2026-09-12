import streamlit as st
import requests
import json
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
FASTAPI_BASE_URL = "http://127.0.0.1:8000"

UPLOAD_URL = f"{FASTAPI_BASE_URL}/upload"
ASK_URL = f"{FASTAPI_BASE_URL}/ask"

LANGUAGES = [
    "English",
    "Telugu",
    "Hindi",
    "Tamil",
    "Kannada",
    "Marathi"
]

SPEECH_SECTIONS = [
    "simple_summary",
    "important_clauses",
    "risks",
    "financial_details",
    "important_dates",
    "farmer_responsibilities",
    "farmer_rights",
    "final_recommendation"
]


# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(
    page_title="LexBridge AI",
    page_icon="📄",
    layout="wide"
)

st.title("📄 LexBridge AI")
st.write("Upload a PDF, analyze it, translate the summary, generate speech, and ask questions about the uploaded document.")


# -----------------------------
# HELPERS
# -----------------------------
def format_analysis_section(title: str, value):
    st.subheader(title)

    if value is None:
        st.write("No data")
        return

    if isinstance(value, str):
        st.write(value)
        return

    if isinstance(value, list):
        if not value:
            st.write("No data")
            return

        for item in value:
            if isinstance(item, dict):
                st.json(item)
            else:
                st.markdown(f"- {item}")
        return

    if isinstance(value, dict):
        st.json(value)
        return

    st.write(value)


def render_analysis(analysis: dict, heading: str):
    st.header(heading)

    if not analysis:
        st.warning("No analysis available.")
        return

    col1, col2 = st.columns(2)

    with col1:
        format_analysis_section("Document Type", analysis.get("document_type"))
        format_analysis_section("Simple Summary", analysis.get("simple_summary"))
        format_analysis_section("Important Clauses", analysis.get("important_clauses"))
        format_analysis_section("Risks", analysis.get("risks"))

    with col2:
        format_analysis_section("Financial Details", analysis.get("financial_details"))
        format_analysis_section("Important Dates", analysis.get("important_dates"))
        format_analysis_section("Farmer Responsibilities", analysis.get("farmer_responsibilities"))
        format_analysis_section("Farmer Rights", analysis.get("farmer_rights"))
        format_analysis_section("Final Recommendation", analysis.get("final_recommendation"))


def get_audio_bytes(audio_path: str):
    """
    audio_path returned by FastAPI is usually something like:
    audio/xxxx.mp3

    Since Streamlit runs in same project folder, we can read it directly.
    """
    if not audio_path:
        return None

    path = Path(audio_path)
    if not path.exists():
        return None

    return path.read_bytes()


# -----------------------------
# SESSION STATE
# -----------------------------
if "uploaded_result" not in st.session_state:
    st.session_state.uploaded_result = None

if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"


# -----------------------------
# SIDEBAR - UPLOAD
# -----------------------------
st.sidebar.header("Upload Settings")

uploaded_file = st.sidebar.file_uploader(
    "Choose PDF file",
    type=["pdf"]
)

selected_language = st.sidebar.selectbox(
    "Select Language",
    LANGUAGES,
    index=0
)

speech_section = st.sidebar.selectbox(
    "Select section for upload speech",
    SPEECH_SECTIONS,
    index=0
)

analyze_button = st.sidebar.button("Analyze PDF")


# -----------------------------
# UPLOAD FLOW
# -----------------------------
if analyze_button:
    if uploaded_file is None:
        st.warning("Please upload a PDF first.")
    else:
        with st.spinner("Uploading PDF, analyzing document, translating, and generating speech..."):
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
            }

            data = {
                "language": selected_language,
                "speech_section": speech_section
            }

            try:
                response = requests.post(UPLOAD_URL, files=files, data=data)

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.uploaded_result = result
                    st.session_state.selected_language = selected_language
                    st.success("PDF uploaded and analyzed successfully.")
                else:
                    st.error(f"Upload failed: {response.status_code}")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.text(response.text)

            except Exception as e:
                st.error(f"Could not connect to FastAPI backend: {e}")


# -----------------------------
# DISPLAY UPLOAD RESULT
# -----------------------------
result = st.session_state.uploaded_result

if result:
    st.success(f"Current uploaded file: {result.get('filename', 'Unknown file')}")
    st.info(f"Selected language: {result.get('selected_language', 'Unknown')}")

    # Upload speech preview
    st.header("🔊 Upload Speech Output")
    st.write(f"**Speech section:** {result.get('speech_section', '')}")

    speech_text = result.get("speech_text", "")
    if speech_text:
        st.text_area("Speech Text", speech_text, height=160)

    audio_file = result.get("audio_file")
    if audio_file:
        audio_bytes = get_audio_bytes(audio_file)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.warning(f"Audio file not found at path: {audio_file}")

    # Tabs for original and translated analysis
    tab1, tab2, tab3 = st.tabs(["Original Analysis", "Translated Analysis", "Raw JSON"])

    with tab1:
        render_analysis(result.get("analysis", {}), "Original Analysis")

    with tab2:
        render_analysis(result.get("translated_analysis", {}), "Translated Analysis")

    with tab3:
        st.subheader("Full Upload Response")
        st.json(result)


# -----------------------------
# ASK SECTION
# -----------------------------
st.divider()
st.header("💬 Ask Questions About Uploaded Document")

question = st.text_input("Enter your question")

ask_button = st.button("Ask")

if ask_button:
    if not result:
        st.warning("Please upload a document first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Getting answer from uploaded document..."):
            try:
                response = requests.post(
                    ASK_URL,
                    json={"question": question}
                )

                if response.status_code == 200:
                    answer_result = response.json()

                    st.subheader("Answer")
                    st.write(answer_result.get("answer", ""))

                    st.caption(f"Language: {answer_result.get('language', st.session_state.selected_language)}")

                    answer_audio = answer_result.get("audio_file")
                    if answer_audio:
                        audio_bytes = get_audio_bytes(answer_audio)
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                        else:
                            st.warning(f"Answer audio file not found at path: {answer_audio}")

                    with st.expander("Raw /ask response"):
                        st.json(answer_result)

                else:
                    st.error(f"/ask failed: {response.status_code}")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.text(response.text)

            except Exception as e:
                st.error(f"Could not connect to FastAPI backend: {e}")


# -----------------------------
# FOOTER INFO
# -----------------------------
st.divider()
st.markdown("""
### How this frontend works

#### Upload flow
1. You upload a PDF  
2. Streamlit sends it to **FastAPI `/upload`**
3. FastAPI:
   - extracts text
   - stores original text in RAG
   - summarizes using Groq
   - translates the structured analysis
   - generates gTTS speech for the selected section
4. Streamlit shows:
   - original analysis
   - translated analysis
   - audio for the selected section

#### Ask flow
1. You type a question
2. Streamlit sends it to **FastAPI `/ask`**
3. FastAPI:
   - retrieves relevant original chunks from FAISS
   - answers in the selected language
   - generates gTTS audio
4. Streamlit shows answer + audio
""")