"""
============================================================
Modulo: DASHBOARD_STREAMLIT / metricas.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes reutilizaveis para calcular, formatar e exibir metricas e KPIs
    em dashboards Streamlit. O modulo suporta deltas, percentuais, moeda,
    graficos compactos, linhas de indicadores e configuracoes declarativas.
Dependencias:
    - pandas
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao de calculos e formatacao de indicadores.
        - Inclusao de metrica individual e linha automatica de KPIs.
============================================================
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal
from numbers import Number
from typing import Any

import pandas as pd
import streamlit as st

try:
    from .excecoes import (
        ColunaNaoEncontradaError,
        DataFrameInvalidoError,
        DataFrameVazioError,
        MetricaInvalidaError,
    )
except ImportError:
    from excecoes import (
        ColunaNaoEncontradaError,
        DataFrameInvalidoError,
        DataFrameVazioError,
        MetricaInvalidaError,
    )


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

CORES_DELTA_VALIDAS = {
    "normal", "inverse", "off", "red", "orange", "yellow",
    "green", "blue", "violet", "gray", "grey", "primary"
}
VISIBILIDADES_ROTULO_VALIDAS = {"visible", "hidden", "collapsed"}
TIPOS_GRAFICO_METRICA_VALIDOS = {"line", "bar", "area"}
SETAS_DELTA_VALIDAS = {"auto", "up", "down", "none"}
AGREGACOES_VALIDAS = {
    "soma", "media", "mediana", "minimo", "maximo", "contagem",
    "distintos", "primeiro", "ultimo"
}
LARGURAS_METRICA_VALIDAS = {"stretch", "content"}
ALTURAS_METRICA_VALIDAS = {"content", "stretch"}
PREFIXO_CHAVE_METRICA = "metrica"
FORMATO_NUMERO_PADRAO = "br"


# ----------------------------------------------------------------------------
# VALIDACOES INTERNAS
# ----------------------------------------------------------------------------

def _validar_texto(
    valor: Any,
    nome: str,
    permitir_none: bool = False
) -> str | None:
    """Valida um parametro textual.

    Args:
        valor (Any): Valor que sera validado.
        nome (str): Nome usado na mensagem de erro.
        permitir_none (bool): Permite None como retorno.

    Returns:
        str | None: Texto normalizado ou None.

    Raises:
        MetricaInvalidaError: Caso o valor seja invalido.
    """
    if valor is None and permitir_none:
        return None
    if not isinstance(valor, str) or not valor.strip():
        raise MetricaInvalidaError(
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


def _validar_dataframe(
    dataframe: pd.DataFrame,
    permitir_vazio: bool = False
) -> pd.DataFrame:
    """Valida um DataFrame usado em calculos de metricas.

    Args:
        dataframe (pd.DataFrame): DataFrame que sera validado.
        permitir_vazio (bool): Permite ausencia de registros.

    Returns:
        pd.DataFrame: O proprio DataFrame validado.

    Raises:
        DataFrameInvalidoError: Caso o objeto nao seja DataFrame.
        DataFrameVazioError: Caso esteja vazio e nao seja permitido.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise DataFrameInvalidoError("O objeto informado deve ser um DataFrame.")
    _validar_booleano(permitir_vazio, "permitir_vazio")
    if dataframe.empty and not permitir_vazio:
        raise DataFrameVazioError("O DataFrame nao possui dados para a metrica.")
    return dataframe


def _validar_coluna(dataframe: pd.DataFrame, coluna: str) -> str:
    """Valida a existencia de uma coluna no DataFrame.

    Args:
        dataframe (pd.DataFrame): DataFrame consultado.
        coluna (str): Nome da coluna obrigatoria.

    Returns:
        str: Nome normalizado da coluna.

    Raises:
        ColunaNaoEncontradaError: Caso a coluna nao exista.
    """
    _validar_dataframe(dataframe)
    if not isinstance(coluna, str) or not coluna.strip():
        raise ColunaNaoEncontradaError("O nome da coluna deve ser preenchido.")
    nome = coluna.strip()
    if nome not in dataframe.columns:
        raise ColunaNaoEncontradaError(
            f"A coluna '{nome}' nao existe no DataFrame."
        )
    return nome


def _validar_dimensao(
    valor: str | int,
    nome: str,
    textos_validos: set[str]
) -> str | int:
    """Valida largura ou altura da metrica.

    Args:
        valor (str | int): Texto suportado ou pixels.
        nome (str): Nome usado na mensagem.
        textos_validos (set[str]): Valores textuais permitidos.

    Returns:
        str | int: Dimensao validada.

    Raises:
        MetricaInvalidaError: Caso a dimensao seja invalida.
    """
    if isinstance(valor, int) and not isinstance(valor, bool) and valor > 0:
        return valor
    if isinstance(valor, str) and valor.strip().lower() in textos_validos:
        return valor.strip().lower()
    raise MetricaInvalidaError(
        f"O parametro '{nome}' possui uma dimensao invalida."
    )


def _validar_numero(valor: Any, nome: str, permitir_none: bool = False) -> Any:
    """Valida um valor numerico de metrica.

    Args:
        valor (Any): Valor que sera validado.
        nome (str): Nome usado na mensagem.
        permitir_none (bool): Permite None.

    Returns:
        Any: O proprio valor validado.

    Raises:
        MetricaInvalidaError: Caso o valor nao seja numerico.
    """
    if valor is None and permitir_none:
        return None
    if isinstance(valor, bool) or not isinstance(valor, (Number, Decimal)):
        raise MetricaInvalidaError(f"O parametro '{nome}' deve ser numerico.")
    return valor


# ----------------------------------------------------------------------------
# CALCULOS E FORMATACAO
# ----------------------------------------------------------------------------

def calcular_delta(valor_atual: Number, valor_anterior: Number) -> float:
    """Calcula a diferenca absoluta entre dois valores.

    Args:
        valor_atual (Number): Valor do periodo atual.
        valor_anterior (Number): Valor usado na comparacao.

    Returns:
        float: Diferenca entre atual e anterior.

    Raises:
        MetricaInvalidaError: Caso algum valor nao seja numerico.
    """
    atual = _validar_numero(valor_atual, "valor_atual")
    anterior = _validar_numero(valor_anterior, "valor_anterior")
    return float(atual - anterior)


def calcular_variacao_percentual(
    valor_atual: Number,
    valor_anterior: Number,
    *,
    casas_decimais: int = 2,
    zero_anterior: float | None = None
) -> float | None:
    """Calcula a variacao percentual entre dois valores.

    Args:
        valor_atual (Number): Valor do periodo atual.
        valor_anterior (Number): Valor usado na comparacao.
        casas_decimais (int): Quantidade de casas do resultado.
        zero_anterior (float | None): Retorno opcional quando anterior e zero.

    Returns:
        float | None: Variacao percentual ou valor alternativo.

    Raises:
        MetricaInvalidaError: Caso valores ou casas sejam invalidos.
    """
    atual = _validar_numero(valor_atual, "valor_atual")
    anterior = _validar_numero(valor_anterior, "valor_anterior")
    if (
        isinstance(casas_decimais, bool)
        or not isinstance(casas_decimais, int)
        or casas_decimais < 0
    ):
        raise MetricaInvalidaError(
            "As casas decimais devem ser um inteiro nao negativo."
        )
    if zero_anterior is not None:
        _validar_numero(zero_anterior, "zero_anterior")
    if anterior == 0:
        return zero_anterior
    return round(float((atual - anterior) / abs(anterior) * 100), casas_decimais)


def formatar_numero(
    valor: Number | None,
    *,
    casas_decimais: int = 0,
    prefixo: str = "",
    sufixo: str = "",
    separador_milhar: str = ".",
    separador_decimal: str = ",",
    valor_nulo: str = "-"
) -> str:
    """Formata um numero no padrao brasileiro ou personalizado.

    Args:
        valor (Number | None): Valor a ser formatado.
        casas_decimais (int): Quantidade de casas decimais.
        prefixo (str): Texto antes do numero.
        sufixo (str): Texto depois do numero.
        separador_milhar (str): Caractere de milhares.
        separador_decimal (str): Caractere decimal.
        valor_nulo (str): Texto usado quando valor e None.

    Returns:
        str: Numero pronto para exibicao.

    Raises:
        MetricaInvalidaError: Caso a configuracao seja invalida.
    """
    if valor is None:
        return _validar_texto(valor_nulo, "valor_nulo")  # type: ignore[return-value]
    numero = _validar_numero(valor, "valor")
    if (
        isinstance(casas_decimais, bool)
        or not isinstance(casas_decimais, int)
        or casas_decimais < 0
    ):
        raise MetricaInvalidaError(
            "As casas decimais devem ser um inteiro nao negativo."
        )
    if not all(isinstance(item, str) for item in (
        prefixo, sufixo, separador_milhar, separador_decimal
    )):
        raise MetricaInvalidaError("Os elementos de formatacao devem ser textos.")
    if separador_milhar == separador_decimal:
        raise MetricaInvalidaError(
            "Os separadores de milhar e decimal devem ser diferentes."
        )
    texto = f"{float(numero):,.{casas_decimais}f}"
    temporario = "__MILHAR__"
    texto = texto.replace(",", temporario).replace(".", separador_decimal)
    texto = texto.replace(temporario, separador_milhar)
    return f"{prefixo}{texto}{sufixo}"


def formatar_percentual(
    valor: Number | None,
    *,
    casas_decimais: int = 1,
    valor_em_proporcao: bool = False
) -> str:
    """Formata um valor percentual.

    Args:
        valor (Number | None): Percentual ou proporcao.
        casas_decimais (int): Casas decimais.
        valor_em_proporcao (bool): Multiplica o valor por cem.

    Returns:
        str: Percentual formatado.

    Raises:
        MetricaInvalidaError: Caso o valor seja invalido.
    """
    _validar_booleano(valor_em_proporcao, "valor_em_proporcao")
    if valor is None:
        return "-"
    numero = _validar_numero(valor, "valor")
    if valor_em_proporcao:
        numero *= 100
    return formatar_numero(
        numero,
        casas_decimais=casas_decimais,
        sufixo="%"
    )


def formatar_moeda(
    valor: Number | None,
    *,
    simbolo: str = "R$ ",
    casas_decimais: int = 2
) -> str:
    """Formata um valor monetario.

    Args:
        valor (Number | None): Valor monetario.
        simbolo (str): Simbolo ou codigo da moeda.
        casas_decimais (int): Casas decimais.

    Returns:
        str: Valor monetario formatado.

    Raises:
        MetricaInvalidaError: Caso a configuracao seja invalida.
    """
    if not isinstance(simbolo, str):
        raise MetricaInvalidaError("O simbolo da moeda deve ser texto.")
    return formatar_numero(
        valor,
        casas_decimais=casas_decimais,
        prefixo=simbolo
    )


def calcular_metrica_dataframe(
    dataframe: pd.DataFrame,
    coluna: str,
    agregacao: str = "soma"
) -> Any:
    """Calcula uma metrica a partir de uma coluna do DataFrame.

    Args:
        dataframe (pd.DataFrame): Dados de origem.
        coluna (str): Coluna usada no calculo.
        agregacao (str): Operacao cadastrada.

    Returns:
        Any: Resultado da agregacao.

    Raises:
        MetricaInvalidaError: Caso a agregacao seja desconhecida.
    """
    nome = _validar_coluna(dataframe, coluna)
    operacao = _validar_texto(agregacao, "agregacao")
    assert isinstance(operacao, str)
    operacao = operacao.lower()
    if operacao not in AGREGACOES_VALIDAS:
        raise MetricaInvalidaError(
            f"A agregacao '{operacao}' nao e suportada."
        )
    serie = dataframe[nome]
    funcoes: dict[str, Callable[[], Any]] = {
        "soma": serie.sum,
        "media": serie.mean,
        "mediana": serie.median,
        "minimo": serie.min,
        "maximo": serie.max,
        "contagem": serie.count,
        "distintos": serie.nunique,
        "primeiro": lambda: serie.iloc[0],
        "ultimo": lambda: serie.iloc[-1],
    }
    return funcoes[operacao]()


# ----------------------------------------------------------------------------
# EXIBICAO DAS METRICAS
# ----------------------------------------------------------------------------

def exibir_metrica(
    rotulo: str,
    valor: int | float | Decimal | str | None,
    *,
    delta: int | float | Decimal | str | None = None,
    cor_delta: str = "normal",
    ajuda: str | None = None,
    icone: str | None = None,
    visibilidade_rotulo: str = "visible",
    borda: bool = False,
    largura: str | int = "stretch",
    altura: str | int = "content",
    dados_grafico: Sequence[Any] | None = None,
    tipo_grafico: str = "line",
    seta_delta: str = "auto",
    formato: str | None = None,
    descricao_delta: str | None = None
) -> Any:
    """Exibe uma metrica completa usando st.metric.

    Args:
        rotulo (str): Titulo do indicador.
        valor (int | float | Decimal | str | None): Valor principal.
        delta (int | float | Decimal | str | None): Variacao exibida.
        cor_delta (str): Cor ou comportamento da variacao.
        ajuda (str | None): Tooltip da metrica.
        icone (str | None): Emoji ou Material icon.
        visibilidade_rotulo (str): visible, hidden ou collapsed.
        borda (bool): Exibe borda no card.
        largura (str | int): stretch, content ou pixels.
        altura (str | int): content, stretch ou pixels.
        dados_grafico (Sequence[Any] | None): Serie do mini grafico.
        tipo_grafico (str): line, bar ou area.
        seta_delta (str): auto, up, down ou none.
        formato (str | None): Formato nativo do Streamlit.
        descricao_delta (str | None): Descricao acessivel da variacao.

    Returns:
        Any: Retorno do componente st.metric.

    Raises:
        MetricaInvalidaError: Caso alguma configuracao seja invalida.
    """
    nome = _validar_texto(rotulo, "rotulo")
    assert isinstance(nome, str)
    if valor is not None and isinstance(valor, bool):
        raise MetricaInvalidaError("O valor da metrica nao pode ser booleano.")
    if valor is not None and not isinstance(valor, (Number, Decimal, str)):
        raise MetricaInvalidaError("O valor da metrica possui tipo invalido.")
    cor = _validar_texto(cor_delta, "cor_delta")
    visibilidade = _validar_texto(
        visibilidade_rotulo, "visibilidade_rotulo"
    )
    grafico = _validar_texto(tipo_grafico, "tipo_grafico")
    seta = _validar_texto(seta_delta, "seta_delta")
    assert all(isinstance(item, str) for item in (cor, visibilidade, grafico, seta))
    cor = cor.lower()
    visibilidade = visibilidade.lower()
    grafico = grafico.lower()
    seta = seta.lower()
    if cor not in CORES_DELTA_VALIDAS:
        raise MetricaInvalidaError("A cor do delta nao e suportada.")
    if visibilidade not in VISIBILIDADES_ROTULO_VALIDAS:
        raise MetricaInvalidaError("A visibilidade do rotulo nao e suportada.")
    if grafico not in TIPOS_GRAFICO_METRICA_VALIDOS:
        raise MetricaInvalidaError("O tipo do grafico da metrica nao e suportado.")
    if seta not in SETAS_DELTA_VALIDAS:
        raise MetricaInvalidaError("A orientacao da seta do delta nao e suportada.")
    _validar_booleano(borda, "borda")
    if dados_grafico is not None and (
        isinstance(dados_grafico, (str, bytes))
        or not isinstance(dados_grafico, Sequence)
    ):
        raise MetricaInvalidaError(
            "Os dados do grafico devem ser uma sequencia ou None."
        )

    return st.metric(
        label=nome,
        value=valor,
        delta=delta,
        delta_color=cor,
        help=_validar_texto(ajuda, "ajuda", permitir_none=True),
        icon=None if icone is None else _validar_texto(icone, "icone"),
        label_visibility=visibilidade,
        border=borda,
        width=_validar_dimensao(largura, "largura", LARGURAS_METRICA_VALIDAS),
        height=_validar_dimensao(altura, "altura", ALTURAS_METRICA_VALIDAS),
        chart_data=None if dados_grafico is None else list(dados_grafico),
        chart_type=grafico,
        delta_arrow=seta,
        format=_validar_texto(formato, "formato", permitir_none=True),
        delta_description=_validar_texto(
            descricao_delta, "descricao_delta", permitir_none=True
        )
    )


def criar_metrica(configuracao: Mapping[str, Any]) -> Any:
    """Cria uma metrica a partir de uma configuracao declarativa.

    Args:
        configuracao (Mapping[str, Any]): Parametros de exibir_metrica.

    Returns:
        Any: Retorno da metrica criada.

    Raises:
        MetricaInvalidaError: Caso a configuracao nao seja mapeamento.
    """
    if not isinstance(configuracao, Mapping):
        raise MetricaInvalidaError("A configuracao deve ser um mapeamento.")
    return exibir_metrica(**dict(configuracao))


def criar_linha_metricas(
    metricas: Sequence[Mapping[str, Any]],
    *,
    espacamento: str | int | None = "small",
    alinhamento_vertical: str = "top",
    borda_colunas: bool = False,
    largura: str | int = "stretch",
    quebrar_linha: bool = True
) -> list[Any]:
    """Cria uma linha responsiva de metricas declarativas.

    Args:
        metricas (Sequence[Mapping]): Configuracoes das metricas.
        espacamento (str | int | None): Espaco entre colunas.
        alinhamento_vertical (str): top, center ou bottom.
        borda_colunas (bool): Exibe borda em cada coluna.
        largura (str | int): stretch ou pixels.
        quebrar_linha (bool): Permite empilhamento responsivo.

    Returns:
        list[Any]: Retornos gerados por st.metric.

    Raises:
        MetricaInvalidaError: Caso a colecao seja invalida.
    """
    if isinstance(metricas, (str, bytes)) or not isinstance(metricas, Sequence):
        raise MetricaInvalidaError("As metricas devem ser uma sequencia.")
    configuracoes = list(metricas)
    if not configuracoes:
        raise MetricaInvalidaError("Informe ao menos uma metrica.")
    if not all(isinstance(item, Mapping) for item in configuracoes):
        raise MetricaInvalidaError(
            "Cada configuracao de metrica deve ser um mapeamento."
        )
    alinhamento = _validar_texto(
        alinhamento_vertical, "alinhamento_vertical"
    )
    assert isinstance(alinhamento, str)
    alinhamento = alinhamento.lower()
    if alinhamento not in {"top", "center", "bottom"}:
        raise MetricaInvalidaError(
            "O alinhamento deve ser top, center ou bottom."
        )
    _validar_booleano(borda_colunas, "borda_colunas")
    _validar_booleano(quebrar_linha, "quebrar_linha")
    if espacamento is not None:
        if isinstance(espacamento, int) and not isinstance(espacamento, bool):
            if espacamento < 0:
                raise MetricaInvalidaError("O espacamento nao pode ser negativo.")
        elif espacamento not in {
            "xxsmall", "xsmall", "small", "medium", "large", "xlarge", "xxlarge"
        }:
            raise MetricaInvalidaError("O espacamento informado e invalido.")

    colunas = st.columns(
        len(configuracoes),
        gap=espacamento,
        vertical_alignment=alinhamento,
        border=borda_colunas,
        width=_validar_dimensao(largura, "largura", {"stretch"}),
        wrap=quebrar_linha
    )
    resultados: list[Any] = []
    for coluna, configuracao in zip(colunas, configuracoes):
        with coluna:
            resultados.append(criar_metrica(configuracao))
    return resultados


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "CORES_DELTA_VALIDAS",
    "VISIBILIDADES_ROTULO_VALIDAS",
    "TIPOS_GRAFICO_METRICA_VALIDOS",
    "SETAS_DELTA_VALIDAS",
    "AGREGACOES_VALIDAS",
    "LARGURAS_METRICA_VALIDAS",
    "ALTURAS_METRICA_VALIDAS",
    "PREFIXO_CHAVE_METRICA",
    "FORMATO_NUMERO_PADRAO",
    "calcular_delta",
    "calcular_variacao_percentual",
    "formatar_numero",
    "formatar_percentual",
    "formatar_moeda",
    "calcular_metrica_dataframe",
    "exibir_metrica",
    "criar_metrica",
    "criar_linha_metricas"
]
