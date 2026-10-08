"""
===============================================================================
Módulo: navegacao.py

Descrição:
    Responsável por gerenciar as ações comuns de navegação dentro de uma
    sessão SAP GUI.

    Este módulo centraliza operações técnicas reutilizáveis relacionadas à
    navegação no SAP, incluindo:
        - Abrir transações;
        - Encerrar a transação atual;
        - Abrir transações em uma nova sessão;
        - Voltar para a tela anterior;
        - Confirmar uma operação;
        - Cancelar uma operação;
        - Enviar teclas de função;
        - Aguardar a sessão ficar disponível;
        - Localizar elementos;
        - Ler mensagens da barra de status;
        - Identificar erros apresentados pelo SAP;
        - Validar se uma transação foi aberta corretamente.

    Este módulo não abre o SAP Logon, não estabelece conexões, não realiza
    login, não preenche seleções múltiplas e não exporta arquivos.

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

from typing import Any

from .constantes import (
    SAP_COMANDO_ENCERRAR_SESSAO,
    SAP_COMANDO_ENCERRAR_SISTEMA,
    SAP_COMANDO_NOVA_SESSAO,
    SAP_COMANDO_NOVA_TRANSACAO,
    SAP_ID_BARRA_STATUS,
    SAP_ID_CAMPO_TRANSACAO,
    SAP_ID_JANELA_PRINCIPAL,
    SAP_INTERVALO_VERIFICACAO,
    SAP_TECLA_ENTER,
    SAP_TECLA_F3,
    SAP_TECLA_F8,
    SAP_TECLA_F12,
    SAP_TEMPO_LIMITE_SESSAO,
    SAP_TIPO_MENSAGEM_AVISO,
    SAP_TIPO_MENSAGEM_CANCELAMENTO,
    SAP_TIPO_MENSAGEM_ERRO,
)

from .excecoes import (
    SAPElementoNaoEncontradoErro,
    SAPMensagemCancelamentoErro,
    SAPMensagemStatusErro,
    SAPNavegacaoErro,
    SAPSessaoInvalidaErro,
    SAPSessaoOcupadaErro,
    SAPTempoLimiteSessaoErro,
    SAPTransacaoAberturaErro,
    SAPTransacaoNaoEncontradaErro,
)


# =============================================================================
# CLASSE DE NAVEGAÇÃO SAP
# =============================================================================


class NavegacaoSAP:
    """
    Gerencia ações comuns de navegação em uma sessão SAP.

    A classe recebe uma sessão SAP GUI Scripting e fornece métodos
    reutilizáveis para abrir transações, voltar, confirmar, cancelar,
    enviar teclas e validar mensagens apresentadas pelo sistema.

    Attributes:
        tempo_limite_navegacao (int):
            Tempo máximo, em segundos, para aguardar uma operação.

        intervalo_verificacao (float):
            Intervalo, em segundos, entre as verificações.

        id_janela_principal (str):
            Identificador da janela principal do SAP.

        id_campo_transacao (str):
            Identificador do campo de comandos do SAP.

        id_barra_status (str):
            Identificador da barra de status do SAP.
    """

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================

    def __init__(
        self,
        tempo_limite_navegacao: int = SAP_TEMPO_LIMITE_SESSAO,
        intervalo_verificacao: float = SAP_INTERVALO_VERIFICACAO,
        id_janela_principal: str = SAP_ID_JANELA_PRINCIPAL,
        id_campo_transacao: str = SAP_ID_CAMPO_TRANSACAO,
        id_barra_status: str = SAP_ID_BARRA_STATUS,
    ) -> None:
        """
        Inicializa o gerenciador de navegação SAP.

        Args:
            tempo_limite_navegacao (int):
                Tempo máximo, em segundos, para aguardar a conclusão
                de uma operação de navegação.

            intervalo_verificacao (float):
                Intervalo, em segundos, entre as verificações.

            id_janela_principal (str):
                Identificador SAP GUI da janela principal.

            id_campo_transacao (str):
                Identificador SAP GUI do campo de comandos.

            id_barra_status (str):
                Identificador SAP GUI da barra de status.

        Returns:
            None.

        Raises:
            ValueError:
                Caso algum tempo, intervalo ou identificador informado
                seja inválido.
        """

        if (
            isinstance(tempo_limite_navegacao, bool)
            or not isinstance(tempo_limite_navegacao, int)
            or tempo_limite_navegacao <= 0
        ):
            raise ValueError(
                "O tempo limite da navegação deve ser um número "
                "inteiro maior que zero."
            )

        if (
            isinstance(intervalo_verificacao, bool)
            or not isinstance(intervalo_verificacao, (int, float))
            or intervalo_verificacao <= 0
        ):
            raise ValueError(
                "O intervalo de verificação deve ser um número "
                "maior que zero."
            )

        identificadores = {
            "id_janela_principal": id_janela_principal,
            "id_campo_transacao": id_campo_transacao,
            "id_barra_status": id_barra_status,
        }

        for nome, identificador in identificadores.items():
            if not isinstance(identificador, str):
                raise ValueError(
                    f"O identificador '{nome}' deve ser uma string."
                )

            if not identificador.strip():
                raise ValueError(
                    f"O identificador '{nome}' não pode ser vazio."
                )

        self.tempo_limite_navegacao = tempo_limite_navegacao

        self.intervalo_verificacao = float(
            intervalo_verificacao
        )

        self.id_janela_principal = (
            id_janela_principal.strip()
        )

        self.id_campo_transacao = (
            id_campo_transacao.strip()
        )

        self.id_barra_status = (
            id_barra_status.strip()
        )

    # =========================================================================
    # VALIDAÇÃO DA SESSÃO
    # =========================================================================

    @staticmethod
    def validar_sessao(
        session: Any,
    ) -> None:
        """
        Valida se uma sessão SAP foi informada e está acessível.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            None.

        Raises:
            SAPSessaoInvalidaErro:
                Caso a sessão seja None, esteja encerrada ou não possa
                ser acessada.
        """

        if session is None:
            raise SAPSessaoInvalidaErro(
                "A sessão SAP não pode ser None."
            )

        try:
            _ = session.Id

        except Exception as erro:
            raise SAPSessaoInvalidaErro(
                "A sessão SAP informada não está válida ou não "
                "está acessível."
            ) from erro

    def sessao_ocupada(
        self,
        session: Any,
    ) -> bool:
        """
        Verifica se a sessão SAP está processando uma operação.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            bool:
                True quando a sessão estiver ocupada.
                False quando a sessão estiver disponível.

        Raises:
            SAPSessaoInvalidaErro:
                Caso a sessão informada não esteja válida.
        """

        self.validar_sessao(
            session=session
        )

        try:
            return bool(
                session.Busy
            )

        except Exception as erro:
            raise SAPSessaoInvalidaErro(
                "Não foi possível consultar o estado da sessão SAP."
            ) from erro

    def aguardar_sessao_disponivel(
        self,
        session: Any,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Aguarda até que a sessão SAP fique disponível.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar a sessão.
                Quando não informado, utiliza a configuração da instância.

        Returns:
            Any:
                A mesma sessão SAP após ficar disponível.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.

            SAPSessaoInvalidaErro:
                Caso a sessão deixe de estar acessível.

            SAPSessaoOcupadaErro:
                Caso a sessão permaneça ocupada após o tempo limite.
        """

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_navegacao
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()

        while time.monotonic() - inicio < limite:
            self.validar_sessao(
                session=session
            )

            if not self.sessao_ocupada(
                session=session
            ):
                return session

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPSessaoOcupadaErro(
            "A sessão SAP permaneceu ocupada por mais de "
            f"{limite} segundos."
        )

    # =========================================================================
    # LOCALIZAÇÃO DE ELEMENTOS
    # =========================================================================

    @staticmethod
    def localizar_elemento(
        session: Any,
        id_elemento: str,
        obrigatorio: bool = True,
    ) -> Any | None:
        """
        Localiza um elemento na sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_elemento (str):
                Identificador completo do elemento SAP GUI.

            obrigatorio (bool):
                Define se a ausência do elemento deve gerar uma exceção.

        Returns:
            Any | None:
                Elemento localizado ou None quando o elemento não existir
                e obrigatorio for False.

        Raises:
            ValueError:
                Caso o identificador informado seja inválido.

            SAPElementoNaoEncontradoErro:
                Caso o elemento seja obrigatório e não seja encontrado.
        """

        if not isinstance(id_elemento, str):
            raise ValueError(
                "O ID do elemento deve ser uma string."
            )

        id_normalizado = id_elemento.strip()

        if not id_normalizado:
            raise ValueError(
                "O ID do elemento não pode ser vazio."
            )

        try:
            return session.findById(
                id_normalizado
            )

        except Exception as erro:
            if obrigatorio:
                raise SAPElementoNaoEncontradoErro(
                    "O elemento SAP não foi encontrado: "
                    f"'{id_normalizado}'."
                ) from erro

            return None

    def elemento_existe(
        self,
        session: Any,
        id_elemento: str,
    ) -> bool:
        """
        Verifica se um elemento existe na sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_elemento (str):
                Identificador completo do elemento SAP GUI.

        Returns:
            bool:
                True quando o elemento existir.
                False quando o elemento não for localizado.
        """

        try:
            elemento = self.localizar_elemento(
                session=session,
                id_elemento=id_elemento,
                obrigatorio=False,
            )

            return elemento is not None

        except Exception:
            return False

    # =========================================================================
    # BARRA DE STATUS
    # =========================================================================

    def obter_mensagem_status(
        self,
        session: Any,
    ) -> tuple[str, str]:
        """
        Obtém o texto e o tipo da mensagem na barra de status.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            tuple[str, str]:
                Tupla contendo o texto e o tipo da mensagem.
                Retorna strings vazias quando a barra não estiver disponível.
        """

        self.validar_sessao(
            session=session
        )

        barra_status = self.localizar_elemento(
            session=session,
            id_elemento=self.id_barra_status,
            obrigatorio=False,
        )

        if barra_status is None:
            return "", ""

        try:
            texto = str(
                barra_status.Text
            ).strip()

        except Exception:
            texto = ""

        try:
            tipo = str(
                barra_status.MessageType
            ).strip().upper()

        except Exception:
            tipo = ""

        return texto, tipo

    def verificar_mensagem_erro(
        self,
        session: Any,
        considerar_aviso: bool = False,
    ) -> None:
        """
        Verifica se a barra de status apresenta erro ou cancelamento.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            considerar_aviso (bool):
                Define se mensagens do tipo aviso também deverão gerar
                uma exceção. O valor padrão é False.

        Returns:
            None.

        Raises:
            SAPMensagemStatusErro:
                Caso a barra de status apresente uma mensagem de erro.

            SAPMensagemCancelamentoErro:
                Caso a barra de status apresente uma mensagem de
                cancelamento.
        """

        mensagem, tipo_mensagem = self.obter_mensagem_status(
            session=session
        )

        if tipo_mensagem == SAP_TIPO_MENSAGEM_CANCELAMENTO:
            raise SAPMensagemCancelamentoErro(
                mensagem
                or "O SAP cancelou a operação solicitada."
            )

        if tipo_mensagem == SAP_TIPO_MENSAGEM_ERRO:
            raise SAPMensagemStatusErro(
                mensagem
                or "O SAP apresentou um erro durante a navegação."
            )

        if (
            considerar_aviso
            and tipo_mensagem == SAP_TIPO_MENSAGEM_AVISO
        ):
            raise SAPMensagemStatusErro(
                mensagem
                or "O SAP apresentou um aviso durante a navegação."
            )

    # =========================================================================
    # ENVIO DE TECLAS
    # =========================================================================

    def enviar_tecla(
        self,
        session: Any,
        codigo_tecla: int,
        aguardar_antes: bool = True,
        aguardar_depois: bool = True,
        verificar_erro: bool = False,
    ) -> None:
        """
        Envia uma tecla virtual para a janela principal do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            codigo_tecla (int):
                Código numérico da tecla reconhecida pelo método sendVKey.

            aguardar_antes (bool):
                Define se a sessão deverá estar disponível antes do envio.

            aguardar_depois (bool):
                Define se o método deverá aguardar a sessão após o envio.

            verificar_erro (bool):
                Define se a barra de status deverá ser verificada após
                a operação.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o código da tecla seja inválido.

            SAPNavegacaoErro:
                Caso a tecla não possa ser enviada.

            SAPSessaoOcupadaErro:
                Caso a sessão não fique disponível.
        """

        if (
            isinstance(codigo_tecla, bool)
            or not isinstance(codigo_tecla, int)
            or codigo_tecla < 0
        ):
            raise ValueError(
                "O código da tecla deve ser um número inteiro "
                "maior ou igual a zero."
            )

        self.validar_sessao(
            session=session
        )

        if aguardar_antes:
            self.aguardar_sessao_disponivel(
                session=session
            )

        try:
            janela_principal = self.localizar_elemento(
                session=session,
                id_elemento=self.id_janela_principal,
                obrigatorio=True,
            )

            janela_principal.sendVKey(
                codigo_tecla
            )

        except SAPElementoNaoEncontradoErro:
            raise

        except Exception as erro:
            raise SAPNavegacaoErro(
                "Não foi possível enviar a tecla para a janela "
                f"principal do SAP. Código: {codigo_tecla}."
            ) from erro

        if aguardar_depois:
            self.aguardar_sessao_disponivel(
                session=session
            )

        if verificar_erro:
            self.verificar_mensagem_erro(
                session=session
            )

    # =========================================================================
    # AÇÕES COMUNS
    # =========================================================================

    def confirmar(
        self,
        session: Any,
        verificar_erro: bool = False,
    ) -> None:
        """
        Confirma a operação atual enviando a tecla Enter.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            verificar_erro (bool):
                Define se a barra de status deverá ser validada após
                a confirmação.

        Returns:
            None.
        """

        self.enviar_tecla(
            session=session,
            codigo_tecla=SAP_TECLA_ENTER,
            aguardar_antes=True,
            aguardar_depois=True,
            verificar_erro=verificar_erro,
        )

    def executar(
        self,
        session: Any,
        verificar_erro: bool = True,
    ) -> None:
        """
        Executa a operação atual utilizando a tecla F8.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            verificar_erro (bool):
                Define se a barra de status deverá ser validada após
                a execução.

        Returns:
            None.
        """

        self.enviar_tecla(
            session=session,
            codigo_tecla=SAP_TECLA_F8,
            aguardar_antes=True,
            aguardar_depois=True,
            verificar_erro=verificar_erro,
        )

    def voltar(
        self,
        session: Any,
        quantidade: int = 1,
        verificar_erro: bool = False,
    ) -> None:
        """
        Volta uma ou mais telas utilizando a tecla F3.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            quantidade (int):
                Quantidade de telas que deverão ser retornadas.
                O valor padrão é 1.

            verificar_erro (bool):
                Define se a barra de status deverá ser validada após
                cada retorno.

        Returns:
            None.

        Raises:
            ValueError:
                Caso a quantidade informada seja menor ou igual a zero.
        """

        if (
            isinstance(quantidade, bool)
            or not isinstance(quantidade, int)
            or quantidade <= 0
        ):
            raise ValueError(
                "A quantidade de retornos deve ser um número "
                "inteiro maior que zero."
            )

        for _ in range(quantidade):
            self.enviar_tecla(
                session=session,
                codigo_tecla=SAP_TECLA_F3,
                aguardar_antes=True,
                aguardar_depois=True,
                verificar_erro=verificar_erro,
            )

    def cancelar(
        self,
        session: Any,
        verificar_erro: bool = False,
    ) -> None:
        """
        Cancela a operação atual utilizando a tecla F12.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            verificar_erro (bool):
                Define se a barra de status deverá ser validada após
                o cancelamento.

        Returns:
            None.
        """

        self.enviar_tecla(
            session=session,
            codigo_tecla=SAP_TECLA_F12,
            aguardar_antes=True,
            aguardar_depois=True,
            verificar_erro=verificar_erro,
        )

    # =========================================================================
    # CAMPO DE COMANDOS
    # =========================================================================

    def obter_campo_transacao(
        self,
        session: Any,
    ) -> Any:
        """
        Obtém o campo de comandos da sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            Any:
                Objeto correspondente ao campo de comandos do SAP.

        Raises:
            SAPElementoNaoEncontradoErro:
                Caso o campo de comandos não esteja disponível.
        """

        self.validar_sessao(
            session=session
        )

        return self.localizar_elemento(
            session=session,
            id_elemento=self.id_campo_transacao,
            obrigatorio=True,
        )

    def enviar_comando(
        self,
        session: Any,
        comando: str,
        verificar_erro: bool = True,
        aguardar_conclusao: bool = True,
    ) -> None:
        """
        Envia um comando por meio do campo de transações do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            comando (str):
                Comando que será inserido no campo de transações.

            verificar_erro (bool):
                Define se a barra de status deverá ser validada após
                o envio do comando.

            aguardar_conclusao (bool):
                Define se o método deverá aguardar a sessão ficar livre
                após o envio.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o comando informado esteja vazio.

            SAPNavegacaoErro:
                Caso o campo não possa ser preenchido ou o comando
                não possa ser enviado.
        """

        if not isinstance(comando, str):
            raise ValueError(
                "O comando SAP deve ser uma string."
            )

        comando_normalizado = comando.strip()

        if not comando_normalizado:
            raise ValueError(
                "O comando SAP não pode ser vazio."
            )

        self.aguardar_sessao_disponivel(
            session=session
        )

        try:
            campo_transacao = self.obter_campo_transacao(
                session=session
            )

            campo_transacao.text = comando_normalizado

            janela_principal = self.localizar_elemento(
                session=session,
                id_elemento=self.id_janela_principal,
                obrigatorio=True,
            )

            janela_principal.sendVKey(
                SAP_TECLA_ENTER
            )

        except SAPElementoNaoEncontradoErro:
            raise

        except Exception as erro:
            raise SAPNavegacaoErro(
                "Não foi possível enviar o comando SAP: "
                f"'{comando_normalizado}'."
            ) from erro

        if aguardar_conclusao:
            self.aguardar_sessao_disponivel(
                session=session
            )

        if verificar_erro:
            self.verificar_mensagem_erro(
                session=session
            )

    # =========================================================================
    # TRANSAÇÕES
    # =========================================================================

    @staticmethod
    def normalizar_codigo_transacao(
        codigo_transacao: str,
    ) -> str:
        """
        Valida e normaliza o código de uma transação SAP.

        Args:
            codigo_transacao (str):
                Código da transação SAP.

        Returns:
            str:
                Código da transação normalizado em letras maiúsculas.

        Raises:
            ValueError:
                Caso o código informado seja inválido ou esteja vazio.
        """

        if not isinstance(codigo_transacao, str):
            raise ValueError(
                "O código da transação deve ser uma string."
            )

        transacao = codigo_transacao.strip().upper()

        if not transacao:
            raise ValueError(
                "O código da transação não pode ser vazio."
            )

        if transacao.startswith("/"):
            partes = transacao.split(
                maxsplit=1
            )

            transacao = partes[0]

        return transacao

    def abrir_transacao(
        self,
        session: Any,
        codigo_transacao: str,
        encerrar_transacao_atual: bool = True,
        verificar_abertura: bool = True,
    ) -> None:
        """
        Abre uma transação na sessão SAP atual.

        Quando encerrar_transacao_atual estiver habilitado, o comando
        será iniciado com "/n", encerrando a transação atual antes
        de abrir a nova transação.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            codigo_transacao (str):
                Código da transação que será aberta, como "ME2N",
                "MB52" ou uma transação iniciada por "Z".

            encerrar_transacao_atual (bool):
                Define se a transação atual será encerrada antes da
                abertura da nova transação.

            verificar_abertura (bool):
                Define se o método deverá validar a transação aberta por
                meio das informações da sessão.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o código da transação seja inválido.

            SAPTransacaoNaoEncontradaErro:
                Caso o SAP indique que a transação não existe ou não esteja
                disponível.

            SAPTransacaoAberturaErro:
                Caso não seja possível abrir ou validar a transação.
        """

        transacao = self.normalizar_codigo_transacao(
            codigo_transacao=codigo_transacao
        )

        if transacao.startswith("/"):
            comando = transacao

        elif encerrar_transacao_atual:
            comando = (
                f"{SAP_COMANDO_NOVA_TRANSACAO}"
                f"{transacao}"
            )

        else:
            comando = transacao

        try:
            self.enviar_comando(
                session=session,
                comando=comando,
                verificar_erro=False,
                aguardar_conclusao=True,
            )

            mensagem, tipo_mensagem = self.obter_mensagem_status(
                session=session
            )

            if tipo_mensagem in {
                SAP_TIPO_MENSAGEM_ERRO,
                SAP_TIPO_MENSAGEM_CANCELAMENTO,
            }:
                raise SAPTransacaoNaoEncontradaErro(
                    mensagem
                    or (
                        "A transação não foi encontrada ou não está "
                        f"disponível: '{transacao}'."
                    )
                )

            if verificar_abertura:
                self.aguardar_transacao(
                    session=session,
                    codigo_transacao=transacao,
                )

        except (
            SAPTransacaoNaoEncontradaErro,
            SAPTempoLimiteSessaoErro,
        ):
            raise

        except Exception as erro:
            raise SAPTransacaoAberturaErro(
                "Não foi possível abrir a transação SAP: "
                f"'{transacao}'."
            ) from erro

    def abrir_transacao_nova_sessao(
        self,
        session: Any,
        codigo_transacao: str,
    ) -> None:
        """
        Solicita a abertura de uma transação em uma nova sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting atual.

            codigo_transacao (str):
                Código da transação que será aberta na nova sessão.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o código da transação seja inválido.

            SAPTransacaoAberturaErro:
                Caso o comando não possa ser enviado.
        """

        transacao = self.normalizar_codigo_transacao(
            codigo_transacao=codigo_transacao
        )

        comando = (
            f"{SAP_COMANDO_NOVA_SESSAO}"
            f"{transacao}"
        )

        try:
            self.enviar_comando(
                session=session,
                comando=comando,
                verificar_erro=True,
                aguardar_conclusao=False,
            )

        except Exception as erro:
            raise SAPTransacaoAberturaErro(
                "Não foi possível solicitar a abertura da transação "
                f"'{transacao}' em uma nova sessão."
            ) from erro

    def obter_transacao_atual(
        self,
        session: Any,
    ) -> str:
        """
        Obtém o código da transação atualmente aberta.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            str:
                Código da transação atual.
                Retorna uma string vazia quando a informação não estiver
                disponível.

        Raises:
            SAPSessaoInvalidaErro:
                Caso a sessão informada não esteja válida.
        """

        self.validar_sessao(
            session=session
        )

        try:
            transacao = session.Info.Transaction

            return str(
                transacao
            ).strip().upper()

        except Exception:
            return ""

    def transacao_esta_aberta(
        self,
        session: Any,
        codigo_transacao: str,
    ) -> bool:
        """
        Verifica se uma determinada transação está aberta.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            codigo_transacao (str):
                Código da transação que será comparado.

        Returns:
            bool:
                True quando a transação estiver aberta.
                False quando uma transação diferente estiver ativa.
        """

        transacao_esperada = self.normalizar_codigo_transacao(
            codigo_transacao=codigo_transacao
        )

        transacao_atual = self.obter_transacao_atual(
            session=session
        )

        return (
            transacao_atual == transacao_esperada
        )

    def aguardar_transacao(
        self,
        session: Any,
        codigo_transacao: str,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Aguarda até que uma transação fique aberta na sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            codigo_transacao (str):
                Código da transação esperada.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar a transação.
                Quando não informado, utiliza a configuração da instância.

        Returns:
            Any:
                A mesma sessão SAP após a transação ser identificada.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.

            SAPTransacaoNaoEncontradaErro:
                Caso o SAP apresente erro ao abrir a transação.

            SAPTempoLimiteSessaoErro:
                Caso a transação não fique disponível dentro do tempo
                limite.
        """

        transacao = self.normalizar_codigo_transacao(
            codigo_transacao=codigo_transacao
        )

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_navegacao
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()
        ultima_transacao = ""

        while time.monotonic() - inicio < limite:
            self.validar_sessao(
                session=session
            )

            if self.sessao_ocupada(
                session=session
            ):
                time.sleep(
                    self.intervalo_verificacao
                )

                continue

            mensagem, tipo_mensagem = self.obter_mensagem_status(
                session=session
            )

            if tipo_mensagem in {
                SAP_TIPO_MENSAGEM_ERRO,
                SAP_TIPO_MENSAGEM_CANCELAMENTO,
            }:
                raise SAPTransacaoNaoEncontradaErro(
                    mensagem
                    or (
                        "O SAP não conseguiu abrir a transação "
                        f"'{transacao}'."
                    )
                )

            ultima_transacao = self.obter_transacao_atual(
                session=session
            )

            if ultima_transacao == transacao:
                return session

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPTempoLimiteSessaoErro(
            "A transação SAP não ficou disponível dentro de "
            f"{limite} segundos. "
            f"Transação esperada: '{transacao}'. "
            f"Transação identificada: "
            f"'{ultima_transacao or 'não identificada'}'."
        )

    def encerrar_transacao_atual(
        self,
        session: Any,
    ) -> None:
        """
        Encerra a transação atual e retorna ao menu inicial do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            None.

        Raises:
            SAPNavegacaoErro:
                Caso o comando não possa ser executado.
        """

        self.enviar_comando(
            session=session,
            comando=SAP_COMANDO_NOVA_TRANSACAO,
            verificar_erro=True,
            aguardar_conclusao=True,
        )

    # =========================================================================
    # ENCERRAMENTO
    # =========================================================================

    def encerrar_sessao(
        self,
        session: Any,
    ) -> None:
        """
        Encerra somente a sessão SAP atual.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            None.

        Raises:
            SAPNavegacaoErro:
                Caso o comando de encerramento não possa ser enviado.
        """

        try:
            self.enviar_comando(
                session=session,
                comando=SAP_COMANDO_ENCERRAR_SESSAO,
                verificar_erro=False,
                aguardar_conclusao=False,
            )

        except Exception as erro:
            raise SAPNavegacaoErro(
                "Não foi possível encerrar a sessão SAP atual."
            ) from erro

    def encerrar_sap(
        self,
        session: Any,
    ) -> None:
        """
        Encerra todas as sessões e fecha a conexão SAP atual.

        O comando utilizado pode fechar o SAP sem apresentar uma nova
        confirmação. Utilize este método somente quando o encerramento
        completo for realmente necessário.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            None.

        Raises:
            SAPNavegacaoErro:
                Caso o comando de encerramento não possa ser enviado.
        """

        try:
            self.enviar_comando(
                session=session,
                comando=SAP_COMANDO_ENCERRAR_SISTEMA,
                verificar_erro=False,
                aguardar_conclusao=False,
            )

        except Exception as erro:
            raise SAPNavegacaoErro(
                "Não foi possível encerrar a conexão SAP."
            ) from erro