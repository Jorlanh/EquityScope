from __future__ import annotations

import csv
import re
import zipfile
from collections import Counter
from pathlib import Path

from src.utils import ensure_project_dirs, load_config, project_path, source_zip, write_csv


def source_category(name: str) -> str:
    lower = name.casefold()
    if "wid world" in lower:
        return "WID"
    if "wiid" in lower:
        return "WIID"
    if "ilostat" in lower:
        return "ILOSTAT"
    if "pnad" in lower or "dicionario_e_input" in lower:
        return "PNAD_CONTINUA"
    if "findex" in lower:
        return "GLOBAL_FINDEX"
    if "v-dem" in lower or "vdem" in lower:
        return "VDEM"
    return "OUTROS"


def pnad_periods(names: list[str]) -> list[str]:
    periods: set[str] = set()
    for name in names:
        match = re.search(r"PNADC_(\d{2})(\d{4})", name, flags=re.IGNORECASE)
        if match:
            periods.add(f"{match.group(2)}-T{int(match.group(1))}")
    return sorted(periods)


def csv_time_range(zip_file: zipfile.ZipFile, info: zipfile.ZipInfo) -> tuple[int | None, int | None, int]:
    years: list[int] = []
    rows = 0
    with zip_file.open(info) as stream:
        text = stream.read().decode("utf-8-sig", errors="replace")
    for row in csv.DictReader(text.splitlines()):
        rows += 1
        value = row.get("time", "")
        if re.fullmatch(r"\d{4}", value or ""):
            years.append(int(value))
    return (min(years) if years else None, max(years) if years else None, rows)


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    raw_zip = source_zip(config)
    if not raw_zip.exists():
        raise FileNotFoundError(f"ZIP bruto não encontrado: {raw_zip}")

    inventory_path = project_path(config, "metadata") / "inventario_arquivos.csv"
    coverage_path = project_path(config, "metadata") / "cobertura_fontes.csv"
    outer_names: list[str] = []
    rows: list[dict[str, object]] = []
    csv_coverage: dict[str, tuple[int | None, int | None, int]] = {}

    with zipfile.ZipFile(raw_zip) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            outer_names.append(name)
            rows.append({
                "arquivo": name,
                "fonte": source_category(name),
                "extensao": Path(name).suffix.casefold(),
                "tamanho_bytes": info.file_size,
                "tamanho_comprimido_bytes": info.compress_size,
                "arquivo_aninhado": Path(name).suffix.casefold() == ".zip",
            })
            if Path(name).suffix.casefold() == ".csv":
                csv_coverage[name] = csv_time_range(archive, info)

    fields = ["arquivo", "fonte", "extensao", "tamanho_bytes", "tamanho_comprimido_bytes", "arquivo_aninhado"]
    count = write_csv(inventory_path, fields, rows)

    pnad = pnad_periods(outer_names)
    ear = next((value for name, value in csv_coverage.items() if "EAR_EMTA" in name), (None, None, 0))
    lap = next((value for name, value in csv_coverage.items() if "LAP_2FTM" in name), (None, None, 0))
    coverage_rows = [
        {"fonte": "WID", "periodo_observado": "consultar variáveis e metadados por país", "arquivo_principal": "wid_all_data.zip", "observacoes": "Arquivo aninhado grande; filtrar variáveis antes de carregar."},
        {"fonte": "WIID", "periodo_observado": "consultar coluna year", "arquivo_principal": "WIID-08SEP2026.xlsx", "observacoes": "Manter wiidglobal_6.xlsx como versão de comparação, sem concatenar."},
        {"fonte": "ILOSTAT", "periodo_observado": f"{ear[0]}–{ear[1]} ({ear[2]} linhas)" if ear[0] else "não identificado", "arquivo_principal": "EAR_EMTA_SEX_CUR_NB_A-20261013T2257.csv", "observacoes": "Remuneração por sexo; cobertura anual irregular."},
        {"fonte": "ILOSTAT_MODELADO", "periodo_observado": f"{lap[0]}–{lap[1]} ({lap[2]} linhas)" if lap[0] else "não identificado", "arquivo_principal": "LAP_2FTM_NOC_RT_A-20261013T2256.csv", "observacoes": "Somente 2026 no pacote."},
        {"fonte": "PNAD_CONTINUA", "periodo_observado": "; ".join(pnad), "arquivo_principal": "arquivos PNADC trimestrais", "observacoes": "2026-T1 e 2026-T2 estão incluídos; não são semestres completos."},
        {"fonte": "GLOBAL_FINDEX", "periodo_observado": "ondas de pesquisa; consultar coluna Year", "arquivo_principal": "GlobalFindexDatabase2025.xlsx", "observacoes": "A edição contém referência de 2024; não é painel anual."},
        {"fonte": "VDEM", "periodo_observado": "país-ano; filtrar 2002–2026", "arquivo_principal": "V-Dem-CY-Full+Others-v16.csv", "observacoes": "Preservar codebook e notas."},
    ]
    write_csv(coverage_path, list(coverage_rows[0]), coverage_rows)
    counts = Counter(row["fonte"] for row in rows)
    print(f"Inventário concluído: {count} arquivos -> {inventory_path}")
    for name, value in sorted(counts.items()):
        print(f"  {name}: {value}")
    print(f"Cobertura registrada em: {coverage_path}")


if __name__ == "__main__":
    main()
