from __future__ import annotations

import csv
import io
import zipfile

from src.utils import ensure_project_dirs, find_outer_entry, load_config, project_path, project_period, source_zip, write_csv


BASE_COLUMNS = ["country_name", "country_text_id", "country_id", "year", "historical_date"]
CANDIDATE_COLUMNS = [
    "v2x_polyarchy",
    "v2x_libdem",
    "v2x_partipdem",
    "v2x_delibdem",
    "v2x_egaldem",
    "v2x_freexp_altinf",
    "v2x_frassoc_thick",
    "v2x_suffr",
    "v2x_elecoff",
    "v2x_gender",
    "v2xeg_eqdr",
    "v2xeg_eqprotec",
    "v2xeg_eqaccess",
]


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    start, end = project_period(config)
    selected_path = project_path(config, "processed") / "vdem_contexto_pais_ano.csv"

    with zipfile.ZipFile(source_zip(config)) as outer:
        outer_entry = find_outer_entry(outer, "V-Dem-CY-FullOthers-v16_csv.zip")
        if outer_entry is None:
            outer_entry = find_outer_entry(outer, "V-Dem-CY-Full+Others-v16_csv.zip")
        if outer_entry is None:
            raise FileNotFoundError("Arquivo V-Dem Full + Others não encontrado no ZIP bruto.")
        with outer.open(outer_entry) as nested_stream:
            with zipfile.ZipFile(nested_stream) as nested:
                csv_name = next(name for name in nested.namelist() if name.lower().endswith(".csv"))
                with nested.open(csv_name) as raw:
                    text = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
                    reader = csv.DictReader(text)
                    available = reader.fieldnames or []
                    columns = [name for name in BASE_COLUMNS + CANDIDATE_COLUMNS if name in available]
                    if "year" not in columns:
                        raise ValueError("V-Dem não possui coluna year.")
                    rows = []
                    for row in reader:
                        try:
                            year = int(row.get("year", ""))
                        except ValueError:
                            continue
                        if start <= year <= end:
                            rows.append({column: row.get(column, "") for column in columns})

    write_csv(selected_path, columns, rows)
    print(f"V-Dem selecionado: {len(rows)} linhas, {len(columns)} colunas -> {selected_path}")
    print("Atenção: este arquivo é contexto institucional; não é classificação automática de ideologia.")


if __name__ == "__main__":
    main()
