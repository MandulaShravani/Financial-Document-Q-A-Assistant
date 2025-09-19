
# Financial Document Q&A Assistant (Local, Streamlit + Ollama)

A minimal reference implementation for the assignment: upload PDF/Excel financial docs, extract text/tables, and ask questions in natural language.  
Runs **locally** with **Streamlit** and **Ollama** (Small Language Models on-device).

## Features
- Upload **PDF** and **Excel** files (e.g., income statement, balance sheet, cash flow).
- Extract **text** (PDF) and **tables** (PDF/Excel).
- Build a lightweight knowledge base and retrieve relevant chunks using **TF‑IDF**.
- Ask natural‑language questions; responses are generated via an **Ollama** model using the retrieved context.
- Clean, simple Streamlit UI with progress/status messages and error handling.

## Quick Start

### 1) Prerequisites
- Python 3.10+ (recommended)
- [Ollama](https://ollama.com) installed and running locally (defaults to `http://localhost:11434`)

Pull at least one small model, for example:
```bash
ollama pull llama3.1:8b
# or
ollama pull mistral
```
> You can change the model name in `config.json` (default: `llama3.1:8b`).

### 2) Create and activate a virtual environment (optional but recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3) Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4) Run the app
```bash
streamlit run app.py
```
Then open the URL that Streamlit prints (usually http://localhost:8501).

## Project Structure
```
.
├─ app.py               # Streamlit UI and orchestration
├─ parser.py            # PDF/Excel parsing utilities
├─ qa.py                # Retrieval (TF-IDF) + Ollama LLM call
├─ utils.py             # Helpers (chunking, cleaning, caching)
├─ requirements.txt     # Python dependencies
├─ config.json          # Model and app config
└─ sample_data/
   ├─ sample_income_statement.xlsx
   └─ sample_notes.pdf
```

## Notes & Limitations
- PDF table extraction varies with layout quality; this starter focuses on text extraction via `pdfplumber`. You can add Camelot or Tabula if you have Java/Ghostscript available.
- The retrieval is TF‑IDF‑based for simplicity; feel free to swap in embeddings.
- This is a reference starter—extend error handling, add more robust parsing, and refine prompts as needed.

## Example Questions
- "What was total revenue in 2023?"
- "List operating expenses and summarize the trend."
- "What is the net profit margin for Q1?"
