import akshare as ak
from datetime import datetime, timedelta
import sys

def debug_etfs():
    etfs = [
        {"name": "黄金ETF", "code": "518880"},
        {"name": "创业板ETF", "code": "159915"},
        {"name": "沪深300ETF", "code": "510300"},
        {"name": "纳指ETF", "code": "513100"}
    ]
    
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")
    
    print("START DEBUG", flush=True)
    
    for item in etfs:
        name = item['name']
        code = item['code']
        print(f"Checking {name} ({code})...", end=" ", flush=True)
        try:
            df = ak.fund_etf_hist_em(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            if df is None or df.empty:
                print("FAILED: Empty df", flush=True)
            else:
                print(f"SUCCESS: {len(df)} rows", flush=True)
        except Exception as e:
            print(f"ERROR: {e}", flush=True)

if __name__ == "__main__":
    debug_etfs()
