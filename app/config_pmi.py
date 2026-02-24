# app/config_pmi.py

"""
Configurazione specifica per la sezione PIM (Product Information Management) + AI.
Contiene mapping codice -> label in italiano per le opzioni usate nella UI.
"""

PMI_AI_FEATURES = {
    "product_descriptions": "Generazione descrizioni prodotto (testi delle schede prodotto)",
    "translations": "Traduzioni automatiche (es. italiano → inglese, ecc.)",
    "seo_optimization": "Ottimizzazione SEO (titoli, descrizioni, keyword per motori di ricerca)",
    "categorization": "Categorizzazione automatica prodotti (assegnazione categorie / tag)",
    "dynamic_pricing": "Prezzi dinamici / raccomandazioni di prezzo",
}

PMI_TRAINING_SOURCES = {
    "own_product_data": "Dati di prodotto interni (catalogo, schede prodotto)",
    "customer_data": "Dati clienti (ricerche, recensioni, cronologia acquisti)",
    "open_licensed_data": "Dati con licenze aperte / autorizzate (open data, dataset con licenza)",
    "web_scraped": "Dati estratti dal web (web scraping di siti esterni)",
    "third_party_datasets": "Dataset forniti da terzi (fornitori, partner, vendor)",
}

PMI_THIRD_PARTY_MODELS = {
    "none": "Nessun modello di terze parti (solo modelli interni)",
    "some": "Uso limitato di modelli di terze parti (es. solo traduzioni o riassunti)",
    "extensive": "Uso estensivo di modelli di terze parti (gran parte delle funzionalità AI)",
}
