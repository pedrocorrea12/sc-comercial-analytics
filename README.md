# SC Comercial Analytics

Pipeline de dados e dashboard de inteligência comercial para acompanhamento de funil de captação educacional em Santa Catarina.

---

## Estrutura de pastas

```
sc-comercial-analytics/
├── scripts/
│   └── tratar_dados.py
├── 01_dados_brutos/
│   ├── leads_atualizados.csv
│   ├── matriculas_atualizadas.csv
│   └── pre_matriculas_atualizadas.csv
├── 02_dados_tratados/
│   ├── leads_tratado.csv
│   ├── inscritos_tratado.csv
│   ├── pre_matriculas_tratado.csv
│   ├── matriculas_tratado.csv
│   ├── metas_tratado.csv
│   └── fFunil.csv
├── .gitignore
└── README.md
```

---

## Descrição dos arquivos CSV

| Arquivo | Linhas | Descrição |
|---|---|---|
| `leads_tratado.csv` | 400 | Leads captados por curso, regional, canal e status CRM. Etapa inicial do funil. |
| `inscritos_tratado.csv` | 300 | Leads que avançaram para inscrição. Contém data de inscrição, curso e regional. |
| `pre_matriculas_tratado.csv` | 220 | Inscritos que realizaram pré-matrícula. Vinculados por `inscrito_id` e `lead_id`. |
| `matriculas_tratado.csv` | 180 | Pré-matrículas confirmadas, com data e valor da matrícula. |
| `metas_tratado.csv` | 11 | Metas por regional para cada etapa do funil (leads, inscritos, pré-matrículas, matrículas). |
| `fFunil.csv` | 400 | Tabela unificada do funil completo. Um registro por lead com todas as etapas em colunas. A coluna `etapa` indica a fase mais avançada atingida por cada lead. |

---

## Colunas principais — fFunil.csv

| Coluna | Tipo | Descrição |
|---|---|---|
| `lead_id` | int | Identificador único do lead |
| `data_lead` | date | Data de geração do lead (dd/mm/yyyy) |
| `curso` | text | Curso de interesse |
| `regional` | text | Regional da instituição |
| `canal` | text | Canal de captação (Facebook, Google, Indicação…) |
| `status_crm` | text | Status no CRM (Novo, Contato, Qualificado…) |
| `inscrito_id` | int | ID da inscrição (vazio se não inscrito) |
| `data_inscricao` | date | Data da inscrição |
| `pre_matricula_id` | int | ID da pré-matrícula |
| `data_pre_matricula` | date | Data da pré-matrícula |
| `matricula_id` | int | ID da matrícula |
| `data_matricula` | date | Data da matrícula |
| `valor_matricula` | float | Valor pago na matrícula |
| `etapa` | text | Etapa mais avançada: Lead / Inscrito / Pre_Matricula / Matricula |

---

## Scripts

| Script | Descrição |
|---|---|
| `scripts/tratar_dados.py` | Leitura, limpeza, normalização e exportação de todas as bases do funil |
| `scripts/eda_fiesc.py` | Análise exploratória completa — distribuições, conversões e sazonalidade |
| `scripts/setup_projeto.py` | Criação da estrutura de pastas do projeto |
| `scripts/gerar_shapefile_regionais.py` | Geração do GeoJSON das regionais SENAI/SC para uso em mapas |

---

## Como executar o pipeline

```bash
python scripts/tratar_dados.py
```

Gera todos os CSVs tratados em `02_dados_tratados/`.

---

*Dados referentes ao ano letivo de 2026 — Santa Catarina.*
