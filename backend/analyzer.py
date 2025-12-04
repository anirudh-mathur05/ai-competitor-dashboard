from .llm_client import LLMClient


class Analyzer:
    def __init__(self):
        self.llm = LLMClient()
        self.STATE = {
            "root_company": None,
            "root_category": None,
            "root_keywords": [],
            "root_industry": None,
        }

    async def infer_category(self, url: str) -> dict:
        """
        Extract industry, category, and keywords for the primary company.
        Updates backend STATE.
        """

        prompt = f"""
        Analyze this company based on its website: {url}

        Return ONLY JSON in the format:
        {{
            "industry": "...",
            "category": "...",
            "keywords": ["...", "..."]
        }}
        """

        result = await self.llm.call_llm(prompt)

        if not result.json:
            raise RuntimeError("Invalid LLM JSON response for category inference.")

        data = result.json

        # Update backend memory state
        self.STATE["root_company"] = url
        self.STATE["root_category"] = data.get("category")
        self.STATE["root_industry"] = data.get("industry")
        self.STATE["root_keywords"] = data.get("keywords", [])

        return data

    async def validate_company(self, company_url: str) -> dict:
        """
        Validate if a manually added company belongs to the same category.
        Strict Option-A logic:
        - Only companies in the same inferred category are allowed.
        """

        category = self.STATE["root_category"]
        if not category:
            return {
                "allowed": False,
                "reason": "Primary company category not set. Run /infer_category first."
            }

        prompt = f"""
        The ROOT CATEGORY is: {category}.
        Evaluate whether the company at URL {company_url}
        offers any major product in this category.

        Return ONLY JSON:
        {{
            "allowed": true/false,
            "reason": "..."
        }}
        """

        result = await self.llm.call_llm(prompt)

        if not result.json:
            raise RuntimeError("Invalid LLM JSON for company validation.")

        return result.json

    async def analyze_competitor(self, url: str) -> dict:
        """
        Generates a full competitor battlecard in JSON format.
        """

        prompt = f"""
        Analyze the competitor at URL: {url}

        Return ONLY JSON:
        {{
            "name": "...",
            "url": "{url}",
            "product_summary": "...",
            "target_users": "...",
            "key_features": ["...", "..."],
            "strengths": ["..."],
            "weaknesses": ["..."],
            "ai_usage": "...",
            "differentiators": ["...", "..."]
        }}
        """

        result = await self.llm.call_llm(prompt)

        if not result.json:
            raise RuntimeError("Invalid LLM JSON for competitor analysis.")

        return result.json
