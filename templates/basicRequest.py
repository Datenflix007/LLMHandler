# basicRequest.py
import ollama

# 1️⃣ Prompt definieren
prompt = "Erkläre die Relativitätstheorie in einfachen Worten."

# 2️⃣ Optionen (optional, aber empfohlen)
options = ollama.Options(
    temperature=0.7,      # Wärme‑Einstellung (0–1)
    num_predict=512,      # Max. Tokens in der Antwort
    top_p=0.9,           # Top‑P‑Sampling
    stop=["END"],         # Stop‑Sequenz (falls gewünscht)
)

# 3️⃣ Anfrage
try:
    response = ollama.generate(
        model="gpt-oss:20b",
        prompt=prompt,
        options=options
    )
    print("\n--- Antwort ---")
    print(response["response"])

except ollama.ResponseError as e:
    print(f"Fehler bei der Anfrage: {e}")

except ollama.RequestError as e:
    print(f"Ungültige Anfrage: {e}")
