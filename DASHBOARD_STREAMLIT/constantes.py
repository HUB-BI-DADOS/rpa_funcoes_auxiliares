"""
============================================================
Modulo: DASHBOARD_STREAMLIT / constantes.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Constantes compartilhadas pelos modulos de dashboards Streamlit.
    O modulo centraliza cores, icones, tamanhos, espacamentos, formatos,
    configuracoes de pagina, estilos de graficos e valores semanticos.
Dependencias:
    - Nenhuma dependencia externa
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao das paletas de cores e icones semanticos.
        - Inclusao dos tamanhos, espacamentos e formatos padrao.
        - Inclusao das configuracoes de pagina, graficos e componentes.
============================================================
"""

# ----------------------------------------------------------------------------
# INFORMACOES DO MODULO
# ----------------------------------------------------------------------------

NOME_BIBLIOTECA = "DASHBOARD_STREAMLIT"
VERSAO_BIBLIOTECA = "1.0.0"


# ----------------------------------------------------------------------------
# CORES PRINCIPAIS
# ----------------------------------------------------------------------------

COR_PRIMARIA = "#2563EB"
COR_PRIMARIA_CLARA = "#DBEAFE"
COR_PRIMARIA_ESCURA = "#1D4ED8"

COR_SECUNDARIA = "#0F172A"
COR_SECUNDARIA_CLARA = "#334155"
COR_SECUNDARIA_ESCURA = "#020617"

COR_FUNDO = "#F8FAFC"
COR_FUNDO_CARD = "#FFFFFF"
COR_FUNDO_SIDEBAR = "#FFFFFF"

COR_TEXTO = "#0F172A"
COR_TEXTO_SECUNDARIO = "#64748B"
COR_TEXTO_CLARO = "#FFFFFF"
COR_TEXTO_DESABILITADO = "#94A3B8"

COR_BORDA = "#E2E8F0"
COR_BORDA_FORTE = "#CBD5E1"
COR_DIVISOR = "#E2E8F0"

COR_SUCESSO = "#16A34A"
COR_SUCESSO_CLARA = "#DCFCE7"
COR_ALERTA = "#D97706"
COR_ALERTA_CLARA = "#FEF3C7"
COR_ERRO = "#DC2626"
COR_ERRO_CLARA = "#FEE2E2"
COR_INFORMACAO = "#2563EB"
COR_INFORMACAO_CLARA = "#DBEAFE"
COR_NEUTRA = "#64748B"
COR_NEUTRA_CLARA = "#F1F5F9"


# ----------------------------------------------------------------------------
# PALETAS
# ----------------------------------------------------------------------------

CORES_STATUS = {
    "informacao": COR_INFORMACAO,
    "sucesso": COR_SUCESSO,
    "alerta": COR_ALERTA,
    "erro": COR_ERRO,
    "neutro": COR_NEUTRA,
    "pendente": "#F59E0B",
    "em_andamento": "#3B82F6",
    "concluido": "#10B981",
    "atrasado": "#EF4444",
    "cancelado": "#6B7280"
}

CORES_STATUS_CLARAS = {
    "informacao": COR_INFORMACAO_CLARA,
    "sucesso": COR_SUCESSO_CLARA,
    "alerta": COR_ALERTA_CLARA,
    "erro": COR_ERRO_CLARA,
    "neutro": COR_NEUTRA_CLARA,
    "pendente": "#FEF3C7",
    "em_andamento": "#DBEAFE",
    "concluido": "#D1FAE5",
    "atrasado": "#FEE2E2",
    "cancelado": "#F3F4F6"
}

CORES_GRAFICOS = [
    "#2563EB",
    "#16A34A",
    "#D97706",
    "#DC2626",
    "#7C3AED",
    "#0891B2",
    "#DB2777",
    "#65A30D",
    "#EA580C",
    "#475569"
]

CORES_GRAFICOS_PASTEIS = [
    "#93C5FD",
    "#86EFAC",
    "#FCD34D",
    "#FCA5A5",
    "#C4B5FD",
    "#67E8F9",
    "#F9A8D4",
    "#BEF264",
    "#FDBA74",
    "#CBD5E1"
]

CORES_MONOCROMATICAS_AZUIS = [
    "#DBEAFE",
    "#BFDBFE",
    "#93C5FD",
    "#60A5FA",
    "#3B82F6",
    "#2563EB",
    "#1D4ED8",
    "#1E40AF"
]


# ----------------------------------------------------------------------------
# ICONES
# ----------------------------------------------------------------------------

ICONES_STATUS = {
    "informacao": "ℹ️",
    "sucesso": "✓",
    "alerta": "⚠️",
    "erro": "✕",
    "neutro": "•",
    "pendente": "⏳",
    "em_andamento": "⚙️",
    "concluido": "✅",
    "atrasado": "⏰",
    "cancelado": "🚫"
}

ICONES_ACOES = {
    "adicionar": "➕",
    "editar": "✏️",
    "excluir": "🗑️",
    "salvar": "💾",
    "cancelar": "✕",
    "atualizar": "🔄",
    "buscar": "🔍",
    "filtrar": "🔽",
    "limpar": "🧹",
    "baixar": "⬇️",
    "enviar": "📤",
    "voltar": "⬅️",
    "avancar": "➡️",
    "configurar": "⚙️"
}

ICONES_DASHBOARD = {
    "dashboard": "📊",
    "grafico": "📈",
    "tabela": "📋",
    "filtro": "🔽",
    "calendario": "📅",
    "usuario": "👤",
    "usuarios": "👥",
    "pedido": "📦",
    "transporte": "🚚",
    "dinheiro": "💰",
    "tempo": "🕒",
    "localizacao": "📍",
    "notificacao": "🔔",
    "documento": "📄",
    "banco_dados": "🗄️"
}

ICONES_MATERIAL = {
    "dashboard": ":material/dashboard:",
    "grafico": ":material/monitoring:",
    "tabela": ":material/table_view:",
    "filtro": ":material/filter_alt:",
    "configuracao": ":material/settings:",
    "inicio": ":material/home:",
    "usuario": ":material/person:",
    "usuarios": ":material/groups:",
    "buscar": ":material/search:",
    "atualizar": ":material/refresh:",
    "baixar": ":material/download:",
    "adicionar": ":material/add:",
    "editar": ":material/edit:",
    "excluir": ":material/delete:"
}


# ----------------------------------------------------------------------------
# TIPOGRAFIA
# ----------------------------------------------------------------------------

FONTE_PADRAO = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
FONTE_MONOESPACADA = "'JetBrains Mono', 'Fira Code', monospace"

TAMANHOS_TEXTO = {
    "muito_pequeno": "0.70rem",
    "pequeno": "0.80rem",
    "normal": "0.95rem",
    "medio": "1.10rem",
    "grande": "1.35rem",
    "titulo_secao": "1.55rem",
    "titulo_pagina": "2.00rem",
    "valor_card": "1.75rem",
    "valor_kpi": "2.10rem"
}

PESOS_FONTE = {
    "leve": 300,
    "normal": 400,
    "medio": 500,
    "seminegrito": 600,
    "negrito": 700,
    "extranegrito": 800
}


# ----------------------------------------------------------------------------
# ESPACAMENTOS E DIMENSOES
# ----------------------------------------------------------------------------

ESPACAMENTOS = {
    "zero": "0",
    "muito_pequeno": "0.25rem",
    "pequeno": "0.50rem",
    "normal": "1.00rem",
    "medio": "1.50rem",
    "grande": "2.00rem",
    "muito_grande": "3.00rem"
}

ESPACAMENTOS_COLUNAS_VALIDOS = {
    "small",
    "medium",
    "large"
}

RAIOS_BORDA = {
    "pequeno": 8,
    "normal": 12,
    "grande": 16,
    "muito_grande": 24,
    "circular": 999
}

ALTURA_CARD_PADRAO = 132
ALTURA_CARD_INFORMACAO = 150
ALTURA_TABELA_PADRAO = 500
ALTURA_GRAFICO_PADRAO = 420
LARGURA_MAXIMA_DASHBOARD = 1600
QUANTIDADE_MAXIMA_COLUNAS = 6

SOMBRAS = {
    "nenhuma": "none",
    "suave": "0 4px 18px rgba(15, 23, 42, 0.07)",
    "normal": "0 8px 24px rgba(15, 23, 42, 0.10)",
    "forte": "0 12px 32px rgba(15, 23, 42, 0.16)"
}


# ----------------------------------------------------------------------------
# CONFIGURACAO DA PAGINA
# ----------------------------------------------------------------------------

TITULO_PAGINA_PADRAO = "Dashboard"
ICONE_PAGINA_PADRAO = "📊"
LAYOUT_PAGINA_PADRAO = "wide"
ESTADO_SIDEBAR_PADRAO = "expanded"

LAYOUTS_PAGINA_VALIDOS = {"wide", "centered"}
ESTADOS_SIDEBAR_VALIDOS = {
    "auto",
    "expanded",
    "collapsed",
    "locked"
}

POSICOES_NAVEGACAO_VALIDAS = {
    "sidebar",
    "top",
    "hidden"
}


# ----------------------------------------------------------------------------
# FORMATOS DE VALORES
# ----------------------------------------------------------------------------

FORMATO_NUMERO_INTEIRO = "{:,.0f}"
FORMATO_NUMERO_DECIMAL = "{:,.2f}"
FORMATO_PERCENTUAL = "{:.1%}"
FORMATO_MOEDA_REAL = "R$ {:,.2f}"
FORMATO_MOEDA_DOLAR = "US$ {:,.2f}"

FORMATOS_NUMERICOS = {
    "inteiro": FORMATO_NUMERO_INTEIRO,
    "decimal": FORMATO_NUMERO_DECIMAL,
    "percentual": FORMATO_PERCENTUAL,
    "moeda_real": FORMATO_MOEDA_REAL,
    "moeda_dolar": FORMATO_MOEDA_DOLAR
}

FORMATO_DATA_BR = "%d/%m/%Y"
FORMATO_DATA_HORA_BR = "%d/%m/%Y %H:%M"
FORMATO_HORA = "%H:%M:%S"
FORMATO_DATA_ISO = "%Y-%m-%d"

FORMATOS_DATA = {
    "data_br": FORMATO_DATA_BR,
    "data_hora_br": FORMATO_DATA_HORA_BR,
    "hora": FORMATO_HORA,
    "data_iso": FORMATO_DATA_ISO
}

SUFIXOS_NUMERO_COMPACTO = {
    1_000: "mil",
    1_000_000: "mi",
    1_000_000_000: "bi",
    1_000_000_000_000: "tri"
}


# ----------------------------------------------------------------------------
# GRAFICOS
# ----------------------------------------------------------------------------

TEMPLATE_GRAFICO_PADRAO = "plotly_white"
FONTE_GRAFICO_PADRAO = "Inter"
POSICAO_LEGENDA_PADRAO = "top"

POSICOES_LEGENDA_VALIDAS = {
    "top",
    "bottom",
    "left",
    "right",
    "none"
}

ORIENTACOES_GRAFICO_VALIDAS = {
    "vertical",
    "horizontal"
}

ORDENACOES_VALIDAS = {
    "crescente",
    "decrescente",
    "nenhuma"
}

CONFIGURACAO_GRAFICO_PADRAO = {
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False
}

MARGENS_GRAFICO_PADRAO = {
    "l": 20,
    "r": 20,
    "t": 60,
    "b": 20
}


# ----------------------------------------------------------------------------
# TABELAS E DATAFRAMES
# ----------------------------------------------------------------------------

ALTURA_DATAFRAME_PADRAO = 500
OCULTAR_INDICE_PADRAO = True
USAR_LARGURA_TOTAL_PADRAO = True

TIPOS_FORMATACAO_COLUNA = {
    "texto",
    "inteiro",
    "decimal",
    "moeda",
    "percentual",
    "data",
    "data_hora",
    "booleano",
    "link",
    "imagem",
    "progresso"
}


# ----------------------------------------------------------------------------
# FILTROS E FORMULARIOS
# ----------------------------------------------------------------------------

TIPOS_FILTRO = {
    "selecao",
    "multisselecao",
    "data",
    "periodo",
    "numero",
    "intervalo_numerico",
    "texto",
    "booleano"
}

TIPOS_CAMPO = {
    "texto",
    "texto_longo",
    "numero",
    "data",
    "hora",
    "selecao",
    "multisselecao",
    "booleano",
    "arquivo"
}

TEXTO_OPCAO_TODOS = "Todos"
TEXTO_FILTROS = "Filtros"
TEXTO_LIMPAR_FILTROS = "Limpar filtros"
TEXTO_APLICAR_FILTROS = "Aplicar filtros"


# ----------------------------------------------------------------------------
# MENSAGENS PADRAO
# ----------------------------------------------------------------------------

MENSAGENS_PADRAO = {
    "sem_dados": "Nenhum dado disponível para exibição.",
    "sem_resultados": "Nenhum registro encontrado para os filtros selecionados.",
    "carregando": "Carregando informações...",
    "processando": "Processando dados...",
    "sucesso": "Operação realizada com sucesso.",
    "erro": "Não foi possível concluir a operação.",
    "atualizado": "Dados atualizados com sucesso.",
    "selecione_filtros": "Selecione os filtros para continuar."
}


# ----------------------------------------------------------------------------
# CACHE
# ----------------------------------------------------------------------------

TEXTO_CACHE_DADOS = "Carregando dados..."
TEXTO_CACHE_RECURSO = "Inicializando recurso..."
EXPIRACAO_CACHE_PADRAO = None
MAXIMO_ENTRADAS_CACHE_PADRAO = None
PERSISTIR_CACHE_DADOS_PADRAO = False


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "NOME_BIBLIOTECA",
    "VERSAO_BIBLIOTECA",
    "COR_PRIMARIA",
    "COR_PRIMARIA_CLARA",
    "COR_PRIMARIA_ESCURA",
    "COR_SECUNDARIA",
    "COR_SECUNDARIA_CLARA",
    "COR_SECUNDARIA_ESCURA",
    "COR_FUNDO",
    "COR_FUNDO_CARD",
    "COR_FUNDO_SIDEBAR",
    "COR_TEXTO",
    "COR_TEXTO_SECUNDARIO",
    "COR_TEXTO_CLARO",
    "COR_TEXTO_DESABILITADO",
    "COR_BORDA",
    "COR_BORDA_FORTE",
    "COR_DIVISOR",
    "COR_SUCESSO",
    "COR_SUCESSO_CLARA",
    "COR_ALERTA",
    "COR_ALERTA_CLARA",
    "COR_ERRO",
    "COR_ERRO_CLARA",
    "COR_INFORMACAO",
    "COR_INFORMACAO_CLARA",
    "COR_NEUTRA",
    "COR_NEUTRA_CLARA",
    "CORES_STATUS",
    "CORES_STATUS_CLARAS",
    "CORES_GRAFICOS",
    "CORES_GRAFICOS_PASTEIS",
    "CORES_MONOCROMATICAS_AZUIS",
    "ICONES_STATUS",
    "ICONES_ACOES",
    "ICONES_DASHBOARD",
    "ICONES_MATERIAL",
    "FONTE_PADRAO",
    "FONTE_MONOESPACADA",
    "TAMANHOS_TEXTO",
    "PESOS_FONTE",
    "ESPACAMENTOS",
    "ESPACAMENTOS_COLUNAS_VALIDOS",
    "RAIOS_BORDA",
    "ALTURA_CARD_PADRAO",
    "ALTURA_CARD_INFORMACAO",
    "ALTURA_TABELA_PADRAO",
    "ALTURA_GRAFICO_PADRAO",
    "LARGURA_MAXIMA_DASHBOARD",
    "QUANTIDADE_MAXIMA_COLUNAS",
    "SOMBRAS",
    "TITULO_PAGINA_PADRAO",
    "ICONE_PAGINA_PADRAO",
    "LAYOUT_PAGINA_PADRAO",
    "ESTADO_SIDEBAR_PADRAO",
    "LAYOUTS_PAGINA_VALIDOS",
    "ESTADOS_SIDEBAR_VALIDOS",
    "POSICOES_NAVEGACAO_VALIDAS",
    "FORMATO_NUMERO_INTEIRO",
    "FORMATO_NUMERO_DECIMAL",
    "FORMATO_PERCENTUAL",
    "FORMATO_MOEDA_REAL",
    "FORMATO_MOEDA_DOLAR",
    "FORMATOS_NUMERICOS",
    "FORMATO_DATA_BR",
    "FORMATO_DATA_HORA_BR",
    "FORMATO_HORA",
    "FORMATO_DATA_ISO",
    "FORMATOS_DATA",
    "SUFIXOS_NUMERO_COMPACTO",
    "TEMPLATE_GRAFICO_PADRAO",
    "FONTE_GRAFICO_PADRAO",
    "POSICAO_LEGENDA_PADRAO",
    "POSICOES_LEGENDA_VALIDAS",
    "ORIENTACOES_GRAFICO_VALIDAS",
    "ORDENACOES_VALIDAS",
    "CONFIGURACAO_GRAFICO_PADRAO",
    "MARGENS_GRAFICO_PADRAO",
    "ALTURA_DATAFRAME_PADRAO",
    "OCULTAR_INDICE_PADRAO",
    "USAR_LARGURA_TOTAL_PADRAO",
    "TIPOS_FORMATACAO_COLUNA",
    "TIPOS_FILTRO",
    "TIPOS_CAMPO",
    "TEXTO_OPCAO_TODOS",
    "TEXTO_FILTROS",
    "TEXTO_LIMPAR_FILTROS",
    "TEXTO_APLICAR_FILTROS",
    "MENSAGENS_PADRAO",
    "TEXTO_CACHE_DADOS",
    "TEXTO_CACHE_RECURSO",
    "EXPIRACAO_CACHE_PADRAO",
    "MAXIMO_ENTRADAS_CACHE_PADRAO",
    "PERSISTIR_CACHE_DADOS_PADRAO"
]
