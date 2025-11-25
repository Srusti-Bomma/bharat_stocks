import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.app.symbol_meta import get_sector_for_symbol

def test_lookup(symbol, company_name=None, expected_sector=None, file=None):
    sector = get_sector_for_symbol(symbol, company_name=company_name)
    msg = f"Symbol: {symbol}, Name: {company_name}, Sector: {sector}, Expected: {expected_sector}"
    print(msg)
    if file:
        file.write(msg + "\n")

if __name__ == "__main__":
    with open("results.txt", "w", encoding="utf-8") as f:
        f.write(f"Current working directory: {os.getcwd()}\n")
        p = Path("d:/stocks/nse_working_stocks.json")
        f.write(f"Checking if {p} exists: {p.exists()}\n")
        
        # Try loading JSON directly
        try:
            import json
            with open(p, "r", encoding="utf-8") as jf:
                data = json.load(jf)
            f.write(f"Successfully loaded JSON. Items: {len(data)}\n")
        except Exception as e:
            f.write(f"Error loading JSON directly: {e}\n")

        f.write("Testing get_sector_for_symbol...\n")
        test_lookup("RELIANCE", None, "Oil & Gas Operations", file=f)
        test_lookup("CNBK.NS", None, None, file=f) 
        test_lookup("CNBK.NS", "Canara Bank", "Regional Banks", file=f)
        test_lookup("ADAN.NS", "Adani Power", "Electric Utilities", file=f)
        test_lookup("CANBK", None, "Regional Banks", file=f)
