import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Consolidador Fluxo de Caixa",
    page_icon="💰",
    layout="centered"
)

def main():
    st.title("💰 Consolidador de Fluxo de Caixa")
    
    st.markdown("""
    Faça upload do arquivo Excel para consolidar receitas e despesas automaticamente.
    
    **Requisitos do arquivo:**
    - Deve conter as abas **'receitas'** e **'despesas'**
    - Os dados devem começar na **linha 7** (célula C7)
    - Serão lidas apenas as **colunas C até Q**
    - **Colunas finais:** Data, Tipo, Cliente, Status, Valor
    """)
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel",
        type=['xlsx', 'xls', 'xlsm'],
        help="Arquivo deve ter abas 'receitas' e 'despesas'"
    )
    
    if uploaded_file is not None:
        if st.button("🔄 Processar Arquivo", type="primary"):
            with st.spinner("Processando arquivo... Aguarde!"):
                try:
                    # Verificar se o arquivo tem as abas necessárias
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_names = excel_file.sheet_names
                    
                    st.write(f"**Abas encontradas:** {', '.join(sheet_names)}")
                    
                    if 'receitas' not in sheet_names or 'despesas' not in sheet_names:
                        st.error("❌ O arquivo deve conter as abas 'receitas' e 'despesas'")
                        return
                    
                    # Definir range de colunas C até Q
                    colunas_range = list(range(2, 17))  # Colunas C (2) até Q (16)
                    
                    # Ler as abas
                    receitas = pd.read_excel(
                        uploaded_file,
                        sheet_name='receitas',
                        skiprows=6,
                        usecols=colunas_range,
                        header=0
                    )
                    
                    despesas = pd.read_excel(
                        uploaded_file,
                        sheet_name='despesas', 
                        skiprows=6,
                        usecols=colunas_range,
                        header=0
                    )
                    
                    # Limpar dados vazios
                    receitas = receitas.dropna(how='all')
                    despesas = despesas.dropna(how='all')
                    
                    # COLUNAS QUE QUEREMOS MANTER
                    colunas_desejadas = ['Data', 'Tipo', 'Cliente', 'Status', 'Valor']
                    
                    # Função para padronizar nomes de colunas
                    def padronizar_colunas(df):
                        # Mapeamento de possíveis nomes de colunas
                        mapeamento_colunas = {
                            'data': 'Data',
                            'data ': 'Data',
                            'data_': 'Data',
                            'cliente': 'Cliente', 
                            'cliente ': 'Cliente',
                            'cliente_': 'Cliente',
                            'status': 'Status',
                            'status ': 'Status',
                            'status_': 'Status',
                            'valor': 'Valor',
                            'valor ': 'Valor',
                            'valor_': 'Valor',
                            'vlr': 'Valor',
                            'vlr ': 'Valor',
                            'vlr_': 'Valor'
                        }
                        
                        # Renomear colunas
                        df = df.rename(columns=mapeamento_colunas)
                        
                        # Manter apenas colunas desejadas (se existirem)
                        colunas_existentes = [col for col in colunas_desejadas if col in df.columns]
                        
                        if colunas_existentes:
                            df = df[colunas_existentes]
                        
                        return df
                    
                    # Aplicar padronização
                    receitas = padronizar_colunas(receitas)
                    despesas = padronizar_colunas(despesas)
                    
                    # Mostrar colunas encontradas
                    st.write(f"**Colunas nas receitas:** {list(receitas.columns)}")
                    st.write(f"**Colunas nas despesas:** {list(despesas.columns)}")
                    
                    # Adicionar coluna de Tipo
                    receitas['Tipo'] = 'Receita'
                    despesas['Tipo'] = 'Despesa'
                    
                    # Consolidar
                    consolidado = pd.concat([receitas, despesas], ignore_index=True)
                    
                    # GARANTIR que temos apenas as colunas desejadas
                    colunas_finais = []
                    for coluna in colunas_desejadas:
                        if coluna in consolidado.columns:
                            colunas_finais.append(coluna)
                    
                    consolidado = consolidado[colunas_finais]
                    
                    # Ordenar colunas na ordem desejada
                    ordem_colunas = [col for col in colunas_desejadas if col in consolidado.columns]
                    consolidado = consolidado[ordem_colunas]
                    
                    # Resultado
                    st.success("✅ Arquivo processado com sucesso!")
                    
                    # Estatísticas
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total de Registros", len(consolidado))
                    col2.metric("Receitas", len(receitas))
                    col3.metric("Despesas", len(despesas))
                    
                    # Informações sobre dados
                    st.write(f"**Colunas mantidas:** {list(consolidado.columns)}")
                    
                    # Preview
                    st.subheader("👀 Preview dos Dados Consolidados")
                    st.dataframe(consolidado.head(10))
                    
                    # Estatísticas dos valores
                    if 'Valor' in consolidado.columns:
                        st.write(f"**💰 Valor total:** R$ {consolidado['Valor'].sum():,.2f}")
                        st.write(f"**📈 Valor médio:** R$ {consolidado['Valor'].mean():,.2f}")
                    
                    # Download
                    csv_data = consolidado.to_csv(index=False, sep=',', encoding='utf-8')
                    st.download_button(
                        label="📥 Baixar CSV Consolidado",
                        data=csv_data,
                        file_name=f"consolidado_fluxo_caixa_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        type="primary"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
    
    else:
        st.info("👆 Faça upload de um arquivo Excel para começar")

if __name__ == "__main__":
    main()
# Rodapé
st.markdown("---")
st.markdown("**Desenvolvido para automatizar o fluxo de caixa** • 📧 Suporte: 51-98147-9517 [jefe.gomes@outlook.com]")