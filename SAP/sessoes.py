"""
===============================================================================
Módulo: sessoes.py

Descrição:
    Responsável por localizar, listar, validar, aguardar e recuperar conexões
    e sessões disponíveis no SAP GUI Scripting.

    Este módulo centraliza as operações técnicas relacionadas às sessões SAP:
        - Obter o mecanismo SAP GUI Scripting;
        - Listar conexões abertas;
        - Listar sessões disponíveis;
        - Verificar se existem conexões ou sessões;
        - Recuperar conexões e sessões por índice;
        - Aguardar a criação de uma conexão;
        - Aguardar a criação de uma sessão;
        - Verificar se uma sessão continua válida;
        - Verificar se uma sessão está ocupada;
        - Aguardar uma sessão ficar disponível;
        - Localizar uma sessão por sistema, usuário ou transação;
        - Recuperar a primeira sessão válida e disponível.

    Este módulo não deve abrir o executável do SAP Logon, criar conexões,
    realizar login, abrir transações ou exportar arquivos.

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

import win32com.client

from services.SAP.constantes import (
    SAP_INDICE_CONEXAO_PADRAO,
    SAP_INDICE_SESSAO_PADRAO,
    SAP_INTERVALO_VERIFICACAO,
    SAP_OBJETO_GUI,
    SAP_TEMPO_LIMITE_CONEXAO,
    SAP_TEMPO_LIMITE_SESSAO,
)

from services.SAP.excecoes import (
    SAPConexaoNaoEncontradaErro,
    SAPScriptingErro,
    SAPSessaoInvalidaErro,
    SAPSessaoNaoEncontradaErro,
    SAPSessaoOcupadaErro,
    SAPTempoLimiteConexaoErro,
    SAPTempoLimiteSessaoErro,
)


# =============================================================================
# CLASSE DE GERENCIAMENTO DE SESSÕES
# =============================================================================


class GerenciadorSessoesSAP:
    """
    Gerencia as conexões e sessões disponíveis no SAP GUI.

    A classe permite consultar o objeto SAP GUI Scripting, listar conexões,
    listar sessões, recuperar uma sessão específica e aguardar dinamicamente
    até que uma conexão ou sessão fique disponível.

    Attributes:
        tempo_limite_conexao (int):
            Tempo máximo, em segundos, para aguardar uma conexão SAP.

        tempo_limite_sessao (int):
            Tempo máximo, em segundos, para aguardar uma sessão SAP.

        intervalo_verificacao (float):
            Intervalo, em segundos, entre as tentativas de verificação.
    """

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================

    def __init__(
        self,
        tempo_limite_conexao: int = SAP_TEMPO_LIMITE_CONEXAO,
        tempo_limite_sessao: int = SAP_TEMPO_LIMITE_SESSAO,
        intervalo_verificacao: float = SAP_INTERVALO_VERIFICACAO,
    ) -> None:
        """
        Inicializa o gerenciador de sessões SAP.

        Args:
            tempo_limite_conexao (int):
                Tempo máximo, em segundos, para aguardar uma conexão SAP.

            tempo_limite_sessao (int):
                Tempo máximo, em segundos, para aguardar uma sessão SAP.

            intervalo_verificacao (float):
                Intervalo, em segundos, entre as verificações.

        Returns:
            None.

        Raises:
            ValueError:
                Caso algum tempo limite ou intervalo seja menor ou igual
                a zero.
        """

        if tempo_limite_conexao <= 0:
            raise ValueError(
                "O tempo limite da conexão deve ser maior que zero."
            )

        if tempo_limite_sessao <= 0:
            raise ValueError(
                "O tempo limite da sessão deve ser maior que zero."
            )

        if intervalo_verificacao <= 0:
            raise ValueError(
                "O intervalo de verificação deve ser maior que zero."
            )

        self.tempo_limite_conexao = tempo_limite_conexao
        self.tempo_limite_sessao = tempo_limite_sessao
        self.intervalo_verificacao = float(
            intervalo_verificacao
        )

    # =========================================================================
    # ACESSO AO SAP GUI SCRIPTING
    # =========================================================================

    def obter_application(self) -> Any:
        """
        Obtém o objeto principal do SAP GUI Scripting.

        Returns:
            Any:
                Objeto de aplicação do SAP GUI Scripting.

        Raises:
            SAPScriptingErro:
                Caso o objeto SAP GUI não esteja disponível ou o mecanismo
                de scripting não possa ser acessado.
        """

        try:
            sap_gui = win32com.client.GetObject(
                SAP_OBJETO_GUI
            )

            application = sap_gui.GetScriptingEngine

            if application is None:
                raise SAPScriptingErro(
                    "O SAP GUI não retornou uma aplicação de scripting."
                )

            return application

        except SAPScriptingErro:
            raise

        except Exception as erro:
            raise SAPScriptingErro(
                "Não foi possível acessar o SAP GUI Scripting. "
                "Verifique se o SAP Logon está aberto e se o scripting "
                "está habilitado."
            ) from erro

    def scripting_disponivel(self) -> bool:
        """
        Verifica se o SAP GUI Scripting está disponível.

        Returns:
            bool:
                True quando o mecanismo de scripting estiver acessível.
                False quando o mecanismo não estiver disponível.
        """

        try:
            self.obter_application()
            return True

        except SAPScriptingErro:
            return False

    # =========================================================================
    # GERENCIAMENTO DE CONEXÕES
    # =========================================================================

    def listar_conexoes(
        self,
        application: Any | None = None,
    ) -> list[Any]:
        """
        Lista todas as conexões abertas no SAP GUI.

        Args:
            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Quando não
                informado, o objeto será obtido automaticamente.

        Returns:
            listLista contendo as conexões SAP encontradas. Retorna uma
                lista vazia quando nenhuma conexão estiver disponível.

        Raises:
            SAPScriptingErro:
                Caso o SAP GUI Scripting não possa ser acessado.
        """

        aplicacao = (
            application
            if application is not None
            else self.obter_application()
        )

        conexoes: list[Any] = []

        try:
            quantidade_conexoes = aplicacao.Children.Count

        except Exception:
            return conexoes

        for indice in range(quantidade_conexoes):
            try:
                conexao = aplicacao.Children(indice)

                if conexao is not None:
                    conexoes.append(conexao)

            except Exception:
                continue

        return conexoes

    def existe_conexao(
        self,
        application: Any | None = None,
    ) -> bool:
        """
        Verifica se existe pelo menos uma conexão SAP aberta.

        Args:
            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Quando não
                informado, o objeto será obtido automaticamente.

        Returns:
            bool:
                True quando existir pelo menos uma conexão SAP.
                False quando nenhuma conexão estiver disponível.
        """

        try:
            return bool(
                self.listar_conexoes(
                    application=application
                )
            )

        except SAPScriptingErro:
            return False

    def obter_conexao(
        self,
        indice_conexao: int = SAP_INDICE_CONEXAO_PADRAO,
        application: Any | None = None,
    ) -> Any:
        """
        Recupera uma conexão SAP pelo índice informado.

        Args:
            indice_conexao (int):
                Índice da conexão que será recuperada.

            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Quando não
                informado, o objeto será obtido automaticamente.

        Returns:
            Any:
                Objeto da conexão SAP encontrada.

        Raises:
            ValueError:
                Caso o índice informado seja negativo.

            SAPConexaoNaoEncontradaErro:
                Caso a conexão solicitada não exista.
        """

        if indice_conexao < 0:
            raise ValueError(
                "O índice da conexão não pode ser negativo."
            )

        conexoes = self.listar_conexoes(
            application=application
        )

        if indice_conexao >= len(conexoes):
            raise SAPConexaoNaoEncontradaErro(
                "A conexão SAP solicitada não foi encontrada. "
                f"Índice informado: {indice_conexao}. "
                f"Quantidade disponível: {len(conexoes)}."
            )

        return conexoes[indice_conexao]

    def aguardar_conexao(
        self,
        application: Any | None = None,
        indice_conexao: int = SAP_INDICE_CONEXAO_PADRAO,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Aguarda até que uma conexão SAP fique disponível.

        Args:
            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Quando não
                informado, o objeto será obtido automaticamente.

            indice_conexao (int):
                Índice da conexão que será aguardada.

            tempo_limite (int | None):
                Tempo máximo de espera, em segundos. Quando não informado,
                utiliza o tempo configurado na instância.

        Returns:
            Any:
                Objeto da conexão SAP encontrada.

        Raises:
            ValueError:
                Caso o índice seja negativo ou o tempo limite seja menor
                ou igual a zero.

            SAPTempoLimiteConexaoErro:
                Caso a conexão não fique disponível dentro do tempo limite.
        """

        if indice_conexao < 0:
            raise ValueError(
                "O índice da conexão não pode ser negativo."
            )

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_conexao
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()
        ultimo_erro: Exception | None = None

        while time.monotonic() - inicio < limite:
            try:
                return self.obter_conexao(
                    indice_conexao=indice_conexao,
                    application=application,
                )

            except (
                SAPConexaoNaoEncontradaErro,
                SAPScriptingErro,
            ) as erro:
                ultimo_erro = erro

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPTempoLimiteConexaoErro(
            "A conexão SAP não ficou disponível dentro de "
            f"{limite} segundos. Índice aguardado: "
            f"{indice_conexao}."
        ) from ultimo_erro

    # =========================================================================
    # GERENCIAMENTO DE SESSÕES
    # =========================================================================

    def listar_sessoes(
        self,
        connection: Any | None = None,
        application: Any | None = None,
    ) -> list[Any]:
        """
        Lista as sessões SAP disponíveis.

        Quando uma conexão for informada, apenas as sessões dessa conexão
        serão retornadas. Quando nenhuma conexão for informada, todas as
        conexões abertas serão consultadas.

        Args:
            connection (Any | None):
                Conexão SAP que será consultada.

            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Utilizado apenas
                quando nenhuma conexão for informada.

        Returns:
            listLista contendo as sessões SAP encontradas. Retorna uma lista
                vazia quando nenhuma sessão estiver disponível.

        Raises:
            SAPScriptingErro:
                Caso o SAP GUI Scripting não possa ser acessado.
        """

        if connection is not None:
            conexoes = [connection]

        else:
            conexoes = self.listar_conexoes(
                application=application
            )

        sessoes: list[Any] = []

        for conexao in conexoes:
            try:
                quantidade_sessoes = conexao.Children.Count

            except Exception:
                continue

            for indice in range(quantidade_sessoes):
                try:
                    sessao = conexao.Children(indice)

                    if sessao is not None:
                        sessoes.append(sessao)

                except Exception:
                    continue

        return sessoes

    def existe_sessao(
        self,
        connection: Any | None = None,
        application: Any | None = None,
    ) -> bool:
        """
        Verifica se existe pelo menos uma sessão SAP disponível.

        Args:
            connection (Any | None):
                Conexão SAP que será consultada. Quando não informada,
                todas as conexões serão verificadas.

            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Utilizado apenas
                quando nenhuma conexão for informada.

        Returns:
            bool:
                True quando existir pelo menos uma sessão SAP.
                False quando nenhuma sessão estiver disponível.
        """

        try:
            return bool(
                self.listar_sessoes(
                    connection=connection,
                    application=application,
                )
            )

        except SAPScriptingErro:
            return False

    def obter_sessao(
        self,
        indice_conexao: int = SAP_INDICE_CONEXAO_PADRAO,
        indice_sessao: int = SAP_INDICE_SESSAO_PADRAO,
        application: Any | None = None,
    ) -> Any:
        """
        Recupera uma sessão SAP pelos índices da conexão e da sessão.

        Args:
            indice_conexao (int):
                Índice da conexão que contém a sessão.

            indice_sessao (int):
                Índice da sessão dentro da conexão.

            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Quando não
                informado, o objeto será obtido automaticamente.

        Returns:
            Any:
                Objeto da sessão SAP encontrada.

        Raises:
            ValueError:
                Caso algum índice informado seja negativo.

            SAPConexaoNaoEncontradaErro:
                Caso a conexão informada não exista.

            SAPSessaoNaoEncontradaErro:
                Caso a sessão informada não exista.
        """

        if indice_conexao < 0:
            raise ValueError(
                "O índice da conexão não pode ser negativo."
            )

        if indice_sessao < 0:
            raise ValueError(
                "O índice da sessão não pode ser negativo."
            )

        conexao = self.obter_conexao(
            indice_conexao=indice_conexao,
            application=application,
        )

        sessoes = self.listar_sessoes(
            connection=conexao
        )

        if indice_sessao >= len(sessoes):
            raise SAPSessaoNaoEncontradaErro(
                "A sessão SAP solicitada não foi encontrada. "
                f"Índice da conexão: {indice_conexao}. "
                f"Índice da sessão: {indice_sessao}. "
                f"Quantidade disponível: {len(sessoes)}."
            )

        sessao = sessoes[indice_sessao]

        if not self.sessao_valida(
            session=sessao
        ):
            raise SAPSessaoInvalidaErro(
                "A sessão SAP foi encontrada, mas não está válida."
            )

        return sessao

    def obter_primeira_sessao(
        self,
        application: Any | None = None,
        somente_disponivel: bool = False,
    ) -> Any:
        """
        Recupera a primeira sessão SAP válida encontrada.

        Args:
            application (Any | None):
                Objeto de aplicação do SAP GUI Scripting. Quando não
                informado, o objeto será obtido automaticamente.

            somente_disponivel (bool):
                Define se sessões ocupadas devem ser ignoradas.
                O valor padrão é False.

        Returns:
            Any:
                Primeira sessão SAP válida encontrada.

        Raises:
            SAPSessaoNaoEncontradaErro:
                Caso nenhuma sessão válida seja encontrada.
        """

        sessoes = self.listar_sessoes(
            application=application
        )

        for sessao in sessoes:
            if not self.sessao_valida(
                session=sessao
            ):
                continue

            if (
                somente_disponivel
                and self.sessao_ocupada(session=sessao)
            ):
                continue

            return sessao

        raise SAPSessaoNaoEncontradaErro(
            "Nenhuma sessão SAP válida foi encontrada."
        )

    def aguardar_sessao(
        self,
        connection: Any | None = None,
        indice_sessao: int = SAP_INDICE_SESSAO_PADRAO,
        tempo_limite: int | None = None,
        somente_disponivel: bool = False,
    ) -> Any:
        """
        Aguarda até que uma sessão SAP fique disponível.

        Args:
            connection (Any | None):
                Conexão SAP que será monitorada. Quando não informada,
                todas as conexões serão consultadas.

            indice_sessao (int):
                Índice da sessão que será aguardada quando uma conexão
                específica for informada.

            tempo_limite (int | None):
                Tempo máximo de espera, em segundos. Quando não informado,
                utiliza o tempo configurado na instância.

            somente_disponivel (bool):
                Define se a sessão também precisa estar livre para uso.
                O valor padrão é False.

        Returns:
            Any:
                Objeto da sessão SAP encontrada.

        Raises:
            ValueError:
                Caso o índice seja negativo ou o tempo limite seja menor
                ou igual a zero.

            SAPTempoLimiteSessaoErro:
                Caso nenhuma sessão fique disponível dentro do tempo limite.
        """

        if indice_sessao < 0:
            raise ValueError(
                "O índice da sessão não pode ser negativo."
            )

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_sessao
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()
        ultimo_erro: Exception | None = None

        while time.monotonic() - inicio < limite:
            try:
                sessoes = self.listar_sessoes(
                    connection=connection
                )

                if indice_sessao < len(sessoes):
                    sessao = sessoes[indice_sessao]

                    if not self.sessao_valida(
                        session=sessao
                    ):
                        raise SAPSessaoInvalidaErro(
                            "A sessão encontrada não está válida."
                        )

                    if (
                        somente_disponivel
                        and self.sessao_ocupada(session=sessao)
                    ):
                        time.sleep(
                            self.intervalo_verificacao
                        )
                        continue

                    return sessao

            except (
                SAPScriptingErro,
                SAPSessaoInvalidaErro,
            ) as erro:
                ultimo_erro = erro

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPTempoLimiteSessaoErro(
            "Nenhuma sessão SAP ficou disponível dentro de "
            f"{limite} segundos."
        ) from ultimo_erro

    # =========================================================================
    # VALIDAÇÃO DA SESSÃO
    # =========================================================================

    def sessao_valida(
        self,
        session: Any,
    ) -> bool:
        """
        Verifica se uma sessão SAP continua válida e acessível.

        Args:
            session (Any):
                Objeto da sessão SAP que será validado.

        Returns:
            bool:
                True quando a sessão estiver acessível.
                False quando a sessão estiver encerrada ou inválida.
        """

        if session is None:
            return False

        try:
            _ = session.Id
            _ = session.Children.Count

            return True

        except Exception:
            return False

    def validar_sessao(
        self,
        session: Any,
    ) -> None:
        """
        Valida se uma sessão SAP está disponível para utilização.

        Args:
            session (Any):
                Objeto da sessão SAP que será validado.

        Returns:
            None.

        Raises:
            SAPSessaoInvalidaErro:
                Caso a sessão seja None, tenha sido encerrada ou esteja
                inacessível.
        """

        if not self.sessao_valida(
            session=session
        ):
            raise SAPSessaoInvalidaErro(
                "A sessão SAP informada não está válida ou foi encerrada."
            )

    def sessao_ocupada(
        self,
        session: Any,
    ) -> bool:
        """
        Verifica se uma sessão SAP está processando uma operação.

        Args:
            session (Any):
                Objeto da sessão SAP que será consultado.

        Returns:
            bool:
                True quando a sessão estiver ocupada.
                False quando a sessão estiver livre.

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
        Aguarda até que uma sessão SAP fique livre para utilização.

        Args:
            session (Any):
                Objeto da sessão SAP que será monitorado.

            tempo_limite (int | None):
                Tempo máximo de espera, em segundos. Quando não informado,
                utiliza o tempo configurado na instância.

        Returns:
            Any:
                A mesma sessão SAP após ficar disponível.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.

            SAPSessaoInvalidaErro:
                Caso a sessão seja encerrada durante a espera.

            SAPSessaoOcupadaErro:
                Caso a sessão permaneça ocupada após o tempo limite.
        """

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_sessao
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
    # INFORMAÇÕES DA SESSÃO
    # =========================================================================

    @staticmethod
    def _obter_propriedade(
        objeto: Any,
        nome_propriedade: str,
        valor_padrao: Any = None,
    ) -> Any:
        """
        Obtém uma propriedade de um objeto COM com segurança.

        Args:
            objeto (Any):
                Objeto COM que será consultado.

            nome_propriedade (str):
                Nome da propriedade que será recuperada.

            valor_padrao (Any):
                Valor retornado quando a propriedade não puder ser obtida.

        Returns:
            Any:
                Valor da propriedade ou o valor padrão informado.
        """

        try:
            return getattr(
                objeto,
                nome_propriedade
            )

        except Exception:
            return valor_padrao

    def obter_informacoes_sessao(
        self,
        session: Any,
    ) -> dict[str, Any]:
        """
        Obtém informações técnicas de uma sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP que será consultado.

        Returns:
            dict[str, Any]:
                Dicionário contendo informações da sessão, como sistema,
                mandante, usuário, transação, programa e estado de ocupação.

        Raises:
            SAPSessaoInvalidaErro:
                Caso a sessão informada não esteja válida.
        """

        self.validar_sessao(
            session=session
        )

        try:
            info = session.Info

        except Exception as erro:
            raise SAPSessaoInvalidaErro(
                "Não foi possível acessar as informações da sessão SAP."
            ) from erro

        return {
            "id": self._obter_propriedade(
                session,
                "Id",
            ),
            "sistema": self._obter_propriedade(
                info,
                "SystemName",
            ),
            "mandante": self._obter_propriedade(
                info,
                "Client",
            ),
            "usuario": self._obter_propriedade(
                info,
                "User",
            ),
            "transacao": self._obter_propriedade(
                info,
                "Transaction",
            ),
            "programa": self._obter_propriedade(
                info,
                "Program",
            ),
            "servidor": self._obter_propriedade(
                info,
                "ApplicationServer",
            ),
            "ocupada": self.sessao_ocupada(
                session=session
            ),
        }

    # =========================================================================
    # LOCALIZAÇÃO DE SESSÕES
    # =========================================================================

    def localizar_sessao(
        self,
        sistema: str | None = None,
        usuario: str | None = None,
        transacao: str | None = None,
        somente_disponivel: bool = False,
    ) -> Any:
        """
        Localiza uma sessão SAP utilizando os filtros informados.

        Os filtros não informados são ignorados. As comparações são
        realizadas sem diferenciação entre letras maiúsculas e minúsculas.

        Args:
            sistema (str | None):
                Nome do sistema SAP que deverá ser localizado.

            usuario (str | None):
                Usuário autenticado na sessão.

            transacao (str | None):
                Código da transação atualmente aberta.

            somente_disponivel (bool):
                Define se sessões ocupadas devem ser ignoradas.
                O valor padrão é False.

        Returns:
            Any:
                Primeira sessão SAP que corresponda aos filtros.

        Raises:
            ValueError:
                Caso nenhum filtro seja informado.

            SAPSessaoNaoEncontradaErro:
                Caso nenhuma sessão corresponda aos filtros.
        """

        filtros = {
            "sistema": sistema,
            "usuario": usuario,
            "transacao": transacao,
        }

        filtros_normalizados = {
            chave: valor.strip().upper()
            for chave, valor in filtros.items()
            if isinstance(valor, str) and valor.strip()
        }

        if not filtros_normalizados:
            raise ValueError(
                "Informe pelo menos um filtro para localizar a sessão."
            )

        sessoes = self.listar_sessoes()

        for sessao in sessoes:
            if not self.sessao_valida(
                session=sessao
            ):
                continue

            if (
                somente_disponivel
                and self.sessao_ocupada(session=sessao)
            ):
                continue

            try:
                informacoes = self.obter_informacoes_sessao(
                    session=sessao
                )

            except SAPSessaoInvalidaErro:
                continue

            corresponde = True

            for chave, valor_esperado in filtros_normalizados.items():
                valor_atual = informacoes.get(
                    chave
                )

                valor_atual_normalizado = (
                    str(valor_atual).strip().upper()
                    if valor_atual is not None
                    else ""
                )

                if valor_atual_normalizado != valor_esperado:
                    corresponde = False
                    break

            if corresponde:
                return sessao

        raise SAPSessaoNaoEncontradaErro(
            "Nenhuma sessão SAP corresponde aos filtros informados."
        )