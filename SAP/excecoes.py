"""
===============================================================================
Módulo: excecoes.py

Descrição:
    Centraliza as exceções personalizadas utilizadas pela biblioteca de
    automação SAP.

    Este módulo fornece uma hierarquia padronizada de exceções para facilitar
    a identificação, o tratamento e o registro dos erros que podem ocorrer
    durante as automações.

    As exceções estão organizadas por responsabilidade:
        - Configuração;
        - Inicialização do SAP Logon;
        - SAP GUI Scripting;
        - Conexões;
        - Sessões;
        - Login;
        - Navegação;
        - Elementos;
        - Janelas;
        - Seleções múltiplas;
        - Exportações;
        - Tempos limites.

    Todas as exceções personalizadas herdam de SAPErro, permitindo capturar
    qualquer erro da biblioteca SAP utilizando uma única exceção base.

Autor:
    Tiago Eneas Antunes

Data de criação:
    08/10/2026

Versão:
    1.0.0
===============================================================================
"""

# =============================================================================
# EXCEÇÃO BASE
# =============================================================================


class SAPErro(Exception):
    """
    Exceção base da biblioteca de automação SAP.

    Todas as exceções personalizadas da biblioteca devem herdar desta
    classe. Isso permite capturar qualquer erro relacionado ao SAP por
    meio de uma única exceção.

    Examples:
        Captura genérica de erros da biblioteca:

        ```python
        try:
            executar_automacao()
        except SAPErro as erro:
            print(f"Erro na automação SAP: {erro}")
        ```
    """


# =============================================================================
# EXCEÇÕES DE CONFIGURAÇÃO
# =============================================================================


class SAPConfiguracaoErro(SAPErro):
    """
    Exceção gerada quando uma configuração da biblioteca é inválida.

    Pode ser utilizada para configurações ausentes, valores inválidos,
    caminhos incorretos ou parâmetros incompatíveis.
    """


class SAPCredencialErro(SAPConfiguracaoErro):
    """
    Exceção gerada quando uma credencial SAP não está disponível.

    Pode ser utilizada quando o usuário, a senha, o mandante ou outra
    informação necessária para autenticação não estiver configurada.
    """


# =============================================================================
# EXCEÇÕES DO EXECUTÁVEL E DO SAP LOGON
# =============================================================================


class SAPExecutavelErro(SAPErro):
    """
    Exceção base para erros relacionados ao executável do SAP Logon.
    """


class SAPExecutavelNaoEncontradoErro(SAPExecutavelErro):
    """
    Exceção gerada quando o executável do SAP Logon não é encontrado.

    Essa exceção deve ser utilizada quando o caminho configurado para
    o executável não existir ou não corresponder a um arquivo válido.
    """


class SAPInicializacaoErro(SAPExecutavelErro):
    """
    Exceção gerada quando o SAP Logon não pode ser inicializado.

    Essa exceção pode ocorrer mesmo quando o executável existe, mas o
    sistema operacional não consegue iniciar o processo.
    """


# =============================================================================
# EXCEÇÕES DO SAP GUI SCRIPTING
# =============================================================================


class SAPScriptingErro(SAPErro):
    """
    Exceção gerada quando o SAP GUI Scripting não pode ser acessado.

    Pode indicar que:
        - O SAP Logon não está aberto;
        - O scripting está desabilitado no SAP GUI;
        - O scripting está desabilitado no servidor;
        - O objeto COM do SAP não está disponível;
        - O mecanismo de scripting não respondeu corretamente.
    """


class SAPScriptingDesabilitadoErro(SAPScriptingErro):
    """
    Exceção gerada quando o SAP GUI Scripting está desabilitado.

    A habilitação pode depender das configurações locais do SAP GUI
    ou de configurações administradas pela equipe responsável pelo SAP.
    """


# =============================================================================
# EXCEÇÕES DE CONEXÃO
# =============================================================================


class SAPConexaoErro(SAPErro):
    """
    Exceção base para erros relacionados às conexões SAP.

    Essa exceção deve ser utilizada quando ocorrer uma falha genérica
    ao localizar, abrir, consultar ou reutilizar uma conexão SAP.
    """


class SAPConexaoNaoEncontradaErro(SAPConexaoErro):
    """
    Exceção gerada quando uma conexão SAP não é encontrada.

    Pode ser utilizada quando:
        - O nome informado não existe no SAP Logon;
        - O índice solicitado não existe;
        - Nenhuma conexão está aberta;
        - A conexão foi encerrada durante a execução.
    """


class SAPConexaoAberturaErro(SAPConexaoErro):
    """
    Exceção gerada quando não é possível abrir uma conexão SAP.

    Essa exceção deve ser utilizada quando a chamada responsável por
    abrir a conexão falhar ou não retornar um objeto válido.
    """


# =============================================================================
# EXCEÇÕES DE SESSÃO
# =============================================================================


class SAPSessaoErro(SAPErro):
    """
    Exceção base para erros relacionados às sessões SAP.
    """


class SAPSessaoNaoEncontradaErro(SAPSessaoErro):
    """
    Exceção gerada quando nenhuma sessão SAP válida é encontrada.

    Pode ser utilizada quando:
        - Nenhuma sessão foi criada;
        - O índice solicitado não existe;
        - A sessão foi encerrada;
        - A conexão não possui sessões disponíveis.
    """


class SAPSessaoInvalidaErro(SAPSessaoErro):
    """
    Exceção gerada quando uma sessão SAP não pode mais ser utilizada.

    Uma sessão pode ser considerada inválida quando foi encerrada, perdeu
    a conexão ou não permite acessar os elementos esperados.
    """


class SAPSessaoOcupadaErro(SAPSessaoErro):
    """
    Exceção gerada quando uma sessão SAP está ocupada.

    Pode ser utilizada quando a sessão estiver processando uma operação
    anterior e ainda não estiver disponível para uma nova ação.
    """


# =============================================================================
# EXCEÇÕES DE SEGURANÇA E JANELAS
# =============================================================================


class SAPJanelaErro(SAPErro):
    """
    Exceção base para erros relacionados às janelas do SAP.
    """


class SAPJanelaNaoEncontradaErro(SAPJanelaErro):
    """
    Exceção gerada quando uma janela esperada não é encontrada.

    Pode ser utilizada para janelas principais, secundárias, diálogos,
    avisos de segurança e mensagens de confirmação.
    """


class SAPPopupErro(SAPJanelaErro):
    """
    Exceção gerada quando ocorre uma falha ao tratar um popup do SAP.
    """


class SAPPopupSegurancaErro(SAPPopupErro):
    """
    Exceção gerada quando um aviso de segurança não pode ser tratado.

    Essa exceção pode ser utilizada quando o aviso é identificado, mas
    o botão de confirmação não pode ser localizado ou acionado.
    """


# =============================================================================
# EXCEÇÕES DE LOGIN
# =============================================================================


class SAPLoginErro(SAPErro):
    """
    Exceção base para erros relacionados ao login no SAP.
    """


class SAPTelaLoginNaoEncontradaErro(SAPLoginErro):
    """
    Exceção gerada quando a tela de login não é encontrada.

    Pode indicar que a sessão já está autenticada, que outra janela está
    aberta ou que a conexão ainda não foi totalmente carregada.
    """


class SAPAutenticacaoErro(SAPLoginErro):
    """
    Exceção gerada quando a autenticação no SAP não é concluída.

    Pode ser utilizada em situações como:
        - Usuário inválido;
        - Senha inválida;
        - Senha expirada;
        - Mandante inválido;
        - Acesso bloqueado;
        - Erro retornado pela barra de status.
    """


class SAPMultiplosLoginsErro(SAPLoginErro):
    """
    Exceção gerada quando o SAP identifica múltiplos logins.

    Essa exceção pode ser utilizada quando a janela de múltiplos acessos
    não puder ser tratada automaticamente.
    """


# =============================================================================
# EXCEÇÕES DE NAVEGAÇÃO
# =============================================================================


class SAPNavegacaoErro(SAPErro):
    """
    Exceção base para erros durante a navegação no SAP.
    """


class SAPTransacaoErro(SAPNavegacaoErro):
    """
    Exceção base para erros relacionados às transações SAP.
    """


class SAPTransacaoNaoEncontradaErro(SAPTransacaoErro):
    """
    Exceção gerada quando uma transação SAP não é encontrada.

    Pode ocorrer quando o código informado não existe ou quando o usuário
    não possui acesso à transação solicitada.
    """


class SAPTransacaoAberturaErro(SAPTransacaoErro):
    """
    Exceção gerada quando uma transação não pode ser aberta.
    """


# =============================================================================
# EXCEÇÕES DE ELEMENTOS
# =============================================================================


class SAPElementoErro(SAPErro):
    """
    Exceção base para erros relacionados aos elementos do SAP GUI.
    """


class SAPElementoNaoEncontradoErro(SAPElementoErro):
    """
    Exceção gerada quando um elemento do SAP GUI não é encontrado.

    Pode ser utilizada para campos, botões, tabelas, abas, menus,
    barras de ferramentas e outros componentes da interface.
    """


class SAPElementoIndisponivelErro(SAPElementoErro):
    """
    Exceção gerada quando um elemento é encontrado, mas está indisponível.

    O elemento pode estar invisível, desabilitado ou bloqueado para edição.
    """


class SAPPreenchimentoErro(SAPElementoErro):
    """
    Exceção gerada quando não é possível preencher um campo do SAP.
    """


class SAPCliqueErro(SAPElementoErro):
    """
    Exceção gerada quando não é possível acionar um elemento do SAP.
    """


# =============================================================================
# EXCEÇÕES DE SELEÇÃO MÚLTIPLA
# =============================================================================


class SAPSelecaoErro(SAPErro):
    """
    Exceção base para erros relacionados às seleções do SAP.
    """


class SAPSelecaoMultiplaErro(SAPSelecaoErro):
    """
    Exceção gerada quando uma seleção múltipla não pode ser preenchida.

    Pode ocorrer ao abrir a janela, copiar valores, colar os valores,
    limpar a seleção ou confirmar os dados informados.
    """


class SAPListaVaziaErro(SAPSelecaoErro):
    """
    Exceção gerada quando uma lista de valores está vazia.

    Essa exceção evita abrir a seleção múltipla do SAP sem valores para
    serem inseridos.
    """


# =============================================================================
# EXCEÇÕES DE EXPORTAÇÃO
# =============================================================================


class SAPExportacaoErro(SAPErro):
    """
    Exceção base para erros relacionados às exportações do SAP.
    """


class SAPArquivoExportacaoErro(SAPExportacaoErro):
    """
    Exceção gerada quando o arquivo exportado não é localizado ou criado.
    """


class SAPFormatoExportacaoErro(SAPExportacaoErro):
    """
    Exceção gerada quando o formato solicitado não está disponível.
    """


class SAPArquivoExistenteErro(SAPExportacaoErro):
    """
    Exceção gerada quando o arquivo de destino já existe e não pode
    ser substituído.
    """


# =============================================================================
# EXCEÇÕES DE MENSAGENS DO SAP
# =============================================================================


class SAPMensagemErro(SAPErro):
    """
    Exceção base para erros relacionados às mensagens do SAP.
    """


class SAPMensagemStatusErro(SAPMensagemErro):
    """
    Exceção gerada quando a barra de status apresenta uma mensagem de erro.

    A mensagem exibida pelo SAP pode ser armazenada no texto da exceção
    para facilitar o diagnóstico do problema.
    """


class SAPMensagemCancelamentoErro(SAPMensagemErro):
    """
    Exceção gerada quando o SAP apresenta uma mensagem de cancelamento.
    """


# =============================================================================
# EXCEÇÕES DE TEMPO LIMITE
# =============================================================================


class SAPTempoLimiteErro(SAPErro, TimeoutError):
    """
    Exceção base para operações SAP que ultrapassam o tempo limite.

    Essa exceção também herda de TimeoutError, permitindo que o código
    capture o erro como uma exceção genérica de tempo limite ou como uma
    exceção específica da biblioteca SAP.
    """


class SAPTempoLimiteAberturaErro(SAPTempoLimiteErro):
    """
    Exceção gerada quando o SAP Logon não abre dentro do tempo limite.
    """


class SAPTempoLimiteConexaoErro(SAPTempoLimiteErro):
    """
    Exceção gerada quando a conexão SAP não abre dentro do tempo limite.
    """


class SAPTempoLimiteSessaoErro(SAPTempoLimiteErro):
    """
    Exceção gerada quando uma sessão SAP não fica disponível dentro
    do tempo limite.
    """


class SAPTempoLimiteElementoErro(SAPTempoLimiteErro):
    """
    Exceção gerada quando um elemento não fica disponível dentro
    do tempo limite.
    """


class SAPTempoLimiteExportacaoErro(SAPTempoLimiteErro):
    """
    Exceção gerada quando uma exportação não é concluída dentro
    do tempo limite.
    """