"""
============================================================
Modulo: DASHBOARD_STREAMLIT / filtros.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes simples para criar filtros Streamlit e aplicar as selecoes em
    DataFrames pandas. O modulo oferece filtros individuais e uma barra
    automatica baseada em configuracoes curtas e faceis de reutilizar.
Funcoes disponiveis:
    - obter_opcoes_coluna()
    - filtro_selecao()
    - filtro_multisselecao()
    - filtro_data()
    - filtro_periodo()
    - filtro_numerico()
    - filtro_intervalo_numerico()
    - filtro_texto()
    - filtro_booleano()
    - aplicar_filtros_dataframe()
    - criar_barra_filtros()
    - limpar_filtros()
Dependencias:
    - pandas
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao dos filtros individuais.
        - Inclusao da filtragem de DataFrames e barra automatica.
============================================================
"""

from __future__ import annotations

# ----------------------------------------------------------------------------
# IMPORTACOES
# ----------------------------------------------------------------------------

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

import pandas as pd
import streamlit as st

try:
    from .constantes import TEXTO_OPCAO_TODOS, TIPOS_FILTRO
    from .excecoes import (
        ColunaNaoEncontradaError,
        ConfiguracaoFiltroInvalidaError,
        DataFrameInvalidoError,
        ValorFiltroInvalidoError,
    )
except ImportError:
    from constantes import TEXTO_OPCAO_TODOS, TIPOS_FILTRO
    from excecoes import (
        ColunaNaoEncontradaError,
        ConfiguracaoFiltroInvalidaError,
        DataFrameInvalidoError,
        ValorFiltroInvalidoError,
    )


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

LOCAL_FILTROS_VALIDOS = {"principal", "sidebar"}
ESPACOS_COLUNAS_VALIDOS = {"small", "medium", "large"}
QUANTIDADE_MAXIMA_COLUNAS = 6
FORMATO_DATA_PADRAO = "DD/MM/YYYY"
PREFIXO_CHAVE_FILTRO = "filtro"


# ----------------------------------------------------------------------------
# VALIDACOES INTERNAS
# ----------------------------------------------------------------------------

def _validar_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Valida se o objeto informado e um DataFrame pandas.

    Args:
        dataframe (pd.DataFrame): Objeto que sera validado.

    Returns:
        pd.DataFrame: O proprio DataFrame validado.

    Raises:
        DataFrameInvalidoError: Caso o objeto nao seja DataFrame.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise DataFrameInvalidoError("O objeto informado deve ser um DataFrame.")
    return dataframe


def _validar_coluna(dataframe: pd.DataFrame, coluna: str) -> str:
    """
    Valida a existencia de uma coluna no DataFrame.

    Args:
        dataframe (pd.DataFrame): DataFrame que sera consultado.
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


def _validar_texto(valor: Any, nome: str) -> str:
    """
    Valida um texto obrigatorio.

    Args:
        valor (Any): Valor que sera validado.
        nome (str): Nome utilizado na mensagem de erro.

    Returns:
        str: Texto sem espacos externos.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso o texto seja invalido.
    """
    if not isinstance(valor, str) or not valor.strip():
        raise ConfiguracaoFiltroInvalidaError(
            f"O parametro '{nome}' deve ser uma string preenchida."
        )
    return valor.strip()


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


def _validar_opcoes(opcoes: Sequence[Any]) -> list[Any]:
    """
    Valida e converte uma sequencia de opcoes.

    Args:
        opcoes (Sequence[Any]): Valores disponiveis no filtro.

    Returns:
        list[Any]: Lista de opcoes preservando a ordem.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso opcoes seja invalida.
    """
    if isinstance(opcoes, (str, bytes)) or not isinstance(opcoes, Sequence):
        raise ConfiguracaoFiltroInvalidaError(
            "O parametro 'opcoes' deve ser uma sequencia nao textual."
        )
    return list(opcoes)


def _gerar_chave(chave: str | None, titulo: str) -> str:
    """
    Retorna uma chave informada ou gera uma chave simples pelo titulo.

    Args:
        chave (str | None): Chave personalizada do widget.
        titulo (str): Titulo utilizado como base da chave.

    Returns:
        str: Chave pronta para uso no Streamlit.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso a chave seja invalida.
    """
    if chave is not None:
        return _validar_texto(chave, "chave")
    base = "_".join(_validar_texto(titulo, "titulo").lower().split())
    return f"{PREFIXO_CHAVE_FILTRO}_{base}"


def _obter_container(local: str) -> Any:
    """
    Retorna o modulo principal ou a sidebar para renderizacao.

    Args:
        local (str): Local principal ou sidebar.

    Returns:
        Any: Objeto Streamlit que recebera o widget.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso o local seja invalido.
    """
    local_normalizado = _validar_texto(local, "local").lower()
    if local_normalizado not in LOCAL_FILTROS_VALIDOS:
        raise ConfiguracaoFiltroInvalidaError(
            "O parametro 'local' deve ser 'principal' ou 'sidebar'."
        )
    return st.sidebar if local_normalizado == "sidebar" else st


# ----------------------------------------------------------------------------
# OPCOES E WIDGETS
# ----------------------------------------------------------------------------

def obter_opcoes_coluna(
    dataframe: pd.DataFrame,
    coluna: str,
    incluir_nulos: bool = False,
    ordenar: bool = True
) -> list[Any]:
    """
    Obtem os valores unicos de uma coluna.

    Args:
        dataframe (pd.DataFrame): DataFrame de origem.
        coluna (str): Coluna utilizada para obter as opcoes.
        incluir_nulos (bool): Mantem valores nulos na lista.
        ordenar (bool): Ordena as opcoes pelo texto exibido.

    Returns:
        list[Any]: Valores unicos da coluna.

    Raises:
        ColunaNaoEncontradaError: Caso a coluna nao exista.
    """
    nome = _validar_coluna(dataframe, coluna)
    _validar_booleano(incluir_nulos, "incluir_nulos")
    _validar_booleano(ordenar, "ordenar")
    serie = dataframe[nome]
    if not incluir_nulos:
        serie = serie.dropna()
    opcoes = list(pd.unique(serie))
    if ordenar:
        opcoes.sort(key=lambda valor: str(valor).casefold())
    return opcoes


def filtro_selecao(
    titulo: str,
    opcoes: Sequence[Any],
    valor_padrao: Any = None,
    incluir_todos: bool = True,
    texto_todos: str = TEXTO_OPCAO_TODOS,
    chave: str | None = None,
    local: str = "principal",
    ajuda: str | None = None
) -> Any:
    """
    Exibe um filtro de selecao unica.

    Args:
        titulo (str): Rotulo do filtro.
        opcoes (Sequence[Any]): Opcoes disponiveis.
        valor_padrao (Any): Valor inicialmente selecionado.
        incluir_todos (bool): Inclui uma opcao que representa ausencia de filtro.
        texto_todos (str): Texto da opcao de todos.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.
        ajuda (str | None): Texto de ajuda do widget.

    Returns:
        Any: Valor selecionado ou None quando todos estiver ativo.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso a configuracao seja invalida.
    """
    rotulo = _validar_texto(titulo, "titulo")
    valores = _validar_opcoes(opcoes)
    _validar_booleano(incluir_todos, "incluir_todos")
    marcador_todos = _validar_texto(texto_todos, "texto_todos")
    exibidas = [marcador_todos, *valores] if incluir_todos else valores

    if valor_padrao is None:
        indice = 0 if exibidas else None
    else:
        if valor_padrao not in valores:
            raise ValorFiltroInvalidoError(
                "O valor padrao nao pertence as opcoes do filtro."
            )
        indice = exibidas.index(valor_padrao)

    resultado = _obter_container(local).selectbox(
        rotulo,
        exibidas,
        index=indice,
        key=_gerar_chave(chave, rotulo),
        help=ajuda
    )
    return None if incluir_todos and resultado == marcador_todos else resultado


def filtro_multisselecao(
    titulo: str,
    opcoes: Sequence[Any],
    valores_padrao: Sequence[Any] | None = None,
    chave: str | None = None,
    local: str = "principal",
    ajuda: str | None = None,
    maximo_selecoes: int | None = None
) -> list[Any]:
    """
    Exibe um filtro de selecao multipla.

    Args:
        titulo (str): Rotulo do filtro.
        opcoes (Sequence[Any]): Opcoes disponiveis.
        valores_padrao (Sequence[Any] | None): Valores inicialmente selecionados.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.
        ajuda (str | None): Texto de ajuda do widget.
        maximo_selecoes (int | None): Limite opcional de selecoes.

    Returns:
        list[Any]: Valores selecionados.

    Raises:
        ValorFiltroInvalidoError: Caso um padrao nao pertença as opcoes.
    """
    rotulo = _validar_texto(titulo, "titulo")
    valores = _validar_opcoes(opcoes)
    padroes = [] if valores_padrao is None else _validar_opcoes(valores_padrao)
    invalidos = [valor for valor in padroes if valor not in valores]
    if invalidos:
        raise ValorFiltroInvalidoError(
            f"Valores padrao nao encontrados: {invalidos}."
        )
    if maximo_selecoes is not None and (
        isinstance(maximo_selecoes, bool)
        or not isinstance(maximo_selecoes, int)
        or maximo_selecoes < 1
    ):
        raise ConfiguracaoFiltroInvalidaError(
            "O limite de selecoes deve ser um inteiro positivo ou None."
        )

    resultado = _obter_container(local).multiselect(
        rotulo,
        valores,
        default=padroes,
        key=_gerar_chave(chave, rotulo),
        help=ajuda,
        max_selections=maximo_selecoes
    )
    return list(resultado)


def filtro_data(
    titulo: str,
    valor_padrao: date | datetime | str | None = None,
    data_minima: date | datetime | str | None = None,
    data_maxima: date | datetime | str | None = None,
    chave: str | None = None,
    local: str = "principal",
    formato: str = FORMATO_DATA_PADRAO
) -> Any:
    """
    Exibe um filtro para uma unica data.

    Args:
        titulo (str): Rotulo do filtro.
        valor_padrao (date | datetime | str | None): Data inicial.
        data_minima (date | datetime | str | None): Menor data selecionavel.
        data_maxima (date | datetime | str | None): Maior data selecionavel.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.
        formato (str): Formato visual aceito pelo Streamlit.

    Returns:
        Any: Data selecionada.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso titulo ou formato seja invalido.
    """
    rotulo = _validar_texto(titulo, "titulo")
    return _obter_container(local).date_input(
        rotulo,
        value=valor_padrao,
        min_value=data_minima,
        max_value=data_maxima,
        key=_gerar_chave(chave, rotulo),
        format=_validar_texto(formato, "formato")
    )


def filtro_periodo(
    titulo: str,
    inicio: date | datetime | str | None = None,
    fim: date | datetime | str | None = None,
    data_minima: date | datetime | str | None = None,
    data_maxima: date | datetime | str | None = None,
    chave: str | None = None,
    local: str = "principal",
    formato: str = FORMATO_DATA_PADRAO
) -> tuple[Any, ...]:
    """
    Exibe um filtro para intervalo de datas.

    Args:
        titulo (str): Rotulo do filtro.
        inicio (date | datetime | str | None): Data inicial padrao.
        fim (date | datetime | str | None): Data final padrao.
        data_minima (date | datetime | str | None): Menor data selecionavel.
        data_maxima (date | datetime | str | None): Maior data selecionavel.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.
        formato (str): Formato visual aceito pelo Streamlit.

    Returns:
        tuple[Any, ...]: Intervalo selecionado com zero, uma ou duas datas.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso titulo ou formato seja invalido.
    """
    rotulo = _validar_texto(titulo, "titulo")
    valores = [valor for valor in (inicio, fim) if valor is not None]
    resultado = _obter_container(local).date_input(
        rotulo,
        value=valores,
        min_value=data_minima,
        max_value=data_maxima,
        key=_gerar_chave(chave, rotulo),
        format=_validar_texto(formato, "formato")
    )
    if resultado is None:
        return tuple()
    if isinstance(resultado, tuple):
        return resultado
    if isinstance(resultado, list):
        return tuple(resultado)
    return (resultado,)


def filtro_numerico(
    titulo: str,
    valor_padrao: int | float = 0,
    minimo: int | float | None = None,
    maximo: int | float | None = None,
    passo: int | float = 1,
    chave: str | None = None,
    local: str = "principal",
    formato: str | None = None
) -> int | float:
    """
    Exibe um filtro de entrada numerica.

    Args:
        titulo (str): Rotulo do filtro.
        valor_padrao (int | float): Valor inicial.
        minimo (int | float | None): Menor valor permitido.
        maximo (int | float | None): Maior valor permitido.
        passo (int | float): Incremento do campo.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.
        formato (str | None): Formato numerico opcional.

    Returns:
        int | float: Valor informado.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso os limites sejam invalidos.
    """
    rotulo = _validar_texto(titulo, "titulo")
    numeros = [valor_padrao, passo]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in numeros):
        raise ConfiguracaoFiltroInvalidaError(
            "Valor padrao e passo devem ser numericos."
        )
    if passo <= 0:
        raise ConfiguracaoFiltroInvalidaError("O passo deve ser maior que zero.")
    if minimo is not None and maximo is not None and minimo > maximo:
        raise ConfiguracaoFiltroInvalidaError("O minimo nao pode superar o maximo.")
    if minimo is not None and valor_padrao < minimo:
        raise ValorFiltroInvalidoError("O valor padrao e menor que o minimo.")
    if maximo is not None and valor_padrao > maximo:
        raise ValorFiltroInvalidoError("O valor padrao e maior que o maximo.")

    parametros: dict[str, Any] = {
        "label": rotulo,
        "value": valor_padrao,
        "min_value": minimo,
        "max_value": maximo,
        "step": passo,
        "key": _gerar_chave(chave, rotulo)
    }
    if formato is not None:
        parametros["format"] = _validar_texto(formato, "formato")
    return _obter_container(local).number_input(**parametros)


def filtro_intervalo_numerico(
    titulo: str,
    minimo: int | float,
    maximo: int | float,
    valor_padrao: tuple[int | float, int | float] | None = None,
    passo: int | float = 1,
    chave: str | None = None,
    local: str = "principal"
) -> tuple[int | float, int | float]:
    """
    Exibe um slider para intervalo numerico.

    Args:
        titulo (str): Rotulo do filtro.
        minimo (int | float): Menor valor permitido.
        maximo (int | float): Maior valor permitido.
        valor_padrao (tuple | None): Intervalo inicialmente selecionado.
        passo (int | float): Incremento do slider.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.

    Returns:
        tuple[int | float, int | float]: Intervalo selecionado.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso limites ou passo sejam invalidos.
    """
    rotulo = _validar_texto(titulo, "titulo")
    numeros = (minimo, maximo, passo)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in numeros):
        raise ConfiguracaoFiltroInvalidaError(
            "Minimo, maximo e passo devem ser numericos."
        )
    if minimo > maximo or passo <= 0:
        raise ConfiguracaoFiltroInvalidaError(
            "O intervalo e o passo devem possuir valores validos."
        )
    padrao = (minimo, maximo) if valor_padrao is None else valor_padrao
    if (
        not isinstance(padrao, tuple)
        or len(padrao) != 2
        or padrao[0] < minimo
        or padrao[1] > maximo
        or padrao[0] > padrao[1]
    ):
        raise ValorFiltroInvalidoError("O intervalo padrao e invalido.")
    resultado = _obter_container(local).slider(
        rotulo,
        min_value=minimo,
        max_value=maximo,
        value=padrao,
        step=passo,
        key=_gerar_chave(chave, rotulo)
    )
    return tuple(resultado)


def filtro_texto(
    titulo: str,
    valor_padrao: str = "",
    placeholder: str | None = None,
    chave: str | None = None,
    local: str = "principal",
    ajuda: str | None = None
) -> str:
    """
    Exibe um filtro de busca textual.

    Args:
        titulo (str): Rotulo do filtro.
        valor_padrao (str): Texto inicial.
        placeholder (str | None): Exemplo exibido no campo vazio.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.
        ajuda (str | None): Texto de ajuda.

    Returns:
        str: Texto informado pelo usuario.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso valor_padrao nao seja texto.
    """
    rotulo = _validar_texto(titulo, "titulo")
    if not isinstance(valor_padrao, str):
        raise ConfiguracaoFiltroInvalidaError(
            "O valor padrao do filtro de texto deve ser uma string."
        )
    return _obter_container(local).text_input(
        rotulo,
        value=valor_padrao,
        placeholder=placeholder,
        key=_gerar_chave(chave, rotulo),
        help=ajuda
    )


def filtro_booleano(
    titulo: str,
    valor_padrao: bool = False,
    chave: str | None = None,
    local: str = "principal",
    ajuda: str | None = None
) -> bool:
    """
    Exibe um filtro booleano no formato toggle.

    Args:
        titulo (str): Rotulo do filtro.
        valor_padrao (bool): Valor inicial.
        chave (str | None): Chave unica do widget.
        local (str): Principal ou sidebar.
        ajuda (str | None): Texto de ajuda.

    Returns:
        bool: Estado atual do filtro.

    Raises:
        TypeError: Caso valor_padrao nao seja booleano.
    """
    rotulo = _validar_texto(titulo, "titulo")
    _validar_booleano(valor_padrao, "valor_padrao")
    return bool(_obter_container(local).toggle(
        rotulo,
        value=valor_padrao,
        key=_gerar_chave(chave, rotulo),
        help=ajuda
    ))


# ----------------------------------------------------------------------------
# APLICACAO DOS FILTROS
# ----------------------------------------------------------------------------

def aplicar_filtros_dataframe(
    dataframe: pd.DataFrame,
    filtros: Mapping[str, Mapping[str, Any]]
) -> pd.DataFrame:
    """
    Aplica valores de filtros previamente coletados em um DataFrame.

    Args:
        dataframe (pd.DataFrame): DataFrame original.
        filtros (Mapping): Configuracoes contendo coluna, tipo e valor.

    Returns:
        pd.DataFrame: Novo DataFrame filtrado com indice reiniciado.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso uma configuracao seja invalida.
    """
    _validar_dataframe(dataframe)
    if not isinstance(filtros, Mapping):
        raise ConfiguracaoFiltroInvalidaError(
            "O parametro 'filtros' deve ser um mapeamento."
        )

    resultado = dataframe.copy()
    for nome_filtro, configuracao in filtros.items():
        if not isinstance(configuracao, Mapping):
            raise ConfiguracaoFiltroInvalidaError(
                f"A configuracao do filtro '{nome_filtro}' deve ser um mapeamento."
            )
        coluna = _validar_coluna(resultado, configuracao.get("coluna", nome_filtro))
        tipo = _validar_texto(configuracao.get("tipo", "selecao"), "tipo").lower()
        valor = configuracao.get("valor")

        if valor is None or valor == "" or valor == [] or valor == ():
            continue
        if tipo == "selecao":
            resultado = resultado[resultado[coluna] == valor]
        elif tipo == "multisselecao":
            resultado = resultado[resultado[coluna].isin(list(valor))]
        elif tipo == "data":
            datas = pd.to_datetime(resultado[coluna], errors="coerce").dt.date
            resultado = resultado[datas == pd.to_datetime(valor).date()]
        elif tipo == "periodo":
            if not isinstance(valor, (tuple, list)) or len(valor) != 2:
                raise ValorFiltroInvalidoError(
                    f"O filtro '{nome_filtro}' exige duas datas."
                )
            datas = pd.to_datetime(resultado[coluna], errors="coerce")
            inicio, fim = pd.to_datetime(valor[0]), pd.to_datetime(valor[1])
            resultado = resultado[datas.between(inicio, fim, inclusive="both")]
        elif tipo == "numero":
            resultado = resultado[resultado[coluna] == valor]
        elif tipo == "intervalo_numerico":
            if not isinstance(valor, (tuple, list)) or len(valor) != 2:
                raise ValorFiltroInvalidoError(
                    f"O filtro '{nome_filtro}' exige um intervalo numerico."
                )
            resultado = resultado[resultado[coluna].between(
                valor[0], valor[1], inclusive="both"
            )]
        elif tipo == "texto":
            resultado = resultado[
                resultado[coluna].astype("string").str.contains(
                    str(valor), case=False, na=False, regex=False
                )
            ]
        elif tipo == "booleano":
            resultado = resultado[resultado[coluna].astype(bool) == bool(valor)]
        else:
            raise ConfiguracaoFiltroInvalidaError(
                f"O tipo de filtro '{tipo}' nao e suportado."
            )

    return resultado.reset_index(drop=True)


def criar_barra_filtros(
    dataframe: pd.DataFrame,
    filtros: Mapping[str, str | Mapping[str, Any]],
    colunas: int = 3,
    local: str = "principal",
    espaco: str = "small"
) -> dict[str, Any]:
    """
    Cria widgets automaticamente e retorna o DataFrame filtrado.

    Args:
        dataframe (pd.DataFrame): DataFrame original.
        filtros (Mapping): Colunas e configuracoes simplificadas dos filtros.
        colunas (int): Quantidade de filtros por linha, entre 1 e 6.
        local (str): Principal ou sidebar.
        espaco (str): Espacamento small, medium ou large.

    Returns:
        dict[str, Any]: DataFrame filtrado, valores e configuracoes aplicadas.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso a barra seja invalida.
    """
    _validar_dataframe(dataframe)
    if not isinstance(filtros, Mapping):
        raise ConfiguracaoFiltroInvalidaError(
            "O parametro 'filtros' deve ser um mapeamento."
        )
    if isinstance(colunas, bool) or not isinstance(colunas, int) or not 1 <= colunas <= 6:
        raise ConfiguracaoFiltroInvalidaError(
            "O parametro 'colunas' deve ser inteiro entre 1 e 6."
        )
    local_normalizado = _validar_texto(local, "local").lower()
    if local_normalizado not in LOCAL_FILTROS_VALIDOS:
        raise ConfiguracaoFiltroInvalidaError(
            "O parametro 'local' deve ser 'principal' ou 'sidebar'."
        )
    espaco_normalizado = _validar_texto(espaco, "espaco").lower()
    if espaco_normalizado not in ESPACOS_COLUNAS_VALIDOS:
        raise ConfiguracaoFiltroInvalidaError(
            "O parametro 'espaco' deve ser small, medium ou large."
        )

    valores: dict[str, Any] = {}
    aplicaveis: dict[str, dict[str, Any]] = {}
    itens = list(filtros.items())

    for inicio in range(0, len(itens), colunas):
        grupo = itens[inicio:inicio + colunas]
        containers = (
            [st.sidebar] * len(grupo)
            if local_normalizado == "sidebar"
            else st.columns(colunas, gap=espaco_normalizado)[:len(grupo)]
        )
        for indice, (coluna, especificacao) in enumerate(grupo):
            nome_coluna = _validar_coluna(dataframe, coluna)
            config = {"tipo": especificacao} if isinstance(especificacao, str) else dict(especificacao)
            tipo = _validar_texto(config.pop("tipo", "selecao"), "tipo").lower()
            if tipo not in TIPOS_FILTRO:
                raise ConfiguracaoFiltroInvalidaError(
                    f"O tipo de filtro '{tipo}' nao e suportado."
                )
            titulo = config.pop("titulo", nome_coluna)
            chave = config.pop("chave", f"{PREFIXO_CHAVE_FILTRO}_{nome_coluna}")
            config.pop("local", None)

            with containers[indice]:
                if tipo == "selecao":
                    valor = filtro_selecao(
                        titulo,
                        config.pop("opcoes", obter_opcoes_coluna(dataframe, nome_coluna)),
                        chave=chave,
                        local="principal",
                        **config
                    )
                elif tipo == "multisselecao":
                    valor = filtro_multisselecao(
                        titulo,
                        config.pop("opcoes", obter_opcoes_coluna(dataframe, nome_coluna)),
                        chave=chave,
                        local="principal",
                        **config
                    )
                elif tipo == "data":
                    valor = filtro_data(titulo, chave=chave, local="principal", **config)
                elif tipo == "periodo":
                    valor = filtro_periodo(titulo, chave=chave, local="principal", **config)
                elif tipo == "numero":
                    valor = filtro_numerico(titulo, chave=chave, local="principal", **config)
                elif tipo == "intervalo_numerico":
                    serie = pd.to_numeric(dataframe[nome_coluna], errors="coerce").dropna()
                    if serie.empty:
                        raise ValorFiltroInvalidoError(
                            f"A coluna '{nome_coluna}' nao possui valores numericos."
                        )
                    valor = filtro_intervalo_numerico(
                        titulo,
                        minimo=config.pop("minimo", serie.min()),
                        maximo=config.pop("maximo", serie.max()),
                        chave=chave,
                        local="principal",
                        **config
                    )
                elif tipo == "texto":
                    valor = filtro_texto(titulo, chave=chave, local="principal", **config)
                else:
                    valor = filtro_booleano(titulo, chave=chave, local="principal", **config)

            valores[nome_coluna] = valor
            aplicaveis[nome_coluna] = {
                "coluna": nome_coluna,
                "tipo": tipo,
                "valor": valor
            }

    return {
        "dataframe": aplicar_filtros_dataframe(dataframe, aplicaveis),
        "valores": valores,
        "filtros": aplicaveis
    }


def limpar_filtros(
    prefixo: str = PREFIXO_CHAVE_FILTRO,
    executar_rerun: bool = True
) -> list[str]:
    """
    Remove do Session State as chaves iniciadas pelo prefixo informado.

    Args:
        prefixo (str): Prefixo das chaves de filtros.
        executar_rerun (bool): Executa st.rerun apos a limpeza.

    Returns:
        list[str]: Chaves removidas do estado da sessao.

    Raises:
        ConfiguracaoFiltroInvalidaError: Caso o prefixo seja invalido.
    """
    prefixo_validado = _validar_texto(prefixo, "prefixo")
    _validar_booleano(executar_rerun, "executar_rerun")
    removidas: list[str] = []
    for chave in list(st.session_state.keys()):
        if str(chave).startswith(prefixo_validado):
            del st.session_state[chave]
            removidas.append(chave)
    if executar_rerun and removidas:
        st.rerun()
    return removidas


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "LOCAL_FILTROS_VALIDOS",
    "ESPACOS_COLUNAS_VALIDOS",
    "QUANTIDADE_MAXIMA_COLUNAS",
    "FORMATO_DATA_PADRAO",
    "PREFIXO_CHAVE_FILTRO",
    "obter_opcoes_coluna",
    "filtro_selecao",
    "filtro_multisselecao",
    "filtro_data",
    "filtro_periodo",
    "filtro_numerico",
    "filtro_intervalo_numerico",
    "filtro_texto",
    "filtro_booleano",
    "aplicar_filtros_dataframe",
    "criar_barra_filtros",
    "limpar_filtros"
]
