import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from pathlib import Path
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
from sklearn.metrics import mean_absolute_error, mean_squared_error


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"
labels_file = DATA_DIR / "ripple_labels.csv"


# --------------------------------------------------
# Load data
# --------------------------------------------------

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)
labels = pd.read_csv(labels_file)


# --------------------------------------------------
# Node features
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


# --------------------------------------------------
# Edge index
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
# Model
# --------------------------------------------------

class RippleGCN(nn.Module):

    def __init__(self, input_features=4, hidden_features=32):

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
# Training
# --------------------------------------------------

device = torch.device("cpu")

model = RippleGCN().to(device)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)

loss_function = nn.MSELoss()


# --------------------------------------------------
# Training loop
# --------------------------------------------------

epochs = 200

print("===== AtmoGraph GCN Training =====")

for epoch in range(epochs):

    model.train()

    total_loss = 0

    for scenario_id in labels["scenario_id"].unique():

        scenario = labels[
            labels["scenario_id"] == scenario_id
        ]

        target = torch.tensor(
            scenario[
                "target_delay"
            ].values,
            dtype=torch.float
        )

        prediction = model(
            x,
            edge_index
        )

        loss = loss_function(
            prediction,
            target
        )

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        total_loss += loss.item()


    if (epoch + 1) % 20 == 0:

        print(
            f"Epoch [{epoch + 1}/{epochs}] "
            f"Loss: {total_loss:.4f}"
        )


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

model.eval()

with torch.no_grad():

    predictions = model(
        x,
        edge_index
    ).numpy()


actual = labels[
    labels["scenario_id"] ==
    labels["scenario_id"].iloc[0]
]["target_delay"].values


predictions = predictions[:len(actual)]


mae = mean_absolute_error(
    actual,
    predictions
)

rmse = mean_squared_error(
    actual,
    predictions
) ** 0.5


print("\n===== Evaluation =====")

print("MAE :", round(mae, 2))
print("RMSE:", round(rmse, 2))


# --------------------------------------------------
# Save model
# --------------------------------------------------

model_path = MODEL_DIR / "ripple_gcn.pth"

torch.save(
    model.state_dict(),
    model_path
)

print("\nModel saved to:")
print(model_path)

print("\n===== Training Complete =====")