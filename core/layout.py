
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"

# Dimensões em milímetros
CARD_WIDTH = 63
CARD_HEIGHT = 88

SHEET_WIDTH = 210
SHEET_HEIGHT = 297

COLUMNS = 3
ROWS = 3
CARDS_PER_SHEET = COLUMNS * ROWS

GAP_X = 2
GAP_Y = 2


def generate_layout():
    input_file = JOBS / "resolved_job.json"

    if not input_file.exists():
        print("Arquivo resolved_job.json não encontrado.")
        return

    job = json.loads(
        input_file.read_text(encoding="utf-8")
    )

    positions = []

    for card in job["cards"]:
        for copy_number in range(1, card["quantity"] + 1):
            positions.append({
                "name": card["name"],
                "set": card["set"],
                "collector_number": card["collector_number"],
                "image": card["image"],
                "id": card["id"],
                "copy": copy_number
            })

    total_cards = len(positions)
    total_sheets = math.ceil(total_cards / CARDS_PER_SHEET)

    # Centraliza a grade na folha A4
    grid_width = (COLUMNS * CARD_WIDTH) + ((COLUMNS - 1) * GAP_X)
    grid_height = (ROWS * CARD_HEIGHT) + ((ROWS - 1) * GAP_Y)

    margin_x = (SHEET_WIDTH - grid_width) / 2
    margin_y = (SHEET_HEIGHT - grid_height) / 2

    sheets = []

    for sheet_number in range(total_sheets):
        sheet_cards = positions[
            sheet_number * CARDS_PER_SHEET:
            (sheet_number + 1) * CARDS_PER_SHEET
        ]

        cells = []

        for index, card in enumerate(sheet_cards):
            column = index % COLUMNS
            row = index // COLUMNS

            x = margin_x + column * (CARD_WIDTH + GAP_X)
            y = margin_y + row * (CARD_HEIGHT + GAP_Y)

            cells.append({
                "position": index + 1,
                "x_mm": round(x, 2),
                "y_mm": round(y, 2),
                "width_mm": CARD_WIDTH,
                "height_mm": CARD_HEIGHT,
                "card": card
            })

        sheets.append({
            "sheet": sheet_number + 1,
            "cells": cells,
            "empty_positions": CARDS_PER_SHEET - len(cells)
        })

    output = {
        "total_cards": total_cards,
        "total_sheets": total_sheets,
        "grid": {
            "columns": COLUMNS,
            "rows": ROWS,
            "card_width_mm": CARD_WIDTH,
            "card_height_mm": CARD_HEIGHT,
            "sheet_width_mm": SHEET_WIDTH,
            "sheet_height_mm": SHEET_HEIGHT,
            "margin_x_mm": margin_x,
            "margin_y_mm": margin_y
        },
        "sheets": sheets
    }

    output_file = JOBS / "layout.json"

    output_file.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\n========== LAYOUT ==========")
    print(f"Cartas distribuídas: {total_cards}")
    print(f"Folhas A4: {total_sheets}")
    print(f"Posições por folha: {CARDS_PER_SHEET}")
    print(f"Margem horizontal: {margin_x:.2f} mm")
    print(f"Margem vertical: {margin_y:.2f} mm")

    for sheet in sheets:
        print(
            f"Folha {sheet['sheet']}: "
            f"{len(sheet['cells'])} cartas | "
            f"{sheet['empty_positions']} posições vazias"
        )

    print(f"\nArquivo gerado: {output_file}")


if __name__ == "__main__":
    generate_layout()
