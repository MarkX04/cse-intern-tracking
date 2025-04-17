from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import threading, time, json, os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://MarkX04.github.io", "http://127.0.0.1:5500"]}})

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

cached_company_data = {}

def load_company_data_from_files(folder="data_histories"):
    company_data = {}
    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue
        comp_id = filename[:-5]
        path = os.path.join(folder, filename)
        with open(path, encoding="utf-8") as f:
            history = json.load(f)
        if history:
            company_data[comp_id] = history[-1]
    return company_data

def update_company_data_periodically():
    global cached_company_data
    while True:
        new_data = load_company_data_from_files()
        cached_company_data = new_data
        socketio.emit('company_update', cached_company_data)
        print("Broadcast company_update at", time.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(60)

@app.route("/api/company_data", methods=["GET"])
def api_get_company_data():
    if cached_company_data:
        return jsonify(cached_company_data), 200
    return jsonify({"error": "No data"}), 500

if __name__ == "__main__":
    thread = threading.Thread(target=update_company_data_periodically, daemon=True)
    thread.start()
    socketio.run(app, host="0.0.0.0", port=5001)
