### 📄 **LexBridge AI – Legal Document Analyser**

**LexBridge AI** is a document analysis system that helps users understand uploaded PDF documents using **Generative AI**. It extracts the content of a document, generates a simple structured analysis, supports multiple Indian languages, provides text-to-speech output, and allows users to ask questions based on the uploaded document.

#### 🔧 Features

* **PDF Document Upload** – Allows users to upload PDF documents for analysis
* **AI Document Analysis** – Uses Groq LLMs to analyze the uploaded document and generate a structured response
* **Simple Summary** – Provides an easy-to-understand summary of the document
* **Important Clauses & Risks** – Identifies important clauses and potential risks in the document
* **Financial Details & Important Dates** – Extracts relevant financial information and dates
* **Rights & Responsibilities** – Identifies farmer rights and responsibilities when applicable
* **Final Recommendation** – Provides an overall risk level and recommendation based on the document
* **Multilingual Support** – Supports English, Telugu, Hindi, Tamil, Kannada, and Marathi
* **Document-Based Question Answering** – Allows users to ask questions about the uploaded document using **RAG**
* **Text-to-Speech** – Converts the generated analysis and answers into speech in the selected language

#### 🛠️ How It Works

1. **PDF Upload** – User uploads a PDF and selects a language and speech section
2. **Text Extraction** – The system extracts the text from the PDF using PyMuPDF
3. **AI Analysis** – The extracted document text is analyzed by a Groq-hosted LLM
4. **Structured Output** – The AI generates information such as summary, clauses, risks, financial details, dates, rights, responsibilities, and recommendation
5. **Translation** – The generated analysis is translated into the selected language when required
6. **RAG Processing** – The original document is divided into chunks, converted into embeddings, and stored in a FAISS vector index
7. **Question Answering** – User questions are converted to English when required, relevant document chunks are retrieved, and the LLM generates an answer using only the retrieved context
8. **Speech Generation** – The selected analysis section or generated answer is converted into audio using gTTS
9. **Result Display** – Streamlit displays the original analysis, translated analysis, answer, and audio output

#### 💻 Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python, FastAPI
* **LLM:** Groq API with Llama models
* **RAG:** Sentence Transformers + FAISS
* **PDF Processing:** PyMuPDF
* **Translation:** GoogleTranslator through deep-translator
* **Text-to-Speech:** gTTS
* **Libraries:** NumPy, Requests, python-dotenv

🤖 *Built as a Generative AI + RAG application to make complex PDF documents easier to understand through structured analysis, multilingual support, question answering, and voice output.*
