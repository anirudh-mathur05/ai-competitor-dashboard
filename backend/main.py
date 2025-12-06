from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .analyzer import Analyzer
from .state import STATE

app = FastAPI(
    title="AI Competitor Battlecard Backend",
    version="2.0"
)

analyzer = Analyzer()

# --------------------
# Request Models
# --------------------

class InferPayload(BaseModel):
    url: str

class ValidatePayload(BaseModel):
    url: str


# --------------------
# Root Category Setter
# --------------------
# UI owns category selection.
class CategoryPayload(BaseModel):
    category: str

@app.post("/set_category")
async def set_category(payload: CategoryPayload):
    """
    User manually selects category from UI.
    This value controls competitor validation.
    """
    STATE["root_category"] = payload.category
    return {
        "root_category": STATE["root_category"],
        "message": "Category set successfully."
    }


# --------------------
# Infer Category (Advisory)
# --------------------
@app.post("/infer_category")
async def infer_category(payload: InferPayload):
    """
    Analyze root company:
    - DOES NOT overwrite root_category (which UI selected).
    - Enriches industry + keywords + suggested category.
    """
    try:
        result = await analyzer.infer_category(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------
# Validate Competitor
# --------------------
@app.post("/validate_company")
async def validate_company(payload: ValidatePayload):
    """
    Validates if a competitor belongs in the chosen root_category.
    """
    try:
        result = await analyzer.validate_company(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------
# Analyze Competitor (Battlecard)
# --------------------
class AnalyzePayload(BaseModel):
    url: str

@app.post("/analyze_competitor")
async def analyze_competitor(payload: AnalyzePayload):
    """
    Only allowed if:
    - root_category is set
    - competitor passes validate_company beforehand
    """
    if not STATE["root_category"]:
        raise HTTPException(
            status_code=400,
            detail="root_category not set. User must set category before analysis."
        )

    # Optional: block unvalidated companies (future strict mode)
    # For now: allow analysis directly.

    try:
        result = await analyzer.analyze_competitor(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------
# Health Check
# --------------------
@app.get("/health")
async def health():
    return {"status": "ok", "category": STATE["root_category"]}
