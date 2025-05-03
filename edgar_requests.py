import requests
import json
import time
import string
import os
from bs4 import BeautifulSoup

# Header to use when sending requests to EDGAR
headers = {
    "User-Agent": "10KSentimentAnalysisProject/1.0 (azizs@vt.edu)"
}

# Fortune 35 tickers
tickers = ["wmt", "amzn", "aapl", "unh", "brka", "cvs", "xom",
           "googl", "mck", "cor", "cost", "jpm", "msft", "cah",
           "cvx", "ci", "f", "bac", "gm", "elv", "c", "cnc",
           "hd", "mpc", "kr", "psx", "fnma", "wba", "vlo", "meta",
           "vz", "t", "cmcsa", "wfc", "gs"]

# Use the SEC provided json to get CIKs
with open('misc/company_tickers.json', 'r') as file:
    company_tickers = json.load(file)

# Store left-padded CIKs for each of our tickers as well as names
companies = {}
for company in company_tickers.values():
    if company['ticker'].lower() in tickers:
        companies[company['ticker'].lower()] = {}
        companies[company['ticker'].lower()]['cik'] = str(company['cik_str']).zfill(10)
        companies[company['ticker'].lower()]['name'] = company['title'].translate(str.maketrans('', '', string.punctuation)).lower().replace(' ','_')

# Make requests to get all submissions for each company
for ticker, company in companies.items():
    url = f"https://data.sec.gov/submissions/CIK{company['cik']}.json"
    print(url)
    response = requests.get(url, headers=headers)
    
    submissions_dict = response.json()
    dir_path = f"10k_reports/{company['name']}/"

    # Create directory path for this company if it does not exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    # Likely won't have to use this file, but saving it just in case
    with open(dir_path+"submissions.json", 'w') as file:
        json.dump(submissions_dict, file, indent=4)

    for idx, form in enumerate(submissions_dict['filings']['recent']['form']):
        if form == "10-K":
            accession_number = submissions_dict['filings']['recent']['accessionNumber'][idx]
            filename = submissions_dict['filings']['recent']['primaryDocument'][idx]

            url = f"https://www.sec.gov/Archives/edgar/data/{company['cik']}/{accession_number.replace("-", "")}/{filename}"
            response = requests.get(url, headers=headers)
            time.sleep(0.5)

            date = submissions_dict['filings']['recent']['reportDate'][idx].replace('-','_')
            file_10k = ticker+'_'+date
            print(file_10k)

            # Save the htm file locally
            with open(dir_path+file_10k+'.htm', "wb") as file:
                file.write(response.content)
            time.sleep(0.5)

            with open(dir_path+file_10k+'.htm', "r", encoding="utf-8") as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, "html.parser")

            # Extract plain text
            plain_text = soup.get_text()

            # Save the plain text to a new file
            with open(dir_path+file_10k+'.txt', "w", encoding="utf-8") as file:
                file.write(plain_text)