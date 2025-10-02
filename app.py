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
                    
                    # Remover colunas indesejadas
                    colunas_para_remover = ['Instruções', 'Unnamed: 1']
                    for coluna in colunas_para_remover:
                        if coluna in receitas.columns:
                            receitas = receitas.drop(columns=[coluna])
                        if coluna in despesas.columns:
                            despesas = despesas.drop(columns=[coluna])
                    
                    # Remover colunas Unnamed
                    receitas = receitas.loc[:, ~receitas.columns.str.contains('^Unnamed')]
                    despesas = despesas.loc[:, ~despesas.columns.str.contains('^Unnamed')]
                    
                    # Adicionar tipo
                    receitas['Tipo'] = 'Receita'
                    despesas['Tipo'] = 'Despesa'
                    
                    # Consolidar
                    consolidado = pd.concat([receitas, despesas], ignore_index=True)
                    
                    # Remover colunas Unnamed do consolidado
                    consolidado = consolidado.loc[:, ~consolidado.columns.str.contains('^Unnamed')]
                    
                    # Resultado
                    st.success("✅ Arquivo processado com sucesso!")
                    
                    # Estatísticas
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total de Registros", len(consolidado))
                    col2.metric("Receitas", len(receitas))
                    col3.metric("Despesas", len(despesas))
                    
                    # Preview
                    st.subheader("Preview dos Dados")
                    st.dataframe(consolidado.head(10))
                    
                    # Download
                    csv_data = consolidado.to_csv(index=False)
                    st.download_button(
                        label="📥 Baixar CSV Consolidado",
                        data=csv_data,
                        file_name=f"consolidado_fluxo_caixa_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
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