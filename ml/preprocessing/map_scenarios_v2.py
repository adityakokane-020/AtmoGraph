import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

scenarios_file = DATA_DIR / "disruption_scenarios_v2.csv"
nodes_file = DATA_DIR / "supply_chain_nodes.csv"

output_file = DATA_DIR / "mapped_scenarios_v2.csv"

# --------------------------------------------------
# Load data
# --------------------------------------------------

scenarios = pd.read_csv(scenarios_file)
nodes = pd.read_csv(nodes_file)

# --------------------------------------------------
# Create node ID → node index mapping
# --------------------------------------------------

node_mapping = {
    node_id: index
    for index, node_id in enumerate(nodes["id"])
}

# --------------------------------------------------
# Map disrupted node to node index
# --------------------------------------------------

scenarios["node_index"] = scenarios["disrupted_node"].map(
    node_mapping
)

# --------------------------------------------------
# Validate mapping
# --------------------------------------------------

if scenarios["node_index"].isna().any():
    print("\nERROR: Some disrupted nodes could not be mapped.")

    print(
        scenarios[
            scenarios["node_index"].isna()
        ]
    )

    raise ValueError("Node mapping failed.")

# Convert index to integer
scenarios["node_index"] = scenarios["node_index"].astype(int)

# --------------------------------------------------
# Save mapped scenarios
# --------------------------------------------------

scenarios.to_csv(
    output_file,
    index=False
)

print("==============================================")
print("      ATMOGRAPH SCENARIO MAPPING V2")
print("==============================================")

print("\nTotal Scenarios:", len(scenarios))

print("\nMapped Scenarios:")
print(scenarios)

print("\nSaved to:")
print(output_file)

print("\n==============================================")
print("       SCENARIO MAPPING COMPLETE")
print("==============================================")
