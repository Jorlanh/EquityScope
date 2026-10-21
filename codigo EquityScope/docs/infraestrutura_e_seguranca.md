# Infraestrutura e segurança

## Infraestrutura

Usamos a Aiven para hospedar o PostgreSQL que guarda a versão analítica resumida dos dados. O Terraform em `infra/terraform/` representa o serviço PostgreSQL e o banco lógico do projeto.

O Terraform não cria um projeto Aiven novo. Ele recebe o nome de um projeto já existente e cria o serviço dentro dele. Essa escolha evita misturar a administração da conta com o código do trabalho e permite que a equipe use o projeto que já foi criado no console.

O schema, as tabelas, as chaves estrangeiras, os índices e as views continuam definidos em SQL. Depois que o serviço estiver disponível, o script `src/14_carregar_aiven.py` envia os CSVs tratados usando `COPY`.

## Segurança

Não versionamos credenciais. O token da API da Aiven deve ser informado por `TF_VAR_aiven_api_token`. A URL com usuário e senha do PostgreSQL deve ser usada somente na variável de ambiente `AIVEN_DATABASE_URL` durante a carga.

O `.gitignore` bloqueia:

- `terraform.tfvars`;
- `.terraform/`;
- arquivos de estado do Terraform;
- logs e arquivos de crash do Terraform;
- a senha e a URI se forem salvas em arquivos locais.

O arquivo `terraform.tfvars.example` contém apenas nomes de variáveis e exemplos sem credenciais. A URI produzida pelo Terraform é marcada como `sensitive`, mas isso não substitui o cuidado com o arquivo de estado. O estado pode conter informações sensíveis e deve ficar fora do repositório, em uma máquina protegida ou em um backend remoto com controle de acesso.

Para o plano Free, a conexão pública do PostgreSQL fica configurável porque a equipe precisa conseguir executar a carga a partir do computador local. A conexão deve usar TLS, a senha deve permanecer fora do código e, se a infraestrutura permitir uma rede privada ou uma restrição por IP, a variável `enable_public_access` deve ser desligada.

## Limites da entrega


