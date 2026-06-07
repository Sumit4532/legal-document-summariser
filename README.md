# legal-document-summariser
AI-powered legal document analysis using ML + NLP + Deep Learning.

## Features
- 📝 Auto summarisation of legal documents
- 🔍 Clause detection (payment, termination, liability etc.)
- ⚠️ Risk scoring (Low/Medium/High)
- 👥 Entity extraction (parties, dates, locations)

## Tech Stack
- **Backend:** FastAPI, Python
- **NLP:** spaCy
- **ML/DL:** HuggingFace Transformers
- **Frontend:** Streamlit
- **Database:** SQLite

## How to Run
```bash
cd backend
python main.py
streamlit run backend/app_streamlit.py
