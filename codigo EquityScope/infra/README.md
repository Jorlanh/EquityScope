# Infraestrutura

A infraestrutura do projeto é representada por Terraform em `infra/terraform/`.

O código provisiona o serviço PostgreSQL da Aiven e o banco lógico que recebe o schema `analytics`. Os arquivos SQL continuam em `sql/`, porque o Terraform cria a infraestrutura e o carregador Python insere os dados analíticos.

A separação foi feita para manter cada responsabilidade no lugar certo:

- Terraform: serviço, banco lógico e configurações da infraestrutura;
- SQL: tabelas, chaves, índices e views;
- Python: tratamento, agregação, carga e gráficos;
- README e `docs/infraestrutura_e_seguranca.md`: reprodução e segurança.
