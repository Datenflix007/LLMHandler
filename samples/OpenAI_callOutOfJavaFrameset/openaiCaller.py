import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

class PythonClass:
    def __init__(self, value):
        self.value = value
        #print(f"PythonClass initialisiert mit Wert: {self.value}")
        
        load_dotenv()
        #print(os.getenv("OPENAI_API_KEY"))  # Sollte den API-Schlüssel ausgeben, wenn richtig gesetzt
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": self.value}]
        )

        # Antwort des Modells ausgeben (UTF-8 kodiert)
        result = completion.choices[0].message.content.strip()
        
        # Sicherstellen, dass wir die Antwort korrekt als UTF-8 ausgeben
        sys.stdout.buffer.write(result.encode('utf-8'))
        sys.stdout.flush()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Das Argument von der Batch-Datei holen
        arg_value = sys.argv[1]
        # Python-Klasse mit dem Argument instanziieren
        python_class_instance = PythonClass(arg_value)
    else:
        print("Kein Argument übergeben.")
