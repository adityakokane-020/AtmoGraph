import sys
from pathlib import Path


# ==================================================
# Project Path Setup
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE_DIR))


# ==================================================
# Imports
# ==================================================

from entity_mapper import extract_and_map
from ml.nlp.severity_detection import detect_severity
from ml.nlp.neo4j_risk_update import update_node_risk


# ==================================================
# NLP Pipeline
# ==================================================

def run_pipeline(news):

    print("\n======================================")
    print("        AtmoGraph NLP Pipeline")
    print("======================================")

    # ------------------------------------------------
    # STEP 1: News Input
    # ------------------------------------------------

    print("\n[1] News Input:")
    print(news)

    # ------------------------------------------------
    # STEP 2: Entity Mapping
    # ------------------------------------------------

    print("\n[2] Entity Mapping:")

    mapped_nodes = extract_and_map(news)

    # ------------------------------------------------
    # No Entity Found
    # ------------------------------------------------

    if not mapped_nodes:

        print("No supply chain entity found.")

        return False

    # ------------------------------------------------
    # Display Mapped Nodes
    # ------------------------------------------------

    for node in mapped_nodes:

        print(
            f"Entity: {node['entity']} | "
            f"Node ID: {node['node_id']} | "
            f"Node: {node['node_name']}"
        )

    # ------------------------------------------------
    # STEP 3: Severity Detection
    # ------------------------------------------------

    severity = detect_severity(news)

    print("\n[3] Severity Detection:")
    print("Severity:", severity)

    # ------------------------------------------------
    # STEP 4: Neo4j Risk Update
    # ------------------------------------------------

    print("\n[4] Neo4j Risk Update:")

    for node in mapped_nodes:

        update_node_risk(
            node["node_id"],
            severity
        )

    # ------------------------------------------------
    # Pipeline Success
    # ------------------------------------------------

    print("\n======================================")
    print("       Pipeline Completed")
    print("======================================")

    return True


# ==================================================
# Direct Execution
# ==================================================

if __name__ == "__main__":

    news = (
        "Rotterdam Port has been closed due to a severe "
        "operational disruption."
    )

    run_pipeline(news)
