import httpx
from bs4 import BeautifulSoup
from .llm_client import LLMClient
from .state import STATE


class Analyzer:
    def __init__(self):
        self.llm = LLMClient()

    async def scrape_website(self, url: str) -> str:
        """
        Downloads the page and extracts visible text.
        """
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(url)
                resp.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to scrape website: {e}")

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text[:6000]

    async def infer_category(self, url: str):
        """
        Scrape root company and retrieve:
        - industry
        - keywords
        - LLM-suggested category (advisory)
        """

        text = await self.scrape_website(url)

        prompt = (
            "Analyze the company below and return JSON with fields:\n"
            "- industry\n"
            "- category (suggested only)\n"
            "- keywords\n\n"
            f"COMPANY TEXT:\n{text}\n\n"
            "Return valid JSON only."
        )

        llm_response = await self.llm.call_llm(prompt)

        if not llm_response.json:
            raise RuntimeError("Invalid JSON returned by LLM in /infer_category")

        industry = llm_response.json.get("industry")
        suggested = llm_response.json.get("category")
        keywords = llm_response.json.get("keywords", [])

        STATE["root_company"] = url
        STATE["root_industry"] = industry
        STATE["root_keywords"] = keywords

        return {
            "root_company": url,
            "root_category": STATE["root_category"],
            "llm_suggested_category": suggested,
            "root_industry": industry,
            "root_keywords": keywords
        }

    async def validate_company(self, url: str):
        """
        Validate competitor based on chosen root_category.
        """

        if not STATE["root_category"]:
            raise RuntimeError("root_category not set.")

        text = await self.scrape_website(url)

        prompt = (
            "ROOT CATEGORY:\n"
            f"{STATE['root_category']}\n\n"
            "COMPANY TEXT:\n"
            f"{text}\n\n"
            "Your job:\n"
            "- Determine if the company clearly operates in the ROOT CATEGORY.\n"
            "- If yes: return {\"allowed\": true, \"reason\": \"...\"}\n"
            "- If no: return {\"allowed\": false, \"reason\": \"...\"}\n"
            "Return valid JSON only."
        )

        llm_response = await self.llm.call_llm(prompt)

        if not llm_response.json:
            raise RuntimeError("Invalid JSON returned by LLM in /validate_company")

        return llm_response.json
