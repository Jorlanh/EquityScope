# Análise e execução

## Indicadores produzidos

O projeto gera os seguintes arquivos com os dados tratados:

- `data/processed/pnad_rendimento_sexo_raca.csv`: médias de rendimento da PNAD por trimestre, sexo, cor ou raça e cruzamento entre sexo e raça.
- `outputs/tables/wid_brasil_concentracao.csv`: dados sobre a distribuição de renda e patrimônio no Brasil.
- `outputs/tables/ilostat_gap_genero.csv`: comparação entre os rendimentos de mulheres e homens, em dólares PPP de 2021.
- `outputs/tables/findex_gap_genero.csv`: diferença entre mulheres e homens no acesso a serviços financeiros, em pontos percentuais.
- `outputs/tables/wiid_gini_pais_ano.csv`: dados do índice de Gini por país e ano.
- `data/processed/painel_analitico_pais_ano.csv`: dados do V-Dem e do WIID organizados por país e ano.
- `outputs/statistical_tests/associacoes_exploratorias.csv`: resultados de correlações e inclinações para analisar possíveis relações entre os indicadores. Esses resultados não comprovam relações de causa e efeito.

## Como interpretar os resultados

O projeto reúne dados para comparar países e períodos. Ele não faz previsões financeiras.

Para trabalhar com projeções futuras, será necessário desenvolver um modelo separado, testar seu desempenho com dados de períodos anteriores e considerar as incertezas dos resultados.

O WID não permite analisar diferenças de gênero ou de cor ou raça quando esses dados não estão disponíveis separadamente. Por isso, o cruzamento entre sexo e cor ou raça é feito com os dados da PNAD brasileira. Nas comparações internacionais, usamos as fontes que possuem indicadores compatíveis.

## Correção dos rendimentos da PNAD

Os valores da PNAD ainda estão em valores nominais, sem correção da inflação. Por isso, é necessário aplicar o deflator oficial antes de comparar os rendimentos de anos diferentes.

O campo `deflator_applied=False` indica que essa correção ainda não foi aplicada. Assim, os valores não devem ser tratados como rendimentos reais.

## Como executar o projeto

Para instalar as bibliotecas e processar os dados, execute os comandos abaixo:

```powershell
python -m pip install -r requirements.txt
python run_pipeline.py
```

O caminho dos arquivos originais é definido no `config.yaml`. Os arquivos brutos não são incluídos no pacote do projeto por causa do tamanho.