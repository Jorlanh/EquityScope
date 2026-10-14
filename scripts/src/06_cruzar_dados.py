from __future__ import annotations

import csv

from src.utils import ensure_project_dirs, load_config, normalize_label, project_path, write_csv


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    earnings_path = project_path(config, "processed") / "ilostat_remuneracao_harmonizada.csv"
    vdem_path = project_path(config, "processed") / "vdem_contexto_pais_ano.csv"
    output_path = project_path(config, "processed") / "painel_exploratorio_ilostat_vdem.csv"
    if not earnings_path.exists() or not vdem_path.exists():
        raise FileNotFoundError("Execute 04_harmonizar_indicadores.py e 05_classificar_contexto_politico.py primeiro.")

    with vdem_path.open(encoding="utf-8-sig", newline="") as handle:
        vdem_rows = list(csv.DictReader(handle))
    with earnings_path.open(encoding="utf-8-sig", newline="") as handle:
        earnings_rows = list(csv.DictReader(handle))

    earnings_by_key: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    for row in earnings_rows:
        key = (normalize_label(row.get("country")), row.get("year", ""), row.get("sex", ""), row.get("currency", ""))
        earnings_by_key.setdefault(key, []).append(row)

    output_rows = []
    for row in vdem_rows:
        country = row.get("country_name", "")
        year = row.get("year", "")
        matches = [
            item
            for (country_key, item_year, _sex, _currency), values in earnings_by_key.items()
            if country_key == normalize_label(country) and item_year == year
            for item in values
        ]
        if not matches:
            output_rows.append({**row, "ilostat_country": "", "ilostat_sex": "", "ilostat_currency": "", "ilostat_value": ""})
            continue
        for match in matches:
            output_rows.append({
                **row,
                "ilostat_country": match.get("country", ""),
                "ilostat_sex": match.get("sex", ""),
                "ilostat_currency": match.get("currency", ""),
                "ilostat_value": match.get("value_numeric", ""),
            })

    fields = list(output_rows[0]) if output_rows else ["country_name", "year"]
    write_csv(output_path, fields, output_rows)
    matched = sum(1 for row in output_rows if row.get("ilostat_country"))
    print(f"Painel exploratório: {len(output_rows)} linhas; {matched} com correspondência exata -> {output_path}")
    print("Correspondências aproximadas de nomes de países não foram forçadas.")


if __name__ == "__main__":
    main()
