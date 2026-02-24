# app/db.py

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Percorso del file SQLite (nella root del progetto)
DB_PATH = Path(__file__).resolve().parent.parent / "assessments.db"


def get_connection():
    """Ritorna una connessione SQLite al file assessments.db."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Crea la tabella assessments se non esiste."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            company_name TEXT,
            final_score REAL NOT NULL,
            risk_class TEXT NOT NULL,
            ai_risk REAL NOT NULL,
            gdpr_risk REAL NOT NULL,
            operational_risk REAL NOT NULL,
            urgency_risk REAL NOT NULL,
            answers_json TEXT NOT NULL,
            report_text TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


def log_assessment(company_name, answers, result):
    """
    Salva una valutazione nel database.

    result deve avere attributi:
    - final_score
    - risk_class
    - ai_risk
    - gdpr_risk
    - operational_risk
    - urgency_risk
    - report
    """
    conn = get_connection()
    cur = conn.cursor()

    created_at = datetime.now().isoformat(timespec="seconds")

    cur.execute(
        """
        INSERT INTO assessments (
            created_at,
            company_name,
            final_score,
            risk_class,
            ai_risk,
            gdpr_risk,
            operational_risk,
            urgency_risk,
            answers_json,
            report_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            created_at,
            company_name,
            float(result.final_score),
            str(result.risk_class),
            float(result.ai_risk),
            float(result.gdpr_risk),
            float(result.operational_risk),
            float(result.urgency_risk),
            json.dumps(answers, ensure_ascii=False),
            result.report,
        ),
    )

    conn.commit()
    conn.close()


def get_recent_assessments(limit=50):
    """
    Ritorna le ultime N valutazioni come lista di tuple:

    (id, created_at, company_name, final_score, risk_class,
     ai_risk, gdpr_risk, operational_risk, urgency_risk)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id,
            created_at,
            company_name,
            final_score,
            risk_class,
            ai_risk,
            gdpr_risk,
            operational_risk,
            urgency_risk
        FROM assessments
        ORDER BY datetime(created_at) DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_last_assessment():
    """
    Ritorna l'ultima valutazione (una sola riga) oppure None.
    """
    rows = get_recent_assessments(limit=1)
    return rows[0] if rows else None


def clear_all_assessments():
    """Cancella tutte le righe dalla tabella assessments (senza eliminare il file)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM assessments;")
    conn.commit()
    conn.close()
