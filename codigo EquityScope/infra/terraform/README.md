# Infraestrutura da Aiven

Nesta pasta estão os arquivos do Terraform usados para configurar a infraestrutura do projeto. Eles definem o serviço PostgreSQL na Aiven, o banco de dados e as configurações de acesso.

O projeto da Aiven é informado por uma variável, pois ele pode já existir na conta da equipe. Também foi incluída uma proteção para evitar a exclusão acidental do serviço.

## Pré-requisitos

Para configurar a infraestrutura, é necessário ter:

- Terraform na versão 1.6 ou superior;
- uma conta na Aiven;
- um projeto já criado na Aiven;
- um token com permissão para administrar o projeto;
- um plano PostgreSQL disponível na conta.

## Configuração

No PowerShell, entre nesta pasta e execute os comandos abaixo:

```powershell
$env:TF_VAR_aiven_api_token = "SEU_TOKEN"
Copy-Item terraform.tfvars.example terraform.tfvars
```

Depois, edite o arquivo `terraform.tfvars` e informe o nome do projeto. Em seguida, execute:

```powershell
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

O token, a senha do banco, a URI de conexão e o arquivo `terraform.tfstate` não devem ser enviados para o GitHub. O estado do Terraform pode conter informações sensíveis, por isso deve ser mantido em um local privado.

## Conexão com o banco

Depois de criar a infraestrutura, consulte a URI de conexão no terminal:

```powershell
terraform output -raw postgresql_service_uri
```

Para carregar os dados, configure a variável de ambiente e execute o script:

```powershell
$env:AIVEN_DATABASE_URL = terraform output -raw postgresql_service_uri
python ..\..\src\14_carregar_aiven.py --replace
```

Antes da carga, execute o arquivo `sql/aiven_postgresql_completo.sql` para criar as tabelas. Depois, execute `sql/003_monitoramento_aiven.sql` para conferir a quantidade de registros armazenados.

## Observação sobre o plano Free

O nome do plano pode variar conforme a conta e a região. O exemplo utilizado é `free-1-1gb`. Se a Aiven apresentar outro identificador, será necessário ajustar a variável `aiven_plan` no arquivo `terraform.tfvars`.

No plano Free, não é necessário informar `aiven_cloud_name`, pois a própria Aiven escolhe a localização. O acesso público fica habilitado para permitir a conexão a partir do computador da equipe. Se houver uma alternativa segura de conexão, ele poderá ser desativado.