import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE_DIR))

from entity_mapper import extract_and_map
from ml.nlp.severity_detection import detect_severity
from ml.nlp.disruption_type_detection import detect_disruption_type
from ml.nlp.neo4j_risk_update import update_node_risk


def run_pipeline(news):

    print("\n======================================")
    print("        AtmoGraph NLP Pipeline")
    print("======================================")

    # ======================================================
    # STEP 1 - NEWS INPUT
    # ======================================================

    print("\n[1] News Input:")
    print(news)

    # ======================================================
    # STEP 2 - ENTITY MAPPING
    # ======================================================

    print("\n[2] Entity Mapping:")

    mapped_nodes = extract_and_map(news)

    if not mapped_nodes:

        print("No supply chain entity found.")

        return {
            "success": False,
            "severity": None,
            "disruption_type": None,
            "nodes": []
        }

    for node in mapped_nodes:

        print(
            f"Entity: {node['entity']} | "
            f"Node ID: {node['node_id']} | "
            f"Node: {node['node_name']}"
        )

    # ======================================================
    # STEP 3 - SEVERITY DETECTION
    # ======================================================

    severity = detect_severity(news)

    print("\n[3] Severity Detection:")
    print("Severity:", severity)

    # ======================================================
    # STEP 4 - DISRUPTION TYPE DETECTION
    # ======================================================

    disruption_type = detect_disruption_type(news)

    print("\n[4] Disruption Type Detection:")
    print("Disruption Type:", disruption_type)

    # ======================================================
    # STEP 5 - NEO4J RISK UPDATE
    # ======================================================

    print("\n[5] Neo4j Risk Update:")

    for node in mapped_nodes:

        update_node_risk(
            node["node_id"],
            severity,
            disruption_type
        )

    print("\n======================================")
    print("       NLP Pipeline Completed")
    print("======================================")

    # ======================================================
    # RETURN RESULT TO GCN
    # ======================================================

    return {
        "success": True,
        "severity": severity,
        "disruption_type": disruption_type,
        "nodes": mapped_nodes
    }


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    news = (
        "Rotterdam Port has been closed due to a severe "
        "operational disruption."
    )

    result = run_pipeline(news)

    print("\n===== NLP RESULT =====")

    print("Success:", result["success"])
    print("Severity:", result["severity"])
    print("Disruption Type:", result["disruption_type"])
    print("Nodes:", result["nodes"])