import json
import pymysql  # This library is used by your SQLAlchemy connection string

# --- Database Configuration ---
# IMPORTANT: Update these with your actual database details from the .env file
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "17045"  # Your actual password
DB_NAME = "bharat_stocks"
JSON_FILE_PATH = "nse_working_stocks.json"

def populate_symbols():
    """Reads stock data from JSON and inserts it into the dim_symbol table."""
    
    # 1. Read the JSON file
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            stocks_data = json.load(f)
        print(f"Successfully loaded {len(stocks_data)} records from {JSON_FILE_PATH}")
    except Exception as e:
        print(f"Error: Could not read or parse {JSON_FILE_PATH}. Details: {e}")
        return

    # 2. Connect to the database
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Successfully connected to the database.")
    except Exception as e:
        print(f"Error: Could not connect to the database. Details: {e}")
        return

    # 3. Insert data into the dim_symbol table
    inserted_count = 0
    skipped_count = 0
    with conn.cursor() as cursor:
        for stock in stocks_data:
            # Use INSERT IGNORE to safely skip duplicates if the script is run more than once
            sql = "INSERT IGNORE INTO `dim_symbol` (`symbol`, `name`, `sector`) VALUES (%s, %s, %s)"
            
            # Ensure values are not None before inserting
            symbol = stock.get('symbol')
            name = stock.get('name')
            sector = stock.get('sector')

            if symbol:
                cursor.execute(sql, (symbol, name, sector))
                if cursor.rowcount > 0:
                    inserted_count += 1
                else:
                    skipped_count += 1
    
    # Commit the transaction to save the changes
    conn.commit()
    conn.close()
    
    print("\n--- Population Complete ---")
    print(f"Records inserted: {inserted_count}")
    print(f"Records skipped (already exist): {skipped_count}")
    print("---------------------------\n")


if __name__ == "__main__":
    populate_symbols()
