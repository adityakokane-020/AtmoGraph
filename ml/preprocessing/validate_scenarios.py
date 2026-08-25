import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

file = DATA_DIR / "disruption_scenarios.csv"

df = pd.read_csv(file)

print("===== Disruption Scenario Validation =====")

print("Total Scenarios:", len(df))

print("\nDisruption Types:")
print(df["disruption_type"].value_counts())

print("\nSeverity:")
print(df["severity"].value_counts())

print("\nTarget Delay Statistics:")
print(df["target_delay"].describe())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Scenario IDs:",
      df["scenario_id"].duplicated().sum())

print("\n===== Validation Complete =====")