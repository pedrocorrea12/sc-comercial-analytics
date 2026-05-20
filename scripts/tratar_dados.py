import sys
import os
import re
import unicodedata
import pandas as pd

# Garante UTF-8 no stdout do terminal
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = r'C:\inteligencia_mercado\01_dados_brutos'
OUT  = r'C:\inteligencia_mercado\02_dados_tratados'
os.makedirs(OUT, exist_ok=True)

# ── helpers ──────────────────────────────────────────────────────────────────

def normalize_col(name: str) -> str:
    nfkd = unicodedata.normalize('NFKD', str(name))
    ascii_name = nfkd.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', '_', ascii_name.strip()).lower()

SIGLAS = {'Ti': 'TI', 'Rh': 'RH', 'It': 'IT'}

def proper(series: pd.Series) -> pd.Series:
    result = series.astype(str).str.strip().str.title()
    return result.replace(SIGLAS)

def fmt_date(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, dayfirst=False, errors='coerce')
    return parsed.dt.strftime('%d/%m/%Y')

def read_csv(path):
    for enc in ('utf-8-sig', 'cp1252', 'latin-1'):
        try:
            df = pd.read_csv(path, encoding=enc)
            # teste rápido: se não há U+FFFD nos dados, a encoding está certa
            sample = df.astype(str).to_csv(index=False)
            if '�' not in sample:
                return df
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, encoding='latin-1', errors='replace')

# ── leitura ──────────────────────────────────────────────────────────────────

print("Lendo arquivos…")
leads         = read_csv(rf'{BASE}\leads_atualizados.csv')
inscritos     = pd.read_excel(rf'{BASE}\inscritos_atualizados.xlsx')
pre_mat       = read_csv(rf'{BASE}\pre_matriculas_atualizadas.csv')
matriculas    = read_csv(rf'{BASE}\matriculas_atualizadas.csv')
metas         = pd.read_excel(rf'{BASE}\metas_atualizadas.xlsx')

# ── normalização de nomes de colunas ─────────────────────────────────────────

for df in (leads, inscritos, pre_mat, matriculas, metas):
    df.columns = [normalize_col(c) for c in df.columns]

# ── colunas de texto e data por tabela ───────────────────────────────────────

TEXT_COLS = {
    'leads':      ['regional', 'curso', 'canal', 'status_crm'],
    'inscritos':  ['regional', 'curso'],
    'pre_mat':    [],
    'matriculas': [],
    'metas':      ['regional'],
}

DATE_COLS = {
    'leads':      ['data_lead'],
    'inscritos':  ['data_inscricao'],
    'pre_mat':    ['data_pre_matricula'],
    'matriculas': ['data_matricula'],
    'metas':      [],
}

ETAPAS = {
    'leads':      'Lead',
    'inscritos':  'Inscrito',
    'pre_mat':    'Pre_Matricula',
    'matriculas': 'Matricula',
    'metas':      'Meta',
}

tables = {
    'leads': leads, 'inscritos': inscritos, 'pre_mat': pre_mat,
    'matriculas': matriculas, 'metas': metas,
}

# ── tratamento ───────────────────────────────────────────────────────────────

print("Aplicando tratamentos…")
for key, df in tables.items():
    for col in TEXT_COLS[key]:
        if col in df.columns:
            df[col] = proper(df[col])
    for col in DATE_COLS[key]:
        if col in df.columns:
            df[col] = fmt_date(df[col])
    df['etapa'] = ETAPAS[key]

# ── fFunil ───────────────────────────────────────────────────────────────────

print("Construindo fFunil…")

# Colunas selecionadas para o funil (evita duplicatas de curso/regional)
ins_cols  = ['lead_id', 'inscrito_id', 'data_inscricao']
pre_cols  = ['inscrito_id', 'pre_matricula_id', 'data_pre_matricula']
mat_cols  = ['pre_matricula_id', 'matricula_id', 'data_matricula', 'valor_matricula']

funil = leads.copy()
funil = funil.merge(inscritos[ins_cols],  on='lead_id',         how='left')
funil = funil.merge(pre_mat[pre_cols],    on='inscrito_id',     how='left')
funil = funil.merge(matriculas[mat_cols], on='pre_matricula_id', how='left')

# Etapa mais avançada atingida por lead
def calc_etapa(row):
    if pd.notna(row.get('matricula_id')):    return 'Matricula'
    if pd.notna(row.get('pre_matricula_id')): return 'Pre_Matricula'
    if pd.notna(row.get('inscrito_id')):     return 'Inscrito'
    return 'Lead'

funil['etapa'] = funil.apply(calc_etapa, axis=1)

# Reordena colunas: IDs e datas cronológicas primeiro
col_order = [
    'lead_id', 'data_lead', 'curso', 'regional', 'canal', 'status_crm',
    'inscrito_id', 'data_inscricao',
    'pre_matricula_id', 'data_pre_matricula',
    'matricula_id', 'data_matricula', 'valor_matricula',
    'etapa',
]
funil = funil[[c for c in col_order if c in funil.columns]]

# ── exportação ───────────────────────────────────────────────────────────────

print("Exportando arquivos…\n")

exports = [
    ('leads_tratado',         leads),
    ('inscritos_tratado',     inscritos),
    ('pre_matriculas_tratado', pre_mat),
    ('matriculas_tratado',    matriculas),
    ('metas_tratado',         metas),
    ('fFunil',                funil),
]

for fname, df in exports:
    path = rf'{OUT}\{fname}.csv'
    df.to_csv(path, index=False, encoding='utf-8-sig')

# ── resumo ───────────────────────────────────────────────────────────────────

print("=" * 60)
print("RESUMO DAS TABELAS EXPORTADAS")
print("=" * 60)

for fname, df in exports:
    print(f"\n{'─'*60}")
    print(f"  {fname}.csv")
    print(f"  Shape  : {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    print(f"  Colunas: {df.columns.tolist()}")
    print(f"  Amostra (3 linhas):")
    print(df.head(3).to_string(index=False))

print(f"\n{'='*60}")
print(f"Arquivos salvos em: {OUT}")
print("=" * 60)
