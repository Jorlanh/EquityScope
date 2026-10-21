from __future__ import annotations

import csv
import re
import zipfile

from src.utils import ensure_project_dirs, load_config, project_path, source_zip, write_csv


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    output = project_path(config, "metadata") / "pnad_microdados.csv"
    rows = []
    with zipfile.ZipFile(source_zip(config)) as outer:
        for info in outer.infolist():
            name = info.filename.replace("\\", "/")
            if "PNAD Contínua" not in name or not name.lower().endswith(".zip"):
                continue
            match = re.search(r"PNADC_(\d{2})(\d{4})", name, flags=re.IGNORECASE)
            if not match:
                continue
            quarter = int(match.group(1))
            year = int(match.group(2))
            rows.append({
                "arquivo": name,
                "ano": year,
                "trimestre": quarter,
                "periodo": f"{year}-T{quarter}",
                "tamanho_bytes": info.file_size,
                "tamanho_comprimido_bytes": info.compress_size,
                "incluido_no_recorte": 2012 <= year <= 2026,
                "observacao": "Microdado bruto; exige input, dicionário, pesos e desenho amostral.",
            })
    rows.sort(key=lambda row: (row["ano"], row["trimestre"]))
    write_csv(output, list(rows[0]) if rows else ["arquivo"], rows)
    print(f"Catálogo PNAD: {len(rows)} arquivos -> {output}")


if __name__ == "__main__":
    main()
