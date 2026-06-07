import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> dict:
    doc = nlp(text[:5000])

    entities = {
        "parties": [],
        "dates": [],
        "locations": [],
        "organizations": [],
        "money": [],
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["parties"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ in ["GPE", "LOC"]:
            entities["locations"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["organizations"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)

    for key in entities:
        entities[key] = list(set(entities[key]))

    return entities