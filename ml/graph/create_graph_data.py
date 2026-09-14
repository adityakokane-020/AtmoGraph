import pandas as pd
import torch
from pathlib import Path
from torch_geometric.data import Data


# ==============================
# Paths
# ==============================

BASE_DIR = Path(__file__).resolve().parents[1]

NODES_FILE = BASE_DIR / "data" / "supply_chain_nodes.csv"
EDGES_FILE = BASE_DIR / "data" / "supply_chain_edges.csv"


# ==============================
# Load CSV files
# ==============================

print("\n===== AtmoGraph Graph Data Creation =====")

nodes_df = pd.read_csv(NODES_FILE)
edges_df = pd.read_csv(EDGES_FILE)

print("\nLoading Data...")
print("Nodes:", len(nodes_df))
print("Edges:", len(edges_df))


# ==============================
# Create Node ID Mapping
# ==============================

node_id_map = {
    node_id: index
    for index, node_id in enumerate(nodes_df["id"])
}


# ==============================
# Create Node Features
# ==============================

# Features:
# 1. Capacity
# 2. Delay
# 3. Risk
# 4. Disruption

risk_mapping = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2
}

disruption_mapping = {
    "None": 0,
    "Delay": 1,
    "Disruption": 2
}

nodes_df["risk_value"] = (
    nodes_df["risk"]
    .astype(str)
    .str.upper()
    .map(risk_mapping)
    .fillna(0)
)

nodes_df["disruption_value"] = (
    nodes_df["disruption"]
    .astype(str)
    .str.strip()
    .map(disruption_mapping)
    .fillna(0)
)

x = torch.tensor(
    nodes_df[
        [
            "capacity",
            "delay",
            "risk_value",
            "disruption_value"
        ]
    ].values,
    dtype=torch.float
)


# ==============================
# Create Edge Index
# ==============================

source_nodes = []
target_nodes = []

for _, row in edges_df.iterrows():

    source = row["source"]
    target = row["target"]

    if source in node_id_map and target in node_id_map:

        source_nodes.append(node_id_map[source])
        target_nodes.append(node_id_map[target])


edge_index = torch.tensor(
    [source_nodes, target_nodes],
    dtype=torch.long
)


# ==============================
# Create PyTorch Geometric Data
# ==============================

graph_data = Data(
    x=x,
    edge_index=edge_index
)


# ==============================
# Display Graph Information
# ==============================

print("\n===== Graph Data =====")

print("Node Feature Shape:", graph_data.x.shape)
print("Edge Index Shape:", graph_data.edge_index.shape)

print("\nNode Features:")
print(graph_data.x)

print("\nEdge Index:")
print(graph_data.edge_index)

print("\n===== Graph Data Creation Complete =====")