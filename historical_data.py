"""
historical_data.py
==========================

This module retrieves historical stock data from the Polygon.io API
and exports it to CSV format.

Polygon.io API has a free tier that allows for 5 requests per minute
and 20 requests per day and 2 years of historical data. 
This module is designed to work within these limits.

Example:
    $ python polygon_historical_data.py AAPL 2020-01-01 2023-01-01 day

Dependencies:
    - polygon-api-client
    - pandas
    - datetime
    - os
"""

from polygon import RESTClient
import pandas as pd
from datetime import datetime
import os
import argparse

def main():

    # Set up the Polygon API client
    client = setup_client()

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Download historical stock data from Polygon.io API.')
    parser.add_argument('--ticker', '-t', type=str, required=True,
                        help='Ticker symbol of the stock to download data for.')
    parser.add_argument('--from_date', '-fd', type=str, required=False, default='2023-01-01',
                        help='Start date for historical data in YYYY-MM-DD format. (ex: 2024-01-01)')
    parser.add_argument('--to_date', '-td', type=str, required=False, default='2025-01-01',
                        help='End date for historical data in YYYY-MM-DD format. (ex: 2024-01-01)')
    parser.add_argument('--timespan', '-ts', type=str, required=False, default='week',
                        help='Timespan for historical data (can be minute, hour, day, week, month, quarter, year).')
    args = parser.parse_args()
    ticker = args.ticker
    from_date = args.from_date
    to_date = args.to_date
    timespan = args.timespan


    # Check if the ticker symbol is valid
    if not ticker.isalpha() or len(ticker) < 1 or len(ticker) > 5:
        raise ValueError("Invalid ticker symbol. Please enter a valid ticker symbol.")
    # Check if the dates are in the correct format
    try:
        datetime.strptime(from_date, '%Y-%m-%d')
        datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Please enter dates in YYYY-MM-DD format.")
    # Check if the timespan is valid
    valid_timespans = ['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']
    if timespan not in valid_timespans:
        raise ValueError(f"Invalid timespan. Please enter one of the following: {', '.join(valid_timespans)}.")
    # Check if the from_date is before the to_date
    if from_date > to_date:
        raise ValueError("Invalid date range. The from_date must be before the to_date.")

    # Set up the directory for historical data
    aggs = []


    # Retrieve historical data from Polygon.io API
    for a in client.list_aggs(
        ticker.upper(),           # ticker symbol
        1,                        # multiplier
        timespan,                 # timespan (can be minute, hour, day, week, month, quarter, year)
        from_date,                # from date
        to_date,                  # to date
        limit=50000,              # limit of results
    ):
        aggs.append(a)


    # Convert each agg object to a dict and create a list of dicts
    data = []
    for agg in aggs:
        # Get all attributes from the agg object
        agg_dict = {key: getattr(agg, key) for key in dir(agg) 
                    if not key.startswith('_') and not callable(getattr(agg, key))}
        
        # Convert timestamp to datetime if needed
        if 'timestamp' in agg_dict and isinstance(agg_dict['timestamp'], int):
            agg_dict['timestamp'] = datetime.fromtimestamp(agg_dict['timestamp']/1000)
        
        data.append(agg_dict)

    dir_path = 'historical_data/polygon/'

    # Create directory path for historical data if it does not exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Create DataFrame and export to CSV
    df = pd.DataFrame(data)
    df.to_csv(dir_path + f'HistoricalData_{ticker.lower()}.csv', index=False)

def setup_client():
    """
    Set up the Polygon.io REST client with the API key.
    """

    # Check if os linux or check resources for api key file
    if os.name == 'posix':
        API_KEY = os.environ.get("POLYGON_API_KEY")
    else:
        # Set up the Polygon API client
        if not os.path.exists('resources/polygon_api_key.txt'):
            raise ValueError("Please create a file named 'polygon_api_key.txt' in the 'resources' " \
            "directory with your Polygon API key or set as environment variable 'POLYGON_API_KEY'.")
        else:
            with open('resources/polygon_api_key.txt', 'r') as file:
                API_KEY = file.read

    if not API_KEY:
        raise ValueError("Please set the POLYGON_API_KEY environment variable or create a " \
        "file named 'polygon_api_key.txt' in the 'resources' directory with your Polygon API key.")
    
    client = RESTClient(API_KEY)

    return client


if __name__ == "__main__":
    main()