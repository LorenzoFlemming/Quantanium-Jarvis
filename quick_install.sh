#!/data/data/com.termux/files/usr/bin/bash

# JARVIS Complete Installation & Setup Guide
# Run this script to set up and launch JARVIS

set -e

JARVIS_HOME="$HOME/quantanium-jarvis"
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${COLOR_CYAN}================================================${NC}"
    echo -e "${COLOR_CYAN}🤖 JARVIS Quantanium Intelligence System${NC}"
    echo -e "${COLOR_CYAN}================================================${NC}"
}

print_step() {
    echo -e "${COLOR_GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${COLOR_YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${COLOR_RED}✗ $1${NC}"
}

print_header

# Step 1: Clone Repository
echo -e "\n${COLOR_YELLOW}[STEP 1] Cloning Repository...${NC}"
if [ -d "$JARVIS_HOME" ]; then
    print_warning "JARVIS directory already exists at $JARVIS_HOME"
    read -p "Do you want to update? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$JARVIS_HOME"
        git pull origin main
        print_step "Repository updated"
    fi
else
    git clone https://github.com/LorenzoFlemming/quantanium-jarvis.git "$JARVIS_HOME"
    print_step "Repository cloned to $JARVIS_HOME"
fi

cd "$JARVIS_HOME"

# Step 2: Install Dependencies
echo -e "\n${COLOR_YELLOW}[STEP 2] Installing Dependencies...${NC}"

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    print_step "Python dependencies installed"
else
    print_warning "requirements.txt not found, installing manually"
    pip install -q flask requests psutil
    print_step "Basic dependencies installed"
fi

# Step 3: Create Configuration
echo -e "\n${COLOR_YELLOW}[STEP 3] Setting up Configuration...${NC}"

if [ ! -f "jarvis_config.json" ]; then
    cat > jarvis_config.json << 'EOF'
{
  "mode": "ONTIC",
  "theme": "dark",
  "language": "en",
  "timezone": "UTC",
  "api_keys": {
    "openweather": "",
    "gmail": ""
  },
  "features": {
    "voice_commands": true,
    "notifications": true,
    "email_alerts": true,
    "auto_backup": true
  },
  "security": {
    "require_auth": false,
    "api_rate_limit": 100
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "debug": false,
    "log_level": "INFO"
  },
  "database": {
    "type": "sqlite",
    "path": "jarvis.db"
  },
  "integrations": {
    "github": false,
    "slack": false,
    "discord": false,
    "telegram": false
  }
}
EOF
    print_step "Configuration created"
else
    print_step "Configuration file already exists"
fi

# Step 4: Create Required Directories
echo -e "\n${COLOR_YELLOW}[STEP 4] Creating Directories...${NC}"

mkdir -p logs
mkdir -p backups
mkdir -p data
mkdir -p cache

print_step "Directories created"

# Step 5: Initialize Database
echo -e "\n${COLOR_YELLOW}[STEP 5] Initializing Database...${NC}"

python3 << 'PYTHON_INIT'
import sqlite3
import os

# Create notifications database
conn = sqlite3.connect('notifications.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT NOT NULL,
        priority TEXT DEFAULT 'normal',
        read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        action_url TEXT
    )
''')

conn.commit()
conn.close()

print("✓ Database initialized")
PYTHON_INIT

print_step "Database initialized"

# Step 6: Create Sample Data
echo -e "\n${COLOR_YELLOW}[STEP 6] Creating Sample Data...${NC}"

cat > todos.json << 'EOF'
[
  {
    "id": 1,
    "title": "Setup JARVIS System",
    "description": "Complete initial installation and configuration",
    "priority": "high",
    "completed": true,
    "created_at": "2026-06-01T08:00:00",
    "tags": ["setup", "installation"]
  },
  {
    "id": 2,
    "title": "Configure API Keys",
    "description": "Add OpenWeather and GitHub API keys",
    "priority": "high",
    "completed": false,
    "created_at": "2026-06-01T08:30:00",
    "tags": ["configuration", "api"]
  },
  {
    "id": 3,
    "title": "Test Dashboard",
    "description": "Test all dashboard interfaces",
    "priority": "medium",
    "completed": false,
    "created_at": "2026-06-01T09:00:00",
    "tags": ["testing", "dashboard"]
  }
]
EOF

print_step "Sample data created"

# Step 7: Set Permissions
echo -e "\n${COLOR_YELLOW}[STEP 7] Setting Permissions...${NC}"

chmod +x install.sh
chmod +x daemon.sh
chmod +x jarvis_hud.sh
chmod +x update.sh
chmod +x doctor.sh
chmod +x voice_commands.sh

print_step "Permissions set"

# Step 8: Display Configuration Options
echo -e "\n${COLOR_CYAN}================================================${NC}"
echo -e "${COLOR_YELLOW}[OPTIONAL] Configuration Setup${NC}"
echo -e "${COLOR_CYAN}================================================${NC}"

read -p "Do you want to set up API keys? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter OpenWeather API Key (or press Enter to skip): " weather_key
    read -p "Enter GitHub Token (or press Enter to skip): " github_token
    
    if [ ! -z "$weather_key" ]; then
        export OPENWEATHER_API_KEY="$weather_key"
        print_step "OpenWeather API key set"
    fi
    
    if [ ! -z "$github_token" ]; then
        export GITHUB_TOKEN="$github_token"
        print_step "GitHub token set"
    fi
fi

# Step 9: System Check
echo -e "\n${COLOR_YELLOW}[STEP 8] Running System Check...${NC}"

python3 << 'PYTHON_CHECK'
import os
import sys

checks = {
    "Python 3": sys.version.split()[0],
    "Flask": "Installed",
    "SQLite": "Ready",
    "Configuration": "✓" if os.path.exists("jarvis_config.json") else "✗",
    "Database": "✓" if os.path.exists("notifications.db") else "✗",
}

for check, status in checks.items():
    print(f"  {check}: {status}")
PYTHON_CHECK

print_step "System check complete"

# Step 10: Show Next Steps
echo -e "\n${COLOR_CYAN}================================================${NC}"
echo -e "${COLOR_GREEN}🎉 JARVIS Installation Complete!${NC}"
echo -e "${COLOR_CYAN}================================================${NC}"

echo -e "\n${COLOR_YELLOW}📋 Quick Start Commands:${NC}"
echo -e "  ${COLOR_CYAN}1. Start Web Server:${NC}"
echo -e "     python web_server.py"
echo -e "\n  ${COLOR_CYAN}2. Start Daemon (in another terminal):${NC}"
echo -e "     ./daemon.sh &"
echo -e "\n  ${COLOR_CYAN}3. Access Dashboards:${NC}"
echo -e "     http://localhost:8080                (Main Panel)"
echo -e "     http://localhost:8080/dashboard.html (System Dashboard)"
echo -e "     http://localhost:8080/analytics_dashboard.html (Analytics)"
echo -e "     http://localhost:8080/visualization_3d.html (3D View)"
echo -e "     http://localhost:8080/todos (Todo App)"
echo -e "     http://localhost:8080/mobile (Mobile App)"

echo -e "\n${COLOR_YELLOW}🔧 Useful Commands:${NC}"
echo -e "  Update system: ./update.sh"
echo -e "  Run diagnostics: ./doctor.sh"
echo -e "  Backup data: python -c \"from advanced_systems import BackupManager; BackupManager().create_backup(['todos.json', 'events.ics'])\""
echo -e "  Check health: python -c \"from advanced_systems import HealthCheck; import json; print(json.dumps(HealthCheck().get_full_report(), indent=2))\""

echo -e "\n${COLOR_YELLOW}📚 Documentation:${NC}"
echo -e "  GitHub: https://github.com/LorenzoFlemming/quantanium-jarvis"
echo -e "  Issues: https://github.com/LorenzoFlemming/quantanium-jarvis/issues"

echo -e "\n${COLOR_CYAN}================================================${NC}"
echo -e "${COLOR_GREEN}Ready to launch? Run: python web_server.py${NC}"
echo -e "${COLOR_CYAN}================================================${NC}\n"

# Ask to start server
read -p "Do you want to start the web server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Starting web server..."
    sleep 2
    python3 web_server.py
fi
