"""
============================================================
Modulo: DASHBOARD_STREAMLIT / layout.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes reutilizaveis para organizar dashboards Streamlit com colunas,
    containers, abas, expansores, sidebar, placeholders, secoes, cabecalhos
    e espacamentos. O modulo centraliza validacoes e configuracoes de layout.
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao de colunas, containers, abas e expansores.
        - Inclusao de cabecalho, secao, sidebar e placeholders.
============================================================
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import streamlit as st

try:
    from .excecoes import LayoutInvalidoError, TextoInvalidoError
except ImportError:
    from excecoes import LayoutInvalidoError, TextoInvalidoError


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

ESPACAMENTOS_VALIDOS = {
    "xxsmall", "xsmall", "small", "medium", "large", "xlarge", "xxlarge"
}
ALINHAMENTOS_VERTICAIS_VALIDOS = {"top", "center", "bottom"}
ALINHAMENTOS_HORIZONTAIS_VALIDOS = {"left", "center", "right", "distribute"}
LARGURAS_VALIDAS = {"stretch", "content"}
ALTURAS_VALIDAS = {"content", "stretch"}
TIPOS_EXPANSOR_VALIDOS = {"default", "step", "accordion"}
NIVEIS_TITULO_VALIDOS = {1, 2, 3, 4, 5, 6}
PREFIXO_CHAVE_LAYOUT = "layout"


# ----------------------------------------------------------------------------
# VALIDACOES INTERNAS
# ----------------------------------------------------------------------------

def _validar_texto(valor: Any, nome: str) -> str:
    """Valida um texto obrigatorio.

    Args:
        valor (Any): Valor que sera validado.
        nome (str): Nome usado na mensagem de erro.

    Returns:
        str: Texto sem espacos externos.

    Raises:
        TextoInvalidoError: Caso o valor nao seja texto preenchido.
    """
    if not isinstance(valor, str) or not valor.strip():
        raise TextoInvalidoError(
            f"O parametro '{nome}' deve ser uma string preenchida."
        )
    return valor.strip()


def _validar_booleano(valor: bool, nome: str) -> bool:
    """Valida estritamente um parametro booleano.

    Args:
        valor (bool): Valor que sera validado.
        nome (str): Nome usado na mensagem de erro.

    Returns:
        bool: O proprio valor validado.

    Raises:
        TypeError: Caso o valor nao seja booleano.
    """
    if not isinstance(valor, bool):
        raise TypeError(f"O parametro '{nome}' deve ser booleano.")
    return valor


def _validar_dimensao(
    valor: str | int,
    nome: str,
    textos_validos: set[str]
) -> str | int:
    """Valida uma largura ou altura do Streamlit.

    Args:
        valor (str | int): Texto suportado ou quantidade de pixels.
        nome (str): Nome usado na mensagem de erro.
        textos_validos (set[str]): Valores textuais permitidos.

    Returns:
        str | int: Dimensao normalizada.

    Raises:
        LayoutInvalidoError: Caso a dimensao seja invalida.
    """
    if isinstance(valor, int) and not isinstance(valor, bool) and valor > 0:
        return valor
    if isinstance(valor, str) and valor.strip().lower() in textos_validos:
        return valor.strip().lower()
    permitidos = ", ".join(sorted(textos_validos))
    raise LayoutInvalidoError(
        f"O parametro '{nome}' deve ser inteiro positivo ou: {permitidos}."
    )


def _validar_espacamento(espacamento: str | int | None) -> str | int | None:
    """Valida o espacamento entre elementos.

    Args:
        espacamento (str | int | None): Nome, pixels ou None.

    Returns:
        str | int | None: Espacamento normalizado.

    Raises:
        LayoutInvalidoError: Caso o espacamento seja invalido.
    """
    if espacamento is None:
        return None
    if isinstance(espacamento, int) and not isinstance(espacamento, bool):
        if espacamento >= 0:
            return espacamento
    if isinstance(espacamento, str):
        valor = espacamento.strip().lower()
        if valor in ESPACAMENTOS_VALIDOS:
            return valor
    raise LayoutInvalidoError(
        "O espacamento deve ser um nome valido, inteiro nao negativo ou None."
    )


def _validar_chave(chave: str | None, base: str | None = None) -> str | None:
    """Valida uma chave ou gera uma chave a partir de uma base.

    Args:
        chave (str | None): Chave personalizada.
        base (str | None): Texto usado para gerar uma chave.

    Returns:
        str | None: Chave normalizada, gerada ou None.

    Raises:
        LayoutInvalidoError: Caso a chave informada seja invalida.
    """
    if chave is not None:
        if not isinstance(chave, str) or not chave.strip():
            raise LayoutInvalidoError("A chave deve ser uma string preenchida.")
        return chave.strip()
    if base is None:
        return None
    texto = _validar_texto(base, "base")
    normalizado = "_".join(texto.lower().split())
    return f"{PREFIXO_CHAVE_LAYOUT}_{normalizado}"


# ----------------------------------------------------------------------------
# CONTAINERS E COLUNAS
# ----------------------------------------------------------------------------

def criar_colunas(
    especificacao: int | Sequence[int | float],
    *,
    espacamento: str | int | None = "small",
    alinhamento_vertical: str = "top",
    borda: bool = False,
    largura: str | int = "stretch",
    quebrar_linha: bool = True
) -> list[Any]:
    """Cria colunas lado a lado com configuracao validada.

    Args:
        especificacao (int | Sequence): Quantidade ou proporcoes das colunas.
        espacamento (str | int | None): Espaco entre colunas.
        alinhamento_vertical (str): top, center ou bottom.
        borda (bool): Exibe borda nas colunas.
        largura (str | int): stretch ou largura em pixels.
        quebrar_linha (bool): Permite empilhamento em telas estreitas.

    Returns:
        list[Any]: Containers de coluna retornados pelo Streamlit.

    Raises:
        LayoutInvalidoError: Caso a especificacao seja invalida.
    """
    if isinstance(especificacao, bool):
        raise LayoutInvalidoError("A especificacao de colunas e invalida.")
    if isinstance(especificacao, int):
        if especificacao < 1:
            raise LayoutInvalidoError("A quantidade de colunas deve ser positiva.")
        spec: int | list[int | float] = especificacao
    elif isinstance(especificacao, Sequence) and not isinstance(
        especificacao, (str, bytes)
    ):
        spec = list(especificacao)
        if not spec or any(
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or valor <= 0
            for valor in spec
        ):
            raise LayoutInvalidoError(
                "As proporcoes das colunas devem ser numeros positivos."
            )
    else:
        raise LayoutInvalidoError(
            "A especificacao deve ser um inteiro ou sequencia numerica."
        )

    alinhamento = _validar_texto(
        alinhamento_vertical, "alinhamento_vertical"
    ).lower()
    if alinhamento not in ALINHAMENTOS_VERTICAIS_VALIDOS:
        raise LayoutInvalidoError(
            "O alinhamento vertical deve ser top, center ou bottom."
        )
    _validar_booleano(borda, "borda")
    _validar_booleano(quebrar_linha, "quebrar_linha")

    return list(st.columns(
        spec,
        gap=_validar_espacamento(espacamento),
        vertical_alignment=alinhamento,
        border=borda,
        width=_validar_dimensao(largura, "largura", {"stretch"}),
        wrap=quebrar_linha
    ))


def criar_container(
    *,
    borda: bool | None = None,
    chave: str | None = None,
    largura: str | int = "stretch",
    altura: str | int = "content",
    horizontal: bool = False,
    quebrar_linha: bool = True,
    alinhamento_horizontal: str = "left",
    alinhamento_vertical: str = "top",
    espacamento: str | int | None = "small"
) -> Any:
    """Cria um container vertical ou horizontal.

    Args:
        borda (bool | None): Exibe borda ou usa o comportamento automatico.
        chave (str | None): Chave estavel do container.
        largura (str | int): stretch, content ou pixels.
        altura (str | int): content, stretch ou pixels.
        horizontal (bool): Organiza elementos horizontalmente.
        quebrar_linha (bool): Permite quebra em multiplas linhas.
        alinhamento_horizontal (str): left, center, right ou distribute.
        alinhamento_vertical (str): top, center ou bottom.
        espacamento (str | int | None): Espaco entre elementos.

    Returns:
        Any: Container criado pelo Streamlit.

    Raises:
        LayoutInvalidoError: Caso uma configuracao seja invalida.
    """
    if borda is not None:
        _validar_booleano(borda, "borda")
    _validar_booleano(horizontal, "horizontal")
    _validar_booleano(quebrar_linha, "quebrar_linha")

    horizontal_alinhamento = _validar_texto(
        alinhamento_horizontal, "alinhamento_horizontal"
    ).lower()
    if horizontal_alinhamento not in ALINHAMENTOS_HORIZONTAIS_VALIDOS:
        raise LayoutInvalidoError(
            "O alinhamento horizontal deve ser left, center, right ou distribute."
        )

    vertical_alinhamento = _validar_texto(
        alinhamento_vertical, "alinhamento_vertical"
    ).lower()
    if vertical_alinhamento not in ALINHAMENTOS_VERTICAIS_VALIDOS:
        raise LayoutInvalidoError(
            "O alinhamento vertical deve ser top, center ou bottom."
        )

    return st.container(
        border=borda,
        key=_validar_chave(chave),
        width=_validar_dimensao(largura, "largura", LARGURAS_VALIDAS),
        height=_validar_dimensao(altura, "altura", ALTURAS_VALIDAS),
        horizontal=horizontal,
        wrap=quebrar_linha,
        horizontal_alignment=horizontal_alinhamento,
        vertical_alignment=vertical_alinhamento,
        gap=_validar_espacamento(espacamento)
    )


def criar_linha_metricas(
    quantidade: int,
    *,
    espacamento: str | int | None = "small",
    borda: bool = False
) -> list[Any]:
    """Cria uma linha de colunas iguais para cards ou metricas.

    Args:
        quantidade (int): Quantidade de metricas.
        espacamento (str | int | None): Espaco entre as colunas.
        borda (bool): Exibe borda nas colunas.

    Returns:
        list[Any]: Colunas preparadas para metricas.

    Raises:
        LayoutInvalidoError: Caso a quantidade seja invalida.
    """
    return criar_colunas(
        quantidade,
        espacamento=espacamento,
        borda=borda,
        alinhamento_vertical="top"
    )


# ----------------------------------------------------------------------------
# ABAS, EXPANSORES E SIDEBAR
# ----------------------------------------------------------------------------

def criar_abas(
    titulos: Sequence[str],
    *,
    largura: str | int = "stretch",
    altura: str | int = "content",
    aba_padrao: str | None = None,
    chave: str | None = None,
    ao_mudar: str | Any = "ignore"
) -> list[Any]:
    """Cria abas de navegacao para grupos de conteudo.

    Args:
        titulos (Sequence[str]): Titulos das abas.
        largura (str | int): stretch ou pixels.
        altura (str | int): content, stretch ou pixels.
        aba_padrao (str | None): Aba selecionada inicialmente.
        chave (str | None): Chave para controlar a aba.
        ao_mudar (str | Any): ignore, rerun ou callback.

    Returns:
        list[Any]: Containers das abas.

    Raises:
        LayoutInvalidoError: Caso os titulos ou aba padrao sejam invalidos.
    """
    if isinstance(titulos, (str, bytes)) or not isinstance(titulos, Sequence):
        raise LayoutInvalidoError("Os titulos devem ser uma sequencia textual.")
    nomes = [_validar_texto(titulo, "titulo_aba") for titulo in titulos]
    if not nomes:
        raise LayoutInvalidoError("Informe ao menos uma aba.")
    if len(nomes) != len(set(nomes)):
        raise LayoutInvalidoError("Os titulos das abas nao podem se repetir.")
    padrao = None
    if aba_padrao is not None:
        padrao = _validar_texto(aba_padrao, "aba_padrao")
        if padrao not in nomes:
            raise LayoutInvalidoError("A aba padrao nao existe na lista.")

    return list(st.tabs(
        nomes,
        width=_validar_dimensao(largura, "largura", {"stretch"}),
        height=_validar_dimensao(altura, "altura", ALTURAS_VALIDAS),
        default=padrao,
        key=_validar_chave(chave),
        on_change=ao_mudar
    ))


def criar_expansor(
    titulo: str,
    *,
    expandido: bool = False,
    chave: str | None = None,
    icone: str | None = None,
    tipo: str = "default",
    largura: str | int = "stretch",
    ao_mudar: str | Any = "ignore"
) -> Any:
    """Cria um container expansivel.

    Args:
        titulo (str): Texto exibido no cabecalho.
        expandido (bool): Inicia aberto.
        chave (str | None): Chave do expansor.
        icone (str | None): Emoji ou Material icon.
        tipo (str): default, step ou accordion.
        largura (str | int): stretch ou pixels.
        ao_mudar (str | Any): ignore, rerun ou callback.

    Returns:
        Any: Container expansivel.

    Raises:
        LayoutInvalidoError: Caso o tipo seja invalido.
    """
    nome = _validar_texto(titulo, "titulo")
    _validar_booleano(expandido, "expandido")
    tipo_validado = _validar_texto(tipo, "tipo").lower()
    if tipo_validado not in TIPOS_EXPANSOR_VALIDOS:
        raise LayoutInvalidoError(
            "O tipo do expansor deve ser default, step ou accordion."
        )
    return st.expander(
        nome,
        expanded=expandido,
        key=_validar_chave(chave, nome),
        icon=icone,
        type=tipo_validado,
        width=_validar_dimensao(largura, "largura", {"stretch"}),
        on_change=ao_mudar
    )


def obter_sidebar() -> Any:
    """Retorna o container lateral do Streamlit.

    Args:
        Nenhum.

    Returns:
        Any: Objeto st.sidebar.

    Raises:
        LayoutInvalidoError: Nunca e gerada no fluxo normal.
    """
    return st.sidebar


# ----------------------------------------------------------------------------
# CABECALHOS, SECOES E ESPACAMENTO
# ----------------------------------------------------------------------------

def criar_cabecalho(
    titulo: str,
    *,
    subtitulo: str | None = None,
    descricao: str | None = None,
    divisor: bool = False
) -> dict[str, Any]:
    """Renderiza um cabecalho padronizado de pagina.

    Args:
        titulo (str): Titulo principal.
        subtitulo (str | None): Subtitulo opcional.
        descricao (str | None): Descricao opcional.
        divisor (bool): Exibe uma linha abaixo do cabecalho.

    Returns:
        dict[str, Any]: Valores renderizados no cabecalho.

    Raises:
        TextoInvalidoError: Caso algum texto informado seja invalido.
    """
    titulo_validado = _validar_texto(titulo, "titulo")
    subtitulo_validado = (
        None if subtitulo is None else _validar_texto(subtitulo, "subtitulo")
    )
    descricao_validada = (
        None if descricao is None else _validar_texto(descricao, "descricao")
    )
    _validar_booleano(divisor, "divisor")

    st.title(titulo_validado)
    if subtitulo_validado:
        st.subheader(subtitulo_validado)
    if descricao_validada:
        st.caption(descricao_validada)
    if divisor:
        st.divider()

    return {
        "titulo": titulo_validado,
        "subtitulo": subtitulo_validado,
        "descricao": descricao_validada,
        "divisor": divisor
    }


def criar_titulo_secao(
    titulo: str,
    *,
    descricao: str | None = None,
    nivel: int = 2,
    divisor: bool = False
) -> dict[str, Any]:
    """Renderiza o titulo de uma secao usando Markdown.

    Args:
        titulo (str): Titulo da secao.
        descricao (str | None): Texto auxiliar.
        nivel (int): Nivel Markdown entre 1 e 6.
        divisor (bool): Exibe divisor antes do titulo.

    Returns:
        dict[str, Any]: Configuracao renderizada.

    Raises:
        LayoutInvalidoError: Caso o nivel seja invalido.
    """
    nome = _validar_texto(titulo, "titulo")
    if isinstance(nivel, bool) or nivel not in NIVEIS_TITULO_VALIDOS:
        raise LayoutInvalidoError("O nivel do titulo deve estar entre 1 e 6.")
    descricao_validada = (
        None if descricao is None else _validar_texto(descricao, "descricao")
    )
    _validar_booleano(divisor, "divisor")

    if divisor:
        st.divider()
    st.markdown(f"{'#' * nivel} {nome}")
    if descricao_validada:
        st.caption(descricao_validada)

    return {
        "titulo": nome,
        "descricao": descricao_validada,
        "nivel": nivel,
        "divisor": divisor
    }


def adicionar_espaco(
    tamanho: str | int = "small",
    *,
    quantidade: int = 1
) -> list[Any]:
    """Adiciona espacos verticais usando st.space quando disponivel.

    Args:
        tamanho (str | int): Nome de espacamento ou pixels.
        quantidade (int): Quantidade de espacos.

    Returns:
        list[Any]: Retornos gerados pelo Streamlit.

    Raises:
        LayoutInvalidoError: Caso quantidade ou tamanho sejam invalidos.
    """
    if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade < 1:
        raise LayoutInvalidoError("A quantidade deve ser um inteiro positivo.")
    tamanho_validado = _validar_espacamento(tamanho)
    resultados: list[Any] = []
    funcao_space = getattr(st, "space", None)
    for _ in range(quantidade):
        if callable(funcao_space):
            resultados.append(funcao_space(tamanho_validado))
        else:
            altura = tamanho_validado if isinstance(tamanho_validado, int) else 16
            resultados.append(st.markdown(
                f"<div style='height:{altura}px'></div>",
                unsafe_allow_html=True
            ))
    return resultados


def criar_placeholder() -> Any:
    """Cria um placeholder de elemento unico.

    Args:
        Nenhum.

    Returns:
        Any: Placeholder retornado por st.empty.

    Raises:
        LayoutInvalidoError: Nunca e gerada no fluxo normal.
    """
    return st.empty()


def adicionar_divisor() -> Any:
    """Adiciona uma linha divisoria ao layout.

    Args:
        Nenhum.

    Returns:
        Any: Retorno de st.divider.

    Raises:
        LayoutInvalidoError: Nunca e gerada no fluxo normal.
    """
    return st.divider()


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "ESPACAMENTOS_VALIDOS",
    "ALINHAMENTOS_VERTICAIS_VALIDOS",
    "ALINHAMENTOS_HORIZONTAIS_VALIDOS",
    "LARGURAS_VALIDAS",
    "ALTURAS_VALIDAS",
    "TIPOS_EXPANSOR_VALIDOS",
    "NIVEIS_TITULO_VALIDOS",
    "PREFIXO_CHAVE_LAYOUT",
    "criar_colunas",
    "criar_container",
    "criar_linha_metricas",
    "criar_abas",
    "criar_expansor",
    "obter_sidebar",
    "criar_cabecalho",
    "criar_titulo_secao",
    "adicionar_espaco",
    "criar_placeholder",
    "adicionar_divisor"
]
