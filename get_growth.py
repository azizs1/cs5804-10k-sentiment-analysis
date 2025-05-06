import requests
import json
import time
import string
import os
import argparse
from bs4 import BeautifulSoup
from collections import defaultdict

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

    # Parse through resources/edgar_tickers.json to get CIKs
    company_ciks = []
    i = 0
    with open('resources/edgar_tickers.json', 'r') as file:
        company_tickers = json.load(file)
        for company in company_tickers.values():
            # If it's one of the fortune 50 tickers, add it to the list
            if company['ticker'].lower() in tickers:
                cik = company['cik_str']
                # Left pad the CIK with zeros to make it 10 digits long
                padded_cik = str(cik).zfill(10)
                company_ciks.append(padded_cik)

    get_facts(company_ciks)

def get_facts(company_ciks):
    # Get the ciks for the tickers
    # Get the company facts using:
    #     companyFacts = requests.get(f'https://data.sec.gov/api/xbrl/company_facts/{cik}').json'
    #     , headers=headers)
    # For each company, it will be in the following format:
    #    companyFacts.json()['facts']['us-gaap']['Assets']['units']['USD']
    #    companyFacts.json()['facts']['us-gaap']['Revenues']['units']['USD']

    # JSON object to hold the growth data
    all_growth_data = {}

    # Loop through the ciks
    for cik in company_ciks:
        # This holds all of the financial data for the company over a number of years
        companyFacts = requests.get(
            f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',
            headers=headers
        )

        # Check if the request was successful
        try:
            # Get the revenue data from the response
            data = companyFacts.json()['facts']['us-gaap']['Revenues']['units']['USD']

            print(f'Company CIK: {cik}')
            annual_revenue = defaultdict(int)
            quarterly_counts = defaultdict(int)

            # Loop through the data and sum the revenue for each year
            for entry in data:
                # If the entry has an accessible 'frame' key, use it to get the year
                try:
                    # Sum up the quarterly revenue for each year
                    if entry['frame'].startswith('CY') and (entry['form'] == '10-K' or entry['form'] == '10-Q') and len(entry['frame']) == 8:
                        annual_revenue[int(entry['frame'][2:6])] += entry['val']
                        quarterly_counts[int(entry['frame'][2:6])] += 1
                    # # If the company posted yearly revenue, use that instead
                    elif entry['frame'].startswith('CY') and len(entry['frame']) == 6 and entry['form'] == '10-K':
                        annual_revenue[int(entry['frame'][2:])] += (entry['val'] / 4)
                        quarterly_counts[int(entry['frame'][2:])] += 1

                except (KeyError, TypeError):
                    # print(f"Error processing entry")
                    continue


            # Get the average quarterly revenue for each year
            average_quarterly_revenue = {}
            for year in annual_revenue:
                if quarterly_counts[year] > 0:  # Avoid division by zero
                    average_quarterly_revenue[year] = annual_revenue[year] / quarterly_counts[year]

            # Sort the years in ascending order
            sorted_years = sorted(average_quarterly_revenue.keys())


            # Calculate the compound annual growth rate (CAGR) for each period
            cagr_results = {}
            for i in range(1, len(sorted_years)):
                # start_year = sorted_years[i - 1]
                # end_year = sorted_years[i]
                # start_val = annual_revenue[start_year]
                # end_val = annual_revenue[end_year]
                # years_diff = end_year - start_year
                # cagr = (end_val / start_val) ** (1 / years_diff) - 1
                # cagr_results[end_year] = cagr
                
                # ((New revenue - Old Revenue) / Old Revenue) * 100
                # Is also adjusted for potential gaps between years
                cagr_results[sorted_years[i]] = ((average_quarterly_revenue[sorted_years[i]] - average_quarterly_revenue[sorted_years[i - 1]]) / average_quarterly_revenue[sorted_years[i - 1]]) / (sorted_years[i] - sorted_years[i - 1])


            # Print results
            for period, growth in cagr_results.items():
                print(f"Composite annual growth (CAGR) from {period} for {cik}: {growth:.2%}")

            # Put the results into a JSON file
            all_growth_data[cik] = cagr_results

        except (KeyError, TypeError):
            all_growth_data[cik] = {"Error" : "Could not be read due to lack of revenue data."}
            print(f"Error processing CIK {cik}")
            continue

        # Write all growth data to a JSON file
        with open("growth.json", "w") as f:
            json.dump(all_growth_data, f, indent=4)



if __name__ == '__main__':
    main()