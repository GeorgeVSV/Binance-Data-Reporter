# Standard Python Libraries
import os
import time
import datetime
import logging

# Third-Party Libraries
import requests
import pandas as pd

# Importing helper functions from utils
from utils import convert_millisec_to_datetime, create_total_params

# Cryptographic Libraries for Authentication
import hashlib
import hmac

# Fetch secrets
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
API_LOG_NAME = os.getenv('API_LOG_NAME')

# Constants for fetching
BASE_URL = os.getenv('BASE_URL')
ENDPOINT = os.getenv('DEPOSITS_HIST_ENDPOINT')
URL = BASE_URL + ENDPOINT

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def fetch_deposits(start_time: int, end_time: int) -> list[dict]:
    """Fetch deposits for the specified account's API KEY & time range.
    :param start_time: time in milliseconds from which deposits are fetched inclusively
    :param end_time: time in milliseconds before which deposits are fetched inclusively
    :return: list of dicts where each dict is a deposit
    """

    # Headers with API key
    headers = {
        'X-MBX-APIKEY': API_KEY
    }

    # Query parameters with start_time, end_time (based on 'insertTime' field) and timestamp
    query_params = {
        'startTime': start_time,  # Filters deposits where 'insertTime' >= start_time
        'endTime': end_time,      # Filters deposits where 'insertTime' <= end_time
        'timestamp': int(time.time() * 1000),  # Current timestamp in milliseconds
    }

    # Generate totalParams
    total_params = create_total_params(query_params)

    # Generate HMAC SHA256 signature
    signature = hmac.new(API_SECRET.encode('utf-8'), total_params.encode('utf-8'), hashlib.sha256).hexdigest()

    # Add signature to the query parameters
    query_params['signature'] = signature

    # Make the GET request with signed query parameters
    try:
        response = requests.get(url=URL, headers=headers, params=query_params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.RequestException as e:
        logger.critical(f"ERROR: Fetching deposits for account {API_LOG_NAME} failed with error: {e}")
        return []

    # Convert JSON to dict
    deposits = response.json()

    # Count deposits for logging
    deposits_cnt = len(deposits)

    # Define start_time and end_time for logs readability
    start_time_dt = convert_millisec_to_datetime(start_time)
    end_time_dt = convert_millisec_to_datetime(end_time)

    # Check response
    if deposits_cnt == 0:
        logger.warning(f"WARNING: For account {API_LOG_NAME}, there are NO deposits in the time range from {start_time_dt} to {end_time_dt}.")
    else:
        logger.info(f"SUCCESS: Fetched {deposits_cnt} deposits for account {API_LOG_NAME} in the time range from {start_time_dt} to {end_time_dt}.")
    return deposits


def process_deposits(deposits: list[dict]) -> pd.DataFrame:
    """Process raw deposits to a pandas DataFrame with additional formatting.
    This function fetches deposit data from the Binance API and processes it
    according to the official Binance documentation: 
    https://developers.binance.com/docs/wallet/capital/deposite-history.

    :param deposits: A list of dictionaries representing raw deposits fetched 
                       from the Binance API's 'Deposit History (USER_DATA)' method.
    :return: A pandas DataFrame containing processed deposit information.
    """

    # deposits fetching prerequisites
    status_mapping = {
        0: 'Pending',
        1: 'Success',
        2: 'Rejected',
        6: 'Credited But Cannot Withdraw',
        7: 'Wrong Deposit',
        8: 'Waiting User Confirm'
    }

    transfer_type_mapping = {
        0: 'External Transfer',
        1: 'Internal Transfer'
    }

    wallet_type_mapping = {
        0: 'Spot Wallet',
        1: 'Funding Wallet'
    }

    # Fetch current UTC datetime
    current_utc_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # Convert list to Pandas DataFrame
    deposits_df = pd.DataFrame(deposits)

    # Map deposit statuses according to Binance official docs
    deposits_df['status_name'] = deposits_df['status'].map(status_mapping)

    # Map transfer type according to Binance official docs
    deposits_df['transfer_type_name'] = deposits_df['transferType'].map(transfer_type_mapping)

    # Map wallet type according to Binance official docs
    deposits_df['wallet_type_name'] = deposits_df['walletType'].map(wallet_type_mapping)

    # Add insert_time in human readable format 'YYYY-MM-DD HH:MM:SS'
    deposits_df['insert_time_dttm'] = deposits_df['insertTime'].apply(convert_millisec_to_datetime)

    # Set timestamp for logging analysis
    deposits_df['load_dttm'] = current_utc_date


    # Rename columns for consistent naming convention
    field_mapping = {
        'txId': 'tx_id',
        'transferType': 'transfer_type',
        'confirmNo': 'confirm_no',
        'walletType': 'wallet_type',
        'addressTag': 'address_tag',
        'unlockConfirm': 'unlock_confirm',
        'confirmTimes': 'confirm_times',
        'insertTime': 'insert_time',
    }

    # Rename columns
    deposits_df.rename(columns=field_mapping, inplace=True)

    # Reorder columns by grouping them into logical subgroups
    new_order = [
        'id', 'tx_id', 'address', 'address_tag',
        'network', 'coin', 'amount',
        'transfer_type', 'transfer_type_name',
        'wallet_type', 'wallet_type_name',
        'status', 'status_name',
        'confirm_times', 'unlock_confirm',
        'insert_time', 'insert_time_dttm', 'load_dttm'
    ]
                 
    # Reorder columns
    deposits_df = deposits_df[new_order]

    return deposits_df
