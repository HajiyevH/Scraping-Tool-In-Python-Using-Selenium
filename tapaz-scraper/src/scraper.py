# filepath: tapaz-scraper/src/scraper.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from . import config  
from . import utils  
from src.database import is_link_in_database,check_and_update_price,get_row_by_link

def initialize_driver():
    """Initializes and returns a Selenium WebDriver instance."""
    try:
        driver = webdriver.Chrome()
        driver.implicitly_wait(config.IMPLICIT_WAIT_TIME)
        print("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Ensure chromedriver is installed and accessible, or matches your Chrome version.")
        return None


def scrape_product_details(driver, product_url):
    """Scrapes details from a single product page."""
    details = {
        "full_name": "NaN", "location": "NaN", "comp_name": "NaN",
        "price": "NaN", "currency": "NaN", "date": "NaN",
        "type": "NaN", "description": "NaN", "link": product_url
    }
    try:
        driver.get(product_url)
        time.sleep(1) # Small pause for page elements to load after navigation

        # Use WebDriverWait for more robust element finding
        wait = WebDriverWait(driver, config.IMPLICIT_WAIT_TIME)

        details["full_name"] = wait.until(EC.visibility_of_element_located((By.XPATH, config.PRODUCT_TITLE_XPATH))).text

        properties_col = wait.until(EC.visibility_of_element_located((By.XPATH, config.PROPERTIES_COLUMN_XPATH)))
        details["location"] = properties_col.find_element(By.XPATH, config.LOCATION_XPATH).text
        comp_name_raw = properties_col.find_element(By.TAG_NAME, config.COMPANY_TAG_NAME).text
        details["comp_name"] = "other" if comp_name_raw == config.OTHER_COMPANY_TEXT else comp_name_raw

        price_cont = wait.until(EC.visibility_of_element_located((By.XPATH, config.PRICE_CONTAINER_XPATH)))
        price_spans = price_cont.find_elements(By.TAG_NAME, config.PRICE_SPAN_TAG_NAME)
        if len(price_spans) >= 2:
            details["price"] = price_spans[0].text.replace(" ", "") # Clean price
            details["currency"] = price_spans[1].text

        stats_cont = wait.until(EC.visibility_of_element_located((By.XPATH, config.STATS_CONTAINER_XPATH)))
        stats_divs = stats_cont.find_elements(By.TAG_NAME, config.STATS_DIV_TAG_NAME)
        if len(stats_divs) > 1:
            date_raw = stats_divs[1].find_element(By.TAG_NAME, config.DATE_SPAN_TAG_NAME).text.split(',')[0]
            details["date"] = utils.az_to_eng_date(date_raw)

        # Seller type check
        seller_divs = driver.find_elements(By.CSS_SELECTOR, config.SELLER_TYPE_SELECTOR)
        is_individual = any(config.SELLER_TYPE_CLASS in div.get_attribute("class") for div in seller_divs)
        details["type"] = 'individual_seller' if is_individual else 'shop'

        try:
            # Description might not always exist
            desc_element = driver.find_element(By.XPATH, config.DESCRIPTION_XPATH)
            details["description"] = desc_element.text
        except NoSuchElementException:
            details["description"] = 'NaN' # Explicitly NaN if not found

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"Error scraping details for {product_url}: {type(e).__name__}")
    except Exception as e:
         print(f"An unexpected error occurred scraping {product_url}: {e}")
    finally:
        # Go back in the main loop, not here, to avoid issues if an error occurred before navigation
        pass # driver.back() will be called in the main scraping loop

    return details



def scrape_tapaz_laptops(driver, base_url=config.BASE_URL, max_items=None):
    """Main function to scrape laptop listings from Tap.az."""
    scraped_data = {
        "location": [], "date": [], "link": [], "price": [], "comp_name": [],
        "full_name": [], "currency": [], "description": [], "type": []
    }
    processed_links = set() # Keep track of links already processed in this run

    try:
        print(f"Navigating to base URL: {base_url}")
        driver.get(base_url)
        time.sleep(2) # Allow homepage to load

        # Navigate to Electronics
        print("Finding and clicking Electronics category...")
        category = WebDriverWait(driver, config.IMPLICIT_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, config.ELECTRONICS_CATEGORY_XPATH))
        )
        electronics_url = category.get_attribute('href')
        print(f"Navigating to Electronics URL: {electronics_url}")
        driver.get(electronics_url)
        time.sleep(2)

        # --- Apply Price Filter ---
        print("Applying price filter...")
        price_dropdown = WebDriverWait(driver, config.IMPLICIT_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, config.PRICE_DROPDOWN_XPATH))
        )
        price_dropdown.click()
        time.sleep(0.5)
        min_price_input = driver.find_element(By.XPATH, config.MIN_PRICE_INPUT_XPATH)
        max_price_input = driver.find_element(By.XPATH, config.MAX_PRICE_INPUT_XPATH)
        min_price_input.send_keys(str(config.MIN_PRICE))
        max_price_input.send_keys(str(config.MAX_PRICE))
        # Click somewhere else or press Enter if needed to apply filter, often clicking the dropdown again works
        price_dropdown.click() # Or find an 'Apply' button if it exists
        print(f"Price filter set ({config.MIN_PRICE}-{config.MAX_PRICE}). Waiting for results...")
        time.sleep(config.SCROLL_PAUSE_TIME) # Wait for page to potentially reload/filter

        # --- Find Laptop Subcategory ---
        print("Finding Laptop subcategory...")
        laptop_href = None
        categories_section = WebDriverWait(driver, config.IMPLICIT_WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class = 'subcategories-inner']")) # More specific if possible
        )
        sub_links = categories_section.find_elements(By.TAG_NAME, 'a')
        for link in sub_links:
            href = link.get_attribute('href')
            if href and config.LAPTOP_SUBCATEGORY_KEYWORD in href.lower():
                laptop_href = href
                print(f"Found Laptop URL: {laptop_href}")
                break
        if not laptop_href:
            print("Laptop subcategory link not found.")
            return scraped_data # Return empty data

        driver.get(laptop_href)
        print("Navigated to Laptop page. Waiting...")
        time.sleep(config.SCROLL_PAUSE_TIME)

        print("Applying 'New' filter...")
        new_dropdown = WebDriverWait(driver, config.IMPLICIT_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, config.NEW_FILTER_XPATH))
        )
        new_dropdown.click()
        time.sleep(0.5)
        new_options = new_dropdown.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, 'li')
        if len(new_options) > config.NEW_FILTER_OPTION_INDEX:
            new_options[config.NEW_FILTER_OPTION_INDEX].click()
            print("'New' filter applied. Waiting for results...")
            time.sleep(config.SCROLL_PAUSE_TIME) # Wait for page update
        else:
            print("Could not find 'New' filter option.")
            # Decide whether to continue without the filter or stop
            # return scraped_data

        # --- Scrape Product Links with Scrolling ---
        print("Starting product scraping loop...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        product_links_found = set() # Store links found on the page to avoid duplicates per scroll
        
        count_before_0 = 0
        COUNT_BEFORE_RESTART = config.COUNT_BEFORE_RESTART
        count_existing = 0
        STOP_THRESHOLD = config.STOP_THRESHOLD

    while max_items is None or len(scraped_data["link"]) < max_items:
            print(f"Scraping page... Found {len(scraped_data['link'])} items so far (Target: {max_items}).")
            # Find product containers visible now
            try:
                # Add a specific wait for the container AND at least one product element (adjust selector if needed)
                product_list_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, config.PRODUCT_LIST_SELECTOR))
                )
                # Wait for at least one direct child div to be present
                WebDriverWait(product_list_container, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ":scope > div"))
                )
                product_elements = product_list_container.find_elements(By.CSS_SELECTOR, ":scope > div") # Find direct children divs relative to the container
                print(f"DEBUG: Found {len(product_elements)} potential product elements using selector: {config.PRODUCT_LIST_SELECTOR} > div") # DEBUG PRINT
            except TimeoutException:
                print(f"DEBUG: Timed out waiting for product elements within: {config.PRODUCT_LIST_SELECTOR}")
                product_elements = []
            except NoSuchElementException:
                 print(f"DEBUG: Could not find product list container: {config.PRODUCT_LIST_SELECTOR}")
                 product_elements = []

            new_links_on_page = []
            for product in product_elements:
                if config.PAGINATION_CLASS_CHECK not in product.get_attribute("class"):
                    try:
                        # Find the main link within the product container
                        product_link_element = product.find_element(By.TAG_NAME, "a")
                        product_url = product_link_element.get_attribute("href")

                        # Basic check if it looks like a product URL (adjust count if needed)
                        expected_slash_count = laptop_href.count('/') + 1
                        if product_url and product_url.count('/') == expected_slash_count and product_url not in processed_links:
                             new_links_on_page.append(product_url)
                             product_links_found.add(product_url) # Add to set for this scroll cycle

                    except NoSuchElementException:
                        continue # Skip if the element structure is unexpected

            # Process newly found links for this scroll cycle
            print(f"Found {len(new_links_on_page)} new product links on this scroll.")
            for link_to_scrape in new_links_on_page:

                if max_items is not None and len(scraped_data["link"]) >= max_items:
                    print("Reached max_items limit during link processing.")
                    break # Stop processing links if limit reached
                
                if is_link_in_database(link_to_scrape):
                    count_existing += 1
                    print(f"  - Found existing link ({count_existing}/{STOP_THRESHOLD}): {link_to_scrape}")
                    processed_links.add(link_to_scrape)
                    try:
                        price_element = product.find_element(By.CLASS_NAME, "price-val")
                        scraped_price = price_element.text.replace(" ", "")
                    except Exception:
                        scraped_price = None

                    if scraped_price is not None and check_and_update_price(link_to_scrape, scraped_price):
                        print(f"Price updated for {link_to_scrape}")
                        updated_row = get_row_by_link(link_to_scrape)
                        if updated_row:
                            for key in scraped_data.keys():
                                scraped_data[key].append(updated_row[key]) 

                    if count_existing >= STOP_THRESHOLD:
                        print(f"Found {STOP_THRESHOLD} consecutive existing items. Stopping scrape.")
                        # Exit the entire function when threshold is met
                        return scraped_data
                    # Continue to the next link in new_links_on_page
                    continue
                else:
                    if count_before_0 >= COUNT_BEFORE_RESTART:
                        count_before_0 = 0
                        print("reset")
                        count_existing = 0
                    else:
                        print(f"  - Found non existing link. Did not restart ({count_before_0}/{COUNT_BEFORE_RESTART}): {link_to_scrape}")
                        count_before_0 +=1
                if link_to_scrape not in processed_links:
                    print(f"Scraping details for: {link_to_scrape}")
                    details = scrape_product_details(driver, link_to_scrape)
                    # Append data only if scraping was successful (or handle NaNs appropriately)
                    for key in scraped_data.keys():
                        if key in details:
                            scraped_data[key].append(details[key])
                        else:
                            scraped_data[key].append("Error") 
                    processed_links.add(link_to_scrape) # Mark as processed for this run
                    print(f"Items collected: {len(scraped_data['link'])}")
                    # Go back to the listings page
                    print("Navigating back to listings page...")
                    driver.back()
                    time.sleep(0.05) # Wait after navigating back

            if len(scraped_data["link"]) >= max_items:
                print("Reached max_items limit after processing links.")
                break # Exit while loop

            # Scroll down
            print("Scrolling down...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(config.SCROLL_PAUSE_TIME) # Wait for new content to load
            print("aaaaaaa")
            # Check if scroll height has changed
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached bottom of the page or no new content loaded.")
                break # Exit if no more scrolling is possible
            last_height = new_height

    except (NoSuchElementException, TimeoutException) as e:
        print(f"A critical element was not found or timed out: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
    finally:
         print(f"Scraping finished. Total items collected: {len(scraped_data['link'])}")

    return scraped_data
