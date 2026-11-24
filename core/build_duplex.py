import csv
import json
import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from scanner import scan_job
from layout import generate_layout
from pdf_front import generate_pdf as generate_front
from pdf_back import generate_pdf as generate_back


ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"
OUTPUT = ROOT / "output"

FRONT_TEMP = OUTPUT / "magic_front.pdf"
BACK_TEMP = OUTPUT / "magic_back.pdf"


def get_collection_name(csv_filename):
    csv_path = JOBS / csv_filename

    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if "collection_name" not in (reader.fieldnames or []):
            return Path(csv_filename).stem

        names = {
            (row.get("collection_name") or "").strip()
            for row in reader
            if (row.get("collection_name") or "").strip()
        }

    if not names:
        return Path(csv_filename).stem

    if len(names) > 1:
        raise ValueError(
            "O CSV contém mais de um collection_name. "
            "Todas as linhas devem usar o mesmo nome."
        )

    return names.pop()


def build_duplex(csv_filename, collection_name=None):
    OUTPUT.mkdir(exist_ok=True)

    if collection_name is not None:
        collection = collection_name.strip()

        if not collection:
            raise ValueError("Nome da coleção não pode ficar vazio.")
    else:
        collection = get_collection_name(csv_filename)

    collection = re.sub(r"[^a-zA-Z0-9_-]", "_", collection)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_file = OUTPUT / f"{collection}_{timestamp}_duplex.pdf"

    try:
        print("\n========== MAGIC PRINT MANAGER ==========")
        print(f"Coleção: {collection}")
        print(f"Data/hora: {timestamp}")

        print("\n[1/5] Processando lista de cartas...")

        scan_job(
            csv_filename,
            collection_name_override=collection
            if collection_name is not None else None
        )

        resolved_file = JOBS / "resolved_job.json"

        if not resolved_file.exists():
            raise RuntimeError("Scanner não gerou resolved_job.json.")

        job = json.loads(resolved_file.read_text(encoding="utf-8"))

        if job.get("errors"):
            raise RuntimeError(
                f"Existem {len(job['errors'])} erros no CSV."
            )

        if not job.get("cards"):
            raise RuntimeError("Nenhuma carta válida encontrada.")

        print("\n[2/5] Calculando distribuição...")
        generate_layout()

        print("\n[3/5] Gerando páginas frontais...")
        generate_front()

        if not FRONT_TEMP.exists():
            raise RuntimeError("PDF frontal não foi gerado.")

        print("\n[4/5] Gerando páginas traseiras...")
        generate_back()

        if not BACK_TEMP.exists():
            raise RuntimeError("PDF traseiro não foi gerado.")

        print("\n[5/5] Intercalando frente e verso...")

        front = PdfReader(str(FRONT_TEMP))
        back = PdfReader(str(BACK_TEMP))

        if len(front.pages) != len(back.pages):
            raise RuntimeError(
                "Quantidade de páginas diferente entre frente e verso."
            )

        writer = PdfWriter()

        for front_page, back_page in zip(front.pages, back.pages):
            writer.add_page(front_page)
            writer.add_page(back_page)

        with final_file.open("wb") as file:
            writer.write(file)

        total_sheets = len(front.pages)
        total_pages = len(writer.pages)

        print("\n========== CONCLUÍDO ==========")
        print(f"Coleção: {collection}")
        print(f"Cartas: {job['total_cards']}")
        print(f"Folhas físicas: {total_sheets}")
        print(f"Páginas duplex: {total_pages}")
        print(f"\nPDF GERADO: {final_file}")

        return {
            "collection": collection,
            "total_cards": job["total_cards"],
            "total_sheets": total_sheets,
            "total_pages": total_pages,
            "duplex_file": final_file
        }

    finally:
        FRONT_TEMP.unlink(missing_ok=True)
        BACK_TEMP.unlink(missing_ok=True)


if __name__ == "__main__":
    build_duplex("test_lands.csv")