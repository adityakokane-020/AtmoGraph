import pandas as pd
import networkx as nx

# Paths
BASE = "ml/data"

nodes = pd.read_csv(f"{BASE}/supply_chain_nodes.csv")
edges = pd.read_csv(f"{BASE}/supply_chain_edges.csv")
scenarios = pd.read_csv(f"{BASE}/disruption_scenarios_v2.csv")


# Build graph
G = nx.DiGraph()

for _, row in edges.iterrows():
    G.add_edge(row["source"], row["target"])


# Propagation factors by hop
FACTORS = {
    0: 1.00,
    1: 0.70,
    2: 0.45,
    3: 0.25,
}


rows = []

for _, scenario in scenarios.iterrows():

    # Actual disrupted node
    source = scenario["disrupted_node"]

    # Original disruption delay
    base_delay = float(scenario["target_delay"])

    # Find downstream nodes
    try:
        distances = nx.single_source_shortest_path_length(G, source)
    except nx.NetworkXError:
        distances = {}

    for _, node in nodes.iterrows():

        # Actual node ID
        node_id = node["id"]

        # Distance from disrupted node
        hop = distances.get(node_id)

        if hop is None:
            delay = 0.0
        else:
            factor = FACTORS.get(hop, 0.10)
            delay = base_delay * factor

        # Risk based on predicted delay
        if delay <= 2:
            risk = "Low"
        elif delay <= 7:
            risk = "Medium"
        elif delay <= 15:
            risk = "High"
        else:
            risk = "Critical"

        rows.append({
            "scenario_id": scenario["scenario_id"],
            "node_id": node_id,
            "target_delay": round(delay, 2),
            "risk": risk
        })


# Create DataFrame
df = pd.DataFrame(rows)


# Save NEW candidate file
output = f"{BASE}/ripple_labels_v3.csv"
df.to_csv(output, index=False)


print(f"\nCreated: {output}")
print(f"Rows: {len(df)}")


# Overall risk distribution
print("\nRisk distribution:")
print(df["risk"].value_counts())


# Rotterdam example
print("\nRotterdam example:")

print(
    df[
        (df["scenario_id"] == "SC002") &
        (df["target_delay"] > 0)
    ][
        ["node_id", "target_delay", "risk"]
    ]
)