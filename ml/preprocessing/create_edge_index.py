import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

nodes_file = DATA_DIR / "supply_chain_nodes.csv"
edges_file = DATA_DIR / "supply_chain_edges.csv"
output_file = DATA_DIR / "edge_index.csv"

# Load data
nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)

# Create node ID → numeric index mapping
node_mapping = {
    node_id: index
    for index, node_id in enumerate(nodes["id"])
}

# Convert source and target IDs into numeric indices
edges["source_index"] = edges["source"].map(node_mapping)
edges["target_index"] = edges["target"].map(node_mapping)

# Keep required columns
edge_index = edges[
    ["source_index", "target_index", "relationship"]
]

# Validation
invalid = edge_index[
    edge_index["source_index"].isna() |
    edge_index["target_index"].isna()
]

print("===== Edge Index Creation =====")
print("Total Edges:", len(edge_index))
print("Invalid Edges:", len(invalid))

edge_index.to_csv(output_file, index=False)

print("\nSaved to:")
print(output_file)

print("\nFirst 5 edges:")
print(edge_index.head())