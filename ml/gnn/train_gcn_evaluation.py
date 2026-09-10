import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from pathlib import Path
from torch_geometric.nn import GCNConv

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


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


print("==============================================")
print("     ATMOGRAPH GCN TRAIN / TEST EVALUATION")
print("==============================================")


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
# Scenario IDs
# ==================================================

scenario_ids = labels[
    "scenario_id"
].unique()


# ==================================================
# Train / Test Split
# ==================================================

train_scenarios, test_scenarios = train_test_split(

    scenario_ids,

    test_size=0.2,

    random_state=42
)


print("\nTrain Scenarios:")

for scenario in train_scenarios:

    print(scenario)


print("\nTest Scenarios:")

for scenario in test_scenarios:

    print(scenario)


print(
    "\nTraining Scenarios:",
    len(train_scenarios)
)

print(
    "Testing Scenarios:",
    len(test_scenarios)
)


# ==================================================
# Create Scenario Features
# ==================================================

def create_scenario_features(scenario_id):

    scenario = labels[
        labels["scenario_id"] == scenario_id
    ].sort_values("node_index")


    target = torch.tensor(

        scenario["target_delay"].values,

        dtype=torch.float
    )


    source_nodes = scenario[

        scenario["hop_distance"] == 0

    ][
        "node_index"
    ].values


    scenario_features = base_features.clone()


    # ------------------------------------------------
    # Disruption Signal
    # ------------------------------------------------

    for source_node in source_nodes:

        scenario_features[
            source_node,
            3
        ] = 1.0


    # ------------------------------------------------
    # Source Indicator
    # ------------------------------------------------

    source_indicator = torch.zeros(

        (len(nodes), 1),

        dtype=torch.float
    )


    for source_node in source_nodes:

        source_indicator[
            source_node,
            0
        ] = 1.0


    # ------------------------------------------------
    # Final Features
    # ------------------------------------------------

    x = torch.cat(

        [
            scenario_features,
            source_indicator
        ],

        dim=1
    )


    return x, target


# ==================================================
# Device
# ==================================================

device = torch.device("cpu")


# ==================================================
# Model Setup
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


print("\n==============================================")
print("              TRAINING STARTED")
print("==============================================")


for epoch in range(epochs):

    model.train()

    total_loss = 0.0


    for scenario_id in train_scenarios:

        x, target = create_scenario_features(
            scenario_id
        )


        x = x.to(device)

        target = target.to(device)


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


    # ------------------------------------------------
    # Training Progress
    # ------------------------------------------------

    if (epoch + 1) % 25 == 0:

        average_loss = (

            total_loss /

            len(train_scenarios)

        )


        print(

            f"Epoch [{epoch + 1}/{epochs}] "
            f"Loss: {average_loss:.4f}"

        )


# ==================================================
# Test Evaluation
# ==================================================

print("\n==============================================")
print("           UNSEEN TEST EVALUATION")
print("==============================================")


model.eval()


all_actual = []

all_predictions = []

prediction_results = []


with torch.no_grad():

    for scenario_id in test_scenarios:

        x, target = create_scenario_features(
            scenario_id
        )


        prediction = model(

            x,

            edge_index
        )


        actual_values = target.numpy()

        predicted_values = prediction.numpy()


        all_actual.extend(

            actual_values

        )


        all_predictions.extend(

            predicted_values

        )


        # ------------------------------------------------
        # Save Prediction Results
        # ------------------------------------------------

        scenario_data = labels[

            labels["scenario_id"] == scenario_id

        ].sort_values(

            "node_index"

        )


        for i, (_, row) in enumerate(

            scenario_data.iterrows()

        ):

            prediction_results.append(

                {

                    "scenario_id":
                        scenario_id,

                    "node_index":
                        row["node_index"],

                    "actual_delay":
                        actual_values[i],

                    "predicted_delay":
                        predicted_values[i]

                }

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


r2 = r2_score(

    all_actual,

    all_predictions

)


# ==================================================
# Display Metrics
# ==================================================

print("\n===== Test Evaluation Results =====")


print(

    "Total Test Predictions:",

    len(all_predictions)

)


print(

    "Test MAE:",

    round(mae, 3)

)


print(

    "Test RMSE:",

    round(rmse, 3)

)


print(

    "Test R² Score:",

    round(r2, 3)

)


# ==================================================
# Save Test Predictions
# ==================================================

results_df = pd.DataFrame(

    prediction_results

)


results_file = (

    DATA_DIR /

    "gcn_test_predictions.csv"

)


results_df.to_csv(

    results_file,

    index=False

)


print("\nTest prediction results saved:")

print(results_file)


# ==================================================
# Save Evaluated Model
# ==================================================

model_path = (

    MODEL_DIR /

    "ripple_gcn_evaluated.pth"

)


torch.save(

    model.state_dict(),

    model_path

)


print("\nEvaluated model saved:")

print(model_path)


# ==================================================
# Complete
# ==================================================

print("\n==============================================")
print("        TRAIN / TEST EVALUATION COMPLETE")
print("==============================================")
