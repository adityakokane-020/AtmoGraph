import sys
from pathlib import Path

# --------------------------------------------------
# Project Root Path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

# Add project root to Python path
sys.path.append(str(BASE_DIR))

# --------------------------------------------------
# Import Project Modules
# --------------------------------------------------

from entity_mapper import extract_and_map
from ml.nlp.severity_detection import detect_severity
from ml.nlp.neo4j_risk_update import update_node_risk


# --------------------------------------------------
# Main NLP Pipeline
# --------------------------------------------------

def run_pipeline(news):

    print("\n======================================")
    print("        AtmoGraph NLP Pipeline")
    print("======================================")

    # --------------------------------------------------
    # Step 1: News Input
    # --------------------------------------------------

    print("\n[1] News Input:")
    print(news)

    # --------------------------------------------------
    # Step 2: Entity Mapping
    # --------------------------------------------------

    print("\n[2] Entity Mapping:")

    mapped_nodes = extract_and_map(news)

    if not mapped_nodes:
        print("No supply chain entity found.")
        return

    for node in mapped_nodes:

        print(
            f"Entity: {node['entity']} | "
            f"Node ID: {node['node_id']} | "
            f"Node: {node['node_name']}"
        )

    # --------------------------------------------------
    # Step 3: Severity Detection
    # --------------------------------------------------

    severity = detect_severity(news)

    print("\n[3] Severity Detection:")
    print("Severity:", severity)

    # --------------------------------------------------
    # Step 4: Update Neo4j
    # --------------------------------------------------

    print("\n[4] Neo4j Risk Update:")

    for node in mapped_nodes:

        update_node_risk(
            node["node_id"],
            severity
        )

    # --------------------------------------------------
    # Pipeline Completed
    # --------------------------------------------------

    print("\n======================================")
    print("       Pipeline Completed")
    print("======================================")


# --------------------------------------------------
# Test News
# --------------------------------------------------

if __name__ == "__main__":

    news = (
        "Rotterdam Port has been closed due to a severe "
        "operational disruption."
    )

    run_pipeline(news)

