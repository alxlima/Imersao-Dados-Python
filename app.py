# Importando as bibliotecas instalado, origem requirements.txt
import streamlit as st
import pandas as pd
import plotly.express as px


# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
# layout="wide" - deixo pagina tamanhça large.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊", 
    layout="wide",
)

# --- Carregamento dos dados ---
# Importar um arquivo dados.csv.no diretório nuvem.
# Link do diretório :https://github.com/guilhermeonrails/idcp-alura/blob/T8R7W1/Todas_as_aulas_Imers%C3%A3o_dados_com_Python_Alura_Agosto_2025.ipynb
# modelo 01 - original sem tratamento campos  |   df = pd.read_csv("https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv")
# modelo 02 - conclusão aula 04
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ----------------------------------------------------------------------------------------------
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ------------------------------------------------------------------------------------------------
# aplico cada tipo de filtro por tipo selecionados, fazendo atualização automaticas.
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal --------------------------------------------------------------------------------------------------
# st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.title("📊 Dashboard de Análise de Salários na Área de Dados")
st.markdown(">Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")
# --se df não estiver vazio(empty),preencho dados , snão apresento valor 0
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""
# - Col1,2,3,4 - divido as informações em colunas na pagina.
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)
#--insito linha separado de bloco metricas.
st.markdown("---")


# --- Sesão com os Graticos -------------------------------------------------------------------------------------------------------
# --- Análises Visuais com Plotly ---
# subheader - é subtitulo titulo
st.subheader("Gráficos")
#- mostro 2 colunas, sendo grafico 01 e 02, um ao lado do outro.   
col_graf1, col_graf2 = st.columns(2)

# --Grafico 01 - tipo Barras (bar)
with col_graf1:
    if not df_filtrado.empty:
        # Antes crio agrupamento de dados por cargo,
        # mean().nlargest(10) - mostro os 10 maiores valores. 
        # orientation= h - exibo as barras com orientação horizontal
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        #update_layout - uso para mover o tipo não ficar tanto na esquerda, mova para direita
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        #plotly_chart - consigo exibir o grafico, com use_container_width=true
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        # warning - é mensagem de alerta caso ocorrer algum tipo de erro
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

# --Grafico 02 - tipo Histrograma (histogram)- mostra a distribuições dos salarios, 
# modo de grafico interativo, usando o plotly
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

#- mostro 2 colunas, sendo  grafico 03 e 04, um ao lado do outro.   
col_graf3, col_graf4 = st.columns(2)

# --Grafico 03 - tipo Pizza(pie) - tipo rosca (hole=0.5)
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

# --Grafico 04 - tipo (choropleth) - tipo Map 
with col_graf4:
    if not df_filtrado.empty:
        # Calcular média salarial por país (ISO-3)
        # df_ds - filtro especificando o cargo(df_lipo) = Data scientist
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        # media_ds_apis - calculo a media do cargo data scientist da cada (residencia_iso3) é o pais agrupado
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        # Gerar o Grafico "choropleth", tipo mapa.
        # color= definio o campo residencia.
        # color_continuos_scale='rdylgn' - defino a paleta de cores em scala, na documentação Lib.potly
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
#subheader - é o subtitulo da tabela
st.subheader("Dados Detalhados")
#mostra dados data frame principal filtrado.
st.dataframe(df_filtrado)