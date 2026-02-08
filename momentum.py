import requests
from datetime import datetime
import math

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
        返回结果为 list of dicts: [{"日期": str, "收盘": float}, ...]
        """
        results = {}
        # Increase lookback window to ensure enough trading days
        # Simple date diff approximation
        
        # Use simple string formatting for dates
        # Note: We don't strictly need start/end date for EastMoney API 'lmt' param,
        # but we keep logic similar.
        
        for item in etf_list:
            name = item['name']
            code = item['code']
            
            # Check cache (simple 1-hour cache based on code)
            if code in self.cache and (datetime.now() - self.cache_time.get(code, datetime.min)).seconds < 3600:
                 results[name] = (self.cache[code], code)
                 continue

            try:
                # Direct fetch from EastMoney API
                print(f"Fetching data for {name} ({code})...")
                
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
                    # parts[0] is date "YYYY-MM-DD"
                    # parts[2] is close price
                    parsed_data.append({
                        "日期": parts[0], 
                        "收盘": float(parts[2])
                    })
                
                self.cache[code] = parsed_data
                self.cache_time[code] = datetime.now()
                results[name] = (parsed_data, code)
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                results[name] = (None, code)
        
        return results

    def simple_linregress(self, y_values):
        """
        计算简单的线性回归 y = mx + c
        返回: (slope, r_squared)
        x 默认为 0, 1, 2, ... len(y)-1
        """
        n = len(y_values)
        if n < 2:
            return 0, 0
        
        x_values = list(range(n))
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xx = sum(x * x for x in x_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_yy = sum(y * y for y in y_values)
        
        # Calculate slope (m) and intercept (c)
        denominator = n * sum_xx - sum_x * sum_x
        if denominator == 0:
            return 0, 0
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        # intercept = (sum_y - slope * sum_x) / n # Not needed for R2
        
        # Calculate R^2
        # r = (n*sum_xy - sum_x*sum_y) / sqrt((n*sum_xx - sum_x^2)(n*sum_yy - sum_y^2))
        numerator_r = (n * sum_xy - sum_x * sum_y)
        denominator_r_sq = (n * sum_xx - sum_x ** 2) * (n * sum_yy - sum_y ** 2)
        
        if denominator_r_sq <= 0:
            return slope, 0
            
        r_value = numerator_r / math.sqrt(denominator_r_sq)
        r_squared = r_value ** 2
        
        return slope, r_squared

    def calculate_momentum(self, n_days=15, etf_list=None):
        """
        计算动量：涨幅 * R^2
        """
        if etf_list is None:
            etf_list = self.default_etfs
            
        data_map = self.get_data(etf_list, days=n_days)
        rankings = []
        
        processed_codes = set()

        for name, data_tuple in data_map.items():
            if data_tuple is None:
                continue
            
            data_list, code = data_tuple
            processed_codes.add(code)
            
            if data_list is None or len(data_list) < n_days:
                print(f"Insufficient data for {name}: {len(data_list) if data_list else 'None'}")
                rankings.append({
                    "name": name,
                    "code": code,
                    "price": 0,
                    "return_pct": 0,
                    "r_squared": 0,
                    "score": -9999,
                    "date": "数据不足",
                    "error": True
                })
                continue
            
            # 取最近 n_days 的数据
            recent_data = data_list[-n_days:]
            if len(recent_data) < 5: 
                rankings.append({
                    "name": name,
                    "code": code,
                    "price": 0,
                    "return_pct": 0,
                    "r_squared": 0,
                    "score": -9999,
                    "date": "数据不足",
                     "error": True
                })
                continue

            # 1. 计算涨幅 (Return)
            start_price = recent_data[0]['收盘']
            end_price = recent_data[-1]['收盘']
            
            if start_price == 0:
                pct_change = 0
            else:
                pct_change = (end_price - start_price) / start_price

            # 2. 计算 R^2 (R-squared)
            y_values = [d['收盘'] for d in recent_data]
            slope, r_squared = self.simple_linregress(y_values)

            # 3. 动量得分
            momentum_score = pct_change * r_squared

            rankings.append({
                "name": name,
                "code": code,
                "price": round(end_price, 3),
                "return_pct": round(pct_change * 100, 2),
                "r_squared": round(r_squared, 4),
                "score": round(momentum_score * 100, 4), 
                "date": recent_data[-1]['日期'],
                "error": False
            })
            
        # Ensure any ETFs that failed completely are also added
        for item in etf_list:
            if item['code'] not in processed_codes:
                 rankings.append({
                    "name": item['name'],
                    "code": item['code'],
                    "price": 0,
                    "return_pct": 0,
                    "r_squared": 0,
                    "score": -9999,
                    "date": "获取失败",
                    "error": True
                })

        # 排序：分数从高到低
        rankings.sort(key=lambda x: x['score'], reverse=True)
        return rankings
