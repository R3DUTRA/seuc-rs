# SEUC/RS — Dashboard Web

Plataforma oficial de dados do Sistema Estadual de Unidades de Conservação do Rio Grande do Sul.

## Estrutura do projeto

```
seuc_rs/
├── app.py              ← App principal
├── requirements.txt    ← Dependências Python
├── README.md
└── data/
    ├── BaseSeuc.xlsx
    ├── BIOMAS_SCM_12M.xlsx
    ├── Municipios.xlsx
    └── BioMap.xlsx
```

## Rodando localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy gratuito no Streamlit Cloud

1. Crie uma conta em https://streamlit.io/cloud
2. Crie um repositório no GitHub e suba todos os arquivos
3. No Streamlit Cloud: **New app → selecione o repo → app.py**
4. Clique em **Deploy** — em ~2 minutos está no ar

## Páginas

| Sigla | Página | Descrição |
|-------|--------|-----------|
| MENU | Visão geral | KPIs e gráficos gerais |
| CR   | Cadastro e Regularização | Filtros por esfera/bioma/grupo/categoria |
| CE   | Cobertura Espacial | Áreas por bioma SCM e esfera |
| IE   | Implementação e Efetividade | % PM, CG, ZA, CNUC, Shapefile |
| GE   | Informações Geoespaciais | Municípios, biomas, mapa de UCs |

## Dados

- **BaseSeuc.xlsx** — Base principal com 225 UCs e 47 atributos
- **BIOMAS_SCM_12M.xlsx** — Dados geoespaciais por bioma (115 registros)
- **Municipios.xlsx** — Relação UC × Município (260 registros)
- **BioMap.xlsx** — Mapeamento bioma × UC (242 registros)
