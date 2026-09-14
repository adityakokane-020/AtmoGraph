import os
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
from neo4j import GraphDatabase
from torch_geometric.nn import GCNConv


# ============================================================
# NEO4J CONFIG
# ============================================================

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"

# Set your Neo4j password in environment variable:
# Windows CMD:
# set NEO4J_PASSWORD=your_password
PASSWORD = os.getenv("NEO4J_PASSWORD")

DATABASE = "atmograph"


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "ml" / "data"
MODEL_DIR = BASE_DIR / "ml" / "models"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"
model_file = MODEL_DIR / "ripple_gcn_v2.pth"


# ============================================================
# LOAD DATA
# ============================================================

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)


# ============================================================
# GCN V2 MODEL
# ============================================================

class RippleGCN(nn.Module):

    def __init__(self, input_dim):
        super().__init__()

        self.conv1 = GCNConv(input_dim, 64)
        self.conv2 = GCNConv(64, 32)
        self.conv3 = GCNConv(32, 16)

        self.output = nn.Linear(16, 1)

    def forward(self, x, edge_index):

        x = self.conv1(x, edge_index)
        x = torch.relu(x)

        x = self.conv2(x, edge_index)
        x = torch.relu(x)

        x = self.conv3(x, edge_index)
        x = torch.relu(x)

        x = self.output(x)

        return x.squeeze(-1)


# ============================================================
# LOAD MODEL CHECKPOINT
# ============================================================

checkpoint = torch.load(
    model_file,
    map_location="cpu",
    weights_only=False
)

model = RippleGCN(input_dim=9)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


target_mean = checkpoint["target_mean"]

target_std = checkpoint["target_std"]

feature_mean = torch.tensor(
    checkpoint["feature_mean"],
    dtype=torch.float32
)

feature_std = torch.tensor(
    checkpoint["feature_std"],
    dtype=torch.float32
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
# GET ACTIVE DISRUPTION NODES
# ============================================================

def get_disrupted_nodes(driver):

    query = """
    MATCH (n)
    WHERE n.disruption = 1
    RETURN
        n.id AS id,
        n.name AS name,
        n.risk AS risk,
        n.disruption_type AS disruption_type
    """

    with driver.session(database=DATABASE) as session:

        result = session.run(query)

        return list(result)


# ============================================================
# NORMALIZE SEVERITY
# ============================================================

def normalize_severity(severity):

    if severity is None:
        return None

    severity = str(severity).strip().lower()

    if severity == "high":
        return "High"

    if severity == "medium":
        return "Medium"

    if severity == "low":
        return "Low"

    return None


# ============================================================
# CREATE SCENARIO FEATURES
# ============================================================

def create_scenario_features(
    source_ids,
    severity,
    disruption_type
):

    feature_columns = [
        "capacity",
        "delay",
        "risk_value",
        "disruption_value"
    ]

    # --------------------------------------------------------
    # Base features
    # --------------------------------------------------------

    base_features = nodes[
        feature_columns
    ].values.astype("float32")

    base_features = (
        base_features
        - feature_mean.numpy()
    ) / feature_std.numpy()

    # --------------------------------------------------------
    # Source indicator
    # --------------------------------------------------------

    source_indicator = (
        nodes["id"]
        .isin(source_ids)
        .astype("float32")
        .values
        .reshape(-1, 1)
    )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    severity_map = {
        "Low": 0.0,
        "Medium": 0.5,
        "High": 1.0
    }

    severity_value = severity_map[severity]

    severity_column = torch.full(
        (len(nodes), 1),
        severity_value,
        dtype=torch.float32
    )

    # --------------------------------------------------------
    # Disruption type
    # --------------------------------------------------------

    strike = torch.full(
        (len(nodes), 1),
        1.0 if disruption_type == "Port Strike" else 0.0,
        dtype=torch.float32
    )

    closure = torch.full(
        (len(nodes), 1),
        1.0 if disruption_type == "Port Closure" else 0.0,
        dtype=torch.float32
    )

    congestion = torch.full(
        (len(nodes), 1),
        1.0 if disruption_type == "Port Congestion" else 0.0,
        dtype=torch.float32
    )

    # --------------------------------------------------------
    # Combine 9 features
    # --------------------------------------------------------

    x = torch.tensor(
        base_features,
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
# PREDICTED RISK
# ============================================================

def calculate_risk(delay):

    if delay > 15:
        return "Critical"

    elif delay > 7:
        return "High"

    elif delay > 2:
        return "Medium"

    else:
        return "Low"


# ============================================================
# UPDATE NEO4J
# ============================================================

def update_predictions(driver, results):

    query = """
    MATCH (n {id: $node_id})

    SET
        n.predicted_delay = $predicted_delay,
        n.predicted_risk = $predicted_risk

    RETURN
        n.id AS id,
        n.name AS name,
        n.predicted_delay AS predicted_delay,
        n.predicted_risk AS predicted_risk
    """

    with driver.session(database=DATABASE) as session:

        for row in results:

            session.run(
                query,
                node_id=row["node_id"],
                predicted_delay=row["predicted_delay"],
                predicted_risk=row["predicted_risk"]
            )


# ============================================================
# MAIN GCN PIPELINE
# ============================================================

def run_gcn_pipeline(
    severity=None,
    disruption_type=None
):

    print("\n==========================================")
    print("       GCN V2 RIPPLE PREDICTION")
    print("==========================================")

    if PASSWORD is None:

        print("\nERROR: NEO4J_PASSWORD is not set.")

        print(
            "\nWindows CMD example:"
        )

        print(
            "set NEO4J_PASSWORD=your_password"
        )

        return None

    # --------------------------------------------------------
    # Neo4j connection
    # --------------------------------------------------------

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        # ----------------------------------------------------
        # Get disrupted nodes
        # ----------------------------------------------------

        disrupted_nodes = get_disrupted_nodes(driver)

        if not disrupted_nodes:

            print(
                "\nNo active disruption found in Neo4j."
            )

            return None

        print("\nActive Disruption Nodes:")

        for node in disrupted_nodes:

            print(
                f"{node['id']} | "
                f"{node['name']} | "
                f"Risk: {node['risk']}"
            )

        # ----------------------------------------------------
        # Severity
        # ----------------------------------------------------

        if severity is None:

            severity = normalize_severity(
                disrupted_nodes[0]["risk"]
            )

        else:

            severity = normalize_severity(
                severity
            )

        if severity is None:

            print(
                "\nERROR: Invalid severity."
            )

            return None

        # ----------------------------------------------------
        # Disruption Type
        # ----------------------------------------------------

        if disruption_type is None:

            disruption_type = (
                disrupted_nodes[0]["disruption_type"]
            )

        if disruption_type not in [
            "Port Strike",
            "Port Closure",
            "Port Congestion"
        ]:

            print(
                "\nERROR: Unsupported disruption type:"
            )

            print(disruption_type)

            print(
                "\nSupported types:"
            )

            print("Port Strike")
            print("Port Closure")
            print("Port Congestion")

            return None

        print("\nScenario Information:")
        print("Severity:", severity)
        print("Disruption Type:", disruption_type)

        # ----------------------------------------------------
        # Source node IDs
        # ----------------------------------------------------

        source_ids = [
            node["id"]
            for node in disrupted_nodes
        ]

        # ----------------------------------------------------
        # Create 9-feature input
        # ----------------------------------------------------

        x = create_scenario_features(
            source_ids,
            severity,
            disruption_type
        )

        print(
            "\nInput Feature Shape:",
            x.shape
        )

        # ----------------------------------------------------
        # GCN Prediction
        # ----------------------------------------------------

        with torch.no_grad():

            normalized_prediction = model(
                x,
                edge_index
            )

            prediction = (
                normalized_prediction
                * target_std
                + target_mean
            )

            prediction = prediction.numpy()

            prediction = prediction.clip(
                min=0
            )

        # ----------------------------------------------------
        # Prepare results
        # ----------------------------------------------------

        results = []

        for i in range(len(nodes)):

            delay = float(
                prediction[i]
            )

            risk = calculate_risk(
                delay
            )

            results.append(
                {
                    "node_id": nodes.iloc[i]["id"],
                    "node_name": nodes.iloc[i]["id"],
                    "predicted_delay": round(
                        delay,
                        2
                    ),
                    "predicted_risk": risk
                }
            )

        # ----------------------------------------------------
        # Print predictions
        # ----------------------------------------------------

        print("\n===== GCN V2 Predictions =====")

        for row in results:

            print(
                f"{row['node_id']} | "
                f"{row['node_name']} | "
                f"Delay: {row['predicted_delay']} days | "
                f"Risk: {row['predicted_risk']}"
            )

        # ----------------------------------------------------
        # Update Neo4j
        # ----------------------------------------------------

        update_predictions(
            driver,
            results
        )

        print(
            "\nNeo4j predicted delay and risk "
            "updated successfully."
        )

        print("\n==========================================")
        print("       GCN V2 PIPELINE COMPLETED")
        print("==========================================")

        return results

    finally:

        driver.close()


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    run_gcn_pipeline()