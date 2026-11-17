"""
============================================================
Modulo: DASHBOARD_STREAMLIT / formularios.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes reutilizaveis para criar campos e formularios Streamlit.
    O modulo permite montar formularios individuais ou automaticos,
    validar campos obrigatorios e retornar dados prontos para processamento.
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao dos campos individuais e formulario automatico.
        - Inclusao da validacao de dados e do botao de envio.
============================================================
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import date, time
from typing import Any

import streamlit as st

try:
    from .constantes import TIPOS_CAMPO
    from .excecoes import (
        ConfiguracaoFormularioInvalidaError,
        ValidacaoFormularioError,
    )
except ImportError:
    from constantes import TIPOS_CAMPO
    from excecoes import (
        ConfiguracaoFormularioInvalidaError,
        ValidacaoFormularioError,
    )


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

TIPOS_BOTAO_VALIDOS = {"primary", "secondary", "tertiary"}
VISIBILIDADES_ROTULO_VALIDAS = {"visible", "hidden", "collapsed"}
LARGURAS_FORMULARIO_VALIDAS = {"stretch", "content"}
FORMATO_DATA_PADRAO = "DD/MM/YYYY"
PREFIXO_CHAVE_CAMPO = "campo"
PREFIXO_CHAVE_FORMULARIO = "formulario"
TEXTO_BOTAO_ENVIAR = "Enviar"


# ----------------------------------------------------------------------------
# VALIDACOES INTERNAS
# ----------------------------------------------------------------------------

def _validar_texto(valor: Any, nome: str) -> str:
    """Valida um texto obrigatorio.

    Args:
        valor (Any): Valor que sera validado.
        nome (str): Nome utilizado na mensagem.

    Returns:
        str: Texto normalizado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso o texto seja invalido.
    """
    if not isinstance(valor, str) or not valor.strip():
        raise ConfiguracaoFormularioInvalidaError(
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


def _validar_opcoes(opcoes: Sequence[Any]) -> list[Any]:
    """Valida uma sequencia de opcoes.

    Args:
        opcoes (Sequence[Any]): Opcoes do campo.

    Returns:
        list[Any]: Opcoes convertidas em lista.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso a colecao seja invalida.
    """
    if isinstance(opcoes, (str, bytes)) or not isinstance(opcoes, Sequence):
        raise ConfiguracaoFormularioInvalidaError(
            "O parametro 'opcoes' deve ser uma sequencia nao textual."
        )
    return list(opcoes)


def _gerar_chave(chave: str | None, rotulo: str) -> str:
    """Gera uma chave previsivel para um campo.

    Args:
        chave (str | None): Chave personalizada.
        rotulo (str): Rotulo usado como base.

    Returns:
        str: Chave do widget.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso a chave seja invalida.
    """
    if chave is not None:
        return _validar_texto(chave, "chave")
    base = "_".join(_validar_texto(rotulo, "rotulo").lower().split())
    return f"{PREFIXO_CHAVE_CAMPO}_{base}"


def _validar_visibilidade(valor: str) -> str:
    """Valida a visibilidade do rotulo.

    Args:
        valor (str): Visibilidade solicitada.

    Returns:
        str: Valor normalizado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso seja desconhecida.
    """
    resultado = _validar_texto(valor, "visibilidade_rotulo").lower()
    if resultado not in VISIBILIDADES_ROTULO_VALIDAS:
        raise ConfiguracaoFormularioInvalidaError(
            "A visibilidade deve ser visible, hidden ou collapsed."
        )
    return resultado


# ----------------------------------------------------------------------------
# CAMPOS INDIVIDUAIS
# ----------------------------------------------------------------------------

def campo_texto(
    rotulo: str,
    valor_padrao: str = "",
    *,
    chave: str | None = None,
    placeholder: str | None = None,
    ajuda: str | None = None,
    maximo_caracteres: int | None = None,
    desabilitado: bool = False,
    visibilidade_rotulo: str = "visible"
) -> str:
    """Cria um campo de texto de uma linha.

    Args:
        rotulo (str): Rotulo do campo.
        valor_padrao (str): Texto inicial.
        chave (str | None): Chave unica.
        placeholder (str | None): Texto de exemplo.
        ajuda (str | None): Texto de ajuda.
        maximo_caracteres (int | None): Limite de caracteres.
        desabilitado (bool): Desabilita o campo.
        visibilidade_rotulo (str): Visibilidade do rotulo.

    Returns:
        str: Texto informado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso a configuracao seja invalida.
    """
    nome = _validar_texto(rotulo, "rotulo")
    if not isinstance(valor_padrao, str):
        raise ConfiguracaoFormularioInvalidaError(
            "O valor padrao deve ser uma string."
        )
    if maximo_caracteres is not None and (
        isinstance(maximo_caracteres, bool)
        or not isinstance(maximo_caracteres, int)
        or maximo_caracteres < 1
    ):
        raise ConfiguracaoFormularioInvalidaError(
            "O maximo de caracteres deve ser inteiro positivo ou None."
        )
    _validar_booleano(desabilitado, "desabilitado")
    return st.text_input(
        nome,
        value=valor_padrao,
        max_chars=maximo_caracteres,
        key=_gerar_chave(chave, nome),
        help=ajuda,
        placeholder=placeholder,
        disabled=desabilitado,
        label_visibility=_validar_visibilidade(visibilidade_rotulo)
    )


def campo_texto_longo(
    rotulo: str,
    valor_padrao: str = "",
    *,
    chave: str | None = None,
    altura: int = 120,
    placeholder: str | None = None,
    ajuda: str | None = None,
    maximo_caracteres: int | None = None
) -> str:
    """Cria um campo de texto com varias linhas.

    Args:
        rotulo (str): Rotulo do campo.
        valor_padrao (str): Texto inicial.
        chave (str | None): Chave unica.
        altura (int): Altura entre 68 e 1000 pixels.
        placeholder (str | None): Texto de exemplo.
        ajuda (str | None): Texto de ajuda.
        maximo_caracteres (int | None): Limite de caracteres.

    Returns:
        str: Texto informado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso a configuracao seja invalida.
    """
    nome = _validar_texto(rotulo, "rotulo")
    if not isinstance(valor_padrao, str):
        raise ConfiguracaoFormularioInvalidaError("O valor padrao deve ser texto.")
    if isinstance(altura, bool) or not isinstance(altura, int) or not 68 <= altura <= 1000:
        raise ConfiguracaoFormularioInvalidaError(
            "A altura deve ser inteira entre 68 e 1000."
        )
    if maximo_caracteres is not None and (
        isinstance(maximo_caracteres, bool)
        or not isinstance(maximo_caracteres, int)
        or maximo_caracteres < 1
    ):
        raise ConfiguracaoFormularioInvalidaError(
            "O maximo de caracteres deve ser inteiro positivo ou None."
        )
    return st.text_area(
        nome,
        value=valor_padrao,
        height=altura,
        max_chars=maximo_caracteres,
        key=_gerar_chave(chave, nome),
        help=ajuda,
        placeholder=placeholder
    )


def campo_numero(
    rotulo: str,
    valor_padrao: int | float = 0,
    *,
    minimo: int | float | None = None,
    maximo: int | float | None = None,
    passo: int | float = 1,
    formato: str | None = None,
    chave: str | None = None,
    ajuda: str | None = None
) -> int | float:
    """Cria um campo numerico.

    Args:
        rotulo (str): Rotulo do campo.
        valor_padrao (int | float): Valor inicial.
        minimo (int | float | None): Menor valor permitido.
        maximo (int | float | None): Maior valor permitido.
        passo (int | float): Incremento do campo.
        formato (str | None): Formato printf opcional.
        chave (str | None): Chave unica.
        ajuda (str | None): Texto de ajuda.

    Returns:
        int | float: Valor informado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso os numeros sejam invalidos.
    """
    nome = _validar_texto(rotulo, "rotulo")
    numeros = [valor_padrao, passo]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in numeros):
        raise ConfiguracaoFormularioInvalidaError(
            "Valor padrao e passo devem ser numericos."
        )
    if passo <= 0:
        raise ConfiguracaoFormularioInvalidaError("O passo deve ser positivo.")
    if minimo is not None and maximo is not None and minimo > maximo:
        raise ConfiguracaoFormularioInvalidaError(
            "O minimo nao pode ser maior que o maximo."
        )
    if minimo is not None and valor_padrao < minimo:
        raise ConfiguracaoFormularioInvalidaError(
            "O valor padrao e menor que o minimo."
        )
    if maximo is not None and valor_padrao > maximo:
        raise ConfiguracaoFormularioInvalidaError(
            "O valor padrao e maior que o maximo."
        )
    parametros: dict[str, Any] = {
        "label": nome,
        "value": valor_padrao,
        "min_value": minimo,
        "max_value": maximo,
        "step": passo,
        "key": _gerar_chave(chave, nome),
        "help": ajuda
    }
    if formato is not None:
        parametros["format"] = _validar_texto(formato, "formato")
    return st.number_input(**parametros)


def campo_data(
    rotulo: str,
    valor_padrao: date | str | None = None,
    *,
    data_minima: date | str | None = None,
    data_maxima: date | str | None = None,
    formato: str = FORMATO_DATA_PADRAO,
    chave: str | None = None,
    ajuda: str | None = None
) -> Any:
    """Cria um campo de data.

    Args:
        rotulo (str): Rotulo do campo.
        valor_padrao (date | str | None): Data inicial.
        data_minima (date | str | None): Menor data permitida.
        data_maxima (date | str | None): Maior data permitida.
        formato (str): Formato visual.
        chave (str | None): Chave unica.
        ajuda (str | None): Texto de ajuda.

    Returns:
        Any: Data informada.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso rotulo ou formato seja invalido.
    """
    nome = _validar_texto(rotulo, "rotulo")
    return st.date_input(
        nome,
        value=valor_padrao,
        min_value=data_minima,
        max_value=data_maxima,
        format=_validar_texto(formato, "formato"),
        key=_gerar_chave(chave, nome),
        help=ajuda
    )


def campo_hora(
    rotulo: str,
    valor_padrao: time | None = None,
    *,
    passo_segundos: int = 900,
    chave: str | None = None,
    ajuda: str | None = None
) -> Any:
    """Cria um campo de horario.

    Args:
        rotulo (str): Rotulo do campo.
        valor_padrao (time | None): Horario inicial.
        passo_segundos (int): Intervalo entre horarios em segundos.
        chave (str | None): Chave unica.
        ajuda (str | None): Texto de ajuda.

    Returns:
        Any: Horario informado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso o passo seja invalido.
    """
    nome = _validar_texto(rotulo, "rotulo")
    if isinstance(passo_segundos, bool) or not isinstance(passo_segundos, int) or passo_segundos < 1:
        raise ConfiguracaoFormularioInvalidaError(
            "O passo em segundos deve ser um inteiro positivo."
        )
    return st.time_input(
        nome,
        value=valor_padrao,
        step=passo_segundos,
        key=_gerar_chave(chave, nome),
        help=ajuda
    )


def campo_selecao(
    rotulo: str,
    opcoes: Sequence[Any],
    *,
    valor_padrao: Any = None,
    chave: str | None = None,
    ajuda: str | None = None,
    permitir_vazio: bool = False
) -> Any:
    """Cria um campo de selecao unica.

    Args:
        rotulo (str): Rotulo do campo.
        opcoes (Sequence[Any]): Opcoes disponiveis.
        valor_padrao (Any): Opcao selecionada inicialmente.
        chave (str | None): Chave unica.
        ajuda (str | None): Texto de ajuda.
        permitir_vazio (bool): Permite iniciar sem selecao.

    Returns:
        Any: Opcao selecionada.

    Raises:
        ValidacaoFormularioError: Caso o valor padrao nao exista.
    """
    nome = _validar_texto(rotulo, "rotulo")
    valores = _validar_opcoes(opcoes)
    _validar_booleano(permitir_vazio, "permitir_vazio")
    if valor_padrao is not None and valor_padrao not in valores:
        raise ValidacaoFormularioError(
            "O valor padrao nao pertence as opcoes do campo."
        )
    indice = None if valor_padrao is None and permitir_vazio else 0
    if valor_padrao is not None:
        indice = valores.index(valor_padrao)
    return st.selectbox(
        nome,
        valores,
        index=indice,
        key=_gerar_chave(chave, nome),
        help=ajuda
    )


def campo_multisselecao(
    rotulo: str,
    opcoes: Sequence[Any],
    *,
    valores_padrao: Sequence[Any] | None = None,
    maximo_selecoes: int | None = None,
    chave: str | None = None,
    ajuda: str | None = None
) -> list[Any]:
    """Cria um campo de selecao multipla.

    Args:
        rotulo (str): Rotulo do campo.
        opcoes (Sequence[Any]): Opcoes disponiveis.
        valores_padrao (Sequence[Any] | None): Selecoes iniciais.
        maximo_selecoes (int | None): Limite opcional.
        chave (str | None): Chave unica.
        ajuda (str | None): Texto de ajuda.

    Returns:
        list[Any]: Opcoes selecionadas.

    Raises:
        ValidacaoFormularioError: Caso uma selecao padrao nao exista.
    """
    nome = _validar_texto(rotulo, "rotulo")
    valores = _validar_opcoes(opcoes)
    padroes = [] if valores_padrao is None else _validar_opcoes(valores_padrao)
    invalidos = [v for v in padroes if v not in valores]
    if invalidos:
        raise ValidacaoFormularioError(
            f"Valores padrao nao encontrados: {invalidos}."
        )
    if maximo_selecoes is not None and (
        isinstance(maximo_selecoes, bool)
        or not isinstance(maximo_selecoes, int)
        or maximo_selecoes < 1
    ):
        raise ConfiguracaoFormularioInvalidaError(
            "O maximo de selecoes deve ser inteiro positivo ou None."
        )
    return list(st.multiselect(
        nome,
        valores,
        default=padroes,
        max_selections=maximo_selecoes,
        key=_gerar_chave(chave, nome),
        help=ajuda
    ))


def campo_booleano(
    rotulo: str,
    valor_padrao: bool = False,
    *,
    chave: str | None = None,
    ajuda: str | None = None
) -> bool:
    """Cria um campo booleano no formato checkbox.

    Args:
        rotulo (str): Rotulo do campo.
        valor_padrao (bool): Estado inicial.
        chave (str | None): Chave unica.
        ajuda (str | None): Texto de ajuda.

    Returns:
        bool: Estado atual.

    Raises:
        TypeError: Caso o valor padrao nao seja booleano.
    """
    nome = _validar_texto(rotulo, "rotulo")
    _validar_booleano(valor_padrao, "valor_padrao")
    return bool(st.checkbox(
        nome,
        value=valor_padrao,
        key=_gerar_chave(chave, nome),
        help=ajuda
    ))


def campo_arquivo(
    rotulo: str,
    *,
    tipos: Sequence[str] | None = None,
    varios_arquivos: bool = False,
    chave: str | None = None,
    ajuda: str | None = None
) -> Any:
    """Cria um campo para envio de arquivos.

    Args:
        rotulo (str): Rotulo do campo.
        tipos (Sequence[str] | None): Extensoes permitidas.
        varios_arquivos (bool): Permite multiplos arquivos.
        chave (str | None): Chave unica.
        ajuda (str | None): Texto de ajuda.

    Returns:
        Any: Arquivo ou lista retornada pelo Streamlit.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso os tipos sejam invalidos.
    """
    nome = _validar_texto(rotulo, "rotulo")
    extensoes = None if tipos is None else _validar_opcoes(tipos)
    if extensoes is not None and not all(
        isinstance(item, str) and item.strip() for item in extensoes
    ):
        raise ConfiguracaoFormularioInvalidaError(
            "Todos os tipos de arquivo devem ser textos preenchidos."
        )
    _validar_booleano(varios_arquivos, "varios_arquivos")
    return st.file_uploader(
        nome,
        type=extensoes,
        accept_multiple_files=varios_arquivos,
        key=_gerar_chave(chave, nome),
        help=ajuda
    )


# ----------------------------------------------------------------------------
# VALIDACAO E FORMULARIO AUTOMATICO
# ----------------------------------------------------------------------------

def validar_dados_formulario(
    dados: Mapping[str, Any],
    campos_obrigatorios: Sequence[str] | None = None,
    validadores: Mapping[str, Callable[[Any], bool | str | None]] | None = None
) -> dict[str, Any]:
    """Valida dados preenchidos antes do processamento.

    Args:
        dados (Mapping[str, Any]): Valores coletados.
        campos_obrigatorios (Sequence[str] | None): Chaves obrigatorias.
        validadores (Mapping | None): Funcoes de validacao por campo.

    Returns:
        dict[str, Any]: Copia dos dados validados.

    Raises:
        ValidacaoFormularioError: Caso algum campo seja invalido.
    """
    if not isinstance(dados, Mapping):
        raise ConfiguracaoFormularioInvalidaError(
            "O parametro 'dados' deve ser um mapeamento."
        )
    obrigatorios = [] if campos_obrigatorios is None else _validar_opcoes(campos_obrigatorios)
    validadores_finais = {} if validadores is None else dict(validadores)

    erros: list[str] = []
    for campo in obrigatorios:
        chave = _validar_texto(campo, "campo_obrigatorio")
        valor = dados.get(chave)
        if valor is None or valor == "" or valor == [] or valor == ():
            erros.append(f"O campo '{chave}' e obrigatorio.")

    for campo, validador in validadores_finais.items():
        if not callable(validador):
            raise ConfiguracaoFormularioInvalidaError(
                f"O validador do campo '{campo}' deve ser chamavel."
            )
        retorno = validador(dados.get(campo))
        if retorno is False:
            erros.append(f"O campo '{campo}' e invalido.")
        elif isinstance(retorno, str) and retorno.strip():
            erros.append(retorno.strip())

    if erros:
        raise ValidacaoFormularioError(" ".join(erros), contexto={"erros": erros})
    return dict(dados)


def criar_campo(configuracao: Mapping[str, Any]) -> Any:
    """Cria um campo com base em uma configuracao declarativa.

    Args:
        configuracao (Mapping[str, Any]): Tipo, rotulo e parametros do campo.

    Returns:
        Any: Valor retornado pelo widget criado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso a configuracao seja invalida.
    """
    if not isinstance(configuracao, Mapping):
        raise ConfiguracaoFormularioInvalidaError(
            "A configuracao do campo deve ser um mapeamento."
        )
    parametros = dict(configuracao)
    tipo = _validar_texto(parametros.pop("tipo", "texto"), "tipo").lower()
    if tipo not in TIPOS_CAMPO:
        raise ConfiguracaoFormularioInvalidaError(
            f"O tipo de campo '{tipo}' nao e suportado."
        )
    funcoes = {
        "texto": campo_texto,
        "texto_longo": campo_texto_longo,
        "numero": campo_numero,
        "data": campo_data,
        "hora": campo_hora,
        "selecao": campo_selecao,
        "multisselecao": campo_multisselecao,
        "booleano": campo_booleano,
        "arquivo": campo_arquivo,
    }
    return funcoes[tipo](**parametros)


def botao_enviar_formulario(
    texto: str = TEXTO_BOTAO_ENVIAR,
    *,
    tipo: str = "primary",
    icone: str | None = None,
    ajuda: str | None = None,
    desabilitado: bool = False,
    usar_largura_total: bool = True
) -> bool:
    """Cria o botao obrigatorio de envio do formulario.

    Args:
        texto (str): Texto do botao.
        tipo (str): primary, secondary ou tertiary.
        icone (str | None): Emoji ou Material icon.
        ajuda (str | None): Texto de ajuda.
        desabilitado (bool): Desabilita o botao.
        usar_largura_total (bool): Estende o botao no container.

    Returns:
        bool: True quando o formulario foi enviado.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso tipo seja invalido.
    """
    rotulo = _validar_texto(texto, "texto")
    tipo_normalizado = _validar_texto(tipo, "tipo").lower()
    if tipo_normalizado not in TIPOS_BOTAO_VALIDOS:
        raise ConfiguracaoFormularioInvalidaError(
            "O tipo do botao deve ser primary, secondary ou tertiary."
        )
    _validar_booleano(desabilitado, "desabilitado")
    _validar_booleano(usar_largura_total, "usar_largura_total")
    return bool(st.form_submit_button(
        rotulo,
        help=ajuda,
        type=tipo_normalizado,
        icon=icone,
        disabled=desabilitado,
        use_container_width=usar_largura_total
    ))


def criar_formulario(
    chave: str,
    campos: Mapping[str, Mapping[str, Any]],
    *,
    texto_botao: str = TEXTO_BOTAO_ENVIAR,
    limpar_ao_enviar: bool = False,
    permitir_enter: bool = True,
    exibir_borda: bool = True,
    largura: str | int = "stretch",
    validar_ao_enviar: bool = True
) -> dict[str, Any]:
    """Cria um formulario completo a partir de configuracoes de campos.

    Args:
        chave (str): Chave unica do formulario.
        campos (Mapping): Campos organizados por nome de retorno.
        texto_botao (str): Texto do botao de envio.
        limpar_ao_enviar (bool): Limpa widgets depois do envio.
        permitir_enter (bool): Permite envio pela tecla Enter.
        exibir_borda (bool): Exibe borda no container.
        largura (str | int): stretch, content ou largura em pixels.
        validar_ao_enviar (bool): Valida campos obrigatorios no envio.

    Returns:
        dict[str, Any]: Dados, estado de envio e resultado da validacao.

    Raises:
        ConfiguracaoFormularioInvalidaError: Caso a definicao seja invalida.
    """
    chave_validada = _validar_texto(chave, "chave")
    if not isinstance(campos, Mapping):
        raise ConfiguracaoFormularioInvalidaError(
            "O parametro 'campos' deve ser um mapeamento."
        )
    for nome, valor in {
        "limpar_ao_enviar": limpar_ao_enviar,
        "permitir_enter": permitir_enter,
        "exibir_borda": exibir_borda,
        "validar_ao_enviar": validar_ao_enviar,
    }.items():
        _validar_booleano(valor, nome)
    if not (
        isinstance(largura, int) and not isinstance(largura, bool) and largura > 0
    ) and largura not in LARGURAS_FORMULARIO_VALIDAS:
        raise ConfiguracaoFormularioInvalidaError(
            "A largura deve ser stretch, content ou inteiro positivo."
        )

    dados: dict[str, Any] = {}
    obrigatorios: list[str] = []
    validadores: dict[str, Callable[[Any], bool | str | None]] = {}

    with st.form(
        key=f"{PREFIXO_CHAVE_FORMULARIO}_{chave_validada}",
        clear_on_submit=limpar_ao_enviar,
        enter_to_submit=permitir_enter,
        border=exibir_borda,
        width=largura
    ):
        for nome_campo, definicao in campos.items():
            nome = _validar_texto(nome_campo, "nome_campo")
            if not isinstance(definicao, Mapping):
                raise ConfiguracaoFormularioInvalidaError(
                    f"A definicao do campo '{nome}' deve ser um mapeamento."
                )
            config = dict(definicao)
            obrigatorio = config.pop("obrigatorio", False)
            validador = config.pop("validador", None)
            _validar_booleano(obrigatorio, f"obrigatorio_{nome}")
            config.setdefault("rotulo", nome)
            config.setdefault("chave", f"{chave_validada}_{nome}")
            dados[nome] = criar_campo(config)
            if obrigatorio:
                obrigatorios.append(nome)
            if validador is not None:
                validadores[nome] = validador

        enviado = botao_enviar_formulario(texto_botao)

    valido = False
    erros: list[str] = []
    if enviado:
        if validar_ao_enviar:
            try:
                validar_dados_formulario(dados, obrigatorios, validadores)
                valido = True
            except ValidacaoFormularioError as erro:
                erros = list(erro.contexto.get("erros", [str(erro)]))
        else:
            valido = True

    return {
        "dados": dados,
        "enviado": enviado,
        "valido": valido,
        "erros": erros
    }


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "TIPOS_BOTAO_VALIDOS",
    "VISIBILIDADES_ROTULO_VALIDAS",
    "LARGURAS_FORMULARIO_VALIDAS",
    "FORMATO_DATA_PADRAO",
    "PREFIXO_CHAVE_CAMPO",
    "PREFIXO_CHAVE_FORMULARIO",
    "TEXTO_BOTAO_ENVIAR",
    "campo_texto",
    "campo_texto_longo",
    "campo_numero",
    "campo_data",
    "campo_hora",
    "campo_selecao",
    "campo_multisselecao",
    "campo_booleano",
    "campo_arquivo",
    "validar_dados_formulario",
    "criar_campo",
    "botao_enviar_formulario",
    "criar_formulario"
]
