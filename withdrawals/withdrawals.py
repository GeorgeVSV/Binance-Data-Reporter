# Standard Python Libraries
import os
import time
import datetime
import logging

# Third-Party Libraries
import requests
import pandas as pd

# Cryptographic Libraries for Authentication
import hashlib
import hmac

# Fetch secrets
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
API_LOG_NAME = os.getenv('API_LOG_NAME')

# Constants for fetching
BASE_URL = os.getenv('BASE_URL')
ENDPOINT = os.getenv('WITHDRAWAL_HIST_ENPOINT')
URL = BASE_URL + ENDPOINT

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Helper functions
def convert_millisec_to_datetime(millisec: int) -> str:
    """Converts milliseconds to UTC datetime string in 'YYYY-MM-DD HH:MM:SS' format."""
    return datetime.datetime.fromtimestamp(millisec / 1000.0, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def convert_datetime_to_millsec(datetime_val: str) -> int:
    """Converts a UTC datetime string in 'YYYY-MM-DD HH:MM:SS' format to milliseconds."""
    return int(datetime.datetime.strptime(datetime_val, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)


def create_total_params(query_params: dict) -> str:
    """Generate a query string from a dictionary of parameters."""
    return '&'.join([f"{key}={value}" for key, value in query_params.items()])


def fetch_withdrawals(start_time: int, end_time: int) -> list[dict]:
    """Fetch withdrawals for the specified account's API KEY & time range.
    :param start_time: time in milliseconds from which withdrawals are fetched inclusively
    :param end_time: time in milliseconds before which withdrawals are fetched inclusively
    :return: list of dicts where each dict is a withdrawal
    """

    # Headers with API key
    headers = {
        'X-MBX-APIKEY': API_KEY
    }

    # Query parameters with start_time, end_time (based on 'applyTime' field) and timestamp
    query_params = {
        'startTime': start_time,  # Filters withdrawals where 'applyTime' >= start_time
        'endTime': end_time,      # Filters withdrawals where 'applyTime' <= end_time
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
        logger.critical(f"ERROR: Fetching withdrawals for account {API_LOG_NAME} failed with error: {e}")
        return []

    # Convert JSON to dict
    withdrawals = response.json()

    # Count withdrawals for logging
    withdrawals_cnt = len(withdrawals)

    # Define start_time and end_time for logs readability
    start_time_dt = convert_millisec_to_datetime(start_time)
    end_time_dt = convert_millisec_to_datetime(end_time)

    # Check response
    if withdrawals_cnt == 0:
        logger.warning(f"WARNING: For account {API_LOG_NAME}, there are NO withdrawals in the time range from {start_time_dt} to {end_time_dt}.")
    else:
        logger.info(f"SUCCESS: Fetched {withdrawals_cnt} withdrawals for account {API_LOG_NAME} in the time range from {start_time_dt} to {end_time_dt}.")
    return withdrawals


def process_withdrawals(withdrawals: list[dict]) -> pd.DataFrame:
    """Process raw withdrawals to a pandas DataFrame with additional formatting.
    This function fetches withdrawal data from the Binance API and processes it
    according to the official Binance documentation: 
    https://developers.binance.com/docs/wallet/capital/withdraw-history.

    :param withdrawals: A list of dictionaries representing raw withdrawals fetched 
                       from the Binance API's 'Withdraw History (USER_DATA)' method.
    :return: A pandas DataFrame containing processed withdrawal information.
    """

    # Withdrawals fetching prerequisites
    status_mapping = {
        0: 'Email Sent',
        2: 'Awaiting Approval',
        3: 'Rejected',
        4: 'Processing',
        6: 'Completed'
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
    current_utc_date = datetime.datetime.now(datetime.timezone.utc)

    # Convert list to Pandas DataFrame
    withdrawals_df = pd.DataFrame(withdrawals)

    # Map withdrawal statuses according to Binance official docs
    withdrawals_df['status_name'] = withdrawals_df['status'].map(status_mapping)

    # Map transfer type according to Binance official docs
    withdrawals_df['transfer_type_name'] = withdrawals_df['transferType'].map(transfer_type_mapping)

    # Map wallet type according to Binance official docs
    withdrawals_df['wallet_type_name'] = withdrawals_df['walletType'].map(wallet_type_mapping)

    # Set timestamp for logging analysis
    withdrawals_df['load_dttm'] = current_utc_date

    # Handle missing 'withdrawOrderId' column case
    if 'withdrawOrderId' not in withdrawals_df.columns:
        withdrawals_df['withdrawOrderId'] = pd.NA

    # Rename columns for consistent naming convention
    field_mapping = {
        'transactionFee': 'transaction_fee',
        'txId': 'tx_id',
        'applyTime': 'apply_time_dttm',
        'transferType': 'transfer_type',
        'confirmNo': 'confirm_no',
        'walletType': 'wallet_type',
        'txKey': 'tx_key',
        'completeTime': 'complete_time_dttm',
        'withdrawOrderId': 'withdraw_order_id'
    }

    # Rename columns
    withdrawals_df.rename(columns=field_mapping, inplace=True)

    # Reorder columns by grouping them into logical subgroups
    new_order = [
        'id', 'tx_id', 'address', 'tx_key',
        'network', 'coin', 'amount', 'transaction_fee',
        'transfer_type', 'transfer_type_name',
        'wallet_type', 'wallet_type_name',
        'status', 'status_name',
        'info', 'withdraw_order_id',
        'apply_time_dttm', 'complete_time_dttm', 'load_dttm'
    ]

    # Reorder columns
    withdrawals_df = withdrawals_df[new_order]

    return withdrawals_df
