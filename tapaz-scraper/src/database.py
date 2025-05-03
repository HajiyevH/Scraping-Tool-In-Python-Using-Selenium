import sqlite3
from datetime import datetime
from src import config
import os
from typing import Optional, List, Dict, Any 
import pandas as pd

def update_row_with_llm_specs(link, new_row):
    """
    Updates the database row identified by 'link' with fields from new_row.
    """
    update_data = {k: v for k, v in new_row.items() if k != "link"}
    update_laptop_specs(link, update_data)

def process_llm_results(results):
    """
    Takes a list of dicts with 'link' and 'extracted_specs' (as markdown JSON string),
    parses and updates the database for each.
    """
    for item in results:
        link = item.get("link")
        raw_specs = item.get("extracted_specs", "")
        cleaned = clean_llm_response(raw_specs)
        try:
            specs = json.loads(cleaned)
            from src import database as db
            db.update_row_with_llm_specs(link, specs)
            print(f"Updated DB for {link}")
        except Exception as e:
            print(f"Failed to parse or update specs for {link}: {e}")

def init_db():
    """Initializes the database and creates the 'laptops' table if it doesn't exist."""
    # Ensure the output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        # Create table - Adjust column names and types as needed
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS laptops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT,
                date TEXT,
                link TEXT UNIQUE, -- Ensure links are unique to avoid duplicates
                price REAL,       -- Use REAL for potential decimal prices
                comp_name TEXT,
                full_name TEXT,
                currency TEXT,
                description TEXT,
                type TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Track when it was scraped
            )
        ''')
        conn.commit()
        print(f"Database initialized successfully at {config.DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"Database error during initialization:a {e}")
    finally:
        if conn:
            conn.close()

def insert_data(data_dict):
    """Inserts scraped data from a dictionary into the SQLite database."""
    if not data_dict or not any(data_dict.values()):
        print("No data provided to insert into the database.")
        return

    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()

        # Prepare data for insertion (list of tuples)
        # Assumes all lists in data_dict have the same length
        num_items = len(data_dict.get("link", []))
        if num_items == 0:
            print("Data dictionary is empty or missing 'link' key.")
            return

        rows_to_insert = []
        keys = ["location", "date", "link", "price", "comp_name", "full_name", "currency", "description", "type"]

        for i in range(num_items):
            row = tuple(data_dict.get(key, [])[i] if i < len(data_dict.get(key, [])) else None for key in keys)
             # Basic price cleaning (remove non-numeric, convert to float)
            price_str = str(data_dict.get("price", [])[i]).replace(' ', '').replace('AZN', '').replace(',', '.') if i < len(data_dict.get("price", [])) else '0'
            try:
                price_float = float(price_str)
            except ValueError:
                price_float = None # Or 0.0, depending on how you want to handle invalid prices

            row_list = list(row)
            price_index = keys.index("price")
            row_list[price_index] = price_float # Replace original price string with float
            rows_to_insert.append(tuple(row_list))


        # Use INSERT OR IGNORE to skip inserting if a link already exists (due to UNIQUE constraint)
        sql = '''
            INSERT OR IGNORE INTO laptops (location, date, link, price, comp_name, full_name, currency, description, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        cursor.executemany(sql, rows_to_insert)
        conn.commit()
        inserted_count = cursor.rowcount
        print(f"Attempted to insert {len(rows_to_insert)} rows. Successfully inserted {inserted_count} new rows.")

    except sqlite3.Error as e:
        print(f"Database error during insertion: {e}")
    except IndexError as e:
         print(f"Data alignment error: Check if all lists in data_dict have the same length. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during data insertion: {e}")
    finally:
        if conn:
            conn.close()

def get_recent_laptops(limit: int = 100, since_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches the most recent 'limit' number of laptop entries from the database.

    Args:
        limit (int): The maximum number of laptops to retrieve. Defaults to 100.

    Returns:
        list: A list of dictionaries, where each dictionary represents a laptop row.
              Returns an empty list if no data is found or an error occurs.
    """
    conn = None
    laptops = []
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        params = []
        query = "SELECT * FROM laptops"

        # Add WHERE clause if since_id is provided and valid
        valid_since_date = None

        if since_date:
            print("aaaaaaaaaaaaa")
            try:
                # Validate the format 'YYYY-MM-DD'
                datetime.strptime(since_date, '%Y-%m-%d')

                valid_since_date = since_date # Use it if format is correct

            except (ValueError, TypeError):
                print(f"Warning: Invalid since_date format provided ('{since_date}'). Expected 'YYYY-MM-DD'. Ignoring filter.")

        if valid_since_date:
            query += " WHERE TRIM(date) > ?" # Use >= to include the date itself
            params.append(valid_since_date)
        # Add ORDER BY and LIMIT
        query += " ORDER BY TRIM(date) DESC LIMIT ?"
        params.append(limit)

        print(f"Executing query: {query} with params: {tuple(params)}") # Debug print
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        # Convert sqlite3.Row objects to standard dictionaries
        laptops = [dict(row) for row in rows]
        print(f"Successfully fetched {len(laptops)} recent laptops.")

    except sqlite3.Error as e:
        print(f"Database error while fetching recent laptops: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching recent laptops: {e}")
    finally:
        if conn:
            conn.close()
    return laptops    

def is_link_in_database(href: str) -> bool:
    """Checks if a given link already exists in the laptops table."""
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM laptops WHERE link = ? LIMIT 1", (href,))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        print(f"Database error while checking link in laptops: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while checking link in laptops: {e}")
    finally:
        if conn:
            conn.close()
    return False

def check_and_update_price(link: str, new_price: float) -> bool:
    """
    Checks if the price for the given link has changed.
    If changed, updates the price and returns True.
    If not changed or link not found, returns False.
    """
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM laptops WHERE link = ?", (link,))
        row = cursor.fetchone()
        if row is None:
            return False  # Link not found
        old_price = row[0]
        if str(old_price) != str(new_price):
            cursor.execute("UPDATE laptops SET price = ? WHERE link = ?", (new_price, link))
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Error in check_and_update_price: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_row_by_link(link: str) -> dict:
    """Fetches the full row for a given link from the laptops table."""
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM laptops WHERE link = ?", (link,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"Error in get_row_by_link: {e}")
        return None
    finally:
        if conn:
            conn.close()

            import pandas as pd

def import_csv_to_db(csv_path: str):
    """
    Imports data from a CSV file into the laptops table in the database.
    """
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)
        data_dict = {col: df[col].tolist() for col in df.columns}
        insert_data(data_dict)
        print(f"Successfully imported data from {csv_path} into the database.")
    except Exception as e:
        print(f"Error importing CSV to database: {e}")
def clear_laptops_table():
    """Deletes all rows from the laptops table."""
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM laptops")
        conn.commit()
        print("All data deleted from the laptops table.")
    except Exception as e:
        print(f"Error clearing laptops table: {e}")
    finally:
        if conn:
            conn.close()

def get_first_n_rows(n: int = None) -> List[Dict[str, Any]]:
    """Fetches the first n rows from the laptops table."""
    conn = None
    rows = []
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if n is None:
            cursor.execute("SELECT * FROM laptops")
        elif n >= 0:
            cursor.execute("SELECT * FROM laptops LIMIT ?", (n,))
        rows = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching first n rows: {e}")
    finally:
        if conn:
            conn.close()
    return rows

def update_laptop_specs(link: str, specs: dict):
    """
    Updates the laptops table for the given link with the fields in specs.
    Only updates columns that exist in the table.
    """
    if not specs:
        print("No specs provided for update.")
        return
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        # Build the SET part of the SQL dynamically
        set_clause = ", ".join([f"{k}=?" for k in specs.keys()])
        values = list(specs.values())
        values.append(link)
        sql = f"UPDATE laptops SET {set_clause} WHERE link=?"
        cursor.execute(sql, values)
        conn.commit()
        print(f"Updated specs for link: {link}")
    except Exception as e:
        print(f"Error updating specs for {link}: {e}")
    finally:
        if conn:
            conn.close()

def add_llm_columns():
    """
    Adds new columns for LLM-extracted specs to the laptops table if they do not exist.
    """
    new_columns = [
        ("cpu_full", "TEXT"),
        ("cpu_brand", "TEXT"),
        ("cpu_family", "TEXT"),
        ("cpu_generation", "TEXT"),
        ("cpu_cores_threads", "TEXT"),
        ("gpu_full", "TEXT"),
        ("gpu_brand", "TEXT"),
        ("gpu_power_consumption", "TEXT"),
        ("ram", "TEXT"),
        ("ram_type", "TEXT"),
        ("ram_speed_mhz", "TEXT"),
        ("storage", "TEXT"),
        ("storage_type", "TEXT"),
        ("storage_size_gb", "TEXT"),
        ("combined_storage_gb", "TEXT"),
        ("screen_size", "TEXT"),
        ("brand", "TEXT"),
        ("model", "TEXT"),
    ]
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    for col, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE laptops ADD COLUMN {col} {col_type}")
            print(f"Added column: {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column already exists: {col}")
            else:
                print(f"Error adding column {col}: {e}")
    conn.commit()
    conn.close()
# if __name__ == "__main__":
#     clear_laptops_table()
#     import_csv_to_db("/Users/hajiaga/Desktop/Personal/Scraping-Tool-In-Python-Using-Selenium/tapaz-scraper/output/tapaz_laptops.csv")