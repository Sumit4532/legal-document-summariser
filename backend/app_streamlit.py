import streamlit as st
import pdfplumber
import re
from collections import Counter

def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def summarise(text):
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 30]
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    freq = Counter(words)
    scores = {}
    for i, sent in enumerate(sentences[:50]):
        score = sum(freq.get(w, 0) for w in re.findall(r'\b[a-zA-Z]{4,}\b', sent.lower()))
        scores[i] = score
    top = sorted(sorted(scores, key=scores.get, reverse=True)[:5])
    return '. '.join([sentences[i] for i in top]) + '.'

def get_entities(text):
    ents = {"dates": [], "organizations": [], "money": []}
    ents["dates"] = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
    ents["money"] = re.findall(r'(?:INR|Rs\.?|USD|\$)\s?[\d,]+(?:\.\d+)?(?:\s?(?:Lakhs?|Crores?|million|billion))?', text)
    ents["organizations"] = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*(?:\s+(?:Ltd|Pvt|Inc|Corp|LLC|LLP|Solutions|Technologies|Services|Group))\b', text)
    return {k: list(set(v))[:5] for k, v in ents.items()}

def get_clauses(text):
    keywords = {
        "termination clause": ["terminat", "end of agreement"],
        "payment clause": ["invoice", "retainer", "EMI", "installment"],
        "penalty clause": ["penalty", "late fee", "late payment", "overdue", "bounce", "withheld"],
        "confidentiality clause": ["confidential", "non-disclosure"],
        "liability clause": ["liability", "liable", "indemnif"],
        "intellectual property clause": ["intellectual property", "copyright"],
        "governing law clause": ["governing law", "jurisdiction"],
    }
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]
    clauses = []
    for sent in sentences:
        for clause_type, kws in keywords.items():
            if any(kw.lower() in sent.lower() for kw in kws):
                clauses.append({"type": clause_type, "text": sent[:200]})
                break
    return clauses

def get_risk(clauses):
    risky = ["termination clause", "penalty clause", "liability clause"]
    count = sum(1 for c in clauses if c["type"] in risky)
    score = min(count * 20, 100)
    level = "High" if score > 60 else "Medium" if score > 30 else "Low"
    return {"score": score, "level": level}

st.set_page_config(page_title="LegalAI", page_icon="⚖️", layout="wide")
st.title("⚖️ LegalAI — Legal Document Summariser")
st.markdown("Upload any legal document — AI will summarise, classify clauses & score risk")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.success(f"✅ Selected: {uploaded_file.name}")
    if st.button("🔍 Analyse Document", type="primary"):
        with st.spinner("AI processing document..."):
            text = extract_text(uploaded_file)
            summary = summarise(text)
            entities = get_entities(text)
            clauses = get_clauses(text)
            risk = get_risk(clauses)
            key_points = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 40][:5]

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Risk Level", risk["level"])
        with col2: st.metric("Risk Score", f"{risk['score']:.1f}%")
        with col3: st.metric("Clauses Found", len(clauses))

        st.divider()
        st.subheader("📝 AI Summary")
        st.write(summary)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔑 Key Points")
            for pt in key_points:
                st.markdown(f"• {pt}")
        with col2:
            st.subheader("👥 Entities Found")
            icons = {"dates": "📅", "organizations": "🏢", "money": "💰"}
            for key, val in entities.items():
                if val:
                    st.markdown(f"**{icons.get(key,'📌')} {key}:** {', '.join(val)}")

        st.divider()
        st.subheader("🔍 Detected Clauses")
        for clause in clauses:
            color = "🔴" if "termination" in clause["type"] or "penalty" in clause["type"] else "🟡" if "liability" in clause["type"] else "🟢"
            st.markdown(f"{color} **{clause['type']}** — {clause['text']}")