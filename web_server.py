from flask import Flask, request, jsonify, render_template_string
import subprocess, json, os
from todo import TodoManager
from weather import WeatherManager

app = Flask(__name__)
todo_manager = TodoManager()

# Try to initialize weather manager (optional)
try:
    weather_manager = WeatherManager()
except ValueError:
    weather_manager = None

CONFIG = "config.json"

def load_config():
    if not os.path.exists(CONFIG):
        return {"mode": "ONTIC"}
    return json.load(open(CONFIG))

def save_config(cfg):
    json.dump(cfg, open(CONFIG, "w"), indent=2)

# Web Panel Routes
@app.route("/")
def home():
    return open("web_panel.html").read()

@app.route("/agents")
def agents():
    return open("agent_dashboard.html").read()

@app.route("/todos")
def todos_page():
    return open("todo_dashboard.html").read()

# API Routes - Mode Control
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

# API Routes - Todo Management
@app.route("/api/todos", methods=["GET", "POST"])
def todos_api():
    if request.method == "POST":
        data = request.json
        try:
            todo = todo_manager.add_todo(
                data.get("title"),
                data.get("description", ""),
                data.get("priority", "medium")
            )
            return jsonify({"status": "ok", "todo": todo}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    filter_by = request.args.get("filter")
    todos = todo_manager.get_all_todos(filter_by)
    return jsonify({"todos": todos})

@app.route("/api/todos/<int:todo_id>", methods=["GET", "PUT", "DELETE"])
def todo_detail(todo_id):
    if request.method == "GET":
        todo = todo_manager.get_todo(todo_id)
        if not todo:
            return jsonify({"error": "Not found"}), 404
        return jsonify(todo)
    
    elif request.method == "PUT":
        try:
            todo = todo_manager.update_todo(todo_id, **request.json)
            return jsonify(todo)
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
    
    elif request.method == "DELETE":
        if todo_manager.delete_todo(todo_id):
            return jsonify({"status": "ok"})
        return jsonify({"error": "Not found"}), 404

@app.route("/api/todos/<int:todo_id>/complete", methods=["POST"])
def complete_todo(todo_id):
    try:
        todo = todo_manager.complete_todo(todo_id)
        return jsonify(todo)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/todos/<int:todo_id>/tag", methods=["POST"])
def add_todo_tag(todo_id):
    data = request.json
    if not data or "tag" not in data:
        return jsonify({"error": "Tag required"}), 400
    
    try:
        todo = todo_manager.add_tag(todo_id, data["tag"])
        return jsonify(todo)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/stats")
def stats():
    return jsonify(todo_manager.get_stats())

# API Routes - Weather (if API key available)
@app.route("/api/weather/<city>")
def get_weather(city):
    if not weather_manager:
        return jsonify({"error": "Weather API not configured"}), 503
    
    try:
        weather = weather_manager.get_weather_by_city(city)
        return jsonify(weather)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/forecast/<city>")
def get_forecast(city):
    if not weather_manager:
        return jsonify({"error": "Weather API not configured"}), 503
    
    try:
        forecast = weather_manager.get_forecast(city)
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
