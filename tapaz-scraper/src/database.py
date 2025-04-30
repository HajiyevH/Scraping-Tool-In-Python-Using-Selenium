import sqlite3
from . import config
import os

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
