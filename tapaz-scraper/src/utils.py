# filepath: tapaz-scraper/src/utils.py
from datetime import datetime, timedelta
import re
import os
import pandas as pd
from . import config 
from . import database

def az_to_eng_date(date_str):
    """Converts Azerbaijani date strings ('Bugün', 'Dünən', 'DD Ay') to 'MM DD' format."""
    date_str = date_str.strip()
    if date_str == config.DATE_TODAY_AZ:
        return datetime.today().strftime('%m %d')
    elif date_str == config.DATE_YESTERDAY_AZ:
        yesterday = datetime.today() - timedelta(days=1)
        return yesterday.strftime('%m %d')
    else:
        try:
            # Extract day (first digits)
            day_match = re.match(r'\d+', date_str)
            if not day_match:
                return "NaN NaN" # Or raise an error/log
            gun = day_match.group(0).zfill(2) # Ensure 2 digits

            # Extract month name (non-digits)
            month_match = re.findall(r'\D+', date_str)
            if not month_match:
                 return "NaN NaN" # Or raise an error/log
            ay = month_match[0].strip().lower()

            numay = config.MONTH_MAP_AZ.get(ay, "NaN") # Use .get for safety

            return f"{numay} {gun}"
        except Exception as e:
            print(f"Error parsing date string '{date_str}': {e}") # Basic error logging
            return "NaN NaN"

def save_data(data_dict, output_dir=config.OUTPUT_DIR, csv_filename=config.CSV_FILENAME, excel_filename=config.EXCEL_FILENAME):
    """Saves the scraped data dictionary to CSV and Excel files."""
    if not data_dict or not any(data_dict.values()):
        print("No data to save.")
        return
    try:
        print("Attempting to save data to SQLite database...")
        database.insert_data(data_dict) # Call the database insertion function
    except Exception as e:
        print(f"Error saving data to database: {e}")

    try:
        df = pd.DataFrame.from_dict(data_dict)
    except ValueError as e:
         print(f"Error creating DataFrame. Check if all lists in the dictionary have the same length: {e}")
         # Optional: Print lengths for debugging
         # for key, value in data_dict.items():
         #    print(f"Length of {key}: {len(value)}")
         return


    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    csv_filepath = os.path.join(output_dir, csv_filename)
    excel_filepath = os.path.join(output_dir, excel_filename)

    # Remove old files if they exist (optional, depends on desired behavior)
    # if os.path.exists(csv_filepath):
    #     os.remove(csv_filepath)
    # if os.path.exists(excel_filepath):
    #     os.remove(excel_filepath)

    # try:
    #     df.to_csv(csv_filepath, index=False)
    #     df.to_excel(excel_filepath, index=False)
    #     print(f"Data saved successfully to {csv_filepath} and {excel_filepath}")
    #     print(df.head()) # Print head for confirmation
    # except Exception as e:
    #     print(f"Error saving data files: {e}")

