# Funções Auxiliares para RPA

Biblioteca Python com funções reutilizáveis para automações corporativas
(RPA), tratamento de dados e operações com arquivos. O projeto é organizado
por área funcional; cada pasta contém módulos que podem ser importados
individualmente.

## Funcionalidades

| Pasta | Recursos |
| --- | --- |
| `DATAFRAME/` | Validação, limpeza, transformação, datas e exportação de DataFrames pandas. |
| `EXCEL/` | Manipulação de arquivos e planilhas: importação, formatação, fórmulas, tabelas, validações e exportação. |
| `OUTLOOK/` | Automação do Outlook clássico: conexão, e-mails, anexos, calendário, contatos, pastas e regras. |
| `WEB_SCRAPPING_SELENIUM/` | Automação de navegador com Selenium: drivers Chrome/Edge, navegação, elementos, esperas, janelas, capturas e downloads. |
| `DASHBOARD_STREAMLIT/` | Componentes para dashboards Streamlit: configuração, estado, cache, layout, filtros, formulários, métricas, gráficos, tabelas e cartões. |
| `SAP/` | Automação do SAP GUI: conexão, sessões, janelas, login, navegação, seleção e exportação. |
| `BANCO_DE_DADOS/` | Estrutura reservada para módulos relacionados a bancos de dados. |
| `API/`, `ARQUIVOS/` | Estrutura reservada para módulos futuros. |

As pastas reservadas não possuem funcionalidades implementadas no momento.

## Requisitos

- Python 3.10 ou superior.
- Instale somente as dependências necessárias para as áreas utilizadas.
- Outlook e SAP GUI precisam estar instalados e configurados no Windows para
  suas respectivas automações.
- A automação Selenium requer um navegador compatível (Chrome ou Edge).

O arquivo `requirements.txt` ainda não lista dependências. Instale os pacotes
diretamente conforme o módulo que for usar:

| Área | Pacotes Python |
| --- | --- |
| DataFrames e exportação Excel | `pandas`, `openpyxl` |
| Exportação Parquet | `pyarrow` |
| Utilitários Excel | `openpyxl` |
| Dashboard | `streamlit`, `pandas`, `plotly` |
| Selenium | `selenium` |
| Outlook | `pywin32` |
| SAP GUI | `pywin32`, `pywinauto`, `pyperclip` |
| Testes | `pytest` |

Por exemplo, para preparar um ambiente com suporte a DataFrames e Excel:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pandas openpyxl
```

Acrescente os pacotes da tabela acima quando utilizar outras áreas. Para
executar a exportação Parquet, instale também `pyarrow`.

## Utilização

Execute os scripts a partir da raiz do repositório, para que os diretórios
dos módulos estejam disponíveis para importação. Exemplo com as funções de
DataFrame:

```python
import pandas as pd

from DATAFRAME.datas import extrair_ano
from DATAFRAME.exportacao import exportar_excel

dados = pd.DataFrame({"DATA": ["2026-01-15", "2026-02-20"]})
resultado = extrair_ano(dados, "DATA")
exportar_excel(resultado, r"C:\relatorios\resultado.xlsx")
```

As funções validam entradas e podem lançar exceções quando os dados, caminhos
ou configurações são inválidos. Consulte a documentação e as assinaturas no
módulo correspondente antes de usá-las.

## Testes

Os testes existentes ficam junto aos módulos e usam `pytest`. Para executar,
por exemplo, os testes de exportação de DataFrames, entre na pasta do módulo:

```powershell
Set-Location DATAFRAME
python -m pytest teste.py
```

## Boas práticas

- Não armazene credenciais, tokens ou dados sensíveis no código ou no Git.
- Configure acessos e caminhos no ambiente de execução, conforme a automação.
- Verifique as dependências específicas e pré-requisitos do aplicativo antes
  de executar automações de Outlook, SAP ou navegador.
