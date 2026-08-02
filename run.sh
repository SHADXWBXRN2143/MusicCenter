#!/bin/bash

#
# ===========================================================
# MusicCenter
# -----------------------------------------------------------
# Startup Script
#
# Version : 0.1
# ===========================================================
#


PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"


VENV_DIR="$PROJECT_DIR/venv"


APP_FILE="app:app"



echo "===================================="

echo " Starting MusicCenter "

echo "===================================="



cd "$PROJECT_DIR" || exit 1



# ==========================================
# Check virtual environment
# ==========================================


if [ ! -d "$VENV_DIR" ]

then

    echo "Virtual environment not found."

    echo "Creating venv..."

    python3 -m venv "$VENV_DIR"

fi



# ==========================================
# Activate environment
# ==========================================


source "$VENV_DIR/bin/activate"





# ==========================================
# Update pip
# ==========================================


python3 -m pip install --upgrade pip





# ==========================================
# Install requirements
# ==========================================


if [ -f "requirements.txt" ]

then

    echo "Checking dependencies..."

    pip install -r requirements.txt

fi





# ==========================================
# Start server
# ==========================================


echo ""

echo "Starting Gunicorn..."

echo ""



# Single worker: the player/queue state and the mpv process are
# in-memory singletons, so more than one worker process would each
# spawn its own mpv and disagree about what's playing.
exec gunicorn \
--workers 1 \
--threads 4 \
--bind 0.0.0.0:5000 \
--access-logfile - \
--error-logfile - \
app:app
