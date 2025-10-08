import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import io
import traceback
import os  # ADICIONE ESTA LINHA
from typing import Tuple, Optional

# Configuração do logging


def setup_logging():
    """Configura o sistema de logging"""
    logger = logging.getLogger('fluxo_caixa')
    logger.setLevel(logging.DEBUG)

    # Evitar duplicação de handlers
    if not logger.handlers:
        # Handler para arquivo
        file_handler = logging.FileHandler('fluxo_caixa.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Handler para stream (console)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        # Formatação
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


# Inicializar logger
logger = setup_logging()

# Configuração da página
st.set_page_config(
    page_title="Consolidador Fluxo de Caixa",
    page_icon="💰",
    layout="centered"
)


class ProcessadorFluxoCaixa:
    """Classe para processamento e consolidação do fluxo de caixa"""

    def __init__(self):
        self.colunas_desejadas = ['Data', 'Categoria',
                                  'Subcategoria', 'Tipo', 'Cliente', 'Valor']
        self.colunas_range = list(range(2, 17))  # Colunas C até Q
        self.mapeamento_colunas = {
            'data': 'Data', 'data ': 'Data', 'data_': 'Data',
            'cliente': 'Cliente', 'cliente ': 'Cliente', 'cliente_': 'Cliente',
            'fornecedor': 'Cliente', 'fornecedor ': 'Cliente', 'fornecedor_': 'Cliente',
            'valor': 'Valor', 'valor ': 'Valor', 'valor_': 'Valor',
            'vlr': 'Valor', 'vlr ': 'Valor', 'vlr_': 'Valor',
            'categoria': 'Categoria', 'categoria ': 'Categoria', 'categoria_': 'Categoria',
            'cat': 'Categoria', 'cat ': 'Categoria', 'cat_': 'Categoria',
            'subcategoria': 'Subcategoria', 'subcategoria ': 'Subcategoria', 'subcategoria_': 'Subcategoria',
            'subcat': 'Subcategoria', 'subcat ': 'Subcategoria', 'subcat_': 'Subcategoria',
            'sub': 'Subcategoria', 'sub ': 'Subcategoria', 'sub_': 'Subcategoria'
        }

    def validar_arquivo(self, uploaded_file) -> Tuple[bool, str]:
        """Valida se o arquivo atende aos requisitos"""
        try:
            logger.info("Iniciando validação do arquivo")

            if uploaded_file is None:
                return False, "Nenhum arquivo selecionado"

            # Verificar extensão do arquivo
            allowed_extensions = ['.xlsx', '.xls', '.xlsm']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            if file_extension not in allowed_extensions:
                logger.error(f"Extensão não permitida: {file_extension}")
                return False, f"Tipo de arquivo não suportado. Use .xlsx, .xls ou .xlsm. Arquivo enviado: {uploaded_file.name}"

            # Verificar abas necessárias
            try:
                # Garantir que estamos no início do arquivo
                uploaded_file.seek(0)
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                logger.info(f"Abas encontradas: {sheet_names}")
            except Exception as e:
                logger.error(f"Erro ao ler arquivo Excel: {str(e)}")
                return False, f"Erro ao ler arquivo Excel. Certifique-se de que é um arquivo Excel válido: {str(e)}"

            if 'receitas' not in sheet_names or 'despesas' not in sheet_names:
                logger.error(
                    f"Abas necessárias não encontradas. Abas: {sheet_names}")
                return False, "O arquivo deve conter as abas 'receitas' e 'despesas'"

            logger.info("Validação do arquivo concluída com sucesso")
            return True, "Arquivo válido"

        except Exception as e:
            logger.error(f"Erro na validação do arquivo: {str(e)}")
            return False, f"Erro na validação: {str(e)}"

    def padronizar_colunas(self, df: pd.DataFrame, eh_despesa: bool = False) -> pd.DataFrame:
        """Padroniza os nomes das colunas do DataFrame"""
        try:
            logger.info("Iniciando padronização de colunas")

            # Fazer cópia para evitar modificações no original
            df = df.copy()

            # Renomear colunas baseado no mapeamento
            df = df.rename(columns=lambda x: self.mapeamento_colunas.get(
                str(x).lower().strip(), x))

            # Tratamento específico para despesas
            if eh_despesa:
                if 'Fornecedor' in df.columns:
                    df = df.rename(columns={'Fornecedor': 'Cliente'})
                    logger.info("Coluna 'Fornecedor' renomeada para 'Cliente'")

            logger.info(f"Colunas após padronização: {list(df.columns)}")
            return df

        except Exception as e:
            logger.error(f"Erro na padronização de colunas: {str(e)}")
            raise

    def processar_aba(self, uploaded_file, sheet_name: str) -> pd.DataFrame:
        """Processa uma aba específica do arquivo Excel"""
        try:
            logger.info(f"Processando aba: {sheet_name}")

            # Voltar ao início do arquivo para leitura
            uploaded_file.seek(0)

            df = pd.read_excel(
                uploaded_file,
                sheet_name=sheet_name,
                skiprows=6,
                usecols=self.colunas_range,
                header=0,
                dtype={'Valor': float, 'Data': 'object'}  # Tipos esperados
            )

            # Limpar dados vazios
            df = df.dropna(how='all')
            logger.info(f"Aba {sheet_name} processada - {len(df)} registros")

            return df

        except Exception as e:
            logger.error(f"Erro ao processar aba {sheet_name}: {str(e)}")
            raise

    def consolidar_dados(self, receitas: pd.DataFrame, despesas: pd.DataFrame) -> pd.DataFrame:
        """Consolida receitas e despesas em um único DataFrame"""
        try:
            logger.info("Iniciando consolidação de dados")

            # Adicionar coluna de Tipo
            receitas['Tipo'] = 'Receita'
            despesas['Tipo'] = 'Despesa'

            # Consolidar
            consolidado = pd.concat([receitas, despesas], ignore_index=True)

            # Selecionar apenas colunas desejadas
            colunas_finais = [
                col for col in self.colunas_desejadas if col in consolidado.columns]
            consolidado = consolidado[colunas_finais]

            # Ordenar colunas
            ordem_colunas = [
                col for col in self.colunas_desejadas if col in consolidado.columns]
            consolidado = consolidado[ordem_colunas]

            # Limpeza final de dados
            consolidado = consolidado.dropna(subset=['Valor'], how='all')

            logger.info(
                f"Consolidação concluída - Total: {len(consolidado)} registros")
            return consolidado

        except Exception as e:
            logger.error(f"Erro na consolidação: {str(e)}")
            raise

    def calcular_estatisticas(self, consolidado: pd.DataFrame) -> dict:
        """Calcula estatísticas financeiras"""
        try:
            logger.info("Calculando estatísticas")

            stats = {}

            if 'Valor' in consolidado.columns:
                stats['total_receitas'] = consolidado[consolidado['Tipo']
                                                      == 'Receita']['Valor'].sum()
                stats['total_despesas'] = consolidado[consolidado['Tipo']
                                                      == 'Despesa']['Valor'].sum()
                stats['saldo'] = stats['total_receitas'] - \
                    stats['total_despesas']
                stats['total_registros'] = len(consolidado)
                stats['qtd_receitas'] = len(
                    consolidado[consolidado['Tipo'] == 'Receita'])
                stats['qtd_despesas'] = len(
                    consolidado[consolidado['Tipo'] == 'Despesa'])

            logger.info(f"Estatísticas calculadas: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Erro no cálculo de estatísticas: {str(e)}")
            return {}

    def listar_logs_disponiveis(self):
        """Lista todos os arquivos de log disponíveis"""
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                return []

            logs = []
            for filename in sorted(os.listdir(log_dir)):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    stat = os.stat(filepath)
                    tamanho_kb = stat.st_size / 1024
                    criacao_time = datetime.fromtimestamp(stat.st_ctime)

                    logs.append({
                        'nome': filename,
                        'caminho': filepath,
                        'tamanho_kb': round(tamanho_kb, 2),
                        'criado_em': criacao_time.strftime('%d/%m/%Y %H:%M:%S')
                    })

            return logs

        except Exception as e:
            logger.error(f"Erro ao listar logs: {str(e)}")
            return []


def mostrar_erro_detalhado(exception: Exception):
    """Exibe erro detalhado na interface"""
    error_msg = str(exception)
    st.error(f"❌ Erro ao processar o arquivo: {error_msg}")

    # Expandir para detalhes técnicos
    with st.expander("🔍 Detalhes técnicos do erro (para suporte)"):
        st.code(f"""
        Tipo do erro: {type(exception).__name__}
        Mensagem: {error_msg}
        Traceback completo:
        {traceback.format_exc()}
        """)

    st.info("💡 **Dicas para resolver:**\n"
            "- Verifique se as abas 'receitas' e 'despesas' existem\n"
            "- Confirme que os dados começam na linha 7\n"
            "- Verifique os nomes das colunas nas abas\n"
            "- Certifique-se de que não há fórmulas quebradas no Excel")


def main():
    st.title("💰 Consolidador de Fluxo de Caixa")

    st.markdown("""
    Faça upload do arquivo Excel para consolidar receitas e despesas automaticamente.
    
    **Requisitos do arquivo:**
    - Deve conter as abas **'receitas'** e **'despesas'**
    - Os dados devem começar na **linha 7** (célula C7)
    - Serão lidas apenas as **colunas C até Q**
    - **Colunas finais:** Data, Categoria, Subcategoria, Tipo, Cliente, Valor
    """)

    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel",
        type=['xlsx', 'xls', 'xlsm'],
        help="Arquivo deve ter abas 'receitas' e 'despesas'"
    )

    # Inicializar processador
    processador = ProcessadorFluxoCaixa()

    if uploaded_file is not None:
        # Validação inicial
        is_valid, valid_msg = processador.validar_arquivo(uploaded_file)

        if not is_valid:
            st.error(f"❌ {valid_msg}")
            return

        st.success(f"✅ {valid_msg}")

        if st.button("🔄 Processar Arquivo", type="primary"):
            with st.spinner("Processando arquivo... Aguarde!"):
                try:
                    logger.info("=== INÍCIO DO PROCESSAMENTO ===")

                    # Processar abas
                    receitas = processador.processar_aba(
                        uploaded_file, 'receitas')
                    despesas = processador.processar_aba(
                        uploaded_file, 'despesas')

                    # Padronizar colunas
                    receitas = processador.padronizar_colunas(
                        receitas, eh_despesa=False)
                    despesas = processador.padronizar_colunas(
                        despesas, eh_despesa=True)

                    # Mostrar informações das colunas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**📊 Colunas nas receitas:**")
                        st.write(list(receitas.columns))
                    with col2:
                        st.write("**📊 Colunas nas despesas:**")
                        st.write(list(despesas.columns))

                    # Consolidar dados
                    consolidado = processador.consolidar_dados(
                        receitas, despesas)

                    # Calcular estatísticas
                    stats = processador.calcular_estatisticas(consolidado)

                    # Resultado
                    st.success("✅ Arquivo processado com sucesso!")

                    # Estatísticas básicas
                    col1, col2, col3 = st.columns(3)
                    col1.metric("📈 Total de Registros",
                                stats.get('total_registros', 0))
                    col2.metric("💰 Receitas", stats.get('qtd_receitas', 0))
                    col3.metric("💸 Despesas", stats.get('qtd_despesas', 0))

                    # Informações sobre dados
                    st.write(
                        f"**🎯 Colunas mantidas:** {list(consolidado.columns)}")

                    # Preview
                    st.subheader("👀 Preview dos Dados Consolidados")
                    st.dataframe(consolidado.head(
                        10), use_container_width=True)

                    # Resumo financeiro
                    if stats:
                        st.subheader("📊 Resumo Financeiro")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("💰 Total Receitas",
                                    f"R$ {stats['total_receitas']:,.2f}")
                        col2.metric("💸 Total Despesas",
                                    f"R$ {stats['total_despesas']:,.2f}")

                        saldo_color = "normal" if stats['saldo'] >= 0 else "inverse"
                        col3.metric("⚖️ Saldo", f"R$ {stats['saldo']:,.2f}",
                                    delta=f"R$ {stats['saldo']:,.2f}",
                                    delta_color=saldo_color)

                    # Download
                    csv_data = consolidado.to_csv(
                        index=False, sep=',', encoding='utf-8')
                    st.download_button(
                        label="📥 Baixar CSV Consolidado",
                        data=csv_data,
                        file_name=f"consolidado_fluxo_caixa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        type="primary"
                    )

                    # Log de sucesso
                    logger.info("=== PROCESSAMENTO CONCLUÍDO COM SUCESSO ===")

                except Exception as e:
                    logger.error(f"=== ERRO NO PROCESSAMENTO: {str(e)} ===")
                    logger.error(traceback.format_exc())
                    mostrar_erro_detalhado(e)

    else:
        st.info("👆 Faça upload de um arquivo Excel para começar")

    st.markdown("---")
    st.subheader("📋 Gerenciamento de Logs")

    processador = ProcessadorFluxoCaixa()
    logs = processador.listar_logs_disponiveis()

    if logs:
        st.write(f"**Logs encontrados:** {len(logs)} arquivos")

        # Tabela com informações dos logs
        log_data = []
        for log in logs:
            log_data.append({
                'Arquivo': log['nome'],
                'Tamanho (KB)': log['tamanho_kb'],
                'Criado em': log['criado_em']
            })

        df_logs = pd.DataFrame(log_data)
        st.dataframe(df_logs, use_container_width=True)

        # Selecionar log para visualizar
        log_options = [log['nome'] for log in logs]
        log_selecionado = st.selectbox(
            "Selecione um log para visualizar:", log_options)

        if log_selecionado:
            log_path = os.path.join("logs", log_selecionado)
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    conteudo_log = f.read()

                with st.expander(f"📄 Conteúdo do log: {log_selecionado}"):
                    st.text_area("Log content", conteudo_log, height=300)

                # Botão para download do log
                st.download_button(
                    label=f"📥 Baixar {log_selecionado}",
                    data=conteudo_log,
                    file_name=log_selecionado,
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Erro ao ler log: {str(e)}")
    else:
        st.info(
            "Nenhum arquivo de log encontrado. Os logs serão criados automaticamente durante o processamento.")

    # ... resto do código ...


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Erro crítico na aplicação: {str(e)}")
        logger.critical(traceback.format_exc())
        st.error(
            "❌ Ocorreu um erro crítico na aplicação. Verifique os logs para detalhes.")

    # Rodapé
    st.markdown("---")
    st.markdown(
        "**Desenvolvido para automatizar o fluxo de caixa** • 📧 Suporte: 51-98147-9517 [jefe.gomes@outlook.com]")
