# clear_db.py

from app.db import clear_all_assessments, init_db

# Assicura che la tabella esista
init_db()

# Cancella tutte le valutazioni
clear_all_assessments()
print("Storico valutazioni cancellato (tabella assessments svuotata).")
