import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from pathlib import Path
from torch_geometric.nn import GCNConv


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"

model_path = MODEL_DIR / "ripple_gcn.pth"


# --------------------------------------------------
# GCN Model Architecture
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
# Load Graph Data
# --------------------------------------------------

print("===== AtmoGraph Ripple Prediction =====")

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)


# Node Features

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

# Add source node indicator
source_indicator = torch.zeros(
    (len(nodes), 1),
    dtype=torch.float
)

# Example disruption source: P001
source_node_id = "P001"

source_index = nodes[
    nodes["id"] == source_node_id
].index[0]

source_indicator[source_index, 0] = 1.0


# Combine 4 base features + source indicator
x = torch.cat(
    [
        x,
        source_indicator
    ],
    dim=1
)

# Edge Index

edge_index = torch.tensor(

    edges[
        [
            "source_index",
            "target_index"
        ]
    ].values.T,

    dtype=torch.long
)


print("\nGraph Loaded")

print("Nodes:", len(nodes))
print("Edges:", len(edges))


# --------------------------------------------------
# Load Trained Model
# --------------------------------------------------

model = RippleGCN()

model.load_state_dict(
    torch.load(
        model_path,
        map_location=torch.device("cpu")
    )
)

model.eval()

print("\nTrained GCN Model Loaded")


# --------------------------------------------------
# Run Prediction
# --------------------------------------------------

with torch.no_grad():

    predictions = model(
        x,
        edge_index
    ).numpy()


# --------------------------------------------------
# Create Prediction Results
# --------------------------------------------------

results = nodes[
    [
        "id",
        "type",
        "country"
    ]
].copy()

results["predicted_delay"] = predictions


# Remove negative predictions

results["predicted_delay"] = results[
    "predicted_delay"
].clip(lower=0)


# --------------------------------------------------
# Display Results
# --------------------------------------------------

print("\n===== Ripple Effect Predictions =====")

results = results.sort_values(
    by="predicted_delay",
    ascending=False
)


for _, row in results.iterrows():

    print(
        f"{row['id']} | "
        f"{row['type']} | "
        f"{row['country']} | "
        f"Predicted Delay: "
        f"{row['predicted_delay']:.2f} days"
    )


# --------------------------------------------------
# Identify At-Risk Nodes
# --------------------------------------------------

at_risk = results[
    results["predicted_delay"] > 5
]


print("\n===== At-Risk Nodes =====")

if len(at_risk) == 0:

    print("No significant supply chain risk detected.")

else:

    for _, row in at_risk.iterrows():

        print(
            f"{row['id']} - "
            f"Predicted Delay: "
            f"{row['predicted_delay']:.2f} days"
        )


# --------------------------------------------------
# Save Predictions
# --------------------------------------------------

output_file = DATA_DIR / "ripple_predictions.csv"

results.to_csv(
    output_file,
    index=False
)


print("\nPredictions saved to:")

print(output_file)


print("\n===== Prediction Complete =====")