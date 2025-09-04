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
    echo "Aktiviere VENV"
    call .venv\Scripts\activate.bat
)


REM ----------------------------------------------
REM 3️⃣ Demo‑Aufruf
REM ----------------------------------------------
echo 🚀 Starte LLMHandler...
python dummy.py -m ollama -p "Schreibe mir einen kleinen Aufsatz über die Zirkusparteien von Konstantinopel. Schreibe so in die Datei, sodass die Datei in Microsoft Word ausführbar und normal nutzbar ist. Formalia: Blocksatz, Schrift New Roman und Schriftgröße 12." -l 100000000 -O output\Aufsatz.docx
REM python dummy.py -m ollama -p "Programmiere die Aufgabe" -F input/prompt.txt -l 1000 -O output\index.html

pause