
import requests

TARGET_SETS = [
    "usg", "ulg", "uds", "tmp",
    "mir", "mor", "ori", "dtk"
]

BASE_URL = "https://api.scryfall.com/cards/search"

ranked = []

for set_code in TARGET_SETS:
    print(f"Consultando {set_code.upper()}...")

    url = BASE_URL
    params = {
        "q": f"set:{set_code}",
        "order": "usd",
        "dir": "desc",
        "unique": "prints"
    }

    while url:
        response = requests.get(
            url,
            params=params if url == BASE_URL else None,
            headers={"User-Agent": "MagicPrintManager/1.0"},
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        for card in data.get("data", []):
            prices = card.get("prices") or {}
            price = prices.get("usd")

            if not price:
                continue

            ranked.append({
                "name": card.get("name"),
                "set": card.get("set", "").upper(),
                "number": card.get("collector_number"),
                "price": float(price)
            })

        if data.get("has_more"):
            url = data.get("next_page")
        else:
            url = None

        params = None

ranked.sort(
    key=lambda card: card["price"],
    reverse=True
)

print("\n========== 9 CARTAS MAIS CARAS ==========\n")

for index, card in enumerate(ranked[:9], 1):
    print(
        f"{index}. {card['name']} "
        f"({card['set']} #{card['number']}) "
        f"- US$ {card['price']:.2f}"
    )

print(f"\nCartas com preço encontrado: {len(ranked)}")
