import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from pathlib import Path
from torch_geometric.nn import GCNConv
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ==================================================
# Paths
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"
labels_file = DATA_DIR / "ripple_labels.csv"


# ==================================================
# Load Data
# ==================================================

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)
labels = pd.read_csv(labels_file)

print("===== AtmoGraph GCN Training =====")

print("\nDataset Information:")
print("Nodes:", len(nodes))
print("Edges:", len(edges))
print("Scenarios:", labels["scenario_id"].nunique())
print("Labels:", len(labels))


# ==================================================
# Base Node Features
# ==================================================

base_features = torch.tensor(
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


# ==================================================
# Edge Index
# ==================================================

edge_index = torch.tensor(
    edges[
        [
            "source_index",
            "target_index"
        ]
    ].values.T,
    dtype=torch.long
)


# ==================================================
# GCN Model
# ==================================================

class RippleGCN(nn.Module):

    def __init__(
        self,
        input_features=5,
        hidden_features=32
    ):

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

        x = self.conv1(
            x,
            edge_index
        )

        x = F.relu(x)

        x = self.conv2(
            x,
            edge_index
        )

        x = F.relu(x)

        x = self.output(x)

        return x.squeeze(-1)


# ==================================================
# Device
# ==================================================

device = torch.device("cpu")


# ==================================================
# Model
# ==================================================

model = RippleGCN().to(device)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)

loss_function = nn.MSELoss()


# ==================================================
# Training
# ==================================================

epochs = 300

scenario_ids = labels[
    "scenario_id"
].unique()

for epoch in range(epochs):

    model.train()

    total_loss = 0.0

    for scenario_id in scenario_ids:

        scenario = labels[
            labels["scenario_id"] == scenario_id
        ].sort_values("node_index")

        # ------------------------------------------
        # Scenario target
        # ------------------------------------------

        target = torch.tensor(
            scenario["target_delay"].values,
            dtype=torch.float
        ).to(device)

        # ------------------------------------------
        # Find disrupted/source node
        # ------------------------------------------

        source_nodes = scenario[
            scenario["hop_distance"] == 0
        ]["node_index"].values

        scenario_features = base_features.clone()

        # ------------------------------------------
        # Add scenario disruption signal
        # ------------------------------------------

        if len(source_nodes) > 0:

            for source_node in source_nodes:

                scenario_features[
                    source_node,
                    3
                ] = 1.0

        # ------------------------------------------
        # Add source-node indicator
        # ------------------------------------------

        source_indicator = torch.zeros(
            (len(nodes), 1),
            dtype=torch.float
        )

        if len(source_nodes) > 0:

            for source_node in source_nodes:

                source_indicator[
                    source_node,
                    0
                ] = 1.0

        # ------------------------------------------
        # Final node features
        # ------------------------------------------

        x = torch.cat(
            [
                scenario_features,
                source_indicator
            ],
            dim=1
        ).to(device)

        # ------------------------------------------
        # GCN prediction
        # ------------------------------------------

        prediction = model(
            x,
            edge_index
        )

        # ------------------------------------------
        # Loss
        # ------------------------------------------

        loss = loss_function(
            prediction,
            target
        )

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    # ----------------------------------------------
    # Print progress
    # ----------------------------------------------

    if (epoch + 1) % 25 == 0:

        average_loss = (
            total_loss /
            len(scenario_ids)
        )

        print(
            f"Epoch [{epoch + 1}/{epochs}] "
            f"Loss: {average_loss:.4f}"
        )


# ==================================================
# Evaluation
# ==================================================

model.eval()

all_actual = []
all_predictions = []

with torch.no_grad():

    for scenario_id in scenario_ids:

        scenario = labels[
            labels["scenario_id"] == scenario_id
        ].sort_values("node_index")

        target = torch.tensor(
            scenario["target_delay"].values,
            dtype=torch.float
        )

        source_nodes = scenario[
            scenario["hop_distance"] == 0
        ]["node_index"].values

        scenario_features = base_features.clone()

        if len(source_nodes) > 0:

            for source_node in source_nodes:

                scenario_features[
                    source_node,
                    3
                ] = 1.0

        source_indicator = torch.zeros(
            (len(nodes), 1),
            dtype=torch.float
        )

        if len(source_nodes) > 0:

            for source_node in source_nodes:

                source_indicator[
                    source_node,
                    0
                ] = 1.0

        x = torch.cat(
            [
                scenario_features,
                source_indicator
            ],
            dim=1
        )

        prediction = model(
            x,
            edge_index
        )

        all_actual.extend(
            target.numpy()
        )

        all_predictions.extend(
            prediction.numpy()
        )


# ==================================================
# Metrics
# ==================================================

mae = mean_absolute_error(
    all_actual,
    all_predictions
)

rmse = mean_squared_error(
    all_actual,
    all_predictions
) ** 0.5


print("\n===== Evaluation =====")

print(
    "Total Predictions:",
    len(all_predictions)
)

print(
    "MAE :",
    round(mae, 2)
)

print(
    "RMSE:",
    round(rmse, 2)
)


# ==================================================
# Save Model
# ==================================================

model_path = (
    MODEL_DIR /
    "ripple_gcn.pth"
)

torch.save(
    model.state_dict(),
    model_path
)

print("\nModel saved to:")
print(model_path)

print("\n===== Training Complete =====")