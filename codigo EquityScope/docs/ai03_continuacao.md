# Continuação da AI 03

## O que foi acrescentado

Nesta etapa, acrescentamos os arquivos de infraestrutura, as configurações de segurança e a documentação do projeto para atender aos requisitos do Marco 2.

| Requisito | Arquivo ou pasta | Situação |
|---|---|---|
| Infraestrutura com Terraform | `infra/terraform/` | Código preparado |
| Segurança | `.gitignore`, `infra/terraform/README.md` e `docs/infraestrutura_e_seguranca.md` | Documentada |
| Tratamento dos dados | `run_pipeline.py` e `src/` | Código disponível |
| Dados tratados | `data/processed/` e `outputs/tables/` | Preparados localmente |
| Banco de dados | `sql/` | Arquivos de criação e monitoramento disponíveis |
| Dashboard | `frontend/app.py` | Arquivo disponível |
| Testes | `tests/` | 12 testes locais aprovados |

## Infraestrutura escolhida

Escolhemos o PostgreSQL da Aiven para armazenar os dados resumidos do projeto. Os arquivos brutos e os microdados completos ficam fora do banco para reduzir o espaço utilizado.

O Terraform foi configurado para criar o serviço PostgreSQL, o banco do projeto e uma proteção contra exclusão acidental. Também permite configurar o acesso ao banco e consultar a URI de conexão.

O projeto da Aiven é informado por uma variável, pois já pode existir na conta da equipe.

## Segurança

O token da Aiven não fica no código nem deve ser enviado para o GitHub. Ele é configurado localmente pelo PowerShell:

```powershell
$env:TF_VAR_aiven_api_token = "SEU_TOKEN"
```

A conexão com o banco também é configurada localmente:

```powershell
$env:AIVEN_DATABASE_URL = terraform output -raw postgresql_service_uri
```

O arquivo `.gitignore` impede o envio de arquivos de configuração, estados e logs do Terraform. O arquivo `terraform.tfvars.example` contém apenas exemplos, sem senhas ou tokens.

## Como executar

Primeiro, entre na pasta do Terraform, copie o arquivo de exemplo e configure o projeto da Aiven:

```powershell
cd infra\terraform
Copy-Item terraform.tfvars.example terraform.tfvars
```

Depois, informe o token e execute os comandos:

```powershell
$env:TF_VAR_aiven_api_token = "SEU_TOKEN"

terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

Após a criação do banco, configure a conexão e execute o schema SQL:

```powershell
$env:AIVEN_DATABASE_URL = terraform output -raw postgresql_service_uri

psql $env:AIVEN_DATABASE_URL -f ..\..\sql\aiven_postgresql_completo.sql
```

Em seguida, carregue os dados tratados:

```powershell
python ..\..\src\14_carregar_aiven.py --replace
```

Por último, execute o arquivo `sql/003_monitoramento_aiven.sql` para conferir a quantidade de registros no banco. O resultado deve ser registrado no relatório para comprovar quantos dados foram realmente armazenados.

## Situação da entrega

Os arquivos do Terraform, a documentação e os dados tratados estão preparados. Porém, a criação do banco na Aiven, a carga dos dados e a conferência da quantidade de registros ainda dependem da execução na conta da equipe.

Por isso, essas etapas só serão consideradas concluídas depois que forem executadas e verificadas.