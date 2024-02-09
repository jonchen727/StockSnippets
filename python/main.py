import yfinance as yf
import json
from datetime import datetime
import time
import pycountry
import os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import cairosvg
from vertex import summarize
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-quarter", "--quarter", dest = "quarter", default="Q#-YY", help="Quarter and Year i.e. Q1-24" )
args = parser.parse_args

# Set python script path
script_path = os.path.dirname(os.path.abspath(__file__))
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
    "PNK": 'OTC',
    "PXC": 'NYSE'
}

def load_database_data(filename="database.json"):
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
def fetch_data(symbols, database, quarter, kind):
    data = []  # Initialize as an empty list for the array structure
    if quarter not in database:
        database[quarter] = {}
    if kind not in database[quarter]:
        database[quarter][kind] = {}
    kind_database = database[quarter][kind]
    updated = False
    for symbol in symbols:
        time.sleep(1)
        if symbol in kind_database:
            # Use existing data
            info = kind_database[symbol]
            print("Using Data from Database for", symbol)
        else:
            # Fetch new data
            ticker = yf.Ticker(symbol)
            kind_database[symbol] = ticker.info
            info = ticker.info.copy()
            print("Not in Database Fetching Data for", symbol)
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
            sector_icon_path = os.path.abspath(os.path.join(script_path, '..', 'icons', 'sector'))
            cairosvg.svg2png(url=f"{sector_icon_path}/{formatted_sector}.svg" , write_to=f"{sector_icon_path}/{formatted_sector}.png")
            info['svgSectorIcon'] = f"https://raw.githubusercontent.com/jonchen727/StockSnippets/main/icons/sector/{formatted_sector}.svg"
            info['pngSectorIcon'] = f"https://raw.githubusercontent.com/jonchen727/StockSnippets/main/icons/sector/{formatted_sector}.png"
        if 'country' in info: 
            code = pycountry.countries.search_fuzzy(info['country'])[0].alpha_2
            flag_icon_path = os.path.abspath(os.path.join(script_path, '..', 'icons', 'flags'))
            cairosvg.svg2png(url=f"https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{code.lower()}.svg", write_to=f"{flag_icon_path}/{code.lower()}.png")
            info['svg_flag'] = f"https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{code.lower()}.svg"
            info['png_flag'] = f"https://raw.githubusercontent.com/jonchen727/StockSnippets/main/icons/flags/{code.lower()}.png"
        if 'exchange' in info:
            info['exchange_name'] = exchange_dict.get(info['exchange'], info['exchange'])
        if 'industry' in info:
            info['industry_pe'] = avg_pe.get(info['industry'], "N/A")
        if 'longBusinessSummary' in info:
            info['summary'] = summarize(info['longBusinessSummary'], max_output_tokens=128)

        info['quarter'] = quarter
        # Directly append the info dictionary to the list
        data.append(info)
    return data, database, updated

# Function to save data to a JSON file
def save_data_to_json(data, filename="output.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

if os.path.exists("input.json"):
    with open("input.json", "r") as file:
        input = json.load(file)


database = load_database_data("database.json")

for key in input.keys():
    for kind in input[key].keys():
        symbols = input[key][kind]
        data, database, updated = fetch_data(symbols, database, key, kind)
        save_data_to_json(data, f"outputs/{key}-{kind}-output.json")

if updated:
    save_data_to_json(database, "database.json")


