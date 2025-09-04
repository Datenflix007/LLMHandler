#!/usr/bin/env python
"""
Einfaches Test‑Skript für die LLMHandler‑Klasse.

Der Benutzer kann entscheiden:

* Welches Backend (ollama, openai, gemini) verwendet werden soll.
* Welcher Prompt gesendet werden soll (oder ein Prompt aus einer Datei).
* Optionalen Pfad zu einer oder mehreren Dateien (Text‑ oder Bild‑Dateien),
  die dem Prompt hinzugefügt werden.

Beispielaufrufe:

    # 1️⃣ Nur Prompt, Ollama
    python dummy.py -m ollama -p "Erkläre die Relativitätstheorie."

    # 2️⃣ Prompt aus einer Textdatei, OpenAI
    python dummy.py -m openai -f prompt.txt

    # 3️⃣ Prompt + Bild, Gemini
    python dummy.py -m gemini -p "Was ist die Relativität?" -f image.png

Der Code verwendet standardmäßig die Umgebungsvariablen aus einer .env‑Datei
(OPENAI_API_KEY, GEMINI_API_KEY, OLLAMA_HOST, OLLAMA_MODEL usw.).
"""

import argparse
import sys
from pathlib import Path
from typing import List

from LLMHandler import LLMHandler


def _read_text_file(path: Path) -> str:
    """Hilfsfunktion, die eine Text‑Datei als UTF‑8 liest."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Fehler beim Lesen von {path!s}: {exc}") from exc


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dummy.py",
        description="Test‑Skript für die LLMHandler‑Klasse.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-m",
        "--model",
        choices=["ollama", "openai", "gemini"],
        default="ollama",
        help="Backend, das benutzt werden soll.",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="Direkter Prompt-Text.",
    )
    group.add_argument(
        "-f",
        "--file",
        type=Path,
        help="Pfad zu einer Text‑Datei, die als Prompt benutzt wird.",
    )

    parser.add_argument(
        "-F",
        "--files",
        type=Path,
        nargs="*",
        help="Zusätzliche Dateien (Text‑ oder Bild‑Dateien), die zusammen mit dem Prompt gesendet werden.",
    )

    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=None,
        help="Temperatur für Ollama / Gemini (0–1).",
    )

    parser.add_argument(
        "-n",
        "--max-tokens",
        type=int,
        default=None,
        help="Maximale Token‑Anzahl bei Ollama.",
    )

    parser.add_argument(
        "-s",
        "--stream",
        action="store_true",
        help="Antwort in Stream‑Modus zurückgeben (nur bei Ollama/Gemini).",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Prompt aus Datei oder direktem Argument
    prompt = args.prompt or _read_text_file(args.file)

    # Alle optionalen Dateien (außer dem Prompt‑Datei)
    files: List[Path] = list(args.files or []) if args.files else []

    # Initialisiere den Handler
    handler = LLMHandler(args.model)

    print(f"\n=== LLM: {args.model.upper()} ===")
    try:
        answer = handler.get_answer(
            prompt,
            files=files,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            stream=args.stream,
        )
        print("\n--- Antwort ---")
        print(answer)
    except Exception as exc:
        print(f"\n❌ Fehler: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
