import pandas as pd
from pathlib import Path
from collections import defaultdict, deque

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"
scenarios_file = DATA_DIR / "mapped_scenarios.csv"

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)
scenarios = pd.read_csv(scenarios_file)

# --------------------------------------------------
# Build directed graph
# --------------------------------------------------

graph = defaultdict(list)

for _, edge in edges.iterrows():
    source = int(edge["source_index"])
    target = int(edge["target_index"])

    graph[source].append(target)


# --------------------------------------------------
# Find downstream nodes using BFS
# --------------------------------------------------

def find_downstream_nodes(start_node):
    distances = {start_node: 0}

    queue = deque([start_node])

    while queue:

        current = queue.popleft()

        for neighbour in graph[current]:

            if neighbour not in distances:

                distances[neighbour] = distances[current] + 1
                queue.append(neighbour)

    return distances


# --------------------------------------------------
# Generate ripple-effect labels
# --------------------------------------------------

ripple_data = []

for _, scenario in scenarios.iterrows():

    scenario_id = scenario["scenario_id"]
    disrupted_node = int(scenario["node_index"])
    base_delay = float(scenario["target_delay"])

    distances = find_downstream_nodes(disrupted_node)

    for node_index in range(len(nodes)):

        distance = distances.get(node_index, -1)

        # Disrupted node
        if distance == 0:
            predicted_delay = base_delay

        # Direct downstream node
        elif distance == 1:
            predicted_delay = base_delay * 0.70

        # Two-hop downstream
        elif distance == 2:
            predicted_delay = base_delay * 0.45

        # Three-hop downstream
        elif distance == 3:
            predicted_delay = base_delay * 0.25

        # Further downstream
        elif distance > 3:
            predicted_delay = base_delay * 0.10

        # Unconnected node
        else:
            predicted_delay = 0

        ripple_data.append({
            "scenario_id": scenario_id,
            "node_index": node_index,
            "node_id": nodes.iloc[node_index]["id"],
            "hop_distance": distance,
            "target_delay": round(predicted_delay, 2)
        })


# --------------------------------------------------
# Save dataset
# --------------------------------------------------

ripple_df = pd.DataFrame(ripple_data)

output_file = DATA_DIR / "ripple_labels.csv"

ripple_df.to_csv(output_file, index=False)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("===== AtmoGraph Ripple Effect Labels =====")

print("Total Rows:", len(ripple_df))

print(
    "Total Scenarios:",
    ripple_df["scenario_id"].nunique()
)

print(
    "Total Nodes:",
    ripple_df["node_id"].nunique()
)

print("\nHop Distribution:")
print(ripple_df["hop_distance"].value_counts().sort_index())

print("\nSample Ripple Results:")

print(
    ripple_df[
        ripple_df["target_delay"] > 0
    ].head(20)
)

print("\nSaved to:")
print(output_file)

print("\n===== Ripple Label Generation Complete =====")