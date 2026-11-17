"""
============================================================
Modulo: DASHBOARD_STREAMLIT / configuracao.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes simples para configurar paginas e dashboards Streamlit.
    O modulo centraliza titulo, icone, layout, sidebar, menu, largura,
    espacamento e elementos visuais globais da aplicacao.
Funcoes disponiveis:
    - configurar_pagina()
    - configurar_dashboard()
    - definir_largura_dashboard()
    - definir_espacamento_pagina()
    - ocultar_menu_padrao()
    - ocultar_rodape_streamlit()
    - ocultar_cabecalho_streamlit()
    - ocultar_elementos_streamlit()
    - aplicar_configuracao_visual()
    - obter_configuracao_dashboard()
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao da configuracao de pagina e dashboard.
        - Inclusao dos ajustes visuais globais.
============================================================
"""

# ----------------------------------------------------------------------------
# IMPORTACOES
# ----------------------------------------------------------------------------

# Importa Mapping para aceitar itens de menu sem exigir um dicionario concreto
from collections.abc import Mapping

# Importa Any para os retornos dos componentes do Streamlit
from typing import Any

# Importa Streamlit para configurar e estilizar a pagina
import streamlit as st


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

TITULO_PADRAO = "Dashboard"
ICONE_PADRAO = "📊"
LAYOUT_PADRAO = "wide"
ESTADO_SIDEBAR_PADRAO = "expanded"
LARGURA_MAXIMA_PADRAO = 1600
ESPACAMENTO_SUPERIOR_PADRAO = 1.5
ESPACAMENTO_LATERAL_PADRAO = 2.0

LAYOUTS_VALIDOS = {"wide", "centered"}
ESTADOS_SIDEBAR_VALIDOS = {"auto", "expanded", "collapsed", "locked"}

# Mantem a ultima configuracao aplicada por este modulo durante a execucao
_CONFIGURACAO_ATUAL: dict[str, Any] = {}


# ----------------------------------------------------------------------------
# EXCECOES
# ----------------------------------------------------------------------------

class DashboardConfiguracaoError(Exception):
    """Erro base para configuracoes do dashboard Streamlit."""


class ConfiguracaoPaginaInvalidaError(DashboardConfiguracaoError, ValueError):
    """Indica que uma configuracao da pagina possui valor invalido."""


class ConfiguracaoVisualInvalidaError(DashboardConfiguracaoError, ValueError):
    """Indica que uma configuracao visual possui valor invalido."""


# ----------------------------------------------------------------------------
# FUNCOES INTERNAS
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


def _validar_texto(
    valor: Any,
    nome: str,
    permitir_vazio: bool = False
) -> str:
    """
    Valida e normaliza um parametro textual.

    Args:
        valor (Any): Valor que sera convertido em texto.
        nome (str): Nome utilizado na mensagem de erro.
        permitir_vazio (bool): Define se texto vazio sera permitido.

    Returns:
        str: Texto sem espacos externos.

    Raises:
        ConfiguracaoPaginaInvalidaError: Caso o texto seja invalido.
    """
    _validar_booleano(permitir_vazio, "permitir_vazio")

    if valor is None:
        if permitir_vazio:
            return ""
        raise ConfiguracaoPaginaInvalidaError(
            f"O parametro '{nome}' nao pode ser None."
        )

    texto = str(valor).strip()
    if not texto and not permitir_vazio:
        raise ConfiguracaoPaginaInvalidaError(
            f"O parametro '{nome}' nao pode estar vazio."
        )
    return texto


def _validar_numero(
    valor: int | float,
    nome: str,
    minimo: float,
    maximo: float
) -> float:
    """
    Valida um numero dentro de um intervalo fechado.

    Args:
        valor (int | float): Valor numerico que sera validado.
        nome (str): Nome utilizado na mensagem de erro.
        minimo (float): Menor valor permitido.
        maximo (float): Maior valor permitido.

    Returns:
        float: Valor convertido para float.

    Raises:
        ConfiguracaoVisualInvalidaError: Caso o valor seja invalido.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ConfiguracaoVisualInvalidaError(
            f"O parametro '{nome}' deve ser numerico."
        )

    numero = float(valor)
    if not minimo <= numero <= maximo:
        raise ConfiguracaoVisualInvalidaError(
            f"O parametro '{nome}' deve estar entre {minimo} e {maximo}."
        )
    return numero


def _validar_layout(layout: str) -> str:
    """
    Valida o layout principal da pagina.

    Args:
        layout (str): Layout wide ou centered.

    Returns:
        str: Layout normalizado.

    Raises:
        ConfiguracaoPaginaInvalidaError: Caso o layout seja desconhecido.
    """
    valor = _validar_texto(layout, "layout").lower()
    if valor not in LAYOUTS_VALIDOS:
        raise ConfiguracaoPaginaInvalidaError(
            "O parametro 'layout' deve ser 'wide' ou 'centered'."
        )
    return valor


def _validar_estado_sidebar(estado: str) -> str:
    """
    Valida o estado inicial da barra lateral.

    Args:
        estado (str): Estado auto, expanded, collapsed ou locked.

    Returns:
        str: Estado normalizado.

    Raises:
        ConfiguracaoPaginaInvalidaError: Caso o estado seja desconhecido.
    """
    valor = _validar_texto(estado, "estado_sidebar").lower()
    if valor not in ESTADOS_SIDEBAR_VALIDOS:
        raise ConfiguracaoPaginaInvalidaError(
            "O parametro 'estado_sidebar' deve ser auto, expanded, "
            "collapsed ou locked."
        )
    return valor


def _normalizar_menu(
    itens_menu: Mapping[str, str | None] | None
) -> dict[str, str | None] | None:
    """
    Valida e converte os itens do menu para um dicionario.

    Args:
        itens_menu (Mapping | None): Links e textos do menu do Streamlit.

    Returns:
        dict | None: Itens normalizados ou None.

    Raises:
        ConfiguracaoPaginaInvalidaError: Caso o mapeamento seja invalido.
    """
    if itens_menu is None:
        return None
    if not isinstance(itens_menu, Mapping):
        raise ConfiguracaoPaginaInvalidaError(
            "O parametro 'itens_menu' deve ser um mapeamento ou None."
        )

    resultado: dict[str, str | None] = {}
    for chave, valor in itens_menu.items():
        chave_normalizada = _validar_texto(chave, "chave_menu")
        if valor is not None and not isinstance(valor, str):
            raise ConfiguracaoPaginaInvalidaError(
                "Os valores de 'itens_menu' devem ser strings ou None."
            )
        resultado[chave_normalizada] = valor
    return resultado


def _aplicar_css(css: str) -> Any:
    """
    Aplica um bloco CSS controlado na pagina.

    Args:
        css (str): Regras CSS sem a tag style.

    Returns:
        Any: Resultado retornado por st.markdown.

    Raises:
        ConfiguracaoVisualInvalidaError: Caso o CSS esteja vazio.
    """
    if not isinstance(css, str) or not css.strip():
        raise ConfiguracaoVisualInvalidaError(
            "O bloco CSS nao pode estar vazio."
        )
    return st.markdown(
        f"<style>{css.strip()}</style>",
        unsafe_allow_html=True
    )


# ----------------------------------------------------------------------------
# CONFIGURACAO DA PAGINA
# ----------------------------------------------------------------------------

def configurar_pagina(
    titulo: str = TITULO_PADRAO,
    icone: Any = ICONE_PADRAO,
    layout: str = LAYOUT_PADRAO,
    estado_sidebar: str = ESTADO_SIDEBAR_PADRAO,
    itens_menu: Mapping[str, str | None] | None = None
) -> dict[str, Any]:
    """
    Configura titulo, icone, layout, sidebar e menu da pagina.

    Args:
        titulo (str): Titulo exibido na aba do navegador.
        icone (Any): Emoji, Material icon, imagem ou valor aceito pelo Streamlit.
        layout (str): Layout wide ou centered.
        estado_sidebar (str): Estado inicial da barra lateral.
        itens_menu (Mapping | None): Itens opcionais do menu principal.

    Returns:
        dict[str, Any]: Configuracao normalizada aplicada a pagina.

    Raises:
        ConfiguracaoPaginaInvalidaError: Caso algum parametro seja invalido.
    """
    titulo_validado = _validar_texto(titulo, "titulo")
    if icone is None:
        raise ConfiguracaoPaginaInvalidaError(
            "O parametro 'icone' nao pode ser None."
        )

    configuracao = {
        "page_title": titulo_validado,
        "page_icon": icone,
        "layout": _validar_layout(layout),
        "initial_sidebar_state": _validar_estado_sidebar(estado_sidebar),
        "menu_items": _normalizar_menu(itens_menu)
    }

    st.set_page_config(**configuracao)

    _CONFIGURACAO_ATUAL.update({
        "titulo": titulo_validado,
        "icone": icone,
        "layout": configuracao["layout"],
        "estado_sidebar": configuracao["initial_sidebar_state"],
        "itens_menu": configuracao["menu_items"]
    })
    return dict(_CONFIGURACAO_ATUAL)


def configurar_dashboard(
    titulo: str = TITULO_PADRAO,
    icone: Any = ICONE_PADRAO,
    layout: str = LAYOUT_PADRAO,
    estado_sidebar: str = ESTADO_SIDEBAR_PADRAO,
    itens_menu: Mapping[str, str | None] | None = None,
    largura_maxima: int | float = LARGURA_MAXIMA_PADRAO,
    espacamento_superior: int | float = ESPACAMENTO_SUPERIOR_PADRAO,
    espacamento_lateral: int | float = ESPACAMENTO_LATERAL_PADRAO,
    ocultar_menu: bool = False,
    ocultar_rodape: bool = True,
    ocultar_cabecalho: bool = False
) -> dict[str, Any]:
    """
    Configura a pagina e aplica os ajustes visuais mais comuns.

    Args:
        titulo (str): Titulo exibido na aba do navegador.
        icone (Any): Icone exibido na aba do navegador.
        layout (str): Layout wide ou centered.
        estado_sidebar (str): Estado inicial da barra lateral.
        itens_menu (Mapping | None): Itens opcionais do menu principal.
        largura_maxima (int | float): Largura maxima do conteudo em pixels.
        espacamento_superior (int | float): Espaco superior em rem.
        espacamento_lateral (int | float): Espaco lateral em rem.
        ocultar_menu (bool): Define se o menu padrao sera ocultado.
        ocultar_rodape (bool): Define se o rodape sera ocultado.
        ocultar_cabecalho (bool): Define se o cabecalho sera ocultado.

    Returns:
        dict[str, Any]: Configuracao completa aplicada ao dashboard.

    Raises:
        DashboardConfiguracaoError: Caso alguma configuracao seja invalida.
    """
    configurar_pagina(
        titulo=titulo,
        icone=icone,
        layout=layout,
        estado_sidebar=estado_sidebar,
        itens_menu=itens_menu
    )

    aplicar_configuracao_visual(
        largura_maxima=largura_maxima,
        espacamento_superior=espacamento_superior,
        espacamento_lateral=espacamento_lateral,
        ocultar_menu=ocultar_menu,
        ocultar_rodape=ocultar_rodape,
        ocultar_cabecalho=ocultar_cabecalho
    )
    return obter_configuracao_dashboard()


# ----------------------------------------------------------------------------
# CONFIGURACOES VISUAIS
# ----------------------------------------------------------------------------

def definir_largura_dashboard(
    largura_maxima: int | float = LARGURA_MAXIMA_PADRAO
) -> Any:
    """
    Define a largura maxima da area principal do dashboard.

    Args:
        largura_maxima (int | float): Largura entre 320 e 3840 pixels.

    Returns:
        Any: Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoVisualInvalidaError: Caso a largura seja invalida.
    """
    largura = _validar_numero(
        largura_maxima,
        "largura_maxima",
        320,
        3840
    )
    _CONFIGURACAO_ATUAL["largura_maxima"] = largura
    return _aplicar_css(
        f'.stMainBlockContainer {{max-width: {largura:g}px;}}'
    )


def definir_espacamento_pagina(
    superior: int | float = ESPACAMENTO_SUPERIOR_PADRAO,
    lateral: int | float = ESPACAMENTO_LATERAL_PADRAO,
    inferior: int | float = 2.0
) -> Any:
    """
    Define os espacamentos internos da area principal.

    Args:
        superior (int | float): Espacamento superior em rem.
        lateral (int | float): Espacamento lateral em rem.
        inferior (int | float): Espacamento inferior em rem.

    Returns:
        Any: Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoVisualInvalidaError: Caso algum valor seja invalido.
    """
    valor_superior = _validar_numero(superior, "superior", 0, 20)
    valor_lateral = _validar_numero(lateral, "lateral", 0, 20)
    valor_inferior = _validar_numero(inferior, "inferior", 0, 20)

    _CONFIGURACAO_ATUAL.update({
        "espacamento_superior": valor_superior,
        "espacamento_lateral": valor_lateral,
        "espacamento_inferior": valor_inferior
    })

    return _aplicar_css(
        ".stMainBlockContainer {"
        f"padding-top: {valor_superior:g}rem;"
        f"padding-right: {valor_lateral:g}rem;"
        f"padding-bottom: {valor_inferior:g}rem;"
        f"padding-left: {valor_lateral:g}rem;"
        "}"
    )


def ocultar_menu_padrao() -> Any:
    """
    Oculta o menu principal padrao do Streamlit.

    Args:
        Nenhum.

    Returns:
        Any: Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoVisualInvalidaError: Caso o CSS nao possa ser aplicado.
    """
    _CONFIGURACAO_ATUAL["ocultar_menu"] = True
    return _aplicar_css("#MainMenu {visibility: hidden;}")


def ocultar_rodape_streamlit() -> Any:
    """
    Oculta o rodape padrao do Streamlit.

    Args:
        Nenhum.

    Returns:
        Any: Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoVisualInvalidaError: Caso o CSS nao possa ser aplicado.
    """
    _CONFIGURACAO_ATUAL["ocultar_rodape"] = True
    return _aplicar_css("footer {visibility: hidden;}")


def ocultar_cabecalho_streamlit() -> Any:
    """
    Oculta o cabecalho e a barra superior do Streamlit.

    Args:
        Nenhum.

    Returns:
        Any: Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoVisualInvalidaError: Caso o CSS nao possa ser aplicado.
    """
    _CONFIGURACAO_ATUAL["ocultar_cabecalho"] = True
    return _aplicar_css(
        'header[data-testid="stHeader"] {visibility: hidden; height: 0;}'
    )


def ocultar_elementos_streamlit(
    menu: bool = True,
    rodape: bool = True,
    cabecalho: bool = False
) -> list[Any]:
    """
    Oculta em uma chamada os elementos padrao selecionados.

    Args:
        menu (bool): Define se o menu sera ocultado.
        rodape (bool): Define se o rodape sera ocultado.
        cabecalho (bool): Define se o cabecalho sera ocultado.

    Returns:
        list[Any]: Resultados das regras CSS aplicadas.

    Raises:
        TypeError: Caso alguma opcao nao seja booleana.
    """
    _validar_booleano(menu, "menu")
    _validar_booleano(rodape, "rodape")
    _validar_booleano(cabecalho, "cabecalho")

    resultados: list[Any] = []
    if menu:
        resultados.append(ocultar_menu_padrao())
    if rodape:
        resultados.append(ocultar_rodape_streamlit())
    if cabecalho:
        resultados.append(ocultar_cabecalho_streamlit())
    return resultados


def aplicar_configuracao_visual(
    largura_maxima: int | float = LARGURA_MAXIMA_PADRAO,
    espacamento_superior: int | float = ESPACAMENTO_SUPERIOR_PADRAO,
    espacamento_lateral: int | float = ESPACAMENTO_LATERAL_PADRAO,
    ocultar_menu: bool = False,
    ocultar_rodape: bool = True,
    ocultar_cabecalho: bool = False
) -> list[Any]:
    """
    Aplica largura, espacamento e visibilidade dos elementos padrao.

    Args:
        largura_maxima (int | float): Largura maxima do conteudo em pixels.
        espacamento_superior (int | float): Espaco superior em rem.
        espacamento_lateral (int | float): Espaco lateral em rem.
        ocultar_menu (bool): Define se o menu sera ocultado.
        ocultar_rodape (bool): Define se o rodape sera ocultado.
        ocultar_cabecalho (bool): Define se o cabecalho sera ocultado.

    Returns:
        list[Any]: Resultados dos componentes st.markdown executados.

    Raises:
        DashboardConfiguracaoError: Caso alguma configuracao seja invalida.
    """
    resultados = [
        definir_largura_dashboard(largura_maxima),
        definir_espacamento_pagina(
            superior=espacamento_superior,
            lateral=espacamento_lateral
        )
    ]
    resultados.extend(
        ocultar_elementos_streamlit(
            menu=ocultar_menu,
            rodape=ocultar_rodape,
            cabecalho=ocultar_cabecalho
        )
    )

    _CONFIGURACAO_ATUAL.update({
        "ocultar_menu": ocultar_menu,
        "ocultar_rodape": ocultar_rodape,
        "ocultar_cabecalho": ocultar_cabecalho
    })
    return resultados


# ----------------------------------------------------------------------------
# CONSULTA
# ----------------------------------------------------------------------------

def obter_configuracao_dashboard() -> dict[str, Any]:
    """
    Retorna uma copia da ultima configuracao aplicada pelo modulo.

    Args:
        Nenhum.

    Returns:
        dict[str, Any]: Copia da configuracao atual.

    Raises:
        DashboardConfiguracaoError: Nunca e gerada no fluxo normal.
    """
    return dict(_CONFIGURACAO_ATUAL)


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "TITULO_PADRAO",
    "ICONE_PADRAO",
    "LAYOUT_PADRAO",
    "ESTADO_SIDEBAR_PADRAO",
    "LARGURA_MAXIMA_PADRAO",
    "ESPACAMENTO_SUPERIOR_PADRAO",
    "ESPACAMENTO_LATERAL_PADRAO",
    "LAYOUTS_VALIDOS",
    "ESTADOS_SIDEBAR_VALIDOS",
    "DashboardConfiguracaoError",
    "ConfiguracaoPaginaInvalidaError",
    "ConfiguracaoVisualInvalidaError",
    "configurar_pagina",
    "configurar_dashboard",
    "definir_largura_dashboard",
    "definir_espacamento_pagina",
    "ocultar_menu_padrao",
    "ocultar_rodape_streamlit",
    "ocultar_cabecalho_streamlit",
    "ocultar_elementos_streamlit",
    "aplicar_configuracao_visual",
    "obter_configuracao_dashboard"
]
