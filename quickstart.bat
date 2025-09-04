@echo off
REM Prüfen, ob venv-Ordner existiert
if not exist ".venv\" (
    echo Erstelle eine neue virtuelle Umgebung...
    python -m venv .venv

    REM venv aktivieren
    call .venv\Scripts\activate.bat

    REM Dependencies installieren, falls requirements.txt vorhanden
    if exist requirements.txt (
        echo Installiere Dependencies...
        pip install --upgrade pip
        pip install -r requirements.txt
    ) else (
        echo ⚠️  Keine requirements.txt gefunden, ueberspringe Installation.
    )
) else (
    REM venv aktivieren
    echo "Aktiviere VNEV"
    call .venv\Scripts\activate.bat
)

REM LLMHandler starten
echo 🚀 Starte LLMHandler...

python dummy.py -m ollama -p "Erzähl mir einen mittelalterlichen Witz"

echo
echo =============================

python dummy.py -m ollama -f input/prompt.txt 

endlocal
pause