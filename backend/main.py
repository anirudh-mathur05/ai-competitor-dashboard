from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .analyzer import Analyzer
from .state import STATE

app = FastAPI(
    title="AI Competitor Battlecard Backend",
    version="2.0"
)

analyzer = Analyzer()


# ----------------------------
# Request Models
# ----------------------------
class InferPayload(BaseModel):
    url: str


class ValidatePayload(BaseModel):
    url: str


class AnalyzePayload(BaseModel):
    url: str


class CategoryPayload(BaseModel):
    category: str


# ----------------------------
# Set Category (UI-Owned)
# ----------------------------
@app.post("/set_category")
async def set_category(payload: CategoryPayload):
    """
    User selects the root category in the UI.
    Backend uses this for validation.
    """
    STATE["root_category"] = payload.category
    return {
        "root_category": STATE["root_category"],
        "message": "Category set successfully."
    }


# ----------------------------
# Infer Category (Advisory Only)
# ----------------------------
@app.post("/infer_category")
async def infer_category(payload: InferPayload):
    """
    Uses LLM to enrich:
    - industry
    - keywords
    - suggested category (advisory only)

    Does NOT overwrite root_category.
    """
    try:
        result = await analyzer.infer_category(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Validate Competitor
# ----------------------------
@app.post("/validate_company")
async def validate_company(payload: ValidatePayload):
    """
    Allows adding a manual competitor only if it matches root_category.
    """
    try:
        result = await analyzer.validate_company(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Analyze Competitor (Battlecard)
# ----------------------------
@app.post("/analyze_competitor")
async def analyze_competitor(payload: AnalyzePayload):
    """
    Generates a battlecard for a competitor.
    Only valid if root_category is set.
    """

    if not STATE["root_category"]:
        raise HTTPException(
            status_code=400,
            detail="root_category not set. Call /set_category first."
        )

    # NOTE: Strict validation check can be enforced later.
    try:
        result = await analyzer.analyze_competitor(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Health Check
# ----------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "root_category": STATE["root_category"]
    }
