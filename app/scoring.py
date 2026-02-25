# app/scoring.py

from dataclasses import dataclass
from typing import Any, Dict, List

from .config_pmi import PMI_AI_FEATURES, PMI_TRAINING_SOURCES, PMI_THIRD_PARTY_MODELS


@dataclass
class RiskResult:
    """Risultato strutturato di una valutazione di rischio."""

    ai_risk: float
    gdpr_risk: float
    operational_risk: float
    urgency_risk: float
    final_score: float
    risk_class: str
    reasons: List[str]
    report: str


SIZE_MULTIPLIERS: Dict[str, float] = {
    "1_5": 0.9,
    "6_20": 1.0,
    "21_50": 1.1,
    "51_100": 1.2,
    "100_plus": 1.3,
}

GEO_MULTIPLIERS: Dict[str, float] = {
    "single_eu": 1.0,
    "multi_eu": 1.1,
    "eu_plus_third_countries": 1.25,
}


def clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, value))


def classify_risk(score: float) -> str:
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Medium"
    if score <= 80:
        return "High"
    return "Critical"


# -------------------------------------------------------------------
#  AI Act risk
# -------------------------------------------------------------------


def _compute_ai_risk_base(answers: Dict[str, Any], reasons: List[str]) -> float:
    score = 0.0

    # In questo tool assumo che ci sia sempre AI (PIM+AI),
    # ma tengo comunque la logica generica per altri casi d'uso futuri.
    if answers.get("uses_ai") == "yes":
        score += 20
        reasons.append("L'azienda utilizza sistemi di AI o automazione sui dati.")

        ai_affects = answers.get("ai_affects_individuals")
        if ai_affects == "direct":
            score += 25
            reasons.append("Le decisioni di AI influenzano direttamente gli individui.")
        elif ai_affects == "support":
            score += 15
            reasons.append("L'AI supporta decisioni su persone.")

        use_cases = set(answers.get("ai_use_cases", []))
        if "hr" in use_cases:
            score += 20
            reasons.append("L'AI è usata in ambito HR / selezione del personale.")
        if "scoring" in use_cases:
            score += 15
            reasons.append("L'AI è usata per scoring, ranking o raccomandazioni.")

        oversight = answers.get("human_oversight")
        if oversight == "none":
            score += 20
            reasons.append("Manca una supervisione umana significativa sulle decisioni di AI.")
        elif oversight == "sometimes":
            score += 10
            reasons.append("La supervisione umana sulle decisioni di AI è solo parziale.")

        if answers.get("ai_usage_clarity") == "unknown":
            score += 10
            reasons.append("Non è chiaro come e dove viene usata l'AI nei processi aziendali.")

    return score


def _compute_ai_risk_pim(answers: Dict[str, Any], reasons: List[str]) -> float:
    """Componenti di rischio AI Act specifiche per PIM + AI."""
    score = 0.0

    pim_features = set(answers.get("pim_ai_features", []))
    if not pim_features:
        return 0.0

    # Presenza di AI nel PMI
    score += 5

    if "dynamic_pricing" in pim_features or "categorization" in pim_features:
        score += 15
        reasons.append(
            "Il PIM utilizza AI per decisioni automatizzate su prezzi o categorizzazione prodotti."
        )

    transparency = answers.get("pim_ai_transparency")
    if transparency == "partial":
        score += 10
        reasons.append(
            "La trasparenza sui contenuti generati da AI nel PIM è solo parziale."
        )
    elif transparency == "no":
        score += 20
        reasons.append(
            "Manca trasparenza sui contenuti generati da AI nel PIM, in potenziale contrasto con i requisiti di trasparenza."
        )

    supervision = answers.get("pim_ai_supervision_level")
    if supervision == "none":
        score += 20
        reasons.append(
            "Le decisioni automatizzate del PIM non sono sottoposte a supervisione umana."
        )
    elif supervision == "limited":
        score += 10
        reasons.append(
            "La supervisione umana sulle decisioni AI del PIM è limitata."
        )

    third_party = answers.get("pim_third_party_models")
    if third_party == "extensive":
        score += 10
        reasons.append(
            "Uso estensivo di modelli AI di terze parti nel PIM (es. GPAI via API)."
        )
    elif third_party == "some":
        score += 5
        reasons.append(
            "Uso di modelli AI di terze parti nel PIM per alcune funzionalità."
        )

    return score


def _compute_ai_risk(answers: Dict[str, Any], reasons: List[str]) -> float:
    base = _compute_ai_risk_base(answers, reasons)
    pim = _compute_ai_risk_pim(answers, reasons)
    return clamp(base + pim)


# -------------------------------------------------------------------
#  GDPR / Data risk
# -------------------------------------------------------------------


def _compute_gdpr_risk_base(answers: Dict[str, Any], reasons: List[str]) -> float:
    score = 0.0

    if answers.get("processes_personal_data") == "yes":
        score += 20
        reasons.append("L'azienda tratta dati personali dei clienti o dipendenti.")

        sensitive = answers.get("processes_sensitive_data")
        if sensitive == "yes":
            score += 30
            reasons.append("L'azienda tratta dati sensibili (es. salute, finanza, minori).")
        elif sensitive == "unknown":
            score += 10
            reasons.append("Non è chiaro se vengono trattati dati sensibili.")

        data_location = answers.get("data_location")
        if data_location == "eu_plus_third_countries":
            score += 20
            reasons.append("I dati vengono trasferiti anche fuori dall'UE.")
        elif data_location == "unknown":
            score += 10
            reasons.append("Non è chiaro dove sono conservati o trattati i dati.")

        if answers.get("third_party_access") == "yes":
            score += 15
            reasons.append("Terze parti o API di terze parti accedono ai dati personali.")

        informed = answers.get("users_informed_ai")
        if informed in ("no", "partial"):
            score += 20
            reasons.append(
                "Gli utenti non sono chiaramente informati sull'uso di AI sui loro dati personali."
            )

    return score


def _compute_gdpr_risk_pim(answers: Dict[str, Any], reasons: List[str]) -> float:
    score = 0.0

    pim_features = set(answers.get("pim_ai_features", []))
    if not pim_features:
        return 0.0

    training_sources = set(answers.get("pim_training_data_source", []))
    if "web_scraped" in training_sources:
        score += 15
        reasons.append(
            "I modelli AI del PIM sono addestrati anche su dati estratti dal web (rischio copyright/GDPR secondo Legge 132/2025)."
        )
    if "customer_data" in training_sources:
        score += 10
        reasons.append(
            "I modelli AI del PIM utilizzano dati cliente (ricerche, recensioni, ecc.) potenzialmente personali."
        )
    if "unknown" in training_sources:
        score += 10
        reasons.append(
            "Non è chiaro da dove provengono i dati di training dei modelli AI nel PIM."
        )

    copyright_policy = answers.get("pim_copyright_policy")
    if copyright_policy == "none":
        score += 20
        reasons.append(
            "Mancano policy chiare sull'uso di contenuti protetti da copyright per l'addestramento dell'AI (Legge 132/2025)."
        )
    elif copyright_policy == "partial":
        score += 10
        reasons.append(
            "Le policy sul copyright per l'AI nel PIM sono solo parziali."
        )

    return score


def _compute_gdpr_risk(answers: Dict[str, Any], reasons: List[str]) -> float:
    base = _compute_gdpr_risk_base(answers, reasons)
    pim = _compute_gdpr_risk_pim(answers, reasons)
    return clamp(base + pim)


# -------------------------------------------------------------------
#  Operational / Governance risk
# -------------------------------------------------------------------


def _compute_operational_risk_base(
    answers: Dict[str, Any], reasons: List[str]
) -> float:
    score = 0.0

    ai_doc = answers.get("ai_documentation")
    if ai_doc == "none":
        score += 25
        reasons.append("Manca documentazione sui sistemi di AI utilizzati dall'azienda.")
    elif ai_doc == "partial":
        score += 10
        reasons.append("La documentazione sui sistemi di AI è solo parziale.")

    policies = answers.get("policies")
    if policies == "none":
        score += 20
        reasons.append("Mancano policy interne su protezione dati e uso dell'AI.")
    elif policies == "in_progress":
        score += 10
        reasons.append("Le policy interne su dati e AI sono ancora in sviluppo.")

    risk_assessments = answers.get("risk_assessments")
    if risk_assessments == "none":
        score += 20
        reasons.append("Non vengono effettuate valutazioni periodiche dei rischi.")
    elif risk_assessments == "occasional":
        score += 10
        reasons.append("Le valutazioni del rischio non sono regolari.")

    incident_response = answers.get("incident_response")
    if incident_response == "none":
        score += 20
        reasons.append("Manca un piano di risposta in caso di problemi con AI o dati.")
    elif incident_response == "partial":
        score += 10
        reasons.append("Esiste solo un piano parziale di risposta agli incidenti.")

    ai_training = answers.get("ai_training_done")
    if ai_training == "no":
        score += 10
        reasons.append(
            "Non è stata ancora fatta formazione/alfabetizzazione AI per il personale coinvolto."
        )
    elif ai_training == "planned":
        score += 5
        reasons.append(
            "La formazione AI per il personale è solo pianificata, non ancora realizzata."
        )

    ai_plan = answers.get("ai_act_plan_status")
    if ai_plan == "none":
        score += 15
        reasons.append(
            "Manca un piano strutturato di adeguamento alle scadenze AI Act / Legge 132/2025."
        )
    elif ai_plan == "informal":
        score += 7
        reasons.append(
            "Esiste solo un piano informale per l'adeguamento alle scadenze AI Act / Legge 132/2025."
        )

    return score


def _compute_operational_risk(answers: Dict[str, Any], reasons: List[str]) -> float:
    return clamp(_compute_operational_risk_base(answers, reasons))


# -------------------------------------------------------------------
#  Urgency risk
# -------------------------------------------------------------------


def _compute_urgency_risk(answers: Dict[str, Any], reasons: List[str]) -> float:
    score = 0.0

    upcoming = set(answers.get("upcoming_changes", []))
    if "new_ai_feature" in upcoming:
        score += 25
        reasons.append("È previsto il lancio di una nuova funzionalità di AI.")
    if "new_countries" in upcoming:
        score += 20
        reasons.append("È prevista l'espansione in nuovi paesi.")
    if "new_integrations" in upcoming:
        score += 15
        reasons.append("Sono previste nuove integrazioni con tool o API di terze parti.")

    if answers.get("decision_criticality") == "high":
        score += 25
        reasons.append("Le decisioni pianificate sono critiche per il business.")

    if answers.get("reg_issue_impact") == "high":
        score += 25
        reasons.append(
            "Un problema regolatorio avrebbe un impatto elevato sull'azienda."
        )

    pim_features = set(answers.get("pim_ai_features", []))
    if pim_features:
        pim_impact = answers.get("pim_ai_impact")
        if pim_impact == "high":
            score += 10
            reasons.append(
                "L'uso di AI nel PIM ha un impatto elevato su prezzi, visibilità o decisioni di business."
            )
        elif pim_impact == "medium":
            score += 5
            reasons.append(
                "L'uso di AI nel PIM ha un impatto moderato sulle decisioni di business."
            )

    return clamp(score)


# -------------------------------------------------------------------
#  Report
# -------------------------------------------------------------------


def _build_report(
    final_score: float,
    risk_class: str,
    ai_risk: float,
    gdpr_risk: float,
    operational_risk: float,
    urgency_risk: float,
    reasons: List[str],
) -> str:
    """Crea un report testuale"""

    lines: List[str] = []

    lines.append("=== Valutazione Rischi AI & Dati ===")
    lines.append("")
    lines.append(f"Punteggio complessivo: {final_score:.1f} / 100")
    lines.append(f"Classe di rischio: {risk_class}")
    lines.append("")
    lines.append("Punteggi per ambito:")
    lines.append(f"  • Rischio AI Act: {ai_risk:.1f} / 100")
    lines.append(f"  • Rischio GDPR / dati: {gdpr_risk:.1f} / 100")
    lines.append(f"  • Rischio operativo / governance: {operational_risk:.1f} / 100")
    lines.append(f"  • Urgenza legata alle decisioni future: {urgency_risk:.1f} / 100")
    lines.append("")

    if reasons:
        lines.append("Principali driver di rischio individuati:")
        for r in reasons[:5]:
            lines.append(f"  • {r}")
    else:
        lines.append(
            "In base alle risposte fornite non emergono driver di rischio particolarmente critici. "
            "È comunque consigliabile mantenere un monitoraggio periodico."
        )

    lines.append("")
    lines.append(
        "Nota: questa valutazione ha lo scopo di fornire una fotografia sintetica dei rischi "
        "legati all'uso di AI e dati. Non sostituisce una consulenza legale o regolatoria."
    )

    return "\n".join(lines)


# -------------------------------------------------------------------
#  Public function
# -------------------------------------------------------------------


def compute_risk(answers: Dict[str, Any]) -> RiskResult:
    """Calcola i punteggi di rischio e il report a partire dalle risposte al questionario."""
    reasons: List[str] = []

    ai_risk = _compute_ai_risk(answers, reasons)
    gdpr_risk = _compute_gdpr_risk(answers, reasons)
    operational_risk = _compute_operational_risk(answers, reasons)
    urgency_risk = _compute_urgency_risk(answers, reasons)

    # Moltiplicatori per dimensione e geografia (stessa logica di prima)
    size_mult = SIZE_MULTIPLIERS.get(answers.get("company_size"), 1.0)
    geo_mult = GEO_MULTIPLIERS.get(answers.get("geography"), 1.0)

    # Nuovi pesi tra i domini, basati sulla "vita reale":
    # - AI Act e GDPR: impatto regolatorio maggiore (fino al 7% e 4% del fatturato)
    # - Operativo / governance: importante ma più come fattore abilitante
    # - Urgenza: influenza il "quando intervenire", meno l'esposizione assoluta
    base_score = (
        0.35 * ai_risk
        + 0.35 * gdpr_risk
        + 0.20 * operational_risk
        + 0.10 * urgency_risk
    )

    # Applichiamo i moltiplicatori di scala aziendale
    final_score = clamp(base_score * size_mult * geo_mult)
    risk_class = classify_risk(final_score)

    trimmed_reasons = reasons[:5]
    report = _build_report(
        final_score=final_score,
        risk_class=risk_class,
        ai_risk=ai_risk,
        gdpr_risk=gdpr_risk,
        operational_risk=operational_risk,
        urgency_risk=urgency_risk,
        reasons=trimmed_reasons,
    )

    return RiskResult(
        ai_risk=ai_risk,
        gdpr_risk=gdpr_risk,
        operational_risk=operational_risk,
        urgency_risk=urgency_risk,
        final_score=final_score,
        risk_class=risk_class,
        reasons=trimmed_reasons,
        report=report,
    )
