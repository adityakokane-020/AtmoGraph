import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

nodes_file = DATA_DIR / "supply_chain_nodes.csv"
edges_file = DATA_DIR / "supply_chain_edges.csv"

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)

print("===== AtmoGraph Graph Validation =====")

print("\nTotal Nodes:", len(nodes))
print("Total Edges:", len(edges))

print("\nNode Types:")
print(nodes["type"].value_counts())

print("\nRelationships:")
print(edges["relationship"].value_counts())

# Check duplicate node IDs
duplicate_nodes = nodes[nodes["id"].duplicated()]

print("\nDuplicate Node IDs:", len(duplicate_nodes))

# Check invalid source/target IDs
node_ids = set(nodes["id"])

invalid_source = edges[~edges["source"].isin(node_ids)]
invalid_target = edges[~edges["target"].isin(node_ids)]

print("Invalid Source IDs:", len(invalid_source))
print("Invalid Target IDs:", len(invalid_target))

# Check missing values
print("\nMissing Values:")
print(nodes.isnull().sum())

print("\n===== Validation Complete =====")