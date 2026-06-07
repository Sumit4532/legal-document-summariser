import pdfplumber
import re

def extract_text_from_pdf(file_path: str) -> str:
    """PDF file se saara text extract karta hai"""
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text.strip()

def clean_text(text: str) -> str:
    """Text ko clean karta hai — extra spaces, newlines hataata hai"""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 512) -> list:
    """
    Text ko chhote chhote chunks mein tod deta hai
    BERT aur T5 ke liye — kyunki unki max token limit hoti hai
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks