import streamlit as st
import pandas as pd
import datetime
import locale
from dateutil.relativedelta import relativedelta

def home():
    col1, col2, col3 = st.columns([2,5,2])
    with col2:
        st.markdown('---')
        st.subheader('BEM VINDO A PEDIDOS')
        st.text('SELECIONE UMA DAS OPCOES AO LADO')
        st.markdown('---')

def pegarelatorios():
    st.markdown('---')
    st.subheader('ATUALIZA PLANILHA PEDIDOS')
    st.text('ANEXE OS ARQUIVOS ABAIXO')
    st.markdown('---')

    with st.expander('IMPORTAR PLANILHAS PARA ATUALIZAR ESTOQUE E VENDAS', expanded=True):
        # Primeiro uploader sempre visível
        arq_estoque = st.file_uploader("Escolha o arquivo estoque:", type=["csv", "txt", "xlsx", "xls"], help=None)
        if arq_estoque is not None:
            st.success("Arquivo estoque carregado com sucesso!")
            st.session_state.df_estoque = pd.read_excel(arq_estoque)
            
            # Segundo uploader só aparece após o primeiro ser carregado
            arq_codigobarras = st.file_uploader("Escolha o arquivo de codigo de barras:", type=["csv", "txt", "xlsx","xls"], help=None)
            if arq_codigobarras is not None:
                st.success("Arquivo código de barras carregado com sucesso!")
                st.session_state.df_codigo_barras = pd.read_excel(arq_codigobarras)
                
                # Terceiro uploader só aparece após o segundo ser carregado
                arq_venda_mes_atual = st.file_uploader("Escolha o arquivo venda do mes atual:", type=["csv", "txt", "xlsx", "xls"], help=None)
                if arq_venda_mes_atual is not None:
                    st.success("Arquivo venda mês atual carregado com sucesso!")
                    st.session_state.df_venda_mes_atual = pd.read_excel(arq_venda_mes_atual)
                    
                    # Quarto uploader só aparece após o terceiro ser carregado
                    arq_venda_penultimo_mes = st.file_uploader("Escolha o arquivo venda do penultimo mes", type=["csv", "txt", "xlsx", "xls"], help=None)
                    if arq_venda_penultimo_mes is not None:
                        st.success("Arquivo venda penúltimo mês carregado com sucesso!")
                        st.session_state.df_venda_penultimo_mes = pd.read_excel(arq_venda_penultimo_mes)
                        
                        # Quinto uploader só aparece após o quarto ser carregado
                        arq_venda_ultimo_mes = st.file_uploader("Escolha o arquivo venda do ultimo mes", type=["csv", "txt", "xlsx", "xls"], help=None)
                        if arq_venda_ultimo_mes is not None:
                            st.success("Arquivo venda último mês carregado com sucesso!")
                            st.session_state.df_venda_ultimo_mes = pd.read_excel(arq_venda_ultimo_mes)
                            return True
    
    return False

@st.cache_data(ttl=3600)
def processa_dados(estoque, codigo_barras, venda_mes_atual, venda_ultimo_mes, venda_penultimo_mes):
    try:
        #locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        mes = datetime.datetime.now()
        atual_mes = mes.strftime("%B").upper()
        ultimo_mes = mes - relativedelta(months=1)
        penultimo_mes = mes - relativedelta(months=2)

        # Processamento do estoque
        excluir_colunas = ['Preço Venda','Total Venda','Custo c/ Imposto','Custo s/ Imposto','Total Custo c/ Imposto','Total Custo s/ Imposto','Curva']
        estoque = estoque.drop(columns=excluir_colunas)
        
        # Loop para copiar valores de células ímpares para células pares
        for i in range(0, len(estoque)-1, 2):
            valor_atual = estoque.iloc[i, 0]
            estoque.iloc[i + 1, 0] = valor_atual
        
        estoque = estoque.dropna()
        coluna = 'Produto'
        inicio = 0
        fim = 6
        nova_coluna = 'Cod Externo'
        estoque[nova_coluna] = estoque[coluna].str.slice(start=inicio, stop=fim)
        estoque[coluna] = estoque[coluna].str.slice(8)
        estoque['Cod Externo'] = estoque['Cod Externo'].astype(int)
        estoque = estoque.rename(columns={'Produto' : 'Descricao'})

        # Processamento das vendas
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        
        # Processamento venda atual
        venda_atual = venda_mes_atual.drop(columns=excluir_colunas)
        venda_atual = venda_atual.drop('Motivo Cancelamento', axis=1)
        venda_atual = venda_atual.dropna(subset=['Produto'])
        venda_atual['Produto'] = venda_atual['Produto'].astype(int)
        venda_gerada1 = venda_atual.groupby('Produto')['Quantidade'].sum().reset_index()
        venda_gerada1 = venda_gerada1.rename(columns={'Quantidade': atual_mes})

        # Processamento venda último mês
        venda_ultimo_mes = venda_ultimo_mes.drop(columns=excluir_colunas)
        venda_ultimo_mes = venda_ultimo_mes.drop('Motivo Cancelamento', axis=1)
        venda_ultimo_mes = venda_ultimo_mes.dropna(subset=['Produto'])
        venda_ultimo_mes['Produto'] = venda_ultimo_mes['Produto'].astype(int)
        venda_gerada2 = venda_ultimo_mes.groupby('Produto')['Quantidade'].sum().reset_index()
        venda_gerada2 = venda_gerada2.rename(columns={'Quantidade': ultimo_mes.strftime("%B").upper()})

        # Processamento venda penúltimo mês
        venda_penultimo_mes = venda_penultimo_mes.drop(columns=excluir_colunas)
        venda_penultimo_mes = venda_penultimo_mes.drop('Motivo Cancelamento', axis=1)
        venda_penultimo_mes = venda_penultimo_mes.dropna(subset=['Produto'])
        venda_penultimo_mes['Produto'] = venda_penultimo_mes['Produto'].astype(int)
        venda_gerada3 = venda_penultimo_mes.groupby('Produto')['Quantidade'].sum().reset_index()
        venda_gerada3 = venda_gerada3.rename(columns={'Quantidade': penultimo_mes.strftime("%B").upper()})

        # Processamento código de barras
        excluir_colunas = ['Unnamed: 0','Preço Atual','Preço Dia Seg.','Preço Lote','Custo c/ Imposto','Custo s/ Imposto','Mrg Líquida','Mrg Bruta','Mrg Sb Custo','Mrg Sb Venda','Mrg Mínima','Mrg Máxima','Familia','Nome','Comprador','Nome Comprador']
        barras = codigo_barras.drop(columns=excluir_colunas)

        # Merge dos dataframes
        venda_1_2 = pd.merge(venda_gerada1, venda_gerada2, on='Produto', how='inner')
        venda_1_2_3 = pd.merge(venda_1_2, venda_gerada3, on='Produto', how='inner')

        banco = pd.merge(estoque, venda_1_2_3, left_on='Cod Externo', right_on='Produto')
        banco = banco.drop(columns=['Embalagem','Produto'])
        banco = banco.rename(columns={'Quantidade' : 'Venda'})

        relatorio_mirandopolis = pd.merge(banco, barras, left_on='Cod Externo', right_on='Produto')
        relatorio_mirandopolis = relatorio_mirandopolis.drop(columns=['Produto','Descrição'])

        # Reorganização das colunas
        move_coluna = 'Cod Externo'
        nova_posicao = 0
        colunas = relatorio_mirandopolis.columns.tolist()
        colunas.remove(move_coluna)
        colunas.insert(nova_posicao, move_coluna)
        relatorio_mirandopolis = relatorio_mirandopolis[colunas]

        return relatorio_mirandopolis
    except Exception as e:
        st.error(f'Erro ao processar dados: {str(e)}')
        return None

def pedido():
    st.subheader('RELATORIO DE PRODUTOS PARA FORMULAR O PEDIDO')
    st.markdown('---')

    if st.session_state.get("limpar_pedido_clicked", False):
        st.session_state.pedidos = pd.DataFrame(columns=['Código Barras', 'Descricao', 'Qtde'])
        st.session_state.limpar_pedido_clicked = False
        st.rerun()
        return

    # Verifica se os dataframes necessários foram carregados
    if not all(key in st.session_state for key in ['df_estoque', 'df_codigo_barras', 'df_venda_mes_atual', 'df_venda_ultimo_mes', 'df_venda_penultimo_mes']):
        st.warning('⚠️ Por favor, carregue os arquivos necessários na seção ATUALIZAR primeiro.')
        st.info('Você precisa carregar os seguintes arquivos:')
        st.markdown("""
        - Arquivo de estoque  
        - Arquivo de código de barras  
        - Arquivo de venda do mês atual  
        - Arquivo de venda do último mês  
        - Arquivo de venda do penúltimo mês  
        """)
        return

    with st.spinner('Processando as planilhas anexadas...'):
        # Processa os dados
        relatorio = processa_dados(
            estoque=st.session_state.df_estoque,
            codigo_barras=st.session_state.df_codigo_barras,
            venda_mes_atual=st.session_state.df_venda_mes_atual,
            venda_ultimo_mes=st.session_state.df_venda_ultimo_mes,
            venda_penultimo_mes=st.session_state.df_venda_penultimo_mes
        )

        if relatorio is None:
            st.error('❌ Erro ao processar os dados. Verifique se todos os arquivos foram carregados corretamente.')
            return

        # Adiciona colunas de controle
        relatorio['Comprar?'] = False
        relatorio['Qtde'] = ''

    st.success(f'✅ Total de produtos carregados: {len(relatorio)}')

    # Campo de busca
    busca = st.text_input('🔍 Buscar produto:', key='busca_produto')
    if busca:
        relatorio = relatorio[relatorio['Descricao'].str.contains(busca, case=False, na=False)]
        st.info(f'📊 Produtos encontrados: {len(relatorio)}')

    # Reorganiza colunas
    colunas = relatorio.columns.tolist()
    for col, pos in [('Código Barras', 1), ('Comprar?', 2), ('Qtde', 3)]:
        if col in colunas:
            colunas.remove(col)
            colunas.insert(pos, col)
    relatorio = relatorio[colunas]

    # Editor com checkbox e campo de quantidade editável
    edited_df = st.data_editor(
        relatorio,
        hide_index=True,
        key="editor_mirandopolis",
        column_config={
            "Comprar?": st.column_config.CheckboxColumn(
                "Comprar?",
                help="Selecione para adicionar ao pedido",
                default=False,
            ),
            "Descricao": st.column_config.TextColumn("Descricao", disabled=True),
            "Qtde": st.column_config.TextColumn("Qtde Pedida")
        },
        use_container_width=True
    )

    # Filtra itens marcados com quantidade válida
    pedido_final = edited_df[(edited_df['Comprar?'] == True) & (edited_df['Qtde'].astype(str).str.strip() != "")]
    pedido_final = pedido_final[['Código Barras', 'Descricao', 'Qtde']].copy().reset_index(drop=True)

    # Se ainda não existe o pedido, cria o DataFrame vazio
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = pd.DataFrame(columns=['Código Barras', 'Descricao', 'Qtde'])

    # Botão para limpar pedido
    col1, col2 = st.columns([4, 2])
    with col1:
        st.subheader('🛒 Itens Selecionados para Compra')
    with col2:
        if st.button("🧹 Limpar pedido", use_container_width=True):
            st.session_state.limpar_pedido_clicked = True
            st.rerun()
            return

    # Junta com o pedido já existente, evitando duplicatas
    pedido_existente = st.session_state.pedidos
    pedido_completo = pd.concat([pedido_existente, pedido_final], ignore_index=True)
    pedido_completo.drop_duplicates(subset='Código Barras', keep='last', inplace=True)
    st.session_state.pedidos = pedido_completo

    # Exibe a tabela somente se houver itens
    if not st.session_state.pedidos.empty:
        st.data_editor(
            st.session_state.pedidos,
            hide_index=True,
            use_container_width=True,
            key="editor_pedido_mirandopolis_final",
            column_config={
                "Descricao": st.column_config.TextColumn("Descricao", disabled=True),
                "Qtde": st.column_config.NumberColumn("Qtde", min_value=0, step=1)
            }
        )
        def salvar_excel_local(df, nome_arquivo="pedido.xlsx"):
            caminho = os.path.join("temp", nome_arquivo)
            os.makedirs("temp", exist_ok=True)
            df.to_excel(caminho, index=False)
            return caminho

        # Gerar o arquivo Excel e exibir botão de download
        if not st.session_state.pedidos.empty:
            caminho_excel = salvar_excel_local(st.session_state.pedidos)

            with open(caminho_excel, "rb") as f:
                st.download_button(
                    label="📥 Baixar Pedido em Excel",
                    data=f,
                    file_name="pedido.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

@st.cache_data(ttl=3600)  # Cache por 1 hora
def processar_dados_mirandopolis(estoque, codigo_barras, venda_mes_atual, venda_ultimo_mes, venda_penultimo_mes):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        mes = datetime.datetime.now()
        atual_mes = mes.strftime("%B").upper()
        ultimo_mes = mes - relativedelta(months=1)
        penultimo_mes = mes - relativedelta(months=2)

        # Processamento do estoque
        excluir_colunas = ['Preço Venda','Total Venda','Custo c/ Imposto','Custo s/ Imposto','Total Custo c/ Imposto','Total Custo s/ Imposto','Curva']
        estoque = estoque.drop(columns=excluir_colunas)
        
        # Loop para copiar valores de células ímpares para células pares
        for i in range(0, len(estoque)-1, 2):
            valor_atual = estoque.iloc[i, 0]
            estoque.iloc[i + 1, 0] = valor_atual
        
        estoque = estoque.dropna()
        coluna = 'Produto'
        inicio = 0
        fim = 6
        nova_coluna = 'Cod Externo'
        estoque[nova_coluna] = estoque[coluna].str.slice(start=inicio, stop=fim)
        estoque[coluna] = estoque[coluna].str.slice(8)
        estoque['Cod Externo'] = estoque['Cod Externo'].astype(int)
        estoque = estoque.rename(columns={'Produto' : 'Descricao'})

        # Processamento das vendas
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        
        # Processamento venda atual
        venda_atual = venda_mes_atual.drop(columns=excluir_colunas)
        venda_atual = venda_atual.drop('Motivo Cancelamento', axis=1)
        venda_atual = venda_atual.dropna(subset=['Produto'])
        venda_atual['Produto'] = venda_atual['Produto'].astype(int)
        venda_gerada1 = venda_atual.groupby('Produto')['Quantidade'].sum().reset_index()
        venda_gerada1 = venda_gerada1.rename(columns={'Quantidade': atual_mes})

        # Processamento venda último mês
        venda_ultimo_mes = venda_ultimo_mes.drop(columns=excluir_colunas)
        venda_ultimo_mes = venda_ultimo_mes.drop('Motivo Cancelamento', axis=1)
        venda_ultimo_mes = venda_ultimo_mes.dropna(subset=['Produto'])
        venda_ultimo_mes['Produto'] = venda_ultimo_mes['Produto'].astype(int)
        venda_gerada2 = venda_ultimo_mes.groupby('Produto')['Quantidade'].sum().reset_index()
        venda_gerada2 = venda_gerada2.rename(columns={'Quantidade': ultimo_mes.strftime("%B").upper()})

        # Processamento venda penúltimo mês
        venda_penultimo_mes = venda_penultimo_mes.drop(columns=excluir_colunas)
        venda_penultimo_mes = venda_penultimo_mes.drop('Motivo Cancelamento', axis=1)
        venda_penultimo_mes = venda_penultimo_mes.dropna(subset=['Produto'])
        venda_penultimo_mes['Produto'] = venda_penultimo_mes['Produto'].astype(int)
        venda_gerada3 = venda_penultimo_mes.groupby('Produto')['Quantidade'].sum().reset_index()
        venda_gerada3 = venda_gerada3.rename(columns={'Quantidade': penultimo_mes.strftime("%B").upper()})

        # Processamento código de barras
        excluir_colunas = ['Unnamed: 0','Preço Atual','Preço Dia Seg.','Preço Lote','Custo c/ Imposto','Custo s/ Imposto','Mrg Líquida','Mrg Bruta','Mrg Sb Custo','Mrg Sb Venda','Mrg Mínima','Mrg Máxima','Familia','Nome','Comprador','Nome Comprador']
        barras = codigo_barras.drop(columns=excluir_colunas)

        # Merge dos dataframes
        venda_1_2 = pd.merge(venda_gerada1, venda_gerada2, on='Produto', how='inner')
        venda_1_2_3 = pd.merge(venda_1_2, venda_gerada3, on='Produto', how='inner')

        banco = pd.merge(estoque, venda_1_2_3, left_on='Cod Externo', right_on='Produto')
        banco = banco.drop(columns=['Embalagem','Produto'])
        banco = banco.rename(columns={'Quantidade' : 'Venda'})

        relatorio_mirandopolis = pd.merge(banco, barras, left_on='Cod Externo', right_on='Produto')
        relatorio_mirandopolis = relatorio_mirandopolis.drop(columns=['Produto','Descrição'])

        # Reorganização das colunas
        move_coluna = 'Cod Externo'
        nova_posicao = 0
        colunas = relatorio_mirandopolis.columns.tolist()
        colunas.remove(move_coluna)
        colunas.insert(nova_posicao, move_coluna)
        relatorio_mirandopolis = relatorio_mirandopolis[colunas]

        return relatorio_mirandopolis
    except Exception as e:
        st.error(f'Erro ao processar dados: {str(e)}')
        return None

def loja_mirandopolis():
    st.subheader('EM BREVE RELATORIO COM OS DADDOS')
    st.subheader('DAS DUAS LOJAS JUNTAS')
    st.markdown('---')

def main():
    
    st.sidebar.subheader('PEDIDOS VERSAO 2.0')
    st.sidebar.markdown('---')
    lista_menu = ['HOME','ATUALIZAR','PEDIDO','LOJA JUNTAS']
    escolha = st.sidebar.radio('Escolha a opcao:', lista_menu)

    if escolha == 'HOME':
        home()
    if escolha == 'ATUALIZAR':
        pegarelatorios()
    if escolha == 'PEDIDO':
        pedido()
    if escolha == 'LOJA JUNTAS':
        loja_mirandopolis()
    

main()

