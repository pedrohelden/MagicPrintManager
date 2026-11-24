
import json
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

COLLECTIONS = {
    "USG": ("1998", "Urza's Saga"),
    "ULG": ("1999", "Urza's Legacy"),
    "UDS": ("1999", "Urza's Destiny"),
}


def validate_collection(code, year, name):
    folder = ROOT / "library" / year / code
    catalog_file = folder / "catalog.json"

    print(f"\n{'=' * 50}")
    print(f"{name} ({code})")

    if not catalog_file.exists():
        print("ERRO: catalog.json não encontrado")
        return

    catalog = json.loads(catalog_file.read_text(encoding="utf-8"))

    valid = 0
    invalid = []
    dimensions = set()

    for card in catalog:
        image_path = ROOT / card["image"]

        if not image_path.exists():
            invalid.append(card["name"] + " - arquivo ausente")
            continue

        try:
            with Image.open(image_path) as img:
                img.verify()

            with Image.open(image_path) as img:
                dimensions.add(img.size)

            valid += 1

        except Exception as error:
            invalid.append(card["name"] + f" - {error}")

    try:
        response = requests.get(
            f"https://api.scryfall.com/sets/{code.lower()}",
            timeout=30
        )
        response.raise_for_status()
        official = response.json().get("card_count")
    except requests.RequestException:
        official = None

    print(f"Cartas no catálogo: {len(catalog)}")
    print(f"Imagens válidas: {valid}")
    print(f"Imagens com problema: {len(invalid)}")
    print(f"Dimensões encontradas: {dimensions}")
    print(f"Total informado pelo Scryfall: {official}")

    if official is not None:
        print(f"Diferença para o catálogo: {official - len(catalog)}")

    for error in invalid:
        print("PROBLEMA:", error)


def main():
    for code, (year, name) in COLLECTIONS.items():
        validate_collection(code, year, name)

    print("\nValidação concluída!")


if __name__ == "__main__":
    main()
