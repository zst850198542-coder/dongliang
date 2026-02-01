import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

# Create a fresh session or forceful proxy bypass
os.environ["NO_PROXY"] = "*"
# Ensure others are empty strings instead of missing
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

def test_single():
    code = "518880" # Gold ETF
    start_date = "20251201"
    end_date = "20260201"
    
    print(f"Fetching {code} from {start_date} to {end_date}...")
    try:
        df = ak.fund_etf_hist_em(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        if df is None:
            print("Return is None")
        elif df.empty:
            print("Return is Empty DataFrame")
        else:
            print("Success!")
            print(df.head())
            print("Columns:", df.columns)
            print("Dtypes:", df.dtypes)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_single()
