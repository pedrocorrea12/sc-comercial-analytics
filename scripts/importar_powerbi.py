import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUT_DIR  = r"C:\inteligencia_mercado\03_powerbi"
OUT_FILE = os.path.join(OUT_DIR, "modelo_powerquery.pq")
os.makedirs(OUT_DIR, exist_ok=True)

BASE_URL = (
    "https://raw.githubusercontent.com/pedrocorrea12/"
    "sc-comercial-analytics/master/02_dados_tratados/modelo/"
)

# ── tipos por coluna ──────────────────────────────────────────────────────────

TIPOS = {
    "dRegional": [
        ('regional_id', 'Int64.Type'),
        ('regional',    'type text'),
    ],
    "dCurso": [
        ('curso_id', 'Int64.Type'),
        ('curso',    'type text'),
    ],
    "dCanal": [
        ('canal_id', 'Int64.Type'),
        ('canal',    'type text'),
    ],
    "dStatus": [
        ('status_id', 'Int64.Type'),
        ('status',    'type text'),
    ],
    "dCalendario": [
        ('data',             'type date'),
        ('ano',              'Int64.Type'),
        ('mes',              'Int64.Type'),
        ('mes_nome',         'type text'),
        ('trimestre',        'Int64.Type'),
        ('semana',           'Int64.Type'),
        ('dia_semana',       'Int64.Type'),
        ('dia_semana_nome',  'type text'),
        ('is_fim_de_semana', 'Int64.Type'),
        ('ytd_flag',         'Int64.Type'),
        ('mtd_flag',         'Int64.Type'),
    ],
    "fLeads": [
        ('lead_id',    'Int64.Type'),
        ('data_lead',  'type date'),
        ('curso',      'type text'),
        ('regional',   'type text'),
        ('canal',      'type text'),
        ('status_crm', 'type text'),
        ('etapa',      'type text'),
    ],
    "fInscritos": [
        ('inscrito_id',    'Int64.Type'),
        ('lead_id',        'Int64.Type'),
        ('data_inscricao', 'type date'),
        ('curso',          'type text'),
        ('regional',       'type text'),
        ('etapa',          'type text'),
    ],
    "fPreMatriculas": [
        ('pre_matricula_id',    'Int64.Type'),
        ('inscrito_id',         'Int64.Type'),
        ('lead_id',             'Int64.Type'),
        ('data_pre_matricula',  'type date'),
        ('etapa',               'type text'),
    ],
    "fMatriculas": [
        ('matricula_id',      'Int64.Type'),
        ('pre_matricula_id',  'Int64.Type'),
        ('inscrito_id',       'Int64.Type'),
        ('lead_id',           'Int64.Type'),
        ('data_matricula',    'type date'),
        ('valor_matricula',   'Decimal.Type'),
        ('etapa',             'type text'),
    ],
}

TABELAS = [
    "dRegional", "dCurso", "dCanal", "dStatus", "dCalendario",
    "fLeads", "fInscritos", "fPreMatriculas", "fMatriculas",
]

# ── helpers M ─────────────────────────────────────────────────────────────────

def m_tipos(nome):
    linhas = [f'        {{"{col}", {tipo}}}' for col, tipo in TIPOS[nome]]
    return ",\n".join(linhas)

def m_query(nome):
    return f"""\
// ─── {nome} ───────────────────────────────────────────────────────────────────
// Consulta: {nome}
let
    Fonte = fnCarregarCSV("{nome}.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {{
{m_tipos(nome)}
    }})
in
    Tipos"""

# ── montagem do arquivo .pq ───────────────────────────────────────────────────

HEADER = f"""\
// =============================================================================
// modelo_powerquery.pq  —  SC Comercial Analytics
// Power Query M  |  gerado automaticamente por importar_powerbi.py
// =============================================================================
//
// COMO USAR NO POWER BI DESKTOP
// ─────────────────────────────
// 1. Abra Transformar dados > Editor do Power Query
// 2. Crie o parâmetro BaseURL:
//    Gerenciar parâmetros > Novo > Nome: BaseURL | Tipo: Texto
//    Valor atual: {BASE_URL}
// 3. Para cada bloco abaixo:
//    Nova consulta > Consulta em branco > Editor avançado > cole o código
// =============================================================================


// =============================================================================
// PARÂMETRO  BaseURL
// =============================================================================
// (criar via interface: Gerenciar parâmetros > Novo parâmetro)
// Nome : BaseURL
// Tipo : Texto
// Valor: {BASE_URL}


// =============================================================================
// FUNÇÃO  fnCarregarCSV
// =============================================================================
// Consulta: fnCarregarCSV
(nomeArquivo as text) as table =>
let
    url    = BaseURL & nomeArquivo,
    fonte  = Csv.Document(
                 Web.Contents(url),
                 [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]
             ),
    header = Table.PromoteHeaders(fonte, [PromoteAllScalars=true])
in
    header


// =============================================================================
// TABELAS DIMENSÃO E FATO
// =============================================================================
"""

blocos = "\n\n".join(m_query(t) for t in TABELAS)
conteudo = HEADER + blocos + "\n"

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(conteudo)

# ── saída ─────────────────────────────────────────────────────────────────────

print("=" * 78)
print(f"Arquivo gerado: {OUT_FILE}")
print("=" * 78)
print(conteudo)
print("=" * 78)
print(f"Total de linhas: {conteudo.count(chr(10))}")
print("=" * 78)
