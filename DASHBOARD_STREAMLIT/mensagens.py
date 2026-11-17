"""
============================================================
Modulo: DASHBOARD_STREAMLIT / mensagens.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes reutilizaveis para exibir mensagens, alertas, notificacoes,
    excecoes, progresso e status em dashboards Streamlit. O modulo
    centraliza validacoes, icones, larguras e configuracoes visuais.
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao de alertas, toast, excecao, progresso e status.
        - Inclusao da fabrica declarativa de mensagens.
============================================================
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any, Iterator

import streamlit as st

try:
    from .excecoes import (
        ConfiguracaoMensagemInvalidaError,
        DashboardStreamlitError,
        obter_mensagem_erro,
    )
except ImportError:
    from excecoes import (
        ConfiguracaoMensagemInvalidaError,
        DashboardStreamlitError,
        obter_mensagem_erro,
    )


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

TIPOS_MENSAGEM_VALIDOS = {"sucesso", "informacao", "aviso", "erro"}
DURACOES_TOAST_VALIDAS = {"short", "long", "infinite"}
ESTADOS_STATUS_VALIDOS = {"running", "complete", "error"}
TIPOS_STATUS_VALIDOS = {"default", "compact", "step"}
LARGURAS_MENSAGEM_VALIDAS = {"stretch"}
ICONES_MENSAGEM_PADRAO = {
    "sucesso": ":material/check_circle:",
    "informacao": ":material/info:",
    "aviso": ":material/warning:",
    "erro": ":material/error:",
}
PREFIXO_CHAVE_MENSAGEM = "mensagem"


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
        nome (str): Nome utilizado na mensagem de erro.
        permitir_none (bool): Permite None como retorno.

    Returns:
        str | None: Texto normalizado ou None.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso o texto seja invalido.
    """
    if valor is None and permitir_none:
        return None
    if not isinstance(valor, str) or not valor.strip():
        raise ConfiguracaoMensagemInvalidaError(
            f"O parametro '{nome}' deve ser uma string preenchida."
        )
    return valor.strip()


def _validar_booleano(valor: bool, nome: str) -> bool:
    """Valida estritamente um parametro booleano.

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


def _validar_largura(largura: str | int) -> str | int:
    """Valida a largura de um alerta.

    Args:
        largura (str | int): stretch ou largura em pixels.

    Returns:
        str | int: Largura normalizada.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a largura seja invalida.
    """
    if isinstance(largura, int) and not isinstance(largura, bool) and largura > 0:
        return largura
    if isinstance(largura, str) and largura.strip().lower() in LARGURAS_MENSAGEM_VALIDAS:
        return largura.strip().lower()
    raise ConfiguracaoMensagemInvalidaError(
        "A largura deve ser 'stretch' ou um inteiro positivo."
    )


def _validar_tipo_mensagem(tipo: str) -> str:
    """Valida e normaliza o tipo de mensagem.

    Args:
        tipo (str): Tipo declarativo da mensagem.

    Returns:
        str: Tipo normalizado.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso o tipo seja desconhecido.
    """
    resultado = _validar_texto(tipo, "tipo")
    assert isinstance(resultado, str)
    resultado = resultado.lower()
    if resultado not in TIPOS_MENSAGEM_VALIDOS:
        raise ConfiguracaoMensagemInvalidaError(
            "O tipo deve ser sucesso, informacao, aviso ou erro."
        )
    return resultado


def _obter_icone(tipo: str, icone: str | None) -> str | None:
    """Retorna o icone personalizado ou o padrao do tipo.

    Args:
        tipo (str): Tipo validado da mensagem.
        icone (str | None): Icone personalizado ou None.

    Returns:
        str | None: Icone pronto para o Streamlit.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso o icone seja invalido.
    """
    if icone is None:
        return ICONES_MENSAGEM_PADRAO[tipo]
    if not isinstance(icone, str):
        raise ConfiguracaoMensagemInvalidaError(
            "O icone deve ser uma string ou None."
        )
    return icone.strip()


# ----------------------------------------------------------------------------
# ALERTAS SIMPLES
# ----------------------------------------------------------------------------

def exibir_mensagem(
    texto: str,
    *,
    tipo: str = "informacao",
    titulo: str | None = None,
    icone: str | None = None,
    largura: str | int = "stretch",
    usar_icone_padrao: bool = True
) -> Any:
    """Exibe um alerta simples conforme o tipo informado.

    Args:
        texto (str): Corpo da mensagem.
        tipo (str): sucesso, informacao, aviso ou erro.
        titulo (str | None): Titulo opcional do alerta.
        icone (str | None): Emoji, Material icon ou string vazia.
        largura (str | int): stretch ou largura em pixels.
        usar_icone_padrao (bool): Usa o icone padrao quando icone e None.

    Returns:
        Any: Retorno do componente Streamlit.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a configuracao seja invalida.
    """
    corpo = _validar_texto(texto, "texto")
    assert isinstance(corpo, str)
    tipo_validado = _validar_tipo_mensagem(tipo)
    titulo_validado = _validar_texto(titulo, "titulo", permitir_none=True)
    _validar_booleano(usar_icone_padrao, "usar_icone_padrao")
    if icone is not None:
        icone_validado = _obter_icone(tipo_validado, icone)
    elif usar_icone_padrao:
        icone_validado = _obter_icone(tipo_validado, None)
    else:
        icone_validado = ""

    funcoes = {
        "sucesso": st.success,
        "informacao": st.info,
        "aviso": st.warning,
        "erro": st.error,
    }
    return funcoes[tipo_validado](
        corpo,
        icon=icone_validado,
        width=_validar_largura(largura),
        title=titulo_validado
    )


def mensagem_sucesso(texto: str, **configuracao: Any) -> Any:
    """Exibe uma mensagem de sucesso.

    Args:
        texto (str): Corpo da mensagem.
        **configuracao (Any): Opcoes adicionais de exibir_mensagem.

    Returns:
        Any: Retorno de st.success.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a configuracao seja invalida.
    """
    return exibir_mensagem(texto, tipo="sucesso", **configuracao)


def mensagem_informacao(texto: str, **configuracao: Any) -> Any:
    """Exibe uma mensagem informativa.

    Args:
        texto (str): Corpo da mensagem.
        **configuracao (Any): Opcoes adicionais de exibir_mensagem.

    Returns:
        Any: Retorno de st.info.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a configuracao seja invalida.
    """
    return exibir_mensagem(texto, tipo="informacao", **configuracao)


def mensagem_aviso(texto: str, **configuracao: Any) -> Any:
    """Exibe uma mensagem de aviso.

    Args:
        texto (str): Corpo da mensagem.
        **configuracao (Any): Opcoes adicionais de exibir_mensagem.

    Returns:
        Any: Retorno de st.warning.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a configuracao seja invalida.
    """
    return exibir_mensagem(texto, tipo="aviso", **configuracao)


def mensagem_erro(texto: str, **configuracao: Any) -> Any:
    """Exibe uma mensagem de erro.

    Args:
        texto (str): Corpo da mensagem.
        **configuracao (Any): Opcoes adicionais de exibir_mensagem.

    Returns:
        Any: Retorno de st.error.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a configuracao seja invalida.
    """
    return exibir_mensagem(texto, tipo="erro", **configuracao)


# ----------------------------------------------------------------------------
# TOAST, EXCECOES E STATUS
# ----------------------------------------------------------------------------

def exibir_toast(
    texto: str,
    *,
    icone: str | None = None,
    duracao: str | int = "short"
) -> Any:
    """Exibe uma notificacao temporaria no dashboard.

    Args:
        texto (str): Corpo da notificacao.
        icone (str | None): Emoji, Material icon ou spinner.
        duracao (str | int): short, long, infinite ou segundos.

    Returns:
        Any: Objeto de toast retornado pelo Streamlit.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a duracao seja invalida.
    """
    corpo = _validar_texto(texto, "texto")
    assert isinstance(corpo, str)
    if isinstance(duracao, int) and not isinstance(duracao, bool):
        if duracao < 1:
            raise ConfiguracaoMensagemInvalidaError(
                "A duracao em segundos deve ser positiva."
            )
        duracao_validada: str | int = duracao
    elif isinstance(duracao, str) and duracao.strip().lower() in DURACOES_TOAST_VALIDAS:
        duracao_validada = duracao.strip().lower()
    else:
        raise ConfiguracaoMensagemInvalidaError(
            "A duracao deve ser short, long, infinite ou inteiro positivo."
        )
    icone_validado = None if icone is None else _validar_texto(icone, "icone")
    return st.toast(corpo, icon=icone_validado, duration=duracao_validada)


def exibir_excecao(
    erro: BaseException,
    *,
    incluir_tipo: bool = False,
    titulo: str | None = None,
    icone: str | None = None,
    largura: str | int = "stretch",
    exibir_traceback: bool = False
) -> Any:
    """Exibe uma excecao como alerta ou traceback.

    Args:
        erro (BaseException): Excecao capturada.
        incluir_tipo (bool): Inclui o nome da classe na mensagem.
        titulo (str | None): Titulo opcional do alerta.
        icone (str | None): Icone personalizado.
        largura (str | int): stretch ou pixels.
        exibir_traceback (bool): Usa st.exception em vez de st.error.

    Returns:
        Any: Retorno do componente Streamlit.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso erro nao seja excecao.
    """
    if not isinstance(erro, BaseException):
        raise ConfiguracaoMensagemInvalidaError(
            "O parametro 'erro' deve ser uma excecao."
        )
    _validar_booleano(incluir_tipo, "incluir_tipo")
    _validar_booleano(exibir_traceback, "exibir_traceback")
    if exibir_traceback:
        return st.exception(erro, width=_validar_largura(largura))
    return mensagem_erro(
        obter_mensagem_erro(erro, incluir_tipo=incluir_tipo),
        titulo=titulo,
        icone=icone,
        largura=largura
    )


def criar_status(
    texto: str,
    *,
    expandido: bool = False,
    estado: str = "running",
    tipo: str = "default",
    largura: str | int = "stretch"
) -> Any:
    """Cria um container de status para tarefas longas.

    Args:
        texto (str): Rotulo inicial do status.
        expandido (bool): Inicia o container aberto.
        estado (str): running, complete ou error.
        tipo (str): default, compact ou step.
        largura (str | int): stretch ou pixels.

    Returns:
        Any: Container de status retornado pelo Streamlit.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso estado ou tipo seja invalido.
    """
    rotulo = _validar_texto(texto, "texto")
    assert isinstance(rotulo, str)
    _validar_booleano(expandido, "expandido")
    estado_validado = _validar_texto(estado, "estado")
    tipo_validado = _validar_texto(tipo, "tipo")
    assert isinstance(estado_validado, str)
    assert isinstance(tipo_validado, str)
    estado_validado = estado_validado.lower()
    tipo_validado = tipo_validado.lower()
    if estado_validado not in ESTADOS_STATUS_VALIDOS:
        raise ConfiguracaoMensagemInvalidaError(
            "O estado deve ser running, complete ou error."
        )
    if tipo_validado not in TIPOS_STATUS_VALIDOS:
        raise ConfiguracaoMensagemInvalidaError(
            "O tipo deve ser default, compact ou step."
        )
    return st.status(
        rotulo,
        expanded=expandido,
        state=estado_validado,
        type=tipo_validado,
        width=_validar_largura(largura)
    )


@contextmanager
def executar_com_status(
    texto: str,
    *,
    texto_sucesso: str = "Concluido com sucesso.",
    texto_erro: str = "Nao foi possivel concluir.",
    expandido: bool = False,
    tipo: str = "default",
    propagar_erro: bool = True
) -> Iterator[Any]:
    """Executa um bloco e atualiza automaticamente seu status.

    Args:
        texto (str): Rotulo inicial da tarefa.
        texto_sucesso (str): Rotulo exibido ao concluir.
        texto_erro (str): Rotulo exibido em caso de falha.
        expandido (bool): Inicia o status aberto.
        tipo (str): default, compact ou step.
        propagar_erro (bool): Relanca a excecao depois da atualizacao.

    Returns:
        Iterator[Any]: Gerenciador de contexto com o objeto de status.

    Raises:
        BaseException: Repassa o erro original quando solicitado.
    """
    sucesso = _validar_texto(texto_sucesso, "texto_sucesso")
    falha = _validar_texto(texto_erro, "texto_erro")
    _validar_booleano(propagar_erro, "propagar_erro")
    status = criar_status(texto, expandido=expandido, tipo=tipo)
    try:
        yield status
    except BaseException:
        status.update(label=falha, state="error")
        if propagar_erro:
            raise
    else:
        status.update(label=sucesso, state="complete")


# ----------------------------------------------------------------------------
# PROGRESSO E CELEBRACOES
# ----------------------------------------------------------------------------

def exibir_progresso(
    valor: int | float,
    *,
    texto: str | None = None,
    largura: str | int = "stretch"
) -> Any:
    """Exibe uma barra de progresso entre zero e cem por cento.

    Args:
        valor (int | float): Percentual 0 a 100 ou proporcao 0 a 1.
        texto (str | None): Texto opcional da barra.
        largura (str | int): stretch ou pixels.

    Returns:
        Any: Objeto de progresso retornado pelo Streamlit.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso o valor seja invalido.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ConfiguracaoMensagemInvalidaError(
            "O valor do progresso deve ser numerico."
        )
    if 0 <= valor <= 1:
        valor_normalizado: int | float = float(valor)
    elif 0 <= valor <= 100:
        valor_normalizado = int(valor)
    else:
        raise ConfiguracaoMensagemInvalidaError(
            "O progresso deve estar entre 0 e 1 ou entre 0 e 100."
        )
    texto_validado = _validar_texto(texto, "texto", permitir_none=True)
    return st.progress(
        valor_normalizado,
        text=texto_validado,
        width=_validar_largura(largura)
    )


def celebrar(tipo: str = "baloes") -> Any:
    """Exibe uma animacao comemorativa.

    Args:
        tipo (str): baloes ou neve.

    Returns:
        Any: Retorno da animacao Streamlit.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso o tipo seja desconhecido.
    """
    tipo_validado = _validar_texto(tipo, "tipo")
    assert isinstance(tipo_validado, str)
    tipo_validado = tipo_validado.lower()
    if tipo_validado == "baloes":
        return st.balloons()
    if tipo_validado == "neve":
        return st.snow()
    raise ConfiguracaoMensagemInvalidaError(
        "A celebracao deve ser 'baloes' ou 'neve'."
    )


# ----------------------------------------------------------------------------
# FABRICA DECLARATIVA
# ----------------------------------------------------------------------------

def criar_mensagem(configuracao: Mapping[str, Any]) -> Any:
    """Cria uma mensagem a partir de uma configuracao declarativa.

    Args:
        configuracao (Mapping[str, Any]): Tipo, texto e opcoes da mensagem.

    Returns:
        Any: Retorno do componente criado.

    Raises:
        ConfiguracaoMensagemInvalidaError: Caso a configuracao seja invalida.
    """
    if not isinstance(configuracao, Mapping):
        raise ConfiguracaoMensagemInvalidaError(
            "A configuracao deve ser um mapeamento."
        )
    parametros = dict(configuracao)
    tipo = _validar_texto(parametros.pop("tipo", "informacao"), "tipo")
    assert isinstance(tipo, str)
    tipo = tipo.lower()
    if tipo == "toast":
        return exibir_toast(**parametros)
    if tipo == "excecao":
        return exibir_excecao(**parametros)
    if tipo == "status":
        return criar_status(**parametros)
    if tipo == "progresso":
        return exibir_progresso(**parametros)
    if tipo == "celebracao":
        animacao = parametros.pop(
            "celebracao",
            parametros.pop("animacao", "baloes")
        )
        if parametros:
            chaves = ", ".join(sorted(parametros))
            raise ConfiguracaoMensagemInvalidaError(
                f"Parametros nao suportados para celebracao: {chaves}."
            )
        return celebrar(animacao)
    return exibir_mensagem(tipo=tipo, **parametros)


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "TIPOS_MENSAGEM_VALIDOS",
    "DURACOES_TOAST_VALIDAS",
    "ESTADOS_STATUS_VALIDOS",
    "TIPOS_STATUS_VALIDOS",
    "LARGURAS_MENSAGEM_VALIDAS",
    "ICONES_MENSAGEM_PADRAO",
    "PREFIXO_CHAVE_MENSAGEM",
    "exibir_mensagem",
    "mensagem_sucesso",
    "mensagem_informacao",
    "mensagem_aviso",
    "mensagem_erro",
    "exibir_toast",
    "exibir_excecao",
    "criar_status",
    "executar_com_status",
    "exibir_progresso",
    "celebrar",
    "criar_mensagem"
]
