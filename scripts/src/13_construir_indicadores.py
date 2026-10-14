from __future__ import annotations

import csv
import math
from collections import defaultdict

from src.utils import ensure_project_dirs, load_config, normalize_label, project_path, write_csv


WID_VARIABLES = {
    "sptincj992": "pre_tax_income_share",
    "sptincj999": "pre_tax_income_share",
    "shwealj992": "net_personal_wealth_share",
    "shwealj999": "net_personal_wealth_share",
    "aptincj992": "pre_tax_income_average",
    "aptincj999": "pre_tax_income_average",
    "ahwealj992": "net_personal_wealth_average",
    "ahwealj999": "net_personal_wealth_average",
    "anninci992": "national_income_average",
    "anninci999": "national_income_average",
    "apweali992": "net_private_wealth_average",
    "apweali999": "net_private_wealth_average",
    "anweali992": "national_wealth_average",
    "anweali999": "national_wealth_average",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_wid(processed, tables) -> None:
    rows = read_csv(processed / "wid_selecao_2002_2026.csv")
    selected = [row for row in rows if row.get("variable") in WID_VARIABLES]
    selected_path = processed / "wid_indicadores_principais.csv"
    write_csv(selected_path, list(selected[0]) + ["indicator"], [{**row, "indicator": WID_VARIABLES[row["variable"]]} for row in selected])

    percentiles = {
        "p0p100": "total",
        "p0p50": "bottom_50",
        "p50p100": "top_50",
        "p90p100": "top_10",
        "p99p100": "top_1",
    }
    summary = {}
    for row in selected:
        indicator = WID_VARIABLES[row["variable"]]
        if indicator not in {"pre_tax_income_share", "net_personal_wealth_share"} or row.get("percentile") not in percentiles:
            continue
        try:
            value = float(row["value"])
        except ValueError:
            continue
        key = (row["year"], indicator, percentiles[row["percentile"]])
        summary[key] = value * 100
    summary_rows = [
        {"country": "BR", "year": int(year), "indicator": indicator, "population_group": group, "share_percent": value, "source": "WID"}
        for (year, indicator, group), value in sorted(summary.items())
    ]
    write_csv(tables / "wid_brasil_concentracao.csv", list(summary_rows[0]) if summary_rows else ["year"], summary_rows)


def build_ilostat(processed, tables) -> None:
    rows = read_csv(processed / "ilostat_remuneracao_harmonizada.csv")
    grouped = defaultdict(dict)
    for row in rows:
        if row.get("currency") != "Currency: 2021 PPP $":
            continue
        key = (normalize_label(row.get("country")), row.get("country"), row.get("year"))
        try:
            grouped[key][row.get("sex", "").casefold()] = float(row.get("value_numeric", ""))
        except ValueError:
            continue
    output = []
    for (_country_key, country, year), values in sorted(grouped.items()):
        if "male" not in values or "female" not in values or values["male"] <= 0:
            continue
        female, male = values["female"], values["male"]
        output.append({
            "country": country,
            "year": int(year),
            "female_mean_ppp2021": female,
            "male_mean_ppp2021": male,
            "female_to_male_ratio": female / male,
            "gender_pay_gap_percent": (1 - female / male) * 100,
            "source": "ILOSTAT",
        })
    write_csv(tables / "ilostat_gap_genero.csv", list(output[0]) if output else ["country"], output)


def build_findex(processed, tables) -> None:
    rows = read_csv(processed / "global_findex_selecionado.csv")
    indicators = [key for key in ["account.t.d", "borrow.any.t.d", "save.any.t.d", "dig.acc"] if rows and key in rows[0]]
    grouped = defaultdict(dict)
    for row in rows:
        if row.get("group") != "gender":
            continue
        key = (row.get("codewb"), row.get("countrynewwb"), row.get("year"))
        for indicator in indicators:
            try:
                grouped[key][(row.get("group2"), indicator)] = float(row.get(indicator, "")) * 100
            except ValueError:
                continue
    output = []
    for (code, country, year), values in sorted(grouped.items()):
        for indicator in indicators:
            women = values.get(("women", indicator))
            men = values.get(("men", indicator))
            if women is None or men is None:
                continue
            output.append({"country_code": code, "country": country, "year": int(year), "indicator": indicator, "women_percent": women, "men_percent": men, "women_minus_men_pp": women - men, "source": "Global Findex"})
    write_csv(tables / "findex_gap_genero.csv", list(output[0]) if output else ["country"], output)


def build_wiid_vdem(processed, tables, tests) -> None:
    wiid = read_csv(processed / "wiid_2002_2026.csv")
    vdem = read_csv(processed / "vdem_contexto_pais_ano.csv")
    grouped = defaultdict(list)
    for row in wiid:
        try:
            value = float(row.get("gini", ""))
            if not math.isfinite(value):
                continue
            grouped[(row.get("c3", ""), int(row["year"]))].append(value)
        except (ValueError, TypeError):
            continue
    wiid_summary = []
    for (code, year), values in sorted(grouped.items()):
        wiid_summary.append({"country_code": code, "year": year, "gini_mean_available_records": sum(values) / len(values), "gini_min": min(values), "gini_max": max(values), "gini_records": len(values), "source": "WIID"})
    write_csv(tables / "wiid_gini_pais_ano.csv", list(wiid_summary[0]) if wiid_summary else ["country_code"], wiid_summary)
    by_key = {(row["country_code"], int(row["year"])): row for row in wiid_summary}
    panel = []
    for row in vdem:
        item = dict(row)
        extra = by_key.get((row.get("country_text_id", ""), int(row.get("year", 0))))
        item.update(extra or {"gini_mean_available_records": "", "gini_min": "", "gini_max": "", "gini_records": ""})
        panel.append(item)
    write_csv(processed / "painel_analitico_pais_ano.csv", list(panel[0]) if panel else ["year"], panel)

    pairs = []
    values_x, values_y = [], []
    for row in panel:
        try:
            x = float(row.get("v2x_egaldem", ""))
            y = float(row.get("gini_mean_available_records", ""))
        except ValueError:
            continue
        values_x.append(x)
        values_y.append(y)
    if len(values_x) >= 3:
        mean_x, mean_y = sum(values_x) / len(values_x), sum(values_y) / len(values_y)
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(values_x, values_y))
        den_x = math.sqrt(sum((x - mean_x) ** 2 for x in values_x))
        den_y = math.sqrt(sum((y - mean_y) ** 2 for y in values_y))
        r = num / (den_x * den_y) if den_x and den_y else ""
        slope = num / sum((x - mean_x) ** 2 for x in values_x) if den_x else ""
        pairs.append({"x": "v2x_egaldem", "y": "gini_mean_available_records", "n": len(values_x), "pearson_r": r, "slope_y_on_x": slope, "interpretation": "associação descritiva; não causal"})
    write_csv(tests / "associacoes_exploratorias.csv", list(pairs[0]) if pairs else ["x"], pairs)


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    processed = project_path(config, "processed")
    tables = project_path(config, "tables")
    tests = project_path(config, "statistical_tests")
    build_wid(processed, tables)
    build_ilostat(processed, tables)
    build_findex(processed, tables)
    build_wiid_vdem(processed, tables, tests)
    print("Indicadores analíticos e associação exploratória gerados.")


if __name__ == "__main__":
    main()
