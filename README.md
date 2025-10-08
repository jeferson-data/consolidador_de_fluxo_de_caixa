💰 Consolidador de Fluxo de Caixa


Sistema automatizado para consolidar e analisar dados de fluxo de caixa a partir de planilhas Excel, com interface web intuitiva e recursos avançados de logging.

✨ Funcionalidades Principais
📤 Upload Inteligente - Suporte para planilhas Excel (.xlsx, .xls, .xlsm)

🔄 Processamento Automático - Consolidação automática de receitas e despesas

📊 Dashboard Interativo - Métricas financeiras em tempo real

📈 Análise Financeira - Saldo, totais e estatísticas detalhadas

📥 Exportação Flexível - Download em CSV formatado

📋 Sistema de Logging - Monitoramento completo e troubleshooting

🎯 Validação Robusta - Verificação de formato e estrutura de dados

🚀 Começando Rápido
Método 1: Executador Automático (Windows)
bash
# Clique duplo no arquivo:
executar.bat
Método 2: Execução Manual
bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar aplicação
streamlit run app.py

# 3. Acessar no navegador
# http://localhost:8501
Método 3: Ambiente Virtual (Recomendado)
bash
# Criar ambiente
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Mac/Linux)
source venv/bin/activate

# Instalar e executar
pip install -r requirements.txt
streamlit run app.py
📋 Pré-requisitos
Python 3.8+ Download aqui

Planilha Excel com formato específico (veja abaixo)

📊 Formato da Planilha Excel
✅ Estrutura Obrigatória
Requisito	Valor
Abas necessárias	receitas e despesas
Início dos dados	Linha 7 (célula C7)
Colunas lidas	C até Q (C, D, E, ..., Q)
Formato suportado	.xlsx, .xls, .xlsm
🎯 Colunas Esperadas
excel
| Data       | Categoria | Subcategoria | Tipo      | Cliente/Fornecedor | Valor    |
|------------|-----------|--------------|-----------|-------------------|----------|
| 2024-01-15 | Vendas    | Produto A    | Receita   | Cliente X         | 1500.00  |
| 2024-01-16 | Materiais | Escritório   | Despesa   | Fornecedor Y      | 250.50   |
📝 Exemplo de Estrutura
text
Planilha Excel
├── 📊 receitas (aba)
│   └── Dados a partir da linha 7, colunas C-Q
├── 📊 despesas (aba)  
│   └── Dados a partir da linha 7, colunas C-Q
└── ... outras abas (ignoradas)
🏗️ Estrutura do Projeto
text
consolidador_fluxo_caixa/
├── 📄 app.py                 # Aplicação principal Streamlit
├── ⚙️ executar.bat           # Executador automático Windows
├── 📋 requirements.txt       # Dependências do projeto
├── 📁 .streamlit/
│   └── ⚙️ config.toml       # Configurações do Streamlit
├── 📁 logs/                 # Pasta de logs (criada automaticamente)
│   ├── 📄 fluxo_caixa_20241201_143022.log
│   └── 📄 fluxo_caixa_20241201_143523.log
└── 📄 README.md             # Este arquivo
🔧 Configuração
🌐 Acesso Web
Porta padrão: 8501

URL: http://localhost:8501

Host: localhost

📋 Funcionalidades da Interface
Upload de Arquivo

Selecione sua planilha Excel

Validação automática de formato

Processamento

Clique em "Processar Arquivo"

Visualize preview dos dados

Análise

Métricas de receitas e despesas

Saldo financeiro

Estatísticas consolidadas

Exportação

Download em CSV

Logs detalhados

🛠️ Tecnologias Utilizadas
Tecnologia	Versão	Finalidade
Streamlit	≥1.28.0	Interface web
Pandas	≥2.0.0	Processamento de dados
OpenPyXL	≥3.0.0	Leitura de Excel
xlrd	≥2.0.0	Suporte a .xls
❗ Solução de Problemas
🔍 Erros Comuns e Soluções
Erro	Causa	Solução
"Tipo de arquivo não suportado"	Formato incorreto	Use .xlsx, .xls ou .xlsm
"Abas não encontradas"	Nomes diferentes	Renomeie para receitas e despesas
"Erro ao processar"	Estrutura inválida	Verifique linha 7, colunas C-Q
Python não encontrado	PATH incorreto	Reinstale Python marcando "Add to PATH"
📋 Verificação de Logs
bash
# Logs automáticos na pasta:
logs/fluxo_caixa_YYYYMMDD_HHMMSS.log

# Na interface web:
# → Seção "Gerenciamento de Logs"
# → Visualização online
# → Download para análise
🐛 Debug Avançado
Verifique o console onde o Streamlit está rodando

Acesse os logs pela interface web

Confirme o formato da planilha Excel

Teste com dados simples para isolamento do problema

📞 Suporte e Contato
Desenvolvedor: Jeferson Gomes
WhatsApp: 51-98147-9517
Email: jefe.gomes@outlook.com
GitHub: jefeg/consolidador_de_fluxo_de_caixa

🔄 Histórico de Versões
v2.1 (Atual)
✅ Sistema de logging em pasta dedicada

✅ Interface para gerenciamento de logs

✅ Validação melhorada de arquivos

v2.0
✅ Arquitetura orientada a objetos

✅ Tratamento de erros robusto

✅ Padronização de colunas inteligente

v1.0
✅ Funcionalidades básicas de consolidação

✅ Processamento de receitas e despesas

✅ Exportação para CSV

📄 Licença
Projeto desenvolvido para automação de processos financeiros internos.

💡 Dica Profissional: Mantenha uma formatação consistente nas planilhas e evite fórmulas complexas nas colunas de dados para melhor processamento.

⭐ Gostou do projeto? Deixe uma estrela no repositório!