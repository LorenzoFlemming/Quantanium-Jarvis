#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[JARVIS] Updating Termux..."
pkg update -y
pkg upgrade -y

echo "[JARVIS] Installing base packages..."
pkg install -y python git ffmpeg termux-api termux-tools cmake make clang

echo "[JARVIS] Installing Python modules..."
pip install -r requirements.txt

echo "[JARVIS] Installing Whisper.cpp..."
if [ ! -d "whisper.cpp" ]; then
  git clone https://github.com/ggerganov/whisper.cpp
fi
cd whisper.cpp
make
bash ./models/download-ggml-model.sh base.en
cd ..

echo "[JARVIS] Ensuring config..."
if [ ! -f config.json ]; then
  cat > config.json << 'EOF'
{
  "mode": "ONTIC"
}
EOF
fi

echo "[JARVIS] Creating HUD launcher..."
cat > jarvis_hud.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/quantanium-jarvis
python hud.py
EOF
chmod +x jarvis_hud.sh

echo "[JARVIS] Creating daemon..."
cat > daemon.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/quantanium-jarvis
while true; do
    python jarvis_core.py >> daemon.log 2>&1
    sleep 2
done
EOF
chmod +x daemon.sh

echo "[JARVIS] Creating update script..."
cat > update.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/quantanium-jarvis
git pull
pip install -r requirements.txt --upgrade
echo "[JARVIS] Updated."
EOF
chmod +x update.sh

echo "[JARVIS] Creating doctor..."
cat > doctor.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
echo "[JARVIS] Termux info:"
termux-info
echo "[JARVIS] Python:"
python - << 'PY'
import sys
print("Python:", sys.version)
PY
echo "[JARVIS] Done."
EOF
chmod +x doctor.sh

echo "[JARVIS] Install complete."
echo "Run: ./daemon.sh &"
echo "HUD: ./jarvis_hud.sh"
echo "Web: python web_server.py"
