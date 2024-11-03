"""
Withdrawals Module
This module handles fetching & processing operations related to withdrawals from the Binance API.
"""


from .withdrawals import (
    fetch_withdrawals,
    process_withdrawals,
)

__all__ = [
    'fetch_withdrawals',
    'process_withdrawals',
]
