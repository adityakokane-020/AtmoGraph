import os
from neo4j import GraphDatabase


URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "atmograph")

def update_node_risk(
    node_id,
    severity,
    disruption_type=None
):

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    query = """
    MATCH (n {id: $node_id})

    SET
        n.risk = $severity,
        n.disruption = 1,
        n.disruption_type = $disruption_type

    RETURN
        n.id AS id,
        n.name AS name,
        n.risk AS risk,
        n.disruption AS disruption,
        n.disruption_type AS disruption_type
    """

    try:

        with driver.session(
            database=DATABASE
        ) as session:

            result = session.run(
                query,
                node_id=node_id,
                severity=severity,
                disruption_type=disruption_type
            )

            record = result.single()

            if record:

                print("===== Node Found =====")

                print(
                    f"Node ID: {record['id']}"
                )

                print(
                    f"Node Name: {record['name']}"
                )

                print(
                    f"Current/Updated Risk: {record['risk']}"
                )

                print(
                    f"Disruption: {record['disruption']}"
                )

                print(
                    f"Disruption Type: "
                    f"{record['disruption_type']}"
                )

            else:

                print(
                    f"Node not found: {node_id}"
                )

    finally:

        driver.close()


if __name__ == "__main__":

    update_node_risk(
        "P001",
        "HIGH",
        "Port Closure"
    )