# LLMHandler.py
"""
Ein generischer Wrapper, der **OpenAI**, **Gemini** (Google‑Gemini) und **Ollama** über eine einheitliche
API anspricht.

Alle Back‑Ends können nicht nur reinen Text, sondern auch Dateien (Text‑ oder Bild‑Inhalte)
übergeben bekommen – die Inhalte werden automatisch in die jeweilige Anfrage integriert.

Nutze das Skript wie:

    handler = LLMHandler("ollama")
    answer = handler.get_answer(
        prompt="Erkläre die Relativitätstheorie.",
        files=["text.txt", "image.png"],
        temperature=0.7,
        max_tokens=512,
        stream=True
    )
"""

import os
import mimetypes
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Laden der Umgebungs‑Variablen
# --------------------------------------------------------------------------- #
load_dotenv(override=True)


# --------------------------------------------------------------------------- #
# Helper – Datei‑inhalte lesen
# --------------------------------------------------------------------------- #
def _read_file_content(path: Union[str, Path]) -> bytes:
    """Liest den Inhalt einer Datei (Binary)."""
    with open(path, "rb") as f:
        return f.read()


def _is_image(path: Union[str, Path]) -> bool:
    """Bestimmt, ob die Datei ein Bild ist (nach MIME‑Typ)."""
    mime, _ = mimetypes.guess_type(path)
    return mime is not None and mime.startswith("image/")


# --------------------------------------------------------------------------- #
# Haupt‑Klasse
# --------------------------------------------------------------------------- #
class LLMHandler:
    """
    Wrapper, der OpenAI, Gemini oder Ollama über ein einheitliches Interface anspricht.

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

    # --------------------------------------------------------------------- #
    #  Backend‑Initialisierung
    # --------------------------------------------------------------------- #
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
            raise ValueError(
                f"Unbekannter llm_type '{self.llm_type}'. "
                "Verwende 'ollama', 'openai' oder 'gemini'."
            )

    # --------------------------------------------------------------------- #
    #  Interface
    # --------------------------------------------------------------------- #
    def get_answer(
        self,
        prompt: str,
        *,
        files: Optional[Sequence[Union[str, Path]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """
        Fragt das hinterlegte LLM mit dem gegebenen Prompt ab.

        Parameters
        ----------
        prompt : str
            Der zu beantwortende Text.
        files : sequence of Path | str | None
            Pfade zu Dateien, deren Inhalt (Text oder Bild) in die Anfrage integriert wird.
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
        # ----- Vorverarbeitung der Dateien --------------------------------
        file_bytes: List[bytes] = []
        file_texts: List[str] = []
        if files:
            for fp in files:
                data = _read_file_content(fp)
                if _is_image(fp):
                    file_bytes.append(data)
                else:
                    try:
                        file_texts.append(data.decode("utf-8"))
                    except Exception:
                        file_texts.append(data.decode("latin1"))  # Fallback

        # ----- Aufruf je Backend -----------------------------------------
        if self.llm_type == "ollama":
            return self._ollama_answer(
                prompt,
                file_bytes=file_bytes,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
        elif self.llm_type == "openai":
            combined_prompt = "\n\n".join(file_texts + [prompt]) if file_texts else prompt
            return self._openai_answer(combined_prompt)
        elif self.llm_type == "gemini":
            return self._gemini_answer(
                prompt,
                file_bytes=file_bytes,
                temperature=temperature,
                stream=stream,
            )
        else:  # pragma: no cover
            raise RuntimeError("Unreachable")

    # --------------------------------------------------------------------- #
    #  Unterfunktionen pro Backend
    # --------------------------------------------------------------------- #
    def _ollama_answer(
        self,
        prompt: str,
        *,
        file_bytes: List[bytes],
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> str:
        opts: Dict[str, Any] = {}
        if temperature is not None:
            opts["temperature"] = temperature
        if max_tokens is not None:
            opts["num_predict"] = max_tokens

        # Ollama erwartet `images=[Image]` – unser bytes‑Objekt wird vom Serializer in base64 konvertiert
        images = file_bytes if file_bytes else None

        if stream:
            chunks = []
            for part in self.client.generate(
                model=self.model,
                prompt=prompt,
                options=opts,
                stream=True,
                images=images,
            ):
                chunks.append(part["response"])
            return "".join(chunks)

        resp = self.client.generate(
            model=self.model,
            prompt=prompt,
            options=opts,
            images=images,
        )
        return resp["response"]

    def _openai_answer(self, prompt: str) -> str:
        resp = self.client.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    def _gemini_answer(
        self,
        prompt: str,
        *,
        file_bytes: List[bytes],
        temperature: Optional[float],
        stream: bool,
    ) -> str:
        model = self.client.GenerativeModel(self.model, temperature=temperature)

        # Für Gemini können wir "parts" nutzen – Text + Bilder
        parts: List[Any] = [prompt]  # erster Teil: reiner Text

        for idx, data in enumerate(file_bytes):
            mime, _ = mimetypes.guess_type(f"file{idx}")
            if not mime:
                mime = "application/octet-stream"
            part = {
                "image": {
                    "mime_type": mime,
                    "data": data.decode("latin1")  # google‑genai erwartet str (base64‑decodable)
                }
            }
            parts.append(part)

        response = model.generate_content(parts, stream=stream)

        if stream:
            return "".join(part.text for part in response)
        return response.text
