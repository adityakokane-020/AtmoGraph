import sys
from pathlib import Path


# ==================================================
# Project Path Setup
# ==================================================

CURRENT_DIR = Path(__file__).resolve().parent

NLP_DIR = CURRENT_DIR / "nlp"
GNN_DIR = CURRENT_DIR / "gnn"

sys.path.append(str(NLP_DIR))
sys.path.append(str(GNN_DIR))


# ==================================================
# Import NLP Pipeline
# ==================================================

from integration import run_pipeline


# ==================================================
# Import GNN Integration
# ==================================================

from neo4j_gcn_integration import run_gcn_pipeline


# ==================================================
# Complete AtmoGraph Pipeline
# ==================================================

def run_complete_pipeline(news):

    print("\n")
    print("====================================================")
    print("        ATMOGRAPH COMPLETE INTELLIGENCE PIPELINE")
    print("====================================================")

    # ------------------------------------------------
    # STEP 1: NLP Pipeline
    # ------------------------------------------------

    print("\n[STEP 1] STARTING NLP PIPELINE")

    run_pipeline(news)

    # ------------------------------------------------
    # STEP 2: GCN Ripple Prediction
    # ------------------------------------------------

    print("\n[STEP 2] STARTING GCN RIPPLE PREDICTION")

    run_gcn_pipeline()

    # ------------------------------------------------
    # Pipeline Complete
    # ------------------------------------------------

    print("\n")
    print("====================================================")
    print("        ATMOGRAPH PIPELINE COMPLETED SUCCESSFULLY")
    print("====================================================")

    print("\nFinal Flow:")

    print("News Input")
    print("   ↓")
    print("Entity Extraction")
    print("   ↓")
    print("Entity Mapping")
    print("   ↓")
    print("Severity Detection")
    print("   ↓")
    print("Neo4j Risk Update")
    print("   ↓")
    print("GCN Ripple Prediction")
    print("   ↓")
    print("Predicted Delay + Predicted Risk")
    print("   ↓")
    print("Neo4j Updated")


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    news = (
        "Rotterdam Port has been closed due to a severe "
        "operational disruption causing major shipping delays."
    )

    run_complete_pipeline(news)
