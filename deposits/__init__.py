"""
Deposits Module
This module handles fetching & processing operations related to deposits from the Binance API.
"""


from .deposits import (
    fetch_deposits,
    process_deposits,
)

__all__ = [
    'fetch_deposits',
    'process_deposits',
]
