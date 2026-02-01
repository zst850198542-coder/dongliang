from flask import Flask, render_template, request, jsonify
from momentum import MomentumCalculator

app = Flask(__name__)
calculator = MomentumCalculator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        n_days = int(data.get('n_days', 15))
        etf_list = data.get('etf_list', None) # Expecting list of {name, code}
        
        results = calculator.calculate_momentum(n_days=n_days, etf_list=etf_list)
        
        if not results:
             return jsonify({"status": "error", "message": "无法获取数据或数据不足"}), 500

        best_pick = results[0] if results else None
        
        return jsonify({
            "status": "success",
            "results": results,
            "best_pick": best_pick
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
