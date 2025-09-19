import streamlit as st
import pandas as pd
import pdfplumber
import json
import requests

# --- Streamlit Config ---
st.set_page_config(page_title="Financial Q&A Chat", page_icon="💬", layout="wide")
st.title("💬 Financial Document Q&A Chat")
st.caption("Upload financial documents and chat with LLaMA 2 locally via Ollama.")

# --- Default Config ---
default_config = {
    "ollama": {
        "host": "http://localhost:11434",
        "model": "llama2",  # ✅ Use the exact model name from `ollama list`
        "options": {"temperature": 0.2}
    },
    "retrieval": {
        "chunk_size": 1200,
        "chunk_overlap": 150,
        "top_k": 6
    }
}

# --- Config Editor ---
with st.expander("⚙️ Configuration", expanded=False):
    cfg_text = json.dumps(default_config, indent=2)
    cfg_text = st.text_area("config.json", value=cfg_text, height=220)
    try:
        cfg = json.loads(cfg_text)
    except Exception as e:
        st.error(f"Invalid JSON: {e}")
        cfg = default_config

# --- Session State ---
if "kb_chunks" not in st.session_state:
    st.session_state.kb_chunks = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- File Upload ---
uploaded_files = st.file_uploader("Upload PDF or Excel files", type=["pdf", "xlsx"], accept_multiple_files=True)

# --- File Parsing ---
def parse_pdf(file_obj):
    with pdfplumber.open(file_obj) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def parse_excel(file_obj):
    df = pd.read_excel(file_obj)
    return df.to_string(index=False)

def build_kb(pdf_texts, xls_texts, chunk_size=1200, overlap=150):
    all_text = "\n\n".join(pdf_texts + xls_texts)
    chunks = [all_text[i:i+chunk_size] for i in range(0, len(all_text), chunk_size - overlap)]
    return chunks

# --- Process Files ---
if st.button("📥 Process Uploaded Files"):
    if not uploaded_files:
        st.warning("Please upload at least one document.")
    else:
        pdf_texts, xls_texts = [], []
        with st.status("Processing documents...", expanded=True) as status:
            for f in uploaded_files:
                try:
                    if f.type == "application/pdf":
                        st.write(f"Parsing PDF: **{f.name}**")
                        pdf_texts.append(parse_pdf(f))
                    else:
                        st.write(f"Parsing Excel: **{f.name}**")
                        xls_texts.append(parse_excel(f))
                except Exception as e:
                    st.error(f"Error processing {f.name}: {e}")
            st.session_state.kb_chunks = build_kb(pdf_texts, xls_texts, cfg["retrieval"]["chunk_size"], cfg["retrieval"]["chunk_overlap"])
            status.update(label="Processing completed ✅", state="complete")

# --- Chat Interface ---
st.divider()
if st.session_state.kb_chunks:
    st.subheader("💬 Ask a Question")
    question = st.text_input("Your question:", placeholder="e.g., What was the net income in 2024?")
    if st.button("🤖 Get Answer", disabled=not question):
        with st.spinner("Thinking..."):
            context = "\n\n".join(st.session_state.kb_chunks[:cfg["retrieval"]["top_k"]])
            prompt = f"Context:\n{context}\n\nQuestion: {question}"
            try:
                response = requests.post(
                    f"{cfg['ollama']['host']}/api/generate",
                    json={
                        "model": cfg["ollama"]["model"],
                        "prompt": prompt,
                        "options": cfg["ollama"]["options"],
                        "stream": False
                    },
                    timeout=30  # ⏱️ Prevent hanging
                )
                response.raise_for_status()
                data = response.json()
                answer = data.get("response", "No response received.")
                st.session_state.chat_history.append((question, answer))
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. Is Ollama running?")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API request failed: {e}")

# --- Display Chat History ---
if st.session_state.chat_history:
    st.subheader("📜 Chat History")
    for i, (q, a) in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**Q{i}:** {q}")
        st.markdown(f"**A{i}:** {a}")
        st.markdown("---")


