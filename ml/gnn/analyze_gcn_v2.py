
import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "ml" / "data"

prediction_file = DATA_DIR / "gcn_v2_test_predictions.csv"
analysis_file = DATA_DIR / "gcn_v2_prediction_analysis.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(prediction_file)


print("==============================================")
print("       ATMOGRAPH GCN V2 PREDICTION ANALYSIS")
print("==============================================")


print("\nTotal Predictions:", len(df))


# ============================================================
# OVERALL RESULTS
# ============================================================

mae = mean_absolute_error(
    df["actual_delay"],
    df["predicted_delay"]
)

rmse = (
    mean_squared_error(
        df["actual_delay"],
        df["predicted_delay"]
    )
    ** 0.5
)


print("\n==============================================")
print("             OVERALL RESULTS")
print("==============================================")

print(
    f"\nMAE : {mae:.3f} days"
)

print(
    f"RMSE: {rmse:.3f} days"
)


# ============================================================
# SCENARIO-WISE RESULTS
# ============================================================

print("\n==============================================")
print("           SCENARIO-WISE RESULTS")
print("==============================================")


scenario_results = []


for scenario_id, group in df.groupby(
    "scenario_id"
):

    scenario_mae = mean_absolute_error(
        group["actual_delay"],
        group["predicted_delay"]
    )

    scenario_rmse = (
        mean_squared_error(
            group["actual_delay"],
            group["predicted_delay"]
        )
        ** 0.5
    )

    actual_avg = group[
        "actual_delay"
    ].mean()

    predicted_avg = group[
        "predicted_delay"
    ].mean()


    scenario_results.append({

        "scenario_id":
            scenario_id,

        "actual_avg":
            round(actual_avg, 3),

        "predicted_avg":
            round(predicted_avg, 3),

        "mae":
            round(scenario_mae, 3),

        "rmse":
            round(scenario_rmse, 3)
    })


scenario_df = pd.DataFrame(
    scenario_results
)


for _, row in scenario_df.iterrows():

    print(
        f"{row['scenario_id']} | "
        f"Actual Avg: {row['actual_avg']:.2f} | "
        f"Predicted Avg: {row['predicted_avg']:.2f} | "
        f"MAE: {row['mae']:.2f} | "
        f"RMSE: {row['rmse']:.2f}"
    )


# ============================================================
# TOP 10 LARGEST ERRORS
# ============================================================

print("\n==============================================")
print("        TOP 10 LARGEST PREDICTION ERRORS")
print("==============================================")


df["absolute_error"] = (
    df["actual_delay"]
    - df["predicted_delay"]
).abs()


largest_errors = df.sort_values(
    "absolute_error",
    ascending=False
).head(10)


for _, row in largest_errors.iterrows():

    print(
        f"{row['scenario_id']} | "
        f"Node: {row['node_id']} | "
        f"Actual: {row['actual_delay']:.2f} | "
        f"Predicted: {row['predicted_delay']:.2f} | "
        f"Error: {row['absolute_error']:.2f}"
    )


# ============================================================
# TOP 10 BEST PREDICTIONS
# ============================================================

print("\n==============================================")
print("          TOP 10 BEST PREDICTIONS")
print("==============================================")


best_predictions = df.sort_values(
    "absolute_error",
    ascending=True
).head(10)


for _, row in best_predictions.iterrows():

    print(
        f"{row['scenario_id']} | "
        f"Node: {row['node_id']} | "
        f"Actual: {row['actual_delay']:.2f} | "
        f"Predicted: {row['predicted_delay']:.2f} | "
        f"Error: {row['absolute_error']:.2f}"
    )


# ============================================================
# HIGH DELAY ANALYSIS
# ============================================================

print("\n==============================================")
print("            HIGH DELAY ANALYSIS")
print("==============================================")


high_delay = df[
    df["actual_delay"] >= 15
].copy()


print(
    "\nActual delays >= 15 days:",
    len(high_delay)
)


if len(high_delay) > 0:

    high_delay_mae = mean_absolute_error(
        high_delay["actual_delay"],
        high_delay["predicted_delay"]
    )

    print(
        f"High-delay MAE: "
        f"{high_delay_mae:.3f} days"
    )

    print("\nHigh-delay predictions:")

    for _, row in high_delay.iterrows():

        print(
            f"{row['scenario_id']} | "
            f"{row['node_id']} | "
            f"Actual: {row['actual_delay']:.2f} | "
            f"Predicted: {row['predicted_delay']:.2f} | "
            f"Error: {row['absolute_error']:.2f}"
        )


# ============================================================
# ZERO DELAY ANALYSIS
# ============================================================

print("\n==============================================")
print("             ZERO DELAY ANALYSIS")
print("==============================================")


zero_delay = df[
    df["actual_delay"] == 0
]


print(
    "\nActual zero-delay nodes:",
    len(zero_delay)
)


if len(zero_delay) > 0:

    zero_prediction_avg = (
        zero_delay["predicted_delay"]
        .mean()
    )

    print(
        "Average predicted delay "
        "for zero-delay nodes:",
        round(
            zero_prediction_avg,
            3
        )
    )


# ============================================================
# ERROR STATISTICS
# ============================================================

print("\n==============================================")
print("             ERROR STATISTICS")
print("==============================================")


print(
    "\nMaximum Error:",
    round(
        df["absolute_error"].max(),
        3
    ),
    "days"
)

print(
    "Average Error:",
    round(
        df["absolute_error"].mean(),
        3
    ),
    "days"
)

print(
    "Median Error:",
    round(
        df["absolute_error"].median(),
        3
    ),
    "days"
)


# ============================================================
# SAVE COMPLETE ANALYSIS
# ============================================================

df.to_csv(
    analysis_file,
    index=False
)


print("\n==============================================")
print("             ANALYSIS COMPLETE")
print("==============================================")

print("\nDetailed analysis saved to:")

print(analysis_file)
