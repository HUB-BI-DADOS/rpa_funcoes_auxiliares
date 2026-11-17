"""
===============================================================================
Módulo: login.py

Descrição:
    Responsável por realizar e validar a autenticação no SAP GUI.

    Este módulo centraliza as operações técnicas relacionadas ao login:
        - Validar as credenciais recebidas;
        - Identificar se a sessão está na tela de login;
        - Preencher mandante, usuário, senha e idioma;
        - Enviar as credenciais para autenticação;
        - Aguardar o processamento do login;
        - Identificar mensagens de erro na barra de status;
        - Tratar a janela de múltiplos logins;
        - Verificar se a sessão está autenticada;
        - Retornar a sessão pronta para utilização pelos demais módulos.

    Este módulo não abre o SAP Logon e não cria conexões. Para essas
    operações, utilize o módulo conexao.py.

    As credenciais devem ser fornecidas pelo código do RPA, preferencialmente
    por meio de variáveis de ambiente, cofre de credenciais ou outro recurso
    seguro. A senha não deve ser escrita diretamente no código-fonte.

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
    SAP_ID_BARRA_STATUS,
    SAP_ID_CAMPO_IDIOMA,
    SAP_ID_CAMPO_MANDANTE,
    SAP_ID_CAMPO_SENHA,
    SAP_ID_CAMPO_USUARIO,
    SAP_ID_JANELA_PRINCIPAL,
    SAP_IDIOMA_PADRAO,
    SAP_INTERVALO_VERIFICACAO,
    SAP_TECLA_ENTER,
    SAP_TEMPO_LIMITE_SESSAO,
    SAP_TIPO_MENSAGEM_AVISO,
    SAP_TIPO_MENSAGEM_CANCELAMENTO,
    SAP_TIPO_MENSAGEM_ERRO,
)

from .excecoes import (
    SAPAutenticacaoErro,
    SAPCredencialErro,
    SAPLoginErro,
    SAPMultiplosLoginsErro,
    SAPSessaoInvalidaErro,
    SAPTelaLoginNaoEncontradaErro,
    SAPTempoLimiteSessaoErro,
)


# =============================================================================
# CLASSE DE LOGIN SAP
# =============================================================================


class LoginSAP:
    """
    Gerencia o processo de autenticação em uma sessão SAP.

    A classe recebe uma sessão criada pelo módulo conexao.py, identifica
    a tela de login, preenche as credenciais, envia os dados e aguarda
    a conclusão da autenticação.

    Attributes:
        tempo_limite_login (int):
            Tempo máximo, em segundos, para aguardar a autenticação.

        intervalo_verificacao (float):
            Intervalo, em segundos, entre as verificações do login.

        id_campo_mandante (str):
            Identificador SAP GUI do campo de mandante.

        id_campo_usuario (str):
            Identificador SAP GUI do campo de usuário.

        id_campo_senha (str):
            Identificador SAP GUI do campo de senha.

        id_campo_idioma (str):
            Identificador SAP GUI do campo de idioma.

        id_janela_principal (str):
            Identificador SAP GUI da janela principal.

        id_barra_status (str):
            Identificador SAP GUI da barra de status.
    """

    # =========================================================================
    # IDENTIFICADORES DA JANELA DE MÚLTIPLOS LOGINS
    # =========================================================================

    ID_JANELA_MULTIPLOS_LOGINS = "wnd[1]"

    ID_OPCAO_CONTINUAR_LOGIN = (
        "wnd[1]/usr/radMULTI_LOGON_OPT2"
    )

    ID_OPCAO_ENCERRAR_OUTROS_LOGINS = (
        "wnd[1]/usr/radMULTI_LOGON_OPT1"
    )

    ID_BOTAO_CONFIRMAR_MULTIPLOS_LOGINS = (
        "wnd[1]/tbar[0]/btn[0]"
    )

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================

    def __init__(
        self,
        tempo_limite_login: int = SAP_TEMPO_LIMITE_SESSAO,
        intervalo_verificacao: float = SAP_INTERVALO_VERIFICACAO,
        id_campo_mandante: str = SAP_ID_CAMPO_MANDANTE,
        id_campo_usuario: str = SAP_ID_CAMPO_USUARIO,
        id_campo_senha: str = SAP_ID_CAMPO_SENHA,
        id_campo_idioma: str = SAP_ID_CAMPO_IDIOMA,
        id_janela_principal: str = SAP_ID_JANELA_PRINCIPAL,
        id_barra_status: str = SAP_ID_BARRA_STATUS,
    ) -> None:
        """
        Inicializa o gerenciador de login SAP.

        Args:
            tempo_limite_login (int):
                Tempo máximo, em segundos, para aguardar a conclusão
                da autenticação.

            intervalo_verificacao (float):
                Intervalo, em segundos, entre as verificações realizadas
                durante o login.

            id_campo_mandante (str):
                Identificador SAP GUI do campo de mandante.

            id_campo_usuario (str):
                Identificador SAP GUI do campo de usuário.

            id_campo_senha (str):
                Identificador SAP GUI do campo de senha.

            id_campo_idioma (str):
                Identificador SAP GUI do campo de idioma.

            id_janela_principal (str):
                Identificador SAP GUI da janela principal.

            id_barra_status (str):
                Identificador SAP GUI da barra de status.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o tempo limite, o intervalo ou algum identificador
                obrigatório seja inválido.
        """

        if (
            isinstance(tempo_limite_login, bool)
            or not isinstance(tempo_limite_login, int)
            or tempo_limite_login <= 0
        ):
            raise ValueError(
                "O tempo limite do login deve ser um número inteiro "
                "maior que zero."
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
            "id_campo_mandante": id_campo_mandante,
            "id_campo_usuario": id_campo_usuario,
            "id_campo_senha": id_campo_senha,
            "id_campo_idioma": id_campo_idioma,
            "id_janela_principal": id_janela_principal,
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

        self.tempo_limite_login = tempo_limite_login

        self.intervalo_verificacao = float(
            intervalo_verificacao
        )

        self.id_campo_mandante = id_campo_mandante.strip()
        self.id_campo_usuario = id_campo_usuario.strip()
        self.id_campo_senha = id_campo_senha.strip()
        self.id_campo_idioma = id_campo_idioma.strip()
        self.id_janela_principal = id_janela_principal.strip()
        self.id_barra_status = id_barra_status.strip()

    # =========================================================================
    # VALIDAÇÕES
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

    @staticmethod
    def validar_credenciais(
        usuario: str,
        senha: str,
        idioma: str = SAP_IDIOMA_PADRAO,
        mandante: str | None = None,
    ) -> tuple[str, str, str, str | None]:
        """
        Valida e normaliza as credenciais de acesso ao SAP.

        Args:
            usuario (str):
                Usuário utilizado para autenticação no SAP.

            senha (str):
                Senha utilizada para autenticação no SAP.

            idioma (str):
                Idioma utilizado na sessão SAP.
                O valor padrão é definido no constantes.py.

            mandante (str | None):
                Código do mandante SAP. Quando não informado, o valor
                já apresentado na tela de login será mantido.

        Returns:
            tuple[str, str, str, str | None]:
                Tupla contendo usuário, senha, idioma e mandante
                normalizados.

        Raises:
            SAPCredencialErro:
                Caso o usuário, a senha, o idioma ou o mandante sejam
                inválidos.
        """

        if not isinstance(usuario, str):
            raise SAPCredencialErro(
                "O usuário SAP deve ser uma string."
            )

        if not isinstance(senha, str):
            raise SAPCredencialErro(
                "A senha SAP deve ser uma string."
            )

        if not isinstance(idioma, str):
            raise SAPCredencialErro(
                "O idioma SAP deve ser uma string."
            )

        usuario_normalizado = usuario.strip()
        idioma_normalizado = idioma.strip().upper()

        if not usuario_normalizado:
            raise SAPCredencialErro(
                "O usuário SAP não pode ser vazio."
            )

        if not senha:
            raise SAPCredencialErro(
                "A senha SAP não pode ser vazia."
            )

        if not idioma_normalizado:
            raise SAPCredencialErro(
                "O idioma SAP não pode ser vazio."
            )

        if mandante is not None:
            if not isinstance(mandante, str):
                raise SAPCredencialErro(
                    "O mandante SAP deve ser uma string."
                )

            mandante_normalizado = mandante.strip()

            if not mandante_normalizado:
                mandante_normalizado = None

            elif not mandante_normalizado.isdigit():
                raise SAPCredencialErro(
                    "O mandante SAP deve conter apenas números."
                )

        else:
            mandante_normalizado = None

        return (
            usuario_normalizado,
            senha,
            idioma_normalizado,
            mandante_normalizado,
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
                Elemento localizado ou None quando o elemento não for
                encontrado e obrigatorio for False.

        Raises:
            ValueError:
                Caso o identificador esteja vazio.

            SAPLoginErro:
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
                raise SAPLoginErro(
                    "Não foi possível localizar o elemento da tela "
                    f"de login: '{id_normalizado}'."
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
    # IDENTIFICAÇÃO DA TELA DE LOGIN
    # =========================================================================

    def esta_na_tela_login(
        self,
        session: Any,
    ) -> bool:
        """
        Verifica se a sessão está exibindo a tela de login do SAP.

        A identificação é realizada verificando a existência dos campos
        de usuário e senha.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            bool:
                True quando os campos de usuário e senha estiverem
                disponíveis.
                False quando a sessão não estiver na tela de login.
        """

        try:
            self.validar_sessao(
                session=session
            )

        except SAPSessaoInvalidaErro:
            return False

        campo_usuario_existe = self.elemento_existe(
            session=session,
            id_elemento=self.id_campo_usuario,
        )

        campo_senha_existe = self.elemento_existe(
            session=session,
            id_elemento=self.id_campo_senha,
        )

        return (
            campo_usuario_existe
            and campo_senha_existe
        )

    def aguardar_tela_login(
        self,
        session: Any,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Aguarda até que a tela de login fique disponível.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar a tela.
                Quando não informado, utiliza o tempo configurado
                na instância.

        Returns:
            Any:
                A mesma sessão SAP após a tela de login ficar disponível.

        Raises:
            ValueError:
                Caso o tempo limite informado seja menor ou igual a zero.

            SAPTelaLoginNaoEncontradaErro:
                Caso a tela de login não fique disponível dentro do
                tempo limite.
        """

        self.validar_sessao(
            session=session
        )

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_login
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()

        while time.monotonic() - inicio < limite:
            if self.esta_na_tela_login(
                session=session
            ):
                return session

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPTelaLoginNaoEncontradaErro(
            "A tela de login do SAP não ficou disponível dentro "
            f"de {limite} segundos."
        )

    # =========================================================================
    # PREENCHIMENTO DOS CAMPOS
    # =========================================================================

    def preencher_campo(
        self,
        session: Any,
        id_campo: str,
        valor: str,
        obrigatorio: bool = True,
    ) -> bool:
        """
        Preenche um campo da tela de login.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_campo (str):
                Identificador completo do campo SAP GUI.

            valor (str):
                Valor que será inserido no campo.

            obrigatorio (bool):
                Define se a ausência do campo deve gerar uma exceção.

        Returns:
            bool:
                True quando o campo for preenchido.
                False quando o campo não existir e obrigatorio for False.

        Raises:
            SAPLoginErro:
                Caso o campo seja obrigatório e não possa ser localizado
                ou preenchido.
        """

        campo = self.localizar_elemento(
            session=session,
            id_elemento=id_campo,
            obrigatorio=obrigatorio,
        )

        if campo is None:
            return False

        try:
            campo.text = valor
            return True

        except Exception as erro:
            raise SAPLoginErro(
                "Não foi possível preencher o campo da tela "
                f"de login: '{id_campo}'."
            ) from erro

    def preencher_credenciais(
        self,
        session: Any,
        usuario: str,
        senha: str,
        idioma: str = SAP_IDIOMA_PADRAO,
        mandante: str | None = None,
    ) -> None:
        """
        Preenche os campos de autenticação na tela de login.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            usuario (str):
                Usuário utilizado para autenticação no SAP.

            senha (str):
                Senha utilizada para autenticação no SAP.

            idioma (str):
                Idioma utilizado na sessão SAP.

            mandante (str | None):
                Código do mandante SAP. Quando não informado, o valor
                atual da tela será mantido.

        Returns:
            None.

        Raises:
            SAPCredencialErro:
                Caso alguma credencial informada seja inválida.

            SAPTelaLoginNaoEncontradaErro:
                Caso a sessão não esteja na tela de login.

            SAPLoginErro:
                Caso algum campo obrigatório não possa ser preenchido.
        """

        self.validar_sessao(
            session=session
        )

        (
            usuario_validado,
            senha_validada,
            idioma_validado,
            mandante_validado,
        ) = self.validar_credenciais(
            usuario=usuario,
            senha=senha,
            idioma=idioma,
            mandante=mandante,
        )

        if not self.esta_na_tela_login(
            session=session
        ):
            raise SAPTelaLoginNaoEncontradaErro(
                "A sessão SAP não está exibindo a tela de login."
            )

        if mandante_validado is not None:
            self.preencher_campo(
                session=session,
                id_campo=self.id_campo_mandante,
                valor=mandante_validado,
                obrigatorio=False,
            )

        self.preencher_campo(
            session=session,
            id_campo=self.id_campo_usuario,
            valor=usuario_validado,
            obrigatorio=True,
        )

        self.preencher_campo(
            session=session,
            id_campo=self.id_campo_senha,
            valor=senha_validada,
            obrigatorio=True,
        )

        self.preencher_campo(
            session=session,
            id_campo=self.id_campo_idioma,
            valor=idioma_validado,
            obrigatorio=False,
        )

    # =========================================================================
    # ENVIO DAS CREDENCIAIS
    # =========================================================================

    def enviar_credenciais(
        self,
        session: Any,
    ) -> None:
        """
        Envia as credenciais preenchidas para autenticação.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            None.

        Raises:
            SAPLoginErro:
                Caso a janela principal não seja localizada ou o comando
                de confirmação não possa ser enviado.
        """

        self.validar_sessao(
            session=session
        )

        try:
            janela_principal = self.localizar_elemento(
                session=session,
                id_elemento=self.id_janela_principal,
                obrigatorio=True,
            )

            janela_principal.sendVKey(
                SAP_TECLA_ENTER
            )

        except SAPLoginErro:
            raise

        except Exception as erro:
            raise SAPLoginErro(
                "Não foi possível enviar as credenciais para "
                "autenticação no SAP."
            ) from erro

    # =========================================================================
    # BARRA DE STATUS
    # =========================================================================

    def obter_mensagem_status(
        self,
        session: Any,
    ) -> tuple[str, str]:
        """
        Obtém o texto e o tipo da mensagem apresentada na barra de status.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            tuple[str, str]:
                Tupla contendo o texto e o tipo da mensagem.
                Retorna strings vazias quando a barra não estiver disponível.
        """

        try:
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

        except Exception:
            return "", ""

    def verificar_erro_autenticacao(
        self,
        session: Any,
    ) -> None:
        """
        Verifica se a barra de status apresenta um erro de autenticação.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            None.

        Raises:
            SAPAutenticacaoErro:
                Caso a barra de status apresente uma mensagem de erro,
                cancelamento ou aviso enquanto a tela de login permanece
                visível.
        """

        mensagem, tipo_mensagem = self.obter_mensagem_status(
            session=session
        )

        tipos_erro = {
            SAP_TIPO_MENSAGEM_ERRO,
            SAP_TIPO_MENSAGEM_CANCELAMENTO,
        }

        if tipo_mensagem in tipos_erro:
            raise SAPAutenticacaoErro(
                mensagem
                or "O SAP retornou um erro durante a autenticação."
            )

        if (
            tipo_mensagem == SAP_TIPO_MENSAGEM_AVISO
            and self.esta_na_tela_login(session=session)
            and mensagem
        ):
            raise SAPAutenticacaoErro(
                mensagem
            )

    # =========================================================================
    # MÚLTIPLOS LOGINS
    # =========================================================================

    def existe_janela_multiplos_logins(
        self,
        session: Any,
    ) -> bool:
        """
        Verifica se a janela de múltiplos logins está aberta.

        A identificação é realizada pela existência das opções conhecidas
        da janela de múltiplas sessões.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            bool:
                True quando a janela de múltiplos logins for identificada.
                False quando a janela não estiver disponível.
        """

        opcao_continuar = self.elemento_existe(
            session=session,
            id_elemento=self.ID_OPCAO_CONTINUAR_LOGIN,
        )

        opcao_encerrar = self.elemento_existe(
            session=session,
            id_elemento=self.ID_OPCAO_ENCERRAR_OUTROS_LOGINS,
        )

        return (
            opcao_continuar
            or opcao_encerrar
        )

    def tratar_multiplos_logins(
        self,
        session: Any,
        continuar_com_login: bool = True,
    ) -> bool:
        """
        Trata a janela apresentada quando existem outros logins ativos.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            continuar_com_login (bool):
                Quando True, seleciona a opção para continuar com o novo
                login sem encerrar as outras sessões.

                Quando False, seleciona a opção para encerrar as outras
                sessões e manter o novo login.

        Returns:
            bool:
                True quando a janela for identificada e tratada.
                False quando a janela de múltiplos logins não estiver aberta.

        Raises:
            SAPMultiplosLoginsErro:
                Caso a janela seja identificada, mas não possa ser tratada.
        """

        if not self.existe_janela_multiplos_logins(
            session=session
        ):
            return False

        id_opcao = (
            self.ID_OPCAO_CONTINUAR_LOGIN
            if continuar_com_login
            else self.ID_OPCAO_ENCERRAR_OUTROS_LOGINS
        )

        try:
            opcao = self.localizar_elemento(
                session=session,
                id_elemento=id_opcao,
                obrigatorio=True,
            )

            try:
                opcao.select()

            except Exception:
                opcao.Selected = True

            botao_confirmar = self.localizar_elemento(
                session=session,
                id_elemento=self.ID_BOTAO_CONFIRMAR_MULTIPLOS_LOGINS,
                obrigatorio=True,
            )

            botao_confirmar.press()

            return True

        except Exception as erro:
            raise SAPMultiplosLoginsErro(
                "A janela de múltiplos logins foi identificada, "
                "mas não pôde ser tratada automaticamente."
            ) from erro

    # =========================================================================
    # VERIFICAÇÃO DA AUTENTICAÇÃO
    # =========================================================================

    def sessao_autenticada(
        self,
        session: Any,
    ) -> bool:
        """
        Verifica se a sessão SAP está autenticada.

        A sessão é considerada autenticada quando:
            - A sessão está válida;
            - A tela de login não está mais disponível;
            - A janela de múltiplos logins não está aberta;
            - As informações da sessão indicam um usuário autenticado
              ou uma transação/programa ativo.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            bool:
                True quando a sessão aparentar estar autenticada.
                False quando a autenticação ainda não estiver concluída.
        """

        try:
            self.validar_sessao(
                session=session
            )

        except SAPSessaoInvalidaErro:
            return False

        if self.esta_na_tela_login(
            session=session
        ):
            return False

        if self.existe_janela_multiplos_logins(
            session=session
        ):
            return False

        try:
            informacoes = session.Info

            usuario = str(
                getattr(informacoes, "User", "")
            ).strip()

            transacao = str(
                getattr(informacoes, "Transaction", "")
            ).strip()

            programa = str(
                getattr(informacoes, "Program", "")
            ).strip()

            return bool(
                usuario
                or transacao
                or programa
            )

        except Exception:
            try:
                janela_principal = self.localizar_elemento(
                    session=session,
                    id_elemento=self.id_janela_principal,
                    obrigatorio=False,
                )

                return janela_principal is not None

            except Exception:
                return False

    def aguardar_autenticacao(
        self,
        session: Any,
        tempo_limite: int | None = None,
        tratar_multiplos_logins: bool = True,
        continuar_com_login: bool = True,
    ) -> Any:
        """
        Aguarda até que a autenticação seja concluída.

        Durante a espera, o método verifica mensagens de erro e pode tratar
        automaticamente a janela de múltiplos logins.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar a autenticação.
                Quando não informado, utiliza o tempo configurado
                na instância.

            tratar_multiplos_logins (bool):
                Define se a janela de múltiplos logins deverá ser tratada
                automaticamente.

            continuar_com_login (bool):
                Define a opção utilizada no tratamento de múltiplos logins.
                Quando True, continua com o novo login sem encerrar as
                outras sessões.

        Returns:
            Any:
                A mesma sessão SAP após a autenticação ser concluída.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.

            SAPAutenticacaoErro:
                Caso o SAP apresente uma mensagem de erro durante o login.

            SAPMultiplosLoginsErro:
                Caso a janela de múltiplos logins não possa ser tratada.

            SAPTempoLimiteSessaoErro:
                Caso a autenticação não seja concluída dentro do
                tempo limite.
        """

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_login
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

            if self.existe_janela_multiplos_logins(
                session=session
            ):
                if not tratar_multiplos_logins:
                    raise SAPMultiplosLoginsErro(
                        "O SAP identificou outro login ativo e o "
                        "tratamento automático está desabilitado."
                    )

                self.tratar_multiplos_logins(
                    session=session,
                    continuar_com_login=continuar_com_login,
                )

                time.sleep(
                    self.intervalo_verificacao
                )

                continue

            self.verificar_erro_autenticacao(
                session=session
            )

            if self.sessao_autenticada(
                session=session
            ):
                return session

            time.sleep(
                self.intervalo_verificacao
            )

        mensagem_status, _ = self.obter_mensagem_status(
            session=session
        )

        mensagem = (
            "A autenticação no SAP não foi concluída dentro de "
            f"{limite} segundos."
        )

        if mensagem_status:
            mensagem = (
                f"{mensagem} Mensagem apresentada pelo SAP: "
                f"{mensagem_status}"
            )

        raise SAPTempoLimiteSessaoErro(
            mensagem
        )

    # =========================================================================
    # MÉTODO PRINCIPAL
    # =========================================================================

    def realizar_login(
        self,
        session: Any,
        usuario: str,
        senha: str,
        idioma: str = SAP_IDIOMA_PADRAO,
        mandante: str | None = None,
        tratar_multiplos_logins: bool = True,
        continuar_com_login: bool = True,
        reutilizar_sessao_autenticada: bool = True,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Realiza o login em uma sessão SAP.

        Quando a sessão já estiver autenticada e a reutilização estiver
        habilitada, a sessão será retornada sem preencher as credenciais.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            usuario (str):
                Usuário utilizado para autenticação no SAP.

            senha (str):
                Senha utilizada para autenticação no SAP.

            idioma (str):
                Idioma utilizado na sessão SAP.

            mandante (str | None):
                Código do mandante SAP. Quando não informado, o valor
                apresentado na tela será mantido.

            tratar_multiplos_logins (bool):
                Define se a janela de múltiplos logins deverá ser tratada
                automaticamente.

            continuar_com_login (bool):
                Quando True, continua com o novo login sem encerrar outras
                sessões. Quando False, seleciona a opção de encerramento
                dos outros logins.

            reutilizar_sessao_autenticada (bool):
                Define se uma sessão já autenticada poderá ser retornada
                sem executar novamente o login.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar a autenticação.
                Quando não informado, utiliza a configuração da instância.

        Returns:
            Any:
                Objeto da sessão SAP autenticada.

        Raises:
            SAPCredencialErro:
                Caso as credenciais informadas sejam inválidas.

            SAPSessaoInvalidaErro:
                Caso a sessão SAP não esteja válida.

            SAPTelaLoginNaoEncontradaErro:
                Caso a tela de login não esteja disponível.

            SAPAutenticacaoErro:
                Caso o SAP apresente uma falha de autenticação.

            SAPMultiplosLoginsErro:
                Caso a janela de múltiplos logins não possa ser tratada.

            SAPTempoLimiteSessaoErro:
                Caso a autenticação não seja concluída dentro do tempo
                limite configurado.

            SAPLoginErro:
                Caso ocorra uma falha inesperada durante o login.
        """

        self.validar_sessao(
            session=session
        )

        credenciais = self.validar_credenciais(
            usuario=usuario,
            senha=senha,
            idioma=idioma,
            mandante=mandante,
        )

        if (
            reutilizar_sessao_autenticada
            and self.sessao_autenticada(session=session)
        ):
            return session

        if not self.esta_na_tela_login(
            session=session
        ):
            self.aguardar_tela_login(
                session=session,
                tempo_limite=tempo_limite,
            )

        try:
            self.preencher_credenciais(
                session=session,
                usuario=credenciais[0],
                senha=credenciais[1],
                idioma=credenciais[2],
                mandante=credenciais[3],
            )

            self.enviar_credenciais(
                session=session
            )

            return self.aguardar_autenticacao(
                session=session,
                tempo_limite=tempo_limite,
                tratar_multiplos_logins=tratar_multiplos_logins,
                continuar_com_login=continuar_com_login,
            )

        except (
            SAPCredencialErro,
            SAPSessaoInvalidaErro,
            SAPTelaLoginNaoEncontradaErro,
            SAPAutenticacaoErro,
            SAPMultiplosLoginsErro,
            SAPTempoLimiteSessaoErro,
        ):
            raise

        except SAPLoginErro:
            raise

        except Exception as erro:
            raise SAPLoginErro(
                "Ocorreu um erro inesperado durante o login no SAP."
            ) from erro