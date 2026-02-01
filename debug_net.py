import requests
import os

def check_net():
    print("Checking network...")
    # 1. Check Baidu (General Internet)
    try:
        r = requests.get("https://www.baidu.com", timeout=5)
        print(f"Baidu: {r.status_code}")
    except Exception as e:
        print(f"Baidu Fail: {e}")

    # 2. Check EastMoney (Data Source), mocking akshare's target
    try:
        # One of the APIs akshare uses
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get" 
        r = requests.get(url, timeout=5)
        print(f"EastMoney: {r.status_code}")
    except Exception as e:
        print(f"EastMoney Fail: {e}")

if __name__ == "__main__":
    check_net()
