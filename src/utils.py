# Standard Python Libraries
import datetime


# Helper functions
def convert_millisec_to_datetime(millisec: int) -> str:
    """Converts milliseconds to a UTC datetime string in 'YYYY-MM-DD HH:MM:SS' format.
    
    Intended for converting Binance API timestamps to a human-readable format.
    
    :param millisec: Time in milliseconds since the epoch.
    :return: Datetime string in UTC.
    
    Example:
        convert_millisec_to_datetime(1708869910000)  # Returns '2024-01-25 15:38:30'
    """
    return datetime.datetime.fromtimestamp(millisec / 1000.0, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def convert_datetime_to_millsec(datetime_val: str) -> int:
    """Converts a UTC datetime string in 'YYYY-MM-DD HH:MM:SS' format to milliseconds.
    
    Useful for creating timestamps compatible with Binance API.
    
    :param datetime_val: Datetime string in 'YYYY-MM-DD HH:MM:SS' format.
    :return: Time in milliseconds since the epoch.
    
    Example:
        convert_datetime_to_millsec('2024-01-25 15:38:30')  # Returns 1708869910000
    """
    return int(datetime.datetime.strptime(datetime_val, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)


def create_total_params(query_params: dict) -> str:
    """Generates a query string from a dictionary of parameters.
    
    Commonly used for creating query strings in API requests, such as Binance API calls.
    
    :param query_params: Dictionary of query parameters.
    :return: Encoded query string for URL.
    
    Example:
        create_total_params({'startTime': 1708869910000, 'endTime': 1709879910000})
        # Returns 'startTime=1708869910000&endTime=1709879910000'
    """
    return '&'.join([f"{key}={value}" for key, value in query_params.items()])
