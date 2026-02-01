import requests
import pandas as pd
import json

def get_kline_direct(code, name):
    # Determine market (1 for SH/51, 0 for SZ/15)
    # This is a heuristic.
    # 5xxxx -> SH (1)
    # 15xxxx -> SZ (0)
    # 16xxxx -> SZ (0) usually? Or SH? 16 is LOF, usually SZ.
    # 30xxxx -> SZ (0)
    # 00xxxx -> SZ (0)
    # 60xxxx -> SH (1)
    
    secid = ""
    if code.startswith("5") or code.startswith("6"):
        secid = f"1.{code}"
    else:
        secid = f"0.{code}"
    
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101", # Daily
        "fqt": "1",   # QFQ (Adjusted)
        "end": "20500101",
        "lmt": "60"   # Last 60 days
    }
    
    print(f"Direct fetching {name} ({secid})...")
    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        if data["data"] is None:
            print(f"Failed: data is None. Msg: {data.get('msg')}")
            return
        
        klines = data["data"]["klines"]
        print(f"Got {len(klines)} lines.")
        # Format: "2024-12-01,1.23,..."
        # Parse last line
        print("Last line:", klines[-1])
        
        # Convert to DF-like structure to verify parsing
        parsed = []
        for line in klines:
            parts = line.split(",")
            parsed.append({
                "日期": parts[0],
                "收盘": float(parts[2])
            })
        print(f"Parsed last close: {parsed[-1]['收盘']}")
        
    except Exception as e:
        print(f"Direct Error: {e}")

if __name__ == "__main__":
    get_kline_direct("518880", "黄金ETF")
    get_kline_direct("159915", "创业板ETF")
