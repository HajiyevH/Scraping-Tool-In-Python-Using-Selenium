import os

# --- General Settings ---
BASE_URL = "https://tap.az"
MAX_ITEMS_TO_SCRAPE = 2000 # Example limit
MIN_PRICE = 300
MAX_PRICE = 7000
IMPLICIT_WAIT_TIME = 10 # Seconds
SCROLL_PAUSE_TIME = 3   # Seconds
STOP_THRESHOLD = 10000
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
DESCRIPTION_XPATH = "//*[@id='js-lot-page']/div/main/section[3]/div/div[1]"

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

PROMPT_TEMPLATE ="""You are an expert at extracting laptop hardware specifications from product listings. 

Given the following laptop information:
Full Name: {full_name}
Description: {description}

Extract the following fields as accurately as possible:
- cpu
- gpu
- ram
- storage
- screen_size
- brand
- model
- gpu_power_consumption (in watts, if possible)

Instructions:
1. Use both the "Full Name" and "Description" fields to extract each value.
2. If a value is explicitly stated in the text, use it and add "-D" to the value (for example: "i7-11370-D").
3. If a value is not stated but you can confidently predict it based on your knowledge or by searching the internet, use your best prediction and add "-P" to the value (for example: "i7-11370-P").
4. If you cannot determine a value, return "Unknown".
5. For gpu_power_consumption, estimate the typical wattage for the GPU model if not given, and use the same "-D" or "-P" suffix rules.
6. Output the result as a JSON object with keys: cpu, gpu, ram, storage, screen_size, brand, model, gpu_power_consumption.

Example output:
{{
  "cpu": "i7-11370-D",
  "gpu": "RTX 3060-P",
  "ram": "16GB-D",
  "storage": "512GB SSD-D",
  "screen_size": "15.6-D",
  "brand": "ASUS-D",
  "model": "TUF Gaming-P",
  "gpu_power_consumption": "80W-P"
}}

Now, extract the information for this laptop:
Full Name: {full_name}
Description: {description}"""