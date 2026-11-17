"""
============================================================
Modulo: DASHBOARD_STREAMLIT / estado.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes simples para criar, consultar, atualizar e remover valores do
    st.session_state. O modulo facilita a persistencia de filtros, pagina
    atual, selecoes e controles entre as reexecucoes do Streamlit.
Funcoes disponiveis:
    - inicializar_estado()
    - estado_existe()
    - obter_estado()
    - definir_estado()
    - definir_estados()
    - obter_estados()
    - atualizar_estado()
    - alternar_estado()
    - incrementar_estado()
    - adicionar_item_estado()
    - remover_item_estado()
    - remover_estado()
    - limpar_estado()
    - restaurar_estado()
    - criar_callback_estado()
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao das operacoes basicas de Session State.
        - Inclusao de atalhos para alternancia, incremento e colecoes.
        - Inclusao de callback simples para widgets.
============================================================
"""

# ----------------------------------------------------------------------------
# IMPORTACOES
# ----------------------------------------------------------------------------

# Importa deepcopy para impedir referencias compartilhadas em valores padrao
from copy import deepcopy

# Importa Mapping e Iterable para validar colecoes recebidas
from collections.abc import Iterable, Mapping, MutableMapping

# Importa Any e Callable para tipagem dos valores e callbacks
from typing import Any, Callable

# Importa Streamlit para acessar o estado da sessao atual
import streamlit as st


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

PREFIXO_ESTADO_PADRAO = "dashboard"
SEPARADOR_CHAVE_ESTADO = "_"
VALOR_BOOLEANO_PADRAO = False
INCREMENTO_PADRAO = 1


# ----------------------------------------------------------------------------
# EXCECOES
# ----------------------------------------------------------------------------

class DashboardEstadoError(Exception):
    """Erro base para operacoes relacionadas ao estado do dashboard."""


class ChaveEstadoInvalidaError(DashboardEstadoError, ValueError):
    """Indica que uma chave de estado e vazia ou possui tipo invalido."""


class EstadoNaoEncontradoError(DashboardEstadoError, KeyError):
    """Indica que a chave solicitada nao existe no estado da sessao."""


class ValorEstadoInvalidoError(DashboardEstadoError, TypeError):
    """Indica que o valor atual nao suporta a operacao solicitada."""


class EstadoSessaoInvalidoError(DashboardEstadoError, TypeError):
    """Indica que o armazenamento informado nao e um mapeamento mutavel."""


# ----------------------------------------------------------------------------
# FUNCOES INTERNAS
# ----------------------------------------------------------------------------

def _obter_armazenamento() -> MutableMapping[str, Any]:
    """
    Retorna o armazenamento atual do Session State.

    Args:
        Nenhum.

    Returns:
        MutableMapping[str, Any]: Estado mutavel da sessao atual.

    Raises:
        EstadoSessaoInvalidoError: Caso session_state nao seja mutavel.
    """
    armazenamento = st.session_state

    if not isinstance(armazenamento, MutableMapping):
        # Session State real implementa a API de mapeamento, mas alguns
        # ambientes de teste usam objetos equivalentes sem heranca direta.
        operacoes = ("__getitem__", "__setitem__", "__contains__", "keys")
        if not all(hasattr(armazenamento, operacao) for operacao in operacoes):
            raise EstadoSessaoInvalidoError(
                "O objeto st.session_state nao possui uma API de mapeamento."
            )

    return armazenamento


def _validar_chave(chave: str) -> str:
    """
    Valida e normaliza uma chave do estado.

    Args:
        chave (str): Chave que sera validada.

    Returns:
        str: Chave sem espacos externos.

    Raises:
        ChaveEstadoInvalidaError: Caso a chave nao seja string preenchida.
    """
    if not isinstance(chave, str):
        raise ChaveEstadoInvalidaError(
            "A chave do estado deve ser uma string."
        )

    resultado = chave.strip()
    if not resultado:
        raise ChaveEstadoInvalidaError(
            "A chave do estado nao pode estar vazia."
        )
    return resultado


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


def _validar_numero(valor: int | float, nome: str) -> int | float:
    """
    Valida um valor numerico sem aceitar booleanos.

    Args:
        valor (int | float): Numero que sera validado.
        nome (str): Nome utilizado na mensagem de erro.

    Returns:
        int | float: O proprio numero validado.

    Raises:
        ValorEstadoInvalidoError: Caso o valor nao seja numerico.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValorEstadoInvalidoError(
            f"O parametro '{nome}' deve ser numerico."
        )
    return valor


def _copiar_valor(valor: Any, copiar: bool) -> Any:
    """
    Retorna uma copia profunda ou o proprio valor.

    Args:
        valor (Any): Valor que sera retornado.
        copiar (bool): Define se uma copia profunda sera criada.

    Returns:
        Any: Copia profunda ou valor original.

    Raises:
        TypeError: Caso copiar nao seja booleano.
    """
    _validar_booleano(copiar, "copiar")
    return deepcopy(valor) if copiar else valor


# ----------------------------------------------------------------------------
# INICIALIZACAO E CONSULTA
# ----------------------------------------------------------------------------

def inicializar_estado(
    valores: Mapping[str, Any] | None = None,
    sobrescrever: bool = False,
    **valores_nomeados: Any
) -> dict[str, Any]:
    """
    Inicializa varias chaves do estado de forma segura.

    Args:
        valores (Mapping | None): Valores iniciais organizados por chave.
        sobrescrever (bool): Define se chaves existentes serao substituidas.
        **valores_nomeados (Any): Valores adicionais informados por nome.

    Returns:
        dict[str, Any]: Chaves processadas e seus valores atuais.

    Raises:
        TypeError: Caso valores nao seja um mapeamento ou None.
    """
    _validar_booleano(sobrescrever, "sobrescrever")

    if valores is None:
        iniciais: dict[str, Any] = {}
    elif isinstance(valores, Mapping):
        iniciais = dict(valores)
    else:
        raise TypeError(
            "O parametro 'valores' deve ser um mapeamento ou None."
        )

    iniciais.update(valores_nomeados)
    armazenamento = _obter_armazenamento()
    resultado: dict[str, Any] = {}

    for chave, valor in iniciais.items():
        chave_validada = _validar_chave(chave)
        if sobrescrever or chave_validada not in armazenamento:
            armazenamento[chave_validada] = deepcopy(valor)
        resultado[chave_validada] = armazenamento[chave_validada]

    return resultado


def estado_existe(chave: str) -> bool:
    """
    Verifica se uma chave existe no estado da sessao.

    Args:
        chave (str): Chave que sera pesquisada.

    Returns:
        bool: True quando a chave existe.

    Raises:
        ChaveEstadoInvalidaError: Caso a chave seja invalida.
    """
    return _validar_chave(chave) in _obter_armazenamento()


def obter_estado(
    chave: str,
    padrao: Any = None,
    obrigatorio: bool = False,
    copiar: bool = False
) -> Any:
    """
    Obtem um valor do estado com padrao e obrigatoriedade opcionais.

    Args:
        chave (str): Chave que sera consultada.
        padrao (Any): Valor retornado quando a chave nao existe.
        obrigatorio (bool): Define se a ausencia deve gerar excecao.
        copiar (bool): Define se o valor sera retornado como copia profunda.

    Returns:
        Any: Valor armazenado ou valor padrao.

    Raises:
        EstadoNaoEncontradoError: Caso a chave obrigatoria nao exista.
    """
    chave_validada = _validar_chave(chave)
    _validar_booleano(obrigatorio, "obrigatorio")
    armazenamento = _obter_armazenamento()

    if chave_validada not in armazenamento:
        if obrigatorio:
            raise EstadoNaoEncontradoError(
                f"A chave '{chave_validada}' nao existe no estado."
            )
        return _copiar_valor(padrao, copiar)

    return _copiar_valor(armazenamento[chave_validada], copiar)


def obter_estados(copiar: bool = False) -> dict[str, Any]:
    """
    Retorna todos os valores atuais do estado.

    Args:
        copiar (bool): Define se os valores serao copiados profundamente.

    Returns:
        dict[str, Any]: Fotografia atual do estado da sessao.

    Raises:
        TypeError: Caso copiar nao seja booleano.
    """
    _validar_booleano(copiar, "copiar")
    armazenamento = _obter_armazenamento()
    resultado = {
        chave: armazenamento[chave]
        for chave in list(armazenamento.keys())
    }
    return deepcopy(resultado) if copiar else resultado


# ----------------------------------------------------------------------------
# DEFINICAO E ATUALIZACAO
# ----------------------------------------------------------------------------

def definir_estado(chave: str, valor: Any, copiar: bool = False) -> Any:
    """
    Define ou substitui um valor no estado.

    Args:
        chave (str): Chave que sera definida.
        valor (Any): Valor armazenado.
        copiar (bool): Define se o valor sera copiado antes do armazenamento.

    Returns:
        Any: Valor efetivamente armazenado.

    Raises:
        ChaveEstadoInvalidaError: Caso a chave seja invalida.
    """
    chave_validada = _validar_chave(chave)
    valor_final = _copiar_valor(valor, copiar)
    _obter_armazenamento()[chave_validada] = valor_final
    return valor_final


def definir_estados(
    valores: Mapping[str, Any],
    copiar: bool = False
) -> dict[str, Any]:
    """
    Define varias chaves em uma unica chamada.

    Args:
        valores (Mapping[str, Any]): Valores organizados por chave.
        copiar (bool): Define se cada valor sera copiado profundamente.

    Returns:
        dict[str, Any]: Valores efetivamente armazenados.

    Raises:
        TypeError: Caso valores nao seja um mapeamento.
    """
    if not isinstance(valores, Mapping):
        raise TypeError("O parametro 'valores' deve ser um mapeamento.")

    return {
        _validar_chave(chave): definir_estado(chave, valor, copiar=copiar)
        for chave, valor in valores.items()
    }


def atualizar_estado(
    chave: str,
    atualizador: Callable[[Any], Any],
    padrao: Any = None
) -> Any:
    """
    Atualiza uma chave utilizando uma funcao transformadora.

    Args:
        chave (str): Chave que sera atualizada.
        atualizador (Callable[[Any], Any]): Funcao que recebe o valor atual.
        padrao (Any): Valor inicial usado quando a chave nao existe.

    Returns:
        Any: Novo valor armazenado.

    Raises:
        ValorEstadoInvalidoError: Caso atualizador nao seja chamavel.
    """
    if not callable(atualizador):
        raise ValorEstadoInvalidoError(
            "O parametro 'atualizador' deve ser uma funcao chamavel."
        )

    atual = obter_estado(chave, padrao=padrao)
    novo_valor = atualizador(atual)
    return definir_estado(chave, novo_valor)


def alternar_estado(
    chave: str,
    padrao: bool = VALOR_BOOLEANO_PADRAO
) -> bool:
    """
    Inverte um valor booleano armazenado no estado.

    Args:
        chave (str): Chave booleana que sera alternada.
        padrao (bool): Valor usado quando a chave ainda nao existe.

    Returns:
        bool: Novo valor booleano armazenado.

    Raises:
        ValorEstadoInvalidoError: Caso o valor atual nao seja booleano.
    """
    _validar_booleano(padrao, "padrao")
    atual = obter_estado(chave, padrao=padrao)

    if not isinstance(atual, bool):
        raise ValorEstadoInvalidoError(
            f"O valor da chave '{_validar_chave(chave)}' deve ser booleano."
        )

    return definir_estado(chave, not atual)


def incrementar_estado(
    chave: str,
    incremento: int | float = INCREMENTO_PADRAO,
    inicial: int | float = 0
) -> int | float:
    """
    Incrementa um valor numerico do estado.

    Args:
        chave (str): Chave numerica que sera incrementada.
        incremento (int | float): Valor adicionado ao estado atual.
        inicial (int | float): Valor inicial usado quando a chave nao existe.

    Returns:
        int | float: Novo valor numerico armazenado.

    Raises:
        ValorEstadoInvalidoError: Caso algum valor nao seja numerico.
    """
    passo = _validar_numero(incremento, "incremento")
    valor_inicial = _validar_numero(inicial, "inicial")
    atual = obter_estado(chave, padrao=valor_inicial)
    atual_validado = _validar_numero(atual, f"estado[{_validar_chave(chave)}]")
    return definir_estado(chave, atual_validado + passo)


# ----------------------------------------------------------------------------
# COLECOES
# ----------------------------------------------------------------------------

def adicionar_item_estado(
    chave: str,
    item: Any,
    evitar_duplicidade: bool = False
) -> list[Any]:
    """
    Adiciona um item a uma lista armazenada no estado.

    Args:
        chave (str): Chave da lista.
        item (Any): Item que sera acrescentado.
        evitar_duplicidade (bool): Impede a inclusao de item repetido.

    Returns:
        list[Any]: Lista atualizada.

    Raises:
        ValorEstadoInvalidoError: Caso o valor atual nao seja lista.
    """
    _validar_booleano(evitar_duplicidade, "evitar_duplicidade")
    atual = obter_estado(chave, padrao=[])

    if not isinstance(atual, list):
        raise ValorEstadoInvalidoError(
            f"O valor da chave '{_validar_chave(chave)}' deve ser uma lista."
        )

    nova_lista = list(atual)
    if not evitar_duplicidade or item not in nova_lista:
        nova_lista.append(item)
    definir_estado(chave, nova_lista)
    return nova_lista


def remover_item_estado(
    chave: str,
    item: Any,
    ignorar_ausente: bool = True
) -> list[Any]:
    """
    Remove a primeira ocorrencia de um item de uma lista do estado.

    Args:
        chave (str): Chave da lista.
        item (Any): Item que sera removido.
        ignorar_ausente (bool): Ignora item ou chave inexistente.

    Returns:
        list[Any]: Lista atualizada.

    Raises:
        ValueError: Caso o item esteja ausente e nao deva ser ignorado.
        ValorEstadoInvalidoError: Caso o valor atual nao seja lista.
    """
    _validar_booleano(ignorar_ausente, "ignorar_ausente")
    atual = obter_estado(chave, padrao=[])

    if not isinstance(atual, list):
        raise ValorEstadoInvalidoError(
            f"O valor da chave '{_validar_chave(chave)}' deve ser uma lista."
        )

    nova_lista = list(atual)
    if item in nova_lista:
        nova_lista.remove(item)
    elif not ignorar_ausente:
        raise ValueError("O item informado nao existe na lista do estado.")

    definir_estado(chave, nova_lista)
    return nova_lista


# ----------------------------------------------------------------------------
# REMOCAO E RESTAURACAO
# ----------------------------------------------------------------------------

def remover_estado(chave: str, ignorar_ausente: bool = True) -> Any:
    """
    Remove uma chave do estado e retorna o valor anterior.

    Args:
        chave (str): Chave que sera removida.
        ignorar_ausente (bool): Retorna None quando a chave nao existe.

    Returns:
        Any: Valor removido ou None.

    Raises:
        EstadoNaoEncontradoError: Caso a chave ausente nao deva ser ignorada.
    """
    chave_validada = _validar_chave(chave)
    _validar_booleano(ignorar_ausente, "ignorar_ausente")
    armazenamento = _obter_armazenamento()

    if chave_validada not in armazenamento:
        if ignorar_ausente:
            return None
        raise EstadoNaoEncontradoError(
            f"A chave '{chave_validada}' nao existe no estado."
        )

    valor = armazenamento[chave_validada]
    del armazenamento[chave_validada]
    return valor


def limpar_estado(
    preservar: Iterable[str] | None = None,
    prefixo: str | None = None
) -> list[str]:
    """
    Limpa chaves do estado, com preservacao e filtro por prefixo opcionais.

    Args:
        preservar (Iterable[str] | None): Chaves que nao serao removidas.
        prefixo (str | None): Remove somente chaves iniciadas pelo prefixo.

    Returns:
        list[str]: Chaves efetivamente removidas.

    Raises:
        TypeError: Caso preservar nao seja iteravel ou None.
    """
    if preservar is None:
        preservadas: set[str] = set()
    elif isinstance(preservar, (str, bytes)) or not isinstance(
        preservar,
        Iterable
    ):
        raise TypeError(
            "O parametro 'preservar' deve ser um iteravel nao textual ou None."
        )
    else:
        preservadas = {_validar_chave(chave) for chave in preservar}

    prefixo_validado = None if prefixo is None else _validar_chave(prefixo)
    armazenamento = _obter_armazenamento()
    removidas: list[str] = []

    for chave in list(armazenamento.keys()):
        if chave in preservadas:
            continue
        if prefixo_validado is not None and not chave.startswith(prefixo_validado):
            continue
        del armazenamento[chave]
        removidas.append(chave)

    return removidas


def restaurar_estado(
    valores: Mapping[str, Any],
    limpar_antes: bool = True,
    copiar: bool = True
) -> dict[str, Any]:
    """
    Restaura o estado a partir de um mapeamento previamente salvo.

    Args:
        valores (Mapping[str, Any]): Fotografia de estado que sera restaurada.
        limpar_antes (bool): Define se o estado atual sera limpo primeiro.
        copiar (bool): Define se os valores serao copiados profundamente.

    Returns:
        dict[str, Any]: Estado restaurado.

    Raises:
        TypeError: Caso valores nao seja um mapeamento.
    """
    if not isinstance(valores, Mapping):
        raise TypeError("O parametro 'valores' deve ser um mapeamento.")

    _validar_booleano(limpar_antes, "limpar_antes")
    _validar_booleano(copiar, "copiar")

    if limpar_antes:
        limpar_estado()
    definir_estados(valores, copiar=copiar)
    return obter_estados(copiar=copiar)


# ----------------------------------------------------------------------------
# CALLBACKS
# ----------------------------------------------------------------------------

def criar_callback_estado(
    chave: str,
    valor: Any = None,
    alternar: bool = False
) -> Callable[[], Any]:
    """
    Cria um callback sem argumentos para uso em widgets Streamlit.

    Args:
        chave (str): Chave que sera atualizada quando o callback for executado.
        valor (Any): Valor definido quando alternar for False.
        alternar (bool): Define se o callback deve inverter um booleano.

    Returns:
        Callable[[], Any]: Funcao pronta para on_click ou on_change.

    Raises:
        ChaveEstadoInvalidaError: Caso a chave seja invalida.
    """
    chave_validada = _validar_chave(chave)
    _validar_booleano(alternar, "alternar")

    def callback() -> Any:
        """Executa a atualizacao configurada no estado."""
        if alternar:
            return alternar_estado(chave_validada)
        return definir_estado(chave_validada, valor)

    callback.__name__ = f"atualizar_estado_{chave_validada}"
    setattr(callback, "__dashboard_estado_chave__", chave_validada)
    setattr(callback, "__dashboard_estado_alternar__", alternar)
    return callback


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "PREFIXO_ESTADO_PADRAO",
    "SEPARADOR_CHAVE_ESTADO",
    "VALOR_BOOLEANO_PADRAO",
    "INCREMENTO_PADRAO",
    "DashboardEstadoError",
    "ChaveEstadoInvalidaError",
    "EstadoNaoEncontradoError",
    "ValorEstadoInvalidoError",
    "EstadoSessaoInvalidoError",
    "inicializar_estado",
    "estado_existe",
    "obter_estado",
    "definir_estado",
    "definir_estados",
    "obter_estados",
    "atualizar_estado",
    "alternar_estado",
    "incrementar_estado",
    "adicionar_item_estado",
    "remover_item_estado",
    "remover_estado",
    "limpar_estado",
    "restaurar_estado",
    "criar_callback_estado"
]
