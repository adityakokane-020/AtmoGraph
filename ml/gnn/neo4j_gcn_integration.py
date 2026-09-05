import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from pathlib import Path
from neo4j import GraphDatabase
from torch_geometric.nn import GCNConv


# --------------------------------------------------
# Neo4j Configuration
# --------------------------------------------------

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"
DATABASE = "atmograph"


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"
model_path = MODEL_DIR / "ripple_gcn.pth"


# --------------------------------------------------
# GCN Model
# --------------------------------------------------

class RippleGCN(nn.Module):

    def __init__(self, input_features=5, hidden_features=32):

        super().__init__()

        self.conv1 = GCNConv(
            input_features,
            hidden_features
        )

        self.conv2 = GCNConv(
            hidden_features,
            hidden_features
        )

        self.output = nn.Linear(
            hidden_features,
            1
        )

    def forward(self, x, edge_index):

        x = self.conv1(x, edge_index)
        x = F.relu(x)

        x = self.conv2(x, edge_index)
        x = F.relu(x)

        x = self.output(x)

        return x.squeeze()


# --------------------------------------------------
# Get Disrupted Node From Neo4j
# --------------------------------------------------

def get_disrupted_nodes():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    query = """
    MATCH (n)
    WHERE n.disruption = 1
    RETURN n.id AS id, n.name AS name, n.risk AS risk
    """

    with driver.session(database=DATABASE) as session:

        result = session.run(query)

        nodes = [
            record.data()
            for record in result
        ]

    driver.close()

    return nodes


# --------------------------------------------------
# Update Predictions in Neo4j
# --------------------------------------------------

def update_predictions(predictions):

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    query = """
    MATCH (n {id: $id})
    SET n.predicted_delay = $predicted_delay
    RETURN n.id AS id
    """

    with driver.session(database=DATABASE) as session:

        for prediction in predictions:

            session.run(
                query,
                id=prediction["id"],
                predicted_delay=float(
                    prediction["predicted_delay"]
                )
            )

    driver.close()


# --------------------------------------------------
# Main Pipeline
# --------------------------------------------------

print("==========================================")
print("   AtmoGraph Neo4j → GCN Integration")
print("==========================================")


# --------------------------------------------------
# 1. Read Disruption From Neo4j
# --------------------------------------------------

disrupted_nodes = get_disrupted_nodes()

print("\n[1] Disrupted Nodes From Neo4j:")

if not disrupted_nodes:

    print("No disrupted node found.")
    exit()

for node in disrupted_nodes:

    print(
        f"{node['id']} | "
        f"{node['name']} | "
        f"Risk: {node['risk']}"
    )


# --------------------------------------------------
# 2. Load Graph Data
# --------------------------------------------------

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)

print("\n[2] Graph Loaded")

print("Nodes:", len(nodes))
print("Edges:", len(edges))


# --------------------------------------------------
# 3. Create GCN Features
# --------------------------------------------------

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


# Source indicator

source_indicator = torch.zeros(
    (len(nodes), 1),
    dtype=torch.float
)


# Use first disrupted node

source_node_id = disrupted_nodes[0]["id"]


source_rows = nodes[
    nodes["id"] == source_node_id
]


if source_rows.empty:

    print(
        f"\nERROR: {source_node_id} "
        "not found in node_features.csv"
    )

    exit()


source_index = source_rows.index[0]

source_indicator[
    source_index,
    0
] = 1.0


# Combine features

x = torch.cat(
    [
        x,
        source_indicator
    ],
    dim=1
)


# --------------------------------------------------
# 4. Edge Index
# --------------------------------------------------

edge_index = torch.tensor(

    edges[
        [
            "source_index",
            "target_index"
        ]
    ].values.T,

    dtype=torch.long
)


# --------------------------------------------------
# 5. Load Trained GCN
# --------------------------------------------------

model = RippleGCN()

model.load_state_dict(

    torch.load(
        model_path,
        map_location=torch.device("cpu")
    )
)

model.eval()

print("\n[3] Trained GCN Model Loaded")


# --------------------------------------------------
# 6. GCN Prediction
# --------------------------------------------------

with torch.no_grad():

    predictions = model(
        x,
        edge_index
    ).numpy()


# --------------------------------------------------
# 7. Create Results
# --------------------------------------------------

results = nodes[
    [
        "id",
        "type",
        "country"
    ]
].copy()


results["predicted_delay"] = predictions


results["predicted_delay"] = results[
    "predicted_delay"
].clip(lower=0)


results = results.sort_values(
    by="predicted_delay",
    ascending=False
)


print("\n[4] Ripple Effect Predictions")

for _, row in results.head(10).iterrows():

    print(
        f"{row['id']} | "
        f"{row['type']} | "
        f"{row['country']} | "
        f"{row['predicted_delay']:.2f} days"
    )


# --------------------------------------------------
# 8. Update Neo4j
# --------------------------------------------------

prediction_records = []

for _, row in results.iterrows():

    prediction_records.append(
        {
            "id": row["id"],
            "predicted_delay":
                row["predicted_delay"]
        }
    )


update_predictions(
    prediction_records
)


print("\n[5] Neo4j Updated Successfully")

print(
    "predicted_delay property added "
    "to supply-chain nodes."
)


print("\n==========================================")
print("        Integration Completed")
print("==========================================")