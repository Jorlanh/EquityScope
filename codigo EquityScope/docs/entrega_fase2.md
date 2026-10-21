# Entrega técnica da Fase 2

## 1. Escopo da entrega

O projeto prepara uma base observacional para comparar desigualdade de renda, concentração econômica, remuneração por gênero, inclusão financeira e diferenças de rendimento por sexo e cor ou raça no Brasil. O recorte geral é 2002–2026, mas 2026 foi incorporado somente onde já existem dados brasileiros disponíveis. As comparações internacionais permanecem limitadas ao último ano existente em cada fonte; não há preenchimento automático de lacunas.

O produto não é uma base de projeção financeira. É uma camada analítica comparativa. Qualquer projeção futura deverá ser construída em outra etapa, com modelo, validação e intervalo de incerteza próprios.

## 2. Levantamento de parâmetros e tipagem

### Fontes e formatos de origem

| Fonte | Formato de origem catalogado | Uso no projeto | Limite temporal adotado |
|---|---|---|---|
| WID | ZIP com arquivos tabulares e metadados | distribuição de renda e patrimônio do Brasil | 2002–2026, conforme disponibilidade |
| WIID | XLSX | observações de desigualdade e Gini por país-ano | 2002–2025/último disponível |
| ILOSTAT | CSV | remuneração por sexo e hiato estimado | 2002–2025/último disponível |
| PNAD Contínua | ZIP trimestral com microdados | rendimento brasileiro por sexo e cor ou raça | 2012–2026; 2026-T1 e 2026-T2 presentes |
| Global Findex | XLSX | contas, poupança, crédito e pagamentos por gênero | ondas de 2011, 2014, 2017, 2021 e 2024 |
| V-Dem | ZIP | painel institucional país-ano | 2002–2025, conforme a configuração internacional |

O inventário das fontes está em `data/metadata/inventario_arquivos.csv`, a cobertura está em `data/metadata/catalogo_cobertura.csv` e as versões e observações estão registradas em `data/metadata/cobertura_fontes.csv`.

### Estratégia para o limite de 1 GB do Aiven Free

O arquivo bruto não é carregado no PostgreSQL. Ele permanece local, preservado para reprocessamento. O banco Aiven recebe apenas tabelas analíticas compactas:

- recorte temporal e seleção de indicadores antes da carga;
- agregação de WIID para um registro por país-ano no painel e preservação das observações selecionadas na tabela de apoio;
- agregação da PNAD por ano, trimestre, nível de agregação, sexo e cor ou raça;
- seleção de indicadores de renda e patrimônio do WID, sem copiar todos os arquivos originais;
- seleção dos indicadores de inclusão financeira do Findex por onda;
- tipos numéricos adequados, chaves e índices apenas nos campos de consulta;
- arquivos brutos, microdados completos, ZIPs e intermediários ficam fora do Aiven;
- consultas de cruzamento usam as tabelas analíticas e as views definidas em `sql/002_views_aiven.sql`.

Assim, o Aiven funciona como catálogo online da versão final resumida e consultável, não como repositório dos microdados originais.

### Conversões e tipagem

As conversões mais importantes são:

- anos e trimestres para inteiros;
- códigos ISO3, sexo, raça, país e indicador para texto padronizado;
- rendimentos e índices para tipos numéricos;
- contagens amostrais para inteiro;
- pesos populacionais para número decimal;
- proporções do Findex e participações do WID para `double precision`;
- `deflator_applied` e `is_member` para booleano;
- datas históricas do V-Dem para `date` quando disponíveis.

O rendimento da PNAD permanece nominal e o campo `deflator_applied` fica falso. Portanto, não se deve interpretar a série nominal como comparação real entre anos antes da aplicação do deflator oficial.

## 3. Entregável: base tratada

Os principais resultados tratados são:

| Arquivo | Conteúdo | Linhas atuais |
|---|---|---:|
| `data/processed/wid_selecao_2002_2026.csv` | seleção WID do Brasil | 240.740 |
| `data/processed/wiid_2002_2026.csv` | observações WIID filtradas | 19.636 |
| `data/processed/ilostat_remuneracao_harmonizada.csv` | remuneração harmonizada | 1.527 |
| `data/processed/ilostat_gender_income_gap_modelado.csv` | hiato de renda modelado por país-ano | 87 |
| `data/processed/pnad_rendimento_sexo_raca.csv` | PNAD agregada por sexo e cor ou raça | 694 |
| `data/processed/global_findex_selecionado.csv` | ondas selecionadas do Findex | 8.401 |
| `data/processed/country_group_membership.csv` | grupos geográficos e comparações documentadas | 827 |
| `outputs/tables/cobertura_processada.csv` | cobertura usada no catálogo de fontes | 140 |
| `data/processed/painel_analitico_pais_ano.csv` | painel analítico V-Dem + WIID | 4.282 |
| `outputs/tables/wiid_gini_pais_ano.csv` | Gini resumido por país-ano | 2.071 |
| `outputs/tables/ilostat_gap_genero.csv` | hiato estimado de remuneração | 157 |
| `outputs/tables/findex_gap_genero.csv` | diferença mulher-homem em pontos percentuais | 1.933 |
| `outputs/tables/wid_brasil_concentracao.csv` | renda e patrimônio por grupo de distribuição | 230 |

O processo de tratamento está dividido nos scripts numerados em `src/`. O arquivo `run_pipeline.py` executa a sequência completa, respeitando a separação entre dados brutos, intermediários, processados e resultados.

## 4. Gráficos e exploração visual

O projeto entrega duas formas de leitura:

1. Gráficos estáticos, gerados por `src/16_gerar_graficos_relatorio.py` em PNG quando Matplotlib está instalado e por `src/17_gerar_graficos_svg.py` em SVG com a biblioteca padrão:
   - `01_gini_comparacao_paises`: Brasil, China, Estados Unidos e demais países disponíveis;
   - `02_hiato_genero_comparacao_paises`: comparação do hiato de remuneração entre os países disponíveis;
   - `03_brasil_genero_raca_pnad`: diferença de rendimento nominal por sexo e cor ou raça no trimestre brasileiro mais recente;
   - `04_inclusao_financeira_genero`: diferença entre mulheres e homens no acesso a contas;
   - `05_gini_medio_por_regiao`: média descritiva do Gini entre países disponíveis por região.
2. Dashboard Streamlit em `frontend/app.py`, com filtros por país, grupo, ano e fonte e download da seleção filtrada.

O gráfico de sexo × cor ou raça é brasileiro porque a PNAD é a fonte que oferece esse cruzamento com a granularidade usada no projeto. Não será criada uma falsa comparação internacional de raça quando as classificações não forem harmonizadas entre os países.

## 5. Entregável: banco de dados Aiven

O script de criação é `sql/aiven_postgresql_completo.sql`. Ele pode ser executado por `psql`, DBeaver ou outro cliente PostgreSQL. Para ambientes que limitam a execução a dez comandos, os arquivos em `sql/aiven_pgstudio/` estão divididos em blocos menores.

O esquema `analytics` contém:

| Tabela | Função principal | Chave ou relação |
|---|---|---|
| `source_catalog` | catálogo de fonte, versão, período e URL | `source_id` primária |
| `country_year_panel` | painel país-ano com V-Dem e resumo de desigualdade | `country_code + year` |
| `wid_income_distribution` | extratos de distribuição de renda | índice país-ano; FK para `source_catalog` |
| `wid_wealth_concentration` | concentração de patrimônio | índice país-ano; FK para `source_catalog` |
| `wiid_inequality` | observações de desigualdade harmonizadas | índice país-ano; FK para `source_catalog` |
| `labor_gender_gap` | remuneração e hiato entre gêneros | índice país-ano; FK para `source_catalog` |
| `labor_gender_modelled` | indicadores modelados do trabalho | índice país-ano; FK para `source_catalog` |
| `brazil_pnad_group_income` | agregados brasileiros sexo × raça | chave ano-trimestre-nível-sexo-raça |
| `financial_inclusion_waves` | ondas do Global Findex | chave país-ano-grupo-detalhe; FK para `source_catalog` |
| `country_group_membership` | grupos geográficos e comparações documentadas | chave país-tipo-código; FK para `source_catalog` |
| `source_coverage` | cobertura e observações de cada fonte | FK para `source_catalog` |

Na preparação local, os dez arquivos que alimentam o carregador somam 275.194 registros, sem contar as oito linhas de referência inseridas em `source_catalog`. Esse número representa a quantidade preparada para carga. A quantidade efetivamente armazenada no servidor Aiven só deve ser registrada depois da execução do carregador e da consulta de monitoramento no próprio banco.

Os tipos, campos e índices estão definidos diretamente no SQL. Os relacionamentos por país e ano que formam o painel são relações analíticas por chave composta; não se duplicam microdados dentro do banco.

### Consultas e views

`sql/002_views_aiven.sql` cria consultas resumidas para o dashboard. `sql/003_monitoramento_aiven.sql` permite verificar quantidade de linhas, tamanho das tabelas e cobertura temporal. O SQL de carga usa `COPY`/carga por arquivo somente na etapa de ingestão preparada; o ZIP completo não deve ser apontado para o PostgreSQL.

## 6. Situação de validação

Foram executados localmente os doze testes automatizados do projeto, todos aprovados, além da conferência da estrutura dos arquivos usados pelo carregador. A criação e a carga efetiva no servidor Aiven dependem da execução do SQL com a URL do serviço do usuário; não há evidência local de uma conexão ao Aiven nesta entrega. Por isso, a documentação não afirma que o banco online já está populado.

Depois da carga, executar as consultas de monitoramento e registrar no relatório os números retornados pelo Aiven. Essa etapa é a evidência final da quantidade de dados armazenados em nuvem.

## 7. Limitações que permanecem documentadas

- 2026 não é uma série internacional completa; no Brasil foram identificados PNAD 2026-T1 e 2026-T2.
- Findex é uma série em ondas, não uma série anual contínua.
- As categorias de cor ou raça da PNAD não são automaticamente comparáveis às classificações usadas em todos os demais países.
- O WID, WIID, ILOSTAT e PNAD não medem exatamente o mesmo conceito de renda.
- As associações estatísticas do projeto são exploratórias e não demonstram causalidade.
- Valores nominais da PNAD exigem deflação antes de comparação temporal de nível.

## 8. Continuação da AI 03

### Infraestrutura

O código Terraform em `infra/terraform/` representa o serviço PostgreSQL e o banco lógico usados pelo projeto na Aiven. O projeto Aiven é recebido por variável e o código não inclui token ou senha.

### Segurança

O token da Aiven é informado por `TF_VAR_aiven_api_token`. A URI de conexão é usada na variável local `AIVEN_DATABASE_URL`. Arquivos de variáveis, estado e cache do Terraform estão bloqueados no `.gitignore`. A estratégia e os cuidados estão detalhados em `docs/infraestrutura_e_seguranca.md`.

### Reprodução

Depois de configurar as variáveis, a equipe deve executar `terraform init`, `terraform validate`, `terraform plan` e `terraform apply` dentro de `infra/terraform/`. Depois, deve executar o schema SQL, carregar os CSVs com `src/14_carregar_aiven.py` e registrar a contagem com `sql/003_monitoramento_aiven.sql`.

Nesta entrega, o código de infraestrutura está versionado e os testes locais passaram. O provisionamento, a carga e a contagem online continuam condicionados às credenciais e à conta Aiven da equipe.
