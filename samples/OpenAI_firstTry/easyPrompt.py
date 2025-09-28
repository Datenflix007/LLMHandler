from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
#print(os.getenv("OPENAI_API_KEY"))  # Sollte den API-Schlüssel ausgeben, wenn richtig gesetzt
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#client = OpenAI( api_key="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"
#)


# Die Eingabe schön formatieren
question = input("\n TASK: Ask anything to Chat-GPT\n📝>>>")

print("\n\nAnswer:\n")


completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": question}
  ]
)

#print(completion.choices[0].message)
print(completion.choices[0].message.content.strip())


# Funktion zur Kommunikation mit OpenAI
def ask_openai(question):
    #lient = openai.OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}]
    )
    
    # Antwort extrahieren und als sauberer String zurückgeben
    return response.choices[0].message.content.strip()

# Beispiel: Java-spezifische Anfrage
if __name__ == "__main__":
    question = input("Frage an OpenAI: ")  # Nutzer kann Frage eingeben
    answer = ask_openai(question)
    print("\nAntwort:\n", answer)