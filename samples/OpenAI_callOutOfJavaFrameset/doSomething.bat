ECHO OFF
call .venv/Scripts/activate
REM %1 is the parameter of text input
ECHO ON
python openaiCaller.py %1