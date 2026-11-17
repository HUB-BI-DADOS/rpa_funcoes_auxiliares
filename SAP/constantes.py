"""
===============================================================================
Módulo: constantes.py

Descrição:
    Centraliza as constantes utilizadas pelos módulos de automação SAP.

    Este módulo contém configurações fixas relacionadas ao SAP Logon,
    SAP GUI Scripting, conexões, tempos de espera, intervalos de verificação,
    títulos de janelas, mensagens de segurança e identificadores comuns.

    A centralização dessas informações evita valores duplicados nos módulos
    da biblioteca e facilita alterações futuras, como mudança do caminho do
    executável, nome da conexão SAP ou configuração dos tempos de espera.

    Este módulo não deve conter regras de negócio, funções de automação ou
    credenciais de acesso.

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

from pathlib import Path
from typing import Final


# =============================================================================
# CAMINHOS DO SAP
# =============================================================================

SAP_CAMINHO_EXECUTAVEL: Final[Path] = Path(
    r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe"
)


# =============================================================================
# CONEXÕES SAP
# =============================================================================

SAP_CONEXAO_PRODUCAO_CLARO: Final[str] = (
    "001 - SAP S/4 HANA - PRODUÇÃO CLARO - CLIQUE AQUI"
)


# =============================================================================
# SAP GUI SCRIPTING
# =============================================================================

SAP_OBJETO_GUI: Final[str] = "SAPGUI"


# =============================================================================
# TEMPOS LIMITES
# =============================================================================

SAP_TEMPO_LIMITE_ABERTURA: Final[int] = 30
SAP_TEMPO_LIMITE_CONEXAO: Final[int] = 60
SAP_TEMPO_LIMITE_SESSAO: Final[int] = 60
SAP_TEMPO_LIMITE_POPUPS: Final[int] = 60


# =============================================================================
# INTERVALOS DE VERIFICAÇÃO
# =============================================================================

SAP_INTERVALO_VERIFICACAO: Final[float] = 1.0
SAP_INTERVALO_POPUPS: Final[float] = 0.5
SAP_INTERVALO_APOS_CLIQUE: Final[float] = 0.5


# =============================================================================
# ÍNDICES PADRÕES
# =============================================================================

SAP_INDICE_CONEXAO_PADRAO: Final[int] = 0
SAP_INDICE_SESSAO_PADRAO: Final[int] = 0


# =============================================================================
# CONFIGURAÇÕES DAS JANELAS
# =============================================================================

SAP_TITULO_JANELA_LOGON: Final[str] = r".*SAP Logon.*"
SAP_BACKEND_AUTOMACAO: Final[str] = "uia"
SAP_TITULO_BOTAO_CONFIRMAR: Final[str] = "OK"
SAP_TIPO_CONTROLE_BOTAO: Final[str] = "Button"
SAP_TIPO_CONTROLE_TEXTO: Final[str] = "Text"


# =============================================================================
# MENSAGENS DE SEGURANÇA
# =============================================================================

SAP_MENSAGENS_SEGURANCA: Final[tuple[str, ...]] = (
    "um script está abrindo uma conexão",
    "um script esta abrindo uma conexao",
    "um script está tentando acessar sap gui",
    "um script esta tentando acessar sap gui",
)


# =============================================================================
# CONFIGURAÇÕES DA THREAD DE POPUPS
# =============================================================================

SAP_NOME_THREAD_POPUPS: Final[str] = (
    "monitor-popups-seguranca-sap"
)

SAP_TEMPO_LIMITE_ENCERRAMENTO_THREAD: Final[int] = 2


# =============================================================================
# IDENTIFICADORES COMUNS DO SAP GUI
# =============================================================================

SAP_ID_JANELA_PRINCIPAL: Final[str] = "wnd[0]"
SAP_ID_JANELA_SECUNDARIA: Final[str] = "wnd[1]"

SAP_ID_CAMPO_TRANSACAO: Final[str] = (
    "wnd[0]/tbar[0]/okcd"
)

SAP_ID_BARRA_STATUS: Final[str] = (
    "wnd[0]/sbar"
)


# =============================================================================
# IDENTIFICADORES DA TELA DE LOGIN
# =============================================================================

SAP_ID_CAMPO_MANDANTE: Final[str] = (
    "wnd[0]/usr/txtRSYST-MANDT"
)

SAP_ID_CAMPO_USUARIO: Final[str] = (
    "wnd[0]/usr/txtRSYST-BNAME"
)

SAP_ID_CAMPO_SENHA: Final[str] = (
    "wnd[0]/usr/pwdRSYST-BCODE"
)

SAP_ID_CAMPO_IDIOMA: Final[str] = (
    "wnd[0]/usr/txtRSYST-LANGU"
)


# =============================================================================
# CONFIGURAÇÕES PADRÕES DE LOGIN
# =============================================================================

SAP_IDIOMA_PADRAO: Final[str] = "PT"


# =============================================================================
# COMANDOS DE NAVEGAÇÃO
# =============================================================================

SAP_COMANDO_NOVA_TRANSACAO: Final[str] = "/n"
SAP_COMANDO_NOVA_SESSAO: Final[str] = "/o"
SAP_COMANDO_ENCERRAR_SESSAO: Final[str] = "/i"
SAP_COMANDO_ENCERRAR_SISTEMA: Final[str] = "/nex"


# =============================================================================
# TECLAS DO SAP GUI
# =============================================================================

SAP_TECLA_ENTER: Final[int] = 0
SAP_TECLA_F2: Final[int] = 2
SAP_TECLA_F3: Final[int] = 3
SAP_TECLA_F4: Final[int] = 4
SAP_TECLA_F8: Final[int] = 8
SAP_TECLA_F12: Final[int] = 12


# =============================================================================
# SELEÇÃO MÚLTIPLA
# =============================================================================

SAP_ID_BOTAO_COLAR_SELECAO: Final[str] = (
    "wnd[1]/tbar[0]/btn[24]"
)

SAP_ID_BOTAO_CONFIRMAR_SELECAO: Final[str] = (
    "wnd[1]/tbar[0]/btn[8]"
)

SAP_ID_BOTAO_LIMPAR_SELECAO: Final[str] = (
    "wnd[1]/tbar[0]/btn[16]"
)


# =============================================================================
# TIPOS DE MENSAGEM DA BARRA DE STATUS
# =============================================================================

SAP_TIPO_MENSAGEM_SUCESSO: Final[str] = "S"
SAP_TIPO_MENSAGEM_INFORMACAO: Final[str] = "I"
SAP_TIPO_MENSAGEM_AVISO: Final[str] = "W"
SAP_TIPO_MENSAGEM_ERRO: Final[str] = "E"
SAP_TIPO_MENSAGEM_CANCELAMENTO: Final[str] = "A"


# =============================================================================
# CODIFICAÇÕES E SEPARADORES
# =============================================================================

SAP_SEPARADOR_VALORES_CLIPBOARD: Final[str] = "\r\n"