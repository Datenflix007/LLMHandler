# LLMHandler.py
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Lade die .env‑Variablen (nur einmal)
load_dotenv(override=True)


class LLMHandler:
    """Ein Wrapper, der OpenAI, Gemini oder Ollama über einen einheitlichen
    Interface anspricht.

    Parameters
    ----------
    llm_type : str
        'ollama' | 'openai' | 'gemini'
    model   : str | None
        Optionaler Modell‑Name, überschreibt die Umgebungs‑Variable.
    host    : str | None
        Nur für Ollama: Host‑URL (z. B. http://localhost:11434)
    """

    def __init__(self, llm_type: str, *, model: Optional[str] = None, host: Optional[str] = None):
        self.llm_type = llm_type.lower()
        self._load_backend(model, host)

    # ------------------------------------------------------------------ #
    #  Backend‑Initialisierung
    # ------------------------------------------------------------------ #
    def _load_backend(self, model: Optional[str], host: Optional[str]) -> None:
        """Lädt die passende Bibliothek und setzt globale Konfigurationen."""
        if self.llm_type == "ollama":
            import ollama
            self.client = ollama
            self.host = host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
            self.model = model or os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
        elif self.llm_type == "openai":
            import openai
            self.client = openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        elif self.llm_type == "gemini":
            import google.generativeai as genai
            self.client = genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        else:
            raise ValueError(f"Unbekannter llm_type '{self.llm_type}'. "
                             "Verwende 'ollama', 'openai' oder 'gemini'.")

    # ------------------------------------------------------------------ #
    #  Interface
    # ------------------------------------------------------------------ #
    def get_answer(self,
                   prompt: str,
                   *,
                   temperature: Optional[float] = None,
                   max_tokens: Optional[int] = None,
                   stream: bool = False) -> str:
        """Fragt das hinterlegte LLM mit dem gegebenen Prompt ab.

        Parameters
        ----------
        prompt : str
            Der zu beantwortende Text.
        temperature : float | None
            Stimmt die Kreativität des Modells ab (nur bei Ollama & Gemini).
        max_tokens : int | None
            Maximale Anzahl an Token (nur bei Ollama & Gemini).
        stream : bool
            Bei `True` wird die Antwort schrittweise zurückgegeben (nur bei Ollama & Gemini).

        Returns
        -------
        str
            Die Antwort des Modells.
        """
        if self.llm_type == "ollama":
            return self._ollama_answer(prompt, temperature, max_tokens, stream)
        elif self.llm_type == "openai":
            return self._openai_answer(prompt)
        elif self.llm_type == "gemini":
            return self._gemini_answer(prompt, temperature, stream)
        else:  # pragma: no cover
            raise RuntimeError("Unreachable")

    # ------------------------------------------------------------------ #
    #  Unterfunktionen pro Backend
    # ------------------------------------------------------------------ #
    def _ollama_answer(self, prompt: str,
                       temperature: Optional[float],
                       max_tokens: Optional[int],
                       stream: bool) -> str:
        opts: Dict[str, Any] = {}
        if temperature is not None:
            opts["temperature"] = temperature
        if max_tokens is not None:
            opts["num_predict"] = max_tokens

        if stream:
            # Bei Streaming gibt ollama einen Iterator zurück
            chunks = []
            for part in self.client.generate(
                model=self.model,
                prompt=prompt,
                options=opts,
                stream=True
            ):
                chunks.append(part["response"])
            return "".join(chunks)

        resp = self.client.generate(
            model=self.model,
            prompt=prompt,
            options=opts
        )
        return resp["response"]

    def _openai_answer(self, prompt: str) -> str:
        resp = self.client.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    def _gemini_answer(self, prompt: str,
                       temperature: Optional[float],
                       stream: bool) -> str:
        model = self.client.GenerativeModel(self.model,
                                            temperature=temperature)
        response = model.generate_content(prompt, stream=stream)
        # google‑generative‑ai liefert bei stream ein Generator
        if stream:
            return "".join(part.text for part in response)
        return response.text
