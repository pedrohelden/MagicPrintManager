
import csv
import json
import time
import uuid
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library" / "test_lands"
JOBS = ROOT / "jobs"

LANDS = {
    "PLAINS": "Plains",
    "ISLAND": "Island",
    "SWAMP": "Swamp",
    "MOUNTAIN": "Mountain",
    "FOREST": "Forest"
}

TARGET_PER_TYPE = 9

HEADERS = {
    "User-Agent": "MagicPrintManager/0.1",
    "Accept": "application/json"
}


def fetch_land_printings(name):
    url = "https://api.scryfall.com/cards/search"

    params = {
        "q": f'!"{name}" t:basic game:paper',
        "unique": "art",
        "order": "released",
        "dir": "asc"
    }

    results = []

    while url:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        results.extend(data.get("data", []))

        if data.get("has_more"):
            url = data["next_page"]
            params = None
            time.sleep(0.12)
        else:
            url = None

    return results


def select_diverse_printings(cards):
    # Uma impressão por coleção, para evitar repetição
    unique_sets = {}

    for card in cards:
        set_code = card["set"].upper()

        if set_code not in unique_sets:
            unique_sets[set_code] = card

    candidates = sorted(
        unique_sets.values(),
        key=lambda card: card.get("released_at", "")
    )

    if len(candidates) < TARGET_PER_TYPE:
        raise RuntimeError(
            f"Apenas {len(candidates)} coleções disponíveis."
        )

    # Distribui a seleção ao longo das coleções disponíveis
    total = len(candidates)

    indexes = [
        round(i * (total - 1) / (TARGET_PER_TYPE - 1))
        for i in range(TARGET_PER_TYPE)
    ]

    return [candidates[i] for i in indexes]


def download_image(card, folder):
    image_url = card.get("image_uris", {}).get("large")

    if not image_url:
        raise RuntimeError(
            f"Imagem não disponível: {card['name']} "
            f"({card['set']})"
        )

    filename = (
        f"{card['set']}_{card['collector_number']}_"
        f"{uuid.uuid4().hex[:8]}.jpg"
    )

    image_path = folder / filename

    response = requests.get(
        image_url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    image_path.write_bytes(response.content)

    return image_path


def main():
    LIBRARY.mkdir(parents=True, exist_ok=True)
    JOBS.mkdir(parents=True, exist_ok=True)

    csv_rows = []
    total = 0

    for folder_name, land_name in LANDS.items():
        print(f"\nBuscando {land_name}...")

        folder = LIBRARY / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        cards = fetch_land_printings(land_name)
        selected = select_diverse_printings(cards)

        catalog = []

        for card in selected:
            image_path = download_image(card, folder)

            relative_image = image_path.relative_to(ROOT).as_posix()

            catalog.append({
                "id": card["id"],
                "name": card["name"],
                "set": card["set"].upper(),
                "collector_number": card["collector_number"],
                "image": relative_image,
                "released_at": card.get("released_at"),
                "full_art": card.get("full_art", False),
                "frame": card.get("frame"),
                "border_color": card.get("border_color"),
                "finishes": card.get("finishes", [])
            })

            csv_rows.append({
                "card": card["name"],
                "set": card["set"].upper(),
                "quantity": 1
            })

            print(
                f"  OK: {card['name']} | "
                f"{card['set'].upper()} | "
                f"{card['collector_number']}"
            )

            total += 1
            time.sleep(0.12)

        catalog_file = folder / "catalog.json"

        catalog_file.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print(f"{land_name}: {len(catalog)} imagens salvas.")

    csv_file = JOBS / "test_lands.csv"

    with csv_file.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["card", "set", "quantity"]
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    print("\n========== DOWNLOAD CONCLUÍDO ==========")
    print(f"Total de terrenos: {total}")
    print(f"CSV gerado: {csv_file}")


if __name__ == "__main__":
    main()
