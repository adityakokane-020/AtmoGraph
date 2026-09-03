import pandas as pd
import spacy
import re
from pathlib import Path


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
# Load graph nodes
# --------------------------------------------------

nodes = pd.read_csv(NODES_FILE)


# --------------------------------------------------
# Normalize text
# --------------------------------------------------

def normalize_text(text):

    text = str(text).lower()

    text = re.sub(r"[^a-z0-9\s]", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


# --------------------------------------------------
# Map entity to graph node
# --------------------------------------------------

def map_entity_to_node(entity_text):

    entity = normalize_text(entity_text)

    # Exact match
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
# Find graph nodes directly inside news text
# --------------------------------------------------

def find_nodes_in_text(text):

    normalized_news = normalize_text(text)

    results = []

    for _, node in nodes.iterrows():

        node_name = normalize_text(node["name"])

        if node_name in normalized_news:

            results.append({
                "entity": node["name"],
                "entity_type": node["type"],
                "node_id": node["id"],
                "node_name": node["name"],
                "node_type": node["type"],
                "country": node["country"]
            })

    return results


# --------------------------------------------------
# Extract + map entities
# --------------------------------------------------

def extract_and_map(text):

    doc = nlp(text)

    results = []

    # First: spaCy entities
    for ent in doc.ents:

        if ent.label_ in [
            "ORG",
            "GPE",
            "LOC",
            "FAC",
            "PRODUCT"
        ]:

            node = map_entity_to_node(ent.text)

            if node:

                results.append({
                    "entity": ent.text,
                    "entity_type": ent.label_,
                    "node_id": node["id"],
                    "node_name": node["name"],
                    "node_type": node["type"],
                    "country": node["country"]
                })

    # Second: direct graph-node matching
    direct_nodes = find_nodes_in_text(text)

    for node in direct_nodes:

        already_exists = any(
            result["node_id"] == node["node_id"]
            for result in results
        )

        if not already_exists:

            results.append(node)

    return results


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    news = (
        "Hamburg Port has been closed due to a severe "
        "operational disruption."
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