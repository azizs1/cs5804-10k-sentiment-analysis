import json
import numpy as np

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def summarize_to_json():
    correlations = load_json("return_correlations.json")
    overall_corr = correlations.get("overall_correlation", None)
    per_ticker = correlations.get("per_ticker", {})

    # Filter NaNs
    filtered = {k: v for k, v in per_ticker.items() if isinstance(v, (float, int)) and not np.isnan(v)}

    summary = {
        "overall_correlation": overall_corr,
        "per_ticker_correlation": filtered
    }

    with open("sentiment_growth_summary_output_all.json", "w") as f:
        json.dump(summary, f, indent=4)

    print("Summary written to sentiment_growth_summary_output_all.json")

if __name__ == "__main__":
    summarize_to_json()
