# Dicionário inicial de variáveis

## WID.world

Os arquivos têm estrutura longa com `country`, `variable`, `percentile`, `year`, `value`, `age`, `pop` e `data_quality`. A interpretação de `variable` deve vir do arquivo `WID_metadata_<pais>.csv` correspondente.

## WIID

A versão datada `WIID-08SEP2026.xlsx` apresenta, entre outros campos, país, código de país, ano e Gini. O arquivo `wiidglobal_6.xlsx` deve ser tratado como outra versão/extrato, não como linhas adicionais da mesma base.

## ILOSTAT

O arquivo de remuneração contém `ref_area.label`, `indicator.label`, `sex.label`, `classif1.label`, `time`, `obs_value` e notas metodológicas. `classif1.label` identifica a unidade monetária.

## PNAD Contínua

Os microdados trimestrais exigem o dicionário e o arquivo de input da pesquisa. As variáveis de sexo, cor ou raça, rendimento, peso e desenho amostral devem ser selecionadas a partir da documentação oficial.

## Global Findex

O arquivo possui uma aba de dados, uma tabela de séries e notas. Os indicadores são percentuais da população adulta ou de subgrupos definidos pelo próprio banco de dados.

## V-Dem

O arquivo selecionado é país-ano. O pipeline preserva identificadores e índices de alto nível disponíveis, sem assumir que qualquer índice seja uma classificação ideológica do governo.
