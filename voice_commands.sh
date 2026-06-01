#!/data/data/com.termux/files/usr/bin/bash

# JARVIS Voice Command Parser
# Integrates speech-to-text with command execution

set -e

JARVIS_HOME="$HOME/quantanium-jarvis"
LOG_FILE="$JARVIS_HOME/voice.log"

log() {
    echo "[JARVIS VOICE] $1" | tee -a "$LOG_FILE"
}

# Check if audio file provided
if [ -z "$1" ]; then
    log "Recording audio for 5 seconds..."
    termux-microphone-record -f "$JARVIS_HOME/voice_input.wav" -d 5
    AUDIO_FILE="$JARVIS_HOME/voice_input.wav"
else
    AUDIO_FILE="$1"
fi

# Transcribe using Whisper
log "Transcribing audio..."
cd "$JARVIS_HOME/whisper.cpp"
TRANSCRIPT=$(./main -m models/ggml-base.en.bin -f "$AUDIO_FILE" 2>/dev/null | grep "\\[" | tail -1 | sed 's/.*\\[//' | sed 's/\\].*//')

log "Transcript: $TRANSCRIPT"

# Parse commands
COMMAND=$(echo "$TRANSCRIPT" | tr '[:upper:]' '[:lower:]')

if [[ "$COMMAND" == *"jarvis"* ]]; then
    log "Wake word detected"
    termux-notification --title "JARVIS" --content "Listening..."
    
    # Extract command after "jarvis"
    CMD_TEXT=$(echo "$COMMAND" | sed 's/.*jarvis //')
    
    # Route commands
    if [[ "$CMD_TEXT" == *"weather"* ]]; then
        log "Weather command detected"
        python "$JARVIS_HOME/jarvis_core.py" --cmd "weather london"
    
    elif [[ "$CMD_TEXT" == *"todo"* ]] || [[ "$CMD_TEXT" == *"add task"* ]]; then
        log "Todo command detected"
        python "$JARVIS_HOME/jarvis_core.py" --cmd "todo"
    
    elif [[ "$CMD_TEXT" == *"status"* ]]; then
        log "Status command detected"
        python "$JARVIS_HOME/jarvis_core.py" --cmd "status"
    
    elif [[ "$CMD_TEXT" == *"shutdown"* ]]; then
        log "Shutdown command detected"
        termux-notification --title "JARVIS" --content "Shutting down..."
        pkill -f "python jarvis_core.py"
    
    elif [[ "$CMD_TEXT" == *"mode"* ]]; then
        log "Mode command detected"
        MODE=$(echo "$CMD_TEXT" | sed 's/.*mode //' | tr '[:lower:]' '[:upper:]')
        python "$JARVIS_HOME/jarvis_core.py" --cmd "mode $MODE"
    
    else
        log "Unknown command: $CMD_TEXT"
        termux-notification --title "JARVIS" --content "Command not recognized"
    fi
    
    termux-notification --title "JARVIS" --content "Command executed"
else
    log "Wake word not detected"
fi
