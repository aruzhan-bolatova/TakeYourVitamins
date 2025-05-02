from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

def generate_supplement_pdf(supplement_logs):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Supplement Intake Report")

    y = height - 90
    c.setFont("Helvetica", 11)

    for log in supplement_logs:
        text = f"{log.intake_date} at {log.intake_time} – {log.supplement_name} | {log.dosage_taken} {log.unit}"
        if log.notes:
            text += f" | Notes: {log.notes}"

        if y < 50:
            c.showPage()
            y = height - 50

        c.drawString(50, y, text)
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

