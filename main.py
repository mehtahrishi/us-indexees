# 1 to 500 full snapshot
import pandas as pd
import requests
import yfinance as yf
import sys

# 1. Sourcing ALL Tickers from Wikipedia
print("Sourcing FULL S&P 500 List...")
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers)
    df_list = pd.read_html(response.text)[0]
    tickers = df_list['Symbol'].tolist()
    # Clean tickers for yfinance compatibility
    tickers_cleaned = [t.replace('.', '-') for t in tickers]
except Exception as e:
    print(f"Error sourcing list: {e}")
    sys.exit()

# 2. BATCH DOWNLOAD (The "Real-Time" Secret)
# This fetches the core data for all 500 stocks in one or two giant requests
print("Fetching real-time market data snapshot...")
stocks_data = yf.download(tickers_cleaned, period="1d", interval="1m", group_by='ticker', threads=True)

# 3. Headers (Exactly as you requested)
header = (f"{'RANK':<4} | {'SYM':<5} | {'NAME':<20} | {'PRICE':<8} | {'CHG':<7} | "
          f"{'CHG%':<7} | {'PREV-CLOSE':<10} | {'DAY-RANGE':<18} | {'52W-RANGE':<18} | "
          f"{'VOL':<10} | {'MCAP':<8} | {'PE':<6} | {'BETA':<5} | {'BID/ASK':<18}")
line = "-" * len(header)

print("\n" + "=" * len(header))
print(header)
print(line)

# 4. Processing and Printing
for i, symbol in enumerate(tickers, 1):
    try:
        sym = symbol.replace('.', '-')
        # Fetching from the yfinance Ticker object for deep metadata (PE, Beta, etc.)
        # Note: .info is still the best way to get Market Cap and PE
        stock = yf.Ticker(sym)
        info = stock.info 
        
        current = info.get('currentPrice', 0)
        prev_close = info.get('previousClose', 0)
        
        # Calculations
        net_change = current - prev_close
        change_pct = (net_change / prev_close) * 100 if prev_close else 0
        
        # Formatting
        name = info.get('shortName', 'N/A')[:20]
        bid_ask = f"{info.get('bid', 0):.2f}x{info.get('bidSize', 0)} / {info.get('ask', 0):.2f}x{info.get('askSize', 0)}"
        day_range = f"{info.get('dayLow', 0):.2f}-{info.get('dayHigh', 0):.2f}"
        year_range = f"{info.get('fiftyTwoWeekLow', 0):.2f}-{info.get('fiftyTwoWeekHigh', 0):.2f}"
        
        m_cap_raw = info.get('marketCap', 0)
        if m_cap_raw > 1e12:
            m_cap = f"{m_cap_raw / 1e12:.2f}T"
        elif m_cap_raw > 1e9:
            m_cap = f"{m_cap_raw / 1e9:.1f}B"
        else:
            m_cap = f"{m_cap_raw / 1e6:.1f}M"
        
        row = (f"{i:<4} | {sym:<5} | {name:<20} | {current:<8.2f} | {net_change:>+7.2f} | "
               f"{change_pct:>+6.2f}% | {prev_close:<10.2f} | {day_range:<18} | {year_range:<18} | "
               f"{info.get('volume', 0):<10} | {m_cap:<8} | "
               f"{info.get('trailingPE', 0):<6.2f} | {info.get('beta', 0):<5.2f} | {bid_ask:<18}")
        
        print(row)

    except Exception:
        continue

print(line)
