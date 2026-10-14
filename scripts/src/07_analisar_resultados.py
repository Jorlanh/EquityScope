from __future__ import annotations

import csv
from collections import Counter

from src.utils import ensure_project_dirs, load_config, project_path, write_csv


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    processed = project_path(config, "processed")
    tables = project_path(config, "tables")
    rows = []

    earnings = processed / "ilostat_remuneracao_harmonizada.csv"
    if earnings.exists():
        with earnings.open(encoding="utf-8-sig", newline="") as handle:
            data = list(csv.DictReader(handle))
        by_year = Counter(row.get("year", "") for row in data)
        rows.extend({"fonte": "ILOSTAT", "dimensao": "ano", "categoria": year, "observacoes": count} for year, count in sorted(by_year.items()))
        by_sex = Counter(row.get("sex", "") for row in data)
        rows.extend({"fonte": "ILOSTAT", "dimensao": "sexo", "categoria": sex, "observacoes": count} for sex, count in sorted(by_sex.items()))

    vdem = processed / "vdem_contexto_pais_ano.csv"
    if vdem.exists():
        with vdem.open(encoding="utf-8-sig", newline="") as handle:
            data = list(csv.DictReader(handle))
        by_year = Counter(row.get("year", "") for row in data)
        rows.extend({"fonte": "VDEM", "dimensao": "ano", "categoria": year, "observacoes": count} for year, count in sorted(by_year.items()))

    for filename, source in [
        ("wid_selecao_2002_2026.csv", "WID"),
        ("wiid_2002_2026.csv", "WIID"),
        ("global_findex_selecionado.csv", "GLOBAL_FINDEX"),
    ]:
        path = processed / filename
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            data = list(csv.DictReader(handle))
        rows.append({"fonte": source, "dimensao": "linhas", "categoria": "total", "observacoes": len(data)})
        by_year = Counter(row.get("year", "") for row in data)
        rows.extend({"fonte": source, "dimensao": "ano", "categoria": year, "observacoes": count} for year, count in sorted(by_year.items()) if year)

    pnad_catalog = project_path(config, "metadata") / "pnad_microdados.csv"
    if pnad_catalog.exists():
        with pnad_catalog.open(encoding="utf-8-sig", newline="") as handle:
            data = list(csv.DictReader(handle))
        rows.append({"fonte": "PNAD_CONTINUA", "dimensao": "arquivos_microdados", "categoria": "total", "observacoes": len(data)})
        by_period = Counter(row.get("periodo", "") for row in data)
        rows.extend({"fonte": "PNAD_CONTINUA", "dimensao": "periodo", "categoria": period, "observacoes": count} for period, count in sorted(by_period.items()))

    output = tables / "cobertura_processada.csv"
    write_csv(output, ["fonte", "dimensao", "categoria", "observacoes"], rows)
    print(f"Tabela de cobertura analítica: {len(rows)} linhas -> {output}")


if __name__ == "__main__":
    main()
