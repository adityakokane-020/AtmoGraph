import pandas as pd
from neo4j import GraphDatabase
from pathlib import Path


# --------------------------------------------------
# Neo4j Configuration
# --------------------------------------------------

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

NODES_FILE = BASE_DIR / "data" / "supply_chain_nodes.csv"
EDGES_FILE = BASE_DIR / "data" / "supply_chain_edges.csv"


# --------------------------------------------------
# Neo4j Driver
# --------------------------------------------------

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# --------------------------------------------------
# Clear Existing Graph
# --------------------------------------------------

def clear_database():

    with driver.session(database="atmograph") as session:

        session.run(
            "MATCH (n) DETACH DELETE n"
        )

    print("Existing graph cleared.")


# --------------------------------------------------
# Create Nodes
# --------------------------------------------------

def create_nodes(nodes_df):

    with driver.session(database="atmograph") as session:

        for _, row in nodes_df.iterrows():

            query = """
            CREATE (n:SupplyChainNode {
                id: $id,
                name: $name,
                type: $type,
                country: $country,
                risk: $risk,
                capacity: $capacity,
                delay: $delay,
                disruption: $disruption
            })
            """

            session.run(
                query,
                id=str(row["id"]),
                name=str(row["name"]),
                type=str(row["type"]),
                country=str(row["country"]),
                risk=str(row["risk"]),
                capacity=int(row["capacity"]),
                delay=int(row["delay"]),
                disruption=(
                    None
                    if pd.isna(row["disruption"])
                    else str(row["disruption"])
                )
            )

    print(f"{len(nodes_df)} nodes created.")


# --------------------------------------------------
# Create Relationships
# --------------------------------------------------

def create_relationships(edges_df):

    with driver.session(database="atmograph") as session:

        for _, row in edges_df.iterrows():

            relationship = str(row["relationship"])

            query = f"""
            MATCH (source:SupplyChainNode {{id: $source}})
            MATCH (target:SupplyChainNode {{id: $target}})

            CREATE (source)-[r:{relationship}]->(target)
            """

            session.run(
                query,
                source=str(row["source"]),
                target=str(row["target"])
            )

    print(f"{len(edges_df)} relationships created.")


# --------------------------------------------------
# Verify Graph
# --------------------------------------------------

def verify_graph():

    with driver.session(database="atmograph") as session:

        node_result = session.run(
            "MATCH (n) RETURN count(n) AS total_nodes"
        )

        edge_result = session.run(
            "MATCH ()-[r]->() RETURN count(r) AS total_edges"
        )

        total_nodes = node_result.single()["total_nodes"]
        total_edges = edge_result.single()["total_edges"]

        print("\n===== Neo4j Graph Verification =====")
        print("Total Nodes:", total_nodes)
        print("Total Relationships:", total_edges)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\n===== AtmoGraph Neo4j Ingestion =====")

    nodes_df = pd.read_csv(NODES_FILE)
    edges_df = pd.read_csv(EDGES_FILE)

    print("\nLoading Data...")
    print("Nodes:", len(nodes_df))
    print("Edges:", len(edges_df))

    clear_database()

    create_nodes(nodes_df)

    create_relationships(edges_df)

    verify_graph()

    print("\n===== Ingestion Complete =====")

    driver.close()


if __name__ == "__main__":
    main()