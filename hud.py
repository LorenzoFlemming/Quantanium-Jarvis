import time, json, os

HUD_FILE = "hudoutput.txt"
CONFIG = "config.json"

def load_cfg():
    if not os.path.exists(CONFIG):
        return {"mode": "ONTIC"}
    return json.load(open(CONFIG))

while True:
    cfg = load_cfg()
    with open(HUD_FILE, "w") as f:
        f.write("QUANTANIUM JARVIS HUD\n")
        f.write(f"Mode: {cfg['mode']}\n")
        f.write("Status: ACTIVE\n")
        f.write("Last Update: " + time.strftime("%H:%M:%S") + "\n")
    time.sleep(1)
