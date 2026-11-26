
import json
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"
OUTPUT = ROOT / "output"

LAYOUT_FILE = JOBS / "layout.json"
PDF_FILE = OUTPUT / "magic_front.pdf"

GUIDE_WIDTH = 0.5 * mm
OUTER_GUIDE_LENGTH = 4 * mm
INNER_GUIDE_LENGTH = 1 * mm

# Aparência dos tokens
TOKEN_BACKGROUND = HexColor("#F0E4C8")
TOKEN_BORDER = HexColor("#B49A6A")
TOKEN_TEXT = HexColor("#302719")


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


def fit_font_size(text, font_name, max_size, max_width):
    size = max_size

    while size > 2:
        if stringWidth(text, font_name, size) <= max_width:
            return size
        size -= 0.2

    return 2


def draw_token(pdf, cell, page_height):
    token = cell["token"]

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

    # Fundo pergaminho
    pdf.setFillColor(TOKEN_BACKGROUND)
    pdf.setStrokeColor(TOKEN_BORDER)
    pdf.setLineWidth(0.35)

    pdf.rect(
        x,
        y,
        width,
        height,
        stroke=1,
        fill=1
    )

    name = token["name"]
    power = token["power"]
    description = token["description"]

    # Texto centralizado e ajustado ao espaço disponível
    center_x = x + width / 2

    lines = [
        (name, "Helvetica-Bold", 3.8),
        (power, "Helvetica-Bold", 4.2),
        (description, "Helvetica", 2.8)
    ]

    positions = [
        y + height * 0.70,
        y + height * 0.49,
        y + height * 0.27
    ]

    pdf.setFillColor(TOKEN_TEXT)

    for (text, font, max_size), text_y in zip(
        lines, positions
    ):
        font_size = fit_font_size(
            text,
            font,
            max_size,
            width - 1.2 * mm
        )

        pdf.setFont(font, font_size)
        pdf.drawCentredString(
            center_x,
            text_y,
            text
        )

    # Guias curtas para os tokens.
    # Mantemos todas com 1 mm para evitar ultrapassar
    # as margens físicas da folha.
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

    layout = json.loads(
        LAYOUT_FILE.read_text(encoding="utf-8")
    )

    OUTPUT.mkdir(exist_ok=True)

    page_width, page_height = A4

    pdf = canvas.Canvas(
        str(PDF_FILE),
        pagesize=A4
    )

    pdf.setTitle("Magic Print Manager - Front")

    total_cards = 0
    total_tokens = 0

    for sheet in layout["sheets"]:

        cells = sheet["cells"]

        # Fundo preto da página inteira
        pdf.setFillColorRGB(0, 0, 0)
        pdf.rect(
            0,
            0,
            page_width,
            page_height,
            stroke=0,
            fill=1
        )

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

        # Frente das cartas Magic
        for cell in cells:
            card = cell["card"]
            image_path = Path(card["image"])

            if not image_path.is_absolute():
                image_path = ROOT / image_path

            if not image_path.exists():
                print(
                    f"Imagem não encontrada: {image_path}"
                )
                return

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

            is_left = abs(x_mm - min_x) < 0.01
            is_right = abs(
                x_mm + width_mm - max_x
            ) < 0.01

            is_top = abs(y_mm - min_y) < 0.01
            is_bottom = abs(
                y_mm + height_mm - max_y
            ) < 0.01

            draw_cut_guides(
                pdf,
                x,
                y,
                width,
                height,
                is_left,
                is_right,
                is_top,
                is_bottom
            )

            total_cards += 1

        # Frente dos tokens
        for cell in sheet.get("token_cells", []):
            draw_token(
                pdf,
                cell,
                page_height
            )

            total_tokens += 1

        pdf.showPage()

    pdf.save()

    print("\n========== PDF FRONT ==========")
    print(f"Cartas inseridas: {total_cards}")
    print(f"Tokens inseridos: {total_tokens}")
    print(f"Páginas A4: {len(layout['sheets'])}")
    print(
        f"Tamanho da página: "
        f"{page_width/mm:.0f} x {page_height/mm:.0f} mm"
    )
    print("Fundo das cartas: Preto")
    print("Fundo dos tokens: Pergaminho")
    print("Guias: Brancas")
    print(f"Arquivo gerado: {PDF_FILE}")


if __name__ == "__main__":
    generate_pdf()
