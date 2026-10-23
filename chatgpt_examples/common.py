"""Shared helpers: client creation, model selection and prompt handling."""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# gpt-6-luna is the low-cost GPT-6 model; set OPENAI_MODEL=gpt-6-sol or gpt-6-astra for more capability.
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


def get_client():
    """Return an OpenAI client; exits with a hint if no API key is set."""
    from openai import OpenAI

    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set. Copy .env.example to .env and add your key.")
    return OpenAI()


def prompt_from_args(default: str) -> str:
    """Use the command-line arguments as the prompt, or a default."""
    return " ".join(sys.argv[1:]).strip() or default
