"""
===============================================================================
Módulo: janelas.py

Descrição:
    Responsável por identificar, monitorar e interagir com janelas externas
    e popups apresentados pelo SAP GUI.

    Este módulo utiliza o pywinauto para tratar janelas que não estão
    disponíveis diretamente pelo SAP GUI Scripting, principalmente os avisos
    de segurança apresentados quando um script tenta abrir uma conexão ou
    acessar o SAP GUI.

    As principais responsabilidades deste módulo são:
        - Localizar janelas abertas do SAP Logon;
        - Obter o texto apresentado nas janelas;
        - Identificar avisos de segurança conhecidos;
        - Localizar e pressionar botões de confirmação;
        - Monitorar popups em segundo plano;
        - Encerrar o monitoramento de forma segura;
        - Informar se o monitoramento está ativo;
        - Utilizar apenas mensagens conhecidas para evitar cliques indevidos.

    Este módulo não deve realizar conexão com o SAP, autenticação, abertura
    de transações ou exportações.

Autor:
    Tiago Eneas Antunes

Data de criação:
    08/10/2026

Versão:
    1.0.0
===============================================================================
"""

# =============================================================================
# IMPORTAÇÕES
# =============================================================================

from __future__ import annotations

import time

from threading import Event, Lock, Thread
from typing import Any

from pywinauto import Desktop

from services.SAP.constantes import (
    SAP_BACKEND_AUTOMACAO,
    SAP_INTERVALO_APOS_CLIQUE,
    SAP_INTERVALO_POPUPS,
    SAP_MENSAGENS_SEGURANCA,
    SAP_NOME_THREAD_POPUPS,
    SAP_TEMPO_LIMITE_ENCERRAMENTO_THREAD,
    SAP_TEMPO_LIMITE_POPUPS,
    SAP_TIPO_CONTROLE_BOTAO,
    SAP_TIPO_CONTROLE_TEXTO,
    SAP_TITULO_BOTAO_CONFIRMAR,
    SAP_TITULO_JANELA_LOGON,
)

from services.SAP.excecoes import (
    SAPJanelaErro,
    SAPJanelaNaoEncontradaErro,
    SAPPopupSegurancaErro,
)

from threading import Event, Lock, Thread, current_thread

# =============================================================================
# CLASSE DE GERENCIAMENTO DE JANELAS
# =============================================================================


class GerenciadorJanelasSAP:
    """
    Gerencia janelas externas e popups apresentados pelo SAP GUI.

    A classe utiliza o pywinauto para localizar e tratar janelas que não
    estão disponíveis diretamente pelo SAP GUI Scripting.

    O monitoramento pode ser executado em uma thread separada, permitindo
    que avisos de segurança sejam confirmados enquanto o SAP GUI Scripting
    executa uma operação que aguarda interação do usuário.

    Attributes:
        tempo_limite_popups (int):
            Tempo máximo, em segundos, para monitoramento dos popups.

        intervalo_popups (float):
            Intervalo, em segundos, entre as buscas por novas janelas.

        intervalo_apos_clique (float):
            Intervalo, em segundos, aguardado após clicar em um botão.

        mensagens_seguranca (tuple[str, ...]):
            Mensagens utilizadas para identificar avisos de segurança.
    """

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================

    def __init__(
        self,
        tempo_limite_popups: int = SAP_TEMPO_LIMITE_POPUPS,
        intervalo_popups: float = SAP_INTERVALO_POPUPS,
        intervalo_apos_clique: float = SAP_INTERVALO_APOS_CLIQUE,
        mensagens_seguranca: tuple[str, ...] | None = None,
    ) -> None:
        """
        Inicializa o gerenciador de janelas do SAP.

        Args:
            tempo_limite_popups (int):
                Tempo máximo, em segundos, durante o qual os popups serão
                monitorados.

            intervalo_popups (float):
                Intervalo, em segundos, entre as tentativas de localização
                dos popups.

            intervalo_apos_clique (float):
                Intervalo, em segundos, aguardado após clicar em um botão
                de confirmação.

            mensagens_seguranca (tuple[str, ...] | None):
                Mensagens utilizadas para identificar os avisos de segurança.
                Quando não informado, utiliza as mensagens cadastradas no
                módulo constantes.py.

        Returns:
            None.

        Raises:
            ValueError:
                Caso algum tempo ou intervalo seja menor ou igual a zero,
                ou caso nenhuma mensagem de segurança válida seja informada.
        """

        if tempo_limite_popups <= 0:
            raise ValueError(
                "O tempo limite dos popups deve ser maior que zero."
            )

        if intervalo_popups <= 0:
            raise ValueError(
                "O intervalo de monitoramento deve ser maior que zero."
            )

        if intervalo_apos_clique < 0:
            raise ValueError(
                "O intervalo após o clique não pode ser negativo."
            )

        mensagens = (
            mensagens_seguranca
            if mensagens_seguranca is not None
            else SAP_MENSAGENS_SEGURANCA
        )

        mensagens_normalizadas = tuple(
            self._normalizar_texto(mensagem)
            for mensagem in mensagens
            if isinstance(mensagem, str) and mensagem.strip()
        )

        if not mensagens_normalizadas:
            raise ValueError(
                "É necessário informar pelo menos uma mensagem "
                "de segurança válida."
            )

        self.tempo_limite_popups = tempo_limite_popups
        self.intervalo_popups = float(intervalo_popups)
        self.intervalo_apos_clique = float(intervalo_apos_clique)
        self.mensagens_seguranca = mensagens_normalizadas

        self._evento_parada = Event()
        self._bloqueio_thread = Lock()
        self._thread_monitoramento: Thread | None = None
        self._ultimo_erro: Exception | None = None

    # =========================================================================
    # NORMALIZAÇÃO DE TEXTO
    # =========================================================================

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        """
        Normaliza um texto para facilitar comparações.

        O texto é convertido para letras minúsculas, tem espaços duplicados
        removidos e espaços no início ou final eliminados.

        Args:
            texto (str):
                Texto que será normalizado.

        Returns:
            str:
                Texto normalizado.
        """

        return " ".join(
            texto.strip().lower().split()
        )

    # =========================================================================
    # LOCALIZAÇÃO DE JANELAS
    # =========================================================================

    def listar_janelas_sap(
        self,
        titulo_janela: str = SAP_TITULO_JANELA_LOGON,
        somente_visiveis: bool = True,
    ) -> list[Any]:
        """
        Localiza as janelas do SAP que correspondem ao título informado.

        Args:
            titulo_janela (str):
                Expressão regular utilizada para localizar as janelas.
                Por padrão, utiliza o título configurado para o SAP Logon.

            somente_visiveis (bool):
                Define se apenas as janelas visíveis serão retornadas.
                O valor padrão é True.

        Returns:
            listLista contendo as janelas encontradas. Retorna uma lista
                vazia quando nenhuma janela for localizada.

        Raises:
            SAPJanelaErro:
                Caso ocorra uma falha durante a busca das janelas.
        """

        if not titulo_janela.strip():
            raise ValueError(
                "O título utilizado para localizar a janela não pode "
                "ser vazio."
            )

        try:
            desktop = Desktop(
                backend=SAP_BACKEND_AUTOMACAO
            )

            return desktop.windows(
                title_re=titulo_janela,
                visible_only=somente_visiveis,
            )

        except Exception as erro:
            raise SAPJanelaErro(
                "Não foi possível consultar as janelas do SAP."
            ) from erro

    def obter_primeira_janela_sap(
        self,
        titulo_janela: str = SAP_TITULO_JANELA_LOGON,
        somente_visiveis: bool = True,
    ) -> Any:
        """
        Obtém a primeira janela do SAP correspondente ao título informado.

        Args:
            titulo_janela (str):
                Expressão regular utilizada para localizar a janela.

            somente_visiveis (bool):
                Define se apenas janelas visíveis serão consideradas.

        Returns:
            Any:
                Primeira janela encontrada pelo pywinauto.

        Raises:
            SAPJanelaNaoEncontradaErro:
                Caso nenhuma janela correspondente seja encontrada.

            SAPJanelaErro:
                Caso ocorra uma falha durante a busca.
        """

        janelas = self.listar_janelas_sap(
            titulo_janela=titulo_janela,
            somente_visiveis=somente_visiveis,
        )

        if not janelas:
            raise SAPJanelaNaoEncontradaErro(
                "Nenhuma janela do SAP foi encontrada."
            )

        return janelas[0]

    def existe_janela_sap(
        self,
        titulo_janela: str = SAP_TITULO_JANELA_LOGON,
        somente_visiveis: bool = True,
    ) -> bool:
        """
        Verifica se existe uma janela do SAP correspondente ao título.

        Args:
            titulo_janela (str):
                Expressão regular utilizada para localizar a janela.

            somente_visiveis (bool):
                Define se apenas janelas visíveis serão consideradas.

        Returns:
            bool:
                True quando pelo menos uma janela for encontrada.
                False quando nenhuma janela for encontrada.
        """

        try:
            janelas = self.listar_janelas_sap(
                titulo_janela=titulo_janela,
                somente_visiveis=somente_visiveis,
            )

            return bool(janelas)

        except SAPJanelaErro:
            return False

    # =========================================================================
    # LEITURA DAS JANELAS
    # =========================================================================

    def obter_texto_janela(
        self,
        janela: Any,
    ) -> str:
        """
        Obtém o conteúdo textual apresentado em uma janela.

        Args:
            janela (Any):
                Objeto da janela localizado pelo pywinauto.

        Returns:
            str:
                Texto normalizado encontrado na janela. Retorna uma string
                vazia caso nenhum conteúdo textual seja encontrado.

        Raises:
            SAPJanelaErro:
                Caso ocorra uma falha ao consultar os controles da janela.
        """

        if janela is None:
            raise ValueError(
                "A janela informada não pode ser None."
            )

        try:
            controles_texto = janela.descendants(
                control_type=SAP_TIPO_CONTROLE_TEXTO
            )

            textos: list[str] = []

            for controle in controles_texto:
                try:
                    texto_controle = controle.window_text()

                    if texto_controle and texto_controle.strip():
                        textos.append(
                            texto_controle.strip()
                        )

                except Exception:
                    continue

            return self._normalizar_texto(
                " ".join(textos)
            )

        except Exception as erro:
            raise SAPJanelaErro(
                "Não foi possível obter o conteúdo textual da janela."
            ) from erro

    def obter_titulo_janela(
        self,
        janela: Any,
    ) -> str:
        """
        Obtém o título de uma janela.

        Args:
            janela (Any):
                Objeto da janela localizado pelo pywinauto.

        Returns:
            str:
                Título da janela. Retorna uma string vazia quando o título
                não puder ser obtido.
        """

        if janela is None:
            return ""

        try:
            return janela.window_text().strip()

        except Exception:
            return ""

    # =========================================================================
    # IDENTIFICAÇÃO DOS AVISOS DE SEGURANÇA
    # =========================================================================

    def eh_popup_seguranca(
        self,
        janela: Any,
    ) -> bool:
        """
        Verifica se uma janela corresponde a um aviso de segurança do SAP.

        A identificação é realizada comparando o conteúdo textual da janela
        com as mensagens conhecidas configuradas na classe.

        Args:
            janela (Any):
                Objeto da janela localizado pelo pywinauto.

        Returns:
            bool:
                True quando a janela corresponder a um aviso conhecido.
                False quando a janela não representar um aviso de segurança.
        """

        try:
            texto_janela = self.obter_texto_janela(
                janela=janela
            )

        except SAPJanelaErro:
            return False

        if not texto_janela:
            return False

        return any(
            mensagem in texto_janela
            for mensagem in self.mensagens_seguranca
        )

    def listar_popups_seguranca(self) -> list[Any]:
        """
        Localiza os avisos de segurança atualmente exibidos pelo SAP.

        Returns:
            listLista contendo apenas as janelas identificadas como avisos
                de segurança. Retorna uma lista vazia quando nenhum aviso
                for encontrado.

        Raises:
            SAPJanelaErro:
                Caso ocorra uma falha ao consultar as janelas do SAP.
        """

        janelas = self.listar_janelas_sap()

        popups_seguranca: list[Any] = []

        for janela in janelas:
            if self.eh_popup_seguranca(
                janela=janela
            ):
                popups_seguranca.append(
                    janela
                )

        return popups_seguranca

    def existe_popup_seguranca(self) -> bool:
        """
        Verifica se existe algum aviso de segurança visível.

        Returns:
            bool:
                True quando existir pelo menos um aviso de segurança.
                False quando nenhum aviso for encontrado.
        """

        try:
            return bool(
                self.listar_popups_seguranca()
            )

        except SAPJanelaErro:
            return False

    # =========================================================================
    # INTERAÇÃO COM BOTÕES
    # =========================================================================

    def localizar_botoes_confirmacao(
        self,
        janela: Any,
    ) -> list[Any]:
        """
        Localiza os botões de confirmação existentes em uma janela.

        Args:
            janela (Any):
                Objeto da janela onde os botões serão procurados.

        Returns:
            listLista contendo os botões de confirmação encontrados.
                Retorna uma lista vazia quando nenhum botão for localizado.

        Raises:
            SAPJanelaErro:
                Caso ocorra uma falha ao consultar os controles da janela.
        """

        if janela is None:
            raise ValueError(
                "A janela informada não pode ser None."
            )

        try:
            botoes = janela.descendants(
                title=SAP_TITULO_BOTAO_CONFIRMAR,
                control_type=SAP_TIPO_CONTROLE_BOTAO,
            )

            return list(botoes)

        except Exception as erro:
            raise SAPJanelaErro(
                "Não foi possível localizar os botões de confirmação "
                "na janela."
            ) from erro

    def confirmar_popup_seguranca(
        self,
        janela: Any,
    ) -> bool:
        """
        Confirma um aviso de segurança do SAP.

        O botão de confirmação somente será pressionado se a janela for
        reconhecida como um aviso de segurança conhecido.

        Args:
            janela (Any):
                Objeto da janela que será analisado e confirmado.

        Returns:
            bool:
                True quando o popup for confirmado.
                False quando a janela não for um aviso conhecido ou nenhum
                botão habilitado for localizado.

        Raises:
            SAPPopupSegurancaErro:
                Caso o popup seja reconhecido, mas ocorra uma falha ao
                pressionar o botão de confirmação.
        """

        if not self.eh_popup_seguranca(
            janela=janela
        ):
            return False

        try:
            botoes_confirmacao = self.localizar_botoes_confirmacao(
                janela=janela
            )

            for botao in botoes_confirmacao:
                try:
                    if not botao.is_visible():
                        continue

                    if not botao.is_enabled():
                        continue

                    botao.click_input()

                    if self.intervalo_apos_clique > 0:
                        time.sleep(
                            self.intervalo_apos_clique
                        )

                    return True

                except Exception:
                    continue

            return False

        except Exception as erro:
            raise SAPPopupSegurancaErro(
                "O aviso de segurança foi identificado, mas não foi "
                "possível confirmar o botão OK."
            ) from erro

    def confirmar_popups_seguranca(self) -> int:
        """
        Localiza e confirma todos os avisos de segurança visíveis.

        Returns:
            int:
                Quantidade de popups confirmados durante a execução.

        Raises:
            SAPPopupSegurancaErro:
                Caso ocorra uma falha geral durante o tratamento dos popups.
        """

        quantidade_confirmada = 0

        try:
            popups = self.listar_popups_seguranca()

            for popup in popups:
                try:
                    confirmado = self.confirmar_popup_seguranca(
                        janela=popup
                    )

                    if confirmado:
                        quantidade_confirmada += 1

                except SAPPopupSegurancaErro:
                    continue

            return quantidade_confirmada

        except SAPJanelaErro as erro:
            raise SAPPopupSegurancaErro(
                "Não foi possível consultar os avisos de segurança do SAP."
            ) from erro

    # =========================================================================
    # MONITORAMENTO DOS POPUPS
    # =========================================================================

    def monitorar_popups_seguranca(
        self,
        tempo_limite: int | None = None,
    ) -> None:
        """
        Monitora e confirma os avisos de segurança do SAP.

        O monitoramento continua até o tempo limite ser atingido ou até que
        o evento interno de parada seja acionado.

        Esse método normalmente é executado em uma thread separada.

        Args:
            tempo_limite (int | None):
                Tempo máximo, em segundos, durante o qual os popups serão
                monitorados. Quando não informado, utiliza o tempo limite
                configurado na instância.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.
        """

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_popups
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite de monitoramento deve ser maior que zero."
            )

        inicio = time.monotonic()

        while time.monotonic() - inicio < limite:
            if self._evento_parada.is_set():
                return

            try:
                self.confirmar_popups_seguranca()

            except SAPPopupSegurancaErro as erro:
                self._ultimo_erro = erro

            self._evento_parada.wait(
                timeout=self.intervalo_popups
            )

    def iniciar_monitoramento(
        self,
        tempo_limite: int | None = None,
    ) -> None:
        """
        Inicia o monitoramento dos avisos de segurança em segundo plano.

        Caso já exista uma thread ativa, uma nova thread não será criada.

        Args:
            tempo_limite (int | None):
                Tempo máximo, em segundos, durante o qual os popups serão
                monitorados. Quando não informado, utiliza o tempo limite
                configurado na instância.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.

            SAPPopupSegurancaErro:
                Caso não seja possível iniciar a thread de monitoramento.
        """

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_popups
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite de monitoramento deve ser maior que zero."
            )

        with self._bloqueio_thread:
            if self.monitoramento_ativo():
                return

            self._evento_parada.clear()
            self._ultimo_erro = None

            try:
                self._thread_monitoramento = Thread(
                    target=self.monitorar_popups_seguranca,
                    kwargs={
                        "tempo_limite": limite,
                    },
                    daemon=True,
                    name=SAP_NOME_THREAD_POPUPS,
                )

                self._thread_monitoramento.start()

            except Exception as erro:
                self._thread_monitoramento = None

                raise SAPPopupSegurancaErro(
                    "Não foi possível iniciar o monitoramento dos "
                    "avisos de segurança."
                ) from erro

    def parar_monitoramento(self) -> None:
        """
        Encerra o monitoramento dos avisos de segurança.

        O método aciona o evento de parada e aguarda por um período limitado
        o encerramento da thread.

        Returns:
            None.
        """

        with self._bloqueio_thread:
            self._evento_parada.set()

            thread = self._thread_monitoramento

            if (
                thread is not None
                and thread.is_alive()
                and thread is not current_thread()
            ):
                thread.join(
                    timeout=SAP_TEMPO_LIMITE_ENCERRAMENTO_THREAD
                )

            self._thread_monitoramento = None
            
    def monitoramento_ativo(self) -> bool:
        """
        Verifica se o monitoramento dos popups está ativo.

        Returns:
            bool:
                True quando a thread de monitoramento estiver em execução.
                False quando não existir uma thread ativa.
        """

        return (
            self._thread_monitoramento is not None
            and self._thread_monitoramento.is_alive()
        )

    def obter_ultimo_erro(self) -> Exception | None:
        """
        Obtém o último erro ocorrido durante o monitoramento.

        O erro é armazenado porque exceções geradas dentro de uma thread
        não são propagadas automaticamente para a thread principal.

        Returns:
            Exception | None:
                Última exceção capturada durante o monitoramento ou None
                quando nenhum erro tiver sido registrado.
        """

        return self._ultimo_erro

    # =========================================================================
    # GERENCIAMENTO DE CONTEXTO
    # =========================================================================

    def __enter__(self) -> GerenciadorJanelasSAP:
        """
        Inicia o monitoramento ao entrar em um bloco with.

        Returns:
            GerenciadorJanelasSAP:
                Instância atual do gerenciador de janelas.
        """

        self.iniciar_monitoramento()

        return self

    def __exit__(
        self,
        tipo_excecao: type[BaseException] | None,
        excecao: BaseException | None,
        traceback: Any | None,
    ) -> None:
        """
        Encerra o monitoramento ao sair de um bloco with.

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

        self.parar_monitoramento()