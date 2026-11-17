"""
============================================================
Modulo: DASHBOARD_STREAMLIT / estilos.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes simples para aplicar estilos modernos em dashboards Streamlit.
    O modulo centraliza tema visual, fontes, fundos, sidebar, metricas,
    tabelas, botoes, campos, abas e espacamentos usando CSS controlado.
Funcoes disponiveis:
    - aplicar_css()
    - aplicar_tema()
    - definir_cor_fundo()
    - definir_fonte_dashboard()
    - estilizar_sidebar()
    - estilizar_metricas()
    - estilizar_tabelas()
    - estilizar_botoes()
    - estilizar_campos()
    - estilizar_abas()
    - remover_espacamento_superior()
    - aplicar_estilo_moderno()
    - obter_estilo_atual()
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao das funcoes de tema e componentes.
        - Inclusao do estilo moderno completo.
============================================================
"""

# ----------------------------------------------------------------------------
# IMPORTACOES
# ----------------------------------------------------------------------------

# Importa Any para os retornos dos componentes Streamlit
from typing import Any

# Importa Streamlit para inserir as regras CSS na pagina
import streamlit as st

# Importa as constantes visuais compartilhadas pela biblioteca
try:
    from .constantes import (
        COR_BORDA,
        COR_FUNDO,
        COR_FUNDO_CARD,
        COR_FUNDO_SIDEBAR,
        COR_PRIMARIA,
        COR_TEXTO,
        COR_TEXTO_SECUNDARIO,
        FONTE_PADRAO,
        RAIOS_BORDA,
        SOMBRAS,
    )
except ImportError:
    from constantes import (
        COR_BORDA,
        COR_FUNDO,
        COR_FUNDO_CARD,
        COR_FUNDO_SIDEBAR,
        COR_PRIMARIA,
        COR_TEXTO,
        COR_TEXTO_SECUNDARIO,
        FONTE_PADRAO,
        RAIOS_BORDA,
        SOMBRAS,
    )


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

COR_SECUNDARIA_PADRAO = "#0F172A"
RAIO_PADRAO = RAIOS_BORDA["normal"]
SOMBRA_PADRAO = SOMBRAS["suave"]
ESPACAMENTO_SUPERIOR_MINIMO = 0.5

# Mantem a ultima configuracao aplicada pelo modulo
_ESTILO_ATUAL: dict[str, Any] = {}


# ----------------------------------------------------------------------------
# EXCECOES
# ----------------------------------------------------------------------------

class DashboardEstilosError(Exception):
    """Erro base para operacoes de estilo do dashboard."""


class CorEstiloInvalidaError(DashboardEstilosError, ValueError):
    """Indica que uma cor informada possui formato invalido."""


class ConfiguracaoEstiloInvalidaError(DashboardEstilosError, ValueError):
    """Indica que uma configuracao visual possui valor invalido."""


class CSSInvalidoError(DashboardEstilosError, ValueError):
    """Indica que um bloco CSS esta vazio ou possui tipo invalido."""


# ----------------------------------------------------------------------------
# VALIDACOES INTERNAS
# ----------------------------------------------------------------------------

def _validar_booleano(valor: bool, nome: str) -> bool:
    """
    Valida estritamente um parametro booleano.

    Args:
        valor (bool): Valor que sera validado.
        nome (str): Nome utilizado na mensagem de erro.

    Returns:
        bool: O proprio valor validado.

    Raises:
        TypeError: Caso o valor nao seja booleano.
    """
    if not isinstance(valor, bool):
        raise TypeError(f"O parametro '{nome}' deve ser booleano.")
    return valor


def _validar_texto(valor: str, nome: str) -> str:
    """
    Valida um texto obrigatorio.

    Args:
        valor (str): Texto que sera validado.
        nome (str): Nome utilizado na mensagem de erro.

    Returns:
        str: Texto sem espacos externos.

    Raises:
        ConfiguracaoEstiloInvalidaError: Caso o texto seja invalido.
    """
    if not isinstance(valor, str) or not valor.strip():
        raise ConfiguracaoEstiloInvalidaError(
            f"O parametro '{nome}' deve ser uma string preenchida."
        )
    return valor.strip()


def _validar_numero(
    valor: int | float,
    nome: str,
    minimo: float,
    maximo: float
) -> float:
    """
    Valida um numero dentro dos limites definidos.

    Args:
        valor (int | float): Numero que sera validado.
        nome (str): Nome utilizado na mensagem de erro.
        minimo (float): Menor valor permitido.
        maximo (float): Maior valor permitido.

    Returns:
        float: Numero convertido para float.

    Raises:
        ConfiguracaoEstiloInvalidaError: Caso o valor seja invalido.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ConfiguracaoEstiloInvalidaError(
            f"O parametro '{nome}' deve ser numerico."
        )
    numero = float(valor)
    if not minimo <= numero <= maximo:
        raise ConfiguracaoEstiloInvalidaError(
            f"O parametro '{nome}' deve estar entre {minimo} e {maximo}."
        )
    return numero


def _normalizar_cor(cor: str, nome: str = "cor") -> str:
    """
    Valida uma cor hexadecimal de tres, seis ou oito caracteres.

    Args:
        cor (str): Cor hexadecimal que sera validada.
        nome (str): Nome utilizado na mensagem de erro.

    Returns:
        str: Cor normalizada em letras maiusculas.

    Raises:
        CorEstiloInvalidaError: Caso a cor possua formato invalido.
    """
    if not isinstance(cor, str):
        raise CorEstiloInvalidaError(
            f"O parametro '{nome}' deve ser uma string hexadecimal."
        )

    codigo = cor.strip().lstrip("#")
    if len(codigo) not in {3, 6, 8} or any(
        caractere.upper() not in "0123456789ABCDEF"
        for caractere in codigo
    ):
        raise CorEstiloInvalidaError(
            f"O parametro '{nome}' deve possuir uma cor hexadecimal valida."
        )
    return f"#{codigo.upper()}"


def _registrar_estilo(nome: str, configuracao: dict[str, Any]) -> None:
    """
    Registra uma configuracao visual aplicada.

    Args:
        nome (str): Identificador da configuracao.
        configuracao (dict[str, Any]): Valores que foram aplicados.

    Returns:
        None: A funcao nao possui valor de retorno.

    Raises:
        ConfiguracaoEstiloInvalidaError: Caso nome seja invalido.
    """
    chave = _validar_texto(nome, "nome")
    _ESTILO_ATUAL[chave] = dict(configuracao)


# ----------------------------------------------------------------------------
# APLICACAO DE CSS E TEMA
# ----------------------------------------------------------------------------

def aplicar_css(css: str) -> Any:
    """
    Aplica um bloco CSS controlado no dashboard.

    Args:
        css (str): Regras CSS sem a tag style.

    Returns:
        Any: Resultado retornado pelo Streamlit.

    Raises:
        CSSInvalidoError: Caso o CSS esteja vazio ou possua tipo invalido.
    """
    if not isinstance(css, str) or not css.strip():
        raise CSSInvalidoError("O bloco CSS deve ser uma string preenchida.")

    codigo = f"<style>{css.strip()}</style>"

    # st.html trata CSS puro sem ocupar espaco; fallback mantem compatibilidade.
    if callable(getattr(st, "html", None)):
        return st.html(codigo)

    return st.markdown(codigo, unsafe_allow_html=True)


def aplicar_tema(
    cor_primaria: str = COR_PRIMARIA,
    cor_secundaria: str = COR_SECUNDARIA_PADRAO,
    cor_fundo: str = COR_FUNDO,
    cor_fundo_card: str = COR_FUNDO_CARD,
    cor_texto: str = COR_TEXTO,
    cor_texto_secundario: str = COR_TEXTO_SECUNDARIO,
    cor_borda: str = COR_BORDA,
    fonte: str = FONTE_PADRAO,
    raio_borda: int | float = RAIO_PADRAO
) -> Any:
    """
    Aplica as variaveis e regras globais do tema visual.

    Args:
        cor_primaria (str): Cor de destaque e interacao.
        cor_secundaria (str): Cor secundaria do tema.
        cor_fundo (str): Cor de fundo da aplicacao.
        cor_fundo_card (str): Cor de fundo de cards e containers.
        cor_texto (str): Cor principal dos textos.
        cor_texto_secundario (str): Cor dos textos auxiliares.
        cor_borda (str): Cor padrao de bordas.
        fonte (str): Familia tipografica CSS.
        raio_borda (int | float): Arredondamento padrao em pixels.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    primaria = _normalizar_cor(cor_primaria, "cor_primaria")
    secundaria = _normalizar_cor(cor_secundaria, "cor_secundaria")
    fundo = _normalizar_cor(cor_fundo, "cor_fundo")
    fundo_card = _normalizar_cor(cor_fundo_card, "cor_fundo_card")
    texto = _normalizar_cor(cor_texto, "cor_texto")
    texto_secundario = _normalizar_cor(
        cor_texto_secundario,
        "cor_texto_secundario"
    )
    borda = _normalizar_cor(cor_borda, "cor_borda")
    fonte_validada = _validar_texto(fonte, "fonte")
    raio = _validar_numero(raio_borda, "raio_borda", 0, 100)

    configuracao = {
        "cor_primaria": primaria,
        "cor_secundaria": secundaria,
        "cor_fundo": fundo,
        "cor_fundo_card": fundo_card,
        "cor_texto": texto,
        "cor_texto_secundario": texto_secundario,
        "cor_borda": borda,
        "fonte": fonte_validada,
        "raio_borda": raio
    }
    _registrar_estilo("tema", configuracao)

    return aplicar_css(f"""
:root {{
    --dashboard-primary: {primaria};
    --dashboard-secondary: {secundaria};
    --dashboard-background: {fundo};
    --dashboard-card: {fundo_card};
    --dashboard-text: {texto};
    --dashboard-muted: {texto_secundario};
    --dashboard-border: {borda};
    --dashboard-radius: {raio:g}px;
}}
html, body, [class*="st-"] {{
    font-family: {fonte_validada};
}}
[data-testid="stAppViewContainer"] {{
    background: {fundo};
    color: {texto};
}}
[data-testid="stMainBlockContainer"] {{
    color: {texto};
}}
a {{ color: {primaria}; }}
hr {{ border-color: {borda}; }}
""")


def definir_cor_fundo(
    cor: str = COR_FUNDO,
    incluir_sidebar: bool = False
) -> Any:
    """
    Define a cor de fundo da pagina e opcionalmente da sidebar.

    Args:
        cor (str): Cor hexadecimal do fundo.
        incluir_sidebar (bool): Aplica a mesma cor na barra lateral.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso cor ou opcao sejam invalidas.
    """
    fundo = _normalizar_cor(cor)
    _validar_booleano(incluir_sidebar, "incluir_sidebar")
    regra_sidebar = (
        f'[data-testid="stSidebar"] {{background: {fundo};}}'
        if incluir_sidebar
        else ""
    )
    _registrar_estilo(
        "fundo",
        {"cor": fundo, "incluir_sidebar": incluir_sidebar}
    )
    return aplicar_css(
        f'[data-testid="stAppViewContainer"] {{background: {fundo};}}'
        f'{regra_sidebar}'
    )


def definir_fonte_dashboard(
    fonte: str = FONTE_PADRAO,
    tamanho_base: int | float = 16
) -> Any:
    """
    Define a familia e o tamanho tipografico base.

    Args:
        fonte (str): Familia tipografica CSS.
        tamanho_base (int | float): Tamanho base entre 10 e 28 pixels.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        ConfiguracaoEstiloInvalidaError: Caso os valores sejam invalidos.
    """
    fonte_validada = _validar_texto(fonte, "fonte")
    tamanho = _validar_numero(tamanho_base, "tamanho_base", 10, 28)
    _registrar_estilo(
        "fonte",
        {"fonte": fonte_validada, "tamanho_base": tamanho}
    )
    return aplicar_css(f"""
html, body, [class*="st-"] {{
    font-family: {fonte_validada};
    font-size: {tamanho:g}px;
}}
""")


# ----------------------------------------------------------------------------
# ESTILOS DE COMPONENTES
# ----------------------------------------------------------------------------

def estilizar_sidebar(
    cor_fundo: str = COR_FUNDO_SIDEBAR,
    cor_texto: str = COR_TEXTO,
    cor_borda: str = COR_BORDA,
    largura: int | float = 320
) -> Any:
    """
    Aplica cores, borda e largura na barra lateral.

    Args:
        cor_fundo (str): Cor de fundo da sidebar.
        cor_texto (str): Cor dos textos da sidebar.
        cor_borda (str): Cor da divisao lateral.
        largura (int | float): Largura entre 220 e 600 pixels.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    fundo = _normalizar_cor(cor_fundo, "cor_fundo")
    texto = _normalizar_cor(cor_texto, "cor_texto")
    borda = _normalizar_cor(cor_borda, "cor_borda")
    largura_validada = _validar_numero(largura, "largura", 220, 600)
    _registrar_estilo(
        "sidebar",
        {
            "cor_fundo": fundo,
            "cor_texto": texto,
            "cor_borda": borda,
            "largura": largura_validada
        }
    )
    return aplicar_css(f"""
[data-testid="stSidebar"] {{
    background: {fundo};
    border-right: 1px solid {borda};
    min-width: {largura_validada:g}px;
    max-width: {largura_validada:g}px;
}}
[data-testid="stSidebar"] * {{ color: {texto}; }}
""")


def estilizar_metricas(
    cor_fundo: str = COR_FUNDO_CARD,
    cor_valor: str = COR_TEXTO,
    cor_rotulo: str = COR_TEXTO_SECUNDARIO,
    cor_borda: str = COR_BORDA,
    raio_borda: int | float = RAIOS_BORDA["grande"],
    sombra: bool = True
) -> Any:
    """
    Estiliza os componentes nativos st.metric.

    Args:
        cor_fundo (str): Cor de fundo das metricas.
        cor_valor (str): Cor do valor principal.
        cor_rotulo (str): Cor do rotulo e textos auxiliares.
        cor_borda (str): Cor da borda.
        raio_borda (int | float): Arredondamento em pixels.
        sombra (bool): Define se uma sombra suave sera aplicada.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    fundo = _normalizar_cor(cor_fundo, "cor_fundo")
    valor = _normalizar_cor(cor_valor, "cor_valor")
    rotulo = _normalizar_cor(cor_rotulo, "cor_rotulo")
    borda = _normalizar_cor(cor_borda, "cor_borda")
    raio = _validar_numero(raio_borda, "raio_borda", 0, 100)
    _validar_booleano(sombra, "sombra")
    box_shadow = SOMBRA_PADRAO if sombra else "none"
    _registrar_estilo(
        "metricas",
        {
            "cor_fundo": fundo,
            "cor_valor": valor,
            "cor_rotulo": rotulo,
            "cor_borda": borda,
            "raio_borda": raio,
            "sombra": sombra
        }
    )
    return aplicar_css(f"""
[data-testid="stMetric"] {{
    background: {fundo};
    border: 1px solid {borda};
    border-radius: {raio:g}px;
    padding: 1rem 1.1rem;
    box-shadow: {box_shadow};
}}
[data-testid="stMetricValue"] {{ color: {valor}; font-weight: 750; }}
[data-testid="stMetricLabel"] {{ color: {rotulo}; font-weight: 600; }}
""")


def estilizar_tabelas(
    cor_cabecalho: str = COR_PRIMARIA,
    cor_texto_cabecalho: str = "#FFFFFF",
    cor_borda: str = COR_BORDA,
    raio_borda: int | float = RAIO_PADRAO
) -> Any:
    """
    Estiliza dataframes, tabelas e editores de dados.

    Args:
        cor_cabecalho (str): Cor do cabecalho da tabela.
        cor_texto_cabecalho (str): Cor do texto do cabecalho.
        cor_borda (str): Cor externa da tabela.
        raio_borda (int | float): Arredondamento em pixels.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    cabecalho = _normalizar_cor(cor_cabecalho, "cor_cabecalho")
    texto = _normalizar_cor(cor_texto_cabecalho, "cor_texto_cabecalho")
    borda = _normalizar_cor(cor_borda, "cor_borda")
    raio = _validar_numero(raio_borda, "raio_borda", 0, 100)
    _registrar_estilo(
        "tabelas",
        {
            "cor_cabecalho": cabecalho,
            "cor_texto_cabecalho": texto,
            "cor_borda": borda,
            "raio_borda": raio
        }
    )
    return aplicar_css(f"""
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
    border: 1px solid {borda};
    border-radius: {raio:g}px;
    overflow: hidden;
}}
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataEditor"] [role="columnheader"] {{
    background: {cabecalho};
    color: {texto};
    font-weight: 650;
}}
""")


def estilizar_botoes(
    cor_primaria: str = COR_PRIMARIA,
    cor_texto: str = "#FFFFFF",
    raio_borda: int | float = RAIO_PADRAO,
    altura: int | float = 42
) -> Any:
    """
    Estiliza botoes nativos da aplicacao.

    Args:
        cor_primaria (str): Cor de fundo dos botoes.
        cor_texto (str): Cor do texto dos botoes.
        raio_borda (int | float): Arredondamento em pixels.
        altura (int | float): Altura minima entre 30 e 80 pixels.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    primaria = _normalizar_cor(cor_primaria, "cor_primaria")
    texto = _normalizar_cor(cor_texto, "cor_texto")
    raio = _validar_numero(raio_borda, "raio_borda", 0, 100)
    altura_validada = _validar_numero(altura, "altura", 30, 80)
    _registrar_estilo(
        "botoes",
        {
            "cor_primaria": primaria,
            "cor_texto": texto,
            "raio_borda": raio,
            "altura": altura_validada
        }
    )
    return aplicar_css(f"""
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
    min-height: {altura_validada:g}px;
    border-radius: {raio:g}px;
    font-weight: 650;
}}
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"] {{
    background: {primaria};
    color: {texto};
    border-color: {primaria};
}}
""")


def estilizar_campos(
    cor_fundo: str = COR_FUNDO_CARD,
    cor_borda: str = COR_BORDA,
    cor_foco: str = COR_PRIMARIA,
    raio_borda: int | float = RAIO_PADRAO
) -> Any:
    """
    Estiliza inputs, seletores e areas de texto.

    Args:
        cor_fundo (str): Cor de fundo dos campos.
        cor_borda (str): Cor normal das bordas.
        cor_foco (str): Cor aplicada durante o foco.
        raio_borda (int | float): Arredondamento em pixels.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    fundo = _normalizar_cor(cor_fundo, "cor_fundo")
    borda = _normalizar_cor(cor_borda, "cor_borda")
    foco = _normalizar_cor(cor_foco, "cor_foco")
    raio = _validar_numero(raio_borda, "raio_borda", 0, 100)
    _registrar_estilo(
        "campos",
        {
            "cor_fundo": fundo,
            "cor_borda": borda,
            "cor_foco": foco,
            "raio_borda": raio
        }
    )
    return aplicar_css(f"""
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] > div {{
    background: {fundo};
    border-color: {borda};
    border-radius: {raio:g}px;
}}
[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within {{
    border-color: {foco};
    box-shadow: 0 0 0 1px {foco};
}}
""")


def estilizar_abas(
    cor_ativa: str = COR_PRIMARIA,
    cor_texto: str = COR_TEXTO_SECUNDARIO,
    raio_borda: int | float = RAIO_PADRAO
) -> Any:
    """
    Estiliza as abas nativas do Streamlit.

    Args:
        cor_ativa (str): Cor da aba selecionada.
        cor_texto (str): Cor das abas nao selecionadas.
        raio_borda (int | float): Arredondamento superior das abas.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    ativa = _normalizar_cor(cor_ativa, "cor_ativa")
    texto = _normalizar_cor(cor_texto, "cor_texto")
    raio = _validar_numero(raio_borda, "raio_borda", 0, 100)
    _registrar_estilo(
        "abas",
        {"cor_ativa": ativa, "cor_texto": texto, "raio_borda": raio}
    )
    return aplicar_css(f"""
.stTabs [data-baseweb="tab-list"] {{ gap: 0.35rem; }}
.stTabs [data-baseweb="tab"] {{
    color: {texto};
    border-radius: {raio:g}px {raio:g}px 0 0;
    padding: 0.65rem 1rem;
}}
.stTabs [aria-selected="true"] {{
    color: {ativa};
    font-weight: 700;
}}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: {ativa}; }}
""")


def remover_espacamento_superior(
    espacamento: int | float = ESPACAMENTO_SUPERIOR_MINIMO
) -> Any:
    """
    Reduz o espacamento superior da area principal.

    Args:
        espacamento (int | float): Espaco superior em rem, entre 0 e 10.

    Returns:
        Any: Resultado retornado pela aplicacao do CSS.

    Raises:
        ConfiguracaoEstiloInvalidaError: Caso o valor seja invalido.
    """
    valor = _validar_numero(espacamento, "espacamento", 0, 10)
    _registrar_estilo("espacamento_superior", {"espacamento": valor})
    return aplicar_css(
        f'[data-testid="stMainBlockContainer"] {{padding-top: {valor:g}rem;}}'
    )


# ----------------------------------------------------------------------------
# ESTILO COMPLETO E CONSULTA
# ----------------------------------------------------------------------------

def aplicar_estilo_moderno(
    cor_primaria: str = COR_PRIMARIA,
    cor_fundo: str = COR_FUNDO,
    fonte: str = FONTE_PADRAO,
    sidebar: bool = True,
    metricas: bool = True,
    tabelas: bool = True,
    botoes: bool = True,
    campos: bool = True,
    abas: bool = True,
    reduzir_espacamento: bool = True
) -> list[Any]:
    """
    Aplica em uma chamada o tema e os estilos mais usados.

    Args:
        cor_primaria (str): Cor central do dashboard.
        cor_fundo (str): Cor de fundo da aplicacao.
        fonte (str): Familia tipografica CSS.
        sidebar (bool): Define se a sidebar sera estilizada.
        metricas (bool): Define se metricas serao estilizadas.
        tabelas (bool): Define se tabelas serao estilizadas.
        botoes (bool): Define se botoes serao estilizados.
        campos (bool): Define se campos serao estilizados.
        abas (bool): Define se abas serao estilizadas.
        reduzir_espacamento (bool): Reduz o espaco superior da pagina.

    Returns:
        list[Any]: Resultados das regras CSS aplicadas.

    Raises:
        DashboardEstilosError: Caso alguma configuracao seja invalida.
    """
    for nome, valor in {
        "sidebar": sidebar,
        "metricas": metricas,
        "tabelas": tabelas,
        "botoes": botoes,
        "campos": campos,
        "abas": abas,
        "reduzir_espacamento": reduzir_espacamento
    }.items():
        _validar_booleano(valor, nome)

    primaria = _normalizar_cor(cor_primaria, "cor_primaria")
    fundo = _normalizar_cor(cor_fundo, "cor_fundo")
    fonte_validada = _validar_texto(fonte, "fonte")

    resultados: list[Any] = [
        aplicar_tema(
            cor_primaria=primaria,
            cor_fundo=fundo,
            fonte=fonte_validada
        )
    ]

    if sidebar:
        resultados.append(estilizar_sidebar())
    if metricas:
        resultados.append(estilizar_metricas())
    if tabelas:
        resultados.append(estilizar_tabelas(cor_cabecalho=primaria))
    if botoes:
        resultados.append(estilizar_botoes(cor_primaria=primaria))
    if campos:
        resultados.append(estilizar_campos(cor_foco=primaria))
    if abas:
        resultados.append(estilizar_abas(cor_ativa=primaria))
    if reduzir_espacamento:
        resultados.append(remover_espacamento_superior())

    _registrar_estilo(
        "moderno",
        {
            "cor_primaria": primaria,
            "cor_fundo": fundo,
            "fonte": fonte_validada,
            "sidebar": sidebar,
            "metricas": metricas,
            "tabelas": tabelas,
            "botoes": botoes,
            "campos": campos,
            "abas": abas,
            "reduzir_espacamento": reduzir_espacamento
        }
    )
    return resultados


def obter_estilo_atual() -> dict[str, Any]:
    """
    Retorna uma copia das configuracoes aplicadas pelo modulo.

    Args:
        Nenhum.

    Returns:
        dict[str, Any]: Copia do estado visual atual.

    Raises:
        DashboardEstilosError: Nunca e gerada no fluxo normal.
    """
    return {
        nome: dict(configuracao)
        for nome, configuracao in _ESTILO_ATUAL.items()
    }


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "COR_SECUNDARIA_PADRAO",
    "RAIO_PADRAO",
    "SOMBRA_PADRAO",
    "ESPACAMENTO_SUPERIOR_MINIMO",
    "DashboardEstilosError",
    "CorEstiloInvalidaError",
    "ConfiguracaoEstiloInvalidaError",
    "CSSInvalidoError",
    "aplicar_css",
    "aplicar_tema",
    "definir_cor_fundo",
    "definir_fonte_dashboard",
    "estilizar_sidebar",
    "estilizar_metricas",
    "estilizar_tabelas",
    "estilizar_botoes",
    "estilizar_campos",
    "estilizar_abas",
    "remover_espacamento_superior",
    "aplicar_estilo_moderno",
    "obter_estilo_atual"
]
