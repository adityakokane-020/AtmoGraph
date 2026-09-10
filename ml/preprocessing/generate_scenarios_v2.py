import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

output_file = DATA_DIR / "disruption_scenarios_v2.csv"

# --------------------------------------------------
# Improved disruption scenarios
# --------------------------------------------------

scenarios = [
    # P001 - Rotterdam Port
    ["SC001", "P001", "Port Strike", "High", 30],
    ["SC002", "P001", "Port Closure", "High", 40],
    ["SC003", "P001", "Port Congestion", "Medium", 18],
    ["SC004", "P001", "Port Strike", "Medium", 20],
    ["SC005", "P001", "Port Congestion", "Low", 10],

    # P002
    ["SC006", "P002", "Port Strike", "High", 25],
    ["SC007", "P002", "Port Closure", "High", 35],
    ["SC008", "P002", "Port Congestion", "Medium", 16],
    ["SC009", "P002", "Port Strike", "Medium", 18],
    ["SC010", "P002", "Port Congestion", "Low", 8],

    # P003
    ["SC011", "P003", "Port Closure", "High", 45],
    ["SC012", "P003", "Port Strike", "High", 38],
    ["SC013", "P003", "Port Congestion", "Medium", 22],
    ["SC014", "P003", "Port Strike", "Medium", 24],
    ["SC015", "P003", "Port Congestion", "Low", 12],

    # P004
    ["SC016", "P004", "Port Closure", "High", 40],
    ["SC017", "P004", "Port Strike", "High", 32],
    ["SC018", "P004", "Port Congestion", "Medium", 20],
    ["SC019", "P004", "Port Strike", "Medium", 18],
    ["SC020", "P004", "Port Congestion", "Low", 9],

    # P005
    ["SC021", "P005", "Port Strike", "High", 35],
    ["SC022", "P005", "Port Closure", "High", 42],
    ["SC023", "P005", "Port Congestion", "Medium", 21],
    ["SC024", "P005", "Port Strike", "Medium", 19],
    ["SC025", "P005", "Port Congestion", "Low", 7],

    # Additional variation
    ["SC026", "P001", "Port Closure", "Medium", 26],
    ["SC027", "P002", "Port Strike", "Low", 12],
    ["SC028", "P003", "Port Closure", "Medium", 28],
    ["SC029", "P004", "Port Strike", "Low", 11],
    ["SC030", "P005", "Port Closure", "Medium", 27],
]

df = pd.DataFrame(
    scenarios,
    columns=[
        "scenario_id",
        "disrupted_node",
        "disruption_type",
        "severity",
        "target_delay"
    ]
)

df.to_csv(output_file, index=False)

print("==============================================")
print("     ATMOGRAPH SCENARIO GENERATOR V2")
print("==============================================")

print("\nTotal Scenarios:", len(df))

print("\nSeverity Distribution:")
print(df["severity"].value_counts())

print("\nDisruption Type Distribution:")
print(df["disruption_type"].value_counts())

print("\nScenario Data:")
print(df)

print("\nSaved to:")
print(output_file)

print("\n==============================================")
print("     SCENARIO GENERATION COMPLETE")
print("==============================================")
