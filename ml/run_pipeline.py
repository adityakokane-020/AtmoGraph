import sys
from pathlib import Path



CURRENT_DIR = Path(__file__).resolve().parent

NLP_DIR = CURRENT_DIR / "nlp"
GNN_DIR = CURRENT_DIR / "gnn"

sys.path.append(str(CURRENT_DIR))
sys.path.append(str(NLP_DIR))
sys.path.append(str(GNN_DIR))


from reset_disruptions import reset_disruptions
from integration import run_pipeline
from neo4j_gcn_v2_integration import run_gcn_pipeline


def run_complete_pipeline(news):

    print("\n")
    print("====================================================")
    print("        ATMOGRAPH COMPLETE INTELLIGENCE PIPELINE")
    print("====================================================")

    print("\nINPUT NEWS:")
    print(news)

    # ======================================================
    # STEP 0 - RESET
    # ======================================================

    print("\n[STEP 0] RESETTING PREVIOUS DISRUPTIONS")

    reset_disruptions()

    # ======================================================
    # STEP 1 - NLP
    # ======================================================

    print("\n[STEP 1] STARTING NLP PIPELINE")

    nlp_result = run_pipeline(news)

    # ======================================================
    # CHECK NLP RESULT
    # ======================================================

    if not nlp_result["success"]:

        print("\n[STEP 2] GCN RIPPLE PREDICTION SKIPPED")

        print(
            "Reason: No supply chain entity was found."
        )

        return

    # ======================================================
    # STEP 2 - GCN V2
    # ======================================================

    print("\n[STEP 2] STARTING GCN V2 RIPPLE PREDICTION")

    run_gcn_pipeline(
        severity=nlp_result["severity"],
        disruption_type=nlp_result["disruption_type"]
    )

    print("\n====================================================")
    print("       ATMOGRAPH PIPELINE COMPLETED")
    print("====================================================")


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    news = (
    "Rotterdam Port is experiencing severe congestion "
    "and container backlog."
)
    

    run_complete_pipeline(news)