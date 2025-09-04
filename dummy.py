# demo.py
from LLMHandler import LLMHandler

def main():
    prompt = "Erkläre die Relativitätstheorie in einfachen Worten."

    # 1️⃣ Ollama
    ollama_handler = LLMHandler("ollama")
    print("\n=== Ollama ===")
    print(ollama_handler.get_answer(prompt, temperature=0.7, max_tokens=300))

    # 2️⃣ OpenAI
    #openai_handler = LLMHandler("openai")
    #print("\n=== OpenAI ===")
    #print(openai_handler.get_answer(prompt))

    # 3️⃣ Gemini
    #gemini_handler = LLMHandler("gemini")
    #print("\n=== Gemini ===")
    #print(gemini_handler.get_answer(prompt, temperature=0.6))

if __name__ == "__main__":
    main()
