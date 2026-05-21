"""
injetar_powerbi.py — SC Comercial Analytics
Injeta as consultas do modelo estrela no arquivo .pbix via manipulação direta do ZIP.

Estrutura .pbix (formato ZIP):
  DataMashup  → binário proprietário: [version 4B][len 4B][inner_zip][perms_xml]
  DataModel   → banco SSAS comprimido (preservado se .pbix já existe)
  Report/Layout, Version, Settings, Metadata → estrutura mínima se criado novo
"""

import sys, os, io, re, struct, zipfile, json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── caminhos ──────────────────────────────────────────────────────────────────

PQ_FILE   = r"C:\inteligencia_mercado\03_powerbi\modelo_powerquery.pq"
PBIX_FILE = r"C:\inteligencia_mercado\03_powerbi\sc_comercial.pbix"
BASE_URL  = (
    "https://raw.githubusercontent.com/pedrocorrea12/"
    "sc-comercial-analytics/master/02_dados_tratados/modelo/"
)

SEP = "=" * 70

# ── 1. parse do .pq ───────────────────────────────────────────────────────────

def parse_queries(pq_text: str) -> list[tuple[str, str]]:
    """
    Extrai (nome, código_M) para cada bloco marcado com '// Consulta: NAME'.
    Retorna lista ordenada: BaseURL primeiro, depois os 10 blocos do .pq.
    """
    queries = []

    # Parâmetro BaseURL — extraído do comentário de valor
    m = re.search(r'//\s*Valor:\s*(https?://\S+)', pq_text)
    base_url = m.group(1).strip() if m else BASE_URL
    queries.append(('BaseURL', base_url))

    # Todos os blocos com marcador '// Consulta: NAME'
    pattern = re.compile(
        r'//\s*Consulta:\s*(\S+)\s*\n'   # marcador
        r'(.*?)'                          # código M (lazy)
        r'(?=\n\s*//\s*[─=]|\Z)',        # até próximo separador ou fim
        re.DOTALL
    )
    for m in pattern.finditer(pq_text):
        name = m.group(1).strip()
        code = m.group(2).strip()
        queries.append((name, code))

    return queries


# ── 2. Section1.m ─────────────────────────────────────────────────────────────

PARAM_META = (
    'meta [IsParameterQuery=true, Type="Text", '
    'IsParameterQueryRequired=true]'
)

def build_section1(queries: list[tuple[str, str]]) -> str:
    lines = ['section Section1;', '']
    for name, code in queries:
        if name == 'BaseURL':
            lines.append(f'shared {name} = "{code}" {PARAM_META};')
        else:
            # code já é expressão M completa (let...in ou lambda)
            lines.append(f'shared {name} =')
            lines.append(code + ';')
        lines.append('')
    return '\n'.join(lines)


# ── 3. DataMashup binary ──────────────────────────────────────────────────────

PACKAGE_XML = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<Package xmlns="http://schemas.microsoft.com/DataMashup" '
    'Permissions="" AllowedPrivacyLevels="" />'
)

PERMS_XML = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b'<Permissions xmlns="http://schemas.microsoft.com/DataMashup" />'
)

def build_data_mashup(section1_m: str) -> bytes:
    """
    DataMashup = [version: 4B LE] [inner_zip_len: 4B LE]
                 [inner_zip] [perms_xml]

    inner_zip contem:
      Config/Package.xml
      Formulas/Section1.m
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('Config/Package.xml',
                    PACKAGE_XML.encode('utf-8'))
        zf.writestr('Formulas/Section1.m',
                    section1_m.encode('utf-8'))
    inner = buf.getvalue()

    version = struct.pack('<I', 6)
    zip_len = struct.pack('<I', len(inner))
    return version + zip_len + inner + PERMS_XML


# ── 4. manipulação do .pbix ───────────────────────────────────────────────────

# Estrutura mínima para .pbix novo
CONTENT_TYPES = """\
<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels"
    ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Override PartName="/DataMashup"
    ContentType="application/octet-stream"/>
  <Override PartName="/DataModel"
    ContentType="application/octet-stream"/>
  <Override PartName="/Report/Layout"
    ContentType="application/json; charset=utf-8"/>
  <Override PartName="/Version"
    ContentType="application/vnd.openxmlformats-officedocument.custom-properties+xml"/>
  <Override PartName="/Settings"
    ContentType="application/json; charset=utf-8"/>
  <Override PartName="/Metadata"
    ContentType="application/json; charset=utf-8"/>
  <Override PartName="/DiagramState"
    ContentType="application/json; charset=utf-8"/>
</Types>"""

RELS = """\
<?xml version="1.0" encoding="utf-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.microsoft.com/DataMashup"
    Target="DataMashup"/>
  <Relationship Id="rId2"
    Type="http://schemas.microsoft.com/power-bi/DataModel"
    Target="DataModel"/>
  <Relationship Id="rId3"
    Type="http://schemas.microsoft.com/power-bi/ReportLayout"
    Target="Report/Layout"/>
</Relationships>"""

REPORT_LAYOUT = json.dumps({
    "id": 0,
    "resourcePackages": [],
    "sections": [{
        "id": 0,
        "name": "ReportSection",
        "displayName": "Página 1",
        "filters": "[]",
        "ordinal": 0,
        "visualContainers": [],
        "config": "{}",
        "width": 1280,
        "height": 720
    }],
    "config": "{}",
    "layoutOptimization": 0
})

METADATA = json.dumps({
    "version": "4.0",
    "createdFrom": "PublishedDataset",
    "modifiedTime": "2026-05-20T00:00:00"
})

SETTINGS = json.dumps({"QueriesStatus": {}, "ReportSettings": {}})
DIAGRAM_STATE = json.dumps({"version": 0})
VERSION = "2.128.0.0"

# DataModel placeholder: Power BI Desktop regenera ao atualizar.
# É o mínimo necessário para o container ZIP ser válido.
# Bytes correspondem a um cabeçalho ABF (Analysis Services Backup) vazio.
MINIMAL_DATAMODEL = (
    b'\x00\x00\x00\x00'   # version placeholder
    b'\x00\x00\x00\x00'   # size placeholder
)


def inject_pbix(pbix_path: str, mashup: bytes) -> None:
    """Substitui DataMashup em .pbix existente, preservando todo o resto."""
    with zipfile.ZipFile(pbix_path, 'r') as zin:
        members = {name: zin.read(name) for name in zin.namelist()}

    members['DataMashup'] = mashup

    tmp = pbix_path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in members.items():
            zout.writestr(name, data)

    os.replace(tmp, pbix_path)


def create_pbix(pbix_path: str, mashup: bytes) -> None:
    """Cria novo .pbix com estrutura mínima e DataMashup injetado."""
    os.makedirs(os.path.dirname(pbix_path), exist_ok=True)
    with zipfile.ZipFile(pbix_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', CONTENT_TYPES.encode('utf-8'))
        zf.writestr('_rels/.rels',         RELS.encode('utf-8'))
        zf.writestr('DataMashup',          mashup)
        zf.writestr('DataModel',           MINIMAL_DATAMODEL)
        zf.writestr('Report/Layout',       REPORT_LAYOUT.encode('utf-8'))
        zf.writestr('Metadata',            METADATA.encode('utf-8'))
        zf.writestr('Settings',            SETTINGS.encode('utf-8'))
        zf.writestr('DiagramState',        DIAGRAM_STATE.encode('utf-8'))
        zf.writestr('Version',             VERSION.encode('utf-8'))


# ── 5. main ───────────────────────────────────────────────────────────────────

print(SEP)
print("  injetar_powerbi.py — SC Comercial Analytics")
print(SEP)

# Leitura do .pq
with open(PQ_FILE, encoding='utf-8') as f:
    pq_text = f.read()

# Parse
queries = parse_queries(pq_text)
print(f"\nConsultas extraídas ({len(queries)}):")
for i, (name, _) in enumerate(queries, 1):
    print(f"  {i:>2}. {name}")

# Section1.m
section1 = build_section1(queries)
print(f"\nSection1.m ({section1.count(chr(10))} linhas):")
print("-" * 70)
print(section1)
print("-" * 70)

# DataMashup
mashup = build_data_mashup(section1)
print(f"\nDataMashup gerado: {len(mashup):,} bytes")

# .pbix
if os.path.exists(PBIX_FILE):
    print(f"\n[MODO: INJETAR em .pbix existente]")
    print(f"  {PBIX_FILE}")
    inject_pbix(PBIX_FILE, mashup)
    print("  DataMashup substituido com sucesso.")
else:
    print(f"\n[MODO: CRIAR novo .pbix]")
    print(f"  {PBIX_FILE}")
    create_pbix(PBIX_FILE, mashup)
    print("  .pbix criado com estrutura minima.")
    print()
    print("  NOTA: Abra no Power BI Desktop e clique em 'Atualizar' para")
    print("  carregar o DataModel via Power Query (requer conexao com GitHub).")

size = os.path.getsize(PBIX_FILE)
print(f"\nArquivo salvo: {PBIX_FILE}")
print(f"Tamanho      : {size:,} bytes")

# Verifica integridade do ZIP gerado
with zipfile.ZipFile(PBIX_FILE, 'r') as z:
    members = z.namelist()
print(f"Entradas ZIP : {len(members)}")
for m in members:
    info = z.getinfo(m)
    print(f"  {m:<35} {info.file_size:>8,} B")

print(f"\n{SEP}")
print("  Concluido.")
print(SEP)
