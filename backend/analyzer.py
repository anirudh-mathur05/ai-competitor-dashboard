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
        return text[:6000]  # Limit for LLM safety

    async def infer_category(self, url: str):
        """
        Scrape the root company and retrieve:
        - industry
        - keywords
        - LLM-suggested category (advisory only)

        DOES NOT overwrite root_category (controlled by UI).
        """

        text = await self.scrape_website(url)

        prompt = f"""
        Analyze the company described below and return JSON with fields:
        - industry: High-level industry, e.g. "Financial Technology"
        - category: Suggested category (advisory only)
        - keywords: List of relevant product/market keywords

        COMPANY TEXT:
        {text}

        Return JSON only.
        """

        llm_response = await self.llm.call_llm(prompt)

        if not llm_response.json:
            raise RuntimeError("Invalid JSON returned by LLM in /infer_category")

        industry = llm_response.json.get("industry")
        category_suggested = llm_response.json.get("category")
        keywords = llm_response.json.get("keywords", [])

        # Update backend state — DO NOT touch root_category
        STATE["root_company"] = url
        STATE["root_industry"] = industry
        STATE["root_keywords"] = keywords

        return {
            "root_company": url,
            "root_category": STATE["root_category"],
            "llm_suggested_category": category_suggested,
            "root_industry": industry,
            "root_keywords": keywords
        }

    async def validate_company(self, url: str):
        """
        Validate if a competitor belongs to the chosen category.
        """

        if not STATE["root_category"]:
            raise RuntimeError(
                "root_category not set. User must select category first."
            )

        text = await self.scrape_website(url)

        prompt = f"""
        You are a strict industry validator.

        ROOT CATEGORY (human-chosen):
        "{STATE['root_category']}"

        COMPANY TEXT:
        {text}

        Your job:
        - Determine if the company clearly offers products/services in the ROOT CATEGORY.
        - If YES: return {{"allowed": true, "reason": "..."}}
        - If NO or uncertain: return {{"allowed": false, "reason": "..."}}

        Return JSON only.
        """

        llm_response = await self.llm.call_llm(prompt)

        if not llm_response.json:
            raise RuntimeError("Invalid JSON returned by LLM in /validate_company")

        return llm_response.json
