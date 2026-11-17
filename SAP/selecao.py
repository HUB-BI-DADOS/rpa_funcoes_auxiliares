"""
===============================================================================
Módulo: selecao.py

Descrição:
    Responsável por gerenciar seleções simples e múltiplas no SAP GUI.

    Este módulo centraliza operações técnicas reutilizáveis relacionadas ao
    preenchimento de filtros e listas no SAP, incluindo:
        - Validar e normalizar listas de valores;
        - Remover valores vazios;
        - Remover valores duplicados;
        - Converter valores para texto;
        - Copiar valores para a área de transferência;
        - Abrir a janela de seleção múltipla;
        - Colar valores na seleção múltipla;
        - Confirmar a seleção;
        - Limpar valores existentes;
        - Preencher campos simples;
        - Preencher múltiplos valores diretamente na tabela;
        - Aguardar elementos da seleção ficarem disponíveis;
        - Tratar erros durante o preenchimento dos filtros.

    Este módulo não contém regras de negócio específicas do RPA. A obtenção
    dos pedidos, materiais, centros ou outros valores deve ser realizada
    pelo serviço responsável pelo processo.

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

from collections.abc import Iterable
from typing import Any

import pyperclip

from .constantes import (
    SAP_ID_BOTAO_COLAR_SELECAO,
    SAP_ID_BOTAO_CONFIRMAR_SELECAO,
    SAP_ID_BOTAO_LIMPAR_SELECAO,
    SAP_INTERVALO_VERIFICACAO,
    SAP_SEPARADOR_VALORES_CLIPBOARD,
    SAP_TEMPO_LIMITE_SESSAO,
)

from .excecoes import (
    SAPElementoNaoEncontradoErro,
    SAPListaVaziaErro,
    SAPPreenchimentoErro,
    SAPSelecaoErro,
    SAPSelecaoMultiplaErro,
    SAPSessaoInvalidaErro,
    SAPTempoLimiteElementoErro,
)


# =============================================================================
# CLASSE DE SELEÇÃO SAP
# =============================================================================


class SelecaoSAP:
    """
    Gerencia seleções simples e múltiplas em uma sessão SAP.

    A classe fornece métodos reutilizáveis para preencher campos, abrir
    janelas de seleção múltipla, copiar listas para a área de transferência,
    colar valores e confirmar os filtros.

    Attributes:
        tempo_limite_elemento (int):
            Tempo máximo, em segundos, para aguardar um elemento SAP.

        intervalo_verificacao (float):
            Intervalo, em segundos, entre as verificações.

        separador_clipboard (str):
            Texto utilizado para separar os valores copiados para a área
            de transferência.

        id_botao_colar (str):
            Identificador padrão do botão de colar valores.

        id_botao_confirmar (str):
            Identificador padrão do botão de confirmar seleção.

        id_botao_limpar (str):
            Identificador padrão do botão de limpar seleção.
    """

    # =========================================================================
    # INICIALIZAÇÃO
    # =========================================================================

    def __init__(
        self,
        tempo_limite_elemento: int = SAP_TEMPO_LIMITE_SESSAO,
        intervalo_verificacao: float = SAP_INTERVALO_VERIFICACAO,
        separador_clipboard: str = SAP_SEPARADOR_VALORES_CLIPBOARD,
        id_botao_colar: str = SAP_ID_BOTAO_COLAR_SELECAO,
        id_botao_confirmar: str = SAP_ID_BOTAO_CONFIRMAR_SELECAO,
        id_botao_limpar: str = SAP_ID_BOTAO_LIMPAR_SELECAO,
    ) -> None:
        """
        Inicializa o gerenciador de seleções SAP.

        Args:
            tempo_limite_elemento (int):
                Tempo máximo, em segundos, para aguardar um elemento.

            intervalo_verificacao (float):
                Intervalo, em segundos, entre as verificações.

            separador_clipboard (str):
                Separador utilizado entre os valores enviados para a área
                de transferência.

            id_botao_colar (str):
                Identificador padrão do botão de colar valores.

            id_botao_confirmar (str):
                Identificador padrão do botão de confirmar seleção.

            id_botao_limpar (str):
                Identificador padrão do botão de limpar seleção.

        Returns:
            None.

        Raises:
            ValueError:
                Caso o tempo limite, o intervalo, o separador ou algum
                identificador seja inválido.
        """

        if (
            isinstance(tempo_limite_elemento, bool)
            or not isinstance(tempo_limite_elemento, int)
            or tempo_limite_elemento <= 0
        ):
            raise ValueError(
                "O tempo limite do elemento deve ser um número "
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

        if not isinstance(separador_clipboard, str):
            raise ValueError(
                "O separador da área de transferência deve ser uma string."
            )

        if not separador_clipboard:
            raise ValueError(
                "O separador da área de transferência não pode ser vazio."
            )

        identificadores = {
            "id_botao_colar": id_botao_colar,
            "id_botao_confirmar": id_botao_confirmar,
            "id_botao_limpar": id_botao_limpar,
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

        self.tempo_limite_elemento = tempo_limite_elemento

        self.intervalo_verificacao = float(
            intervalo_verificacao
        )

        self.separador_clipboard = separador_clipboard

        self.id_botao_colar = id_botao_colar.strip()
        self.id_botao_confirmar = id_botao_confirmar.strip()
        self.id_botao_limpar = id_botao_limpar.strip()

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

    # =========================================================================
    # VALIDAÇÃO E NORMALIZAÇÃO DOS VALORES
    # =========================================================================

    @staticmethod
    def normalizar_valor(
        valor: Any,
    ) -> str:
        """
        Converte e normaliza um valor para utilização no SAP.

        Args:
            valor (Any):
                Valor que será convertido para texto.

        Returns:
            str:
                Valor convertido para texto e sem espaços no início
                ou no final. Retorna uma string vazia quando o valor
                for None.
        """

        if valor is None:
            return ""

        texto = str(
            valor
        ).strip()

        if texto.lower() in {
            "nan",
            "none",
            "nat",
            "<na>",
        }:
            return ""

        if texto.endswith(".0"):
            parte_numerica = texto[:-2]

            if parte_numerica.isdigit():
                texto = parte_numerica

        return texto

    def normalizar_valores(
        self,
        valores: Iterable[Any],
        remover_duplicados: bool = True,
        remover_vazios: bool = True,
    ) -> list[str]:
        """
        Normaliza uma coleção de valores para utilização no SAP.

        Args:
            valores (Iterable[Any]):
                Coleção contendo os valores que serão normalizados.

            remover_duplicados (bool):
                Define se valores duplicados deverão ser removidos.
                O valor padrão é True.

            remover_vazios (bool):
                Define se os valores vazios deverão ser removidos.
                O valor padrão é True.

        Returns:
            listLista contendo os valores normalizados.

        Raises:
            SAPListaVaziaErro:
                Caso a coleção seja vazia ou nenhum valor válido permaneça
                após a normalização.

            ValueError:
                Caso uma string isolada seja informada no lugar de uma
                coleção de valores.
        """

        if isinstance(valores, (str, bytes)):
            raise ValueError(
                "Informe uma coleção de valores, como list, tuple ou set. "
                "Uma string isolada não é considerada uma lista."
            )

        if valores is None:
            raise SAPListaVaziaErro(
                "A coleção de valores não pode ser None."
            )

        try:
            valores_recebidos = list(
                valores
            )

        except TypeError as erro:
            raise ValueError(
                "O parâmetro valores deve ser uma coleção iterável."
            ) from erro

        if not valores_recebidos:
            raise SAPListaVaziaErro(
                "A lista de valores está vazia."
            )

        valores_normalizados: list[str] = []

        for valor in valores_recebidos:
            texto = self.normalizar_valor(
                valor=valor
            )

            if remover_vazios and not texto:
                continue

            valores_normalizados.append(
                texto
            )

        if remover_duplicados:
            valores_normalizados = list(
                dict.fromkeys(valores_normalizados)
            )

        if not valores_normalizados:
            raise SAPListaVaziaErro(
                "Nenhum valor válido foi encontrado após a normalização."
            )

        return valores_normalizados

    # =========================================================================
    # ÁREA DE TRANSFERÊNCIA
    # =========================================================================

    def preparar_texto_clipboard(
        self,
        valores: Iterable[Any],
        remover_duplicados: bool = True,
        remover_vazios: bool = True,
    ) -> str:
        """
        Prepara os valores para envio à área de transferência.

        Cada valor será separado pelo separador configurado na classe,
        normalmente uma quebra de linha do Windows.

        Args:
            valores (Iterable[Any]):
                Coleção contendo os valores que serão preparados.

            remover_duplicados (bool):
                Define se valores duplicados deverão ser removidos.

            remover_vazios (bool):
                Define se valores vazios deverão ser removidos.

        Returns:
            str:
                Texto contendo os valores separados por quebra de linha.

        Raises:
            SAPListaVaziaErro:
                Caso nenhum valor válido seja encontrado.
        """

        valores_normalizados = self.normalizar_valores(
            valores=valores,
            remover_duplicados=remover_duplicados,
            remover_vazios=remover_vazios,
        )

        return self.separador_clipboard.join(
            valores_normalizados
        )

    def copiar_para_area_transferencia(
        self,
        valores: Iterable[Any],
        remover_duplicados: bool = True,
        remover_vazios: bool = True,
    ) -> int:
        """
        Copia uma coleção de valores para a área de transferência.

        Args:
            valores (Iterable[Any]):
                Coleção contendo os valores que serão copiados.

            remover_duplicados (bool):
                Define se valores duplicados deverão ser removidos.

            remover_vazios (bool):
                Define se valores vazios deverão ser removidos.

        Returns:
            int:
                Quantidade de valores copiados para a área de transferência.

        Raises:
            SAPListaVaziaErro:
                Caso nenhum valor válido seja encontrado.

            SAPSelecaoErro:
                Caso o conteúdo não possa ser copiado.
        """

        valores_normalizados = self.normalizar_valores(
            valores=valores,
            remover_duplicados=remover_duplicados,
            remover_vazios=remover_vazios,
        )

        texto = self.separador_clipboard.join(
            valores_normalizados
        )

        try:
            pyperclip.copy(
                texto
            )

        except Exception as erro:
            raise SAPSelecaoErro(
                "Não foi possível copiar os valores para a área "
                "de transferência."
            ) from erro

        return len(
            valores_normalizados
        )

    @staticmethod
    def limpar_area_transferencia() -> None:
        """
        Limpa o conteúdo atual da área de transferência.

        Returns:
            None.

        Raises:
            SAPSelecaoErro:
                Caso a área de transferência não possa ser limpa.
        """

        try:
            pyperclip.copy("")

        except Exception as erro:
            raise SAPSelecaoErro(
                "Não foi possível limpar a área de transferência."
            ) from erro

    # =========================================================================
    # LOCALIZAÇÃO E ESPERA DE ELEMENTOS
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
                Caso o identificador seja inválido.

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

    def aguardar_elemento(
        self,
        session: Any,
        id_elemento: str,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Aguarda até que um elemento fique disponível na sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_elemento (str):
                Identificador completo do elemento aguardado.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o elemento.
                Quando não informado, utiliza a configuração da instância.

        Returns:
            Any:
                Objeto do elemento SAP encontrado.

        Raises:
            ValueError:
                Caso o tempo limite seja menor ou igual a zero.

            SAPTempoLimiteElementoErro:
                Caso o elemento não fique disponível dentro do tempo
                limite configurado.
        """

        self.validar_sessao(
            session=session
        )

        limite = (
            tempo_limite
            if tempo_limite is not None
            else self.tempo_limite_elemento
        )

        if limite <= 0:
            raise ValueError(
                "O tempo limite deve ser maior que zero."
            )

        inicio = time.monotonic()
        ultimo_erro: Exception | None = None

        while time.monotonic() - inicio < limite:
            try:
                elemento = self.localizar_elemento(
                    session=session,
                    id_elemento=id_elemento,
                    obrigatorio=False,
                )

                if elemento is not None:
                    return elemento

            except Exception as erro:
                ultimo_erro = erro

            time.sleep(
                self.intervalo_verificacao
            )

        raise SAPTempoLimiteElementoErro(
            "O elemento SAP não ficou disponível dentro de "
            f"{limite} segundos: '{id_elemento}'."
        ) from ultimo_erro

    # =========================================================================
    # PREENCHIMENTO DE CAMPOS SIMPLES
    # =========================================================================

    def preencher_campo(
        self,
        session: Any,
        id_campo: str,
        valor: Any,
        aguardar_elemento: bool = True,
        tempo_limite: int | None = None,
    ) -> None:
        """
        Preenche um campo simples da sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_campo (str):
                Identificador completo do campo SAP GUI.

            valor (Any):
                Valor que será inserido no campo.

            aguardar_elemento (bool):
                Define se o método deverá aguardar o campo ficar disponível.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o campo.

        Returns:
            None.

        Raises:
            SAPPreenchimentoErro:
                Caso o campo não possa ser localizado ou preenchido.
        """

        self.validar_sessao(
            session=session
        )

        valor_normalizado = self.normalizar_valor(
            valor=valor
        )

        try:
            if aguardar_elemento:
                campo = self.aguardar_elemento(
                    session=session,
                    id_elemento=id_campo,
                    tempo_limite=tempo_limite,
                )

            else:
                campo = self.localizar_elemento(
                    session=session,
                    id_elemento=id_campo,
                    obrigatorio=True,
                )

            campo.text = valor_normalizado

        except (
            SAPElementoNaoEncontradoErro,
            SAPTempoLimiteElementoErro,
        ) as erro:
            raise SAPPreenchimentoErro(
                "Não foi possível localizar o campo SAP para "
                f"preenchimento: '{id_campo}'."
            ) from erro

        except Exception as erro:
            raise SAPPreenchimentoErro(
                "Não foi possível preencher o campo SAP: "
                f"'{id_campo}'."
            ) from erro

    def limpar_campo(
        self,
        session: Any,
        id_campo: str,
    ) -> None:
        """
        Limpa o conteúdo de um campo simples do SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_campo (str):
                Identificador completo do campo que será limpo.

        Returns:
            None.

        Raises:
            SAPPreenchimentoErro:
                Caso o campo não possa ser localizado ou limpo.
        """

        self.preencher_campo(
            session=session,
            id_campo=id_campo,
            valor="",
            aguardar_elemento=True,
        )

    # =========================================================================
    # INTERAÇÃO COM BOTÕES
    # =========================================================================

    def pressionar_botao(
        self,
        session: Any,
        id_botao: str,
        aguardar_elemento: bool = True,
        tempo_limite: int | None = None,
    ) -> None:
        """
        Pressiona um botão na sessão SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao (str):
                Identificador completo do botão SAP GUI.

            aguardar_elemento (bool):
                Define se o método deverá aguardar o botão ficar disponível.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o botão.

        Returns:
            None.

        Raises:
            SAPSelecaoErro:
                Caso o botão não possa ser localizado ou acionado.
        """

        self.validar_sessao(
            session=session
        )

        try:
            if aguardar_elemento:
                botao = self.aguardar_elemento(
                    session=session,
                    id_elemento=id_botao,
                    tempo_limite=tempo_limite,
                )

            else:
                botao = self.localizar_elemento(
                    session=session,
                    id_elemento=id_botao,
                    obrigatorio=True,
                )

            botao.press()

        except (
            SAPElementoNaoEncontradoErro,
            SAPTempoLimiteElementoErro,
        ) as erro:
            raise SAPSelecaoErro(
                "Não foi possível localizar o botão SAP: "
                f"'{id_botao}'."
            ) from erro

        except Exception as erro:
            raise SAPSelecaoErro(
                "Não foi possível pressionar o botão SAP: "
                f"'{id_botao}'."
            ) from erro

    # =========================================================================
    # SELEÇÃO MÚLTIPLA
    # =========================================================================

    def abrir_selecao_multipla(
        self,
        session: Any,
        id_botao_selecao: str,
        id_botao_colar: str | None = None,
        tempo_limite: int | None = None,
    ) -> Any:
        """
        Abre a janela de seleção múltipla de um campo SAP.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao_selecao (str):
                Identificador do botão de seleção múltipla do campo.

            id_botao_colar (str | None):
                Identificador do botão de colar utilizado para confirmar
                que a janela foi aberta. Quando não informado, utiliza
                o identificador padrão da classe.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar a janela.

        Returns:
            Any:
                Objeto correspondente ao botão de colar valores.

        Raises:
            SAPSelecaoMultiplaErro:
                Caso a janela de seleção múltipla não possa ser aberta.
        """

        id_colar = (
            id_botao_colar.strip()
            if isinstance(id_botao_colar, str) and id_botao_colar.strip()
            else self.id_botao_colar
        )

        try:
            self.pressionar_botao(
                session=session,
                id_botao=id_botao_selecao,
                aguardar_elemento=True,
                tempo_limite=tempo_limite,
            )

            return self.aguardar_elemento(
                session=session,
                id_elemento=id_colar,
                tempo_limite=tempo_limite,
            )

        except Exception as erro:
            raise SAPSelecaoMultiplaErro(
                "Não foi possível abrir a janela de seleção múltipla. "
                f"Botão informado: '{id_botao_selecao}'."
            ) from erro

    def colar_valores(
        self,
        session: Any,
        id_botao_colar: str | None = None,
        tempo_limite: int | None = None,
    ) -> None:
        """
        Cola na seleção múltipla os valores da área de transferência.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao_colar (str | None):
                Identificador do botão de colar. Quando não informado,
                utiliza o identificador padrão da classe.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o botão.

        Returns:
            None.

        Raises:
            SAPSelecaoMultiplaErro:
                Caso os valores não possam ser colados.
        """

        id_colar = (
            id_botao_colar.strip()
            if isinstance(id_botao_colar, str) and id_botao_colar.strip()
            else self.id_botao_colar
        )

        try:
            self.pressionar_botao(
                session=session,
                id_botao=id_colar,
                aguardar_elemento=True,
                tempo_limite=tempo_limite,
            )

        except Exception as erro:
            raise SAPSelecaoMultiplaErro(
                "Não foi possível colar os valores na seleção múltipla."
            ) from erro

    def limpar_selecao_multipla(
        self,
        session: Any,
        id_botao_limpar: str | None = None,
        obrigatorio: bool = False,
        tempo_limite: int | None = None,
    ) -> bool:
        """
        Limpa os valores existentes na janela de seleção múltipla.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao_limpar (str | None):
                Identificador do botão de limpar. Quando não informado,
                utiliza o identificador padrão da classe.

            obrigatorio (bool):
                Define se a ausência do botão deverá gerar uma exceção.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o botão.

        Returns:
            bool:
                True quando o botão de limpeza for acionado.
                False quando o botão não existir e obrigatorio for False.

        Raises:
            SAPSelecaoMultiplaErro:
                Caso a limpeza seja obrigatória e não possa ser realizada.
        """

        id_limpar = (
            id_botao_limpar.strip()
            if isinstance(id_botao_limpar, str) and id_botao_limpar.strip()
            else self.id_botao_limpar
        )

        try:
            botao = self.localizar_elemento(
                session=session,
                id_elemento=id_limpar,
                obrigatorio=False,
            )

            if botao is None:
                if obrigatorio:
                    raise SAPSelecaoMultiplaErro(
                        "O botão de limpar a seleção múltipla "
                        "não foi encontrado."
                    )

                return False

            botao.press()

            return True

        except SAPSelecaoMultiplaErro:
            raise

        except Exception as erro:
            if obrigatorio:
                raise SAPSelecaoMultiplaErro(
                    "Não foi possível limpar a seleção múltipla."
                ) from erro

            return False

    def confirmar_selecao_multipla(
        self,
        session: Any,
        id_botao_confirmar: str | None = None,
        tempo_limite: int | None = None,
    ) -> None:
        """
        Confirma os valores inseridos na janela de seleção múltipla.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            id_botao_confirmar (str | None):
                Identificador do botão de confirmar. Quando não informado,
                utiliza o identificador padrão da classe.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar o botão.

        Returns:
            None.

        Raises:
            SAPSelecaoMultiplaErro:
                Caso a seleção não possa ser confirmada.
        """

        id_confirmar = (
            id_botao_confirmar.strip()
            if (
                isinstance(id_botao_confirmar, str)
                and id_botao_confirmar.strip()
            )
            else self.id_botao_confirmar
        )

        try:
            self.pressionar_botao(
                session=session,
                id_botao=id_confirmar,
                aguardar_elemento=True,
                tempo_limite=tempo_limite,
            )

        except Exception as erro:
            raise SAPSelecaoMultiplaErro(
                "Não foi possível confirmar a seleção múltipla."
            ) from erro

    # =========================================================================
    # MÉTODO PRINCIPAL DE SELEÇÃO MÚLTIPLA
    # =========================================================================

    def preencher_selecao_multipla(
        self,
        session: Any,
        valores: Iterable[Any],
        id_botao_selecao: str,
        limpar_selecao_anterior: bool = False,
        remover_duplicados: bool = True,
        remover_vazios: bool = True,
        limpar_clipboard_ao_final: bool = False,
        tempo_limite: int | None = None,
        id_botao_colar: str | None = None,
        id_botao_limpar: str | None = None,
        id_botao_confirmar: str | None = None,
    ) -> int:
        """
        Preenche e confirma uma seleção múltipla no SAP.

        O fluxo executado pelo método é:
            1. Validar a sessão SAP;
            2. Normalizar os valores;
            3. Copiar os valores para a área de transferência;
            4. Abrir a janela de seleção múltipla;
            5. Limpar os valores existentes, quando solicitado;
            6. Colar os valores;
            7. Confirmar a seleção;
            8. Limpar a área de transferência, quando solicitado.

        Args:
            session (Any):
                Objeto da sessão SAP GUI Scripting.

            valores (Iterable[Any]):
                Coleção contendo os valores que serão inseridos.

            id_botao_selecao (str):
                Identificador do botão que abre a seleção múltipla.

            limpar_selecao_anterior (bool):
                Define se os valores existentes deverão ser removidos
                antes da nova seleção.

            remover_duplicados (bool):
                Define se os valores duplicados deverão ser removidos.

            remover_vazios (bool):
                Define se os valores vazios deverão ser removidos.

            limpar_clipboard_ao_final (bool):
                Define se a área de transferência deverá ser limpa após
                o preenchimento.

            tempo_limite (int | None):
                Tempo máximo, em segundos, para aguardar os elementos.

            id_botao_colar (str | None):
                Identificador personalizado do botão de colar.

            id_botao_limpar (str | None):
                Identificador personalizado do botão de limpar.

            id_botao_confirmar (str | None):
                Identificador personalizado do botão de confirmar.

        Returns:
            int:
                Quantidade de valores inseridos na seleção múltipla.

        Raises:
            SAPListaVaziaErro:
                Caso nenhum valor válido seja informado.

            SAPSelecaoMultiplaErro:
                Caso a janela não possa ser aberta, preenchida ou confirmada.

            SAPSessaoInvalidaErro:
                Caso a sessão SAP não esteja válida.
        """

        self.validar_sessao(
            session=session
        )

        valores_normalizados = self.normalizar_valores(
            valores=valores,
            remover_duplicados=remover_duplicados,
            remover_vazios=remover_vazios,
        )

        try:
            self.copiar_para_area_transferencia(
                valores=valores_normalizados,
                remover_duplicados=False,
                remover_vazios=False,
            )

            self.abrir_selecao_multipla(
                session=session,
                id_botao_selecao=id_botao_selecao,
                id_botao_colar=id_botao_colar,
                tempo_limite=tempo_limite,
            )

            if limpar_selecao_anterior:
                self.limpar_selecao_multipla(
                    session=session,
                    id_botao_limpar=id_botao_limpar,
                    obrigatorio=False,
                    tempo_limite=tempo_limite,
                )

            self.colar_valores(
                session=session,
                id_botao_colar=id_botao_colar,
                tempo_limite=tempo_limite,
            )

            self.confirmar_selecao_multipla(
                session=session,
                id_botao_confirmar=id_botao_confirmar,
                tempo_limite=tempo_limite,
            )

            return len(
                valores_normalizados
            )

        except (
            SAPListaVaziaErro,
            SAPSessaoInvalidaErro,
        ):
            raise

        except SAPSelecaoMultiplaErro:
            raise

        except Exception as erro:
            raise SAPSelecaoMultiplaErro(
                "Ocorreu um erro inesperado durante o preenchimento "
                "da seleção múltipla."
            ) from erro

        finally:
            if limpar_clipboard_ao_final:
                try:
                    self.limpar_area_transferencia()

                except SAPSelecaoErro:
                    pass