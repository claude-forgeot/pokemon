#!/bin/bash
# Lance le jeu Pokemon Battle.
# Usage : ./run.sh

cd "$(dirname "$0")"

# Creer le venv si absent
if [ ! -d "venv" ]; then
    echo "Creation du venv..."
    python3 -m venv venv
fi

# Activer le venv et installer les dependances
source venv/bin/activate
pip install -q -r requirements.txt

# Lancer le jeu
python3 main.py
