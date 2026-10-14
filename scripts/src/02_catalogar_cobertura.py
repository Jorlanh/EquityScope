from __future__ import annotations

import csv
from collections import defaultdict

from src.utils import ensure_project_dirs, load_config, project_path


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    inventory = project_path(config, "metadata") / "inventario_arquivos.csv"
    if not inventory.exists():
        raise FileNotFoundError("Execute primeiro 01_inspecionar_bases.py")

    counts: dict[tuple[str, str], int] = defaultdict(int)
    with inventory.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            counts[(row["fonte"], row["extensao"])] += 1

    output = project_path(config, "metadata") / "catalogo_cobertura.csv"
    rows = [{"fonte": source, "extensao": extension, "quantidade_arquivos": count} for (source, extension), count in sorted(counts.items())]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["fonte", "extensao", "quantidade_arquivos"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Catálogo de cobertura concluído: {output}")


if __name__ == "__main__":
    main()
