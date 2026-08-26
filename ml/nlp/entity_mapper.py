import pandas as pd
import spacy
from pathlib import Path
import re

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

NODES_FILE = DATA_DIR / "supply_chain_nodes.csv"


# --------------------------------------------------
# Load NLP model
# --------------------------------------------------

nlp = spacy.load("en_core_web_sm")


# --------------------------------------------------
# Load supply-chain nodes
# --------------------------------------------------

nodes = pd.read_csv(NODES_FILE)


# --------------------------------------------------
# Text normalization
# --------------------------------------------------

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# --------------------------------------------------
# Entity → Graph Node Mapping
# --------------------------------------------------

def map_entity_to_node(entity_text):

    entity = normalize_text(entity_text)

    # Exact name match
    for _, node in nodes.iterrows():

        node_name = normalize_text(node["name"])

        if entity == node_name:
            return node.to_dict()

    # Partial match
    for _, node in nodes.iterrows():

        node_name = normalize_text(node["name"])

        if entity in node_name or node_name in entity:
            return node.to_dict()

    return None


# --------------------------------------------------
# Extract and map entities
# --------------------------------------------------

def extract_and_map(text):

    doc = nlp(text)

    results = []

    for ent in doc.ents:

        if ent.label_ in [
            "ORG",
            "GPE",
            "LOC",
            "FAC",
            "PRODUCT"
        ]:

            node = map_entity_to_node(ent.text)

            results.append({
                "entity": ent.text,
                "entity_type": ent.label_,
                "node_id": node["id"] if node else None,
                "node_name": node["name"] if node else None,
                "node_type": node["type"] if node else None,
                "country": node["country"] if node else None
            })

    return results


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    news = (
        "Workers announced a strike at Rotterdam Port. "
        "The disruption may affect electronics shipments "
        "from Germany to North America."
    )

    print("===== AtmoGraph Entity Mapping =====")

    print("\nNews:")
    print(news)

    results = extract_and_map(news)

    print("\nEntity Mapping:")

    for result in results:

        print(
            f"Entity: {result['entity']} "
            f"| Type: {result['entity_type']} "
            f"| Node ID: {result['node_id']} "
            f"| Node: {result['node_name']}"
        )

    print("\n===== Mapping Complete =====")