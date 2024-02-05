import yfinance as yf
import json
from datetime import datetime

# Define keywords that indicate a percentage field
percentage_keywords = ['percent', 'Percent', 'Yield', 'yield', 'payoutRatio', 'Margins', 'margins', 'To', 'On', 'Change']

# Helper function to convert Unix timestamps to human-readable dates
def timestamp_to_date(timestamp):
    try:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    except:
        return timestamp

# Helper function to format large numbers
def format_large_number(num):
    if num < 1000:
        return str(num)
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return f"{num:.2f}{['', 'K', 'M', 'B', 'T'][magnitude]}"

# Helper function to format percentages
def format_percentage(value):
    return f"{value * 100:.2f}%"

# Check if key indicates a percentage field
def is_percentage_field(key):
    return any(keyword in key for keyword in percentage_keywords)

# Function to fetch equity data and apply conversions
def fetch_equity_data(symbols):
    data = []  # Initialize as an empty list for the array structure
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Apply conversions for specific keys
        for key, value in info.items():
            if 'date' in key or 'Date' in key and isinstance(value, int):
                info[key] = timestamp_to_date(value)
            elif isinstance(value, (int, float)) and value >= 1000 and not is_percentage_field(key):
                info[key] = format_large_number(value)
            elif is_percentage_field(key) and isinstance(value, float):
                info[key] = format_percentage(value)

        # Directly append the info dictionary to the list
        data.append(info)
    return data

# Function to save data to a JSON file
def save_data_to_json(data, filename="output.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

symbols = ["AAPL", "GOOGL", "TSLA", "AMZN"]
equity_data = fetch_equity_data(symbols)
save_data_to_json(equity_data)
