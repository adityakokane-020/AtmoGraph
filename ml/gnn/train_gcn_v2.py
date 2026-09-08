import pandas as pd
import torch
import torch.nn as nn

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from torch_geometric.nn import GCNConv


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "ml" / "data"
MODEL_DIR = BASE_DIR / "ml" / "models"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"
labels_file = DATA_DIR / "ripple_labels_v2.csv"
scenarios_file = DATA_DIR / "mapped_scenarios_v2.csv"

model_file = MODEL_DIR / "ripple_gcn_v2.pth"
prediction_file = DATA_DIR / "gcn_v2_test_predictions.csv"


# ============================================================
# LOAD DATA
# ============================================================

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)
labels = pd.read_csv(labels_file)
scenarios = pd.read_csv(scenarios_file)


print("==============================================")
print("       ATMOGRAPH IMPROVED GCN V2")
print("==============================================")


# ============================================================
# NODE FEATURES
# ============================================================

feature_columns = [
    "capacity",
    "delay",
    "risk_value",
    "disruption_value"
]

base_features = nodes[feature_columns].values.astype("float32")


# ============================================================
# NORMALIZE NODE FEATURES
# ============================================================

feature_mean = base_features.mean(axis=0)
feature_std = base_features.std(axis=0)

feature_std[feature_std == 0] = 1

base_features = (
    (base_features - feature_mean)
    / feature_std
)


# ============================================================
# EDGE INDEX
# ============================================================

edge_index = torch.tensor(
    edges[
        [
            "source_index",
            "target_index"
        ]
    ].values.T,
    dtype=torch.long
)


# ============================================================
# SCENARIO FEATURE CREATION
# ============================================================

def create_scenario_features(scenario):

    scenario_features = base_features.copy()

    # --------------------------------------------------------
    # Source indicator
    # --------------------------------------------------------

    source_indicator = (
        nodes.index == int(scenario["node_index"])
    ).astype("float32").reshape(-1, 1)


    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    severity_map = {
        "Low": 0.0,
        "Medium": 0.5,
        "High": 1.0
    }

    severity = severity_map[
        scenario["severity"]
    ]

    severity_column = torch.full(
        (len(nodes), 1),
        severity,
        dtype=torch.float32
    )


    # --------------------------------------------------------
    # Disruption type
    # --------------------------------------------------------

    disruption_type = scenario["disruption_type"]

    strike = torch.full(
        (len(nodes), 1),
        1.0 if disruption_type == "Port Strike" else 0.0
    )

    closure = torch.full(
        (len(nodes), 1),
        1.0 if disruption_type == "Port Closure" else 0.0
    )

    congestion = torch.full(
        (len(nodes), 1),
        1.0 if disruption_type == "Port Congestion" else 0.0
    )


    # --------------------------------------------------------
    # Combine all features
    # --------------------------------------------------------

    x = torch.tensor(
        scenario_features,
        dtype=torch.float32
    )

    x = torch.cat(
        [
            x,
            torch.tensor(
                source_indicator,
                dtype=torch.float32
            ),
            severity_column,
            strike,
            closure,
            congestion
        ],
        dim=1
    )

    return x


# ============================================================
# MODEL
# ============================================================

class RippleGCN(nn.Module):

    def __init__(self, input_dim):

        super().__init__()

        self.conv1 = GCNConv(
            input_dim,
            64
        )

        self.conv2 = GCNConv(
            64,
            32
        )

        self.conv3 = GCNConv(
            32,
            16
        )

        self.output = nn.Linear(
            16,
            1
        )


    def forward(self, x, edge_index):

        x = self.conv1(
            x,
            edge_index
        )

        x = torch.relu(x)

        x = self.conv2(
            x,
            edge_index
        )

        x = torch.relu(x)

        x = self.conv3(
            x,
            edge_index
        )

        x = torch.relu(x)

        x = self.output(x)

        return x.squeeze(-1)


# ============================================================
# SCENARIO SPLIT
# ============================================================

scenario_ids = scenarios[
    "scenario_id"
].unique()


train_scenarios, test_scenarios = train_test_split(
    scenario_ids,
    test_size=0.20,
    random_state=42
)


print("\nTrain Scenarios:")
print(", ".join(train_scenarios))


print("\nTest Scenarios:")
print(", ".join(test_scenarios))


# ============================================================
# CREATE TRAINING DATA
# ============================================================

train_data = []

target_values = []


for scenario_id in train_scenarios:

    scenario = scenarios[
        scenarios["scenario_id"] == scenario_id
    ].iloc[0]

    x = create_scenario_features(
        scenario
    )

    target = torch.tensor(
        labels[
            labels["scenario_id"] == scenario_id
        ]["target_delay"].values,
        dtype=torch.float32
    )

    train_data.append(
        (
            x,
            target
        )
    )

    target_values.extend(
        target.tolist()
    )


# ============================================================
# TARGET NORMALIZATION
# ============================================================

target_mean = torch.tensor(
    sum(target_values) / len(target_values),
    dtype=torch.float32
)

target_std = torch.tensor(
    (
        sum(
            (x - target_mean.item()) ** 2
            for x in target_values
        )
        / len(target_values)
    ) ** 0.5,
    dtype=torch.float32
)

if target_std == 0:
    target_std = torch.tensor(
        1.0
    )


# ============================================================
# MODEL
# ============================================================

INPUT_DIM = 9

model = RippleGCN(
    INPUT_DIM
)


optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.005,
    weight_decay=0.00001
)

criterion = nn.MSELoss()


# ============================================================
# TRAINING
# ============================================================

EPOCHS = 500


print("\n==============================================")
print("             TRAINING STARTED")
print("==============================================")


for epoch in range(EPOCHS):

    model.train()

    total_loss = 0.0


    for x, target in train_data:

        optimizer.zero_grad()


        prediction = model(
            x,
            edge_index
        )


        # Normalize target
        normalized_target = (
            target - target_mean
        ) / target_std


        loss = criterion(
            prediction,
            normalized_target
        )


        loss.backward()

        optimizer.step()


        total_loss += loss.item()


    if (epoch + 1) % 50 == 0:

        average_loss = (
            total_loss
            / len(train_data)
        )

        print(
            f"Epoch [{epoch + 1}/{EPOCHS}] "
            f"Loss: {average_loss:.4f}"
        )


# ============================================================
# SAVE MODEL
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

torch.save(
    {
        "model_state_dict":
            model.state_dict(),

        "target_mean":
            target_mean,

        "target_std":
            target_std,

        "feature_mean":
            feature_mean,

        "feature_std":
            feature_std
    },
    model_file
)


print("\nModel saved to:")
print(model_file)


# ============================================================
# EVALUATION
# ============================================================

model.eval()

all_predictions = []
all_actual = []

prediction_rows = []


with torch.no_grad():

    for scenario_id in test_scenarios:

        scenario = scenarios[
            scenarios["scenario_id"] == scenario_id
        ].iloc[0]


        x = create_scenario_features(
            scenario
        )


        normalized_prediction = model(
            x,
            edge_index
        )


        # Convert prediction back to days
        prediction = (
            normalized_prediction
            * target_std
            + target_mean
        )


        prediction = prediction.numpy()

        prediction = prediction.clip(
            min=0
        )


        actual = labels[
            labels["scenario_id"] == scenario_id
        ]["target_delay"].values


        all_predictions.extend(
            prediction
        )

        all_actual.extend(
            actual
        )


        scenario_labels = labels[
            labels["scenario_id"] == scenario_id
        ].reset_index(drop=True)


        for i in range(
            len(scenario_labels)
        ):

            prediction_rows.append({

                "scenario_id":
                    scenario_id,

                "node_index":
                    scenario_labels.loc[
                        i,
                        "node_index"
                    ],

                "node_id":
                    scenario_labels.loc[
                        i,
                        "node_id"
                    ],

                "actual_delay":
                    actual[i],

                "predicted_delay":
                    round(
                        float(
                            prediction[i]
                        ),
                        2
                    ),

                "error":
                    round(
                        abs(
                            actual[i]
                            - prediction[i]
                        ),
                        2
                    )
            })


# ============================================================
# METRICS
# ============================================================

mae = mean_absolute_error(
    all_actual,
    all_predictions
)

rmse = (
    mean_squared_error(
        all_actual,
        all_predictions
    )
    ** 0.5
)

r2 = r2_score(
    all_actual,
    all_predictions
)


# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_df = pd.DataFrame(
    prediction_rows
)

prediction_df.to_csv(
    prediction_file,
    index=False
)


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n==============================================")
print("          IMPROVED V2 RESULTS")
print("==============================================")

print(
    "\nTraining Scenarios:",
    len(train_scenarios)
)

print(
    "Testing Scenarios:",
    len(test_scenarios)
)

print(
    "Total Test Predictions:",
    len(all_predictions)
)

print(
    f"\nTest MAE : {mae:.3f} days"
)

print(
    f"Test RMSE: {rmse:.3f} days"
)

print(
    f"Test R²  : {r2:.3f}"
)

print("\nPredictions saved to:")
print(prediction_file)

print("\n==============================================")
print("       IMPROVED GCN V2 COMPLETE")
print("==============================================")
