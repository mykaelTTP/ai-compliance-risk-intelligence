# app/pdf_utils.py

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def build_pdf_from_report(
    company_name: str | None,
    report_text: str,
) -> bytes:
    """
    Crea un PDF semplice a partire da un testo di report.
    Ritorna i bytes del PDF da usare in un download button Streamlit.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Margini
    x_margin = 20 * mm
    y_margin = 20 * mm
    y = height - y_margin

    # Titolo
    c.setFont("Helvetica-Bold", 14)
    title = "Valutazione Rischi AI & Dati"
    c.drawString(x_margin, y, title)
    y -= 12 * mm

    # Eventuale nome azienda
    if company_name:
        c.setFont("Helvetica", 11)
        c.drawString(x_margin, y, f"Azienda: {company_name}")
        y -= 10 * mm

    # Corpo del report, gestendo il ritorno a capo
    c.setFont("Helvetica", 10)
    max_width = width - 2 * x_margin
    for paragraph in report_text.split("\n"):
        # Spezza la riga se troppo lunga
        words = paragraph.split(" ")
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 10) <= max_width:
                line = test_line
            else:
                c.drawString(x_margin, y, line)
                y -= 5 * mm
                line = word
                if y < y_margin:
                    c.showPage()
                    y = height - y_margin
                    c.setFont("Helvetica", 10)
        if line:
            c.drawString(x_margin, y, line)
            y -= 5 * mm
            if y < y_margin:
                c.showPage()
                y = height - y_margin
                c.setFont("Helvetica", 10)

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
