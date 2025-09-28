ECHO OFF
python venv .venv
cd .venv/Scripts/
call activate
cd ../../
ECHO ON
python easyPrompt.py