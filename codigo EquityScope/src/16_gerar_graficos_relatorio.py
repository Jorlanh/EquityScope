from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import ensure_project_dirs, load_config, project_path


PAISES = {
    "BRA": "Brasil",
    "CHN": "China",
    "USA": "Estados Unidos",
    "DEU": "Alemanha",
    "FRA": "França",
    "IND": "Índia",
}


def _matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    plt.rcParams.update(
        {
            "figure.figsize": (10, 5.5),
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "font.size": 10,
        }
    )
    return plt


def _save(plt, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Figura gerada: {path}")


def grafico_gini_paises(plt, tables: Path, figures: Path) -> None:
    path = tables / "wiid_gini_pais_ano.csv"
    if not path.exists():
        return
    data = pd.read_csv(path)
    data = data[data["country_code"].isin(PAISES)].copy()
    if data.empty:
        return
    for code, frame in data.groupby("country_code"):
        frame = frame.sort_values("year")
        plt.plot(
            frame["year"],
            frame["gini_mean_available_records"],
            marker="o",
            markersize=3,
            linewidth=1.6,
            label=PAISES.get(code, code),
        )
    plt.title("Desigualdade de renda: comparação entre países")
    plt.xlabel("Ano")
    plt.ylabel("Índice de Gini (pontos)")
    plt.grid(alpha=0.25)
    plt.legend(ncol=3)
    _save(plt, figures / "01_gini_comparacao_paises.png")


def grafico_renda_genero(plt, tables: Path, figures: Path) -> None:
    path = tables / "ilostat_gap_genero.csv"
    if not path.exists():
        return
    data = pd.read_csv(path)
    wanted = ["Brazil", "China", "United States", "Germany", "France", "India"]
    data = data[data["country"].isin(wanted)].copy()
    if data.empty:
        return
    for country, frame in data.groupby("country"):
        frame = frame.sort_values("year")
        plt.plot(
            frame["year"],
            frame["gender_pay_gap_percent"],
            marker="o",
            markersize=3,
            linewidth=1.5,
            label=country,
        )
    plt.title("Diferença estimada de remuneração entre mulheres e homens")
    plt.xlabel("Ano")
    plt.ylabel("Hiato (%)")
    plt.grid(alpha=0.25)
    plt.legend(ncol=2)
    _save(plt, figures / "02_hiato_genero_comparacao_paises.png")


def grafico_pnad_genero_raca(plt, processed: Path, figures: Path) -> None:
    path = processed / "pnad_rendimento_sexo_raca.csv"
    if not path.exists():
        return
    data = pd.read_csv(path)
    data = data[data["sex"].isin(["homens", "mulheres"])].copy()
    data = data[data["race"] != "todos"].copy()
    if data.empty:
        return
    latest = data[["year", "quarter"]].drop_duplicates().sort_values(["year", "quarter"]).iloc[-1]
    data = data[(data["year"] == latest["year"]) & (data["quarter"] == latest["quarter"])].copy()
    data["grupo"] = data["sex"].map({"homens": "Homens", "mulheres": "Mulheres"}) + " - " + data["race"].str.capitalize()
    data = data.sort_values("mean_monthly_work_income_nominal")
    plt.barh(data["grupo"], data["mean_monthly_work_income_nominal"], color="#35608f")
    plt.title(f"Brasil: rendimento mensal por sexo e cor/raça ({int(latest['year'])}-T{int(latest['quarter'])})")
    plt.xlabel("Rendimento nominal médio")
    plt.ylabel("")
    plt.grid(axis="x", alpha=0.25)
    _save(plt, figures / "03_brasil_genero_raca_pnad.png")


def grafico_inclusao_financeira(plt, tables: Path, figures: Path) -> None:
    path = tables / "findex_gap_genero.csv"
    if not path.exists():
        return
    data = pd.read_csv(path)
    data = data[data["indicator"] == "account.t.d"].copy()
    data = data[data["country_code"].isin(PAISES)].copy()
    if data.empty:
        return
    latest_year = data["year"].max()
    data = data[data["year"] == latest_year].copy()
    data["label"] = data["country"].replace({"United States": "Estados Unidos"})
    data = data.sort_values("women_minus_men_pp")
    colors = ["#b54a4a" if value < 0 else "#357a5b" for value in data["women_minus_men_pp"]]
    plt.barh(data["label"], data["women_minus_men_pp"], color=colors)
    plt.axvline(0, color="#333333", linewidth=0.8)
    plt.title(f"Acesso a conta: diferença entre mulheres e homens ({int(latest_year)})")
    plt.xlabel("Mulheres menos homens (pontos percentuais)")
    plt.ylabel("")
    plt.grid(axis="x", alpha=0.25)
    _save(plt, figures / "04_inclusao_financeira_genero.png")


def grafico_regioes(plt, processed: Path, tables: Path, figures: Path) -> None:
    gini_path = tables / "wiid_gini_pais_ano.csv"
    groups_path = processed / "country_group_membership.csv"
    if not gini_path.exists() or not groups_path.exists():
        return
    gini = pd.read_csv(gini_path)
    groups = pd.read_csv(groups_path)
    groups = groups[groups["group_type"] == "un_region"][["country_code", "group_name"]].drop_duplicates()
    merged = gini.merge(groups, on="country_code", how="inner")
    if merged.empty:
        return
    latest_year = merged["year"].max()
    data = merged[merged["year"] == latest_year].groupby("group_name", as_index=False)["gini_mean_available_records"].mean()
    data = data.sort_values("gini_mean_available_records")
    plt.barh(data["group_name"], data["gini_mean_available_records"], color="#5c6f82")
    plt.title(f"Desigualdade média por região ({int(latest_year)})")
    plt.xlabel("Gini médio dos países disponíveis")
    plt.ylabel("")
    plt.grid(axis="x", alpha=0.25)
    _save(plt, figures / "05_gini_medio_por_regiao.png")


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    plt = _matplotlib()
    if plt is None:
        print("matplotlib não instalado; gráficos estáticos não foram gerados.")
        return
    processed = project_path(config, "processed")
    tables = project_path(config, "tables")
    figures = project_path(config, "figures")
    grafico_gini_paises(plt, tables, figures)
    grafico_renda_genero(plt, tables, figures)
    grafico_pnad_genero_raca(plt, processed, figures)
    grafico_inclusao_financeira(plt, tables, figures)
    grafico_regioes(plt, processed, tables, figures)


if __name__ == "__main__":
    main()
