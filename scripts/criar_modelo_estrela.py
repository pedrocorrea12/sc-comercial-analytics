import sys
import os
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC  = r'C:\inteligencia_mercado\02_dados_tratados'
OUT  = r'C:\inteligencia_mercado\02_dados_tratados\modelo'
os.makedirs(OUT, exist_ok=True)

# ── leitura ───────────────────────────────────────────────────────────────────

print("Lendo CSVs tratados…")

DATE_COLS_MAP = {
    'leads_tratado.csv':         ['data_lead'],
    'inscritos_tratado.csv':     ['data_inscricao'],
    'pre_matriculas_tratado.csv': ['data_pre_matricula'],
    'matriculas_tratado.csv':    ['data_matricula'],
    'metas_tratado.csv':         [],
}

def read(fname):
    path = rf'{SRC}\{fname}'
    date_cols = DATE_COLS_MAP[fname]
    df = pd.read_csv(path, encoding='utf-8-sig')
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
    return df

leads      = read('leads_tratado.csv')
inscritos  = read('inscritos_tratado.csv')
pre_mat    = read('pre_matriculas_tratado.csv')
matriculas = read('matriculas_tratado.csv')
metas      = read('metas_tratado.csv')

# ── dimensões ─────────────────────────────────────────────────────────────────

print("Criando dimensões…")

def dim_from(sources: list, col: str, id_col: str, rename: dict = None) -> pd.DataFrame:
    valores = pd.concat([df[col] for df in sources if col in df.columns])
    df = pd.DataFrame({col: sorted(valores.dropna().unique())})
    if rename:
        df = df.rename(columns=rename)
        id_col_name = id_col
    else:
        id_col_name = id_col
    df.insert(0, id_col_name, range(1, len(df) + 1))
    return df

dRegional = dim_from([leads, inscritos], 'regional', 'regional_id')
dCurso    = dim_from([leads, inscritos], 'curso',    'curso_id')
dCanal    = dim_from([leads],            'canal',    'canal_id')
dStatus   = dim_from([leads],            'status_crm', 'status_id',
                     rename={'status_crm': 'status'})

# dCalendario
datas = pd.date_range('2026-01-01', '2026-12-31', freq='D')
hoje  = pd.Timestamp.today().normalize()

MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',    4: 'Abril',
    5: 'Maio',    6: 'Junho',     7: 'Julho',     8: 'Agosto',
    9: 'Setembro',10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}
DIAS_PT = {
    0: 'Segunda-feira', 1: 'Terça-feira',  2: 'Quarta-feira',
    3: 'Quinta-feira',  4: 'Sexta-feira',  5: 'Sábado', 6: 'Domingo',
}

dCalendario = pd.DataFrame({
    'data':             datas,
    'ano':              datas.year,
    'mes':              datas.month,
    'mes_nome':         datas.month.map(MESES_PT),
    'trimestre':        datas.quarter,
    'semana':           datas.isocalendar().week.astype(int),
    'dia_semana':       datas.dayofweek + 1,          # 1=Seg … 7=Dom
    'dia_semana_nome':  datas.dayofweek.map(DIAS_PT),
    'is_fim_de_semana': datas.dayofweek.isin([5, 6]),
    'ytd_flag':         datas <= hoje,
    'mtd_flag':         (datas <= hoje) & (datas.month == hoje.month) & (datas.year == hoje.year),
})

# ── tabelas fato ──────────────────────────────────────────────────────────────

print("Criando tabelas fato…")

fLeads         = leads.copy()
fInscritos     = inscritos.copy()
fPreMatriculas = pre_mat.copy()
fMatriculas    = matriculas.copy()

# ── exportação ────────────────────────────────────────────────────────────────

print("Exportando…\n")

tabelas = [
    ('dRegional',    dRegional),
    ('dCurso',       dCurso),
    ('dCanal',       dCanal),
    ('dStatus',      dStatus),
    ('dCalendario',  dCalendario),
    ('fLeads',       fLeads),
    ('fInscritos',   fInscritos),
    ('fPreMatriculas', fPreMatriculas),
    ('fMatriculas',  fMatriculas),
    ('metas_tratado', metas),
]

print(f"{'='*60}")
print("TABELAS EXPORTADAS")
print(f"{'='*60}")

for nome, df in tabelas:
    path = rf'{OUT}\{nome}.csv'
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print(f"\n{'─'*60}")
    print(f"  {nome}.csv")
    print(f"  Shape  : {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    print(f"  Colunas: {df.columns.tolist()}")
    print(f"  Amostra (3 linhas):")
    print(df.head(3).to_string(index=False))

print(f"\n{'='*60}")
print(f"Arquivos salvos em: {OUT}")
print(f"{'='*60}")
