from entity_mapping import extract_and_map
from severity_detection import detect_severity
from neo4j_risk_update import update_node_risk


def run_pipeline(news):

    print("\n======================================")
    print("        AtmoGraph NLP Pipeline")
    print("======================================")

    # Step 1: News Input
    print("\n[1] News Input:")
    print(news)

    # Step 2: Entity Mapping
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

    # Step 3: Severity Detection
    severity = detect_severity(news)

    print("\n[3] Severity Detection:")
    print("Severity:", severity)

    # Step 4: Update Neo4j
    print("\n[4] Neo4j Risk Update:")

    for node in mapped_nodes:
        update_node_risk(
            node["node_id"],
            severity
        )

    print("\n======================================")
    print("       Pipeline Completed")
    print("======================================")


if __name__ == "__main__":

    news = (
        "Rotterdam Port has been closed due to a severe "
        "operational disruption."
    )

    run_pipeline(news)