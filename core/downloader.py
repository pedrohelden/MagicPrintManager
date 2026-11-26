
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent

COLLECTIONS = {
    "usg": {"name": "Urza's Saga", "year": "1998"},
    "ulg": {"name": "Urza's Legacy", "year": "1999"},
    "uds": {"name": "Urza's Destiny", "year": "1999"},
    "tmp": {"name": "Tempest", "year": "1997"},
    "mor": {"name": "Morningtide", "year": "2008"},
    "ori": {"name": "Magic Origins", "year": "2015"},
    "dtk": {"name": "Dragons of Tarkir", "year": "2015"},
    "mir": {"name": "Mirage", "year": "1996"},	
}

HEADERS = {
    "User-Agent": "MagicPrintManager/0.1",
    "Accept": "application/json",
}

BASE_URL = "https://api.scryfall.com"


def download_collection(code, info):
    folder = ROOT / "library" / info["year"] / code.upper()
    folder.mkdir(parents=True, exist_ok=True)

    catalog = []
    page = f"{BASE_URL}/cards/search"
    params = {"q": f"set:{code} game:paper"}

    print(f"\nConsultando {info['name']}...")

    while page:
        response = requests.get(
            page,
            params=params,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        for card in data["data"]:
            image_url = card.get(
                "image_uris", {}
            ).get("large")

            if not image_url and card.get("card_faces"):
                image_url = card["card_faces"][0].get(
                    "image_uris", {}
                ).get("large")

            if not image_url:
                print(f"Sem imagem: {card['name']}")
                continue

            filename = (
                f"{card['collector_number']}_"
                f"{card['id'][:8]}.jpg"
            )

            image_path = folder / filename

            if not image_path.exists():
                image = requests.get(
                    image_url,
                    headers=HEADERS,
                    timeout=30
                )
                image.raise_for_status()
                image_path.write_bytes(image.content)

            catalog.append({
                "id": card["id"],
                "name": card["name"],
                "set": card["set"],
                "set_name": card["set_name"],
                "collector_number": card["collector_number"],
                "rarity": card["rarity"],
                "image": str(image_path.relative_to(ROOT))
            })

            print(f"OK: {card['name']}")

        page = data.get("next_page")
        params = None

        time.sleep(0.12)

    catalog_path = folder / "catalog.json"

    catalog_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(
        f"\n{info['name']}: "
        f"{len(catalog)} cartas catalogadas."
    )


def main():
    print("========== MAGIC PRINT MANAGER ==========")
    print("Atualizando catálogos de cartas...\n")

    for code, info in COLLECTIONS.items():
        try:
            download_collection(code, info)
        except requests.RequestException as error:
            print(
                f"\nERRO ao consultar {info['name']}: {error}"
            )
            raise

    print("\nDownload concluído!")


if __name__ == "__main__":
    main()
