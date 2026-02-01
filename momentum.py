import requests
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta

class MomentumCalculator:
    def __init__(self):
        # Default ETF Codes
        self.default_etfs = [
            {"name": "黄金ETF", "code": "518880"},
            {"name": "创业板ETF", "code": "159915"},
            {"name": "沪深300ETF", "code": "510300"},
            {"name": "纳指ETF", "code": "513100"}
        ]
        self.cache = {}
        self.cache_time = {}

    def get_data(self, etf_list, days=30):
        """
        获取过去 N 天的日线数据。
        """
        results = {}
        # Increase lookback window to ensure enough trading days
        start_date = (datetime.now() - timedelta(days=days*3 + 20)).strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")

        for item in etf_list:
            name = item['name']
            code = item['code']
            
            # Check cache (simple 1-hour cache based on code)
            if code in self.cache and (datetime.now() - self.cache_time.get(code, datetime.min)).seconds < 3600:
                 results[name] = (self.cache[code], code)
                 continue

            try:
                # Direct fetch from EastMoney API to bypass akshare issues/proxies
                print(f"Fetching data for {name} ({code})...")
                
                # Determine market (1 for SH, 0 for SZ)
                # 5xxxx -> SH (1)
                # 6xxxx -> SH (1)
                # Others -> SZ (0)
                secid_prefix = "1" if code.startswith("5") or code.startswith("6") else "0"
                secid = f"{secid_prefix}.{code}"
                
                url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
                params = {
                    "secid": secid,
                    "fields1": "f1,f2,f3,f4,f5,f6",
                    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                    "klt": "101", # Daily
                    "fqt": "1",   # QFQ
                    "end": "20500101",
                    "lmt": str(days * 3 + 20) # Limit lines to fetch
                }
                
                r = requests.get(url, params=params, timeout=5)
                data_json = r.json()
                
                if data_json["data"] is None:
                    print(f"Data is None for {name}: {data_json.get('msg')}")
                    results[name] = (None, code)
                    continue
                    
                klines = data_json["data"]["klines"]
                
                # Parse klines: "date,open,close,high,low,..."
                parsed_data = []
                for line in klines:
                    parts = line.split(",")
                    parsed_data.append({
                        "日期": pd.to_datetime(parts[0]),
                        "收盘": float(parts[2])
                    })
                
                df = pd.DataFrame(parsed_data)
                
                self.cache[code] = df
                self.cache_time[code] = datetime.now()
                results[name] = (df, code) # Return tuple (df, code) to keep track
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                results[name] = (None, code)
        
        return results

    def calculate_momentum(self, n_days=15, etf_list=None):
        """
        计算动量：涨幅 * R^2
        """
        if etf_list is None:
            etf_list = self.default_etfs
            
        data_map = self.get_data(etf_list, days=n_days)
        rankings = []
        
        # Track which codes we have processed to ensure we return all input ETFs
        processed_codes = set()

        for name, data_tuple in data_map.items():
            if data_tuple is None:
                continue
            
            df, code = data_tuple
            processed_codes.add(code)
            
            if df is None or len(df) < n_days:
                print(f"Insufficient data for {name}: {len(df) if df is not None else 'None'}")
                rankings.append({
                    "name": name,
                    "code": code,
                    "price": 0,
                    "return_pct": 0,
                    "r_squared": 0,
                    "score": -9999,
                    "date": "Data Insufficient",
                    "error": True
                })
                continue
            
            # 取最近 n_days 的数据
            recent_df = df.iloc[-n_days:].copy()
            if len(recent_df) < 5: # 数据太少无法计算 R2
                rankings.append({
                    "name": name,
                    "code": code,
                    "price": 0,
                    "return_pct": 0,
                    "r_squared": 0,
                    "score": -9999,
                    "date": "Data Insufficient",
                     "error": True
                })
                continue

            # 1. 计算涨幅 (Return)
            start_price = recent_df.iloc[0]['收盘']
            end_price = recent_df.iloc[-1]['收盘']
            pct_change = (end_price - start_price) / start_price

            # 2. 计算 R^2 (R-squared)
            # 使用线性回归: Price vs Time (0, 1, 2, ... n-1)
            y = recent_df['收盘'].values
            x = np.arange(len(y))
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            r_squared = r_value ** 2

            # 3. 动量得分
            # 用户公式: n(涨幅) * R^2
            # 只有当涨幅为正时，R^2 才有意义来强化“平稳上涨”的概念
            # 如果涨幅为负，R^2 高说明是“平稳下跌”，此时动量应该是负的
            
            # 简单处理：保留涨幅的符号
            momentum_score = pct_change * r_squared

            rankings.append({
                "name": name,
                "code": code,
                "price": round(end_price, 3),
                "return_pct": round(pct_change * 100, 2),
                "r_squared": round(r_squared, 4),
                "score": round(momentum_score * 100, 4), # 放大100倍方便看
                "date": recent_df.iloc[-1]['日期'].strftime("%Y-%m-%d"),
                "error": False
            })
            
        # Ensure any ETFs that failed completely (returned None in get_data) are also added
        for item in etf_list:
            if item['code'] not in processed_codes:
                 rankings.append({
                    "name": item['name'],
                    "code": item['code'],
                    "price": 0,
                    "return_pct": 0,
                    "r_squared": 0,
                    "score": -9999,
                    "date": "Fetch Failed",
                    "error": True
                })

        # 排序：分数从高到低
        rankings.sort(key=lambda x: x['score'], reverse=True)
        return rankings
