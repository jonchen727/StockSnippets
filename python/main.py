import yfinance as yf
import json
from datetime import datetime
import time
import pycountry
import os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# Set the URL you want to scrape from
url = 'https://finviz.com/groups.ashx?g=industry&v=120'

# Create a request object with a User-Agent header
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

# Open the URL and read the response content into a variable
response = urlopen(req)

# Read the response content and decode it (if needed)
content = response.read().decode('utf-8')

# Use BeautifulSoup to parse the HTML content
soup = BeautifulSoup(content, 'html.parser')
avg_pe = {}
#print(response)
table = soup.find('table', class_="styled-table-new is-medium is-rounded is-tabular-nums w-full groups_table")
if table:
    # Loop through each row in the table, skipping the header row
    for row in table.find_all('tr')[1:]:
        # Extract the columns (cells) in the row
        columns = row.find_all('td')
        if len(columns) >= 3:  # Ensure there are enough columns for industry, PE ratio, and number of companies
            industry = columns[1].text.strip()
            pe_ratio = columns[4].text.strip()
            # Optionally, you can also extract the number of companies
            # number_of_companies = columns[2].text.strip()
            
            # Add the extracted data to the dictionary
            avg_pe[industry] = pe_ratio
else:
    print("Table not found")
#print(avg_pe)

# Define keywords that indicate a percentage field
percentage_keywords = ['percent', 'Percent', 'Yield', 'yield', 'payoutRatio', 'Margins', 'margins',
                        'returnOnEquity', 'returnOnAssets', 'profitMargins', 'Change']
formatted_percent_keywords = ['debtToEquity', 'fiveYearAvgDividendYield']
price_keywords = ['fiftyTwoWeek', 'price', 'bid', 'ask']

exchange_dict = {
    "NMS": 'NASDAQ', 
    "NCM": 'NASDAQ',
    "NGM": 'NASDAQ',
    "NYQ": 'NYSE', 
    "PNK": 'OTC'
}

def load_database_data(filename="human.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

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

def format_price(value):
    return f"{value:.2f}"
# Helper function to add suffix to formatted percents
def add_percent_suffix(value):
    return f"{value}%"

def is_price_field(key):
    return any(keyword in key for keyword in price_keywords)

def is_percent_suffix_field(key):
    return any(keyword in key for keyword in formatted_percent_keywords)

# Check if key indicates a percentage field
def is_percentage_field(key):
    return any(keyword in key for keyword in percentage_keywords)

# Check if key indicates a price field
def is_price_field(key):
    return any(keyword in key for keyword in price_keywords)


# Function to fetch equity data and apply conversions
def fetch_equity_data(symbols, database):
    data = []  # Initialize as an empty list for the array structure
    updated = False
    for symbol in symbols:
        if symbol in database:
            # Use existing data
            info = database[symbol]
        else:
            # Fetch new data
            ticker = yf.Ticker(symbol)
            time.sleep(1)
            database[symbol] = ticker.info
            info = ticker.info.copy()
            updated = True

        # Apply conversions for specific keys
        for key, value in info.items():
            if 'date' in key or 'Date' in key and isinstance(value, int):
                info[key] = timestamp_to_date(value)
            elif isinstance(value, (int, float)) and value >= 1000 and not (is_percentage_field(key) or is_price_field(key)):
                info[key] = format_large_number(value)
            elif is_percent_suffix_field(key) and isinstance(value, float):
                info[key] = add_percent_suffix(value)
            elif is_percentage_field(key) and isinstance(value, float):
                info[key] = format_percentage(value)
            elif is_price_field(key) and isinstance(value, float):
                info[key] = format_price(value)
            elif isinstance(value, float):
                info[key] = f"{value:.2f}"


        # Check if 'sector' exists in info and create sectorIcon URL
        if 'sector' in info:
            formatted_sector = info['sector'].replace(" ", "").lower()
            sector_icon_url = f"https://raw.githubusercontent.com/jonchen727/StockSnippets/cdc402e3eb1ffbf064ca84dbed5598e121a312cc/icons/sector/{formatted_sector}.svg"
            info['sectorIcon'] = sector_icon_url
        if 'country' in info: 
            code = pycountry.countries.search_fuzzy(info['country'])[0].alpha_2
            flag_url = f"https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{code.lower()}.svg"
            info['flag'] = flag_url
        if 'exchange' in info:
            info['exchange_name'] = exchange_dict.get(info['exchange'], info['exchange'])
        if 'industry' in info:
            info['industry_pe'] = avg_pe.get(info['industry'], "N/A")

        # Directly append the info dictionary to the list
        data.append(info)
    return data, database, updated

# Function to save data to a JSON file
def save_data_to_json(data, filename="output.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

database = load_database_data("database.json")

symbols = ["AAPL", "GOOGL", "TSLA", "AMZN","BA", "AVGO", "TSM", "PBR", "QQQ"]
equity_data, database, updated = fetch_equity_data(symbols, database)
save_data_to_json(equity_data, "output.json")

if updated:
    save_data_to_json(database, "database.json")


