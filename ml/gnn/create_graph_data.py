import pandas as pd
import torch
from pathlib import Path
from torch_geometric.data import Data

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)

# Node features
x = torch.tensor(
    nodes[
        [
            "capacity",
            "delay",
            "risk_value",
            "disruption_value"
        ]
    ].values,
    dtype=torch.float
)

# Edge index
edge_index = torch.tensor(
    edges[
        [
            "source_index",
            "target_index"
        ]
    ].values.T,
    dtype=torch.long
)

# Create PyTorch Geometric graph
graph = Data(
    x=x,
    edge_index=edge_index
)

print("===== AtmoGraph PyG Graph =====")

print("Number of Nodes:", graph.num_nodes)
print("Number of Edges:", graph.num_edges)
print("Number of Node Features:", graph.num_node_features)

print("\nNode Feature Shape:", graph.x.shape)
print("Edge Index Shape:", graph.edge_index.shape)

print("\nGraph:")
print(graph)