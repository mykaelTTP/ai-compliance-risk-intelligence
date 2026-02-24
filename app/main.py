# app/main.py

from fastapi import FastAPI
from app.schemas import AssessmentRequest, AssessmentResponse
from app.scoring import compute_risk

app = FastAPI(
    title="AI Compliance & Risk Intelligence API",
    version="0.1.0",
    description=(
        "Backend API per valutare il rischio regolatorio e operativo "
        "di PMI che utilizzano AI / automazione sui dati."
    ),
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post(
    "/assess",
    response_model=AssessmentResponse,
    summary="Valuta il rischio AI / GDPR per una PMI",
    tags=["assessment"],
)
def assess_risk(payload: AssessmentRequest) -> AssessmentResponse:
    result = compute_risk(payload.dict())

    return AssessmentResponse(
        ai_risk=result.ai_risk,
        gdpr_risk=result.gdpr_risk,
        operational_risk=result.operational_risk,
        urgency_risk=result.urgency_risk,
        final_score=result.final_score,
        risk_class=result.risk_class,
        reasons=result.reasons,
        report=result.report,
    )
