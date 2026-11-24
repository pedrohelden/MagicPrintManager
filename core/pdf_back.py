
import json
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"
OUTPUT = ROOT / "output"

LAYOUT_FILE = JOBS / "layout.json"
BACK_IMAGE = ROOT / "assets" / "backs" / "magic_back.png"
PDF_FILE = OUTPUT / "magic_back.pdf"


def generate_pdf():
    if not LAYOUT_FILE.exists():
        print("Arquivo layout.json não encontrado.")
        return

    if not BACK_IMAGE.exists():
        print("Imagem do verso não encontrada.")
        return

    layout = json.loads(
        LAYOUT_FILE.read_text(encoding="utf-8")
    )

    OUTPUT.mkdir(exist_ok=True)

    page_width, page_height = A4

    pdf = canvas.Canvas(
        str(PDF_FILE),
        pagesize=A4
    )

    pdf.setTitle("Magic Print Manager - Back")

    total_cards = 0

    for sheet in layout["sheets"]:

        for cell in sheet["cells"]:
            x = cell["x_mm"] * mm
            width = cell["width_mm"] * mm
            height = cell["height_mm"] * mm

            y = page_height - (
                cell["y_mm"] + cell["height_mm"]
            ) * mm

            pdf.drawImage(
                str(BACK_IMAGE),
                x,
                y,
                width=width,
                height=height,
                preserveAspectRatio=True,
                anchor="c"
            )

            pdf.setStrokeColor(
                Color(0.45, 0.45, 0.45, alpha=0.8)
            )
            pdf.setLineWidth(0.25)

            pdf.rect(
                x,
                y,
                width,
                height,
                stroke=1,
                fill=0
            )

            total_cards += 1

        pdf.showPage()

    pdf.save()

    print("\n========== PDF BACK ==========")
    print(f"Versos inseridos: {total_cards}")
    print(f"Páginas A4: {len(layout['sheets'])}")
    print(f"Arquivo gerado: {PDF_FILE}")


if __name__ == "__main__":
    generate_pdf()
