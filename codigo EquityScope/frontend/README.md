# Frontend

O dashboard usa Streamlit e pode trabalhar com os CSVs processados ou com as tabelas da Aiven.

## Rodar localmente

Na raiz do projeto:

```powershell
python -m pip install -r requirements-frontend.txt
streamlit run frontend/app.py
```

Por padrão, o painel lê `data/processed` e `outputs/tables`. Para consultar o PostgreSQL, selecione `Aiven` no menu lateral e informe a URL do banco, ou configure `AIVEN_DATABASE_URL` antes de iniciar.

O painel possui filtros por país, agrupamento geográfico ou socioeconômico, período, gênero, raça/cor e indicador. Os gráficos são interativos: o hover mostra os valores e, quando existem, os limites mínimo e máximo; clicar em um ponto fixa o detalhe; clicar na legenda oculta ou exibe uma série; e a barra nativa permite zoom e retorno à visão original. Os rendimentos da PNAD são mostrados como nominais enquanto `deflator_applied` permanecer falso.
