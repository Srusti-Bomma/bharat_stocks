"""
Test top NSE stocks to verify which ones work with the Indian API
"""
import requests
import json
import time

API_KEY = "sk-live-y1O4YaFG4d0biKLvgPFf3vOqr9Jx33j4aKw1Q1uJ"
BASE_URL = "https://stock.indianapi.in"

# Top 100 NSE stocks (Nifty 50 + Nifty Next 50 + popular large caps)
TOP_NSE_STOCKS = [
    # Nifty 50
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN",
    "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
    "SUNPHARMA", "BAJFINANCE", "ULTRACEMCO", "NESTLEIND", "WIPRO", "ADANIENT",
    "HCLTECH", "TATAMOTORS", "ONGC", "NTPC", "M&M", "TECHM", "TATASTEEL", "POWERGRID",
    "BAJAJFINSV", "ADANIPORTS", "COALINDIA", "JSWSTEEL", "GRASIM", "INDUSINDBK",
    "DIVISLAB", "DRREDDY", "BRITANNIA", "HINDALCO", "HEROMOTOCO", "EICHERMOT",
    "CIPLA", "TATACONSUM", "APOLLOHOSP", "BAJAJ-AUTO", "SBILIFE", "BPCL", "UPL",
    "SHREECEM", "TRENT",
    
    # Nifty Next 50
    "ADANIGREEN", "ADANIPOWER", "ATGL", "BANKBARODA", "BERGEPAINT", "BOSCHLTD",
    "CANBK", "CHOLAFIN", "COLPAL", "DABUR", "DLF", "GAIL", "GODREJCP", "HDFCLIFE",
    "HAVELLS", "ICICIPRULI", "INDIGO", "IOC", "JINDALSTEL", "LTIM", "LUPIN",
    "MARICO", "MCDOWELL-N", "MPHASIS", "NMDC", "NYKAA", "PAGEIND", "PERSISTENT",
    "PETRONET", "PNB", "PFC", "RECLTD", "SBICARD", "SIEMENS", "TORNTPHARM",
    "TVSMOTOR", "VEDL", "VOLTAS", "ZOMATO", "ZYDUSLIFE",
    
    # Additional popular large caps
    "AMBUJACEM", "ACC", "BIOCON", "GODREJPROP", "HINDZINC", "IDFC",
    "IDFCFIRSTB", "IRCTC", "JUBLFOOD", "NATIONALUM", "OBEROIRLTY",
    "PAYTM", "PEL", "PIIND", "SAIL", "TATAELXSI", "TATAPOWER", "YESBANK",
    "ASHOKLEY", "AUROPHARMA"
]

def test_stock(symbol):
    """Test if stock symbol works with the API"""
    try:
        url = f"{BASE_URL}/stock"
        headers = {"x-api-key": API_KEY}
        params = {"name": symbol}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Check if we got valid data
            if data and 'companyName' in data:
                return {
                    'success': True,
                    'symbol': symbol,
                    'name': data.get('companyName', symbol),
                    'sector': data.get('industry', 'N/A'),
                    'price': data.get('currentPrice', {}).get('NSE') or data.get('currentPrice', {}).get('BSE'),
                }
        
        return {'success': False, 'symbol': symbol, 'error': f"Status {response.status_code}"}
    
    except Exception as e:
        return {'success': False, 'symbol': symbol, 'error': str(e)}

def main():
    print(f"Testing {len(TOP_NSE_STOCKS)} NSE stocks...")
    print("=" * 80)
    
    working_stocks = []
    failed_stocks = []
    
    for i, symbol in enumerate(TOP_NSE_STOCKS, 1):
        print(f"[{i}/{len(TOP_NSE_STOCKS)}] Testing {symbol}...", end=" ")
        
        result = test_stock(symbol)
        
        if result['success']:
            print(f"✓ {result['name']} - {result['sector']}")
            working_stocks.append(result)
        else:
            print(f"✗ Error: {result.get('error', 'Unknown')}")
            failed_stocks.append(result)
        
        # Rate limiting - wait 0.5 seconds between requests
        time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print(f"\nResults:")
    print(f"  Working stocks: {len(working_stocks)}")
    print(f"  Failed stocks: {len(failed_stocks)}")
    
    # Save working stocks to JSON
    with open('nse_working_stocks.json', 'w', encoding='utf-8') as f:
        json.dump(working_stocks, f, indent=2, ensure_ascii=False)
    
    # Save just the symbols list
    symbols_only = [s['symbol'] for s in working_stocks]
    with open('nse_stock_symbols.json', 'w', encoding='utf-8') as f:
        json.dump(symbols_only, f, indent=2)
    
    print(f"\n✓ Saved working stocks to: nse_working_stocks.json")
    print(f"✓ Saved symbols list to: nse_stock_symbols.json")
    
    if failed_stocks:
        print(f"\nFailed stocks:")
        for stock in failed_stocks:
            print(f"  - {stock['symbol']}: {stock.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
