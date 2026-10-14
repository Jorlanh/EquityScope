from __future__ import annotations

import csv
import html
from pathlib import Path

from src.utils import ensure_project_dirs, load_config, project_path


PAISES = {
    "BRA": "Brasil",
    "CHN": "China",
    "USA": "Estados Unidos",
    "DEU": "Alemanha",
    "FRA": "França",
    "IND": "Índia",
}


def ler_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def numero(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "", "NA", "NaN") else None
    except ValueError:
        return None


def texto(value: object) -> str:
    return html.escape(str(value))


def cabecalho(title: str, subtitle: str = "") -> list[str]:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620" viewBox="0 0 1100 620">',
        '<rect width="1100" height="620" fill="#fbfaf7"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#263238} .muted{fill:#607d8b;font-size:13px} .grid{stroke:#d9e0e3;stroke-width:1} .axis{stroke:#607d8b;stroke-width:1.2} .title{font-size:22px;font-weight:700} .label{font-size:13px} .legend{font-size:13px}</style>',
        f'<text x="70" y="48" class="title">{texto(title)}</text>',
    ]
    if subtitle:
        parts.append(f'<text x="70" y="72" class="muted">{texto(subtitle)}</text>')
    return parts


def escala(values: list[float], low: float | None = None, high: float | None = None) -> tuple[float, float]:
    low = min(values) if low is None else low
    high = max(values) if high is None else high
    if low == high:
        low -= 1
        high += 1
    margin = (high - low) * 0.08
    return low - margin, high + margin


def linha_svg(path: Path, title: str, subtitle: str, series: dict[str, list[tuple[int, float]]], y_label: str) -> None:
    width, height = 1100, 620
    left, right, top, bottom = 82, 1030, 112, 520
    points = [value for values in series.values() for _, value in values]
    if not points:
        return
    y_min, y_max = escala(points)
    x_values = [year for values in series.values() for year, _ in values]
    x_min, x_max = min(x_values), max(x_values)
    if x_min == x_max:
        x_max += 1
    colors = ["#1d5d8f", "#b24a4a", "#367a58", "#8a5b2b", "#704d91", "#536878"]
    out = cabecalho(title, subtitle)
    for step in range(6):
        value = y_min + ((y_max - y_min) * step / 5)
        y = bottom - ((value - y_min) / (y_max - y_min)) * (bottom - top)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" class="label">{value:.1f}</text>')
    out.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>')
    out.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>')
    for year in sorted(set(x_values)):
        x = left + ((year - x_min) / (x_max - x_min)) * (right - left)
        out.append(f'<text x="{x:.1f}" y="{bottom + 25}" text-anchor="middle" class="label">{year}</text>')
    out.append(f'<text x="20" y="{(top + bottom) / 2:.1f}" transform="rotate(-90 20 {(top + bottom) / 2:.1f})" class="muted">{texto(y_label)}</text>')
    for index, (label, values) in enumerate(series.items()):
        color = colors[index % len(colors)]
        values = sorted(values)
        coords = []
        for year, value in values:
            x = left + ((year - x_min) / (x_max - x_min)) * (right - left)
            y = bottom - ((value - y_min) / (y_max - y_min)) * (bottom - top)
            coords.append((x, y))
        if len(coords) >= 2:
            path_data = " ".join(("M" if n == 0 else "L") + f"{x:.1f},{y:.1f}" for n, (x, y) in enumerate(coords))
            out.append(f'<path d="{path_data}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for x, y in coords:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>')
        legend_x = left + (index % 3) * 300
        legend_y = 570 + (index // 3) * 20
        out.append(f'<line x1="{legend_x}" y1="{legend_y - 4}" x2="{legend_x + 22}" y2="{legend_y - 4}" stroke="{color}" stroke-width="3"/>')
        out.append(f'<text x="{legend_x + 30}" y="{legend_y}" class="legend">{texto(label)}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Figura SVG gerada: {path}")


def barras_svg(path: Path, title: str, subtitle: str, values: list[tuple[str, float]], x_label: str, colors: list[str] | None = None) -> None:
    if not values:
        return
    left, right, top, bottom = 270, 1030, 112, 535
    low, high = escala([value for _, value in values], 0 if min(value for _, value in values) >= 0 else None)
    out = cabecalho(title, subtitle)
    for step in range(6):
        value = low + ((high - low) * step / 5)
        x = left + ((value - low) / (high - low)) * (right - left)
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" class="grid"/>')
        out.append(f'<text x="{x:.1f}" y="{bottom + 25}" text-anchor="middle" class="label">{value:.1f}</text>')
    row = (bottom - top) / len(values)
    for index, (label, value) in enumerate(values):
        y = top + index * row + row * 0.2
        height = row * 0.58
        x = left + ((min(value, 0) - low) / (high - low)) * (right - left)
        end = left + ((value - low) / (high - low)) * (right - left)
        color = colors[index % len(colors)] if colors else "#35608f"
        out.append(f'<text x="{left - 12}" y="{y + height * 0.7:.1f}" text-anchor="end" class="label">{texto(label)}</text>')
        out.append(f'<rect x="{min(x, end):.1f}" y="{y:.1f}" width="{abs(end - x):.1f}" height="{height:.1f}" fill="{color}" rx="3"/>')
    out.append(f'<text x="{(left + right) / 2:.1f}" y="{bottom + 55}" text-anchor="middle" class="muted">{texto(x_label)}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Figura SVG gerada: {path}")


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    processed = project_path(config, "processed")
    tables = project_path(config, "tables")
    figures = project_path(config, "figures")
    figures.mkdir(parents=True, exist_ok=True)

    path = tables / "wiid_gini_pais_ano.csv"
    if path.exists():
        rows = ler_csv(path)
        series: dict[str, list[tuple[int, float]]] = {}
        for row in rows:
            if row.get("country_code") in PAISES:
                year, value = numero(row.get("year")), numero(row.get("gini_mean_available_records"))
                if year is not None and value is not None:
                    series.setdefault(PAISES[row["country_code"]], []).append((int(year), value))
        linha_svg(figures / "01_gini_comparacao_paises.svg", "Desigualdade de renda: comparação entre países", "WIID, média dos registros disponíveis por país-ano", series, "Índice de Gini (pontos)")

    path = tables / "ilostat_gap_genero.csv"
    if path.exists():
        rows = ler_csv(path)
        series = {}
        for row in rows:
            if row.get("country") in {"Brazil", "China", "United States", "Germany", "France", "India"}:
                year, value = numero(row.get("year")), numero(row.get("gender_pay_gap_percent"))
                if year is not None and value is not None:
                    series.setdefault(row["country"], []).append((int(year), value))
        linha_svg(figures / "02_hiato_genero_comparacao_paises.svg", "Diferença estimada de remuneração", "ILOSTAT; países com observações disponíveis", series, "Hiato percentual")

    path = processed / "pnad_rendimento_sexo_raca.csv"
    if path.exists():
        rows = ler_csv(path)
        rows = [row for row in rows if row.get("sex") in {"homens", "mulheres"} and row.get("race") != "todos"]
        periods = sorted({(numero(row.get("year")), numero(row.get("quarter"))) for row in rows if numero(row.get("year")) is not None and numero(row.get("quarter")) is not None})
        if periods:
            year, quarter = periods[-1]
            rows = [row for row in rows if numero(row.get("year")) == year and numero(row.get("quarter")) == quarter]
            values = []
            for row in rows:
                value = numero(row.get("mean_monthly_work_income_nominal"))
                if value is not None:
                    label = f"{row['sex'].capitalize()} - {row['race'].capitalize()}"
                    values.append((label, value))
            values.sort(key=lambda item: item[1])
            barras_svg(figures / "03_brasil_genero_raca_pnad.svg", "Brasil: rendimento por sexo e cor ou raça", f"PNAD Contínua; {int(year)}-T{int(quarter)}; valores nominais", values, "Rendimento mensal nominal médio")

    path = tables / "findex_gap_genero.csv"
    if path.exists():
        rows = [row for row in ler_csv(path) if row.get("indicator") == "account.t.d" and row.get("country_code") in PAISES]
        years = [numero(row.get("year")) for row in rows if numero(row.get("year")) is not None]
        if years:
            latest = max(years)
            values = []
            for row in rows:
                if numero(row.get("year")) == latest and numero(row.get("women_minus_men_pp")) is not None:
                    values.append((PAISES.get(row.get("country_code", ""), row.get("country", "")), numero(row["women_minus_men_pp"])))
            values.sort(key=lambda item: item[1])
            colors = ["#b54a4a" if value < 0 else "#367a58" for _, value in values]
            barras_svg(figures / "04_inclusao_financeira_genero.svg", "Acesso a contas por gênero", f"Global Findex; mulheres menos homens; onda de {int(latest)}", values, "Diferença em pontos percentuais", colors)

    gini_path = tables / "wiid_gini_pais_ano.csv"
    groups_path = processed / "country_group_membership.csv"
    if gini_path.exists() and groups_path.exists():
        gini = ler_csv(gini_path)
        groups = {row["country_code"]: row["group_name"] for row in ler_csv(groups_path) if row.get("group_type") == "un_region"}
        years = [numero(row.get("year")) for row in gini if numero(row.get("year")) is not None]
        if years:
            latest = max(years)
            grouped: dict[str, list[float]] = {}
            for row in gini:
                if numero(row.get("year")) == latest and row.get("country_code") in groups and numero(row.get("gini_mean_available_records")) is not None:
                    grouped.setdefault(groups[row["country_code"]], []).append(numero(row["gini_mean_available_records"]))
            values = sorted((label, sum(items) / len(items)) for label, items in grouped.items())
            barras_svg(figures / "05_gini_medio_por_regiao.svg", "Desigualdade média por região", f"WIID; países disponíveis na onda de {int(latest)}", values, "Gini médio")


if __name__ == "__main__":
    main()
