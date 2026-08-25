import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

nodes_file = DATA_DIR / "node_features.csv"
scenarios_file = DATA_DIR / "disruption_scenarios.csv"

nodes = pd.read_csv(nodes_file)
scenarios = pd.read_csv(scenarios_file)

# Map node ID to numeric index
node_mapping = {
    node_id: index
    for index, node_id in enumerate(nodes["id"])
}

# Add numeric node index
scenarios["node_index"] = scenarios["disrupted_node"].map(node_mapping)

# Check invalid mappings
invalid = scenarios[scenarios["node_index"].isna()]

print("===== Scenario Mapping =====")

print("Total Scenarios:", len(scenarios))
print("Valid Mappings:", len(scenarios) - len(invalid))
print("Invalid Mappings:", len(invalid))

print("\nMapped Scenarios:")
print(
    scenarios[
        [
            "scenario_id",
            "disrupted_node",
            "node_index",
            "disruption_type",
            "severity",
            "target_delay"
        ]
    ]
)

# Save mapped scenarios
output_file = DATA_DIR / "mapped_scenarios.csv"
scenarios.to_csv(output_file, index=False)

print("\nSaved to:")
print(output_file)