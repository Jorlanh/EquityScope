from __future__ import annotations

import csv

from src.utils import ensure_project_dirs, load_config, project_path


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    input_path = project_path(config, "processed") / "ilostat_remuneracao_harmonizada.csv"
    figure_path = project_path(config, "figures") / "ilostat_remuneracao_brasil.png"
    if not input_path.exists():
        print("Sem dados harmonizados; gráfico não gerado.")
        return
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado; gráfico não gerado.")
        return

    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("country") == "Brazil" and row.get("is_ppp_2021") == "True"]
    values: dict[str, list[tuple[int, float]]] = {}
    for row in rows:
        try:
            values.setdefault(row["sex"], []).append((int(row["year"]), float(row["value_numeric"])))
        except (KeyError, TypeError, ValueError):
            continue
    if not values:
        print("Não há observações brasileiras PPP 2021 para gerar o gráfico.")
        return
    for sex, points in sorted(values.items()):
        points.sort()
        plt.plot([year for year, _ in points], [value for _, value in points], marker="o", label=sex)
    plt.title("Brasil: remuneração média por sexo, ILOSTAT")
    plt.xlabel("Ano")
    plt.ylabel("Dólares PPP de 2021")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_path, dpi=160)
    plt.close()
    print(f"Figura gerada: {figure_path}")


if __name__ == "__main__":
    main()
