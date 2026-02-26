@echo off
REM Lance le jeu Pokemon Battle.
REM Usage : run.bat

cd /d "%~dp0"

REM Creer le venv si absent
if not exist "venv" (
    echo Creation du venv...
    py -m venv venv
)

REM Activer le venv et installer les dependances
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

REM Lancer le jeu
py main.py
