import os

# --- General Settings ---
BASE_URL = "https://tap.az"
MAX_ITEMS_TO_SCRAPE = 50 # Example limit
MIN_PRICE = 500
MAX_PRICE = 2500
IMPLICIT_WAIT_TIME = 10 # Seconds
SCROLL_PAUSE_TIME = 3   # Seconds
STOP_THRESHOLD = 20
COUNT_BEFORE_RESTART = 5

# --- Target Categories/Selectors ---
ELECTRONICS_CATEGORY_XPATH = "//a[@data-for = 'consumer-electronics']"
LAPTOP_SUBCATEGORY_KEYWORD = "noutbuk"
PRICE_DROPDOWN_XPATH = "//div[@class = 'filter-dropdown' and @id = 'price']"
MIN_PRICE_INPUT_XPATH = "//input[@class = 'string required form-control' and @id = 'price_lower']"
MAX_PRICE_INPUT_XPATH = "//input[@class = 'string required form-control' and @id = 'price_upper']"
NEW_FILTER_XPATH = "//div[@class = 'filter-dropdown' and @id = 'new']"
NEW_FILTER_OPTION_INDEX = 1 # Index for 'New' in the dropdown list
PRODUCT_LIST_SELECTOR = "#content > div > div > div.categories-products.js-categories-products > div.js-endless-container.products.endless-products"
PAGINATION_CLASS_CHECK = "pagination"

# --- Individual Product Page Selectors ---
PRODUCT_TITLE_XPATH = "//h1[@class = 'product-title']"
PROPERTIES_COLUMN_XPATH = "//div[@class = 'product-properties__column']"
LOCATION_XPATH = ".//span[@class = 'product-properties__i-value']" # Relative to properties column
COMPANY_TAG_NAME = "a" # Relative to properties column
OTHER_COMPANY_TEXT = "Digər"
PRICE_CONTAINER_XPATH = "//div[@class = 'product-price__i product-price__i--bold']"
PRICE_SPAN_TAG_NAME = "span" # Relative to price container
STATS_CONTAINER_XPATH = "//div[@class = 'product-info product-info__statistics']"
STATS_DIV_TAG_NAME = "div" # Relative to stats container
DATE_SPAN_TAG_NAME = "span" # Relative to the correct stats div
SELLER_TYPE_SELECTOR = "#js-lot-page > div > aside > div > div > div"
SELLER_TYPE_CLASS = "product-owner"
DESCRIPTION_XPATH = "//*[@id='js-lot-page']/div/main/section[3]/div/div/p"

# --- Output Settings ---
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output') # Example: Create an 'output' folder
CSV_FILENAME = "tapaz_laptops.csv"
EXCEL_FILENAME = "tapaz_laptops.xlsx"
DB_FILENAME = "tapaz_data.db" # Add this line
DATABASE_PATH = os.path.join(OUTPUT_DIR, DB_FILENAME) # Add this line


# --- Date Conversion ---
DATE_TODAY_AZ = "Bugün"
DATE_YESTERDAY_AZ = "Dünən"
MONTH_MAP_AZ = {
    "yanvar": "01", "fevral": "02", "mart": "03", "aprel": "04",
    "may": "05", "iyun": "06", "iyul": "07", "avqust": "08",
    "sentyabr": "09", "oktyabr": "10", "noyabr": "11", "dekabr": "12"
}

PROMPT_TEMPLATE = """
You are an expert in evaluating second-hand laptops for price and performance. Here is a list of laptop postings, each with a name, price, and description:

{POSTINGS}

Please do the following:
1. Rank these laptops from best to worst based on price/performance ratio, considering both the price and the specifications/features in the description.
2. For the top 3 laptops, explain in 1-2 sentences why you ranked them highest.
3. Only output the ranking (with names and prices) and the explanations for the top 3. Do not include any other commentary.

Format your answer as:

Ranking:
1. [Laptop Name] - [Price]
2. [Laptop Name] - [Price]
3. [Laptop Name] - [Price]
...

Explanations:
1. [Explanation for #1]
2. [Explanation for #2]
3. [Explanation for #3]
"""
