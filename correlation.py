import json
import os
import pandas as pd

with open("sentiment_scores.json", "r") as f:
    data = json.load(f)
    #print(data) #Testing output
    
rows = []
for ticker, year_dict in data.items():
    for year_str, score_val in year_dict.items():
        rows.append({
            "ticker": ticker,
            "year": int(year_str),
            "score": float(score_val)
        })

df_scores = pd.DataFrame(rows)
#print(df_scores) #Testing output


def merge_all_tickers(df_scores, folder_path="historical_data/nasdaq"):
    """
    df_scores: DataFrame with columns [ticker, year, score]
    folder_path: folder containing CSVs named 'HistoricalData_{ticker}.csv'
    
    Returns a DataFrame with stock info merged against df_scores for each ticker.
    """

    all_merged_dfs = []

    # For each ticker in df_scores
    for ticker in df_scores["ticker"].unique():
        # Build the path to that ticker's CSV
        csv_name = f"HistoricalData_{ticker}.csv"
        csv_path = os.path.join(folder_path, csv_name)

        # If no CSV found, skip
        if not os.path.exists(csv_path):
            print(f"File not found for ticker {ticker}: {csv_path}")
            continue

        # Read the CSV
        df_stock = pd.read_csv(csv_path)
        
        # Convert date column and extract year
        df_stock["Date"] = pd.to_datetime(df_stock["Date"], errors="coerce")
        df_stock["year"] = df_stock["Date"].dt.year
        
        # Filter scores to just this ticker
        df_scores_ticker = df_scores[df_scores["ticker"] == ticker]

        # Merge on 'year', adding the score to each row of stock data
        df_merged = pd.merge(
            df_stock,
            df_scores_ticker,  # e.g. columns: [ticker, year, score]
            on="year",
            how="left"
        )

        # Keep track of what ticker this is (in case needed for grouping after)
        df_merged["ticker"] = ticker
        
        all_merged_dfs.append(df_merged)

    # Concatenate all per‐ticker merges into one big DataFrame
    if all_merged_dfs:
        df_all = pd.concat(all_merged_dfs, ignore_index=True)
    else:
        # No data was merged, return empty
        df_all = pd.DataFrame()

    return df_all

# run merge
df_all = merge_all_tickers(df_scores, folder_path="historical_data/nasdaq")
#print(df_all) #Testing output

# Convert the "Close/Last" column from a string like "$xx.xx" to a float
df_all["Close/Last"] = (
    df_all["Close/Last"]
    .replace(r"[\$,]", "", regex=True)  # remove $ or commas
    .astype(float)                      # convert to float
)

# Group by ticker/year and compute means
df_yearly = df_all.groupby(["ticker", "year"], as_index=False).agg({
    "Close/Last": "mean",
    "score": "mean"
})

# Sort & shift so each row has "next year's close"
df_yearly.sort_values(["ticker", "year"], inplace=True)
df_yearly["NextYearClose"] = df_yearly.groupby("ticker")["Close/Last"].shift(-1)

# Compute forward return
df_yearly["forward_return"] = (
    df_yearly["NextYearClose"] - df_yearly["Close/Last"]
) / df_yearly["Close/Last"]

# Overall correlation for everything
corr_overall = df_yearly["score"].corr(df_yearly["forward_return"])
print("Overall correlation (score vs next-year return):", corr_overall)

# Ticker-by-ticker correlation
per_ticker_corr = {}

for ticker in df_yearly["ticker"].unique():
    df_t = df_yearly[df_yearly["ticker"] == ticker]
    if len(df_t) < 2:
        print(f"{ticker}: Not enough data for correlation")
        per_ticker_corr[ticker] = None  # or "Not enough data"
    else:
        corr_t = df_t["score"].corr(df_t["forward_return"])
        per_ticker_corr[ticker] = corr_t
        print(f"{ticker}: correlation = {corr_t}")

results_dict = {
    "overall_correlation": corr_overall,
    "per_ticker": per_ticker_corr
}

with open("return_correlations.json", "w") as f:
    json.dump(results_dict, f, indent=4)

print("Saved correlation results to return_correlations.json")
