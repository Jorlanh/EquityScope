from __future__ import annotations

import csv

from src.utils import ensure_project_dirs, load_config, normalize_label, project_path, write_csv


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    input_path = project_path(config, "processed") / "ilostat_remuneracao_por_sexo.csv"
    output_path = project_path(config, "processed") / "ilostat_remuneracao_harmonizada.csv"
    if not input_path.exists():
        raise FileNotFoundError("Execute primeiro 03_limpar_dados.py")

    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    harmonized = []
    for row in rows:
        item = dict(row)
        item["country_key"] = normalize_label(row.get("country"))
        item["year"] = int(row["year"])
        try:
            item["value_numeric"] = float(row["value"])
        except (TypeError, ValueError):
            item["value_numeric"] = ""
        item["is_ppp_2021"] = "2021 PPP" in row.get("currency", "")
        harmonized.append(item)

    fields = list(harmonized[0]) if harmonized else ["country_key"]
    write_csv(output_path, fields, harmonized)
    print(f"Indicadores harmonizados: {len(harmonized)} linhas -> {output_path}")


if __name__ == "__main__":
    main()
