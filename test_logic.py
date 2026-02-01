from momentum import MomentumCalculator
import time

def test_logic():
    print("Initializing Calculator...")
    calc = MomentumCalculator()
    
    print("Fetching data and calculating (n=15)...")
    start_time = time.time()
    results = calc.calculate_momentum(n_days=15)
    end_time = time.time()
    
    print(f"Calculation took {end_time - start_time:.2f} seconds")
    
    if not results:
        print("FAILED: No results returned.")
        return

    print("\nResults:")
    print(f"{'Name':<10} | {'Code':<8} | {'Return%':<8} | {'R2':<6} | {'Score':<8}")
    print("-" * 50)
    for r in results:
        print(f"{r['name']:<10} | {r['code']:<8} | {r['return_pct']:<8} | {r['r_squared']:<6} | {r['score']:<8}")

    print("\nBest Pick:", results[0]['name'])
    print("SUCCESS")

if __name__ == "__main__":
    test_logic()
