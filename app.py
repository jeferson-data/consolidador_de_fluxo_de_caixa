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
    - **Colunas finais:** Data, Categoria, Tipo, Cliente, Valor
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
                        st.error(
                            "❌ O arquivo deve conter as abas 'receitas' e 'despesas'")
                        return

                    # Definir range de colunas C até Q
                    # Colunas C (2) até Q (16)
                    colunas_range = list(range(2, 17))

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

                    # COLUNAS QUE QUEREMOS MANTER - SEM STATUS
                    colunas_desejadas = [
                        'Data', 'Categoria', 'Tipo', 'Cliente', 'Valor']

                    # Função para padronizar nomes de colunas
                    def padronizar_colunas(df, eh_despesa=False):
                        # Mapeamento de possíveis nomes de colunas
                        mapeamento_colunas = {
                            'data': 'Data',
                            'data ': 'Data',
                            'data_': 'Data',
                            'cliente': 'Cliente',
                            'cliente ': 'Cliente',
                            'cliente_': 'Cliente',
                            'fornecedor': 'Cliente',  # FORNECEDOR vira CLIENTE
                            'fornecedor ': 'Cliente',
                            'fornecedor_': 'Cliente',
                            'valor': 'Valor',
                            'valor ': 'Valor',
                            'valor_': 'Valor',
                            'vlr': 'Valor',
                            'vlr ': 'Valor',
                            'vlr_': 'Valor',
                            'categoria': 'Categoria',
                            'categoria ': 'Categoria',
                            'categoria_': 'Categoria',
                            'cat': 'Categoria',
                            'cat ': 'Categoria',
                            'cat_': 'Categoria'
                        }

                        # Renomear colunas
                        df = df.rename(columns=mapeamento_colunas)

                        # Se for despesa e tiver coluna 'Fornecedor', renomear para 'Cliente'
                        if eh_despesa and 'Fornecedor' in df.columns:
                            df = df.rename(columns={'Fornecedor': 'Cliente'})
                            st.write(
                                "✅ Coluna 'Fornecedor' renomeada para 'Cliente' nas despesas")

                        return df

                    # Aplicar padronização
                    receitas = padronizar_colunas(receitas, eh_despesa=False)
                    despesas = padronizar_colunas(despesas, eh_despesa=True)

                    # Mostrar colunas encontradas
                    st.write(
                        f"**Colunas nas receitas:** {list(receitas.columns)}")
                    st.write(
                        f"**Colunas nas despesas:** {list(despesas.columns)}")

                    # Adicionar coluna de Tipo
                    receitas['Tipo'] = 'Receita'
                    despesas['Tipo'] = 'Despesa'

                    # Consolidar
                    consolidado = pd.concat(
                        [receitas, despesas], ignore_index=True)

                    # GARANTIR que temos apenas as colunas desejadas (SEM STATUS)
                    colunas_finais = []
                    for coluna in colunas_desejadas:
                        if coluna in consolidado.columns:
                            colunas_finais.append(coluna)

                    consolidado = consolidado[colunas_finais]

                    # Ordenar colunas na ordem desejada
                    ordem_colunas = [
                        col for col in colunas_desejadas if col in consolidado.columns]
                    consolidado = consolidado[ordem_colunas]

                    # Resultado
                    st.success("✅ Arquivo processado com sucesso!")

                    # Estatísticas
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total de Registros", len(consolidado))
                    col2.metric("Receitas", len(receitas))
                    col3.metric("Despesas", len(despesas))

                    # Informações sobre dados
                    st.write(
                        f"**🎯 Colunas mantidas:** {list(consolidado.columns)}")

                    # Preview
                    st.subheader("👀 Preview dos Dados Consolidados")
                    st.dataframe(consolidado.head(10))

                    # Estatísticas dos valores
                    if 'Valor' in consolidado.columns:
                        total_receitas = consolidado[consolidado['Tipo'] == 'Receita']['Valor'].sum(
                        )
                        total_despesas = consolidado[consolidado['Tipo'] == 'Despesa']['Valor'].sum(
                        )
                        saldo = total_receitas - total_despesas

                        st.subheader("📊 Resumo Financeiro")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("💰 Total Receitas",
                                    f"R$ {total_receitas:,.2f}")
                        col2.metric("💸 Total Despesas",
                                    f"R$ {total_despesas:,.2f}")
                        col3.metric("⚖️ Saldo", f"R$ {saldo:,.2f}",
                                    delta=f"R$ {saldo:,.2f}",
                                    delta_color="normal" if saldo >= 0 else "inverse")

                    # Download
                    csv_data = consolidado.to_csv(
                        index=False, sep=',', encoding='utf-8')
                    st.download_button(
                        label="📥 Baixar CSV Consolidado",
                        data=csv_data,
                        file_name=f"consolidado_fluxo_caixa_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        type="primary"
                    )

                    # Botão para novo processamento
                    if st.button("🔄 Processar Outro Arquivo"):
                        st.experimental_rerun()

                except Exception as e:
                    st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
                    st.info(
                        "💡 **Dica:** Verifique se os nomes das colunas estão corretos nas abas.")

    else:
        st.info("👆 Faça upload de um arquivo Excel para começar")


if __name__ == "__main__":
    main()
    # Rodapé
    st.markdown("---")
    st.markdown(
        "**Desenvolvido para automatizar o fluxo de caixa** • 📧 Suporte: 51-98147-9517 [jefe.gomes@outlook.com]")
