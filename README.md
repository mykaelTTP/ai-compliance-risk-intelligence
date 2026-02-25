# AI Compliance & Risk Intelligence
### Explainable AI Risk Scoring & Decision Memory System for SMEs

---

## Overview

AI Compliance & Risk Intelligence is a structured, explainable risk scoring system designed to help small and medium-sized enterprises (SMEs) assess their exposure to AI-related regulatory risks.

The system evaluates AI usage patterns, data sensitivity, automation levels, sector risk, and governance mechanisms to generate:

- A numerical AI Risk Score (0–100)
- A qualitative risk classification
- An explainable breakdown of risk drivers
- A decision memory system to track recurring high-risk patterns

This project was built as a practical prototype aligned with emerging regulatory frameworks such as the EU AI Act.

---

## Problem Statement

Many SMEs use AI tools without clearly understanding:

- Whether their systems fall into regulated risk categories
- Their exposure to high-risk or prohibited classifications
- Their level of governance and oversight
- The long-term risk of automated decision systems

This project bridges that gap through structured and interpretable pre-assessment.

---

## System Architecture

The project is structured into four core modules:

1. Risk Questionnaire Engine  
2. Rule-Based Risk Scoring System  
3. Explainable Risk Output Generator  
4. Decision Memory & Pattern Tracking Module  

---

## 1. Risk Questionnaire

The application collects structured information about:

- AI usage type (automation, decision-making, profiling)
- Data sensitivity (personal, biometric, financial)
- Industry sector (regulated vs non-regulated)
- Impact level on individuals
- Transparency and explainability level
- Human oversight mechanisms

Each answer maps to weighted risk dimensions.

---

## 2. Risk Scoring Engine

The scoring engine applies weighted aggregation logic across multiple dimensions:

Example conceptual logic:

```python
risk_score = (
    data_weight * data_score +
    automation_weight * automation_score +
    sector_weight * sector_score +
    impact_weight * impact_score -
    oversight_weight * oversight_score
)
```

Risk classification:

- 0–30 → Low Risk
- 31–60 → Medium Risk
- 61–85 → High Risk
- 86–100 → Critical / Potentially Prohibited

The system prioritizes interpretability over black-box modeling.

---

## 3. Explainable Output

Instead of returning only a number, the system generates structured reasoning.

Example output:

"Your system is classified as High Risk because it uses automated decision-making on sensitive personal data within a regulated sector and lacks sufficient human oversight."

This ensures business usability and transparency.

---

## 4. Decision Memory System

The system logs:

- Previous risk assessments
- Risk categories
- Decision contexts
- Identified compliance gaps

New assessments can be compared to past high-risk cases.

Example concept:

```python
if new_decision_similarity > threshold:
    trigger_warning("Similar pattern to previous high-risk classification.")
```

This transforms the tool from static scoring into dynamic risk intelligence.

---

## Tech Stack

- Python
- Streamlit (Frontend)
- Rule-based scoring logic
- CSV / JSON-based decision logging
- Structured risk aggregation engine

---

## Key Features

- Explainable AI risk scoring
- SME-focused compliance assessment
- Decision pattern tracking
- Modular architecture
- Extendable framework for future ML integration

---

## Limitations

- Currently rule-based (no ML-driven scoring)
- No live regulatory API integration
- MVP stage (no authentication layer)
- No automated document audit

---

## Future Improvements

- ML-based dynamic risk scoring
- Compliance drift detection
- Industry-specific risk modules
- Governance dashboard
- API integrations
- Enterprise-grade logging system

---

## Strategic Positioning

This project operates at the intersection of:

- AI Governance
- Risk Analytics
- RegTech
- Compliance Automation
- Decision Intelligence Systems

It is designed as a foundation for a scalable AI governance SaaS product.

---

## Status

MVP Prototype – Functional risk scoring and decision memory system implemented.
