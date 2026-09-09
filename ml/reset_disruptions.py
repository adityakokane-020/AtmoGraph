from neo4j import GraphDatabase
import os


# ==================================================
# Neo4j Configuration
# ==================================================

URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "atmograph")


# ==================================================
# Reset Previous Disruptions
# ==================================================

def reset_disruptions():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    query = """
    MATCH (n)
    WHERE n.disruption = 1

    SET n.disruption = 0,
        n.risk = "Low",
        n.predicted_delay = 0.0,
        n.predicted_risk = "Low"

    RETURN
        n.id AS id,
        n.name AS name
    """

    try:

        with driver.session(database=DATABASE) as session:

            result = session.run(query)

            nodes = list(result)

            print("\n===== Resetting Previous Disruptions =====")

            if not nodes:

                print("No active disruptions found.")

            else:

                for node in nodes:

                    print(
                        f"Reset: {node['id']} | "
                        f"{node['name']}"
                    )

                print(
                    "\nAll previous disruptions and "
                    "predictions reset successfully."
                )

    finally:

        driver.close()


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    reset_disruptions()
