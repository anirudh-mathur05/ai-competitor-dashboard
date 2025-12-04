from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .analyzer import Analyzer

app = FastAPI(title="AI Competitor Battlecard Agent")
analyzer = Analyzer()


# -------------------------------
# Request Model
# -------------------------------
class URLRequest(BaseModel):
    url: str


# -------------------------------
# Endpoints
# -------------------------------

@app.post("/infer_category")
async def infer_category(payload: URLRequest):
    """
    Step 1: User provides the PRIMARY company URL.
    Backend infers:
    - industry
    - category (root category)
    - keywords

    Updates backend memory STATE.
    """
    try:
        result = await analyzer.infer_category(payload.url)
        return {"status": "ok", "data": result, "state": analyzer.STATE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate_company")
async def validate_company(payload: URLRequest):
    """
    Step 2 (manual competitor addition):
    Company is allowed ONLY if it belongs to the same inferred category.
    Strict Option-A behavior.
    """
    try:
        result = await analyzer.validate_company(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_competitor")
async def analyze_competitor(payload: URLRequest):
    """
    Step 3: Full battlecard generation.
    Only permitted once root category is set.
    """
    if analyzer.STATE["root_category"] is None:
        raise HTTPException(
            status_code=400,
            detail="Root category not set. Run /infer_category first."
        )

    try:
        result = await analyzer.analyze_competitor(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
