
import json
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"
OUTPUT = ROOT / "output"

LAYOUT_FILE = JOBS / "layout.json"

CARD_BACK_IMAGE = ROOT / "assets" / "backs" / "magic_back.png"
TOKEN_BACK_IMAGE = ROOT / "assets" / "tokens" / "token_back.jpg"

PDF_FILE = OUTPUT / "magic_back.pdf"

GUIDE_WIDTH = 0.5 * mm
OUTER_GUIDE_LENGTH = 4 * mm
INNER_GUIDE_LENGTH = 1 * mm


def draw_cut_guides(
    pdf, x, y, width, height,
    is_left, is_right, is_top, is_bottom
):
    pdf.setStrokeColorRGB(1, 1, 1)
    pdf.setLineWidth(GUIDE_WIDTH)

    left_length = (
        OUTER_GUIDE_LENGTH if is_left
        else INNER_GUIDE_LENGTH
    )

    right_length = (
        OUTER_GUIDE_LENGTH if is_right
        else INNER_GUIDE_LENGTH
    )

    top_length = (
        OUTER_GUIDE_LENGTH if is_top
        else INNER_GUIDE_LENGTH
    )

    bottom_length = (
        OUTER_GUIDE_LENGTH if is_bottom
        else INNER_GUIDE_LENGTH
    )

    # Cantos superiores
    pdf.line(
        x - left_length, y + height,
        x, y + height
    )
    pdf.line(
        x + width, y + height,
        x + width + right_length, y + height
    )

    pdf.line(
        x, y + height,
        x, y + height + top_length
    )
    pdf.line(
        x + width, y + height,
        x + width, y + height + top_length
    )

    # Cantos inferiores
    pdf.line(
        x - left_length, y,
        x, y
    )
    pdf.line(
        x + width, y,
        x + width + right_length, y
    )

    pdf.line(
        x, y - bottom_length,
        x, y
    )
    pdf.line(
        x + width, y - bottom_length,
        x + width, y
    )


def draw_image_cell(pdf, image_path, cell, page_height):
    x_mm = cell["x_mm"]
    y_mm = cell["y_mm"]
    width_mm = cell["width_mm"]
    height_mm = cell["height_mm"]

    x = x_mm * mm
    width = width_mm * mm
    height = height_mm * mm

    y = page_height - (
        y_mm + height_mm
    ) * mm

    pdf.drawImage(
        str(image_path),
        x,
        y,
        width=width,
        height=height,
        preserveAspectRatio=True,
        anchor="c"
    )

    # Guias curtas nos quatro cantos
    draw_cut_guides(
        pdf,
        x,
        y,
        width,
        height,
        False,
        False,
        False,
        False
    )


def generate_pdf():
    if not LAYOUT_FILE.exists():
        print("Arquivo layout.json não encontrado.")
        return

    if not CARD_BACK_IMAGE.exists():
        print(
            f"Verso das cartas não encontrado: "
            f"{CARD_BACK_IMAGE}"
        )
        return

    if not TOKEN_BACK_IMAGE.exists():
        print(
            f"Verso dos tokens não encontrado: "
            f"{TOKEN_BACK_IMAGE}"
        )
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
    total_tokens = 0

    for sheet in layout["sheets"]:

        # Fundo preto integral da folha A4
        pdf.setFillColorRGB(0, 0, 0)
        pdf.rect(
            0,
            0,
            page_width,
            page_height,
            fill=1,
            stroke=0
        )

        cells = sheet["cells"]

        if cells:
            min_x = min(
                cell["x_mm"] for cell in cells
            )

            max_x = max(
                cell["x_mm"] + cell["width_mm"]
                for cell in cells
            )

            min_y = min(
                cell["y_mm"] for cell in cells
            )

            max_y = max(
                cell["y_mm"] + cell["height_mm"]
                for cell in cells
            )

        # Versos das cartas Magic
        for cell in cells:
            x_mm = cell["x_mm"]
            y_mm = cell["y_mm"]

            is_left = abs(x_mm - min_x) < 0.01
            is_right = abs(
                x_mm + cell["width_mm"] - max_x
            ) < 0.01

            is_top = abs(y_mm - min_y) < 0.01
            is_bottom = abs(
                y_mm + cell["height_mm"] - max_y
            ) < 0.01

            draw_image_cell(
                pdf,
                CARD_BACK_IMAGE,
                cell,
                page_height
            )

            # Guias externas mais longas na grade de cartas
            x = x_mm * mm
            y = page_height - (
                y_mm + cell["height_mm"]
            ) * mm

            draw_cut_guides(
                pdf,
                x,
                y,
                cell["width_mm"] * mm,
                cell["height_mm"] * mm,
                is_left,
                is_right,
                is_top,
                is_bottom
            )

            total_cards += 1

        # Versos dos tokens
        for cell in sheet.get("token_cells", []):
            draw_image_cell(
                pdf,
                TOKEN_BACK_IMAGE,
                cell,
                page_height
            )

            total_tokens += 1

        pdf.showPage()

    pdf.save()

    print("\n========== PDF BACK ==========")
    print(f"Versos de cartas inseridos: {total_cards}")
    print(f"Versos de tokens inseridos: {total_tokens}")
    print(f"Páginas A4: {len(layout['sheets'])}")
    print(
        f"Tamanho da página: "
        f"{page_width/mm:.0f} x {page_height/mm:.0f} mm"
    )
    print("Fundo da página: Preto")
    print("Cartas: Magic Back")
    print("Tokens: imagem personalizada")
    print("Guias: Brancas")
    print(f"Arquivo gerado: {PDF_FILE}")


if __name__ == "__main__":
    generate_pdf()
