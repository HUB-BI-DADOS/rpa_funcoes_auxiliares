"""
===============================================================================
Módulo: exportacao.py

Descrição:
    Responsável por gerenciar exportações de relatórios e dados do SAP GUI
    para arquivos locais.

    Este módulo centraliza operações técnicas reutilizáveis relacionadas à
    exportação de arquivos, incluindo:
        - Validação do diretório de destino;
        - Criação do diretório de destino;
        - Validação e preparação do nome do arquivo;
        - Remoção de arquivos existentes;
        - Preenchimento da janela de salvamento do SAP;
        - Confirmação da exportação;
        - Tratamento da confirmação de substituição;
        - Espera dinâmica pela criação do arquivo;
        - Verificação de estabilidade do arquivo;
        - Exportação utilizando IDs personalizados;
        - Exportação utilizando os IDs tradicionais do SAP GUI.

    Este módulo não executa transações, não realiza login e não define as
    regras de negócio das extrações. O módulo espera receber uma sessão SAP
    válida e posicionada na tela de exportação.

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

from pathlib import Path
from typing import Any

from .constantes import (
    SAP_INTERVALO_VERIFICACAO,
)

from .excecoes import (
    SAPArquivoExistenteErro,
    SAPArquivoExportacaoErro,
    SAPExportacaoErro,
    SAPTempoLimiteExportacaoErro,
)


# =============================================================================
# CLASSE DE EXPORTAÇÃO SAP
# =============================================================================


class ExportadorSAP:
    """
    Gerencia exportações de arquivos realizadas pelo SAP GUI.

    A classe fornece métodos reutilizáveis para preencher os campos da
    janela de salvamento, confirmar a exportação, tratar a substituição
    de arquivos existentes e aguardar a criação do arquivo no diretório
    de destino.

    Attributes:
        tempo_limite_exportacao (int):
            Tempo máximo, em segundos, para aguardar a criação do arquivo.

        intervalo_verificacao (float):
            Intervalo, em segundos, entre as verificações do arquivo.

        quantidade_verificacoes_estabilidade (int):
            Quantidade de verificações consecutivas com o mesmo tamanho
            necessárias para considerar o arquivo estável.
    """

    # =========================================================================
    # IDENTIFICADORES PADRÕES DA JANELA DE SALVAMENTO
    # =========================================================================

    ID_CAMPO_DIRETORIO_PADRAO = (
        "wnd[1]/usr/ctxtDY_PATH"
    )

    ID_CAMPO_NOME_ARQUIVO_PADRAO = (
        "wnd[1]/usr/ctxtDY_FILENAME"
    )

    ID_BOTAO_SALVAR_PADRAO = (
        "wnd[1]/tbar[0]/btn[11]"
    )

    ID_BOTAO_SUBSTITUIR_PADRAO = (
        "wnd[1]/tbar[0]/btn[11]"
    )

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================

    def __init__(
        self,
        tempo_limite_exportacao: int = 120,
        intervalo_verificacao: float = SAP_INTERVALO_VERIFICACAO,
        quantidade_verificacoes_estabilidade: int = 3,
    ) -> None:
        """
        Inicializa o gerenciador de exportações do SAP.

        Args:
            tempo_limite_exportacao (int):
                Tempo máximo, em segundos, para aguardar a criação e a
                finalização do arquivo exportado.

            intervalo_verificacao (float):
                Intervalo, em segundos, entre as verificações realizadas
                no arquivo de destino.

            quantidade_verificacoes_estabilidade (int):
                Quantidade de verificações consecutivas em que o arquivo
                deve permanecer com o mesmo tamanho para ser considerado
                completamente gravado.

        Returns:
            None.

        Raises:
            ValueError:
                Caso algum tempo, intervalo ou quantidade seja menor ou
                igual a zero.
        """

        if (
            isinstance(tempo_limite_exportacao, bool)
            or not isinstance(tempo_limite_exportacao, int)
            or tempo_limite_exportacao <= 0
        ):
            raise ValueError(
                "O tempo limite da exportação deve ser um número "
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

        if (
            isinstance(quantidade_verificacoes_estabilidade, bool)
            or not isinstance(
                quantidade_verificacoes_estabilidade,
                int,
            )
            or quantidade_verificacoes_estabilidade <= 0
        ):
            raise ValueError(
                "A quantidade de verificações de estabilidade deve "
                "ser um número inteiro maior que zero."
            )

        self.tempo_limite_exportacao = tempo_limite_exportacao

        self.intervalo_verificacao = float(
            intervalo_verificacao
        )

        self.quantidade_verificacoes_estabilidade = (
            quantidade_verificacoes_estabilidade
        )

    # =========================================================================
    # VALIDAÇÕES
    # =========================================================================

    @staticmethod
    def validar_sessao(
        session: Any,
    ) -> None:
        """
        Valida se uma sessão SAP foi informada.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

        Returns:
            None.

        Raises:
            SAPExportacaoErro:
                Caso a sessão seja None ou não esteja acessível.
        """

        if session is None:
            raise SAPExportacaoErro(
                "A sessão SAP não pode ser None."
            )

        try:
            _ = session.Id

        except Exception as erro:
            raise SAPExportacaoErro(
                "A sessão SAP informada não está válida ou não "
                "está acessível."
            ) from erro

    @staticmethod
    def validar_nome_arquivo(
        nome_arquivo: str,
    ) -> str:
        """
        Valida e normaliza o nome do arquivo de exportação.

        Args:
            nome_arquivo (str):
                Nome do arquivo que será criado pelo SAP.

        Returns:
            str:
                Nome do arquivo validado e sem espaços desnecessários.

        Raises:
            ValueError:
                Caso o nome informado esteja vazio ou contenha caracteres
                inválidos para nomes de arquivos no Windows.
        """

        if not isinstance(nome_arquivo, str):
            raise ValueError(
                "O nome do arquivo deve ser uma string."
            )

        nome_normalizado = nome_arquivo.strip()

        if not nome_normalizado:
            raise ValueError(
                "O nome do arquivo não pode ser vazio."
            )

        caracteres_invalidos = (
            "<",
            ">",
            ":",
            '"',
            "/",
            "\\",
            "|",
            "?",
            "*",
        )

        caracteres_encontrados = [
            caractere
            for caractere in caracteres_invalidos
            if caractere in nome_normalizado
        ]

        if caracteres_encontrados:
            raise ValueError(
                "O nome do arquivo contém caracteres inválidos: "
                f"{', '.join(caracteres_encontrados)}."
            )

        return nome_normalizado

    @staticmethod
    def preparar_diretorio(
        caminho_diretorio: Path | str,
        criar_diretorio: bool = True,
    ) -> Path:
        """
        Valida e prepara o diretório utilizado na exportação.

        Args:
            caminho_diretorio (Path | str):
                Caminho do diretório onde o arquivo será exportado.

            criar_diretorio (bool):
                Define se o diretório deverá ser criado quando não existir.
                O valor padrão é True.

        Returns:
            Path:
                Caminho absoluto e validado do diretório.

        Raises:
            ValueError:
                Caso o caminho informado esteja vazio.

            SAPArquivoExportacaoErro:
                Caso o diretório não exista, não possa ser criado ou o
                caminho corresponda a um arquivo.
        """

        if caminho_diretorio is None:
            raise ValueError(
                "O caminho do diretório não pode ser None."
            )

        if not str(caminho_diretorio).strip():
            raise ValueError(
                "O caminho do diretório não pode ser vazio."
            )

        diretorio = Path(
            caminho_diretorio
        ).expanduser()

        try:
            diretorio = diretorio.resolve()

        except OSError:
            diretorio = diretorio.absolute()

        if diretorio.exists() and not diretorio.is_dir():
            raise SAPArquivoExportacaoErro(
                "O caminho informado para exportação não corresponde "
                f"a um diretório: {diretorio}"
            )

        if not diretorio.exists():
            if not criar_diretorio:
                raise SAPArquivoExportacaoErro(
                    "O diretório de exportação não existe: "
                    f"{diretorio}"
                )

            try:
                diretorio.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            except OSError as erro:
                raise SAPArquivoExportacaoErro(
                    "Não foi possível criar o diretório de exportação: "
                    f"{diretorio}"
                ) from erro

        return diretorio

    def preparar_caminho_arquivo(
        self,
        caminho_diretorio: Path | str,
        nome_arquivo: str,
        criar_diretorio: bool = True,
    ) -> Path:
        """
        Prepara o caminho completo do arquivo de exportação.

        Args:
            caminho_diretorio (Path | str):
                Diretório onde o arquivo será criado.

            nome_arquivo (str):
                Nome do arquivo que será exportado.

            criar_diretorio (bool):
                Define se o diretório deverá ser criado quando não existir.

        Returns:
            Path:
                Caminho completo e validado do arquivo.
        """

        diretorio = self.preparar_diretorio(
            caminho_diretorio=caminho_diretorio,
            criar_diretorio=criar_diretorio,
        )

        nome_validado = self.validar_nome_arquivo(
            nome_arquivo=nome_arquivo
        )

        return diretorio / nome_validado

    # =========================================================================
    # GERENCIAMENTO DO ARQUIVO DE DESTINO
    # =========================================================================

    @staticmethod
    def remover_arquivo_existente(
        caminho_arquivo: Path | str,
        ignorar_inexistente: bool = True,
    ) -> bool:
        """
        Remove um arquivo existente antes de uma nova exportação.

        Args:
            caminho_arquivo (Path | str):
                Caminho completo do arquivo que será removido.

            ignorar_inexistente (bool):
                Define se a ausência do arquivo deve ser ignorada.
                O valor padrão é True.

        Returns:
            bool:
                True quando o arquivo for removido.
                False quando o arquivo não existir e a ausência for ignorada.

        Raises:
            SAPArquivoExportacaoErro:
                Caso o caminho corresponda a um diretório.

            SAPArquivoExistenteErro:
                Caso o arquivo exista, mas não possa ser removido.

            FileNotFoundError:
                Caso o arquivo não exista e ignorar_inexistente seja False.
        """

        arquivo = Path(
            caminho_arquivo
        )

        if not arquivo.exists():
            if ignorar_inexistente:
                return False

            raise FileNotFoundError(
                f"Arquivo não encontrado: {arquivo}"
            )

        if arquivo.is_dir():
            raise SAPArquivoExportacaoErro(
                "O caminho informado corresponde a um diretório, "
                f"não a um arquivo: {arquivo}"
            )

        try:
            arquivo.unlink()
            return True

        except OSError as erro:
            raise SAPArquivoExistenteErro(
                "O arquivo de destino já existe e não pôde ser "
                f"removido: {arquivo}"
            ) from erro

    # =========================================================================
    # LOCALIZAÇÃO E PREENCHIMENTO DE ELEMENTOS
    # =========================================================================

    @staticmethod
    def localizar_elemento(
        session: Any,
        id_elemento: str,
    ) -> Any:
        """
        Localiza um elemento na sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_elemento (str):
                Identificador completo do elemento no SAP GUI.

        Returns:
            Any:
                Objeto do elemento localizado.

        Raises:
            ValueError:
                Caso o identificador esteja vazio.

            SAPExportacaoErro:
                Caso o elemento não seja encontrado.
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
            raise SAPExportacaoErro(
                "Não foi possível localizar o elemento da exportação: "
                f"'{id_normalizado}'."
            ) from erro

    def preencher_campo(
        self,
        session: Any,
        id_campo: str,
        valor: str,
    ) -> None:
        """
        Preenche um campo na janela de exportação do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_campo (str):
                Identificador completo do campo que será preenchido.

            valor (str):
                Valor que será inserido no campo.

        Returns:
            None.

        Raises:
            SAPExportacaoErro:
                Caso o campo não seja encontrado ou não possa ser preenchido.
        """

        try:
            campo = self.localizar_elemento(
                session=session,
                id_elemento=id_campo,
            )

            campo.text = str(valor)

        except SAPExportacaoErro:
            raise

        except Exception as erro:
            raise SAPExportacaoErro(
                "Não foi possível preencher o campo de exportação: "
                f"'{id_campo}'."
            ) from erro

    def pressionar_botao(
        self,
        session: Any,
        id_botao: str,
    ) -> None:
        """
        Pressiona um botão na janela de exportação do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao (str):
                Identificador completo do botão que será pressionado.

        Returns:
            None.

        Raises:
            SAPExportacaoErro:
                Caso o botão não seja encontrado ou não possa ser acionado.
        """

        try:
            botao = self.localizar_elemento(
                session=session,
                id_elemento=id_botao,
            )

            botao.press()

        except SAPExportacaoErro:
            raise

        except Exception as erro:
            raise SAPExportacaoErro(
                "Não foi possível pressionar o botão de exportação: "
                f"'{id_botao}'."
            ) from erro

    # =========================================================================
    # JANELA DE SALVAMENTO
    # =========================================================================

    def preencher_janela_salvamento(
        self,
        session: Any,
        caminho_diretorio: Path | str,
        nome_arquivo: str,
        id_campo_diretorio: str = ID_CAMPO_DIRETORIO_PADRAO,
        id_campo_nome_arquivo: str = ID_CAMPO_NOME_ARQUIVO_PADRAO,
    ) -> Path:
        """
        Preenche o diretório e o nome na janela de salvamento do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            caminho_diretorio (Path | str):
                Diretório onde o arquivo será salvo.

            nome_arquivo (str):
                Nome do arquivo que será criado.

            id_campo_diretorio (str):
                Identificador do campo de diretório na janela do SAP.

            id_campo_nome_arquivo (str):
                Identificador do campo de nome do arquivo na janela do SAP.

        Returns:
            Path:
                Caminho completo esperado para o arquivo exportado.

        Raises:
            SAPArquivoExportacaoErro:
                Caso o diretório seja inválido.

            SAPExportacaoErro:
                Caso os campos não possam ser preenchidos.
        """

        self.validar_sessao(
            session=session
        )

        caminho_arquivo = self.preparar_caminho_arquivo(
            caminho_diretorio=caminho_diretorio,
            nome_arquivo=nome_arquivo,
            criar_diretorio=True,
        )

        self.preencher_campo(
            session=session,
            id_campo=id_campo_diretorio,
            valor=str(caminho_arquivo.parent),
        )

        self.preencher_campo(
            session=session,
            id_campo=id_campo_nome_arquivo,
            valor=caminho_arquivo.name,
        )

        return caminho_arquivo

    def confirmar_salvamento(
        self,
        session: Any,
        id_botao_salvar: str = ID_BOTAO_SALVAR_PADRAO,
    ) -> None:
        """
        Confirma o salvamento do arquivo na janela do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao_salvar (str):
                Identificador do botão utilizado para confirmar a gravação.

        Returns:
            None.

        Raises:
            SAPExportacaoErro:
                Caso o botão de salvamento não possa ser acionado.
        """

        self.pressionar_botao(
            session=session,
            id_botao=id_botao_salvar,
        )

    def confirmar_substituicao(
        self,
        session: Any,
        id_botao_substituir: str = ID_BOTAO_SUBSTITUIR_PADRAO,
        obrigatorio: bool = False,
    ) -> bool:
        """
        Confirma a substituição de um arquivo existente.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao_substituir (str):
                Identificador do botão utilizado para confirmar a
                substituição do arquivo.

            obrigatorio (bool):
                Define se a ausência da janela de substituição deverá
                gerar uma exceção.

        Returns:
            bool:
                True quando a substituição for confirmada.
                False quando a janela não existir e obrigatorio for False.

        Raises:
            SAPExportacaoErro:
                Caso a substituição seja obrigatória e o botão não possa
                ser localizado ou acionado.
        """

        try:
            self.pressionar_botao(
                session=session,
                id_botao=id_botao_substituir,
            )

            return True

        except SAPExportacaoErro:
            if obrigatorio:
                raise

            return False

    # =========================================================================
    # ESPERA PELO ARQUIVO
    # =========================================================================

    @staticmethod
    def arquivo_existe(
        caminho_arquivo: Path | str,
    ) -> bool:
        """
        Verifica se o arquivo exportado existe.

        Args:
            caminho_arquivo (Path | str):
                Caminho completo do arquivo que será verificado.

        Returns:
            bool:
                True quando o caminho existir e corresponder a um arquivo.
                False quando o arquivo não existir.
        """

        arquivo = Path(
            caminho_arquivo
        )

        return (
            arquivo.exists()
            and arquivo.is_file()
        )

    def aguardar_arquivo(
        self,
        caminho_arquivo: Path | str,
        tempo_limite: int | None = None,
        aguardar_estabilidade: bool = True,
    ) -> Path:
        """
        Aguarda até que o arquivo exportado seja criado.

        Quando aguardar_estabilidade estiver habilitado, o método também
        verifica se o tamanho do arquivo permaneceu inalterado durante um
        número consecutivo de verificações.

        Args:
            caminho_arquivo (Path | str):
                Caminho completo do arquivo esperado.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o arquivo.
                Quando não informado, utiliza a configuração da instância.

            aguardar_estabilidade (bool):
                Define se o método deve esperar o arquivo terminar de ser
                gravado antes de retorná-lo.

        Returns:
            Path:
                Caminho completo do arquivo criado e validado.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.

            SAPTempoLimiteExportacaoErro:
                Caso o arquivo não seja criado ou não fique estável dentro
                do tempo limite.
        """

        arquivo = Path(
            caminho_arquivo
        )

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_exportacao
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()
        tamanho_anterior: int | None = None
        verificacoes_estaveis = 0

        while time.monotonic() - inicio < limite:
            if not self.arquivo_existe(
                caminho_arquivo=arquivo
            ):
                time.sleep(
                    self.intervalo_verificacao
                )
                continue

            if not aguardar_estabilidade:
                return arquivo

            try:
                tamanho_atual = arquivo.stat().st_size

            except OSError:
                time.sleep(
                    self.intervalo_verificacao
                )
                continue

            if tamanho_atual <= 0:
                tamanho_anterior = tamanho_atual
                verificacoes_estaveis = 0

                time.sleep(
                    self.intervalo_verificacao
                )

                continue

            if tamanho_atual == tamanho_anterior:
                verificacoes_estaveis += 1

            else:
                tamanho_anterior = tamanho_atual
                verificacoes_estaveis = 0

            if (
                verificacoes_estaveis
                >= self.quantidade_verificacoes_estabilidade
            ):
                return arquivo

            time.sleep(
                self.intervalo_verificacao
            )

        if arquivo.exists():
            mensagem = (
                "O arquivo foi localizado, mas não ficou estável dentro "
                f"de {limite} segundos: {arquivo}"
            )

        else:
            mensagem = (
                "O arquivo exportado não foi localizado dentro de "
                f"{limite} segundos: {arquivo}"
            )

        raise SAPTempoLimiteExportacaoErro(
            mensagem
        )

    # =========================================================================
    # EXPORTAÇÃO PELA JANELA DE SALVAMENTO
    # =========================================================================

    def exportar_por_janela_salvamento(
        self,
        session: Any,
        caminho_diretorio: Path | str,
        nome_arquivo: str,
        substituir_arquivo: bool = True,
        remover_arquivo_anterior: bool = True,
        aguardar_criacao: bool = True,
        aguardar_estabilidade: bool = True,
        tempo_limite: int | None = None,
        id_campo_diretorio: str = ID_CAMPO_DIRETORIO_PADRAO,
        id_campo_nome_arquivo: str = ID_CAMPO_NOME_ARQUIVO_PADRAO,
        id_botao_salvar: str = ID_BOTAO_SALVAR_PADRAO,
        id_botao_substituir: str = ID_BOTAO_SUBSTITUIR_PADRAO,
    ) -> Path:
        """
        Preenche e confirma a janela de salvamento do SAP.

        O método pressupõe que o RPA já executou os passos necessários
        para abrir a janela de salvamento do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            caminho_diretorio (Path | str):
                Diretório onde o arquivo será exportado.

            nome_arquivo (str):
                Nome completo do arquivo, incluindo a extensão.

            substituir_arquivo (bool):
                Define se a confirmação de substituição deve ser tratada.

            remover_arquivo_anterior (bool):
                Define se um arquivo existente deverá ser removido antes
                do início da exportação.

            aguardar_criacao (bool):
                Define se o método deverá aguardar a criação do arquivo.

            aguardar_estabilidade (bool):
                Define se o método deverá aguardar a finalização da
                gravação do arquivo.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o arquivo.
                Quando não informado, utiliza a configuração da instância.

            id_campo_diretorio (str):
                Identificador do campo de diretório no SAP.

            id_campo_nome_arquivo (str):
                Identificador do campo de nome do arquivo no SAP.

            id_botao_salvar (str):
                Identificador do botão de confirmação do salvamento.

            id_botao_substituir (str):
                Identificador do botão de confirmação da substituição.

        Returns:
            Path:
                Caminho completo do arquivo exportado.

        Raises:
            SAPArquivoExistenteErro:
                Caso o arquivo exista, a substituição esteja desabilitada
                ou o arquivo não possa ser removido.

            SAPExportacaoErro:
                Caso ocorra uma falha durante a interação com a janela.

            SAPTempoLimiteExportacaoErro:
                Caso o arquivo não seja criado dentro do tempo limite.
        """

        self.validar_sessao(
            session=session
        )

        caminho_arquivo = self.preparar_caminho_arquivo(
            caminho_diretorio=caminho_diretorio,
            nome_arquivo=nome_arquivo,
            criar_diretorio=True,
        )

        if caminho_arquivo.exists():
            if not substituir_arquivo:
                raise SAPArquivoExistenteErro(
                    "O arquivo de destino já existe e a substituição "
                    f"está desabilitada: {caminho_arquivo}"
                )

            if remover_arquivo_anterior:
                self.remover_arquivo_existente(
                    caminho_arquivo=caminho_arquivo,
                    ignorar_inexistente=True,
                )

        try:
            self.preencher_janela_salvamento(
                session=session,
                caminho_diretorio=caminho_arquivo.parent,
                nome_arquivo=caminho_arquivo.name,
                id_campo_diretorio=id_campo_diretorio,
                id_campo_nome_arquivo=id_campo_nome_arquivo,
            )

            self.confirmar_salvamento(
                session=session,
                id_botao_salvar=id_botao_salvar,
            )

            if (
                substituir_arquivo
                and not remover_arquivo_anterior
            ):
                self.confirmar_substituicao(
                    session=session,
                    id_botao_substituir=id_botao_substituir,
                    obrigatorio=False,
                )

            if not aguardar_criacao:
                return caminho_arquivo

            return self.aguardar_arquivo(
                caminho_arquivo=caminho_arquivo,
                tempo_limite=tempo_limite,
                aguardar_estabilidade=aguardar_estabilidade,
            )

        except (
            SAPArquivoExistenteErro,
            SAPArquivoExportacaoErro,
            SAPTempoLimiteExportacaoErro,
        ):
            raise

        except SAPExportacaoErro:
            raise

        except Exception as erro:
            raise SAPExportacaoErro(
                "Ocorreu um erro inesperado durante a exportação "
                f"do arquivo: {caminho_arquivo}"
            ) from erro

    # =========================================================================
    # EXPORTAÇÃO POR CAMINHO COMPLETO
    # =========================================================================

    def exportar(
        self,
        session: Any,
        caminho_arquivo: Path | str,
        substituir_arquivo: bool = True,
        remover_arquivo_anterior: bool = True,
        aguardar_criacao: bool = True,
        aguardar_estabilidade: bool = True,
        tempo_limite: int | None = None,
        id_campo_diretorio: str = ID_CAMPO_DIRETORIO_PADRAO,
        id_campo_nome_arquivo: str = ID_CAMPO_NOME_ARQUIVO_PADRAO,
        id_botao_salvar: str = ID_BOTAO_SALVAR_PADRAO,
        id_botao_substituir: str = ID_BOTAO_SUBSTITUIR_PADRAO,
    ) -> Path:
        """
        Exporta um arquivo utilizando um caminho completo.

        Este método é um atalho para exportar_por_janela_salvamento(),
        separando automaticamente o diretório e o nome do arquivo.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            caminho_arquivo (Path | str):
                Caminho completo do arquivo que será exportado.

            substituir_arquivo (bool):
                Define se um arquivo existente poderá ser substituído.

            remover_arquivo_anterior (bool):
                Define se o arquivo existente será removido antes da
                exportação.

            aguardar_criacao (bool):
                Define se o método deverá aguardar a criação do arquivo.

            aguardar_estabilidade (bool):
                Define se o método deverá aguardar a finalização da
                gravação do arquivo.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o arquivo.

            id_campo_diretorio (str):
                Identificador do campo de diretório no SAP.

            id_campo_nome_arquivo (str):
                Identificador do campo de nome do arquivo no SAP.

            id_botao_salvar (str):
                Identificador do botão de confirmação do salvamento.

            id_botao_substituir (str):
                Identificador do botão de confirmação da substituição.

        Returns:
            Path:
                Caminho completo do arquivo exportado.

        Raises:
            ValueError:
                Caso o caminho informado não possua um nome de arquivo.

            SAPExportacaoErro:
                Caso ocorra uma falha durante a exportação.
        """

        arquivo = Path(
            caminho_arquivo
        ).expanduser()

        if not arquivo.name:
            raise ValueError(
                "O caminho informado deve possuir um nome de arquivo."
            )

        return self.exportar_por_janela_salvamento(
            session=session,
            caminho_diretorio=arquivo.parent,
            nome_arquivo=arquivo.name,
            substituir_arquivo=substituir_arquivo,
            remover_arquivo_anterior=remover_arquivo_anterior,
            aguardar_criacao=aguardar_criacao,
            aguardar_estabilidade=aguardar_estabilidade,
            tempo_limite=tempo_limite,
            id_campo_diretorio=id_campo_diretorio,
            id_campo_nome_arquivo=id_campo_nome_arquivo,
            id_botao_salvar=id_botao_salvar,
            id_botao_substituir=id_botao_substituir,
        )