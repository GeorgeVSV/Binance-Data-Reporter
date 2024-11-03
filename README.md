# Binance Data Reporter

**Binance Data Reporter** is a Python-based utility that enables streamlined extraction, transformation, and analysis of cryptocurrency transaction data (specifically withdrawals and deposits) from the Binance API. This project is crafted for modularity, allowing for clear separation of functionalities, easy extensibility, and reusable components.

## Project Structure

The project adheres to a modular structure that organizes scripts for transaction types while centralizing utility functions for easy maintenance.

```
Binance-Data-Reporter/
├── src/
│   ├── withdrawals.py           # Functions for fetching and processing withdrawal data
│   ├── deposits.py              # Functions for fetching and processing deposit data
│   ├── utils.py                 # Shared helper functions (e.g., timestamp conversion)
│   ├── __init__.py              # Initializes the module
├── .env                         # Stores environment variables
├── requirements.txt             # Python dependencies
├── .gitignore                   # Files and directories to ignore in version control
└── README.md                    # Project overview and usage guide
```

### Key Components

- **`withdrawals.py`**: Retrieves and formats Binance withdrawal transaction data.
- **`deposits.py`**: Retrieves and formats Binance deposit transaction data.
- **`utils.py`**: Contains reusable helper functions, such as:
  - `convert_millisec_to_datetime`: Converts timestamps from milliseconds to UTC datetime strings.
  - `convert_datetime_to_millsec`: Converts UTC datetime strings to milliseconds.
  - `create_total_params`: Creates URL query strings from parameter dictionaries.

## Setup Instructions

### Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **Binance API Key and Secret**: Required to authenticate and access Binance data endpoints.

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/GeorgeVSV/Binance-Data-Reporter.git
   cd Binance-Data-Reporter
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate     # On Windows, use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory and add your Binance API credentials:
   ```
   API_KEY=your_api_key_here
   API_SECRET=your_api_secret_here
   API_LOG_NAME =your_api_login_name_here
   BASE_URL = 'https://api.binance.com'
   WITHDRAWAL_HIST_ENPOINT = '/sapi/v1/capital/withdraw/history'
   DEPOSITS_HIST_ENDPOINT = '/sapi/v1/capital/deposit/hisrec'
   ```

## Usage

To run the scripts for fetching withdrawal or deposit data, execute the following commands:

- For Withdrawals:
   ```bash
   python src/withdrawals.py
   ```

- For Deposits:
   ```bash
   python src/deposits.py
   ```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
