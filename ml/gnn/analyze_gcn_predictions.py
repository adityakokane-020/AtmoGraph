import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

file_path = DATA_DIR / "gcn_test_predictions.csv"

df = pd.read_csv(file_path)

print("==============================================")
print("       ATMOGRAPH GCN PREDICTION ANALYSIS")
print("==============================================")

print("\nTotal Predictions:", len(df))

# Calculate error
df["error"] = df["predicted_delay"] - df["actual_delay"]
df["absolute_error"] = df["error"].abs()

# Overall metrics
mae = mean_absolute_error(
    df["actual_delay"],
    df["predicted_delay"]
)

rmse = mean_squared_error(
    df["actual_delay"],
    df["predicted_delay"]
) ** 0.5

print("\n===== Overall Results =====")
print("MAE :", round(mae, 3), "days")
print("RMSE:", round(rmse, 3), "days")

# Scenario-wise analysis
print("\n===== Scenario-wise Results =====")

scenario_results = (
    df.groupby("scenario_id")
    .agg(
        actual_delay_mean=("actual_delay", "mean"),
        predicted_delay_mean=("predicted_delay", "mean"),
        mae=("absolute_error", "mean")
    )
    .reset_index()
)

for _, row in scenario_results.iterrows():
    print(
        f"{row['scenario_id']} | "
        f"Actual Avg: {row['actual_delay_mean']:.2f} | "
        f"Predicted Avg: {row['predicted_delay_mean']:.2f} | "
        f"MAE: {row['mae']:.2f}"
    )

# Worst predictions
print("\n===== Top 10 Largest Prediction Errors =====")

worst = df.sort_values(
    "absolute_error",
    ascending=False
).head(10)

for _, row in worst.iterrows():
    print(
        f"{row['scenario_id']} | "
        f"Node Index: {int(row['node_index'])} | "
        f"Actual: {row['actual_delay']:.2f} | "
        f"Predicted: {row['predicted_delay']:.2f} | "
        f"Error: {row['absolute_error']:.2f}"
    )

# Best predictions
print("\n===== Top 10 Best Predictions =====")

best = df.sort_values(
    "absolute_error",
    ascending=True
).head(10)

for _, row in best.iterrows():
    print(
        f"{row['scenario_id']} | "
        f"Node Index: {int(row['node_index'])} | "
        f"Actual: {row['actual_delay']:.2f} | "
        f"Predicted: {row['predicted_delay']:.2f} | "
        f"Error: {row['absolute_error']:.2f}"
    )

# Save detailed results
output_file = DATA_DIR / "gcn_prediction_analysis.csv"

df.to_csv(
    output_file,
    index=False
)

print("\nDetailed analysis saved:")
print(output_file)

print("\n==============================================")
print("          ANALYSIS COMPLETE")
print("==============================================")
