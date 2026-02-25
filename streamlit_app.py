# streamlit_app.py

import streamlit as st
import pandas as pd

from app.scoring import compute_risk
from app.pdf_utils import build_pdf_from_report
from app.db import (
    init_db,
    log_assessment,
    get_recent_assessments,
    get_last_assessment,
)
from app.config_pmi import (
    PMI_AI_FEATURES,
    PMI_TRAINING_SOURCES,
    PMI_THIRD_PARTY_MODELS,
)

# -------------------------------------------------
# Setup iniziale
# -------------------------------------------------
init_db()
st.set_page_config(
    page_title="Valutazione Rischi AI",
    layout="wide",
    page_icon="🛡️",
)


def inject_css():
    st.markdown(
        """
        <style>
        .main {
            background-color: #f5f7fb;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
        }

        .soft-card {
            background-color: #ffffff;
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.03);
            border: 1px solid #e5e7eb;
        }

        .soft-card-header {
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
            color: #111827;
        }

        .soft-card-sub {
            font-size: 0.8rem;
            color: #6b7280;
        }

        section[data-testid="stSidebar"] {
            background-color: #050816;
            color: #e5e7eb;
        }

        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] p {
            color: #e5e7eb !important;
        }

        button[data-baseweb="tab"] {
            font-size: 0.9rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# -------------------------------------------------
# Helper: banner rischio
# -------------------------------------------------
def show_risk_banner(result):
    risk_class = result.risk_class  # "Low", "Medium", "High", "Critical"

    if risk_class == "Low":
        bg = "#e6f4ea"      # verde chiaro
        border = "#137333"
        text = "#0d652d"
        emoji = "🟢"
    elif risk_class == "Medium":
        bg = "#fef7e0"      # giallo chiaro
        border = "#f9ab00"
        text = "#8d5e00"
        emoji = "🟡"
    elif risk_class == "High":
        bg = "#fce8e6"      # arancione
        border = "#ea4335"
        text = "#a50e0e"
        emoji = "🟠"
    else:  # Critical
        bg = "#fbe9e7"
        border = "#d93025"
        text = "#a50e0e"
        emoji = "🔴"

    st.markdown(
        f"""
        <div style="
            padding: 0.95rem 1.2rem;
            border-radius: 0.75rem;
            border: 1px solid {border};
            background-color: {bg};
            color: {text};
            font-weight: 600;
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        ">
            {emoji} Punteggio complessivo: {result.final_score:.1f} / 100
            &nbsp;&nbsp;•&nbsp;&nbsp;
            Classe di rischio: {risk_class}
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.markdown(
        "<h3 style='margin-top:0.2rem;margin-bottom:0.3rem;'>AI Risk Studio</h3>",
        unsafe_allow_html=True,
    )
    st.caption("Valutazione rischi AI per PMI marketing & e-commerce")

    page = st.radio(
        "Navigazione",
        ["🏠 Dashboard", "📝 Nuova valutazione", "📄 Storico & report", "ℹ️ Guida"],
        index=0,
    )

    st.markdown("---")
    st.caption("Built for PMI che usano AI su dati reali.")


# -------------------------------------------------
# Pagina: Dashboard
# -------------------------------------------------
if page == "🏠 Dashboard":
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("## 🏠 Dashboard")
        st.markdown(
            """
            Benvenuto nella **console di rischio AI**.

            Qui trovi:
            - lo **stato attuale** (ultima valutazione)
            - l'**impatto per ambito** (AI Act, GDPR, governance, urgenza)
            - l'**andamento nel tempo** del punteggio di rischio
            """
        )

    with col_right:
        last = get_last_assessment()

        st.markdown("### 📊 Ultima valutazione")
        if last is None:
            st.info(
                "Non è ancora stata eseguita alcuna valutazione.\n\n"
                "Vai su **📝 Nuova valutazione** per creare il primo report."
            )
        else:
            (
                last_id,
                created_at,
                company_name,
                final_score,
                risk_class,
                ai_risk,
                gdpr_risk,
                operational_risk,
                urgency_risk,
            ) = last

            # KPI cards
            with st.container():
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f"""
                        <div class="soft-card">
                            <div class="soft-card-header">Azienda</div>
                            <div style="font-size:1rem;font-weight:600;">
                                {company_name or "N/A"}
                            </div>
                            <div class="soft-card-sub">
                                Ultimo check: {created_at}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f"""
                        <div class="soft-card">
                            <div class="soft-card-header">Punteggio complessivo</div>
                            <div style="font-size:1.2rem;font-weight:700;">
                                {final_score:.1f} / 100
                            </div>
                            <div class="soft-card-sub">
                                Classe di rischio: <b>{risk_class}</b>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("#### Distribuzione per ambito (ultima valutazione)")

            domain_scores = pd.DataFrame(
                {
                    "Ambito": [
                        "AI Act",
                        "GDPR / dati",
                        "Operativo / governance",
                        "Urgenza decisioni",
                    ],
                    "Punteggio": [
                        ai_risk,
                        gdpr_risk,
                        operational_risk,
                        urgency_risk,
                    ],
                }
            )
            st.bar_chart(domain_scores.set_index("Ambito"))

    # Grafico storico
    st.markdown("### 📈 Andamento del rischio nel tempo")

    rows_all = get_recent_assessments(limit=50)
    if not rows_all:
        st.info("Non ci sono ancora abbastanza dati per mostrare l'andamento nel tempo.")
    else:
        df_hist = pd.DataFrame(
            rows_all,
            columns=[
                "ID",
                "Data",
                "Azienda",
                "Punteggio",
                "Classe",
                "AI Act",
                "GDPR / dati",
                "Operativo / governance",
                "Urgenza decisioni",
            ],
        )
        df_hist["Data"] = pd.to_datetime(df_hist["Data"])
        df_hist = df_hist.sort_values("Data")

        chart_df = df_hist.set_index("Data")[
            ["Punteggio", "AI Act", "GDPR / dati", "Operativo / governance", "Urgenza decisioni"]
        ]

        st.line_chart(chart_df)
        st.caption(
            "Ogni punto rappresenta una valutazione eseguita. "
            "Puoi usare questo grafico per mostrare miglioramenti o peggioramenti nel tempo."
        )

    st.markdown("---")
    st.caption(
        "Suggerimento: usa questa dashboard in call per mostrare in 30 secondi "
        "dove si concentra il rischio AI della PMI."
    )


# -------------------------------------------------
# Pagina: Nuova valutazione
# -------------------------------------------------
elif page == "📝 Nuova valutazione":
    st.markdown("## 📝 Nuova valutazione di rischio")
    st.caption(
        "Compila le informazioni sulla PMI, sull'uso di AI e sulla gestione dei dati. "
        "Il tool restituisce un punteggio e un report sintetico."
    )

    # Tabs 
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🏢 Profilo azienda",
            "🤖 AI nella PMI / marketing",
            "🔐 Dati & GDPR",
            "📋 Governance",
            "📈 Futuro & impatto",
        ]
    )

    # ---------- Tab 1: Profilo azienda ----------
    with tab1:
        st.subheader("🏢 Profilo azienda")
        col1, col2 = st.columns(2)

        with col1:
            company_size = st.selectbox(
                "Dimensione azienda (numero dipendenti)",
                options=["1_5", "6_20", "21_50", "51_100", "100_plus"],
                format_func=lambda v: {
                    "1_5": "1–5",
                    "6_20": "6–20",
                    "21_50": "21–50",
                    "51_100": "51–100",
                    "100_plus": "100+",
                }[v],
                index=None,
                placeholder="Seleziona la dimensione",
            )
            company_name_input = st.text_input(
                "Nome azienda (per il report PDF)",
                value="",
                placeholder="Es. Agenzia XYZ",
            )

        with col2:
            geography = st.selectbox(
                "Operatività geografica",
                options=["single_eu", "multi_eu", "eu_plus_third_countries"],
                format_func=lambda v: {
                    "single_eu": "Un solo paese UE",
                    "multi_eu": "Più paesi UE",
                    "eu_plus_third_countries": "UE + Paesi terzi",
                }[v],
                index=None,
                placeholder="Seleziona l'area",
            )

        st.info(
            "Queste informazioni servono solo per pesare il rischio in base alla "
            "scala della PMI (una realtà locale vs un e-commerce europeo)."
        )

    # ---------- Tab 2: AI nella PMI / marketing ----------
    with tab2:
        st.subheader("🤖 AI nella PMI / marketing")

        st.markdown(
            "Indica come viene usata l'AI **nei processi aziendali** "
            "(catalogo prodotti, contenuti, campagne, automazioni…)."
        )

        pmi_ai_features = st.multiselect(
            "Funzionalità AI presenti nei processi (catalogo, contenuti, campagne…)",
            options=list(PMI_AI_FEATURES.keys()),
            format_func=lambda v: PMI_AI_FEATURES[v],
            placeholder="Seleziona una o più funzionalità (se presenti)",
        )

        if not pmi_ai_features:
            st.warning(
                "Questo strumento è pensato per PMI che utilizzano AI. "
                "Se non selezioni nessuna funzionalità AI, il rischio risulterà molto basso."
            )

        col1, col2 = st.columns(2)
        with col1:
            pmi_ai_impact = st.selectbox(
                "Impatto dell'AI su prezzi, visibilità o decisioni di business",
                options=["low", "medium", "high"],
                format_func=lambda v: {
                    "low": "Basso (suggerimenti interni, non visibili ai clienti)",
                    "medium": "Medio (influenza contenuti/ordine con controllo umano)",
                    "high": "Alto (influenza direttamente prezzi, visibilità o ranking)",
                }[v],
                index=None,
                placeholder="Seleziona il livello di impatto",
            )

        with col2:
            pmi_ai_supervision_level = st.selectbox(
                "Supervisione umana sulle decisioni AI",
                options=["strong", "limited", "none"],
                format_func=lambda v: {
                    "strong": "Forte (ogni cambiamento rilevante è revisionato)",
                    "limited": "Limitata (controlli a campione / saltuari)",
                    "none": "Assente (va in produzione senza review sistematici)",
                }[v],
                index=None,
                placeholder="Seleziona il livello di supervisione",
            )

        pim_ai_transparency = st.selectbox(
            "I contenuti generati/ottimizzati da AI sono etichettati come tali?",
            options=["yes", "partial", "no"],
            format_func=lambda v: {
                "yes": "Sì, è chiaro quando un contenuto è generato da AI",
                "partial": "Solo in parte / non sempre chiaro",
                "no": "No, non è indicato",
            }[v],
            index=None,
            placeholder="Seleziona il livello di trasparenza",
        )

        st.markdown("#### Altri usi di AI in azienda")

        ai_use_cases = st.multiselect(
            "Altri casi d'uso dell'AI",
            options=["chatbot", "marketing", "scoring", "hr", "fraud", "analytics"],
            format_func=lambda v: {
                "chatbot": "Chatbot / assistenza clienti",
                "marketing": "Marketing / personalizzazione",
                "scoring": "Scoring / ranking / raccomandazioni",
                "hr": "HR / selezione / valutazione",
                "fraud": "Rilevazione frodi / rischio",
                "analytics": "Analytics interni",
            }[v],
            placeholder="Seleziona eventuali altri casi d'uso",
        )

        col3, col4 = st.columns(2)
        with col3:
            ai_affects_individuals = st.selectbox(
                "L'AI influisce su decisioni riguardanti persone?",
                options=["none", "support", "direct"],
                format_func=lambda v: {
                    "none": "No, non riguarda direttamente persone",
                    "support": "Supporta decisioni umane su persone",
                    "direct": "Prende decisioni dirette su persone",
                }[v],
                index=None,
                placeholder="Seleziona un'opzione",
            )
        with col4:
            human_oversight = st.selectbox(
                "Supervisione umana sulle decisioni di AI (in generale)",
                options=["always", "sometimes", "none"],
                format_func=lambda v: {
                    "always": "Sempre (decisioni critiche riviste)",
                    "sometimes": "A volte (controlli solo su alcuni casi)",
                    "none": "Quasi mai / mai",
                }[v],
                index=None,
                placeholder="Seleziona un'opzione",
            )

        ai_usage_clarity = st.selectbox(
            "Internamente è chiaro dove / come viene usata l'AI?",
            options=["clear", "unknown"],
            format_func=lambda v: "Sì, abbastanza chiaro" if v == "clear" else "Non molto chiaro",
            index=None,
            placeholder="Seleziona un'opzione",
        )

        pmi_third_party_models = st.selectbox(
            "Uso di modelli AI di terze parti (OpenAI, API esterne, ecc.)",
            options=list(PMI_THIRD_PARTY_MODELS.keys()),
            format_func=lambda v: PMI_THIRD_PARTY_MODELS[v],
            index=None,
            placeholder="Seleziona un'opzione",
        )

    # ---------- Tab 3: Dati & GDPR ----------
    with tab3:
        st.subheader("🔐 Dati & GDPR")

        processes_personal_data = st.radio(
            "I sistemi AI della PMI trattano dati personali di clienti o dipendenti?",
            options=["yes", "no"],
            format_func=lambda v: "Sì" if v == "yes" else "No",
        )

        if processes_personal_data == "yes":
            col1, col2 = st.columns(2)
            with col1:
                processes_sensitive_data = st.selectbox(
                    "Tra questi dati, sono presenti dati sensibili (salute, finanza, minori, ecc.)?",
                    options=["yes", "no", "unknown"],
                    format_func=lambda v: {
                        "yes": "Sì",
                        "no": "No",
                        "unknown": "Non sono sicuro / non saprei",
                    }[v],
                    index=None,
                    placeholder="Seleziona un'opzione",
                )
            with col2:
                data_location = st.selectbox(
                    "Dove sono conservati / trattati principalmente i dati personali?",
                    options=["eu_only", "eu_plus_third_countries", "unknown"],
                    format_func=lambda v: {
                        "eu_only": "Solo in UE",
                        "eu_plus_third_countries": "UE + Paesi terzi",
                        "unknown": "Non ne sono sicuro",
                    }[v],
                    index=None,
                    placeholder="Seleziona una localizzazione",
                )

            third_party_access = st.radio(
                "Tool o API di terze parti accedono ai dati personali?",
                options=["yes", "no"],
                format_func=lambda v: "Sì" if v == "yes" else "No",
            )

            users_informed_ai = st.selectbox(
                "Gli utenti sono informati sull'uso di AI sui loro dati personali?",
                options=["yes", "partial", "no"],
                format_func=lambda v: {
                    "yes": "Sì, in modo chiaro (privacy policy, informative)",
                    "partial": "Solo in parte / poco chiaro",
                    "no": "No, non sono informati in modo esplicito",
                }[v],
                index=None,
                placeholder="Seleziona un'opzione",
            )
        else:
            st.info(
                "Se i sistemi AI della PMI non trattano dati personali, le domande successive "
                "vengono considerate non applicabili."
            )
            processes_sensitive_data = "no"
            data_location = "eu_only"
            third_party_access = "no"
            users_informed_ai = "not_applicable"

        st.markdown("#### Dati di training dei modelli AI usati dalla PMI")

        pmi_training_data_source = st.multiselect(
            "Da dove provengono i dati usati per addestrare / fare fine-tuning dei modelli AI?",
            options=list(PMI_TRAINING_SOURCES.keys()),
            format_func=lambda v: PMI_TRAINING_SOURCES[v],
            placeholder="Seleziona una o più fonti dati",
        )

        pmi_copyright_policy = st.selectbox(
            "Esistono policy sull'uso di contenuti protetti da copyright per l'AI?",
            options=["full", "partial", "none"],
            format_func=lambda v: {
                "full": "Sì, policy definite e documentate",
                "partial": "Solo parziali / non complete",
                "none": "No, non esistono policy specifiche",
            }[v],
            index=None,
            placeholder="Seleziona un'opzione",
        )

    # ---------- Tab 4: Governance ----------
    with tab4:
        st.subheader("📋 Governance & controlli interni")

        ai_documentation = st.selectbox(
            "Documentazione sui sistemi di AI",
            options=["full", "partial", "none"],
            format_func=lambda v: {
                "full": "Completa (architettura, casi d'uso, responsabilità)",
                "partial": "Parziale (solo alcuni aspetti documentati)",
                "none": "Assente",
            }[v],
            index=None,
            placeholder="Seleziona un'opzione",
        )

        policies = st.selectbox(
            "Policy interne su dati e AI",
            options=["full", "in_progress", "none"],
            format_func=lambda v: {
                "full": "Definite e approvate",
                "in_progress": "In definizione / bozza",
                "none": "Assenti",
            }[v],
            index=None,
            placeholder="Seleziona un'opzione",
        )

        col1, col2 = st.columns(2)
        with col1:
            risk_assessments = st.selectbox(
                "Valutazioni di rischio su AI e dati",
                options=["regular", "occasional", "none"],
                format_func=lambda v: {
                    "regular": "Regolari (almeno annuali)",
                    "occasional": "Occasionali (quando succede qualcosa)",
                    "none": "Mai effettuate",
                }[v],
                index=None,
                placeholder="Seleziona un'opzione",
            )

        with col2:
            incident_response = st.selectbox(
                "Piano di risposta ad incidenti (AI / dati)",
                options=["full", "partial", "none"],
                format_func=lambda v: {
                    "full": "Presente, testato e conosciuto dal team",
                    "partial": "Esiste solo in forma informale / parziale",
                    "none": "Assente",
                }[v],
                index=None,
                placeholder="Seleziona un'opzione",
            )

        col3, col4 = st.columns(2)
        with col3:
            ai_training_done = st.selectbox(
                "Formazione / alfabetizzazione AI per il personale",
                options=["yes", "planned", "no"],
                format_func=lambda v: {
                    "yes": "Sì, già effettuata per i ruoli chiave",
                    "planned": "Pianificata ma non ancora fatta",
                    "no": "Non ancora affrontata",
                }[v],
                index=None,
                placeholder="Seleziona un'opzione",
            )
        with col4:
            ai_act_plan_status = st.selectbox(
                "Piano di adeguamento ad AI Act / Legge 132/2025",
                options=["structured", "informal", "none"],
                format_func=lambda v: {
                    "structured": "Piano strutturato e formalizzato",
                    "informal": "Solo idee / piano informale",
                    "none": "Nessun piano definito",
                }[v],
                index=None,
                placeholder="Seleziona un'opzione",
            )

    # ---------- Tab 5: Futuro & impatto ----------
    with tab5:
        st.subheader("📈 Prossimi cambiamenti e impatto")

        upcoming_changes = st.multiselect(
            "Cambiamenti previsti nei prossimi 6 mesi",
            options=["new_ai_feature", "new_countries", "new_integrations"],
            format_func=lambda v: {
                "new_ai_feature": "Nuova funzionalità di AI",
                "new_countries": "Espansione in nuovi paesi / mercati",
                "new_integrations": "Nuove integrazioni con tool / API terze",
            }[v],
            placeholder="Seleziona uno o più cambiamenti (se presenti)",
        )

        col1, col2 = st.columns(2)
        with col1:
            decision_criticality = st.selectbox(
                "Quanto sono critiche per il business le decisioni legate a questi cambiamenti?",
                options=["low", "medium", "high"],
                format_func=lambda v: {
                    "low": "Bassa",
                    "medium": "Media",
                    "high": "Alta (errori con impatti importanti)",
                }[v],
                index=None,
                placeholder="Seleziona un livello di criticità",
            )
        with col2:
            reg_issue_impact = st.selectbox(
                "Impatto di un eventuale problema regolatorio (AI Act / GDPR)",
                options=["low", "medium", "high"],
                format_func=lambda v: {
                    "low": "Limitato",
                    "medium": "Significativo",
                    "high": "Molto alto / critico",
                }[v],
                index=None,
                placeholder="Seleziona un livello di impatto",
            )

    # ---------- Bottone unico in fondo ----------
    st.markdown("---")
    st.caption("Quando hai compilato tutte le sezioni, clicca il pulsante qui sotto per generare il report.")

    if st.button("🚀 Esegui valutazione del rischio"):
        uses_ai = "yes"

        # Validazione minima
        missing = []
        if company_size is None:
            missing.append("dimensione azienda")
        if geography is None:
            missing.append("operatività geografica")

        if missing:
            st.error(
                "Per eseguire la valutazione devi almeno compilare: "
                + ", ".join(missing)
                + "."
            )
            st.stop()

        if not pmi_ai_features and not ai_use_cases:
            st.warning(
                "Non hai indicato nessuna funzionalità AI né casi d'uso. "
                "La valutazione risulterà molto bassa e poco utile."
            )

        # Default neutri se qualcosa è vuoto
        company_size = company_size or "6_20"
        geography = geography or "single_eu"
        ai_affects_individuals = (ai_affects_individuals or "none")
        human_oversight = (human_oversight or "always")
        ai_usage_clarity = (ai_usage_clarity or "clear")
        pmi_ai_impact = (pmi_ai_impact or "medium")
        pmi_ai_supervision_level = (pmi_ai_supervision_level or "limited")
        pmi_ai_transparency = (pim_ai_transparency or "partial")
        pmi_third_party_models = (pmi_third_party_models or "none")

        if processes_personal_data == "yes":
            processes_sensitive_data = (processes_sensitive_data or "no")
            data_location = (data_location or "eu_only")
            users_informed_ai = (users_informed_ai or "partial")

        pmi_copyright_policy = (pmi_copyright_policy or "none")
        ai_documentation = (ai_documentation or "partial")
        policies = (policies or "in_progress")
        risk_assessments = (risk_assessments or "occasional")
        incident_response = (incident_response or "partial")
        ai_training_done = (ai_training_done or "planned")
        ai_act_plan_status = (ai_act_plan_status or "informal")
        decision_criticality = (decision_criticality or "medium")
        reg_issue_impact = (reg_issue_impact or "medium")

        answers = {
            "company_size": company_size,
            "geography": geography,
            "uses_ai": uses_ai,
            "ai_affects_individuals": ai_affects_individuals,
            "human_oversight": human_oversight,
            "ai_use_cases": ai_use_cases,
            "ai_usage_clarity": ai_usage_clarity,
            "processes_personal_data": processes_personal_data,
            "processes_sensitive_data": processes_sensitive_data,
            "data_location": data_location,
            "third_party_access": third_party_access,
            "users_informed_ai": users_informed_ai,
            "ai_documentation": ai_documentation,
            "policies": policies,
            "risk_assessments": risk_assessments,
            "incident_response": incident_response,
            "upcoming_changes": upcoming_changes,
            "decision_criticality": decision_criticality,
            "reg_issue_impact": reg_issue_impact,
            "ai_training_done": ai_training_done,
            "ai_act_plan_status": ai_act_plan_status,
            # PMI-specific (chiavi usate dal motore di scoring)
            "pmi_ai_features": pmi_ai_features,
            "pmi_ai_transparency": pmi_ai_transparency,
            "pmi_ai_impact": pmi_ai_impact,
            "pmi_ai_supervision_level": pmi_ai_supervision_level,
            "pmi_training_data_source": pmi_training_data_source,
            "pmi_copyright_policy": pmi_copyright_policy,
            "pmi_third_party_models": pmi_third_party_models,
        }

        result = compute_risk(answers)

        # Banner risultato
        show_risk_banner(result)

        st.subheader("📊 Distribuzione dei rischi per ambito")
        domain_scores = pd.DataFrame(
            {
                "Ambito": [
                    "AI Act",
                    "GDPR / dati",
                    "Operativo / governance",
                    "Urgenza decisioni",
                ],
                "Punteggio": [
                    result.ai_risk,
                    result.gdpr_risk,
                    result.operational_risk,
                    result.urgency_risk,
                ],
            }
        )
        st.bar_chart(domain_scores.set_index("Ambito"))

        st.subheader("🧾 Report dettagliato")
        st.text(result.report)

        st.subheader("🔍 Motivi principali")
        if result.reasons:
            for r in result.reasons:
                st.markdown(f"- {r}")
        else:
            st.write("Nessun driver di rischio rilevante identificato.")

        # Log nel DB
        try:
            log_assessment(
                company_name=company_name_input or None,
                answers=answers,
                result=result,
            )
            st.success("✅ Valutazione salvata per analisi future.")
        except Exception as e:
            st.warning(f"⚠️ Non è stato possibile salvare la valutazione: {e}")

        # PDF
        pdf_bytes = build_pdf_from_report(
            company_name=company_name_input or None,
            report_text=result.report,
        )
        st.download_button(
            label="📄 Scarica report in PDF",
            data=pdf_bytes,
            file_name="valutazione_rischi_ai_dati.pdf",
            mime="application/pdf",
        )


# -------------------------------------------------
# Pagina: Storico
# -------------------------------------------------
elif page == "📄 Storico & report":
    st.markdown("## 📄 Storico valutazioni")

    rows = get_recent_assessments(limit=50)
    if not rows:
        st.info("Non ci sono ancora valutazioni salvate.")
    else:
        df = pd.DataFrame(
            rows,
            columns=[
                "ID",
                "Data",
                "Azienda",
                "Punteggio",
                "Classe",
                "AI Act",
                "GDPR / dati",
                "Operativo / governance",
                "Urgenza decisioni",
            ],
        )
        st.dataframe(df, use_container_width=True)
        st.caption(
            "Usa questo storico per mostrare come evolve il profilo di rischio AI della PMI nel tempo."
        )


# -------------------------------------------------
# Pagina: Guida
# -------------------------------------------------
elif page == "ℹ️ Guida":
    st.markdown("## ℹ️ Guida alla lettura dei risultati")

    st.markdown(
        """
        Questa sezione spiega **che cosa misura il tool** e **come interpretare i punteggi**.

        ### Cosa misura

        - **AI Act** → quanto l'uso di AI nei processi della PMI può entrare in aree a rischio
        - **GDPR / dati** → quanto il trattamento dati (personali, sensibili, trasferimenti, terze parti) è esposto
        - **Operativo / governance** → quanto la PMI è organizzata (policy, documentazione, formazione, piani AI)
        - **Urgenza** → quanto i cambiamenti in arrivo possono amplificare rischi già presenti

        ### Soglie di rischio (0–100)

        - **0–30** → Rischio basso  
        - **31–60** → Rischio medio  
        - **61–80** → Rischio alto  
        - **81–100** → Rischio critico  

        Un punteggio alto non significa automaticamente che la PMI è "fuori legge",
        ma è un segnale che vale la pena:

        - rivedere processi e contratti,
        - aggiornare informative, policy e documentazione,
        - coinvolgere legale / DPO per approfondire i punti rossi.

        ### Disclaimer

        Questo strumento:

        - **non sostituisce una consulenza legale**,
        - è pensato come **pre-valutazione pratica** per PMI,
        - aiuta a capire **dove ha senso intervenire prima** e cosa può essere rimandato.
        """
    )
    st.info(
        "Tip: durante una demo con una PMI, puoi passare a questa pagina "
        "per chiarire cosa fa (e cosa non fa) il tool, aumentando la fiducia."
    )
