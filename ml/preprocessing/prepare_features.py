import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

input_file = DATA_DIR / "supply_chain_nodes.csv"
output_file = DATA_DIR / "node_features.csv"

df = pd.read_csv(input_file)

# Convert risk into numeric values
risk_mapping = {
    "Low": 0,
    "Medium": 1,
    "High": 2
}

df["risk_value"] = df["risk"].map(risk_mapping)

# Convert disruption into numeric value
df["disruption_value"] = (
    df["disruption"]
    .fillna("None")
    .apply(lambda x: 0 if x == "None" else 1)
)

# Select features for ML
features = df[
    [
        "id",
        "type",
        "country",
        "capacity",
        "delay",
        "risk_value",
        "disruption_value"
    ]
]

features.to_csv(output_file, index=False)

print("===== Feature Preparation =====")
print("Total Nodes:", len(features))
print("\nFeatures:")
print(features.head())

print("\nSaved to:")
print(output_file)