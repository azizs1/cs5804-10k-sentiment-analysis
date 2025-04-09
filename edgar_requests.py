import requests
import json
import ast
import time
from bs4 import BeautifulSoup

# what we want to do is use the txt file here https://www.sec.gov/about/webmaster-frequently-asked-questions#developers
# use stock api to download tickers for top 50 companies and use txt file to map to cik
# loop through and download the submissions json for each of these companies
# make sure u add a sleep for 5 seconds after each request to avoid being rate-limited.
# we only need to do all this once and then save it in a folder in the repo

# THIS CODE IS USED TO DOWNLOAD SUBMISSION DETAILS FOR MICROSOFT
# SEE ms_info.txt for what this looks like
# url = "https://data.sec.gov/submissions/CIK0000789019.json"

# headers = {
#     "User-Agent": "10KSentimentAnalysisProject/1.0 (azizs@vt.edu)"
# }

# response = requests.get(url, headers=headers)

# # Print the JSON data
# print(response.json())


# Read and parse the data
with open("ms_info.txt", 'r') as file:
    dict_data = ast.literal_eval(file.read())  # Safely evaluate the dictionary

# Access specific fields
cik = dict_data['cik']
name = dict_data['name']
sic_description = dict_data['sicDescription']

print(f"CIK: {cik}")
print(f"Name: {name}")
print(f"SIC Description: {sic_description}")
print(dict_data['filings']['recent'].keys())
# print(dict_data['filings']['recent']['primaryDocument'])
for idx, form in enumerate(dict_data['filings']['recent']['form']):
    if form == "10-K":
        accession_number = dict_data['filings']['recent']['accessionNumber'][idx]
        filename = dict_data['filings']['recent']['primaryDocument'][idx]
        print('--------')
        print(f"Accession Number: {accession_number}")
        print(f"Report Date: {dict_data['filings']['recent']['reportDate'][idx]}")
        print(f"Form Type: {dict_data['filings']['recent']['form'][idx]}")
        print(f"File Name: {filename}")

        # commented out since it makes requests
        # url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace("-", "")}/{filename}"

        # headers = {
        #     "User-Agent": "10KSentimentAnalysisProject/1.0 (azizs@vt.edu)"
        # }

        # response = requests.get(url, headers=headers)

        # # Save the file locally
        # with open(filename, "wb") as file:
        #     file.write(response.content)
        # time.sleep(5)

        with open(filename, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract plain text
        plain_text = soup.get_text()

        # Save the plain text to a new file
        with open(filename.replace("htm", "txt"), "w", encoding="utf-8") as file:
            file.write(plain_text)