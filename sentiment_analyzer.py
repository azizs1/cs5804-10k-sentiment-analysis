from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os, json, re

def main():
    sentiment_scores = {}

    # Look through all directories
    reports_dir = "10k_reports/"
    for folder_name in os.listdir(reports_dir):
        company_dir = os.path.join(reports_dir, folder_name)

        # Use the submissions.json to get company name and ticker symbol
        submissions_json = company_dir+"/submissions.json"
        with open(submissions_json, "r", encoding="utf-8") as file:
            submissions_dict = json.load(file)
        print(f"Processing {submissions_dict['name']} ({submissions_dict['tickers'][0]})")

        # Set up a dict where key is ticker, value is dict
        sentiment_scores[submissions_dict['tickers'][0].lower()] = {}

        for file in os.listdir(company_dir):
            if file.endswith(".txt"):
                # Add entry to dict where key is year, value is sentiment score
                year, score = calculate_sentiment(submissions_dict['tickers'][0], company_dir+"/"+file)
                sentiment_scores[submissions_dict['tickers'][0].lower()][str(year)] = score

    # Write scores to JSON file
    with open("sentiment_scores.json", "w") as file:
        json.dump(sentiment_scores, file, indent=4)

def calculate_sentiment(ticker, file_path):
    # Load FinBERT model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    # Read text from file
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Tokenize text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    # Run model inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Get predicted sentiment
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=1)[0]  # Get probabilities for each class

    # Extract individual probabilities
    # FinBERT uses three classes (negative, neutral, positive)
    p_negative = probabilities[0].item()
    p_neutral = probabilities[1].item()
    p_positive = probabilities[2].item()

    # Compute a sentiment score using weighted sums
    sentiment_score = (1 * p_positive) + (0 * p_neutral) + (-1 * p_negative)

    # Extract year for this report
    report_year = re.search(r'\d{4}', file_path).group()

    print(f"{ticker}: Sentiment Score for 10-K ({report_year}): {sentiment_score:.4f}")
    return report_year, sentiment_score

if __name__ == '__main__':
    main()