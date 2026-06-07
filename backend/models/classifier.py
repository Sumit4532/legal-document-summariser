from transformers import pipeline
import re

# BERT-based zero-shot classifier — fine-tuning ke bina bhi kaam karta hai
# Ye pre-trained model HuggingFace se download hoga pehli baar (ek baar hi)
classifier = pipeline(
    "zero-shot-classification",
    model="cross-encoder/nli-MiniLM2-L6-H768"  # Lightweight BERT model
)

# Clause types jo hum detect karna chahte hain
CLAUSE_LABELS = [
    "termination clause",
    "penalty clause",
    "liability clause",
    "payment clause",
    "confidentiality clause",
    "intellectual property clause",
    "governing law clause",
    "indemnification clause",
]

# Risky clause types — inhe red flag karo
RISKY_CLAUSES = {
    "termination clause",
    "penalty clause",
    "liability clause",
    "indemnification clause",
}

def classify_clauses(text: str) -> list:
    """
    Text ko sentences mein tod ke har sentence ko classify karta hai
    Returns: list of {text, type, is_risky, confidence}
    """
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]

    results = []
    for sentence in sentences[:30]:  # Pehle 30 sentences (speed ke liye)
        try:
            output = classifier(sentence, CLAUSE_LABELS)
            top_label = output["labels"][0]
            top_score = output["scores"][0]

            if top_score > 0.4:  # Only confident predictions lo
                results.append({
                    "text": sentence,
                    "type": top_label,
                    "is_risky": top_label in RISKY_CLAUSES,
                    "confidence": round(top_score * 100, 1)
                })
        except Exception:
            continue

    return results

def calculate_risk_score(classified_clauses: list) -> dict:
    """
    Classified clauses se overall risk score calculate karta hai
    Returns: {score: 0-100, level: Low/Medium/High, risky_count, total_count}
    """
    if not classified_clauses:
        return {"score": 0, "level": "Low", "risky_count": 0, "total_count": 0}

    risky = [c for c in classified_clauses if c["is_risky"]]
    total = len(classified_clauses)
    risky_count = len(risky)

    # Risk score = risky clauses ka percentage + confidence weighted
    base_score = (risky_count / total) * 100 if total > 0 else 0
    avg_confidence = sum(c["confidence"] for c in risky) / risky_count if risky_count > 0 else 0
    final_score = round((base_score * 0.6) + (avg_confidence * 0.4))

    if final_score < 30:
        level = "Low"
    elif final_score < 60:
        level = "Medium"
    else:
        level = "High"

    return {
        "score": final_score,
        "level": level,
        "risky_count": risky_count,
        "total_count": total
    }
