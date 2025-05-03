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
- cpu_full (full CPU model, e.g., "Intel Core i7-11370H")
- cpu_brand (e.g., "Intel", "AMD")
- cpu_family (e.g., "i7", "i5", "Ryzen 5")
- cpu_generation (e.g., "11th Gen", "Zen 3", or "Unknown")
- cpu_cores_threads (e.g., "4C/8T" or "Unknown")
- gpu_full (full GPU model, e.g., "NVIDIA RTX 3060")
- gpu_brand (e.g., "NVIDIA", "AMD", "Intel", or "No GPU")
- gpu_power_consumption (in watts, if possible)
- ram (e.g., "16GB")
- ram_type (e.g., "DDR4", "DDR5", or "Unknown")
- ram_speed_mhz (e.g., "3200MHz" or "Unknown")
- storage (e.g., "512GB SSD")
- storage_type (e.g., "SSD", "HDD", "Hybrid", or "Unknown")
- storage_size_gb (numeric, e.g., "512")
- combined_storage_gb (sum of all storage in GB, numeric)
- screen_size (e.g., "15.6")
- brand (e.g., "ASUS")
- model (e.g., "TUF Gaming")

Instructions:
1. Use both the "Full Name" and "Description" fields to extract each value.
2. If a value is explicitly stated in the text, use it and add "-D" to the value (for example: "i7-11370-D").
3. If a value is not stated but you can confidently predict it based on your knowledge or by searching the internet, use your best prediction and add "-P" to the value (for example: "i7-11370-P").
4. If you cannot determine a value, return "Unknown".
5. For gpu_power_consumption, estimate the typical wattage for the GPU model if not given, and use the same "-D" or "-P" suffix rules.
6. For combined_storage_gb, sum all storage devices (e.g., SSD + HDD).
7. For fields like cpu_brand, gpu_brand, storage_type, extract the most specific value possible.
8. Output the result as a JSON object with keys: cpu_full, cpu_brand, cpu_family, cpu_generation, cpu_cores_threads, gpu_full, gpu_brand, gpu_power_consumption, ram, ram_type, ram_speed_mhz, storage, storage_type, storage_size_gb, combined_storage_gb, screen_size, brand, model.

Example output:
{{
  "cpu_full": "Intel Core i7-11370H-D",
  "cpu_brand": "Intel-D",
  "cpu_family": "i7-D",
  "cpu_generation": "11th Gen-D",
  "cpu_cores_threads": "4C/8T-P",
  "gpu_full": "NVIDIA RTX 3060-P",
  "gpu_brand": "NVIDIA-P",
  "gpu_power_consumption": "80W-P",
  "ram": "16GB-D",
  "ram_type": "DDR4-P",
  "ram_speed_mhz": "3200MHz-P",
  "storage": "512GB SSD-D",
  "storage_type": "SSD-D",
  "storage_size_gb": "512-D",
  "combined_storage_gb": "512-D",
  "screen_size": "15.6-D",
  "brand": "ASUS-D",
  "model": "TUF Gaming-P"
}}

Now, extract the information for this laptop:
Full Name: {full_name}
Description: {description}"""