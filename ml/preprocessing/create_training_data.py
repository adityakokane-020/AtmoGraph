import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

nodes_file = DATA_DIR / "node_features.csv"
scenarios_file = DATA_DIR / "mapped_scenarios.csv"

nodes = pd.read_csv(nodes_file)
scenarios = pd.read_csv(scenarios_file)

training_data = []

for _, scenario in scenarios.iterrows():

    for _, node in nodes.iterrows():

        # Default: no disruption
        disruption = 0

        # Mark disrupted node
        if node["id"] == scenario["disrupted_node"]:
            disruption = 1

        training_data.append({
            "scenario_id": scenario["scenario_id"],
            "node_id": node["id"],
            "node_index": node.name,
            "capacity": node["capacity"],
            "delay": node["delay"],
            "risk_value": node["risk_value"],
            "disruption": disruption,
            "target_delay": scenario["target_delay"]
        })

df = pd.DataFrame(training_data)

output_file = DATA_DIR / "training_data.csv"

df.to_csv(output_file, index=False)

print("===== GNN Training Data =====")

print("Total Rows:", len(df))
print("Total Scenarios:", df["scenario_id"].nunique())
print("Total Nodes:", df["node_id"].nunique())

print("\nDisrupted Nodes:")
print(
    df[df["disruption"] == 1][
        ["scenario_id", "node_id", "target_delay"]
    ]
)

print("\nSaved to:")
print(output_file)