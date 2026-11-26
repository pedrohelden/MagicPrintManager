
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

# Paletas vivas, mas equilibradas.
# Cada ficha mantém três faixas horizontais iguais.

PALETTES = {
    "red": ("#D94A42", "#F2B84B", "#963A3A"),
    "blue": ("#2878B8", "#69B5D0", "#24517C"),
    "green": ("#368A4A", "#A7BD50", "#286345"),
    "white": ("#D9B85A", "#F0DFA5", "#C9A64B"),
    "black": ("#68458C", "#81709B", "#302944"),
    "artifact": ("#B47A27", "#E5BB45", "#8B5A25"),
    "creature": ("#327FB1", "#E0B84A", "#387A55"),
    "marker_positive": ("#398B4B", "#A6C75A", "#24683B"),
    "marker_negative": ("#C34D48", "#E39A46", "#873842"),
    "marker_special": ("#7751A2", "#C17BAA", "#48366F"),
    "marker_energy": ("#278AA8", "#D4B947", "#23617C"),
    "marker_generic": ("#596A83", "#AAB5C5", "#39465A"),

    # Human 1/1 - Any Color: três tons de azul.
    "human": ("#4779B8", "#6797CC", "#355D96"),
}


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

    while size > 2.5:
        if stringWidth(text, font_name, size) <= max_width:
            return size
        size -= 0.2

    return 2.5


def get_token_palette(token):
    name = token.get("name", "").lower()
    power = token.get("power", "").lower()
    description = token.get("description", "").lower()

    combined = f"{name} {power} {description}"

    # Human 1/1 - Any Color.
    # Esta regra precisa vir antes das regras genéricas de cor.
    if "human" in combined and any(word in combined for word in (
        "any color", "any colour", "qualquer cor"
    )):
        return PALETTES["human"]

    # Marcadores positivos e negativos
    if "+1/+1" in combined:
        return PALETTES["marker_positive"]

    if "-1/-1" in combined:
        return PALETTES["marker_negative"]

    # Marcadores especiais
    if any(word in combined for word in (
        "poison", "veneno", "loyalty", "lealdade",
        "experience", "experiência"
    )):
        return PALETTES["marker_special"]

    if any(word in combined for word in (
        "energy", "energia", "charge", "carga"
    )):
        return PALETTES["marker_energy"]

    if any(word in combined for word in (
        "shield", "escudo", "stun", "atordoamento"
    )):
        return PALETTES["blue"]

    if any(word in combined for word in (
        "generic", "genérico"
    )):
        return PALETTES["marker_generic"]

    # Fichas de artefato e recursos
    if any(word in combined for word in (
        "treasure", "food", "clue", "blood",
        "map", "powerstone"
    )):
        return PALETTES["artifact"]

    # Identidade de cor das criaturas
    if any(word in combined for word in (
        "red", "vermelho"
    )):
        return PALETTES["red"]

    if any(word in combined for word in (
        "blue", "azul", "flying"
    )):
        return PALETTES["blue"]

    if any(word in combined for word in (
        "green", "verde", "beast", "saproling"
    )):
        return PALETTES["green"]

    if any(word in combined for word in (
        "black", "preto", "zombie"
    )):
        return PALETTES["black"]

    if any(word in combined for word in (
        "white", "branco", "soldier", "angel"
    )):
        return PALETTES["white"]

    return PALETTES["creature"]


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

    name = token.get("name", "")
    power = token.get("power", "")
    description = token.get("description", "")

    colors = get_token_palette(token)

    # Três faixas horizontais de mesma altura.
    band_height = height / 3

    bands = [
        (name, colors[0], 4.5, "#FFFFFF"),
        (power, colors[1], 5.2, "#202020"),
        (description, colors[2], 3.5, "#FFFFFF")
    ]

    for index, (text, color, max_size, text_color) in enumerate(bands):
        band_y = y + height - (index + 1) * band_height

        pdf.setFillColor(HexColor(color))
        pdf.rect(
            x,
            band_y,
            width,
            band_height,
            stroke=0,
            fill=1
        )

        pdf.setFillColor(HexColor(text_color))

        font = "Helvetica-Bold"

        font_size = fit_font_size(
            text,
            font,
            max_size,
            width - 0.8 * mm
        )

        pdf.setFont(font, font_size)

        pdf.drawCentredString(
            x + width / 2,
            band_y + (band_height - font_size) / 2 + 1,
            text
        )

    # Contorno externo da ficha
    pdf.setStrokeColor(HexColor("#171717"))
    pdf.setLineWidth(0.45)
    pdf.rect(
        x,
        y,
        width,
        height,
        stroke=1,
        fill=0
    )

    # Guias curtas para os tokens.
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

        # Frente dos tokens e marcadores
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
    print(f"Tokens e marcadores inseridos: {total_tokens}")
    print(f"Páginas A4: {len(layout['sheets'])}")
    print(
        f"Tamanho da página: "
        f"{page_width/mm:.0f} x {page_height/mm:.0f} mm"
    )
    print("Fundo das cartas: Preto")
    print("Fichas: 3 faixas coloridas")
    print("Cores: Vivas e equilibradas")
    print("Tipografia: Helvetica-Bold")
    print("Guias: Brancas")
    print(f"Arquivo gerado: {PDF_FILE}")


if __name__ == "__main__":
    generate_pdf()
