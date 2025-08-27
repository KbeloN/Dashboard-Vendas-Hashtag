import streamlit as st
import pandas as pd
import plotly.express as px

# Método que carrega os dados e armazenar em cache
@st.cache_data
def load_data():
    df = pd.read_csv("tabela_vendas_final.csv") # Carregar o DF
    df['Data'] = pd.to_datetime(df['Data']) # Conversão da coluna Data para datetime
    return df

# Atribuir os dados carregados no DataFrame
df = load_data()

# Filtrar os dados e armazenar em cache
@st.cache_data
def filtered_data(df, lojas_selecionadas):
    return df[df['Loja'].isin(lojas_selecionadas)]

# Criar os dados das métricas e armazenar em cache
@st.cache_data
def metrics_data(df_filtrado):
    if not df_filtrado.empty:
        loja_mais_faturou = df_filtrado.groupby('Loja')['faturamento'].sum().idxmax()
        faturamento_total = df_filtrado['faturamento'].sum()
        item_mais_vendido = df_filtrado.groupby('Produto')['Quantidade Vendida'].sum().idxmax()
        media_diaria = df_filtrado.groupby(df_filtrado['Data'].dt.date)['faturamento'].sum().mean()
    else:
        loja_mais_faturou, faturamento_total, item_mais_vendido, media_diaria = "N/A", 0, "N/A", 0

    return loja_mais_faturou, faturamento_total, item_mais_vendido, media_diaria

# Config da página
st.set_page_config(
    page_title="Análise de Vendas",
    page_icon=":bar_chart:",
    layout="wide"
)

# Barra lateral (Filtros)
st.sidebar.header("Filtros:")

# Lojas
lojas_disposiveis =  sorted(df['Loja'].unique())
lojas_selecionadas = st.sidebar.multiselect("Loja(s)", lojas_disposiveis, default=lojas_disposiveis)

# DF filtrado
df_filtrado = filtered_data(df, lojas_selecionadas)

# Título e subtítulo principais
st.header("Análise de Vendas da Rede de Lojas (2018)")
st.markdown("Selecione as lojas à esquerda para visualizar as métricas.")

# Subtítulo das métricas
st.subheader("Visão Geral:")

# Métricas gerais
loja_mais_faturou, faturamento_total, item_mais_vendido, media_diaria = metrics_data(df_filtrado)

# Exibição das métricas
col1, col2 ,col3, col4 = st.columns(4)
col1.metric("Estado da loja que mais faturou:", loja_mais_faturou)
col2.metric("Faturamento total:", f'R${faturamento_total:,.2f}'.replace(',','.'))
col3.metric("Item mais vendido:", item_mais_vendido)
col4.metric("Média de faturamento por dia:", f'R${media_diaria:,.2f}'.replace(',','.'))

st.markdown("---") # Cria a linha em baixo das métricas gerais

# Subtítulo dos gráficos
st.subheader("Gráficos de Análise")

# Gráficos
if not df_filtrado.empty:
    col_graf1, col_graf2 = st.columns(2)

    # Gráfico 1 os Faturamento de cada item
    with col_graf1:
        st.header("Faturamento Total por Produto (R$)")

        faturamento_pitem = df_filtrado.groupby('Produto')['faturamento'].sum().reset_index()

        grafico_faturamento = px.bar(
            faturamento_pitem,
            x='faturamento',
            y='Produto',
            orientation='h',
            text_auto=True,
            labels={'faturamento': 'Faturamento Total (R$)', 'Produto': 'Produto(s)'}
        )
        grafico_faturamento.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_faturamento, use_container_width=True)
    
    # Gráfico 2 Vendas unitárias de cada item
    with col_graf2:
        st.header("Vendas Unitárias por Produto:")

        # Usuário pode escolher o tipo do gráfico
        tipo_grafico = st.selectbox(
            'Tipo de Gráfico',
            ['Gráfico de Barras Padrão', 'Gráfico Polar']
        )

        vendas_uni = df_filtrado.groupby(['Produto','Loja'])['Quantidade Vendida'].sum().reset_index()

        # Gráfico de Barras Padrão
        if tipo_grafico == 'Gráfico de Barras Padrão':

            grafico_vendas_uni_bar = px.bar(
                vendas_uni,
                x='Produto',
                y='Quantidade Vendida',
                color='Quantidade Vendida',
                text_auto=True, # Aplica a quantidade bruta aos segmentos da barra
                labels={'Produto': 'Produto(s)', 'Quantidade Vendida': 'Vendas Unitárias'},
                hover_data=['Loja'] # Aplica mais uma informação ao tooltip. Nesse caso, a loja
            )
            grafico_vendas_uni_bar.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(grafico_vendas_uni_bar, use_container_width=True)

        # Gráfico Polar    
        elif tipo_grafico == 'Gráfico Polar':

            grafico_vendas_uni_polar = px.bar_polar(
                vendas_uni,
                r='Quantidade Vendida',
                theta='Produto',
                color='Quantidade Vendida', # Colorir cada produto
                color_discrete_sequence=px.colors.sequential.Plasma_r, # Palheta de cores
                labels={'Produto': 'Produto(s)', 'Quantidade Vendida': 'Vendas Unitárias'},
                hover_data=['Loja'] 
            )
            grafico_vendas_uni_polar.update_layout(polar_radialaxis_visible=True, polar_bgcolor='black')
            st.plotly_chart(grafico_vendas_uni_polar, use_container_width=True)

    # Gráfico 3: Faturamento por dia
    col_graf3 = st.columns(1)

    with col_graf3[0]:
        st.header("Faturamento Diário da Empresa (R$)")

        faturamento_pdia = df_filtrado.groupby(df_filtrado['Data'].dt.date)['faturamento'].sum().reset_index()

        grafico_faturamento_pdia = px.line(
            faturamento_pdia,
            x='Data',
            y='faturamento',
            labels={'Data': 'Data', 'faturamento': 'Faturamento (R$)'}
        )
        st.plotly_chart(grafico_faturamento_pdia, use_container_width=True)

    # Última linha de gráficos
    col_graf4, col_graf5 = st.columns(2)

    # Gráfico 4: Composição do faturamento da empresa
    with col_graf4:
        st.header("Composição do Faturamento da Empresa:")

        tipo_grafico_rosca = st.selectbox(
            'Selecione uma opção para visualizar o gráfico:',
            ['Faturamento pelas Lojas', 'Faturamento pelos Itens']
        )

        # Gráfico de Pizza das Lojas
        if tipo_grafico_rosca == 'Faturamento pelas Lojas':
            dados_faturamento_lojas = df_filtrado.groupby('Loja')['faturamento'].sum().reset_index()
            dados_faturamento_lojas.columns = ['Loja', 'Faturamento']
            
            faturamento_loja = px.pie(
                dados_faturamento_lojas,
                names='Loja',
                values='Faturamento',
                labels={'Loja': 'Loja', 'Faturamento': 'Faturamento (R$)'},
                hole=0.5
            )
            faturamento_loja.update_traces(textinfo='percent+label')
            st.plotly_chart(faturamento_loja, use_container_width=True)

        # Gráfico de Pizza dos Itens
        elif tipo_grafico_rosca == 'Faturamento pelos Itens':

            dados_faturamento_itens = df_filtrado.groupby('Produto')['faturamento'].sum().reset_index()
            dados_faturamento_itens.columns = ['Produto', 'Faturamento']

            faturamento_item = px.pie(
                dados_faturamento_itens,
                names='Produto',
                values='Faturamento',
                labels={'Produto': 'Produto', 'Faturamento': 'Faturamento (R$)'},
                hole=0.5
            )
            faturamento_item.update_traces(textinfo='percent+label')
            st.plotly_chart(faturamento_item, use_container_width=True)

    # Gráfico 5: Os 10 dias que mais faturaram
    with col_graf5:

        st.header("Os 10 dias que mais faturaram:")
        st.markdown('(Em ordem cronológica)')

        dias_10_faturamento = df_filtrado.groupby(df_filtrado['Data'].dt.date)['faturamento'].sum().nlargest(10).reset_index()

        grafico_dias_10_faturamento = px.bar(
            dias_10_faturamento,
            x='Data',
            y='faturamento',
            text_auto=True,
            labels={'Data': 'Data', 'faturamento': 'Faturamento (R$)'},
        )
        st.plotly_chart(grafico_dias_10_faturamento, use_container_width=True)

else:
    st.warning("Nenhum dado disponível para exibir.")

# Dados detalhados
st.header('Dados Detalhados:')
st.dataframe(df_filtrado)