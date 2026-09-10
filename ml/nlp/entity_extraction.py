import spacy
from pathlib import Path

# Load English NLP model
nlp = spacy.load("en_core_web_sm")


def extract_entities(text):
    """
    Extract important entities from supply-chain news.
    """

    doc = nlp(text)

    entities = []

    for ent in doc.ents:

        if ent.label_ in [
            "ORG",
            "GPE",
            "LOC",
            "FAC",
            "PRODUCT"
        ]:

            entities.append({
                "text": ent.text,
                "label": ent.label_
            })

    return entities


if __name__ == "__main__":

    news = (
        "Workers announced a strike at Rotterdam Port. "
        "The disruption may affect electronics shipments "
        "from Germany to North America."
    )

    print("===== AtmoGraph NLP Entity Extraction =====")

    entities = extract_entities(news)

    print("\nNews:")
    print(news)

    print("\nExtracted Entities:")

    for entity in entities:
        print(
            f"Entity: {entity['text']} "
            f"| Type: {entity['label']}"
        )

    print("\n===== Extraction Complete =====")