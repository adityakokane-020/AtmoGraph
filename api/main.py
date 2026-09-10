from fastapi import FastAPI, HTTPException
from pathlib import Path
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import GCNConv


# ==================================================
# FastAPI App
# ==================================================

app = FastAPI(
    title="AtmoGraph API",
    description="Supply Chain Ripple Effect Prediction API",
    version="1.0.0"
)


# ==================================================
# Paths
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "ml" / "data"
MODEL_DIR = BASE_DIR / "ml" / "models"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"

model_path = MODEL_DIR / "ripple_gcn.pth"


# ==================================================
# Load Data
# ==================================================

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)


# ==================================================
# Base Features
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

    def forward(
        self,
        x,
        edge_index
    ):

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
# Load Model
# ==================================================

model = RippleGCN()

model.load_state_dict(
    torch.load(
        model_path,
        map_location=torch.device("cpu")
    )
)

model.eval()


# ==================================================
# Home API
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to AtmoGraph API",
        "status": "running"
    }


# ==================================================
# Health Check
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "RippleGCN",
        "nodes": len(nodes),
        "edges": len(edges)
    }


# ==================================================
# Ripple Prediction API
# ==================================================

@app.get("/predict/{source_node}")
def predict_ripple(source_node: str):

    source_node = source_node.upper()

    if source_node not in nodes["id"].values:

        raise HTTPException(
            status_code=404,
            detail=f"Node {source_node} not found"
        )

    source_index = nodes[
        nodes["id"] == source_node
    ].index[0]

    scenario_features = base_features.clone()

    # Mark disruption
    scenario_features[
        source_index,
        3
    ] = 1.0


    # Source node indicator
    source_indicator = torch.zeros(
        (len(nodes), 1),
        dtype=torch.float
    )

    source_indicator[
        source_index,
        0
    ] = 1.0


    # Create 5-feature input
    x = torch.cat(
        [
            scenario_features,
            source_indicator
        ],
        dim=1
    )


    # Prediction
    with torch.no_grad():

        predictions = model(
            x,
            edge_index
        ).numpy()


    # Prepare results
    results = []

    for i, prediction in enumerate(predictions):

        delay = max(
            0,
            float(prediction)
        )

        if delay > 0.1:

            results.append(
                {
                    "id": nodes.iloc[i]["id"],
                    "name": str(
                        nodes.iloc[i]["type"]
                    ),
                    "country": str(
                        nodes.iloc[i]["country"]
                    ),
                    "predicted_delay": round(
                        delay,
                        2
                    )
                }
            )


    # Sort by delay
    results = sorted(
        results,
        key=lambda x: x["predicted_delay"],
        reverse=True
    )


    return {

        "disruption_source": source_node,

        "total_nodes": len(nodes),

        "at_risk_nodes": results[:10]

    }


# ==================================================
# Run API
# ==================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )