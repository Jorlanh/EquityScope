from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STEPS = [
    "src/01_inspecionar_bases.py",
    "src/02_catalogar_cobertura.py",
    "src/03_limpar_dados.py",
    "src/04_harmonizar_indicadores.py",
    "src/05_classificar_contexto_politico.py",
    "src/09_processar_wid.py",
    "src/10_processar_wiid_findex.py",
    "src/15_preparar_grupos_comparacao.py",
    "src/11_catalogar_pnad.py",
    "src/12_processar_pnad.py",
    "src/13_construir_indicadores.py",
    "src/06_cruzar_dados.py",
    "src/07_analisar_resultados.py",
    "src/08_gerar_graficos.py",
    "src/16_gerar_graficos_relatorio.py",
    "src/17_gerar_graficos_svg.py",
]


def main() -> None:
    for relative in STEPS:
        path = ROOT / relative
        print(f"\n-> {relative}")
        runpy.run_path(str(path), run_name="__main__")
    print("\nConcluído.")


if __name__ == "__main__":
    main()
