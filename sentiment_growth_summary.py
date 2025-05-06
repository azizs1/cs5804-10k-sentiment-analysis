import json
import numpy as np

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def summarize():
    correlations = load_json("return_correlations.json")
    overall_corr = correlations.get("overall_correlation", None)
    per_ticker = correlations.get("per_ticker", {})

    # Filter NaNs
    filtered = {k: v for k, v in per_ticker.items() if isinstance(v, (float, int)) and not np.isnan(v)}
    sorted_positive = sorted(filtered.items(), key=lambda x: -x[1])[:5]
    sorted_negative = sorted(filtered.items(), key=lambda x: x[1])[:5]

    print("=== Sentiment-Growth Correlation Summary ===")
    if overall_corr is not None:
        print(f"Overall correlation across all companies: {overall_corr:.4f}\n")

    print("Top 5 companies with strongest positive correlation:")
    for ticker, corr in sorted_positive:
        print(f"  {ticker.upper():<6}: {corr:.3f}")

    print("\nTop 5 companies with strongest negative correlation:")
    for ticker, corr in sorted_negative:
        print(f"  {ticker.upper():<6}: {corr:.3f}")

if __name__ == "__main__":
    summarize()
