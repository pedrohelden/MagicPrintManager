
import csv
import json
import math
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library"
JOBS = ROOT / "jobs"


def load_library():
    index = defaultdict(list)

    for catalog_file in LIBRARY.rglob("catalog.json"):
        cards = json.loads(
            catalog_file.read_text(encoding="utf-8")
        )

        for card in cards:
            card["image_path"] = str(ROOT / card["image"])
            index[card["name"].casefold()].append(card)

    return index


def scan_job(filename, collection_name_override=None):
    csv_path = JOBS / filename

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {csv_path}"
        )

    resolved = []
    errors = []
    collection_errors = []
    total = 0
    collection_names = set()

    with csv_path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:

        reader = csv.DictReader(file)

        required = {"card", "set", "quantity"}
        fields = set(reader.fieldnames or [])

        if not required.issubset(fields):
            raise ValueError(
                "CSV precisa das colunas: card,set,quantity"
            )

        has_collection_name = "collection_name" in fields

        # Se a interface informou o nome, ele tem prioridade.
        if collection_name_override is not None:
            collection_name = collection_name_override.strip()

            if not collection_name:
                raise ValueError(
                    "Nome da coleção não pode ficar vazio."
                )

        else:
            # Validação do collection_name do CSV.
            for line, row in enumerate(reader, start=2):

                if has_collection_name:
                    name = (
                        row.get("collection_name") or ""
                    ).strip()

                    if not name:
                        collection_errors.append(
                            f"Linha {line}: collection_name vazio"
                        )
                        continue

                    collection_names.add(name)

                if len(collection_names) > 1:
                    message = (
                        "O CSV contém mais de um collection_name. "
                        "Todas as linhas devem usar o mesmo nome."
                    )

                    if message not in collection_errors:
                        collection_errors.append(message)

            if has_collection_name and not collection_names:
                collection_errors.append(
                    "Nenhum collection_name válido foi encontrado."
                )

            if collection_errors:
                print("\n========== ERRO DE VALIDAÇÃO ==========")

                for error in collection_errors:
                    print("ERRO:", error)

                raise ValueError(
                    "Processamento interrompido: "
                    "corrija o collection_name no CSV."
                )

            collection_name = (
                next(iter(collection_names))
                if has_collection_name
                else Path(filename).stem
            )

        # Carrega a biblioteca somente após validar a coleção.
        index = load_library()

        # Volta ao início do CSV para processar as cartas.
        file.seek(0)
        reader = csv.DictReader(file)

        for line, row in enumerate(reader, start=2):
            name = (row.get("card") or "").strip()
            set_code = (row.get("set") or "").strip().upper()

            try:
                quantity = int(row["quantity"])

                if quantity <= 0:
                    raise ValueError()

            except (ValueError, TypeError):
                errors.append(
                    f"Linha {line}: quantidade inválida"
                )
                continue

            if not name:
                errors.append(
                    f"Linha {line}: nome vazio"
                )
                continue

            matches = [
                card for card in index.get(name.casefold(), [])
                if card["set"].upper() == set_code
            ]

            if len(matches) == 0:
                errors.append(
                    f"Linha {line}: {name} ({set_code}) não encontrada"
                )
                continue

            if len(matches) > 1:
                errors.append(
                    f"Linha {line}: {name} ({set_code}) ambígua"
                )
                continue

            card = matches[0]

            resolved.append({
                "name": card["name"],
                "set": card["set"].upper(),
                "collector_number": card["collector_number"],
                "quantity": quantity,
                "image": card["image_path"],
                "id": card["id"]
            })

            total += quantity

    output = {
        "source": filename,
        "collection_name": collection_name,
        "total_cards": total,
        "total_sheets": math.ceil(total / 9),
        "cards": resolved,
        "errors": errors
    }

    output_path = JOBS / "resolved_job.json"

    output_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\n========== RESULTADO ==========")
    print(f"Coleção: {collection_name}")
    print(f"Cartas selecionadas: {len(resolved)}")
    print(f"Quantidade de cópias: {total}")
    print(f"Folhas A4 estimadas: {output['total_sheets']}")
    print(f"Problemas encontrados: {len(errors)}")

    for error in errors:
        print("ERRO:", error)

    print(f"\nArquivo gerado: {output_path}")


if __name__ == "__main__":
    scan_job("urza_test.csv")
