from flask import Flask, request, jsonify
import subprocess, json, os

app = Flask(__name__)
CONFIG = "config.json"

def load_config():
    if not os.path.exists(CONFIG):
        return {"mode": "ONTIC"}
    return json.load(open(CONFIG))

def save_config(cfg):
    json.dump(cfg, open(CONFIG, "w"), indent=2)

@app.route("/")
def home():
    return open("web_panel.html").read()

@app.route("/agents")
def agents():
    return open("agent_dashboard.html").read()

@app.route("/api/mode", methods=["POST"])
def set_mode():
    cfg = load_config()
    if request.json and "mode" in request.json:
        cfg["mode"] = request.json["mode"]
        save_config(cfg)
        return jsonify({"status": "ok"})
    return jsonify({"error": "Invalid request"}), 400

@app.route("/api/command", methods=["POST"])
def command():
    if request.json and "cmd" in request.json:
        cmd = request.json["cmd"]
        out = subprocess.getoutput(f"python jarvis_core.py --cmd \"{cmd}\"")
        return jsonify({"output": out})
    return jsonify({"error": "Invalid request"}), 400

@app.route("/api/status")
def status():
    return jsonify({"running": True, "config": load_config()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
