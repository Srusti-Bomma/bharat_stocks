# Bharat Stocks Insight - Available Stock Symbols

## How the System Works

The application uses the **Indian Stock API** which can fetch data for any valid NSE/BSE listed stock symbol.

### Available Endpoints:

1. **Individual Stock Data**: `/api/fetch-now?symbol=SYMBOL_NAME`
   - You can search for ANY NSE/BSE listed company by symbol or name

2. **Multiple Stocks**: `/api/live-data?symbols=TCS,INFY,RELIANCE`
   - Fetch multiple stocks at once

3. **Most Active Stocks**: `/api/most-active`
   - Returns top 10-15 most actively traded stocks on NSE

4. **Trending Stocks**: `/api/trending`
   - Returns currently trending stocks

---

## Popular Indian Stock Symbols (NSE)

### Banking & Financial Services
- **HDFCBANK** - HDFC Bank
- **ICICIBANK** - ICICI Bank
- **SBIN** - State Bank of India
- **AXISBANK** - Axis Bank
- **KOTAKBANK** - Kotak Mahindra Bank
- **INDUSINDBK** - IndusInd Bank
- **BANDHANBNK** - Bandhan Bank
- **PNB** - Punjab National Bank
- **CANBK** - Canara Bank
- **BANKBARODA** - Bank of Baroda

### IT & Technology
- **TCS** - Tata Consultancy Services
- **INFY** - Infosys
- **WIPRO** - Wipro
- **HCLTECH** - HCL Technologies
- **TECHM** - Tech Mahindra
- **LTTS** - L&T Technology Services
- **LTIM** - LTIMindtree
- **PERSISTENT** - Persistent Systems
- **MPHASIS** - Mphasis
- **COFORGE** - Coforge

### Oil & Gas
- **RELIANCE** - Reliance Industries
- **ONGC** - Oil and Natural Gas Corporation
- **IOC** - Indian Oil Corporation
- **BPCL** - Bharat Petroleum
- **GAIL** - GAIL (India)

### Automobiles
- **MARUTI** - Maruti Suzuki
- **TATAMOTORS** - Tata Motors
- **M&M** - Mahindra & Mahindra
- **BAJAJ-AUTO** - Bajaj Auto
- **HEROMOTOCO** - Hero MotoCorp
- **EICHERMOT** - Eicher Motors
- **ASHOKLEY** - Ashok Leyland
- **TVSMOTOR** - TVS Motor Company

### Pharmaceuticals
- **SUNPHARMA** - Sun Pharmaceutical
- **DRREDDY** - Dr. Reddy's Laboratories
- **CIPLA** - Cipla
- **DIVISLAB** - Divi's Laboratories
- **BIOCON** - Biocon
- **AUROPHARMA** - Aurobindo Pharma
- **LUPIN** - Lupin
- **TORNTPHARM** - Torrent Pharmaceuticals

### FMCG (Fast Moving Consumer Goods)
- **HINDUNILVR** - Hindustan Unilever
- **ITC** - ITC Limited
- **NESTLEIND** - Nestle India
- **BRITANNIA** - Britannia Industries
- **DABUR** - Dabur India
- **MARICO** - Marico
- **GODREJCP** - Godrej Consumer Products

### Metals & Mining
- **TATASTEEL** - Tata Steel
- **JSWSTEEL** - JSW Steel
- **HINDALCO** - Hindalco Industries
- **VEDL** - Vedanta
- **COALINDIA** - Coal India
- **NMDC** - NMDC Limited
- **SAIL** - Steel Authority of India

### Telecom
- **BHARTIARTL** - Bharti Airtel
- **IDEA** - Vodafone Idea

### Power & Utilities
- **POWERGRID** - Power Grid Corporation
- **NTPC** - NTPC Limited
- **ADANIPOWER** - Adani Power
- **TATAPOWER** - Tata Power

### Conglomerates
- **RELIANCE** - Reliance Industries
- **LT** - Larsen & Toubro
- **ITC** - ITC Limited

### Cement
- **ULTRACEMCO** - UltraTech Cement
- **AMBUJACEM** - Ambuja Cements
- **ACC** - ACC Limited
- **SHREECEM** - Shree Cement

### Adani Group
- **ADANIENT** - Adani Enterprises
- **ADANIPORTS** - Adani Ports
- **ADANIPOWER** - Adani Power
- **ADANIGREEN** - Adani Green Energy

### Tata Group
- **TCS** - Tata Consultancy Services
- **TATAMOTORS** - Tata Motors
- **TATASTEEL** - Tata Steel
- **TATAPOWER** - Tata Power
- **TITAN** - Titan Company
- **TATAELXSI** - Tata Elxsi

### Real Estate
- **DLF** - DLF Limited
- **GODREJPROP** - Godrej Properties
- **OBEROIRLTY** - Oberoi Realty

---

## Notes

1. **The dashboard can display ANY valid NSE/BSE stock** - just search for it!
2. **Most Active Stocks** are automatically fetched from the API (top 10-15 stocks by trading volume)
3. **Trending Stocks** are dynamically provided by the market data API
4. You can add more stocks to the default dashboard list by modifying the frontend code

---

## Data Source

All stock data is fetched in real-time from **Indian Stock Market API** (https://stock.indianapi.in)

- Live prices from NSE and BSE
- Company fundamentals
- Financial statements
- Peer comparisons
- Analyst recommendations
- Corporate actions
- Shareholding patterns
