
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"

# Dimensões da folha A4
SHEET_WIDTH = 210
SHEET_HEIGHT = 297

# Cartas Magic
CARD_WIDTH = 63
CARD_HEIGHT = 88
CARD_COLUMNS = 3
CARD_ROWS = 3
CARDS_PER_SHEET = CARD_COLUMNS * CARD_ROWS

# Tokens e marcadores
TOKEN_WIDTH = 12
TOKEN_HEIGHT = 12
TOKENS_PER_SHEET = 52

# Espaçamento
GAP = 1

# Posições das cartas
CARD_START_X = 3
CARD_START_Y = 15.5

# Kit universal de tokens: 32 unidades por folha
TOKEN_TYPES = [
    {
        "id": "goblin",
        "name": "GOBLIN",
        "power": "1/1",
        "description": "RED",
        "quantity": 4
    },
    {
        "id": "soldier",
        "name": "SOLDIER",
        "power": "1/1",
        "description": "WHITE",
        "quantity": 3
    },
    {
        "id": "human",
        "name": "HUMAN",
        "power": "1/1",
        "description": "ANY COLOR",
        "quantity": 3
    },
    {
        "id": "zombie",
        "name": "ZOMBIE",
        "power": "2/2",
        "description": "BLACK",
        "quantity": 2
    },
    {
        "id": "spirit",
        "name": "SPIRIT",
        "power": "1/1",
        "description": "WHITE / FLYING",
        "quantity": 2
    },
    {
        "id": "saproling",
        "name": "SAPROLING",
        "power": "1/1",
        "description": "GREEN",
        "quantity": 2
    },
    {
        "id": "beast",
        "name": "BEAST",
        "power": "3/3",
        "description": "GREEN",
        "quantity": 2
    },
    {
        "id": "angel",
        "name": "ANGEL",
        "power": "4/4",
        "description": "WHITE / FLYING",
        "quantity": 1
    },
    {
        "id": "thopter",
        "name": "THOPTER",
        "power": "1/1",
        "description": "COLORLESS / FLYING",
        "quantity": 1
    },
    {
        "id": "treasure",
        "name": "TREASURE",
        "power": "",
        "description": "ARTIFACT",
        "quantity": 3
    },
    {
        "id": "food",
        "name": "FOOD",
        "power": "",
        "description": "ARTIFACT",
        "quantity": 3
    },
    {
        "id": "clue",
        "name": "CLUE",
        "power": "",
        "description": "ARTIFACT",
        "quantity": 2
    },
    {
        "id": "blood",
        "name": "BLOOD",
        "power": "",
        "description": "ARTIFACT",
        "quantity": 2
    },
    {
        "id": "map",
        "name": "MAP",
        "power": "",
        "description": "ARTIFACT",
        "quantity": 1
    },
    {
        "id": "powerstone",
        "name": "POWERSTONE",
        "power": "",
        "description": "ARTIFACT",
        "quantity": 1
    }
]

# Kit universal de marcadores: 20 unidades por folha
MARKER_TYPES = [
    {
        "id": "plus_one",
        "name": "+1/+1",
        "power": "",
        "description": "COUNTER",
        "quantity": 5
    },
    {
        "id": "minus_one",
        "name": "-1/-1",
        "power": "",
        "description": "COUNTER",
        "quantity": 5
    },
    {
        "id": "loyalty",
        "name": "LOYALTY",
        "power": "",
        "description": "COUNTER",
        "quantity": 2
    },
    {
        "id": "charge",
        "name": "CHARGE",
        "power": "",
        "description": "COUNTER",
        "quantity": 2
    },
    {
        "id": "energy",
        "name": "ENERGY",
        "power": "",
        "description": "COUNTER",
        "quantity": 1
    },
    {
        "id": "shield",
        "name": "SHIELD",
        "power": "",
        "description": "COUNTER",
        "quantity": 1
    },
    {
        "id": "stun",
        "name": "STUN",
        "power": "",
        "description": "COUNTER",
        "quantity": 1
    },
    {
        "id": "experience",
        "name": "EXPERIENCE",
        "power": "",
        "description": "COUNTER",
        "quantity": 1
    },
    {
        "id": "poison",
        "name": "POISON",
        "power": "",
        "description": "COUNTER",
        "quantity": 1
    },
    {
        "id": "generic",
        "name": "GENERIC",
        "power": "",
        "description": "COUNTER",
        "quantity": 1
    }
]


def build_distribution(types):
    """Cria uma distribuição intercalada respeitando as quantidades."""

    distribution = []

    max_quantity = max(
        item["quantity"] for item in types
    )

    for copy_number in range(max_quantity):
        for item in types:
            if copy_number < item["quantity"]:
                distribution.append({
                    "id": item["id"],
                    "name": item["name"],
                    "power": item["power"],
                    "description": item["description"],
                    "copy": copy_number + 1
                })

    return distribution


def build_token_positions():
    """Cria as 52 posições de tokens e marcadores na folha A4."""

    positions = []

    # Fileira superior: 16 tokens
    for column in range(16):
        positions.append({
            "x_mm": round(1.5 + column * (TOKEN_WIDTH + GAP), 2),
            "y_mm": 2.5
        })

    # Coluna direita: 20 marcadores
    for row in range(20):
        positions.append({
            "x_mm": 195,
            "y_mm": round(19 + row * (TOKEN_HEIGHT + GAP), 2)
        })

    # Fileira inferior: 16 tokens
    for column in range(16):
        positions.append({
            "x_mm": round(1.5 + column * (TOKEN_WIDTH + GAP), 2),
            "y_mm": 282.5
        })

    return positions


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

    if total_cards == 0:
        print("Nenhuma carta encontrada.")
        return

    total_sheets = math.ceil(
        total_cards / CARDS_PER_SHEET
    )

    # Monta um kit completo para cada folha.
    token_distribution = build_distribution(TOKEN_TYPES)
    marker_distribution = build_distribution(MARKER_TYPES)

    if len(token_distribution) != 32:
        raise ValueError("A distribuição de tokens deve conter 32 unidades.")

    if len(marker_distribution) != 20:
        raise ValueError("A distribuição de marcadores deve conter 20 unidades.")

    auxiliary_distribution = (
        token_distribution + marker_distribution
    )

    token_positions = build_token_positions()

    sheets = []

    for sheet_number in range(total_sheets):

        # Distribuição das cartas
        sheet_cards = positions[
            sheet_number * CARDS_PER_SHEET:
            (sheet_number + 1) * CARDS_PER_SHEET
        ]

        cells = []

        for index, card in enumerate(sheet_cards):
            column = index % CARD_COLUMNS
            row = index // CARD_COLUMNS

            x = CARD_START_X + column * (CARD_WIDTH + GAP)
            y = CARD_START_Y + row * (CARD_HEIGHT + GAP)

            cells.append({
                "position": index + 1,
                "x_mm": round(x, 2),
                "y_mm": round(y, 2),
                "width_mm": CARD_WIDTH,
                "height_mm": CARD_HEIGHT,
                "card": card
            })

        # Repete o kit universal completo em cada folha.
        token_cells = []

        for index, item in enumerate(auxiliary_distribution):
            position = token_positions[index]

            token_cells.append({
                "position": index + 1,
                "x_mm": position["x_mm"],
                "y_mm": position["y_mm"],
                "width_mm": TOKEN_WIDTH,
                "height_mm": TOKEN_HEIGHT,
                "token": item
            })

        sheets.append({
            "sheet": sheet_number + 1,
            "cells": cells,
            "token_cells": token_cells,
            "empty_positions": CARDS_PER_SHEET - len(cells)
        })

    output = {
        "total_cards": total_cards,
        "total_tokens": total_sheets * TOKENS_PER_SHEET,
        "total_sheets": total_sheets,
        "cards_per_sheet": CARDS_PER_SHEET,
        "tokens_per_sheet": TOKENS_PER_SHEET,
        "token_types": TOKEN_TYPES,
        "marker_types": MARKER_TYPES,
        "grid": {
            "card_width_mm": CARD_WIDTH,
            "card_height_mm": CARD_HEIGHT,
            "token_width_mm": TOKEN_WIDTH,
            "token_height_mm": TOKEN_HEIGHT,
            "sheet_width_mm": SHEET_WIDTH,
            "sheet_height_mm": SHEET_HEIGHT,
            "gap_mm": GAP
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
    print(f"Cartas por folha: {CARDS_PER_SHEET}")
    print(f"Tokens por folha: {len(token_distribution)}")
    print(f"Marcadores por folha: {len(marker_distribution)}")
    print(f"Total de fichas por folha: {TOKENS_PER_SHEET}")

    for sheet in sheets:
        print(
            f"Folha {sheet['sheet']}: "
            f"{len(sheet['cells'])} cartas | "
            f"{len(sheet['token_cells'])} fichas"
        )

    print("\nDistribuição de tokens:")

    for item in TOKEN_TYPES:
        print(f"{item['name']}: {item['quantity']}")

    print("\nDistribuição de marcadores:")

    for item in MARKER_TYPES:
        print(f"{item['name']}: {item['quantity']}")

    print(f"\nArquivo gerado: {output_file}")


if __name__ == "__main__":
    generate_layout()
