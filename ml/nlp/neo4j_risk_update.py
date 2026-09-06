from neo4j import GraphDatabase


# --------------------------------------------------
# Neo4j Configuration
# --------------------------------------------------

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"
DATABASE = "atmograph"


# --------------------------------------------------
# Update Risk + Disruption
# --------------------------------------------------

def update_node_risk(node_id, severity):

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        with driver.session(database=DATABASE) as session:

            # ------------------------------------------
            # Check Node
            # ------------------------------------------

            result = session.run(
                """
                MATCH (n {id: $node_id})
                RETURN
                    n.id AS ID,
                    n.name AS Name,
                    n.risk AS Risk
                """,
                node_id=node_id
            )

            record = result.single()

            if record:

                print("===== Node Found =====")
                print("Node ID:", record["ID"])
                print("Node Name:", record["Name"])
                print("Current Risk:", record["Risk"])

                # --------------------------------------
                # Update Risk + Disruption
                # --------------------------------------

                update_result = session.run(
                    """
                    MATCH (n {id: $node_id})
                    SET
                        n.risk = $severity,
                        n.disruption = 1
                    RETURN
                        n.id AS ID,
                        n.name AS Name,
                        n.risk AS Risk,
                        n.disruption AS Disruption
                    """,
                    node_id=node_id,
                    severity=severity
                )

                updated = update_result.single()

                print("\n===== Neo4j Risk Update =====")
                print("Node ID:", updated["ID"])
                print("Node Name:", updated["Name"])
                print("Updated Risk:", updated["Risk"])
                print("Disruption:", updated["Disruption"])

            else:

                print("Node not found:", node_id)

                # --------------------------------------
                # Show Available Node IDs
                # --------------------------------------

                check = session.run(
                    """
                    MATCH (n)
                    RETURN n.id AS ID
                    LIMIT 10
                    """
                )

                print("\nAvailable Node IDs:")

                for row in check:
                    print(row["ID"])

    finally:

        driver.close()


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    node_id = "P001"
    severity = "HIGH"

    update_node_risk(
        node_id,
        severity
    )
