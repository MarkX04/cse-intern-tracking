from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://MarkX04.github.io", "http://127.0.0.1:5500"]}})

cached_company_data = {}

def load_company_data_from_files(folder="data_histories"):
    company_data = {}

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            company_id = filename[:-5] 
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    history = json.load(f)
                if history:
                    company_data[company_id] = history[-1]
            except Exception as e:
                print(f"Error {filename}: {e}")
    return company_data

def update_company_data_periodically():
    global cached_company_data
    while True:
        try:
            cached_company_data = load_company_data_from_files()
            print("Update cache company data at:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

@app.route("/api/company_data", methods=["GET"])
def api_get_company_data():
    try:
        if cached_company_data:
            return jsonify(cached_company_data), 200
        else:
            return jsonify({"error": "No company data available"}), 500
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    update_thread = threading.Thread(target=update_company_data_periodically, daemon=True)
    update_thread.start()
    
    app.run(port=5001, debug=True)
