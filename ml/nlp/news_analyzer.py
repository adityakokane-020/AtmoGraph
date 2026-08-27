import spacy

from entity_mapper import extract_and_map
from disruption_classifier import analyze_disruption


# --------------------------------------------------
# Master News Analyzer
# --------------------------------------------------

def analyze_news(text):

    # Entity extraction + graph mapping
    mapped_entities = extract_and_map(text)

    # Disruption + severity
    disruption_result = analyze_disruption(text)

    # Find affected graph node
    affected_node = None

    for entity in mapped_entities:

        if entity["node_id"] is not None:

            affected_node = {
                "node_id": entity["node_id"],
                "node_name": entity["node_name"],
                "node_type": entity["node_type"],
                "country": entity["country"]
            }

            break

    # --------------------------------------------------
    # Confidence Score
    # --------------------------------------------------

    confidence = 0

    if affected_node:
        confidence += 40

    if disruption_result["disruption_type"] != "Unknown":
        confidence += 40

    if disruption_result["severity"] != "None":
        confidence += 20

    # --------------------------------------------------
    # Final Result
    # --------------------------------------------------

    return {
        "news": text,
        "entities": mapped_entities,
        "affected_node": affected_node,
        "disruption_type": disruption_result["disruption_type"],
        "severity": disruption_result["severity"],
        "confidence": confidence
    }


# --------------------------------------------------
# Display Result
# --------------------------------------------------

def print_result(result):

    print("\n========================================")
    print("        AtmoGraph NLP Analysis")
    print("========================================")

    print("\nNews:")
    print(result["news"])

    print("\nEntities:")

    if result["entities"]:

        for entity in result["entities"]:

            print(
                f"  {entity['entity']} "
                f"({entity['entity_type']}) "
                f"→ {entity['node_id'] or 'Not mapped'}"
            )

    else:

        print("  No entities detected")

    print("\nAffected Node:")

    if result["affected_node"]:

        node = result["affected_node"]

        print(f"  Node ID   : {node['node_id']}")
        print(f"  Node Name : {node['node_name']}")
        print(f"  Type      : {node['node_type']}")
        print(f"  Country   : {node['country']}")

    else:

        print("  No graph node mapped")

    print("\nDisruption Type:")
    print(f"  {result['disruption_type']}")

    print("\nSeverity:")
    print(f"  {result['severity']}")

    print("\nConfidence:")
    print(f"  {result['confidence']}%")

    print("\n========================================")


# --------------------------------------------------
# Test Cases
# --------------------------------------------------

if __name__ == "__main__":

    test_news = [

        "Workers announced a major strike at Rotterdam Port.",

        "Hamburg Port has been closed due to a severe operational disruption.",

        "Heavy congestion at Singapore Port is causing shipping delays.",

        "Mumbai Port is facing significant shipping delays.",

        "Global electronics companies reported strong quarterly sales."
    ]

    print("\n")
    print("############################################")
    print("#       AtmoGraph Master NLP Pipeline      #")
    print("############################################")

    for i, news in enumerate(test_news, start=1):

        print(f"\n\n========== TEST CASE {i} ==========")

        result = analyze_news(news)

        print_result(result)