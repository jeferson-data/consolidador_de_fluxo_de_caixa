import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(
    page_title="Consolidador Fluxo de Caixa",
    page_icon="💰",
    layout="centered"
)

# CSS para melhorar a aparência
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .upload-box {
        border: 2px dashed #1f77b4;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">💰 Consolidador de Fluxo de Caixa</h1>', unsafe_allow_html=True)

st.write("""
### 📁 Faça upload do arquivo Excel para consolidar receitas e despesas

**Requisitos do arquivo:**
- Deve conter as abas **'receitas'** e **'despesas'**
- Os dados devem começar na **linha 7** (célula C7)
- Serão lidas apenas as **colunas C até Q**
- Formatos suportados: .xlsx, .xls, .xlsm
""")

# Upload do arquivo
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Arraste e solte ou clique para escolher o arquivo",
    type=['xlsx', 'xls', 'xlsm'],
    key="file_uploader"
)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    # Mostrar informações do arquivo
    file_details = {
        "Nome do arquivo": uploaded_file.name,
        "Tipo do arquivo": uploaded_file.type,
        "Tamanho": f"{uploaded_file.size / 1024:.2f} KB"
    }
    
    st.write("**📋 Informações do arquivo:**")
    for key, value in file_details.items():
        st.write(f"- {key}: {value}")
    
    # Processar o arquivo
    if st.button("🔄 Processar Arquivo", type="primary"):
        with st.spinner("Processando arquivo... Aguarde!"):
            try:
                # Verificar se as abas existem
                excel_file = pd.ExcelFile(uploaded_file)
                abas_disponiveis = excel_file.sheet_names
                
                st.write(f"**📑 Abas encontradas:** {', '.join(abas_disponiveis)}")
                
                if 'receitas' not in abas_disponiveis or 'despesas' not in abas_disponiveis:
                    st.error("❌ **Erro:** O arquivo deve conter as abas 'receitas' e 'despesas'")
                    st.info("👉 Abas disponíveis no seu arquivo: " + ", ".join(abas_disponiveis))
                else:
                    # LER APENAS COLUNAS C ATÉ Q (usando usecols e skiprows)
                    # C = coluna 2 (zero-index), Q = coluna 16 (zero-index)
                    # Linha 7 = skip 6 linhas
                    
                    # Definir range de colunas C até Q (índices 2 a 16)
                    colunas_range = range(2, 17)  # C até Q (2 a 16 em zero-index)
                    
                    # Ler as abas com range específico
                    receitas = pd.read_excel(
                        uploaded_file, 
                        sheet_name='receitas',
                        skiprows=6,  # Pula até a linha 7
                        usecols=colunas_range,  # Apenas colunas C até Q
                        header=0  # A primeira linha após o skip será o header
                    )
                    
                    despesas = pd.read_excel(
                        uploaded_file, 
                        sheet_name='despesas',
                        skiprows=6,  # Pula até a linha 7
                        usecols=colunas_range,  # Apenas colunas C até Q
                        header=0  # A primeira linha após o skip será o header
                    )
                    
                    st.success("✅ **Range de colunas definido: C até Q**")
                    
                    # Limpar dados vazios
                    receitas = receitas.dropna(how='all')
                    despesas = despesas.dropna(how='all')
                    
                    st.write(f"📊 Dados lidos: {len(receitas)} receitas e {len(despesas)} despesas")
                    
                    # LISTA DE COLUNAS PARA REMOVER (caso ainda existam)
                    colunas_para_remover = ['Instruções', 'Unnamed: 1']
                    
                    # REMOVER COLUNAS INDESEJADAS
                    for coluna in colunas_para_remover:
                        if coluna in receitas.columns:
                            receitas = receitas.drop(columns=[coluna])
                            st.write(f"🗑️ Coluna '{coluna}' removida das receitas")
                        if coluna in despesas.columns:
                            despesas = despesas.drop(columns=[coluna])
                            st.write(f"🗑️ Coluna '{coluna}' removida das despesas")
                    
                    # REMOVER QUALQUER COLUNA 'Instruções' (com variações de caso)
                    colunas_instrucoes_receitas = [col for col in receitas.columns if 'instru' in col.lower()]
                    colunas_instrucoes_despesas = [col for col in despesas.columns if 'instru' in col.lower()]
                    
                    if colunas_instrucoes_receitas:
                        receitas = receitas.drop(columns=colunas_instrucoes_receitas)
                        st.write(f"🗑️ Colunas de instruções removidas das receitas: {colunas_instrucoes_receitas}")
                    
                    if colunas_instrucoes_despesas:
                        despesas = despesas.drop(columns=colunas_instrucoes_despesas)
                        st.write(f"🗑️ Colunas de instruções removidas das despesas: {colunas_instrucoes_despesas}")
                    
                    # REMOVER COLUNAS QUE COMEÇAM COM 'Unnamed'
                    colunas_unnamed_receitas = [col for col in receitas.columns if 'Unnamed' in col]
                    colunas_unnamed_despesas = [col for col in despesas.columns if 'Unnamed' in col]
                    
                    if colunas_unnamed_receitas:
                        receitas = receitas.drop(columns=colunas_unnamed_receitas)
                        st.write(f"🗑️ Colunas Unnamed removidas das receitas: {colunas_unnamed_receitas}")
                    
                    if colunas_unnamed_despesas:
                        despesas = despesas.drop(columns=colunas_unnamed_despesas)
                        st.write(f"🗑️ Colunas Unnamed removidas das despesas: {colunas_unnamed_despesas}")
                    
                    # Adicionar coluna de tipo
                    receitas['Tipo'] = 'Receita'
                    despesas['Tipo'] = 'Despesa'
                    
                    # Consolidar os dados
                    consolidado = pd.concat([receitas, despesas], ignore_index=True)
                    
                    # GARANTIR que as colunas indesejadas foram removidas do consolidado
                    for coluna in colunas_para_remover:
                        if coluna in consolidado.columns:
                            consolidado = consolidado.drop(columns=[coluna])
                    
                    # Remover colunas de instruções (case insensitive)
                    colunas_instrucoes_consolidado = [col for col in consolidado.columns if 'instru' in col.lower()]
                    if colunas_instrucoes_consolidado:
                        consolidado = consolidado.drop(columns=colunas_instrucoes_consolidado)
                    
                    # Remover colunas Unnamed
                    colunas_unnamed_consolidado = [col for col in consolidado.columns if 'Unnamed' in col]
                    if colunas_unnamed_consolidado:
                        consolidado = consolidado.drop(columns=colunas_unnamed_consolidado)
                    
                    # Mostrar sucesso
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("✅ **Arquivo processado com sucesso!**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Estatísticas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Total de Registros", len(consolidado))
                    with col2:
                        st.metric("💰 Receitas", len(receitas))
                    with col3:
                        st.metric("💸 Despesas", len(despesas))
                    
                    # Preview dos dados
                    st.subheader("👀 Preview dos Dados Consolidados")
                    st.dataframe(consolidado.head(10), use_container_width=True)
                    
                    # Informações sobre colunas
                    st.subheader("📋 Estrutura dos Dados")
                    st.write(f"**Colunas finais ({len(consolidado.columns)}):** {list(consolidado.columns)}")
                    st.write(f"**Range aplicado:** Colunas C até Q (apenas dados relevantes)")
                    
                    if 'Data' in consolidado.columns:
                        # Tentar converter datas se necessário
                        try:
                            consolidado['Data'] = pd.to_datetime(consolidado['Data'])
                            st.write(f"**Período dos dados:** {consolidado['Data'].min().strftime('%d/%m/%Y')} até {consolidado['Data'].max().strftime('%d/%m/%Y')}")
                        except:
                            st.write(f"**Período dos dados:** {consolidado['Data'].min()} até {consolidado['Data'].max()}")
                    else:
                        st.write("**Período dos dados:** Coluna 'Data' não identificada")
                    
                    # Download do arquivo
                    st.subheader("📥 Download do Arquivo Consolidado")
                    
                    # Converter para CSV
                    csv = consolidado.to_csv(index=False, encoding='utf-8')
                    
                    # Botão de download
                    st.download_button(
                        label="💾 Baixar CSV Consolidado",
                        data=csv,
                        file_name=f"fluxo_caixa_consolidado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        type="primary"
                    )
                    
                    # Botão para processar novo arquivo
                    if st.button("🔄 Processar Outro Arquivo"):
                        st.experimental_rerun()
                        
            except Exception as e:
                st.error(f"❌ **Erro ao processar o arquivo:** {str(e)}")
                st.info("💡 **Dicas para resolver:**")
                st.write("- Verifique se as abas se chamam 'receitas' e 'despesas'")
                st.write("- Confirme se os dados começam na linha 7")
                st.write("- Tente salvar o arquivo como .xlsx se estiver usando .xlsm")

else:
    # Instruções quando não há arquivo
    st.info("""
    **📝 Instruções:**
    1. Clique em **"Browse files"** ou arraste seu arquivo Excel para a área acima
    2. Certifique-se de que o arquivo tem as abas **'receitas'** e **'despesas'**
    3. Clique em **"Processar Arquivo"** para consolidar os dados
    4. Baixe o arquivo CSV resultante
    
    **⚙️ Processamento automático:**
    - Lê apenas as **colunas C até Q**
    - Começa na **linha 7** 
    - Remove colunas desnecessárias
    - Limpa dados vazios
    - Consolida receitas e despesas
    """)

# Rodapé
st.markdown("---")
st.markdown("**Desenvolvido para automatizar o fluxo de caixa** • 📧 Suporte: 51-98147-9517 [jefe.gomes@outlook.com]")