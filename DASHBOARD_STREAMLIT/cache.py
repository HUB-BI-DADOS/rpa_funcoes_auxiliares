"""
============================================================
Modulo: DASHBOARD_STREAMLIT / cache.py
Autor: Tiago Eneas Antunes (Z701038)
Data de Criacao: 29/09/2026
Ultima Alteracao: 29/09/2026
Versao: 1.0.0
Descricao:
    Funcoes simples para configurar, aplicar, consultar e limpar os caches
    de dados e recursos do Streamlit. O modulo fornece nomes em portugues
    e uma interface reduzida para acelerar a criacao de dashboards.
Funcoes disponiveis:
    - cache_dados()
    - cache_recurso()
    - limpar_cache_dados()
    - limpar_cache_recursos()
    - limpar_todos_caches()
    - limpar_cache_funcao()
    - possui_cache_funcao()
    - obter_configuracao_cache()
Dependencias:
    - streamlit
Historico:
    v1.0.0 - 29/09/2026
        - Criacao inicial do modulo.
        - Inclusao dos decoradores de dados e recursos.
        - Inclusao das operacoes de limpeza global e por funcao.
        - Inclusao da consulta de configuracao dos decoradores.
============================================================
"""

# ----------------------------------------------------------------------------
# IMPORTACOES
# ----------------------------------------------------------------------------

# Importa timedelta para permitir expiracoes expressas como duracao
from datetime import timedelta

# Importa wraps para preservar os metadados das funcoes decoradas
from functools import wraps

# Importa Callable e TypeVar para tipar decoradores sem perder assinaturas
from typing import Any, Callable, ParamSpec, TypeVar, overload

# Importa Streamlit para utilizar seus mecanismos oficiais de cache
import streamlit as st


# ----------------------------------------------------------------------------
# TIPOS
# ----------------------------------------------------------------------------

# Representa os parametros recebidos pela funcao decorada
P = ParamSpec("P")

# Representa o tipo retornado pela funcao decorada
R = TypeVar("R")

# Define os tipos aceitos pelo parametro de expiracao
TipoExpiracao = float | timedelta | str | None

# Define os tipos aceitos pelo texto do indicador de carregamento
TipoSpinner = bool | str


# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------

# Define o texto padrao exibido durante o processamento dos dados
TEXTO_CARREGAMENTO_DADOS = "Carregando dados..."

# Define o texto padrao exibido durante a inicializacao de recursos
TEXTO_CARREGAMENTO_RECURSO = "Inicializando recurso..."

# Define o tempo padrao sem expiracao automatica
EXPIRACAO_PADRAO = None

# Define o limite padrao sem restricao de entradas
MAXIMO_ENTRADAS_PADRAO = None

# Define se os dados devem ser persistidos por padrao
PERSISTIR_DADOS_PADRAO = False


# ----------------------------------------------------------------------------
# EXCECOES
# ----------------------------------------------------------------------------

class DashboardCacheError(Exception):
    """Erro base para operacoes de cache do dashboard Streamlit."""


class ConfiguracaoCacheInvalidaError(DashboardCacheError, ValueError):
    """Indica que uma configuracao de cache possui valor invalido."""


class FuncaoCacheInvalidaError(DashboardCacheError, TypeError):
    """Indica que o objeto informado nao e uma funcao valida."""


class CacheFuncaoIndisponivelError(DashboardCacheError, AttributeError):
    """Indica que uma funcao nao possui um cache que possa ser limpo."""


# ----------------------------------------------------------------------------
# FUNCOES INTERNAS DE VALIDACAO
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
    # Rejeita inteiros e outros tipos que nao sejam booleanos
    if not isinstance(valor, bool):
        raise TypeError(
            f"O parametro '{nome}' deve ser booleano."
        )

    # Retorna o valor validado
    return valor


def _validar_funcao(
    funcao: Callable[P, R],
    nome: str = "funcao"
) -> Callable[P, R]:
    """
    Valida se o objeto informado pode ser chamado como funcao.

    Args:
        funcao (Callable[P, R]):
            Funcao que sera validada.
        nome (str):
            Nome do parametro utilizado na mensagem de erro.

    Returns:
        Callable[P, R]:
            A propria funcao validada.

    Raises:
        FuncaoCacheInvalidaError:
            Caso o objeto nao seja chamavel.
    """
    # Verifica se o objeto pode ser executado
    if not callable(funcao):
        raise FuncaoCacheInvalidaError(
            f"O parametro '{nome}' deve ser uma funcao ou objeto chamavel."
        )

    # Retorna a funcao validada
    return funcao


def _validar_expiracao(
    expiracao: TipoExpiracao
) -> TipoExpiracao:
    """
    Valida o tempo de expiracao utilizado pelo cache.

    Args:
        expiracao (TipoExpiracao):
            Tempo em segundos, timedelta, texto de duracao ou None.

    Returns:
        TipoExpiracao:
            O proprio valor de expiracao validado.

    Raises:
        ConfiguracaoCacheInvalidaError:
            Caso o valor seja negativo, vazio ou possua tipo invalido.
    """
    # None representa um cache sem expiracao automatica
    if expiracao is None:
        return None

    # Rejeita booleanos, mesmo que bool herde de int
    if isinstance(expiracao, bool):
        raise ConfiguracaoCacheInvalidaError(
            "O parametro 'expiracao' nao pode ser booleano."
        )

    # Valida expiracao numerica em segundos
    if isinstance(expiracao, (int, float)):
        if expiracao < 0:
            raise ConfiguracaoCacheInvalidaError(
                "O parametro 'expiracao' nao pode ser negativo."
            )
        return float(expiracao)

    # Valida uma duracao do Python
    if isinstance(expiracao, timedelta):
        if expiracao.total_seconds() < 0:
            raise ConfiguracaoCacheInvalidaError(
                "O parametro 'expiracao' nao pode ser negativo."
            )
        return expiracao

    # Valida uma duracao textual aceita pelo Streamlit
    if isinstance(expiracao, str):
        texto = expiracao.strip()
        if not texto:
            raise ConfiguracaoCacheInvalidaError(
                "O parametro 'expiracao' nao pode ser um texto vazio."
            )
        return texto

    # Rejeita qualquer outro tipo
    raise ConfiguracaoCacheInvalidaError(
        "O parametro 'expiracao' deve ser numero, timedelta, string ou None."
    )


def _validar_maximo_entradas(
    maximo_entradas: int | None
) -> int | None:
    """
    Valida a quantidade maxima de entradas mantidas no cache.

    Args:
        maximo_entradas (int | None):
            Limite de entradas ou None para nao limitar.

    Returns:
        int | None:
            Limite validado.

    Raises:
        ConfiguracaoCacheInvalidaError:
            Caso o limite nao seja um inteiro positivo ou None.
    """
    # None desabilita o limite de entradas
    if maximo_entradas is None:
        return None

    # Rejeita booleanos e tipos nao inteiros
    if isinstance(maximo_entradas, bool) or not isinstance(
        maximo_entradas,
        int
    ):
        raise ConfiguracaoCacheInvalidaError(
            "O parametro 'maximo_entradas' deve ser inteiro ou None."
        )

    # Exige pelo menos uma entrada
    if maximo_entradas < 1:
        raise ConfiguracaoCacheInvalidaError(
            "O parametro 'maximo_entradas' deve ser maior ou igual a 1."
        )

    # Retorna o limite validado
    return maximo_entradas


def _validar_spinner(
    exibir_carregamento: TipoSpinner
) -> TipoSpinner:
    """
    Valida a configuracao do indicador de carregamento.

    Args:
        exibir_carregamento (TipoSpinner):
            Booleano ou texto exibido durante o processamento.

    Returns:
        TipoSpinner:
            Configuracao validada.

    Raises:
        ConfiguracaoCacheInvalidaError:
            Caso o valor nao seja booleano ou texto preenchido.
    """
    # Aceita diretamente valores booleanos
    if isinstance(exibir_carregamento, bool):
        return exibir_carregamento

    # Aceita textos nao vazios como mensagem personalizada
    if isinstance(exibir_carregamento, str):
        texto = exibir_carregamento.strip()
        if texto:
            return texto

    # Rejeita outros valores
    raise ConfiguracaoCacheInvalidaError(
        "O parametro 'exibir_carregamento' deve ser booleano ou texto."
    )


def _normalizar_persistencia(
    persistir: bool | str
) -> bool | str:
    """
    Valida a persistencia utilizada pelo cache de dados.

    Args:
        persistir (bool | str):
            False, True ou o modo textual aceito pelo Streamlit.

    Returns:
        bool | str:
            Configuracao de persistencia validada.

    Raises:
        ConfiguracaoCacheInvalidaError:
            Caso o valor possua tipo ou texto invalido.
    """
    # Aceita os valores booleanos suportados pelo Streamlit
    if isinstance(persistir, bool):
        return persistir

    # Aceita modos textuais preenchidos para compatibilidade de versoes
    if isinstance(persistir, str) and persistir.strip():
        return persistir.strip()

    # Rejeita valores nao suportados
    raise ConfiguracaoCacheInvalidaError(
        "O parametro 'persistir' deve ser booleano ou texto preenchido."
    )


def _registrar_configuracao(
    funcao: Callable[P, R],
    configuracao: dict[str, Any]
) -> Callable[P, R]:
    """
    Registra a configuracao amigavel no objeto decorado.

    Args:
        funcao (Callable[P, R]):
            Funcao decorada pelo mecanismo do Streamlit.
        configuracao (dict[str, Any]):
            Configuracao aplicada ao decorador.

    Returns:
        Callable[P, R]:
            Funcao decorada com os metadados adicionais.

    Raises:
        FuncaoCacheInvalidaError:
            Caso o objeto recebido nao seja chamavel.
    """
    # Valida a funcao antes de registrar os metadados
    _validar_funcao(funcao)

    # Registra uma copia para evitar alteracoes externas acidentais
    setattr(
        funcao,
        "__dashboard_cache_config__",
        dict(configuracao)
    )

    # Retorna a funcao atualizada
    return funcao


# ----------------------------------------------------------------------------
# DECORADORES DE CACHE
# ----------------------------------------------------------------------------

@overload
def cache_dados(
    funcao: Callable[P, R]
) -> Callable[P, R]:
    ...


@overload
def cache_dados(
    funcao: None = None,
    *,
    expiracao: TipoExpiracao = EXPIRACAO_PADRAO,
    maximo_entradas: int | None = MAXIMO_ENTRADAS_PADRAO,
    exibir_carregamento: TipoSpinner = TEXTO_CARREGAMENTO_DADOS,
    exibir_tempo: bool = False,
    persistir: bool | str = PERSISTIR_DADOS_PADRAO,
    funcoes_hash: dict[type | str, Callable[[Any], Any]] | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def cache_dados(
    funcao: Callable[P, R] | None = None,
    *,
    expiracao: TipoExpiracao = EXPIRACAO_PADRAO,
    maximo_entradas: int | None = MAXIMO_ENTRADAS_PADRAO,
    exibir_carregamento: TipoSpinner = TEXTO_CARREGAMENTO_DADOS,
    exibir_tempo: bool = False,
    persistir: bool | str = PERSISTIR_DADOS_PADRAO,
    funcoes_hash: dict[type | str, Callable[[Any], Any]] | None = None
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Aplica cache a funcoes que retornam dados serializaveis.

    Args:
        funcao (Callable[P, R] | None):
            Funcao decorada quando o decorador e usado sem parenteses.
        expiracao (TipoExpiracao):
            Tempo de vida da entrada em segundos, timedelta, texto ou None.
        maximo_entradas (int | None):
            Quantidade maxima de combinacoes armazenadas.
        exibir_carregamento (TipoSpinner):
            Booleano ou mensagem exibida durante uma nova execucao.
        exibir_tempo (bool):
            Define se o tempo de execucao sera mostrado no spinner.
        persistir (bool | str):
            Define se o cache de dados sera persistido em disco.
        funcoes_hash (dict | None):
            Funcoes personalizadas para calcular o hash dos argumentos.

    Returns:
        Callable:
            Funcao com cache ou decorador configurado.

    Raises:
        ConfiguracaoCacheInvalidaError:
            Caso uma configuracao seja invalida.
        FuncaoCacheInvalidaError:
            Caso funcao nao seja chamavel.
    """
    # Valida toda a configuracao antes de criar o decorador
    ttl = _validar_expiracao(expiracao)
    limite = _validar_maximo_entradas(maximo_entradas)
    spinner = _validar_spinner(exibir_carregamento)
    _validar_booleano(exibir_tempo, "exibir_tempo")
    persistencia = _normalizar_persistencia(persistir)

    if funcoes_hash is not None and not isinstance(funcoes_hash, dict):
        raise ConfiguracaoCacheInvalidaError(
            "O parametro 'funcoes_hash' deve ser um dicionario ou None."
        )

    # Mantem os parametros em portugues para consulta posterior
    configuracao = {
        "tipo": "dados",
        "expiracao": ttl,
        "maximo_entradas": limite,
        "exibir_carregamento": spinner,
        "exibir_tempo": exibir_tempo,
        "persistir": persistencia,
        "funcoes_hash": funcoes_hash
    }

    # Cria o decorador real do Streamlit
    decorador_streamlit = st.cache_data(
        ttl=ttl,
        max_entries=limite,
        show_spinner=spinner,
        show_time=exibir_tempo,
        persist=persistencia,
        hash_funcs=funcoes_hash
    )

    # Aplica o cache a uma funcao especifica
    def decorar(
        alvo: Callable[P, R]
    ) -> Callable[P, R]:
        """Aplica o decorador configurado a uma funcao de dados."""
        _validar_funcao(alvo)
        decorada = decorador_streamlit(alvo)
        return _registrar_configuracao(
            decorada,
            configuracao
        )

    # Permite o uso simples: @cache_dados
    if funcao is not None:
        return decorar(funcao)

    # Permite o uso configurado: @cache_dados(...)
    return decorar


@overload
def cache_recurso(
    funcao: Callable[P, R]
) -> Callable[P, R]:
    ...


@overload
def cache_recurso(
    funcao: None = None,
    *,
    expiracao: TipoExpiracao = EXPIRACAO_PADRAO,
    maximo_entradas: int | None = MAXIMO_ENTRADAS_PADRAO,
    exibir_carregamento: TipoSpinner = TEXTO_CARREGAMENTO_RECURSO,
    exibir_tempo: bool = False,
    validar: Callable[[Any], bool] | None = None,
    funcoes_hash: dict[type | str, Callable[[Any], Any]] | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def cache_recurso(
    funcao: Callable[P, R] | None = None,
    *,
    expiracao: TipoExpiracao = EXPIRACAO_PADRAO,
    maximo_entradas: int | None = MAXIMO_ENTRADAS_PADRAO,
    exibir_carregamento: TipoSpinner = TEXTO_CARREGAMENTO_RECURSO,
    exibir_tempo: bool = False,
    validar: Callable[[Any], bool] | None = None,
    funcoes_hash: dict[type | str, Callable[[Any], Any]] | None = None
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Aplica cache a funcoes que retornam recursos compartilhados.

    Args:
        funcao (Callable[P, R] | None):
            Funcao decorada quando o decorador e usado sem parenteses.
        expiracao (TipoExpiracao):
            Tempo de vida do recurso em segundos, timedelta, texto ou None.
        maximo_entradas (int | None):
            Quantidade maxima de recursos armazenados.
        exibir_carregamento (TipoSpinner):
            Booleano ou mensagem exibida durante a inicializacao.
        exibir_tempo (bool):
            Define se o tempo de execucao sera mostrado no spinner.
        validar (Callable | None):
            Funcao que confirma se o recurso armazenado continua valido.
        funcoes_hash (dict | None):
            Funcoes personalizadas para calcular o hash dos argumentos.

    Returns:
        Callable:
            Funcao com cache ou decorador configurado.

    Raises:
        ConfiguracaoCacheInvalidaError:
            Caso uma configuracao seja invalida.
        FuncaoCacheInvalidaError:
            Caso funcao ou validar nao seja chamavel.
    """
    # Valida toda a configuracao antes de criar o decorador
    ttl = _validar_expiracao(expiracao)
    limite = _validar_maximo_entradas(maximo_entradas)
    spinner = _validar_spinner(exibir_carregamento)
    _validar_booleano(exibir_tempo, "exibir_tempo")

    if validar is not None:
        _validar_funcao(validar, "validar")

    if funcoes_hash is not None and not isinstance(funcoes_hash, dict):
        raise ConfiguracaoCacheInvalidaError(
            "O parametro 'funcoes_hash' deve ser um dicionario ou None."
        )

    # Mantem os parametros em portugues para consulta posterior
    configuracao = {
        "tipo": "recurso",
        "expiracao": ttl,
        "maximo_entradas": limite,
        "exibir_carregamento": spinner,
        "exibir_tempo": exibir_tempo,
        "validar": validar,
        "funcoes_hash": funcoes_hash
    }

    # Cria o decorador real do Streamlit
    decorador_streamlit = st.cache_resource(
        ttl=ttl,
        max_entries=limite,
        show_spinner=spinner,
        show_time=exibir_tempo,
        validate=validar,
        hash_funcs=funcoes_hash
    )

    # Aplica o cache a uma funcao especifica
    def decorar(
        alvo: Callable[P, R]
    ) -> Callable[P, R]:
        """Aplica o decorador configurado a uma funcao de recurso."""
        _validar_funcao(alvo)
        decorada = decorador_streamlit(alvo)
        return _registrar_configuracao(
            decorada,
            configuracao
        )

    # Permite o uso simples: @cache_recurso
    if funcao is not None:
        return decorar(funcao)

    # Permite o uso configurado: @cache_recurso(...)
    return decorar


# ----------------------------------------------------------------------------
# FUNCOES DE LIMPEZA
# ----------------------------------------------------------------------------

def limpar_cache_dados() -> None:
    """
    Remove todas as entradas armazenadas no cache de dados.

    Args:
        Nenhum.

    Returns:
        None:
            A funcao nao possui valor de retorno.

    Raises:
        DashboardCacheError:
            Caso o Streamlit nao consiga limpar o cache de dados.
    """
    # Solicita ao Streamlit a limpeza global dos dados
    try:
        st.cache_data.clear()
    except Exception as erro:
        raise DashboardCacheError(
            "Nao foi possivel limpar o cache de dados."
        ) from erro


def limpar_cache_recursos() -> None:
    """
    Remove todas as entradas armazenadas no cache de recursos.

    Args:
        Nenhum.

    Returns:
        None:
            A funcao nao possui valor de retorno.

    Raises:
        DashboardCacheError:
            Caso o Streamlit nao consiga limpar o cache de recursos.
    """
    # Solicita ao Streamlit a limpeza global dos recursos
    try:
        st.cache_resource.clear()
    except Exception as erro:
        raise DashboardCacheError(
            "Nao foi possivel limpar o cache de recursos."
        ) from erro


def limpar_todos_caches() -> None:
    """
    Remove os caches de dados e de recursos do dashboard.

    Args:
        Nenhum.

    Returns:
        None:
            A funcao nao possui valor de retorno.

    Raises:
        DashboardCacheError:
            Caso algum dos caches nao possa ser limpo.
    """
    # Limpa primeiro os dados serializaveis
    limpar_cache_dados()

    # Limpa em seguida os recursos compartilhados
    limpar_cache_recursos()


def possui_cache_funcao(
    funcao: Callable[..., Any]
) -> bool:
    """
    Verifica se uma funcao possui uma operacao clear de cache.

    Args:
        funcao (Callable[..., Any]):
            Funcao que sera analisada.

    Returns:
        bool:
            True quando a funcao possui cache limpavel.

    Raises:
        FuncaoCacheInvalidaError:
            Caso o objeto informado nao seja chamavel.
    """
    # Valida a funcao recebida
    _validar_funcao(funcao)

    # Verifica a operacao adicionada pelos decoradores do Streamlit
    return callable(getattr(funcao, "clear", None))


def limpar_cache_funcao(
    funcao: Callable[..., Any],
    *args: Any,
    **kwargs: Any
) -> None:
    """
    Limpa todo o cache de uma funcao ou somente uma combinacao de argumentos.

    Args:
        funcao (Callable[..., Any]):
            Funcao decorada cujo cache sera limpo.
        *args (Any):
            Argumentos posicionais da entrada especifica do cache.
        **kwargs (Any):
            Argumentos nomeados da entrada especifica do cache.

    Returns:
        None:
            A funcao nao possui valor de retorno.

    Raises:
        CacheFuncaoIndisponivelError:
            Caso a funcao nao possua a operacao clear.
    """
    # Valida a funcao e localiza sua operacao de limpeza
    _validar_funcao(funcao)
    limpar = getattr(funcao, "clear", None)

    if not callable(limpar):
        raise CacheFuncaoIndisponivelError(
            "A funcao informada nao possui um cache que possa ser limpo."
        )

    # Sem argumentos, limpa todas as entradas da funcao
    if not args and not kwargs:
        limpar()
        return

    # Com argumentos, remove apenas a entrada correspondente
    limpar(*args, **kwargs)


# ----------------------------------------------------------------------------
# FUNCOES DE CONSULTA
# ----------------------------------------------------------------------------

def obter_configuracao_cache(
    funcao: Callable[..., Any]
) -> dict[str, Any] | None:
    """
    Retorna a configuracao aplicada pelos decoradores deste modulo.

    Args:
        funcao (Callable[..., Any]):
            Funcao de dados ou recurso que sera consultada.

    Returns:
        dict[str, Any] | None:
            Copia da configuracao ou None quando ela nao foi registrada.

    Raises:
        FuncaoCacheInvalidaError:
            Caso o objeto informado nao seja chamavel.
    """
    # Valida a funcao recebida
    _validar_funcao(funcao)

    # Localiza a configuracao registrada pelo modulo
    configuracao = getattr(
        funcao,
        "__dashboard_cache_config__",
        None
    )

    # Retorna None para funcoes comuns
    if configuracao is None:
        return None

    # Retorna uma copia para proteger os metadados internos
    return dict(configuracao)


# ----------------------------------------------------------------------------
# EXPORTACOES PUBLICAS
# ----------------------------------------------------------------------------

__all__ = [
    "TEXTO_CARREGAMENTO_DADOS",
    "TEXTO_CARREGAMENTO_RECURSO",
    "EXPIRACAO_PADRAO",
    "MAXIMO_ENTRADAS_PADRAO",
    "PERSISTIR_DADOS_PADRAO",
    "DashboardCacheError",
    "ConfiguracaoCacheInvalidaError",
    "FuncaoCacheInvalidaError",
    "CacheFuncaoIndisponivelError",
    "cache_dados",
    "cache_recurso",
    "limpar_cache_dados",
    "limpar_cache_recursos",
    "limpar_todos_caches",
    "limpar_cache_funcao",
    "possui_cache_funcao",
    "obter_configuracao_cache"
]
