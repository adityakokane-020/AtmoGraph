
import pandas as pd
from pathlib import Path
from collections import defaultdict, deque

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

nodes_file = DATA_DIR / "node_features.csv"
edges_file = DATA_DIR / "edge_index.csv"
scenarios_file = DATA_DIR / "mapped_scenarios_v2.csv"

output_file = DATA_DIR / "ripple_labels_v2.csv"

# ============================================================
# LOAD DATA
# ============================================================

nodes = pd.read_csv(nodes_file)
edges = pd.read_csv(edges_file)
scenarios = pd.read_csv(scenarios_file)

print("==============================================")
print("     ATMOGRAPH RIPPLE LABEL GENERATOR V2")
print("==============================================")

# ============================================================
# BUILD GRAPH
# ============================================================

graph = defaultdict(list)

for _, edge in edges.iterrows():
    source = int(edge["source_index"])
    target = int(edge["target_index"])

    graph[source].append(target)


# ============================================================
# FIND DOWNSTREAM NODES
# ============================================================

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


# ============================================================
# SEVERITY FACTORS
# ============================================================

severity_factors = {
    "High": {
        0: 1.00,
        1: 0.75,
        2: 0.50,
        3: 0.30,
        4: 0.15
    },

    "Medium": {
        0: 1.00,
        1: 0.65,
        2: 0.40,
        3: 0.20,
        4: 0.10
    },

    "Low": {
        0: 1.00,
        1: 0.55,
        2: 0.30,
        3: 0.15,
        4: 0.08
    }
}


# ============================================================
# DISRUPTION TYPE FACTORS
# ============================================================

type_factors = {
    "Port Closure": 1.10,
    "Port Strike": 1.00,
    "Port Congestion": 0.85
}


# ============================================================
# GENERATE RIPPLE LABELS
# ============================================================

ripple_data = []

for _, scenario in scenarios.iterrows():

    scenario_id = scenario["scenario_id"]

    disrupted_node = int(scenario["node_index"])

    disruption_type = scenario["disruption_type"]

    severity = scenario["severity"]

    base_delay = float(scenario["target_delay"])

    distances = find_downstream_nodes(disrupted_node)

    severity_factor = severity_factors[severity]

    type_factor = type_factors[disruption_type]

    for node_index in range(len(nodes)):

        distance = distances.get(node_index, -1)

        # ----------------------------------------------------
        # Disrupted source node
        # ----------------------------------------------------

        if distance == 0:

            predicted_delay = base_delay

        # ----------------------------------------------------
        # Downstream nodes
        # ----------------------------------------------------

        elif distance > 0:

            hop_factor = severity_factor.get(
                distance,
                0.05
            )

            predicted_delay = (
                base_delay
                * type_factor
                * hop_factor
            )

        # ----------------------------------------------------
        # Unconnected nodes
        # ----------------------------------------------------

        else:

            predicted_delay = 0

        ripple_data.append({
            "scenario_id": scenario_id,
            "node_index": node_index,
            "node_id": nodes.iloc[node_index]["id"],
            "hop_distance": distance,
            "target_delay": round(predicted_delay, 2)
        })


# ============================================================
# SAVE LABELS
# ============================================================

ripple_df = pd.DataFrame(ripple_data)

ripple_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print("\nTotal Rows:", len(ripple_df))

print(
    "Total Scenarios:",
    ripple_df["scenario_id"].nunique()
)

print(
    "Total Nodes:",
    ripple_df["node_id"].nunique()
)

print("\nHop Distribution:")

print(
    ripple_df["hop_distance"]
    .value_counts()
    .sort_index()
)

print("\nNon-zero Ripple Predictions:")

print(
    ripple_df[
        ripple_df["target_delay"] > 0
    ].head(30)
)

print("\nSeverity Distribution:")

print(
    scenarios["severity"].value_counts()
)

print("\nDisruption Type Distribution:")

print(
    scenarios["disruption_type"].value_counts()
)

print("\nSaved to:")

print(output_file)

print("\n==============================================")
print("     RIPPLE LABEL GENERATION COMPLETE")
print("==============================================")
