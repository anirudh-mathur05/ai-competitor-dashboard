import os
import httpx
from pydantic import BaseModel

GROQ_API_KEY = os.getenv("LLAMA_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMResponse(BaseModel):
    raw_text: str
    json: dict | None = None


class LLMClient:
    def __init__(self):
        if not GROQ_API_KEY:
            raise RuntimeError("LLAMA_API_KEY environment variable not set.")

    async def call_llm(self, prompt: str) -> LLMResponse:
        """
        Generic wrapper to call Llama-3.3-70B via Groq.
        Returns raw text and best-effort JSON extraction.
        """
        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            }

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    json=payload,
                )
                response.raise_for_status()

            text = response.json()["choices"][0]["message"]["content"]
            # DEBUG LOG: print full raw response from Groq
                print("\n\n================ RAW LLM RESPONSE ================\n")
                print(text)
                print("\n=================================================\n")

            # Attempt JSON parsing
            import json
            try:
                parsed = json.loads(text)
            except Exception:
                parsed = None

            return LLMResponse(raw_text=text, json=parsed)

        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")
