"""
============================================================
Modulo: DASHBOARD_STREAMLIT / excecoes.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Excecoes personalizadas e centralizadas da biblioteca de dashboards
    Streamlit. O modulo organiza os erros por area funcional e permite
    capturas genericas ou especificas sem duplicar classes entre arquivos.
Dependencias:
    - Nenhuma dependencia externa
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial da hierarquia de excecoes.
        - Inclusao dos grupos de configuracao, componentes e dados.
        - Inclusao dos grupos de cache, estado, graficos e navegacao.
        - Inclusao de funcoes auxiliares para mensagens e contexto.
============================================================
"""

# ----------------------------------------------------------------------------
# IMPORTACOES
# ----------------------------------------------------------------------------

# Importa Any para aceitar valores de contexto de diferentes tipos
from typing import Any


# ----------------------------------------------------------------------------
# EXCECAO BASE
# ----------------------------------------------------------------------------

class DashboardStreamlitError(Exception):
    """
    Excecao base de toda a biblioteca DASHBOARD_STREAMLIT.

    Atributos:
        mensagem (str): Mensagem principal do erro.
        codigo (str | None): Codigo opcional para identificacao do erro.
        contexto (dict[str, Any]): Informacoes adicionais da operacao.
    """

    def __init__(
        self,
        mensagem: str,
        *,
        codigo: str | None = None,
        contexto: dict[str, Any] | None = None
    ) -> None:
        """
        Inicializa uma excecao da biblioteca.

        Args:
            mensagem (str): Descricao principal do erro.
            codigo (str | None): Codigo opcional para identificacao.
            contexto (dict[str, Any] | None): Informacoes adicionais.

        Returns:
            None: O construtor nao possui valor de retorno.

        Raises:
            TypeError: Caso mensagem, codigo ou contexto tenham tipo invalido.
            ValueError: Caso a mensagem esteja vazia.
        """
        if not isinstance(mensagem, str):
            raise TypeError("A mensagem da excecao deve ser uma string.")

        mensagem_normalizada = mensagem.strip()
        if not mensagem_normalizada:
            raise ValueError("A mensagem da excecao nao pode estar vazia.")

        if codigo is not None and not isinstance(codigo, str):
            raise TypeError("O codigo da excecao deve ser uma string ou None.")

        if contexto is not None and not isinstance(contexto, dict):
            raise TypeError("O contexto da excecao deve ser um dicionario ou None.")

        self.mensagem = mensagem_normalizada
        self.codigo = codigo.strip() if isinstance(codigo, str) else None
        self.contexto = dict(contexto or {})
        super().__init__(self.mensagem)

    def __str__(self) -> str:
        """
        Retorna a representacao textual amigavel da excecao.

        Args:
            Nenhum.

        Returns:
            str: Codigo opcional seguido da mensagem principal.

        Raises:
            DashboardStreamlitError: Nunca e gerada no fluxo normal.
        """
        if self.codigo:
            return f"[{self.codigo}] {self.mensagem}"
        return self.mensagem

    def para_dicionario(self) -> dict[str, Any]:
        """
        Converte a excecao para uma estrutura serializavel.

        Args:
            Nenhum.

        Returns:
            dict[str, Any]: Tipo, mensagem, codigo e contexto do erro.

        Raises:
            DashboardStreamlitError: Nunca e gerada no fluxo normal.
        """
        return {
            "tipo": self.__class__.__name__,
            "mensagem": self.mensagem,
            "codigo": self.codigo,
            "contexto": dict(self.contexto)
        }


# ----------------------------------------------------------------------------
# CONFIGURACAO E ESTILOS
# ----------------------------------------------------------------------------

class ConfiguracaoDashboardError(DashboardStreamlitError, ValueError):
    """Erro base de configuracoes da pagina ou do dashboard."""


class ConfiguracaoPaginaInvalidaError(ConfiguracaoDashboardError):
    """Indica titulo, icone, layout, sidebar ou menu invalido."""


class ConfiguracaoVisualInvalidaError(ConfiguracaoDashboardError):
    """Indica dimensao, espacamento ou opcao visual invalida."""


class EstiloDashboardError(DashboardStreamlitError, ValueError):
    """Erro base para aplicacao de temas e estilos visuais."""


class CorInvalidaError(EstiloDashboardError):
    """Indica que uma cor nao possui formato reconhecido."""


class FonteInvalidaError(EstiloDashboardError):
    """Indica que uma familia ou tamanho de fonte e invalido."""


class CSSInvalidoError(EstiloDashboardError):
    """Indica que um bloco CSS e vazio, invalido ou incompatível."""


# ----------------------------------------------------------------------------
# COMPONENTES E LAYOUT
# ----------------------------------------------------------------------------

class ComponenteDashboardError(DashboardStreamlitError):
    """Erro base para componentes visuais do dashboard."""


class CardDashboardError(ComponenteDashboardError):
    """Erro base para criacao e exibicao de cards."""


class CardInvalidoError(CardDashboardError, ValueError):
    """Indica configuracao, tipo ou conteudo invalido de um card."""


class MetricaDashboardError(ComponenteDashboardError):
    """Erro base para metricas e indicadores do dashboard."""


class MetricaInvalidaError(MetricaDashboardError, ValueError):
    """Indica valor, variacao ou formato invalido de uma metrica."""


class LayoutDashboardError(ComponenteDashboardError):
    """Erro base para colunas, containers, abas e secoes."""


class LayoutInvalidoError(LayoutDashboardError, ValueError):
    """Indica estrutura, proporcao ou alinhamento invalido de layout."""


class TextoDashboardError(ComponenteDashboardError):
    """Erro base para titulos, descricoes e textos de destaque."""


class TextoInvalidoError(TextoDashboardError, ValueError):
    """Indica texto vazio, nivel ou alinhamento invalido."""


# ----------------------------------------------------------------------------
# DADOS, TABELAS E FILTROS
# ----------------------------------------------------------------------------

class DadosDashboardError(DashboardStreamlitError):
    """Erro base para validacao e manipulacao de dados."""


class DataFrameInvalidoError(DadosDashboardError, TypeError):
    """Indica que o objeto nao e um DataFrame valido."""


class DataFrameVazioError(DadosDashboardError, ValueError):
    """Indica que uma operacao exige um DataFrame com registros."""


class ColunaNaoEncontradaError(DadosDashboardError, KeyError):
    """Indica que uma coluna solicitada nao existe no conjunto de dados."""


class ValorDadosInvalidoError(DadosDashboardError, ValueError):
    """Indica que um valor de dados nao atende a operacao solicitada."""


class TabelaDashboardError(ComponenteDashboardError):
    """Erro base para tabelas, dataframes e editores de dados."""


class ConfiguracaoTabelaInvalidaError(TabelaDashboardError, ValueError):
    """Indica altura, formato ou configuracao de coluna invalida."""


class FiltroDashboardError(ComponenteDashboardError):
    """Erro base para filtros e barras de filtros."""


class ConfiguracaoFiltroInvalidaError(FiltroDashboardError, ValueError):
    """Indica tipo, coluna, opcoes ou valor padrao invalido de filtro."""


class ValorFiltroInvalidoError(FiltroDashboardError, ValueError):
    """Indica selecao ou intervalo invalido de um filtro."""


# ----------------------------------------------------------------------------
# GRAFICOS
# ----------------------------------------------------------------------------

class GraficoDashboardError(ComponenteDashboardError):
    """Erro base para criacao e exibicao de graficos."""


class ConfiguracaoGraficoInvalidaError(GraficoDashboardError, ValueError):
    """Indica tipo, eixo, cor, legenda ou configuracao invalida."""


class DadosGraficoInvalidosError(GraficoDashboardError, ValueError):
    """Indica dados ausentes ou incompatíveis com o grafico."""


class BibliotecaGraficoIndisponivelError(GraficoDashboardError, ImportError):
    """Indica ausencia de uma biblioteca necessaria para o grafico."""


# ----------------------------------------------------------------------------
# CACHE E ESTADO
# ----------------------------------------------------------------------------

class CacheDashboardError(DashboardStreamlitError):
    """Erro base para operacoes de cache de dados e recursos."""


class ConfiguracaoCacheInvalidaError(CacheDashboardError, ValueError):
    """Indica expiracao, limite, persistencia ou hash invalido."""


class FuncaoCacheInvalidaError(CacheDashboardError, TypeError):
    """Indica que o objeto informado nao e uma funcao cacheavel."""


class CacheIndisponivelError(CacheDashboardError, AttributeError):
    """Indica que uma funcao nao possui cache que possa ser manipulado."""


class EstadoDashboardError(DashboardStreamlitError):
    """Erro base para operacoes do Session State."""


class ChaveEstadoInvalidaError(EstadoDashboardError, ValueError):
    """Indica que uma chave do estado e vazia ou possui tipo invalido."""


class EstadoNaoEncontradoError(EstadoDashboardError, KeyError):
    """Indica que uma chave obrigatoria nao existe no Session State."""


class ValorEstadoInvalidoError(EstadoDashboardError, TypeError):
    """Indica valor incompatível com uma operacao do estado."""


# ----------------------------------------------------------------------------
# NAVEGACAO, PAGINAS E FORMULARIOS
# ----------------------------------------------------------------------------

class NavegacaoDashboardError(DashboardStreamlitError):
    """Erro base para navegacao e aplicacoes multipaginas."""


class PaginaNaoEncontradaError(NavegacaoDashboardError, LookupError):
    """Indica que uma pagina solicitada nao foi cadastrada."""


class ConfiguracaoNavegacaoInvalidaError(NavegacaoDashboardError, ValueError):
    """Indica pagina, grupo, posicao ou menu de navegacao invalido."""


class PaginaDashboardError(DashboardStreamlitError):
    """Erro base para montagem de paginas completas."""


class ConfiguracaoPaginaDashboardInvalidaError(PaginaDashboardError, ValueError):
    """Indica configuracao invalida de cabecalho, conteudo ou rodape."""


class FormularioDashboardError(ComponenteDashboardError):
    """Erro base para formularios e campos de entrada."""


class ConfiguracaoFormularioInvalidaError(FormularioDashboardError, ValueError):
    """Indica campo, tipo, opcao ou botao invalido de formulario."""


class ValidacaoFormularioError(FormularioDashboardError, ValueError):
    """Indica que os dados preenchidos nao passaram pela validacao."""


# ----------------------------------------------------------------------------
# MENSAGENS E UTILITARIOS
# ----------------------------------------------------------------------------

class MensagemDashboardError(ComponenteDashboardError):
    """Erro base para alertas, toasts e mensagens visuais."""


class ConfiguracaoMensagemInvalidaError(MensagemDashboardError, ValueError):
    """Indica tipo, texto, icone ou duracao invalida de mensagem."""


class UtilitarioDashboardError(DashboardStreamlitError):
    """Erro base para funcoes utilitarias compartilhadas."""


class FormatacaoDashboardError(UtilitarioDashboardError, ValueError):
    """Indica falha na formatacao de numero, moeda, data ou percentual."""


class ChaveComponenteInvalidaError(UtilitarioDashboardError, ValueError):
    """Indica chave vazia ou duplicada de um componente Streamlit."""


# ----------------------------------------------------------------------------
# FUNCOES AUXILIARES
# ----------------------------------------------------------------------------

def adicionar_contexto_erro(
    erro: DashboardStreamlitError,
    **contexto: Any
) -> DashboardStreamlitError:
    """
    Adiciona informacoes de contexto a uma excecao da biblioteca.

    Args:
        erro (DashboardStreamlitError): Excecao que sera enriquecida.
        **contexto (Any): Informacoes adicionais da operacao.

    Returns:
        DashboardStreamlitError: A propria excecao atualizada.

    Raises:
        TypeError: Caso erro nao pertença a hierarquia da biblioteca.
    """
    if not isinstance(erro, DashboardStreamlitError):
        raise TypeError(
            "O parametro 'erro' deve ser uma DashboardStreamlitError."
        )

    erro.contexto.update(contexto)
    return erro


def obter_mensagem_erro(
    erro: BaseException,
    incluir_tipo: bool = False
) -> str:
    """
    Retorna uma mensagem segura para exibicao no dashboard.

    Args:
        erro (BaseException): Excecao cuja mensagem sera obtida.
        incluir_tipo (bool): Inclui o nome da classe antes da mensagem.

    Returns:
        str: Mensagem textual pronta para exibicao.

    Raises:
        TypeError: Caso erro nao seja uma excecao ou a opcao nao seja booleana.
    """
    if not isinstance(erro, BaseException):
        raise TypeError("O parametro 'erro' deve ser uma excecao.")

    if not isinstance(incluir_tipo, bool):
        raise TypeError("O parametro 'incluir_tipo' deve ser booleano.")

    mensagem = str(erro).strip() or "Ocorreu um erro inesperado."
    if incluir_tipo:
        return f"{erro.__class__.__name__}: {mensagem}"
    return mensagem


def converter_excecao(
    erro: BaseException,
    classe_excecao: type[DashboardStreamlitError] = DashboardStreamlitError,
    mensagem: str | None = None,
    *,
    codigo: str | None = None,
    contexto: dict[str, Any] | None = None
) -> DashboardStreamlitError:
    """
    Converte uma excecao externa para a hierarquia do dashboard.

    Args:
        erro (BaseException): Excecao original que sera convertida.
        classe_excecao (type): Classe de destino da biblioteca.
        mensagem (str | None): Mensagem personalizada ou None para usar a original.
        codigo (str | None): Codigo opcional de identificacao.
        contexto (dict[str, Any] | None): Informacoes adicionais do erro.

    Returns:
        DashboardStreamlitError: Nova excecao com causa preservada.

    Raises:
        TypeError: Caso erro ou classe_excecao sejam invalidos.
    """
    if not isinstance(erro, BaseException):
        raise TypeError("O parametro 'erro' deve ser uma excecao.")

    if not isinstance(classe_excecao, type) or not issubclass(
        classe_excecao,
        DashboardStreamlitError
    ):
        raise TypeError(
            "O parametro 'classe_excecao' deve herdar de DashboardStreamlitError."
        )

    mensagem_final = mensagem if mensagem is not None else obter_mensagem_erro(erro)
    nova_excecao = classe_excecao(
        mensagem_final,
        codigo=codigo,
        contexto=contexto
    )
    nova_excecao.__cause__ = erro
    return nova_excecao


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "DashboardStreamlitError",
    "ConfiguracaoDashboardError",
    "ConfiguracaoPaginaInvalidaError",
    "ConfiguracaoVisualInvalidaError",
    "EstiloDashboardError",
    "CorInvalidaError",
    "FonteInvalidaError",
    "CSSInvalidoError",
    "ComponenteDashboardError",
    "CardDashboardError",
    "CardInvalidoError",
    "MetricaDashboardError",
    "MetricaInvalidaError",
    "LayoutDashboardError",
    "LayoutInvalidoError",
    "TextoDashboardError",
    "TextoInvalidoError",
    "DadosDashboardError",
    "DataFrameInvalidoError",
    "DataFrameVazioError",
    "ColunaNaoEncontradaError",
    "ValorDadosInvalidoError",
    "TabelaDashboardError",
    "ConfiguracaoTabelaInvalidaError",
    "FiltroDashboardError",
    "ConfiguracaoFiltroInvalidaError",
    "ValorFiltroInvalidoError",
    "GraficoDashboardError",
    "ConfiguracaoGraficoInvalidaError",
    "DadosGraficoInvalidosError",
    "BibliotecaGraficoIndisponivelError",
    "CacheDashboardError",
    "ConfiguracaoCacheInvalidaError",
    "FuncaoCacheInvalidaError",
    "CacheIndisponivelError",
    "EstadoDashboardError",
    "ChaveEstadoInvalidaError",
    "EstadoNaoEncontradoError",
    "ValorEstadoInvalidoError",
    "NavegacaoDashboardError",
    "PaginaNaoEncontradaError",
    "ConfiguracaoNavegacaoInvalidaError",
    "PaginaDashboardError",
    "ConfiguracaoPaginaDashboardInvalidaError",
    "FormularioDashboardError",
    "ConfiguracaoFormularioInvalidaError",
    "ValidacaoFormularioError",
    "MensagemDashboardError",
    "ConfiguracaoMensagemInvalidaError",
    "UtilitarioDashboardError",
    "FormatacaoDashboardError",
    "ChaveComponenteInvalidaError",
    "adicionar_contexto_erro",
    "obter_mensagem_erro",
    "converter_excecao"
]
