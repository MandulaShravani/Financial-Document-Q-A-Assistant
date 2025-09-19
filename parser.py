
from __future__ import annotations
import io
import pdfplumber
import pandas as pd
from typing import Dict, Any, List
from utils import clean_text

def parse_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """Extracts text (and basic tables) from a PDF."""
    text_parts: List[str] = []
    tables: List[pd.DataFrame] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            try:
                txt = page.extract_text() or ""
                if txt:
                    text_parts.append(txt)
                page_tables = page.extract_tables()
                for t in page_tables or []:
                    try:
                        df = pd.DataFrame(t)
                        df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
                        if not df.empty:
                            tables.append(df)
                    except Exception:
                        pass
            except Exception:
                continue
    full_text = clean_text("\n\n".join(text_parts))
    return {"text": full_text, "tables": tables}

def parse_excel(file_bytes: bytes) -> Dict[str, Any]:
    """Reads all sheets from an Excel file into text and DataFrames."""
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    text_parts: List[str] = []
    tables: List[pd.DataFrame] = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet_name=sheet)
        tables.append(df)
        head_txt = df.head(20).to_string(index=False)
        text_parts.append(f"Sheet: {sheet}\n{head_txt}")
    full_text = clean_text("\n\n".join(text_parts))
    return {"text": full_text, "tables": tables}
