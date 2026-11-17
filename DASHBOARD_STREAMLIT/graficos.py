"""
============================================================
Modulo: DASHBOARD_STREAMLIT / graficos.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes reutilizaveis para criar, padronizar e exibir graficos Plotly
    em dashboards Streamlit. O modulo centraliza validacoes, estilos,
    cores, ordenacao, legendas e configuracoes de exibicao.
Dependencias:
    - pandas
    - plotly
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao dos graficos principais com Plotly Express.
        - Inclusao da padronizacao visual e exibicao no Streamlit.
============================================================
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from .constantes import (
        ALTURA_GRAFICO_PADRAO,
        CORES_GRAFICOS,
        CONFIGURACAO_GRAFICO_PADRAO,
        FONTE_GRAFICO_PADRAO,
        MARGENS_GRAFICO_PADRAO,
        ORDENACOES_VALIDAS,
        ORIENTACOES_GRAFICO_VALIDAS,
        POSICOES_LEGENDA_VALIDAS,
        POSICAO_LEGENDA_PADRAO,
        TEMPLATE_GRAFICO_PADRAO,
    )
    from .excecoes import (
        BibliotecaGraficoIndisponivelError,
        ColunaNaoEncontradaError,
        ConfiguracaoGraficoInvalidaError,
        DataFrameInvalidoError,
        DataFrameVazioError,
        DadosGraficoInvalidosError,
    )
except ImportError:
    from constantes import (
        ALTURA_GRAFICO_PADRAO,
        CORES_GRAFICOS,
        CONFIGURACAO_GRAFICO_PADRAO,
        FONTE_GRAFICO_PADRAO,
        MARGENS_GRAFICO_PADRAO,
        ORDENACOES_VALIDAS,
        ORIENTACOES_GRAFICO_VALIDAS,
        POSICOES_LEGENDA_VALIDAS,
        POSICAO_LEGENDA_PADRAO,
        TEMPLATE_GRAFICO_PADRAO,
    )
    from excecoes import (
        BibliotecaGraficoIndisponivelError,
        ColunaNaoEncontradaError,
        ConfiguracaoGraficoInvalidaError,
        DataFrameInvalidoError,
        DataFrameVazioError,
        DadosGraficoInvalidosError,
    )


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

TIPOS_GRAFICO_VALIDOS = {
    "barras", "linhas", "area", "dispersao", "pizza", "rosca",
    "histograma", "caixa", "funil"
}
MODOS_BARRA_VALIDOS = {"group", "stack", "relative", "overlay"}
POSICOES_TEXTO_BARRA_VALIDAS = {
    "auto", "inside", "outside", "none"
}
LARGURAS_GRAFICO_VALIDAS = {"stretch", "content"}
PREFIXO_CHAVE_GRAFICO = "grafico"


# ----------------------------------------------------------------------------
# VALIDACOES E AUXILIARES
# ----------------------------------------------------------------------------

def _validar_dataframe(
    dataframe: pd.DataFrame,
    permitir_vazio: bool = False
) -> pd.DataFrame:
    """Valida um DataFrame usado por um grafico.

    Args:
        dataframe (pd.DataFrame): DataFrame que sera validado.
        permitir_vazio (bool): Permite DataFrame sem registros.

    Returns:
        pd.DataFrame: O proprio DataFrame validado.

    Raises:
        DataFrameInvalidoError: Caso o objeto nao seja DataFrame.
        DataFrameVazioError: Caso esteja vazio e nao seja permitido.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise DataFrameInvalidoError("O objeto informado deve ser um DataFrame.")
    if not isinstance(permitir_vazio, bool):
        raise TypeError("O parametro 'permitir_vazio' deve ser booleano.")
    if dataframe.empty and not permitir_vazio:
        raise DataFrameVazioError("O DataFrame nao possui dados para o grafico.")
    return dataframe


def _validar_colunas(
    dataframe: pd.DataFrame,
    *colunas: str | None
) -> list[str]:
    """Valida a existencia das colunas informadas.

    Args:
        dataframe (pd.DataFrame): DataFrame consultado.
        *colunas (str | None): Colunas opcionais ou obrigatorias.

    Returns:
        list[str]: Nomes validos, ignorando None.

    Raises:
        ColunaNaoEncontradaError: Caso uma coluna seja invalida ou ausente.
    """
    _validar_dataframe(dataframe)
    resultado: list[str] = []
    for coluna in colunas:
        if coluna is None:
            continue
        if not isinstance(coluna, str) or not coluna.strip():
            raise ColunaNaoEncontradaError(
                "O nome da coluna deve ser uma string preenchida."
            )
        nome = coluna.strip()
        if nome not in dataframe.columns:
            raise ColunaNaoEncontradaError(
                f"A coluna '{nome}' nao existe no DataFrame."
            )
        resultado.append(nome)
    return resultado


def _validar_texto(valor: Any, nome: str, permitir_none: bool = False) -> str | None:
    """Valida um parametro textual.

    Args:
        valor (Any): Valor que sera validado.
        nome (str): Nome utilizado na mensagem.
        permitir_none (bool): Permite None como resultado.

    Returns:
        str | None: Texto normalizado ou None.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso o texto seja invalido.
    """
    if valor is None and permitir_none:
        return None
    if not isinstance(valor, str) or not valor.strip():
        raise ConfiguracaoGraficoInvalidaError(
            f"O parametro '{nome}' deve ser uma string preenchida."
        )
    return valor.strip()


def _validar_booleano(valor: bool, nome: str) -> bool:
    """Valida estritamente um booleano.

    Args:
        valor (bool): Valor que sera validado.
        nome (str): Nome utilizado na mensagem.

    Returns:
        bool: O proprio valor.

    Raises:
        TypeError: Caso o valor nao seja booleano.
    """
    if not isinstance(valor, bool):
        raise TypeError(f"O parametro '{nome}' deve ser booleano.")
    return valor


def _validar_altura(altura: int) -> int:
    """Valida a altura do grafico.

    Args:
        altura (int): Altura em pixels.

    Returns:
        int: Altura validada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso esteja fora dos limites.
    """
    if isinstance(altura, bool) or not isinstance(altura, int) or not 200 <= altura <= 2000:
        raise ConfiguracaoGraficoInvalidaError(
            "A altura deve ser um inteiro entre 200 e 2000 pixels."
        )
    return altura


def _validar_cores(cores: Sequence[str] | None) -> list[str]:
    """Valida uma paleta de cores.

    Args:
        cores (Sequence[str] | None): Cores CSS ou None.

    Returns:
        list[str]: Paleta informada ou paleta padrao.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso a paleta seja invalida.
    """
    if cores is None:
        return list(CORES_GRAFICOS)
    if isinstance(cores, (str, bytes)) or not isinstance(cores, Sequence):
        raise ConfiguracaoGraficoInvalidaError(
            "O parametro 'cores' deve ser uma sequencia nao textual."
        )
    resultado = list(cores)
    if not resultado or not all(isinstance(cor, str) and cor.strip() for cor in resultado):
        raise ConfiguracaoGraficoInvalidaError(
            "A paleta deve possuir cores textuais preenchidas."
        )
    return resultado


def ordenar_dataframe(
    dataframe: pd.DataFrame,
    coluna: str,
    ordenacao: str = "nenhuma"
) -> pd.DataFrame:
    """Ordena uma copia do DataFrame para exibicao.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        coluna (str): Coluna utilizada na ordenacao.
        ordenacao (str): crescente, decrescente ou nenhuma.

    Returns:
        pd.DataFrame: Copia ordenada ou preservada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso a ordenacao seja invalida.
    """
    nome = _validar_colunas(dataframe, coluna)[0]
    modo = _validar_texto(ordenacao, "ordenacao")
    assert isinstance(modo, str)
    modo = modo.lower()
    if modo not in ORDENACOES_VALIDAS:
        raise ConfiguracaoGraficoInvalidaError(
            "A ordenacao deve ser crescente, decrescente ou nenhuma."
        )
    if modo == "nenhuma":
        return dataframe.copy()
    return dataframe.sort_values(
        nome,
        ascending=modo == "crescente",
        kind="stable"
    ).reset_index(drop=True)


def configurar_layout_grafico(
    figura: go.Figure,
    *,
    titulo: str | None = None,
    titulo_eixo_x: str | None = None,
    titulo_eixo_y: str | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO,
    posicao_legenda: str = POSICAO_LEGENDA_PADRAO,
    exibir_grade_x: bool = False,
    exibir_grade_y: bool = True,
    template: str = TEMPLATE_GRAFICO_PADRAO,
    fonte: str = FONTE_GRAFICO_PADRAO
) -> go.Figure:
    """Aplica o padrao visual compartilhado a uma figura Plotly.

    Args:
        figura (go.Figure): Figura que sera configurada.
        titulo (str | None): Titulo principal.
        titulo_eixo_x (str | None): Titulo horizontal.
        titulo_eixo_y (str | None): Titulo vertical.
        altura (int): Altura em pixels.
        posicao_legenda (str): top, bottom, left, right ou none.
        exibir_grade_x (bool): Exibe grade vertical.
        exibir_grade_y (bool): Exibe grade horizontal.
        template (str): Template Plotly.
        fonte (str): Familia tipografica.

    Returns:
        go.Figure: A propria figura configurada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso a configuracao seja invalida.
    """
    if not isinstance(figura, go.Figure):
        raise ConfiguracaoGraficoInvalidaError(
            "O parametro 'figura' deve ser uma Figure do Plotly."
        )
    altura_validada = _validar_altura(altura)
    posicao = _validar_texto(posicao_legenda, "posicao_legenda")
    assert isinstance(posicao, str)
    posicao = posicao.lower()
    if posicao not in POSICOES_LEGENDA_VALIDAS:
        raise ConfiguracaoGraficoInvalidaError(
            "A legenda deve usar top, bottom, left, right ou none."
        )
    _validar_booleano(exibir_grade_x, "exibir_grade_x")
    _validar_booleano(exibir_grade_y, "exibir_grade_y")
    template_validado = _validar_texto(template, "template")
    fonte_validada = _validar_texto(fonte, "fonte")

    legendas = {
        "top": dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        "bottom": dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
        "left": dict(orientation="v", y=1, x=-0.18),
        "right": dict(orientation="v", y=1, x=1.02),
        "none": dict(visible=False),
    }
    figura.update_layout(
        title=titulo,
        height=altura_validada,
        template=template_validado,
        font=dict(family=fonte_validada),
        margin=dict(MARGENS_GRAFICO_PADRAO),
        legend=legendas[posicao],
        hoverlabel=dict(font_family=fonte_validada),
    )
    figura.update_xaxes(title=titulo_eixo_x, showgrid=exibir_grade_x)
    figura.update_yaxes(title=titulo_eixo_y, showgrid=exibir_grade_y)
    return figura


# ----------------------------------------------------------------------------
# CRIACAO DE GRAFICOS
# ----------------------------------------------------------------------------

def grafico_barras(
    dataframe: pd.DataFrame,
    eixo_x: str,
    eixo_y: str,
    *,
    cor: str | None = None,
    titulo: str | None = None,
    orientacao: str = "vertical",
    ordenacao: str = "nenhuma",
    modo: str = "group",
    texto: str | None = None,
    posicao_texto: str = "auto",
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO,
    posicao_legenda: str = POSICAO_LEGENDA_PADRAO
) -> go.Figure:
    """Cria um grafico de barras vertical ou horizontal.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        eixo_x (str): Coluna do eixo X.
        eixo_y (str): Coluna do eixo Y.
        cor (str | None): Coluna usada nas series.
        titulo (str | None): Titulo do grafico.
        orientacao (str): vertical ou horizontal.
        ordenacao (str): crescente, decrescente ou nenhuma.
        modo (str): group, stack, relative ou overlay.
        texto (str | None): Coluna exibida nas barras.
        posicao_texto (str): auto, inside, outside ou none.
        cores (Sequence[str] | None): Paleta do grafico.
        altura (int): Altura em pixels.
        posicao_legenda (str): Posicao da legenda.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso uma opcao seja invalida.
    """
    x, y, *extras = _validar_colunas(dataframe, eixo_x, eixo_y, cor, texto)
    cor_validada = cor.strip() if cor is not None else None
    texto_validado = texto.strip() if texto is not None else None
    orientacao_validada = _validar_texto(orientacao, "orientacao")
    assert isinstance(orientacao_validada, str)
    orientacao_validada = orientacao_validada.lower()
    if orientacao_validada not in ORIENTACOES_GRAFICO_VALIDAS:
        raise ConfiguracaoGraficoInvalidaError(
            "A orientacao deve ser vertical ou horizontal."
        )
    modo_validado = _validar_texto(modo, "modo")
    assert isinstance(modo_validado, str)
    modo_validado = modo_validado.lower()
    if modo_validado not in MODOS_BARRA_VALIDOS:
        raise ConfiguracaoGraficoInvalidaError("O modo de barras nao e suportado.")
    posicao = _validar_texto(posicao_texto, "posicao_texto")
    assert isinstance(posicao, str)
    posicao = posicao.lower()
    if posicao not in POSICOES_TEXTO_BARRA_VALIDAS:
        raise ConfiguracaoGraficoInvalidaError(
            "A posicao do texto deve ser auto, inside, outside ou none."
        )

    coluna_ordem = y if orientacao_validada == "vertical" else x
    dados = ordenar_dataframe(dataframe, coluna_ordem, ordenacao)
    figura = px.bar(
        dados,
        x=x,
        y=y,
        color=cor_validada,
        text=texto_validado,
        orientation="v" if orientacao_validada == "vertical" else "h",
        color_discrete_sequence=_validar_cores(cores),
        barmode=modo_validado,
    )
    figura.update_traces(textposition=posicao if posicao != "none" else "none")
    return configurar_layout_grafico(
        figura,
        titulo=titulo,
        titulo_eixo_x=x,
        titulo_eixo_y=y,
        altura=altura,
        posicao_legenda=posicao_legenda
    )


def grafico_linhas(
    dataframe: pd.DataFrame,
    eixo_x: str,
    eixo_y: str | Sequence[str],
    *,
    cor: str | None = None,
    titulo: str | None = None,
    marcadores: bool = True,
    ordenacao: str = "nenhuma",
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO,
    posicao_legenda: str = POSICAO_LEGENDA_PADRAO
) -> go.Figure:
    """Cria um grafico de linhas.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        eixo_x (str): Coluna horizontal.
        eixo_y (str | Sequence[str]): Uma ou mais colunas verticais.
        cor (str | None): Coluna usada nas series.
        titulo (str | None): Titulo principal.
        marcadores (bool): Exibe marcadores nos pontos.
        ordenacao (str): Ordenacao pelo eixo X.
        cores (Sequence[str] | None): Paleta do grafico.
        altura (int): Altura em pixels.
        posicao_legenda (str): Posicao da legenda.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ColunaNaoEncontradaError: Caso uma coluna nao exista.
    """
    x = _validar_colunas(dataframe, eixo_x)[0]
    y: str | list[str]
    if isinstance(eixo_y, str):
        y = _validar_colunas(dataframe, eixo_y)[0]
        titulo_y = y
    elif isinstance(eixo_y, Sequence):
        y = _validar_colunas(dataframe, *eixo_y)
        if not y:
            raise DadosGraficoInvalidosError("Informe ao menos uma coluna no eixo Y.")
        titulo_y = "Valor"
    else:
        raise ConfiguracaoGraficoInvalidaError(
            "O eixo Y deve ser uma coluna ou sequencia de colunas."
        )
    cor_validada = _validar_colunas(dataframe, cor)[0] if cor is not None else None
    _validar_booleano(marcadores, "marcadores")
    dados = ordenar_dataframe(dataframe, x, ordenacao)
    figura = px.line(
        dados,
        x=x,
        y=y,
        color=cor_validada,
        markers=marcadores,
        color_discrete_sequence=_validar_cores(cores)
    )
    return configurar_layout_grafico(
        figura, titulo=titulo, titulo_eixo_x=x, titulo_eixo_y=titulo_y,
        altura=altura, posicao_legenda=posicao_legenda
    )


def grafico_area(
    dataframe: pd.DataFrame,
    eixo_x: str,
    eixo_y: str,
    *,
    cor: str | None = None,
    titulo: str | None = None,
    ordenacao: str = "nenhuma",
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO
) -> go.Figure:
    """Cria um grafico de area.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        eixo_x (str): Coluna horizontal.
        eixo_y (str): Coluna vertical.
        cor (str | None): Coluna de series.
        titulo (str | None): Titulo principal.
        ordenacao (str): Ordenacao pelo eixo X.
        cores (Sequence[str] | None): Paleta.
        altura (int): Altura em pixels.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ColunaNaoEncontradaError: Caso alguma coluna nao exista.
    """
    x, y = _validar_colunas(dataframe, eixo_x, eixo_y)
    cor_validada = _validar_colunas(dataframe, cor)[0] if cor else None
    dados = ordenar_dataframe(dataframe, x, ordenacao)
    figura = px.area(
        dados, x=x, y=y, color=cor_validada,
        color_discrete_sequence=_validar_cores(cores)
    )
    return configurar_layout_grafico(
        figura, titulo=titulo, titulo_eixo_x=x, titulo_eixo_y=y, altura=altura
    )


def grafico_dispersao(
    dataframe: pd.DataFrame,
    eixo_x: str,
    eixo_y: str,
    *,
    cor: str | None = None,
    tamanho: str | None = None,
    texto_hover: str | None = None,
    titulo: str | None = None,
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO
) -> go.Figure:
    """Cria um grafico de dispersao ou bolhas.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        eixo_x (str): Coluna horizontal.
        eixo_y (str): Coluna vertical.
        cor (str | None): Coluna de cores.
        tamanho (str | None): Coluna de tamanho das bolhas.
        texto_hover (str | None): Coluna exibida no hover.
        titulo (str | None): Titulo principal.
        cores (Sequence[str] | None): Paleta.
        altura (int): Altura em pixels.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ColunaNaoEncontradaError: Caso alguma coluna nao exista.
    """
    x, y = _validar_colunas(dataframe, eixo_x, eixo_y)
    cor_validada = _validar_colunas(dataframe, cor)[0] if cor else None
    tamanho_validado = _validar_colunas(dataframe, tamanho)[0] if tamanho else None
    hover_validado = _validar_colunas(dataframe, texto_hover)[0] if texto_hover else None
    figura = px.scatter(
        dataframe, x=x, y=y, color=cor_validada, size=tamanho_validado,
        hover_name=hover_validado,
        color_discrete_sequence=_validar_cores(cores)
    )
    return configurar_layout_grafico(
        figura, titulo=titulo, titulo_eixo_x=x, titulo_eixo_y=y, altura=altura
    )


def grafico_pizza(
    dataframe: pd.DataFrame,
    nomes: str,
    valores: str,
    *,
    titulo: str | None = None,
    furo: float = 0.0,
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO,
    exibir_percentual: bool = True
) -> go.Figure:
    """Cria um grafico de pizza ou rosca.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        nomes (str): Coluna de categorias.
        valores (str): Coluna de valores.
        titulo (str | None): Titulo principal.
        furo (float): Tamanho interno entre 0 e 0.9.
        cores (Sequence[str] | None): Paleta.
        altura (int): Altura em pixels.
        exibir_percentual (bool): Exibe percentuais nos setores.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso o furo seja invalido.
    """
    nomes_validado, valores_validado = _validar_colunas(dataframe, nomes, valores)
    if isinstance(furo, bool) or not isinstance(furo, (int, float)) or not 0 <= furo <= 0.9:
        raise ConfiguracaoGraficoInvalidaError(
            "O furo deve ser numerico entre 0 e 0.9."
        )
    _validar_booleano(exibir_percentual, "exibir_percentual")
    figura = px.pie(
        dataframe, names=nomes_validado, values=valores_validado,
        hole=float(furo), color_discrete_sequence=_validar_cores(cores)
    )
    figura.update_traces(
        textinfo="percent+label" if exibir_percentual else "label"
    )
    return configurar_layout_grafico(
        figura, titulo=titulo, altura=altura, exibir_grade_y=False
    )


def grafico_rosca(
    dataframe: pd.DataFrame,
    nomes: str,
    valores: str,
    **kwargs: Any
) -> go.Figure:
    """Cria um grafico de rosca com furo padrao.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        nomes (str): Coluna de categorias.
        valores (str): Coluna de valores.
        **kwargs (Any): Opcoes adicionais de grafico_pizza.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso as opcoes sejam invalidas.
    """
    kwargs.setdefault("furo", 0.55)
    return grafico_pizza(dataframe, nomes, valores, **kwargs)


def grafico_histograma(
    dataframe: pd.DataFrame,
    coluna: str,
    *,
    cor: str | None = None,
    quantidade_bins: int | None = None,
    titulo: str | None = None,
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO
) -> go.Figure:
    """Cria um histograma.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        coluna (str): Coluna numerica ou categorica.
        cor (str | None): Coluna de series.
        quantidade_bins (int | None): Quantidade de faixas.
        titulo (str | None): Titulo principal.
        cores (Sequence[str] | None): Paleta.
        altura (int): Altura em pixels.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso a quantidade de bins seja invalida.
    """
    x = _validar_colunas(dataframe, coluna)[0]
    cor_validada = _validar_colunas(dataframe, cor)[0] if cor else None
    if quantidade_bins is not None and (
        isinstance(quantidade_bins, bool)
        or not isinstance(quantidade_bins, int)
        or quantidade_bins < 1
    ):
        raise ConfiguracaoGraficoInvalidaError(
            "A quantidade de bins deve ser inteiro positivo ou None."
        )
    figura = px.histogram(
        dataframe, x=x, color=cor_validada, nbins=quantidade_bins,
        color_discrete_sequence=_validar_cores(cores)
    )
    return configurar_layout_grafico(
        figura, titulo=titulo, titulo_eixo_x=x,
        titulo_eixo_y="Quantidade", altura=altura
    )


def grafico_caixa(
    dataframe: pd.DataFrame,
    eixo_y: str,
    *,
    eixo_x: str | None = None,
    cor: str | None = None,
    pontos: str | bool = "outliers",
    titulo: str | None = None,
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO
) -> go.Figure:
    """Cria um box plot.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        eixo_y (str): Coluna numerica.
        eixo_x (str | None): Coluna de categorias.
        cor (str | None): Coluna de cores.
        pontos (str | bool): Exibicao de pontos do box plot.
        titulo (str | None): Titulo principal.
        cores (Sequence[str] | None): Paleta.
        altura (int): Altura em pixels.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ColunaNaoEncontradaError: Caso uma coluna nao exista.
    """
    y = _validar_colunas(dataframe, eixo_y)[0]
    x = _validar_colunas(dataframe, eixo_x)[0] if eixo_x else None
    cor_validada = _validar_colunas(dataframe, cor)[0] if cor else None
    figura = px.box(
        dataframe, x=x, y=y, color=cor_validada, points=pontos,
        color_discrete_sequence=_validar_cores(cores)
    )
    return configurar_layout_grafico(
        figura, titulo=titulo, titulo_eixo_x=x,
        titulo_eixo_y=y, altura=altura
    )


def grafico_funil(
    dataframe: pd.DataFrame,
    etapas: str,
    valores: str,
    *,
    titulo: str | None = None,
    cor: str | None = None,
    cores: Sequence[str] | None = None,
    altura: int = ALTURA_GRAFICO_PADRAO
) -> go.Figure:
    """Cria um grafico de funil horizontal.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        etapas (str): Coluna com nomes das etapas.
        valores (str): Coluna com valores.
        titulo (str | None): Titulo principal.
        cor (str | None): Coluna de cores.
        cores (Sequence[str] | None): Paleta.
        altura (int): Altura em pixels.

    Returns:
        go.Figure: Figura Plotly configurada.

    Raises:
        ColunaNaoEncontradaError: Caso alguma coluna nao exista.
    """
    y, x = _validar_colunas(dataframe, etapas, valores)
    cor_validada = _validar_colunas(dataframe, cor)[0] if cor else None
    figura = px.funnel(
        dataframe, y=y, x=x, color=cor_validada,
        color_discrete_sequence=_validar_cores(cores)
    )
    return configurar_layout_grafico(
        figura, titulo=titulo, titulo_eixo_x=x,
        titulo_eixo_y=y, altura=altura
    )


# ----------------------------------------------------------------------------
# EXIBICAO E FABRICA
# ----------------------------------------------------------------------------

def exibir_grafico(
    figura: go.Figure,
    *,
    chave: str | None = None,
    largura: str | int = "stretch",
    altura: str | int = "content",
    tema: str | None = "streamlit",
    configuracao: Mapping[str, Any] | None = None,
    evento_selecao: str | Callable[..., Any] = "ignore",
    modo_selecao: Sequence[str] = ("points", "box", "lasso")
) -> Any:
    """Exibe uma figura Plotly no Streamlit.

    Args:
        figura (go.Figure): Figura que sera exibida.
        chave (str | None): Chave unica do componente.
        largura (str | int): stretch, content ou pixels.
        altura (str | int): content, stretch ou pixels.
        tema (str | None): Tema Streamlit ou None.
        configuracao (Mapping | None): Configuracao do Plotly.
        evento_selecao (str | Callable): ignore, rerun ou callback.
        modo_selecao (Sequence[str]): points, box e/ou lasso.

    Returns:
        Any: Retorno de st.plotly_chart.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso os parametros sejam invalidos.
    """
    if not isinstance(figura, go.Figure):
        raise ConfiguracaoGraficoInvalidaError(
            "O parametro 'figura' deve ser uma Figure do Plotly."
        )
    if not (
        isinstance(largura, int) and not isinstance(largura, bool) and largura > 0
    ) and largura not in LARGURAS_GRAFICO_VALIDAS:
        raise ConfiguracaoGraficoInvalidaError(
            "A largura deve ser stretch, content ou inteiro positivo."
        )
    if not (
        isinstance(altura, int) and not isinstance(altura, bool) and altura > 0
    ) and altura not in {"content", "stretch"}:
        raise ConfiguracaoGraficoInvalidaError(
            "A altura deve ser content, stretch ou inteiro positivo."
        )
    if isinstance(modo_selecao, (str, bytes)) or not isinstance(modo_selecao, Sequence):
        raise ConfiguracaoGraficoInvalidaError(
            "O modo de selecao deve ser uma sequencia."
        )
    modos = tuple(modo_selecao)
    if not modos or not set(modos).issubset({"points", "box", "lasso"}):
        raise ConfiguracaoGraficoInvalidaError(
            "Use somente points, box e lasso na selecao."
        )
    config = dict(CONFIGURACAO_GRAFICO_PADRAO)
    if configuracao is not None:
        if not isinstance(configuracao, Mapping):
            raise ConfiguracaoGraficoInvalidaError(
                "A configuracao do Plotly deve ser um mapeamento."
            )
        config.update(configuracao)
    return st.plotly_chart(
        figura,
        width=largura,
        height=altura,
        theme=tema,
        key=chave,
        on_select=evento_selecao,
        selection_mode=modos,
        config=config
    )


def criar_grafico(
    tipo: str,
    dataframe: pd.DataFrame,
    **configuracao: Any
) -> go.Figure:
    """Cria um grafico pelo nome do tipo.

    Args:
        tipo (str): Tipo registrado na fabrica.
        dataframe (pd.DataFrame): Dados de origem.
        **configuracao (Any): Parametros da funcao correspondente.

    Returns:
        go.Figure: Figura Plotly criada.

    Raises:
        ConfiguracaoGraficoInvalidaError: Caso o tipo seja desconhecido.
    """
    tipo_validado = _validar_texto(tipo, "tipo")
    assert isinstance(tipo_validado, str)
    tipo_validado = tipo_validado.lower()
    funcoes = {
        "barras": grafico_barras,
        "linhas": grafico_linhas,
        "area": grafico_area,
        "dispersao": grafico_dispersao,
        "pizza": grafico_pizza,
        "rosca": grafico_rosca,
        "histograma": grafico_histograma,
        "caixa": grafico_caixa,
        "funil": grafico_funil,
    }
    if tipo_validado not in funcoes:
        raise ConfiguracaoGraficoInvalidaError(
            f"O tipo de grafico '{tipo_validado}' nao e suportado."
        )
    return funcoes[tipo_validado](dataframe, **configuracao)


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "TIPOS_GRAFICO_VALIDOS",
    "MODOS_BARRA_VALIDOS",
    "POSICOES_TEXTO_BARRA_VALIDAS",
    "LARGURAS_GRAFICO_VALIDAS",
    "PREFIXO_CHAVE_GRAFICO",
    "ordenar_dataframe",
    "configurar_layout_grafico",
    "grafico_barras",
    "grafico_linhas",
    "grafico_area",
    "grafico_dispersao",
    "grafico_pizza",
    "grafico_rosca",
    "grafico_histograma",
    "grafico_caixa",
    "grafico_funil",
    "exibir_grafico",
    "criar_grafico"
]
