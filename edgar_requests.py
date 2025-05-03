import requests
import json
import time
import string
import os
import argparse
from bs4 import BeautifulSoup

# Header to use when sending requests to EDGAR
headers = {
    'User-Agent': ''
}

# Fortune 50 tickers
tickers = ['wmt', 'amzn', 'aapl', 'unh', 'brka', 'cvs', 'xom',
        'googl', 'mck', 'cor', 'cost', 'jpm', 'msft', 'cah',
        'cvx', 'ci', 'f', 'bac', 'gm', 'elv', 'c', 'cnc',
        'hd', 'mpc', 'kr', 'psx', 'fnma', 'wba', 'vlo', 'meta',
        'vz', 't', 'cmcsa', 'wfc', 'gs', 'fmcc', 'tgt', 'hum',
        'tsla', 'ms', 'jnj', 'adm', 'pep', 'ups', 'fdx', 'dis',
        'dell', 'low', 'pg', 'et']

def main():

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Download 10-K reports for specific companies using EDGAR API.')

    parser.add_argument('--email', '-e', type=str, required=True,
                        help='Your email address to be used in the User-Agent header.')
    parser.add_argument('--refresh', '-r', action='store_true',
                        help='Refresh the tickers.json file. (if it exists and you believe it is out of date)')
    ticker_group = parser.add_mutually_exclusive_group()
    ticker_group.add_argument('--tickers_file', '-tf', type=str, default='resources/tickers.txt',
                        help='Path to the file containing the per-line list of tickers. (if not using the default list)')
    ticker_group.add_argument('--ticker', '-t', type=str, 
                        help='Single ticker to download 10-K reports for. (if not using the default list)')
    
    args = parser.parse_args()

    # Set the User-Agent header with the provided email
    headers['User-Agent'] = f'10KSentimentAnalysisProject/1.0 ({args.email})'

    # Use the SEC provided json to get CIKs
    company_tickers = retrieve_tickers(refresh=args.refresh)

    # Load single ticker, load from file, or use default list
    if args.ticker:
        tickers = [args.ticker.lower()]
    elif os.path.exists(args.tickers_file):
        with open(args.tickers_file, 'r') as file:
            tickers = [line.strip().lower() for line in file.readlines()]
    else:
        tickers = tickers

    # Store left-padded CIKs for each of our tickers as well as names
    companies = {}
    for company in company_tickers.values():
        if company['ticker'].lower() in tickers:
            companies[company['ticker'].lower()] = {}
            companies[company['ticker'].lower()]['cik'] = str(company['cik_str']).zfill(10)
            companies[company['ticker'].lower()]['name'] = company['title'].translate(str.maketrans('', '', string.punctuation)).lower().replace(' ','_')

    # Make requests to get all submissions for each company
    retrieve_10k(companies)

def retrieve_tickers(refresh=False):
    # Check if the tickers file exists and is not empty
    if os.path.exists('resources/edgar_tickers.json') and os.path.getsize('resources/edgar_tickers.json') > 0 and not refresh:
        with open('resources/edgar_tickers.json', 'r') as file:
            company_tickers = json.loads(file.read())
    else:
        # If the file doesn't exist or is empty, fetch the tickers
        # Use the SEC provided json to get CIKs
        url = 'https://www.sec.gov/files/company_tickers.json'
        response = requests.get(url, headers=headers)
        company_tickers = json.loads(response.text)
        with open('resources/edgar_tickers.json', 'w') as file:
            file.write(json.dumps(company_tickers, indent=4))

    return company_tickers

def retrieve_10k(companies):
    # Make requests to get all submissions for each company
    for ticker, company in companies.items():
        url = f'https://data.sec.gov/submissions/CIK{company['cik']}.json'
        print("Retrieving submissions for: ", company['name'])
        print(url)
        response = requests.get(url, headers=headers)
        
        submissions_dict = response.json()
        dir_path = f'10k_reports/{company['name']}/'

        # Create directory path for this company if it does not exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # Likely won't have to use this file, but saving it just in case
        with open(dir_path+'submissions.json', 'w') as file:
            json.dump(submissions_dict, file, indent=4)

        for idx, form in enumerate(submissions_dict['filings']['recent']['form']):
            if form == '10-K':
                accession_number = submissions_dict['filings']['recent']['accessionNumber'][idx]
                filename = submissions_dict['filings']['recent']['primaryDocument'][idx]

                url = f'https://www.sec.gov/Archives/edgar/data/{company['cik']}/{accession_number.replace('-', '')}/{filename}'
                response = requests.get(url, headers=headers)
                time.sleep(0.5)

                date = submissions_dict['filings']['recent']['reportDate'][idx].replace('-','_')
                file_10k = ticker+'_'+date
                print("Retrieving: ", file_10k)

                # Save the htm file locally
                with open(dir_path+file_10k+'.htm', 'wb') as file:
                    file.write(response.content)
                time.sleep(0.5)

                with open(dir_path+file_10k+'.htm', 'r', encoding='utf-8') as file:
                    html_content = file.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract plain text
                plain_text = soup.get_text()

                # Save the plain text to a new file
                with open(dir_path+file_10k+'.txt', 'w', encoding='utf-8') as file:
                    file.write(plain_text)


if __name__ == '__main__':
    main()