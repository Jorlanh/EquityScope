# Desigualdade e concentração do poder econômico

Este projeto organiza dados públicos sobre renda, patrimônio, desigualdade, gênero, cor ou raça e inclusão financeira. O objetivo é comparar o Brasil com outros países e observar diferenças entre grupos.

## Como o projeto está organizado

- `data/`: dados tratados e metadados;
- `docs/`: explicações do tratamento e das limitações;
- `frontend/`: painel com filtros e gráficos;
- `infra/terraform/`: infraestrutura da Aiven;
- `outputs/`: tabelas, gráficos e resultados;
- `sql/`: tabelas, views e monitoramento do PostgreSQL;
- `src/`: scripts do tratamento e da carga;
- `tests/`: testes do projeto.

Os arquivos brutos ficam fora do banco. O PostgreSQL recebe somente os extratos tratados e resumidos. O arquivo bruto esperado pelo pipeline é `data/raw/dados para bigdata.zip`, mas ele não é incluído neste pacote por causa do tamanho.

## Fontes e período

Usamos WID.world, WIID, ILOSTAT, PNAD Contínua, Global Findex e V-Dem. O período geral é de 2002 a 2026, respeitando a cobertura de cada fonte. O ano de 2026 aparece apenas nos dados brasileiros que já estão disponíveis.

## Tratamento

O tratamento é executado pelo `run_pipeline.py`. Os scripts inspecionam os arquivos, selecionam os indicadores, padronizam campos, agregam a PNAD por ano, trimestre, sexo e cor ou raça, preparam as tabelas e geram os gráficos.

O WID, a WIID, o ILOSTAT, a PNAD e o Global Findex permanecem identificados por fonte. As categorias de cor ou raça não são tratadas como se fossem iguais em todos os países. Os valores da PNAD continuam nominais até que um deflator oficial seja aplicado.

## Execução local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_pipeline.py
python -m unittest discover -s tests -v
```

Para iniciar o painel:

```powershell
python -m pip install -r requirements-frontend.txt
streamlit run frontend/app.py
```

## Infraestrutura como código

O Terraform em `infra/terraform/` representa o serviço PostgreSQL e o banco lógico da Aiven. O token não fica no código. Ele deve ser usado pela variável `TF_VAR_aiven_api_token`. A URI do banco deve ser usada pela variável `AIVEN_DATABASE_URL`.

Dentro de `infra/terraform/`, a sequência é:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform validate
terraform plan
terraform apply
```

Depois do `apply`, executar `sql/aiven_postgresql_completo.sql`, carregar os CSVs com `python src/14_carregar_aiven.py --replace` e consultar `sql/003_monitoramento_aiven.sql`.

## Segurança das informações

Não versionar tokens, senhas, URLs de conexão, `.tfstate`, `.terraform` ou `.venv`. O `.gitignore` já bloqueia esses arquivos. O estado do Terraform deve ficar em local privado.

## Repositório e reprodução

O projeto reúne o código, os dados tratados, o SQL, o Terraform, o painel, os testes e a documentação em uma mesma estrutura. Assim, conseguiremos entender o caminho dos dados e refazer o tratamento em outro computador.

## Situação da entrega

O código, a documentação, o Terraform, os dados tratados, o SQL, o frontend e os testes estão organizados. A criação e a carga no banco online ainda dependem de criarmos conta e e usar as credenciais.
