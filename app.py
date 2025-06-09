import streamlit as st
import pandas as pd
import datetime
import time
import locale
from dateutil.relativedelta import relativedelta
import os

def home():
    col1, col2, col3 = st.columns([2,5,2])
    with col2:
        st.markdown('---')
        st.subheader('BEM VINDO A PEDIDOS')
        st.text('SELECIONE UMA DAS LOJAS NO MENU AO LADO')
        st.markdown('---')
      
       @st.cache_data(ttl=3600)  # Cache por 1 hora
def processar_dados_mirandopolis():
    try:
        #locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        mes = datetime.datetime.now()
        atual_mes = mes.strftime("%B").upper()
        ultimo_mes = mes - relativedelta(months=1)
        penultimo_mes = mes - relativedelta(months=2)

        # Verifica se os arquivos existem
        arquivos_necessarios = [
            'mirandopolis/estoque.xls',
            'mirandopolis/venda mes atual.xls',
            'mirandopolis/venda ultimo mes.xls',
            'mirandopolis/venda penultimo mes.xls',
            'mirandopolis/codigobarras.xls'
        ]

        for arquivo in arquivos_necessarios:
            if not os.path.exists(arquivo):
                st.error(f'Arquivo não encontrado: {arquivo}')
                return None

        #pegar a planilha estoque ....
        estoque = pd.read_excel('mirandopolis/estoque.xls')
        excluir_colunas = ['Preço Venda','Total Venda','Custo c/ Imposto','Custo s/ Imposto','Total Custo c/ Imposto','Total Custo s/ Imposto','Curva']
        estoque = estoque.drop(columns=excluir_colunas)
        # Loop para copiar valores de células ímpares para células pares
        for i in range(0, len(estoque)-1, 2):
            # Pega o valor da célula atual (ímpar)
            valor_atual = estoque.iloc[i, 0]
            # Copia para a próxima célula (par)
            estoque.iloc[i + 1, 0] = valor_atual
        estoque = estoque.dropna()
        coluna = 'Produto'
        inicio = 0
        fim = 6
        nova_coluna = 'Cod Externo'
        estoque[nova_coluna] = estoque[coluna].str.slice(start=inicio, stop=fim)
        estoque[coluna] = estoque[coluna].str.slice(8)
        # Converte para inteiro
        estoque['Cod Externo'] = estoque['Cod Externo'].astype(int)
        estoque = estoque.rename(columns={'Produto' : 'Descricao'})
        #st.write(estoque)

        #pega as planilhas quantidade de vendas vendas....
        venda_atual = pd.read_excel('mirandopolis/venda mes atual.xls')
        venda_ultimo_mes = pd.read_excel('mirandopolis/venda ultimo mes.xls')
        venda_penultimo_mes = pd.read_excel('mirandopolis/venda penultimo mes.xls')

        #pegando planilha venda atual...
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        venda_atual = venda_atual.drop(columns=excluir_colunas)
        coluna_motivo = 'Motivo Cancelamento'
        excluir_devolucao = 'DEVOLUCAO DE MERCADORIA'
        excluir_erro_registro = 'ERRO DE REGISTRO'
        venda_ultimo_mes = venda_ultimo_mes[
            (venda_ultimo_mes[coluna_motivo] != excluir_devolucao) & 
            (venda_ultimo_mes[coluna_motivo] != excluir_erro_registro)
        ]
        venda_atual = venda_atual.drop('Motivo Cancelamento', axis=1)
        # Remove linhas com valores NA antes de converter para inteiro
        venda_atual = venda_atual.dropna(subset=['Produto'])
        # Converte para inteiro
        venda_atual['Produto'] = venda_atual['Produto'].astype(int)
        coluna_codigo = 'Produto'
        coluna_quatidade = 'Quantidade'
        venda_gerada1 = venda_atual.groupby(coluna_codigo)[coluna_quatidade].sum().reset_index()
        coluna = atual_mes
        venda_gerada1 = venda_gerada1.rename(columns={'Quantidade':coluna})

        #st.write(venda_gerada1)
       
        #pegando venda do ultimo mes....
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        venda_ultimo_mes = venda_ultimo_mes.drop(columns=excluir_colunas)
        coluna_motivo = 'Motivo Cancelamento'
        excluir_devolucao = 'DEVOLUCAO DE MERCADORIA'
        excluir_erro_registro = 'ERRO DE REGISTRO'
        venda_ultimo_mes = venda_ultimo_mes[
            (venda_ultimo_mes[coluna_motivo] != excluir_devolucao) & 
            (venda_ultimo_mes[coluna_motivo] != excluir_erro_registro)
        ]
        venda_ultimo_mes = venda_ultimo_mes.drop('Motivo Cancelamento', axis=1)
        # Remove linhas com valores NA antes de converter para inteiro
        venda_ultimo_mes = venda_ultimo_mes.dropna(subset=['Produto'])
        # Converte para inteiro
        venda_ultimo_mes['Produto'] = venda_ultimo_mes['Produto'].astype(int)
        coluna_codigo = 'Produto'
        coluna_quatidade = 'Quantidade'
        venda_gerada2 = venda_ultimo_mes.groupby(coluna_codigo)[coluna_quatidade].sum().reset_index()
        coluna = ultimo_mes.strftime("%B").upper()
        venda_gerada2 = venda_gerada2.rename(columns={'Quantidade':coluna})

        #st.write(venda_gerada2)
       
        #Pegando planilha de venda do penultimo mes ...
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        venda_penultimo_mes = venda_penultimo_mes.drop(columns=excluir_colunas)
        coluna_motivo = 'Motivo Cancelamento'
        excluir_devolucao = 'DEVOLUCAO DE MERCADORIA'
        excluir_erro_registro = 'ERRO DE REGISTRO'
        venda_penultimo_mes = venda_penultimo_mes[
            (venda_penultimo_mes[coluna_motivo] != excluir_devolucao) & 
            (venda_penultimo_mes[coluna_motivo] != excluir_erro_registro)
        ]
        venda_penultimo_mes = venda_penultimo_mes.drop('Motivo Cancelamento', axis=1)
        # Remove linhas com valores NA antes de converter para inteiro
        venda_penultimo_mes = venda_penultimo_mes.dropna(subset=['Produto'])
        # Converte para inteiro
        venda_penultimo_mes['Produto'] = venda_penultimo_mes['Produto'].astype(int)
        coluna_codigo = 'Produto'
        coluna_quatidade = 'Quantidade'
        venda_gerada3 = venda_penultimo_mes.groupby(coluna_codigo)[coluna_quatidade].sum().reset_index()
        coluna = penultimo_mes.strftime("%B").upper()
        venda_gerada3 = venda_gerada3.rename(columns={'Quantidade':coluna})

        #st.write(venda_gerada3)

        barras = pd.read_excel('mirandopolis/codigobarras.xls')
        excluir_colunas = ['Unnamed: 0','Preço Atual','Preço Dia Seg.','Preço Lote','Custo c/ Imposto','Custo s/ Imposto','Mrg Líquida','Mrg Bruta','Mrg Sb Custo','Mrg Sb Venda','Mrg Mínima','Mrg Máxima','Familia','Nome','Comprador','Nome Comprador']
        barras = barras.drop(columns=excluir_colunas)

        #st.write(barras)

        chave = 'Produto'

        venda_1_2 = pd.merge(venda_gerada1, venda_gerada2, on=chave, how='inner')
        #venda_1_2.to_excel('gerado/venda_1_2.xlsx',index=False)
        venda_1_2_3 = pd.merge(venda_1_2, venda_gerada3, on=chave, how='inner')

        #estoque_novo = pd.read_excel('gerado/estoque_novo.xlsx')
        #venda = pd.read_excel('gerado/venda_nova.xlsx')
        cod_estoque = 'Cod Externo'
        cod_venda = 'Produto'
        banco = pd.merge(estoque, venda_1_2_3, left_on=cod_estoque, right_on=cod_venda)
        excluir_colunas = ['Embalagem','Produto']
        banco = banco.drop(columns=excluir_colunas)
        banco = banco.rename(columns={'Quantidade' : 'Venda'})

        #st.write(banco)

        cod_estoque_venda = 'Cod Externo'
        cod_barras = 'Produto'
        relatorio_mirandopolis = pd.merge(banco, barras, left_on=cod_estoque_venda, right_on=cod_barras)
        excluir_colunas = ['Produto','Descrição']
        relatorio_mirandopolis = relatorio_mirandopolis.drop(columns=excluir_colunas)

        move_coluna = 'Cod Externo'
        nova_posicao = 0
        # Obtém a lista atual de colunas
        colunas = relatorio_mirandopolis.columns.tolist()
        # Remove a coluna da sua posição atual
        colunas.remove(move_coluna)
        # Insere a coluna na nova posição
        colunas.insert(nova_posicao, move_coluna)
        # Reindexa o DataFrame com a nova ordem de colunas
        relatorio_mirandopolis = relatorio_mirandopolis[colunas]

        return relatorio_mirandopolis
    except Exception as e:
        st.error(f'Erro ao processar dados: {str(e)}')
        return None

def loja_mirandopolis():
    st.subheader('LOJA MIRANDOPOLIS')
    st.markdown('---')
    
    # Inicializa o dataframe de pedidos se não existir
    if 'pedido_mirandopolis' not in st.session_state:
        st.session_state.pedido_mirandopolis = pd.DataFrame(columns=['Código Barras', 'Descricao', 'Qtde'])
    
    with st.spinner('Carregando dados da loja Mirandópolis...'):
        relatorio = processar_dados_mirandopolis()
        if relatorio is None:
            st.error('Não foi possível carregar os dados. Verifique se todos os arquivos necessários estão presentes.')
            return
        relatorio['Comprar?'] = False
    
    # Mostra a quantidade de linhas do dataframe
    st.write(f'Total de produtos: {len(relatorio)}')

    # Campo de busca
    busca = st.text_input('Buscar produto:', key='busca_mirandopolis')
    if busca:
        relatorio = relatorio[relatorio['Descricao'].str.contains(busca, case=False, na=False)]
        st.write(f'Produtos encontrados: {len(relatorio)}')

    move_coluna = 'Código Barras'
    nova_posicao = 1
    # Obtém a lista atual de colunas
    colunas = relatorio.columns.tolist()
    # Remove a coluna da sua posição atual
    colunas.remove(move_coluna)
    # Insere a coluna na nova posição
    colunas.insert(nova_posicao, move_coluna)
    relatorio = relatorio[colunas]
    
    # Configura o editor para mostrar checkboxes na coluna 'Comprar?'
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
            "Descricao": st.column_config.TextColumn(
                "Descricao",
                disabled=True
            ),
            
        },
        use_container_width=True
    )
    
    # Atualiza o dataframe de pedidos com os itens selecionados
    novos_pedidos = edited_df[edited_df['Comprar?'] == True][['Código Barras', 'Descricao']]
    novos_pedidos['Qtde'] = ''
    
    # Atualiza o session_state do pedido
    if not novos_pedidos.empty:
        st.session_state.pedido_mirandopolis = pd.concat([st.session_state.pedido_mirandopolis, novos_pedidos]).drop_duplicates(subset=['Código Barras'])
    
    if not st.session_state.pedido_mirandopolis.empty:
        st.subheader('Itens Selecionados para Compra')
        st.data_editor(
            st.session_state.pedido_mirandopolis, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Descricao": st.column_config.TextColumn(
                    "Descricao",
                    disabled=True
                )
            }
        )

@st.cache_data(ttl=3600)  # Cache por 1 hora
def processar_dados_carrao():
    try:
        #locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        mes = datetime.datetime.now()
        atual_mes = mes.strftime("%B").upper()
        ultimo_mes = mes - relativedelta(months=1)
        penultimo_mes = mes - relativedelta(months=2)

        # Verifica se os arquivos existem
        arquivos_necessarios = [
            'carrao/estoque.xls',
            'carrao/venda mes atual.xls',
            'carrao/venda ultimo mes.xls',
            'carrao/venda penultimo mes.xls',
            'carrao/codigobarras.xls'
        ]

        for arquivo in arquivos_necessarios:
            if not os.path.exists(arquivo):
                st.error(f'Arquivo não encontrado: {arquivo}')
                return None

        #pegar a planilha estoque ....
        estoque = pd.read_excel('carrao/estoque.xls')
        excluir_colunas = ['Preço Venda','Total Venda','Custo c/ Imposto','Custo s/ Imposto','Total Custo c/ Imposto','Total Custo s/ Imposto']
        estoque = estoque.drop(columns=excluir_colunas)
        # Loop para copiar valores de células ímpares para células pares
        for i in range(0, len(estoque)-1, 2):
            # Pega o valor da célula atual (ímpar)
            valor_atual = estoque.iloc[i, 0]
            # Copia para a próxima célula (par)
            estoque.iloc[i + 1, 0] = valor_atual
        estoque = estoque.dropna()
        coluna = 'Produto'
        inicio = 0
        fim = 6
        nova_coluna = 'Cod Externo'
        estoque[nova_coluna] = estoque[coluna].str.slice(start=inicio, stop=fim)
        estoque[coluna] = estoque[coluna].str.slice(8)
        # Converte para inteiro
        estoque['Cod Externo'] = estoque['Cod Externo'].astype(int)
        estoque = estoque.rename(columns={'Produto' : 'Descricao'})
        #st.write(estoque)

        #pega as planilhas quantidade de vendas vendas....
        venda_atual = pd.read_excel('carrao/venda mes atual.xls')
        venda_ultimo_mes = pd.read_excel('carrao/venda ultimo mes.xls')
        venda_penultimo_mes = pd.read_excel('carrao/venda penultimo mes.xls')

        #pegando planilha venda atual...
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        venda_atual = venda_atual.drop(columns=excluir_colunas)
        coluna_motivo = 'Motivo Cancelamento'
        excluir_devolucao = 'DEVOLUCAO DE MERCADORIA'
        excluir_erro_registro = 'ERRO DE REGISTRO'
        venda_ultimo_mes = venda_ultimo_mes[
            (venda_ultimo_mes[coluna_motivo] != excluir_devolucao) & 
            (venda_ultimo_mes[coluna_motivo] != excluir_erro_registro)
        ]
        venda_atual = venda_atual.drop('Motivo Cancelamento', axis=1)
        # Remove linhas com valores NA antes de converter para inteiro
        venda_atual = venda_atual.dropna(subset=['Produto'])
        # Converte para inteiro
        venda_atual['Produto'] = venda_atual['Produto'].astype(int)
        coluna_codigo = 'Produto'
        coluna_quatidade = 'Quantidade'
        venda_gerada1 = venda_atual.groupby(coluna_codigo)[coluna_quatidade].sum().reset_index()
        coluna = atual_mes
        venda_gerada1 = venda_gerada1.rename(columns={'Quantidade':coluna})

        #st.write(venda_gerada1)
       
        #pegando venda do ultimo mes....
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        venda_ultimo_mes = venda_ultimo_mes.drop(columns=excluir_colunas)
        coluna_motivo = 'Motivo Cancelamento'
        excluir_devolucao = 'DEVOLUCAO DE MERCADORIA'
        excluir_erro_registro = 'ERRO DE REGISTRO'
        venda_ultimo_mes = venda_ultimo_mes[
            (venda_ultimo_mes[coluna_motivo] != excluir_devolucao) & 
            (venda_ultimo_mes[coluna_motivo] != excluir_erro_registro)
        ]
        venda_ultimo_mes = venda_ultimo_mes.drop('Motivo Cancelamento', axis=1)
        # Remove linhas com valores NA antes de converter para inteiro
        venda_ultimo_mes = venda_ultimo_mes.dropna(subset=['Produto'])
        # Converte para inteiro
        venda_ultimo_mes['Produto'] = venda_ultimo_mes['Produto'].astype(int)
        coluna_codigo = 'Produto'
        coluna_quatidade = 'Quantidade'
        venda_gerada2 = venda_ultimo_mes.groupby(coluna_codigo)[coluna_quatidade].sum().reset_index()
        coluna = ultimo_mes.strftime("%B").upper()
        venda_gerada2 = venda_gerada2.rename(columns={'Quantidade':coluna})

        #st.write(venda_gerada2)
       
        #Pegando planilha de venda do penultimo mes ...
        excluir_colunas = ['Venda Bruta','Preço Venda','Venda Cancelada','Valor Desconto','Venda Líquida','Margem Líquida','Margem Bruta','Margem Sb. Custo','Margem Sb. Venda','Cancelado','Operador','Nome','Motivo Desconto','Participação']
        venda_penultimo_mes = venda_penultimo_mes.drop(columns=excluir_colunas)
        coluna_motivo = 'Motivo Cancelamento'
        excluir_devolucao = 'DEVOLUCAO DE MERCADORIA'
        excluir_erro_registro = 'ERRO DE REGISTRO'
        venda_penultimo_mes = venda_penultimo_mes[
            (venda_penultimo_mes[coluna_motivo] != excluir_devolucao) & 
            (venda_penultimo_mes[coluna_motivo] != excluir_erro_registro)
        ]
        venda_penultimo_mes = venda_penultimo_mes.drop('Motivo Cancelamento', axis=1)
        # Remove linhas com valores NA antes de converter para inteiro
        venda_penultimo_mes = venda_penultimo_mes.dropna(subset=['Produto'])
        # Converte para inteiro
        venda_penultimo_mes['Produto'] = venda_penultimo_mes['Produto'].astype(int)
        coluna_codigo = 'Produto'
        coluna_quatidade = 'Quantidade'
        venda_gerada3 = venda_penultimo_mes.groupby(coluna_codigo)[coluna_quatidade].sum().reset_index()
        coluna = penultimo_mes.strftime("%B").upper()
        venda_gerada3 = venda_gerada3.rename(columns={'Quantidade':coluna})

        #st.write(venda_gerada3)

        barras = pd.read_excel('carrao/codigobarras.xls')
        excluir_colunas = ['Unnamed: 0','Preço Atual','Preço Dia Seg.','Preço Lote','Custo c/ Imposto','Custo s/ Imposto','Mrg Líquida','Mrg Bruta','Mrg Sb Custo','Mrg Sb Venda','Mrg Mínima','Mrg Máxima','Familia','Nome','Comprador','Nome Comprador']
        barras = barras.drop(columns=excluir_colunas)

        #st.write(barras)

        chave = 'Produto'

        venda_1_2 = pd.merge(venda_gerada1, venda_gerada2, on=chave, how='inner')
        #venda_1_2.to_excel('gerado/venda_1_2.xlsx',index=False)
        venda_1_2_3 = pd.merge(venda_1_2, venda_gerada3, on=chave, how='inner')

        #estoque_novo = pd.read_excel('gerado/estoque_novo.xlsx')
        #venda = pd.read_excel('gerado/venda_nova.xlsx')
        cod_estoque = 'Cod Externo'
        cod_venda = 'Produto'
        banco = pd.merge(estoque, venda_1_2_3, left_on=cod_estoque, right_on=cod_venda)
        excluir_colunas = ['Embalagem','Produto']
        banco = banco.drop(columns=excluir_colunas)
        banco = banco.rename(columns={'Quantidade' : 'Venda'})

        #st.write(banco)

        cod_estoque_venda = 'Cod Externo'
        cod_barras = 'Produto'
        relatorio_carrao = pd.merge(banco, barras, left_on=cod_estoque_venda, right_on=cod_barras)
        excluir_colunas = ['Produto','Descrição']
        relatorio_carrao = relatorio_carrao.drop(columns=excluir_colunas)

        move_coluna = 'Cod Externo'
        nova_posicao = 0
        # Obtém a lista atual de colunas
        colunas = relatorio_carrao.columns.tolist()
        # Remove a coluna da sua posição atual
        colunas.remove(move_coluna)
        # Insere a coluna na nova posição
        colunas.insert(nova_posicao, move_coluna)
        # Reindexa o DataFrame com a nova ordem de colunas
        relatorio_carrao = relatorio_carrao[colunas]

        return relatorio_carrao
    except Exception as e:
        st.error(f'Erro ao processar dados: {str(e)}')
        return None

def loja_carrao():
    st.subheader('LOJA CARRAO')
    st.markdown('---')
    
    # Inicializa o dataframe de pedidos se não existir
    if 'pedido_carrao' not in st.session_state:
        st.session_state.pedido_carrao = pd.DataFrame(columns=['Código Barras', 'Descricao', 'Qtde'])
    
    with st.spinner('Carregando dados da loja Carrão...'):    
        relatorio = processar_dados_carrao()
        if relatorio is None:
            st.error('Não foi possível carregar os dados. Verifique se todos os arquivos necessários estão presentes.')
            return
        relatorio['Comprar?'] = False

    # Mostra a quantidade de linhas do dataframe
    st.write(f'Total de produtos: {len(relatorio)}')

    # Campo de busca
    busca = st.text_input('Buscar produto:', key='busca_carrao')
    if busca:
        relatorio = relatorio[relatorio['Descricao'].str.contains(busca, case=False, na=False)]
        st.write(f'Produtos encontrados: {len(relatorio)}')

    move_coluna = 'Código Barras'
    nova_posicao = 1
    # Obtém a lista atual de colunas
    colunas = relatorio.columns.tolist()
    # Remove a coluna da sua posição atual
    colunas.remove(move_coluna)
    # Insere a coluna na nova posição
    colunas.insert(nova_posicao, move_coluna)
    relatorio = relatorio[colunas]
    
    # Configura o editor para mostrar checkboxes na coluna 'Comprar?'
    edited_df = st.data_editor(
        relatorio,
        hide_index=True,
        key="editor_carrao",
        column_config={
            "Comprar?": st.column_config.CheckboxColumn(
                "Comprar?",
                help="Selecione para adicionar ao pedido",
                default=False,
            ),
            "Descricao": st.column_config.TextColumn(
                "Descricao",
                disabled=True
            ),
            
        },
        use_container_width=True
    )
    
    # Atualiza o dataframe de pedidos com os itens selecionados
    novos_pedidos = edited_df[edited_df['Comprar?'] == True][['Código Barras', 'Descricao']]
    novos_pedidos['Qtde'] = ''
    
    # Atualiza o session_state do pedido
    if not novos_pedidos.empty:
        st.session_state.pedido_carrao = pd.concat([st.session_state.pedido_carrao, novos_pedidos]).drop_duplicates(subset=['Código Barras'])
    
    if not st.session_state.pedido_carrao.empty:
        st.subheader('Itens Selecionados para Compra')
        st.data_editor(
            st.session_state.pedido_carrao, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Descricao": st.column_config.TextColumn(
                    "Descricao",
                    disabled=True
                )
            }
        )

def main():
    
    st.sidebar.subheader('PEDIDOS VERSAO 1.0')
    st.sidebar.markdown('---')
    lista_menu = ['HOME','LOJA MIRANDOPOLIS','LOJA CARRAO']
    escolha = st.sidebar.radio('Escolha a opcao:', lista_menu)

    if escolha == 'HOME':
        home()
    if escolha == 'LOJA MIRANDOPOLIS':
        loja_mirandopolis()
    if escolha == 'LOJA CARRAO':
        loja_carrao()
    

main()

