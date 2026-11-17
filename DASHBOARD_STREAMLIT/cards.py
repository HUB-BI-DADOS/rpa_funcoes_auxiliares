"""
============================================================
Modulo: DASHBOARD_STREAMLIT / cards.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Componentes simples e modernos para exibir cards em dashboards
    Streamlit. O modulo permite criar cards de indicadores, textos,
    status, progresso e informacoes, alem de organizar varios cards
    automaticamente em uma grade responsiva.
Funcoes disponiveis:
    - exibir_card()
    - exibir_card_texto()
    - exibir_card_status()
    - exibir_card_progresso()
    - exibir_card_informacao()
    - criar_grade_cards()
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao do card generico e das variacoes especializadas.
        - Inclusao da grade automatica de cards.
============================================================
"""

# ----------------------------------------------------------------------------
# IMPORTACOES
# ----------------------------------------------------------------------------

# Importa escape para impedir que textos recebidos sejam interpretados como HTML
from html import escape

# Importa Any e Mapping para tipagem dos valores e configuracoes dos cards
from collections.abc import Mapping, Sequence
from typing import Any

# Importa Streamlit para renderizar os componentes no dashboard
import streamlit as st


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

# Define as cores principais utilizadas pelos cards
COR_PRIMARIA_PADRAO = "#2563EB"
COR_TEXTO_PADRAO = "#0F172A"
COR_TEXTO_SECUNDARIO_PADRAO = "#64748B"
COR_FUNDO_PADRAO = "#FFFFFF"
COR_BORDA_PADRAO = "#E2E8F0"

# Define as cores semanticas dos cards de status
CORES_STATUS = {
    "informacao": "#2563EB",
    "sucesso": "#16A34A",
    "alerta": "#D97706",
    "erro": "#DC2626",
    "neutro": "#64748B"
}

# Define os icones semanticos padrao
ICONES_STATUS = {
    "informacao": "ℹ️",
    "sucesso": "✓",
    "alerta": "⚠️",
    "erro": "✕",
    "neutro": "•"
}

# Define os tamanhos e espacamentos visuais padrao
RAIO_BORDA_PADRAO = 16
ESPACAMENTO_INTERNO_PADRAO = 20
ALTURA_MINIMA_PADRAO = 132
SOMBRA_PADRAO = "0 4px 18px rgba(15, 23, 42, 0.07)"

# Define os formatos aceitos para a grade de cards
QUANTIDADE_MAXIMA_COLUNAS = 6
ESPACOS_VALIDOS = {
    "small",
    "medium",
    "large"
}


# ----------------------------------------------------------------------------
# EXCECOES
# ----------------------------------------------------------------------------

class DashboardCardsError(Exception):
    """Erro base para operacoes relacionadas aos cards do dashboard."""


class ConfiguracaoCardInvalidaError(DashboardCardsError, ValueError):
    """Indica que uma configuracao visual do card e invalida."""


class CardInvalidoError(DashboardCardsError, TypeError):
    """Indica que a definicao recebida para um card e invalida."""


# ----------------------------------------------------------------------------
# FUNCOES INTERNAS DE VALIDACAO E FORMATACAO
# ----------------------------------------------------------------------------

def _validar_booleano(
    valor: bool,
    nome: str
) -> bool:
    """
    Valida estritamente um parametro booleano.

    Args:
        valor (bool):
            Valor que sera validado.
        nome (str):
            Nome do parametro utilizado na mensagem de erro.

    Returns:
        bool:
            O proprio valor booleano validado.

    Raises:
        TypeError:
            Caso o valor nao seja booleano.
    """
    if not isinstance(valor, bool):
        raise TypeError(
            f"O parametro '{nome}' deve ser booleano."
        )

    return valor


def _validar_inteiro(
    valor: int,
    nome: str,
    minimo: int | None = None,
    maximo: int | None = None
) -> int:
    """
    Valida um numero inteiro e seus limites opcionais.

    Args:
        valor (int):
            Numero inteiro que sera validado.
        nome (str):
            Nome do parametro utilizado na mensagem de erro.
        minimo (int | None):
            Menor valor permitido.
        maximo (int | None):
            Maior valor permitido.

    Returns:
        int:
            O proprio numero inteiro validado.

    Raises:
        TypeError:
            Caso o valor nao seja inteiro.
        ConfiguracaoCardInvalidaError:
            Caso o valor esteja fora dos limites definidos.
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(
            f"O parametro '{nome}' deve ser inteiro."
        )

    if minimo is not None and valor < minimo:
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' deve ser maior ou igual a {minimo}."
        )

    if maximo is not None and valor > maximo:
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' deve ser menor ou igual a {maximo}."
        )

    return valor


def _validar_numero(
    valor: int | float,
    nome: str,
    minimo: float | None = None,
    maximo: float | None = None
) -> float:
    """
    Valida um valor numerico e seus limites opcionais.

    Args:
        valor (int | float):
            Valor numerico que sera validado.
        nome (str):
            Nome do parametro utilizado na mensagem de erro.
        minimo (float | None):
            Menor valor permitido.
        maximo (float | None):
            Maior valor permitido.

    Returns:
        float:
            Valor convertido para float.

    Raises:
        TypeError:
            Caso o valor nao seja numerico.
        ConfiguracaoCardInvalidaError:
            Caso o valor esteja fora dos limites definidos.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(
            f"O parametro '{nome}' deve ser numerico."
        )

    numero = float(valor)

    if minimo is not None and numero < minimo:
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' deve ser maior ou igual a {minimo}."
        )

    if maximo is not None and numero > maximo:
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' deve ser menor ou igual a {maximo}."
        )

    return numero


def _normalizar_texto(
    valor: Any,
    nome: str,
    permitir_vazio: bool = False
) -> str:
    """
    Converte um valor em texto seguro para exibicao no card.

    Args:
        valor (Any):
            Valor que sera convertido para texto.
        nome (str):
            Nome do parametro utilizado na mensagem de erro.
        permitir_vazio (bool):
            Define se um texto vazio sera permitido.

    Returns:
        str:
            Texto convertido e sem espacos externos.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso o valor seja None ou resulte em texto vazio sem permissao.
    """
    _validar_booleano(
        permitir_vazio,
        "permitir_vazio"
    )

    if valor is None:
        if permitir_vazio:
            return ""

        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' nao pode ser None."
        )

    texto = str(valor).strip()

    if not texto and not permitir_vazio:
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' nao pode estar vazio."
        )

    return texto


def _normalizar_cor(
    cor: str,
    nome: str = "cor"
) -> str:
    """
    Valida uma cor hexadecimal utilizada pelo card.

    Args:
        cor (str):
            Cor hexadecimal com tres, seis ou oito caracteres.
        nome (str):
            Nome do parametro utilizado na mensagem de erro.

    Returns:
        str:
            Cor hexadecimal normalizada em letras maiusculas.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso a cor nao possua um formato hexadecimal valido.
    """
    if not isinstance(cor, str):
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' deve ser uma string hexadecimal."
        )

    texto = _normalizar_texto(
        cor,
        nome
    )

    codigo = texto.lstrip("#")

    if len(codigo) not in {3, 6, 8}:
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' deve possuir uma cor hexadecimal valida."
        )

    if any(
        caractere.upper() not in "0123456789ABCDEF"
        for caractere in codigo
    ):
        raise ConfiguracaoCardInvalidaError(
            f"O parametro '{nome}' deve possuir uma cor hexadecimal valida."
        )

    return f"#{codigo.upper()}"


def _formatar_valor(
    valor: Any,
    prefixo: str = "",
    sufixo: str = ""
) -> str:
    """
    Monta o texto principal do card com prefixo e sufixo opcionais.

    Args:
        valor (Any):
            Valor principal exibido no card.
        prefixo (str):
            Texto inserido antes do valor.
        sufixo (str):
            Texto inserido depois do valor.

    Returns:
        str:
            Valor formatado para exibicao.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso o valor principal seja None.
    """
    texto_valor = _normalizar_texto(
        valor,
        "valor"
    )
    if not isinstance(prefixo, str):
        raise ConfiguracaoCardInvalidaError(
            "O parametro 'prefixo' deve ser uma string."
        )

    if not isinstance(sufixo, str):
        raise ConfiguracaoCardInvalidaError(
            "O parametro 'sufixo' deve ser uma string."
        )

    # Preserva espacos intencionais usados para separar prefixos e sufixos
    return f"{prefixo}{texto_valor}{sufixo}"


def _construir_html_card(
    titulo: str,
    valor: str,
    descricao: str = "",
    icone: str = "",
    cor: str = COR_PRIMARIA_PADRAO,
    cor_fundo: str = COR_FUNDO_PADRAO,
    cor_texto: str = COR_TEXTO_PADRAO,
    cor_texto_secundario: str = COR_TEXTO_SECUNDARIO_PADRAO,
    cor_borda: str = COR_BORDA_PADRAO,
    destacar_borda: bool = True,
    altura_minima: int = ALTURA_MINIMA_PADRAO
) -> str:
    """
    Constrói o HTML seguro utilizado pelos cards modernos.

    Args:
        titulo (str):
            Titulo exibido acima do valor principal.
        valor (str):
            Valor principal exibido no card.
        descricao (str):
            Texto complementar exibido abaixo do valor.
        icone (str):
            Icone, emoji ou simbolo exibido no canto do card.
        cor (str):
            Cor de destaque do card.
        cor_fundo (str):
            Cor de fundo do card.
        cor_texto (str):
            Cor do valor principal.
        cor_texto_secundario (str):
            Cor dos textos auxiliares.
        cor_borda (str):
            Cor da borda externa.
        destacar_borda (bool):
            Define se uma faixa colorida sera exibida na lateral.
        altura_minima (int):
            Altura minima do card em pixels.

    Returns:
        str:
            Codigo HTML pronto para ser renderizado pelo Streamlit.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso algum texto, cor ou dimensao seja invalido.
    """
    titulo_seguro = escape(_normalizar_texto(titulo, "titulo"))
    valor_seguro = escape(_normalizar_texto(valor, "valor"))
    descricao_segura = escape(
        _normalizar_texto(
            descricao,
            "descricao",
            permitir_vazio=True
        )
    )
    icone_seguro = escape(
        _normalizar_texto(
            icone,
            "icone",
            permitir_vazio=True
        )
    )

    cor_destaque = _normalizar_cor(cor, "cor")
    fundo = _normalizar_cor(cor_fundo, "cor_fundo")
    texto = _normalizar_cor(cor_texto, "cor_texto")
    texto_secundario = _normalizar_cor(
        cor_texto_secundario,
        "cor_texto_secundario"
    )
    borda = _normalizar_cor(cor_borda, "cor_borda")
    _validar_booleano(destacar_borda, "destacar_borda")
    altura = _validar_inteiro(
        altura_minima,
        "altura_minima",
        minimo=80,
        maximo=600
    )

    estilo_borda = (
        f"border-left: 5px solid {cor_destaque};"
        if destacar_borda
        else ""
    )
    bloco_icone = (
        f'<div style="font-size: 1.65rem; line-height: 1;">{icone_seguro}</div>'
        if icone_seguro
        else ""
    )
    bloco_descricao = (
        f'<div style="margin-top: 8px; color: {texto_secundario}; '
        f'font-size: 0.84rem; line-height: 1.35;">{descricao_segura}</div>'
        if descricao_segura
        else ""
    )

    return f"""
<div style="
    background: {fundo};
    border: 1px solid {borda};
    {estilo_borda}
    border-radius: {RAIO_BORDA_PADRAO}px;
    padding: {ESPACAMENTO_INTERNO_PADRAO}px;
    min-height: {altura}px;
    box-shadow: {SOMBRA_PADRAO};
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
    margin-bottom: 0.75rem;
">
    <div style="display: flex; justify-content: space-between; gap: 12px;">
        <div style="color: {texto_secundario}; font-size: 0.82rem; font-weight: 600;
                    letter-spacing: 0.02em; line-height: 1.3;">
            {titulo_seguro}
        </div>
        {bloco_icone}
    </div>
    <div>
        <div style="color: {texto}; font-size: 1.75rem; font-weight: 750;
                    line-height: 1.15; overflow-wrap: anywhere;">
            {valor_seguro}
        </div>
        {bloco_descricao}
    </div>
</div>
""".strip()


def _renderizar_html(
    html: str
) -> Any:
    """
    Renderiza um bloco HTML seguro no dashboard Streamlit.

    Args:
        html (str):
            Codigo HTML previamente construido pelo modulo.

    Returns:
        Any:
            Resultado retornado por st.markdown.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso o HTML recebido esteja vazio.
    """
    codigo = _normalizar_texto(
        html,
        "html"
    )

    return st.markdown(
        codigo,
        unsafe_allow_html=True
    )


# ----------------------------------------------------------------------------
# CARDS PRINCIPAIS
# ----------------------------------------------------------------------------

def exibir_card(
    titulo: str,
    valor: Any,
    descricao: str = "",
    icone: str = "",
    cor: str = COR_PRIMARIA_PADRAO,
    prefixo: str = "",
    sufixo: str = "",
    cor_fundo: str = COR_FUNDO_PADRAO,
    destacar_borda: bool = True,
    altura_minima: int = ALTURA_MINIMA_PADRAO
) -> Any:
    """
    Exibe um card generico com titulo, valor e descricao opcional.

    Args:
        titulo (str):
            Titulo exibido no topo do card.
        valor (Any):
            Valor principal exibido em destaque.
        descricao (str):
            Texto complementar exibido abaixo do valor.
        icone (str):
            Icone, emoji ou simbolo exibido no card.
        cor (str):
            Cor hexadecimal utilizada como destaque.
        prefixo (str):
            Texto inserido antes do valor principal.
        sufixo (str):
            Texto inserido depois do valor principal.
        cor_fundo (str):
            Cor hexadecimal do fundo do card.
        destacar_borda (bool):
            Define se uma faixa lateral colorida sera exibida.
        altura_minima (int):
            Altura minima do card em pixels.

    Returns:
        Any:
            Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso algum parametro obrigatorio seja invalido.
    """
    valor_formatado = _formatar_valor(
        valor,
        prefixo=prefixo,
        sufixo=sufixo
    )

    html = _construir_html_card(
        titulo=titulo,
        valor=valor_formatado,
        descricao=descricao,
        icone=icone,
        cor=cor,
        cor_fundo=cor_fundo,
        destacar_borda=destacar_borda,
        altura_minima=altura_minima
    )

    return _renderizar_html(html)


def exibir_card_texto(
    titulo: str,
    texto: str,
    descricao: str = "",
    icone: str = "",
    cor: str = COR_PRIMARIA_PADRAO
) -> Any:
    """
    Exibe um card voltado para textos curtos e informacoes descritivas.

    Args:
        titulo (str):
            Titulo exibido no topo do card.
        texto (str):
            Texto principal exibido em destaque.
        descricao (str):
            Texto complementar opcional.
        icone (str):
            Icone, emoji ou simbolo exibido no card.
        cor (str):
            Cor hexadecimal utilizada como destaque.

    Returns:
        Any:
            Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso titulo, texto ou cor sejam invalidos.
    """
    return exibir_card(
        titulo=titulo,
        valor=texto,
        descricao=descricao,
        icone=icone,
        cor=cor
    )


def exibir_card_status(
    titulo: str,
    status: str,
    tipo: str = "informacao",
    descricao: str = "",
    icone: str | None = None
) -> Any:
    """
    Exibe um card de status com cor e icone semanticos.

    Args:
        titulo (str):
            Titulo exibido no topo do card.
        status (str):
            Texto principal que representa o status.
        tipo (str):
            Tipo semantico: informacao, sucesso, alerta, erro ou neutro.
        descricao (str):
            Texto complementar opcional.
        icone (str | None):
            Icone personalizado ou None para usar o icone semantico.

    Returns:
        Any:
            Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso o tipo de status nao seja reconhecido.
    """
    tipo_normalizado = _normalizar_texto(tipo, "tipo").lower()

    if tipo_normalizado not in CORES_STATUS:
        raise ConfiguracaoCardInvalidaError(
            "O parametro 'tipo' deve ser informacao, sucesso, alerta, "
            "erro ou neutro."
        )

    icone_final = (
        ICONES_STATUS[tipo_normalizado]
        if icone is None
        else _normalizar_texto(icone, "icone", permitir_vazio=True)
    )

    return exibir_card(
        titulo=titulo,
        valor=status,
        descricao=descricao,
        icone=icone_final,
        cor=CORES_STATUS[tipo_normalizado]
    )


def exibir_card_progresso(
    titulo: str,
    valor: int | float,
    valor_maximo: int | float = 100,
    descricao: str = "",
    icone: str = "",
    cor: str = COR_PRIMARIA_PADRAO,
    exibir_percentual: bool = True
) -> Any:
    """
    Exibe um card com barra de progresso e percentual calculado.

    Args:
        titulo (str):
            Titulo exibido no topo do card.
        valor (int | float):
            Valor atual do progresso.
        valor_maximo (int | float):
            Valor que representa cem por cento do progresso.
        descricao (str):
            Texto complementar opcional.
        icone (str):
            Icone, emoji ou simbolo exibido no card.
        cor (str):
            Cor hexadecimal da barra e do destaque.
        exibir_percentual (bool):
            Define se o percentual sera exibido como valor principal.

    Returns:
        Any:
            Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso os valores sejam negativos ou o maximo seja zero.
    """
    atual = _validar_numero(
        valor,
        "valor",
        minimo=0
    )
    maximo = _validar_numero(
        valor_maximo,
        "valor_maximo",
        minimo=0.000001
    )
    _validar_booleano(
        exibir_percentual,
        "exibir_percentual"
    )

    percentual_real = (atual / maximo) * 100
    percentual_barra = max(0.0, min(percentual_real, 100.0))
    cor_normalizada = _normalizar_cor(cor)

    valor_principal = (
        f"{percentual_real:.1f}%"
        if exibir_percentual
        else f"{atual:g} de {maximo:g}"
    )

    titulo_seguro = escape(_normalizar_texto(titulo, "titulo"))
    valor_seguro = escape(valor_principal)
    descricao_segura = escape(
        _normalizar_texto(
            descricao,
            "descricao",
            permitir_vazio=True
        )
    )
    icone_seguro = escape(
        _normalizar_texto(
            icone,
            "icone",
            permitir_vazio=True
        )
    )

    bloco_icone = (
        f'<div style="font-size: 1.65rem; line-height: 1;">{icone_seguro}</div>'
        if icone_seguro
        else ""
    )
    bloco_descricao = (
        f'<div style="margin-top: 8px; color: {COR_TEXTO_SECUNDARIO_PADRAO}; '
        f'font-size: 0.84rem;">{descricao_segura}</div>'
        if descricao_segura
        else ""
    )

    html = f"""
<div style="
    background: {COR_FUNDO_PADRAO};
    border: 1px solid {COR_BORDA_PADRAO};
    border-left: 5px solid {cor_normalizada};
    border-radius: {RAIO_BORDA_PADRAO}px;
    padding: {ESPACAMENTO_INTERNO_PADRAO}px;
    min-height: {ALTURA_MINIMA_PADRAO}px;
    box-shadow: {SOMBRA_PADRAO};
    box-sizing: border-box;
    margin-bottom: 0.75rem;
">
    <div style="display: flex; justify-content: space-between; gap: 12px;">
        <div style="color: {COR_TEXTO_SECUNDARIO_PADRAO}; font-size: 0.82rem;
                    font-weight: 600;">{titulo_seguro}</div>
        {bloco_icone}
    </div>
    <div style="color: {COR_TEXTO_PADRAO}; font-size: 1.55rem; font-weight: 750;
                margin-top: 10px;">{valor_seguro}</div>
    <div style="height: 9px; background: #E2E8F0; border-radius: 999px;
                overflow: hidden; margin-top: 12px;">
        <div style="width: {percentual_barra:.4f}%; height: 100%;
                    background: {cor_normalizada}; border-radius: 999px;"></div>
    </div>
    {bloco_descricao}
</div>
""".strip()

    return _renderizar_html(html)


def exibir_card_informacao(
    titulo: str,
    descricao: str,
    icone: str = "ℹ️",
    cor: str = COR_PRIMARIA_PADRAO,
    rotulo: str = "Informação"
) -> Any:
    """
    Exibe um card informativo com rotulo, titulo e descricao.

    Args:
        titulo (str):
            Titulo principal da informacao.
        descricao (str):
            Texto explicativo exibido no card.
        icone (str):
            Icone, emoji ou simbolo exibido no card.
        cor (str):
            Cor hexadecimal utilizada como destaque.
        rotulo (str):
            Pequeno rotulo exibido acima do titulo.

    Returns:
        Any:
            Resultado retornado pelo componente st.markdown.

    Raises:
        ConfiguracaoCardInvalidaError:
            Caso titulo, descricao, rotulo ou cor sejam invalidos.
    """
    return exibir_card(
        titulo=rotulo,
        valor=titulo,
        descricao=descricao,
        icone=icone,
        cor=cor,
        altura_minima=150
    )


# ----------------------------------------------------------------------------
# GRADE DE CARDS
# ----------------------------------------------------------------------------

def criar_grade_cards(
    cards: Sequence[Mapping[str, Any]],
    colunas: int = 4,
    espaco: str = "medium"
) -> list[Any]:
    """
    Organiza e exibe varios cards automaticamente em uma grade.

    Args:
        cards (Sequence[Mapping[str, Any]]):
            Sequencia de dicionarios com os parametros dos cards.
        colunas (int):
            Quantidade de colunas por linha, entre 1 e 6.
        espaco (str):
            Espacamento entre colunas: small, medium ou large.

    Returns:
        list[Any]:
            Resultados retornados pelos componentes renderizados.

    Raises:
        CardInvalidoError:
            Caso cards nao seja uma sequencia valida de mapeamentos.
        ConfiguracaoCardInvalidaError:
            Caso a quantidade de colunas ou o espaco sejam invalidos.
    """
    if isinstance(cards, (str, bytes)) or not isinstance(cards, Sequence):
        raise CardInvalidoError(
            "O parametro 'cards' deve ser uma sequencia de mapeamentos."
        )

    quantidade_colunas = _validar_inteiro(
        colunas,
        "colunas",
        minimo=1,
        maximo=QUANTIDADE_MAXIMA_COLUNAS
    )
    espaco_normalizado = _normalizar_texto(
        espaco,
        "espaco"
    ).lower()

    if espaco_normalizado not in ESPACOS_VALIDOS:
        raise ConfiguracaoCardInvalidaError(
            "O parametro 'espaco' deve ser small, medium ou large."
        )

    resultados: list[Any] = []

    for inicio in range(0, len(cards), quantidade_colunas):
        grupo = cards[inicio: inicio + quantidade_colunas]
        containers = st.columns(
            quantidade_colunas,
            gap=espaco_normalizado
        )

        for indice, configuracao in enumerate(grupo):
            if not isinstance(configuracao, Mapping):
                raise CardInvalidoError(
                    "Cada item de 'cards' deve ser um mapeamento."
                )

            parametros = dict(configuracao)
            tipo = str(parametros.pop("tipo", "card")).strip().lower()

            funcoes = {
                "card": exibir_card,
                "texto": exibir_card_texto,
                "status": exibir_card_status,
                "progresso": exibir_card_progresso,
                "informacao": exibir_card_informacao
            }

            if tipo not in funcoes:
                raise CardInvalidoError(
                    "O tipo do card deve ser card, texto, status, "
                    "progresso ou informacao."
                )

            with containers[indice]:
                resultado = funcoes[tipo](**parametros)
                resultados.append(resultado)

    return resultados


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "COR_PRIMARIA_PADRAO",
    "COR_TEXTO_PADRAO",
    "COR_TEXTO_SECUNDARIO_PADRAO",
    "COR_FUNDO_PADRAO",
    "COR_BORDA_PADRAO",
    "CORES_STATUS",
    "ICONES_STATUS",
    "RAIO_BORDA_PADRAO",
    "ESPACAMENTO_INTERNO_PADRAO",
    "ALTURA_MINIMA_PADRAO",
    "SOMBRA_PADRAO",
    "QUANTIDADE_MAXIMA_COLUNAS",
    "ESPACOS_VALIDOS",
    "DashboardCardsError",
    "ConfiguracaoCardInvalidaError",
    "CardInvalidoError",
    "exibir_card",
    "exibir_card_texto",
    "exibir_card_status",
    "exibir_card_progresso",
    "exibir_card_informacao",
    "criar_grade_cards"
]
