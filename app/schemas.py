# app/schemas.py

from typing import List, Literal
from pydantic import BaseModel, Field


# -----------------------------
# Request model
# -----------------------------


class AssessmentRequest(BaseModel):
    """
    Input payload for the risk assessment.

    This closely mirrors your questionnaire structure.
    """

    # Company context
    company_size: Literal["1_5", "6_20", "21_50", "51_100", "100_plus"] = Field(
        ...,
        description="Dimensione azienda approssimativa (numero dipendenti).",
    )
    geography: Literal["single_eu", "multi_eu", "eu_plus_third_countries"] = Field(
        ...,
        description="Area geografica di operatività.",
    )

    # AI usage
    uses_ai: Literal["yes", "no"] = Field(
        ..., description="Se l'azienda utilizza o meno sistemi di AI / automazione."
    )
    ai_affects_individuals: Literal["none", "support", "direct"] = Field(
        ...,
        description="Quanto le decisioni di AI influiscono su individui.",
    )
    human_oversight: Literal["always", "sometimes", "none"] = Field(
        ...,
        description="Livello di supervisione umana sulle decisioni di AI.",
    )
    ai_use_cases: List[
        Literal["chatbot", "marketing", "scoring", "hr", "fraud", "analytics"]
    ] = Field(
        default_factory=list,
        description="Principali casi d'uso per l'AI.",
    )
    ai_usage_clarity: Literal["clear", "unknown"] = Field(
        "clear",
        description="Quanto è chiaro internamente dove e come viene usata l'AI.",
    )

    # Data & GDPR
    processes_personal_data: Literal["yes", "no"] = Field(
        ...,
        description="Se l'azienda tratta dati personali.",
    )
    processes_sensitive_data: Literal["yes", "no", "unknown"] = Field(
        ...,
        description="Se vengono trattati dati sensibili.",
    )
    data_location: Literal["eu_only", "eu_plus_third_countries", "unknown"] = Field(
        ...,
        description="Dove sono conservati / trattati i dati.",
    )
    third_party_access: Literal["yes", "no"] = Field(
        ...,
        description="Se terze parti o API accedono ai dati.",
    )
    users_informed_ai: Literal["yes", "partial", "no"] = Field(
        ...,
        description="Se gli utenti sono informati sull'uso di AI sui loro dati.",
    )

    # Governance
    ai_documentation: Literal["full", "partial", "none"] = Field(
        ...,
        description="Livello di documentazione sui sistemi di AI.",
    )
    policies: Literal["full", "in_progress", "none"] = Field(
        ...,
        description="Stato delle policy interne su dati e AI.",
    )
    risk_assessments: Literal["regular", "occasional", "none"] = Field(
        ...,
        description="Frequenza delle valutazioni del rischio.",
    )
    incident_response: Literal["full", "partial", "none"] = Field(
        ...,
        description="Esistenza di un piano di risposta agli incidenti.",
    )

    # Upcoming decisions
    upcoming_changes: List[
        Literal["new_ai_feature", "new_countries", "new_integrations"]
    ] = Field(
        default_factory=list,
        description="Principali cambiamenti previsti nei prossimi 6 mesi.",
    )
    decision_criticality: Literal["low", "medium", "high"] = Field(
        ...,
        description="Quanto sono critiche per il business le decisioni pianificate.",
    )
    reg_issue_impact: Literal["low", "medium", "high"] = Field(
        ...,
        description="Impatto potenziale di un problema regolatorio sull'azienda.",
    )


# -----------------------------
# Response model
# -----------------------------


class AssessmentResponse(BaseModel):
    ai_risk: float = Field(..., description="Punteggio di rischio AI Act (0–100).")
    gdpr_risk: float = Field(..., description="Punteggio di rischio GDPR / dati (0–100).")
    operational_risk: float = Field(
        ..., description="Punteggio di rischio operativo / governance (0–100)."
    )
    urgency_risk: float = Field(
        ..., description="Punteggio di urgenza legato alle decisioni future (0–100)."
    )
    final_score: float = Field(..., description="Punteggio di rischio complessivo (0–100).")
    risk_class: str = Field(..., description="Classe di rischio (Low, Medium, High, Critical).")
    reasons: List[str] = Field(
        ...,
        description="Principali motivi che contribuiscono al rischio (max 5).",
    )
    report: str = Field(
        ...,
        description="Report testuale riassuntivo della valutazione.",
    )
