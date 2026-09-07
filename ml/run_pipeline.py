
import sys
from pathlib import Path


# ==================================================
# Project Path Setup
# ==================================================

CURRENT_DIR = Path(__file__).resolve().parent

NLP_DIR = CURRENT_DIR / "nlp"
GNN_DIR = CURRENT_DIR / "gnn"

sys.path.append(str(CURRENT_DIR))
sys.path.append(str(NLP_DIR))
sys.path.append(str(GNN_DIR))


# ==================================================
# Import Reset Function
# ==================================================

from reset_disruptions import reset_disruptions


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
    # Display News
    # ------------------------------------------------

    print("\nINPUT NEWS:")
    print(news)

    # ------------------------------------------------
    # STEP 0: Reset Previous Disruptions
    # ------------------------------------------------

    print("\n[STEP 0] RESETTING PREVIOUS DISRUPTIONS")

    reset_disruptions()

    # ------------------------------------------------
    # STEP 1: NLP Pipeline
    # ------------------------------------------------

    print("\n[STEP 1] STARTING NLP PIPELINE")

    nlp_success = run_pipeline(news)

    # ------------------------------------------------
    # STEP 2: GCN Ripple Prediction
    # ------------------------------------------------

    if nlp_success:

        print("\n[STEP 2] STARTING GCN RIPPLE PREDICTION")

        run_gcn_pipeline()

    else:

        print("\n[STEP 2] GCN RIPPLE PREDICTION SKIPPED")

        print("Reason: No supply chain entity was found.")

    # ------------------------------------------------
    # Pipeline Complete
    # ------------------------------------------------

    print("\n")
    print("====================================================")
    print("        ATMOGRAPH PIPELINE COMPLETED")
    print("====================================================")

    # ------------------------------------------------
    # Final Flow
    # ------------------------------------------------

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

    if nlp_success:

        print("GCN Ripple Prediction")
        print("   ↓")
        print("Predicted Delay + Predicted Risk")
        print("   ↓")
        print("Neo4j Updated")

    else:

        print("No Supply Chain Entity")
        print("   ↓")
        print("GCN Prediction Skipped")

    print("\n====================================================")


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    print("\n==============================================")
    print("       ATMOGRAPH SUPPLY CHAIN ANALYZER")
    print("==============================================")

    print("\nEnter supply chain disruption news.")

    print("Example:")
    print(
        "Rotterdam Port has been closed due to a severe "
        "operational disruption causing shipping delays."
    )

    print("\n----------------------------------------------")

    # ------------------------------------------------
    # User News Input
    # ------------------------------------------------

    news = input("\nEnter News: ").strip()

    # ------------------------------------------------
    # Validate Input
    # ------------------------------------------------

    if not news:

        print("\nERROR: News input cannot be empty.")

    else:

        run_complete_pipeline(news)
