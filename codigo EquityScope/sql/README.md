# Camada PostgreSQL da Aiven Free

Este diretório contém o banco online compacto do projeto. Ele não recebe o ZIP bruto nem os microdados completos.

## Ordem de execução no Aiven

### Via psql ou DBeaver

1. Execute `aiven_postgresql_completo.sql` no PostgreSQL da Aiven para criar tabelas, índices, views e consultas de monitoramento em uma única execução.
2. Gere ou atualize `data/processed/country_group_membership.csv` com `python src/15_preparar_grupos_comparacao.py`.
3. Carregue os CSVs processados com `python src/14_carregar_aiven.py --replace`.
4. Execute `003_monitoramento_aiven.sql` periodicamente para acompanhar o volume, caso queira repetir apenas o monitoramento.

O arquivo completo é a combinação de `001_schema_aiven.sql`, `002_views_aiven.sql` e `003_monitoramento_aiven.sql`.

### Via SQL Editor do Aiven (limite de 10 comandos)

O arquivo `001_schema_aiven.sql` é completo, mas possui mais de 10 comandos e não deve ser colado de uma vez no PG Studio. Execute, nesta ordem, os arquivos da pasta `sql/aiven_pgstudio/`: `01_catalogo.sql`, `02_painel_desigualdade.sql`, `03_trabalho_pnad.sql`, `04_grupos_findex_cobertura.sql`, `05_comentarios.sql`, `06_views.sql` e `07_monitoramento.sql`. Cada arquivo contém menos de 10 comandos.

Depois de criar as tabelas, gere o CSV de grupos localmente e use o carregador Python para inserir os dados. O limite do PG Studio afeta a quantidade de comandos executados por vez, não o tamanho lógico do schema.

O carregador usa a variável de ambiente `AIVEN_DATABASE_URL`. Nunca grave a senha no Git, no ZIP ou no arquivo `.py`.

Exemplo no PowerShell:

```powershell
$env:AIVEN_DATABASE_URL = "postgresql://avnadmin:SENHA@HOST:PORT/defaultdb?sslmode=require"
python -m pip install -r requirements-aiven.txt
python src/14_carregar_aiven.py --replace
```

`--replace` é uma operação de atualização completa: ela limpa somente as tabelas analíticas deste esquema e recarrega os CSVs processados. Sem essa opção, o carregador não altera o banco.

## Tabelas

- `source_catalog`: fontes, versões, cobertura e observações metodológicas.
- `country_year_panel`: painel compacto de desigualdade e contexto V-Dem.
- `wid_income_distribution`: extrato selecionado do WID.
- `wid_wealth_concentration`: concentração de riqueza no WID.
- `wiid_inequality`: observações harmonizadas da WIID.
- `labor_gender_gap`: diferença de rendimento por gênero no ILOSTAT.
- `labor_gender_modelled`: série modelada do ILOSTAT.
- `brazil_pnad_group_income`: agregados ponderados da PNAD por sexo e raça/cor.
- `financial_inclusion_waves`: ondas do Global Findex.
- `country_group_membership`: continentes, sub-regiões, regiões do Banco Mundial, grupos de renda e agrupamentos documentados.
- `source_coverage`: cobertura catalogada pelo pipeline.

Os grupos são derivados de metadados da WIID e não representam uma classificação capitalista/comunista. Eles permitem consultas como Brasil × Estados Unidos, Brasil × China, Brasil × Europa, Brasil × América Latina, Brasil × América do Norte e comparações globais, desde que a cobertura do indicador seja compatível. As views `v_pnad_latest_by_group`, `v_country_year_context`, `v_country_comparison_context` e `v_storage_usage` são consultas leves e não duplicam os dados.

## Política de volume

O banco deve permanecer abaixo de aproximadamente 600–700 MB. Os arquivos brutos e microdados ficam fora do PostgreSQL, preferencialmente em Parquet ou ZIP. Se o uso se aproximar do limite, temos que remover staging e duplicatas, ai vamos arquivar resultados antigos externamente.
