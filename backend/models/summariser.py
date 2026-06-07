import re
from collections import Counter

def summarise_text(text: str) -> str:
    try:
        # Sentences nikalo
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 30]
        
        if not sentences:
            return "Text se summary nahi ban saki."
        
        # Word frequency se important sentences chuno
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_freq = Counter(words)
        
        # Har sentence ko score karo
        scores = {}
        for i, sent in enumerate(sentences[:50]):
            score = 0
            for word in re.findall(r'\b[a-zA-Z]{4,}\b', sent.lower()):
                score += word_freq.get(word, 0)
            scores[i] = score
        
        # Top 5 sentences chuno
        top_indices = sorted(scores, key=scores.get, reverse=True)[:5]
        top_indices = sorted(top_indices)  # Original order mein raho
        
        summary = '. '.join([sentences[i] for i in top_indices])
        return summary + '.'
    
    except Exception as e:
        return f"Summary error: {str(e)}"

def extract_key_points(text: str) -> list:
    try:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 40]
        return sentences[:5]
    except:
        return ["Key points extract nahi ho sake."]