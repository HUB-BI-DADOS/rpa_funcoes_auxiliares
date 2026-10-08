"""
===============================================================================
Módulo: conexao.py

Descrição:
    Responsável por abrir o SAP Logon, estabelecer uma conexão com o ambiente
    SAP configurado e retornar uma sessão válida para utilização pelos demais
    módulos da biblioteca.

    Este módulo atua como orquestrador da conexão SAP, utilizando:
        - constantes.py para configurações fixas;
        - excecoes.py para exceções personalizadas;
        - janelas.py para tratamento dos avisos externos de segurança;
        - sessoes.py para localização, validação e reutilização de sessões.

    As principais responsabilidades deste módulo são:
        - Validar o caminho do executável do SAP Logon;
        - Verificar se o SAP Logon já está aberto;
        - Abrir o SAP Logon quando necessário;
        - Aguardar o SAP GUI Scripting ficar disponível;
        - Abrir a conexão SAP configurada;
        - Coordenar o tratamento dos avisos de segurança;
        - Reutilizar uma sessão SAP existente;
        - Aguardar e retornar uma nova sessão SAP.

    Este módulo não realiza login, abertura de transações, preenchimento
    de campos, seleções múltiplas ou exportações.

Autor:
    Tiago Eneas Antunes

Data de criação:
    08/10/2026

Versão:
    1.2.1
===============================================================================
"""

# =============================================================================
# IMPORTAÇÕES
# =============================================================================

from __future__ import annotations

import subprocess
import time

from pathlib import Path
from typing import Any

import win32com.client

from .constantes import (
    SAP_CAMINHO_EXECUTAVEL,
    SAP_CONEXAO_PRODUCAO_CLARO,
    SAP_INTERVALO_VERIFICACAO,
    SAP_OBJETO_GUI,
    SAP_TEMPO_LIMITE_ABERTURA,
    SAP_TEMPO_LIMITE_CONEXAO,
    SAP_TEMPO_LIMITE_POPUPS,
    SAP_TEMPO_LIMITE_SESSAO,
)

from .excecoes import (
    SAPConexaoAberturaErro,
    SAPConexaoErro,
    SAPExecutavelNaoEncontradoErro,
    SAPInicializacaoErro,
    SAPScriptingErro,
    SAPSessaoNaoEncontradaErro,
    SAPTempoLimiteAberturaErro,
    SAPTempoLimiteConexaoErro,
    SAPTempoLimiteSessaoErro,
)

from .janelas import GerenciadorJanelasSAP
from .sessoes import GerenciadorSessoesSAP


# =============================================================================
# CLASSE DE CONEXÃO SAP
# =============================================================================


class ConexaoSAP:
    """
    Gerencia a abertura e a conexão com o SAP GUI.

    A classe coordena a abertura do SAP Logon, o tratamento dos avisos
    externos de segurança e a recuperação de uma sessão disponibilizada
    pelo SAP GUI Scripting.

    Caso uma sessão SAP já esteja aberta e a reutilização esteja habilitada,
    a sessão existente será retornada sem a abertura de uma nova conexão.

    Attributes:
        caminho_executavel (Path):
            Caminho completo do executável do SAP Logon.

        nome_conexao (str):
            Nome da conexão conforme apresentada no SAP Logon.

        tempo_limite_abertura (int):
            Tempo máximo, em segundos, para aguardar o SAP Logon.

        tempo_limite_conexao (int):
            Tempo máximo, em segundos, para aguardar uma conexão SAP.

        tempo_limite_sessao (int):
            Tempo máximo, em segundos, para aguardar uma sessão SAP.

        intervalo_verificacao (float):
            Intervalo, em segundos, entre as verificações.

        gerenciador_janelas (GerenciadorJanelasSAP):
            Gerenciador responsável pelos avisos externos do SAP.

        gerenciador_sessoes (GerenciadorSessoesSAP):
            Gerenciador responsável pelas conexões e sessões SAP.
    """

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================

    def __init__(
        self,
        caminho_executavel: Path | str = SAP_CAMINHO_EXECUTAVEL,
        nome_conexao: str = SAP_CONEXAO_PRODUCAO_CLARO,
        tempo_limite_abertura: int = SAP_TEMPO_LIMITE_ABERTURA,
        tempo_limite_conexao: int = SAP_TEMPO_LIMITE_CONEXAO,
        tempo_limite_sessao: int = SAP_TEMPO_LIMITE_SESSAO,
        intervalo_verificacao: float = SAP_INTERVALO_VERIFICACAO,
        gerenciador_janelas: GerenciadorJanelasSAP | None = None,
        gerenciador_sessoes: GerenciadorSessoesSAP | None = None,
    ) -> None:
        """
        Inicializa o gerenciador de conexão SAP.

        Args:
            caminho_executavel (Path | str):
                Caminho completo do executável do SAP Logon.

            nome_conexao (str):
                Nome da conexão conforme apresentada no SAP Logon.

            tempo_limite_abertura (int):
                Tempo máximo, em segundos, para aguardar o SAP Logon
                ficar disponível.

            tempo_limite_conexao (int):
                Tempo máximo, em segundos, para aguardar a criação
                da conexão SAP.

            tempo_limite_sessao (int):
                Tempo máximo, em segundos, para aguardar uma sessão SAP.

            intervalo_verificacao (float):
                Intervalo, em segundos, entre as verificações.

            gerenciador_janelas (GerenciadorJanelasSAP | None):
                Instância personalizada do gerenciador de janelas.
                Quando não informada, uma nova instância será criada.

            gerenciador_sessoes (GerenciadorSessoesSAP | None):
                Instância personalizada do gerenciador de sessões.
                Quando não informada, uma nova instância será criada.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o caminho, o nome da conexão, os tempos limites
                ou o intervalo de verificação sejam inválidos.
        """

        self.caminho_executavel = Path(
            caminho_executavel
        )

        self.nome_conexao = nome_conexao.strip()

        self.tempo_limite_abertura = tempo_limite_abertura
        self.tempo_limite_conexao = tempo_limite_conexao
        self.tempo_limite_sessao = tempo_limite_sessao

        self.intervalo_verificacao = float(
            intervalo_verificacao
        )

        self._validar_configuracoes()

        if gerenciador_janelas is not None:
            self.gerenciador_janelas = gerenciador_janelas

        else:
            self.gerenciador_janelas = GerenciadorJanelasSAP(
                tempo_limite_popups=SAP_TEMPO_LIMITE_POPUPS,
            )

        if gerenciador_sessoes is not None:
            self.gerenciador_sessoes = gerenciador_sessoes

        else:
            self.gerenciador_sessoes = GerenciadorSessoesSAP(
                tempo_limite_conexao=self.tempo_limite_conexao,
                tempo_limite_sessao=self.tempo_limite_sessao,
                intervalo_verificacao=self.intervalo_verificacao,
            )

    # =========================================================================
    # VALIDAÇÕES
    # =========================================================================

    def _validar_configuracoes(self) -> None:
        """
        Valida as configurações utilizadas pela conexão SAP.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o caminho ou o nome da conexão estejam vazios, algum
                tempo limite seja menor ou igual a zero ou o intervalo
                de verificação seja inválido.
        """

        if not str(self.caminho_executavel).strip():
            raise ValueError(
                "O caminho do executável do SAP não pode ser vazio."
            )

        if not self.nome_conexao:
            raise ValueError(
                "O nome da conexão SAP não pode ser vazio."
            )

        if (
            isinstance(self.tempo_limite_abertura, bool)
            or not isinstance(self.tempo_limite_abertura, int)
            or self.tempo_limite_abertura <= 0
        ):
            raise ValueError(
                "O tempo limite de abertura deve ser um número "
                "inteiro maior que zero."
            )

        if (
            isinstance(self.tempo_limite_conexao, bool)
            or not isinstance(self.tempo_limite_conexao, int)
            or self.tempo_limite_conexao <= 0
        ):
            raise ValueError(
                "O tempo limite de conexão deve ser um número "
                "inteiro maior que zero."
            )

        if (
            isinstance(self.tempo_limite_sessao, bool)
            or not isinstance(self.tempo_limite_sessao, int)
            or self.tempo_limite_sessao <= 0
        ):
            raise ValueError(
                "O tempo limite da sessão deve ser um número "
                "inteiro maior que zero."
            )

        if self.intervalo_verificacao <= 0:
            raise ValueError(
                "O intervalo de verificação deve ser maior que zero."
            )

    def validar_executavel(self) -> None:
        """
        Valida o caminho configurado para o executável do SAP Logon.

        Returns:
            None.

        Raises:
            SAPExecutavelNaoEncontradoErro:
                Caso o caminho não exista ou não corresponda a um arquivo.
        """

        if not self.caminho_executavel.exists():
            raise SAPExecutavelNaoEncontradoErro(
                "O executável do SAP Logon não foi encontrado: "
                f"{self.caminho_executavel}"
            )

        if not self.caminho_executavel.is_file():
            raise SAPExecutavelNaoEncontradoErro(
                "O caminho configurado para o SAP Logon não corresponde "
                f"a um arquivo: {self.caminho_executavel}"
            )

    # =========================================================================
    # VERIFICAÇÃO DO SAP LOGON
    # =========================================================================

    def sap_logon_esta_aberto(self) -> bool:
        """
        Verifica se o SAP Logon está aberto e acessível.

        A verificação é realizada por meio do objeto COM SAPGUI.

        Returns:
            bool:
                True quando o SAP Logon estiver disponível.
                False quando o objeto SAPGUI não puder ser acessado.
        """

        try:
            sap_gui = win32com.client.GetObject(
                SAP_OBJETO_GUI
            )

            return sap_gui is not None

        except Exception:
            return False

    def aguardar_sap_logon(
        self,
        tempo_limite: int | None = None,
    ) -> None:
        """
        Aguarda até que o SAP Logon fique disponível.

        Args:
            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o SAP Logon.
                Quando não informado, utiliza o tempo configurado
                na instância.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o tempo limite informado seja menor ou igual a zero.

            SAPTempoLimiteAberturaErro:
                Caso o SAP Logon não fique disponível dentro do tempo
                limite definido.
        """

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_abertura
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()

        while time.monotonic() - inicio < limite:
            if self.sap_logon_esta_aberto():
                return

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPTempoLimiteAberturaErro(
            "O SAP Logon não ficou disponível dentro de "
            f"{limite} segundos."
        )

    # =========================================================================
    # ABERTURA DO SAP LOGON
    # =========================================================================

    def abrir_sap(self) -> None:
        """
        Abre o SAP Logon caso ainda não esteja aberto.

        Quando o objeto SAPGUI já estiver disponível, nenhuma nova
        instância do aplicativo será iniciada.

        Returns:
            None.

        Raises:
            SAPExecutavelNaoEncontradoErro:
                Caso o executável do SAP Logon não seja encontrado.

            SAPInicializacaoErro:
                Caso o sistema operacional não consiga iniciar o SAP Logon.

            SAPTempoLimiteAberturaErro:
                Caso o SAP Logon não fique disponível dentro do tempo
                limite configurado.
        """

        if self.sap_logon_esta_aberto():
            return

        self.validar_executavel()

        try:
            subprocess.Popen(
                [str(self.caminho_executavel)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except OSError as erro:
            raise SAPInicializacaoErro(
                "Não foi possível iniciar o SAP Logon pelo caminho: "
                f"{self.caminho_executavel}"
            ) from erro

        self.aguardar_sap_logon(
            tempo_limite=self.tempo_limite_abertura
        )

    # =========================================================================
    # ACESSO AO SAP GUI SCRIPTING
    # =========================================================================

    def obter_application(self) -> Any:
        """
        Obtém o objeto principal do SAP GUI Scripting.

        O acesso ao objeto é delegado ao GerenciadorSessoesSAP para manter
        a consulta das conexões e sessões centralizada no módulo sessoes.py.

        Returns:
            Any:
                Objeto de aplicação do SAP GUI Scripting.

        Raises:
            SAPScriptingErro:
                Caso o objeto SAPGUI ou o mecanismo de scripting não possam
                ser acessados.
        """

        return self.gerenciador_sessoes.obter_application()

    def aguardar_scripting(
        self,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Aguarda até que o SAP GUI Scripting fique disponível.

        Args:
            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o SAP GUI
                Scripting. Quando não informado, utiliza o tempo limite
                de abertura configurado na instância.

        Returns:
            Any:
                Objeto de aplicação do SAP GUI Scripting.

        Raises:
            ValueError:
                Caso o tempo limite informado seja menor ou igual a zero.

            SAPScriptingErro:
                Caso o mecanismo de scripting não fique disponível
                dentro do tempo limite.
        """

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_abertura
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()
        ultimo_erro: Exception | None = None

        while time.monotonic() - inicio < limite:
            try:
                return self.obter_application()

            except SAPScriptingErro as erro:
                ultimo_erro = erro

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPScriptingErro(
            "O SAP GUI Scripting não ficou disponível dentro de "
            f"{limite} segundos."
        ) from ultimo_erro

    # =========================================================================
    # ABERTURA DA CONEXÃO
    # =========================================================================

    def abrir_conexao(
        self,
        application: Any | None = None,
    ) -> Any:
        """
        Abre a conexão SAP configurada.

        Antes da chamada ao método OpenConnection, o monitoramento dos
        avisos de segurança é iniciado em uma thread separada.

        O monitoramento permite confirmar os avisos enquanto o método
        OpenConnection aguarda a interação do usuário.

        Args:
            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Quando não
                informado, o objeto será obtido automaticamente.

        Returns:
            Any:
                Objeto da conexão SAP retornado pelo SAP GUI Scripting.

        Raises:
            SAPScriptingErro:
                Caso o mecanismo SAP GUI Scripting não esteja disponível.

            SAPConexaoAberturaErro:
                Caso a conexão não possa ser aberta ou o SAP não retorne
                um objeto de conexão válido.
        """

        aplicacao = (
            application
            if application is not None
            else self.obter_application()
        )

        self.gerenciador_janelas.iniciar_monitoramento(
            tempo_limite=self.tempo_limite_conexao
        )

        try:
            connection = aplicacao.OpenConnection(
                self.nome_conexao,
                True,
            )

            if connection is None:
                raise SAPConexaoAberturaErro(
                    "O SAP GUI Scripting não retornou um objeto "
                    "de conexão válido."
                )

            return connection

        except SAPConexaoAberturaErro:
            raise

        except Exception as erro:
            raise SAPConexaoAberturaErro(
                "Não foi possível abrir a conexão SAP configurada. "
                f"Conexão informada: '{self.nome_conexao}'. "
                "Verifique se o nome corresponde exatamente ao nome "
                "apresentado no SAP Logon."
            ) from erro

    # =========================================================================
    # REUTILIZAÇÃO DE SESSÕES
    # =========================================================================

    def obter_sessao_existente(
        self,
        somente_disponivel: bool = False,
    ) -> Any:
        """
        Obtém a primeira sessão SAP válida já existente.

        Args:
            somente_disponivel (bool):
                Define se as sessões ocupadas devem ser ignoradas.
                O valor padrão é False.

        Returns:
            Any:
                Primeira sessão SAP válida encontrada.

        Raises:
            SAPSessaoNaoEncontradaErro:
                Caso nenhuma sessão SAP válida seja encontrada.

            SAPScriptingErro:
                Caso o SAP GUI Scripting não esteja acessível.
        """

        return self.gerenciador_sessoes.obter_primeira_sessao(
            somente_disponivel=somente_disponivel
        )

    def existe_sessao(self) -> bool:
        """
        Verifica se existe pelo menos uma sessão SAP aberta.

        Returns:
            bool:
                True quando existir uma sessão SAP disponível.
                False quando nenhuma sessão SAP for encontrada.
        """

        return self.gerenciador_sessoes.existe_sessao()

    # =========================================================================
    # MÉTODO PRINCIPAL
    # =========================================================================

    def conectar(
        self,
        reutilizar_sessao: bool = True,
        somente_sessao_disponivel: bool = False,
    ) -> Any:
        """
        Abre ou reutiliza uma conexão SAP e retorna uma sessão válida.

        O fluxo executado pelo método é:
            1. Verificar se uma sessão pode ser reutilizada;
            2. Abrir o SAP Logon, caso necessário;
            3. Aguardar o SAP GUI Scripting ficar disponível;
            4. Iniciar o monitoramento dos avisos de segurança;
            5. Abrir a conexão SAP configurada;
            6. Aguardar a criação de uma sessão;
            7. Encerrar o monitoramento dos avisos;
            8. Retornar a sessão SAP encontrada.

        Args:
            reutilizar_sessao (bool):
                Define se uma sessão SAP existente poderá ser reutilizada.
                O valor padrão é True.

            somente_sessao_disponivel (bool):
                Define se uma sessão ocupada deve ser ignorada durante
                a reutilização ou recuperação.
                O valor padrão é False.

        Returns:
            Any:
                Objeto da sessão SAP GUI Scripting.

        Raises:
            SAPExecutavelNaoEncontradoErro:
                Caso o executável do SAP Logon não seja encontrado.

            SAPInicializacaoErro:
                Caso o SAP Logon não possa ser iniciado.

            SAPScriptingErro:
                Caso o SAP GUI Scripting não esteja disponível.

            SAPConexaoAberturaErro:
                Caso a conexão SAP não possa ser aberta.

            SAPTempoLimiteSessaoErro:
                Caso nenhuma sessão SAP fique disponível dentro do
                tempo limite.

            SAPConexaoErro:
                Caso ocorra um erro inesperado durante a conexão.
        """

        if reutilizar_sessao:
            try:
                return self.obter_sessao_existente(
                    somente_disponivel=somente_sessao_disponivel
                )

            except (
                SAPSessaoNaoEncontradaErro,
                SAPScriptingErro,
            ):
                pass

        self.abrir_sap()

        application = self.aguardar_scripting(
            tempo_limite=self.tempo_limite_abertura
        )

        try:
            connection = self.abrir_conexao(
                application=application
            )

            session = self.gerenciador_sessoes.aguardar_sessao(
                connection=connection,
                tempo_limite=self.tempo_limite_sessao,
                somente_disponivel=somente_sessao_disponivel,
            )

            return session

        except (
            SAPConexaoAberturaErro,
            SAPTempoLimiteConexaoErro,
            SAPTempoLimiteSessaoErro,
            SAPScriptingErro,
        ):
            raise

        except Exception as erro:
            raise SAPConexaoErro(
                "Ocorreu um erro inesperado durante a conexão com o SAP."
            ) from erro

        finally:
            self.gerenciador_janelas.parar_monitoramento()

    # =========================================================================
    # GERENCIAMENTO DE CONTEXTO
    # =========================================================================

    def __enter__(self) -> Any:
        """
        Estabelece a conexão ao entrar em um bloco with.

        Returns:
            Any:
                Objeto da sessão SAP GUI Scripting.
        """

        return self.conectar()

    def __exit__(
        self,
        tipo_excecao: type[BaseException] | None,
        excecao: BaseException | None,
        traceback: Any | None,
    ) -> None:
        """
        Finaliza os recursos internos ao sair de um bloco with.

        O método não encerra a sessão SAP automaticamente, pois a sessão
        pode continuar sendo utilizada por outros processos. Apenas o
        monitoramento de popups é encerrado.

        Args:
            tipo_excecao (type[BaseException] | None):
                Tipo da exceção ocorrida dentro do bloco, quando aplicável.

            excecao (BaseException | None):
                Instância da exceção ocorrida, quando aplicável.

            traceback (Any | None):
                Rastreamento da exceção ocorrida, quando aplicável.

        Returns:
            None.
        """

        self.gerenciador_janelas.parar_monitoramento()


