from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import shutil, os, json, uuid

from parser import extract_text_from_pdf, clean_text
from models.ner import extract_entities
from models.classifier import classify_clauses, calculate_risk_score
from models.summariser import summarise_text, extract_key_points
from database import DocumentResult, create_tables, get_db

app = FastAPI(title="Legal Document Summariser API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
def startup():
    create_tables()
    print("Database ready!")

@app.get("/")
def root():
    return {"message": "Legal Document Summariser API is running!"}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sirf PDF files allowed hain!")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        print("PDF parsing kar raha hoon...")
        raw_text = extract_text_from_pdf(file_path)
        clean = clean_text(raw_text)

        if len(clean) < 50:
            raise HTTPException(status_code=400, detail="PDF mein readable text nahi mila.")

        print("NER run kar raha hoon (spaCy)...")
        entities = extract_entities(clean)

        print("Clauses classify kar raha hoon (BERT)...")
        clauses = classify_clauses(clean)
        risk = calculate_risk_score(clauses)

        print("Summary generate kar raha hoon (DistilBART)...")
        summary = summarise_text(clean)
        key_points = extract_key_points(clean)

        doc = DocumentResult(
            id=file_id,
            filename=file.filename,
            original_text=clean[:10000],
            summary=summary,
            risk_score=risk["score"],
            risk_level=risk["level"],
            entities=json.dumps(entities),
            clauses=json.dumps(clauses),
            key_points=json.dumps(key_points),
        )
        db.add(doc)
        db.commit()

        return JSONResponse({
            "id": file_id,
            "filename": file.filename,
            "summary": summary,
            "key_points": key_points,
            "entities": entities,
            "clauses": clauses,
            "risk": risk,
            "original_text_preview": clean[:2000]
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/result/{doc_id}")
def get_result(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentResult).filter(DocumentResult.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document nahi mila")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "summary": doc.summary,
        "risk_score": doc.risk_score,
        "risk_level": doc.risk_level,
        "entities": json.loads(doc.entities or "{}"),
        "clauses": json.loads(doc.clauses or "[]"),
        "key_points": json.loads(doc.key_points or "[]"),
        "created_at": str(doc.created_at)
    }

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    docs = db.query(DocumentResult).order_by(DocumentResult.created_at.desc()).limit(10).all()
    return [{"id": d.id, "filename": d.filename, "risk_level": d.risk_level, "created_at": str(d.created_at)} for d in docs]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)