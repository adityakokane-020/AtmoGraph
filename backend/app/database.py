from neo4j import GraphDatabase


# Neo4j connection details
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"

# IMPORTANT:
# Replace ONLY this value with the password you created
# when you created the AtmoGraph database.
NEO4J_PASSWORD = "Baji@151098"


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def verify_connection():
    try:
        driver.verify_connectivity()
        print("Neo4j connection successful!")
        return True
    except Exception as e:
        print(f"Neo4j connection failed: {e}")
        return False