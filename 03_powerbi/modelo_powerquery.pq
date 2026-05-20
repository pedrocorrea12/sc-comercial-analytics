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
//    Valor atual: https://raw.githubusercontent.com/pedrocorrea12/sc-comercial-analytics/master/02_dados_tratados/modelo/
// 3. Para cada bloco abaixo:
//    Nova consulta > Consulta em branco > Editor avançado > cole o código
// =============================================================================


// =============================================================================
// PARÂMETRO  BaseURL
// =============================================================================
// (criar via interface: Gerenciar parâmetros > Novo parâmetro)
// Nome : BaseURL
// Tipo : Texto
// Valor: https://raw.githubusercontent.com/pedrocorrea12/sc-comercial-analytics/master/02_dados_tratados/modelo/


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
// ─── dRegional ───────────────────────────────────────────────────────────────────
// Consulta: dRegional
let
    Fonte = fnCarregarCSV("dRegional.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"regional_id", Int64.Type},
        {"regional", type text}
    })
in
    Tipos

// ─── dCurso ───────────────────────────────────────────────────────────────────
// Consulta: dCurso
let
    Fonte = fnCarregarCSV("dCurso.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"curso_id", Int64.Type},
        {"curso", type text}
    })
in
    Tipos

// ─── dCanal ───────────────────────────────────────────────────────────────────
// Consulta: dCanal
let
    Fonte = fnCarregarCSV("dCanal.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"canal_id", Int64.Type},
        {"canal", type text}
    })
in
    Tipos

// ─── dStatus ───────────────────────────────────────────────────────────────────
// Consulta: dStatus
let
    Fonte = fnCarregarCSV("dStatus.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"status_id", Int64.Type},
        {"status", type text}
    })
in
    Tipos

// ─── dCalendario ───────────────────────────────────────────────────────────────────
// Consulta: dCalendario
let
    Fonte = fnCarregarCSV("dCalendario.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"data", type date},
        {"ano", Int64.Type},
        {"mes", Int64.Type},
        {"mes_nome", type text},
        {"trimestre", Int64.Type},
        {"semana", Int64.Type},
        {"dia_semana", Int64.Type},
        {"dia_semana_nome", type text},
        {"is_fim_de_semana", Int64.Type},
        {"ytd_flag", Int64.Type},
        {"mtd_flag", Int64.Type}
    })
in
    Tipos

// ─── fLeads ───────────────────────────────────────────────────────────────────
// Consulta: fLeads
let
    Fonte = fnCarregarCSV("fLeads.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"lead_id", Int64.Type},
        {"data_lead", type date},
        {"curso", type text},
        {"regional", type text},
        {"canal", type text},
        {"status_crm", type text},
        {"etapa", type text}
    })
in
    Tipos

// ─── fInscritos ───────────────────────────────────────────────────────────────────
// Consulta: fInscritos
let
    Fonte = fnCarregarCSV("fInscritos.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"inscrito_id", Int64.Type},
        {"lead_id", Int64.Type},
        {"data_inscricao", type date},
        {"curso", type text},
        {"regional", type text},
        {"etapa", type text}
    })
in
    Tipos

// ─── fPreMatriculas ───────────────────────────────────────────────────────────────────
// Consulta: fPreMatriculas
let
    Fonte = fnCarregarCSV("fPreMatriculas.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"pre_matricula_id", Int64.Type},
        {"inscrito_id", Int64.Type},
        {"lead_id", Int64.Type},
        {"data_pre_matricula", type date},
        {"etapa", type text}
    })
in
    Tipos

// ─── fMatriculas ───────────────────────────────────────────────────────────────────
// Consulta: fMatriculas
let
    Fonte = fnCarregarCSV("fMatriculas.csv"),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"matricula_id", Int64.Type},
        {"pre_matricula_id", Int64.Type},
        {"inscrito_id", Int64.Type},
        {"lead_id", Int64.Type},
        {"data_matricula", type date},
        {"valor_matricula", Decimal.Type},
        {"etapa", type text}
    })
in
    Tipos
