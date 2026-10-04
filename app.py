import streamlit as st
import pandas as pd
import plotly.express as px


def formatar_numero(valor):
    return f"{valor:,.0f}".replace(",", ".")

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------

st.set_page_config(
    page_title="Acidentes de Trânsito no Brasil",
    page_icon="🚗",
    layout="wide"
)

# ---------------------------------------------------------
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ---------------------------------------------------------

df = pd.read_csv("dados/simulacao_acidentes_transito_brasil_tema27.csv")

df["data"] = pd.to_datetime(df["data"])

traducao_dias = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

df["dia_semana"] = (
    df["data"]
    .dt.day_name()
    .map(traducao_dias)
)

# ---------------------------------------------------------
# CABEÇALHO
# ---------------------------------------------------------

st.title("🚗 Análise de Acidentes de Trânsito no Brasil")

st.markdown(
    """
    **Dashboard interativo de análise de acidentes de trânsito no Brasil entre 2015 e 2024.**

    A aplicação permite explorar padrões temporais, geográficos e relacionados
    às características das ocorrências presentes na base simulada.
    """
)

st.caption(
    "Disciplina: Linguagens de Programação | "
     "Discente: Laura Ribeiro Mota | "
    "RA: 1016012 | "
    "Docente: Alexandre Neves Louzada "
   
)

st.divider()

# ---------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------

st.sidebar.title("🔎 Filtros")

st.sidebar.markdown(
    """
    Utilize os filtros abaixo para explorar os dados.
    Os indicadores e gráficos serão atualizados de acordo
    com as opções selecionadas.
    """
)

# ---------------------------------------------------------
# FILTRO POR ANO
# ---------------------------------------------------------

anos_disponiveis = sorted(df["ano"].unique())

anos_selecionados = st.sidebar.multiselect(
    "Ano",
    options=anos_disponiveis,
    default=anos_disponiveis
)

# ---------------------------------------------------------
# FILTRO POR MÊS
# ---------------------------------------------------------

meses_disponiveis = sorted(df["mes"].unique())

meses_selecionados = st.sidebar.multiselect(
    "Mês",
    options=meses_disponiveis,
    default=meses_disponiveis
)

# ---------------------------------------------------------
# FILTRO POR REGIÃO
# ---------------------------------------------------------

regioes_disponiveis = sorted(df["regiao"].unique())

regioes_selecionadas = st.sidebar.multiselect(
    "Região",
    options=regioes_disponiveis,
    default=regioes_disponiveis
)

# ---------------------------------------------------------
# BASE INTERMEDIÁRIA PARA FILTROS DEPENDENTES
# ---------------------------------------------------------

df_auxiliar = df[
    df["ano"].isin(anos_selecionados)
    & df["mes"].isin(meses_selecionados)
    & df["regiao"].isin(regioes_selecionadas)
]

# ---------------------------------------------------------
# FILTRO POR ESTADO
# ---------------------------------------------------------

estados_disponiveis = sorted(df_auxiliar["uf"].unique())

estados_selecionados = st.sidebar.multiselect(
    "Estado",
    options=estados_disponiveis,
    default=estados_disponiveis
)

# Atualiza a base auxiliar com os estados escolhidos

df_auxiliar = df_auxiliar[
    df_auxiliar["uf"].isin(estados_selecionados)
]

# ---------------------------------------------------------
# FILTRO POR CIDADE
# ---------------------------------------------------------

cidades_disponiveis = sorted(df_auxiliar["cidade"].unique())

cidades_selecionadas = st.sidebar.multiselect(
    "Cidade",
    options=cidades_disponiveis,
    default=cidades_disponiveis
)

# ---------------------------------------------------------
# FILTRO POR TIPO DE ACIDENTE
# ---------------------------------------------------------

tipos_disponiveis = sorted(df["tipo_acidente"].unique())

tipos_selecionados = st.sidebar.multiselect(
    "Tipo de acidente",
    options=tipos_disponiveis,
    default=tipos_disponiveis
)

# ---------------------------------------------------------
# FILTRO POR NÍVEL DE GRAVIDADE
# ---------------------------------------------------------

gravidades_disponiveis = sorted(df["nivel_gravidade"].unique())

gravidades_selecionadas = st.sidebar.multiselect(
    "Nível de gravidade",
    options=gravidades_disponiveis,
    default=gravidades_disponiveis
)

# ---------------------------------------------------------
# APLICAÇÃO DE TODOS OS FILTROS
# ---------------------------------------------------------

df_filtrado = df[
    df["ano"].isin(anos_selecionados)
    & df["mes"].isin(meses_selecionados)
    & df["regiao"].isin(regioes_selecionadas)
    & df["uf"].isin(estados_selecionados)
    & df["cidade"].isin(cidades_selecionadas)
    & df["tipo_acidente"].isin(tipos_selecionados)
    & df["nivel_gravidade"].isin(gravidades_selecionadas)
]

# ---------------------------------------------------------
# TESTE DOS FILTROS
# ---------------------------------------------------------

#st.subheader("📋 Dados selecionados")

#st.write(
   # f"Quantidade de registros após os filtros: **{len(df_filtrado)}**"
#)

#st.dataframe(
    #df_filtrado.head(10),
    #use_container_width=True
#)

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------

total_acidentes = df_filtrado["acidentes"].sum()
total_mortes = df_filtrado["mortes"].sum()

if not df_filtrado.empty:
    estado_mais_critico = (
        df_filtrado.groupby("uf")["acidentes"]
        .sum()
        .idxmax()
    )

    tipo_predominante = (
        df_filtrado.groupby("tipo_acidente")["acidentes"]
        .sum()
        .idxmax()
    )

    periodo_mais_critico = (
        df_filtrado.groupby("periodo_dia")["acidentes"]
        .sum()
        .idxmax()
    )

else:
    estado_mais_critico = "-"
    tipo_predominante = "-"
    periodo_mais_critico = "-"


# ---------------------------------------------------------
# ÍNDICE DE GRAVIDADE
# ---------------------------------------------------------

mapa_gravidade = {
    "Leve": 1,
    "Moderado": 2,
    "Grave": 3,
    "Crítico": 4
}

df_filtrado = df_filtrado.copy()

df_filtrado["gravidade_num"] = (
    df_filtrado["nivel_gravidade"].map(mapa_gravidade)
)

if not df_filtrado.empty and total_acidentes > 0:
    indice_gravidade = (
        (df_filtrado["gravidade_num"] * df_filtrado["acidentes"]).sum()
        / total_acidentes
    )
else:
    indice_gravidade = 0


# ---------------------------------------------------------
# EXIBIÇÃO DOS KPIs
# ---------------------------------------------------------

st.subheader("📊 Indicadores principais")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Total de acidentes",
        f"{total_acidentes:,.0f}".replace(",", ".")
    )

with col2:
    st.metric(
        "Total de mortes",
        f"{total_mortes:,.0f}".replace(",", ".")
    )

with col3:
    st.metric(
        "Estado mais crítico",
        estado_mais_critico
    )

with col4:
    st.metric(
        "Tipo predominante",
        tipo_predominante
    )

with col5:
    st.metric(
        "Período crítico",
        periodo_mais_critico
    )

with col6:
    st.metric(
        "Índice de gravidade",
        f"{indice_gravidade:.2f} / 4"
    )

st.divider()

aba_visao_geral, aba_temporal, aba_regional, aba_gravidade, aba_dados = st.tabs(
    [
        "📊 Visão Geral",
        "📈 Análise Temporal",
        "📍 Análise Regional",
        "⚠️ Gravidade e Risco",
        "🔎 Explorar Dados"
    ]
)

# ---------------------------------------------------------
# ABA 1 - VISÃO GERAL
# ---------------------------------------------------------

with aba_visao_geral:

    st.subheader("📊 Visão geral dos acidentes")

    st.write(
        """
        Esta seção apresenta uma visão resumida da distribuição dos acidentes,
        considerando os filtros selecionados na barra lateral.
        """
    )

    if df_filtrado.empty:

        st.warning(
            "Nenhum registro foi encontrado para a combinação de filtros selecionada."
        )

    else:

        acidentes_por_regiao = (
            df_filtrado.groupby("regiao", as_index=False)["acidentes"]
            .sum()
            .sort_values("acidentes", ascending=False)
        )

        acidentes_por_tipo = (
            df_filtrado.groupby("tipo_acidente", as_index=False)["acidentes"]
            .sum()
            .sort_values("acidentes", ascending=False)
        )

        coluna_grafico1, coluna_grafico2 = st.columns(2)

        with coluna_grafico1:

            fig_regiao = px.bar(
                acidentes_por_regiao,
                x="regiao",
                y="acidentes",
                title="Acidentes por Região",
                labels={
                    "regiao": "Região",
                    "acidentes": "Quantidade de Acidentes"
                }
            )

            st.plotly_chart(
                fig_regiao,
                use_container_width=True
            )
        with coluna_grafico2:

            fig_tipo = px.bar(
                acidentes_por_tipo,
                x="tipo_acidente",
                y="acidentes",
                title="Acidentes por Tipo",
                labels={
                    "tipo_acidente": "Tipo de Acidente",
                    "acidentes": "Quantidade de Acidentes"
                }
            )

            st.plotly_chart(
                fig_tipo,
                use_container_width=True
            )

        regiao_destaque = acidentes_por_regiao.iloc[0]
        tipo_destaque = acidentes_por_tipo.iloc[0]

        st.info(
            f"""
            **Interpretação:** considerando os filtros selecionados,
            **{regiao_destaque["regiao"]}** apresenta o maior número de acidentes
            entre as regiões disponíveis, com
            **{regiao_destaque["acidentes"]:,.0f} ocorrências**.

            O tipo de acidente predominante é
            **{tipo_destaque["tipo_acidente"]}**, com
            **{tipo_destaque["acidentes"]:,.0f} ocorrências**.
            """.replace(",", ".")
        )
# ---------------------------------------------------------
# ABA 2 - ANÁLISE TEMPORAL
# ---------------------------------------------------------

with aba_temporal:

    st.subheader("📈 Análise temporal")

    st.write(
        """
        Esta seção apresenta a evolução dos acidentes ao longo dos anos
        e a distribuição das ocorrências de acordo com o dia da semana
        e o período do dia.
        """
    )

    if df_filtrado.empty:

        st.warning(
            "Nenhum registro foi encontrado para a combinação de filtros selecionada."
        )

    else:

        # -------------------------------------------------
        # EVOLUÇÃO DOS ACIDENTES POR ANO
        # -------------------------------------------------

        acidentes_por_ano = (
            df_filtrado.groupby("ano", as_index=False)["acidentes"]
            .sum()
            .sort_values("ano")
        )

        fig_temporal = px.line(
            acidentes_por_ano,
            x="ano",
            y="acidentes",
            markers=True,
            title="Evolução dos Acidentes ao Longo dos Anos",
            labels={
                "ano": "Ano",
                "acidentes": "Quantidade de Acidentes"
            }
        )

        st.plotly_chart(
            fig_temporal,
            use_container_width=True
        )
        if len(acidentes_por_ano) > 1:

            primeiro_ano = acidentes_por_ano.iloc[0]
            ultimo_ano = acidentes_por_ano.iloc[-1]

            diferenca = (
                ultimo_ano["acidentes"]
                - primeiro_ano["acidentes"]
            )

            if diferenca > 0:
                tendencia = "aumento"

            elif diferenca < 0:
                tendencia = "redução"

            else:
                tendencia = "estabilidade"

            st.info(
                f"""
                **Interpretação:** considerando os filtros selecionados,
                o primeiro ano disponível apresenta
                **{primeiro_ano["acidentes"]:,.0f} acidentes**,
                enquanto o último apresenta
                **{ultimo_ano["acidentes"]:,.0f}**.

                A comparação entre esses dois pontos indica
                **{tendencia}** no total de acidentes.
                """.replace(",", ".")
            )

        else:

            st.info(
                """
                Apenas um ano está selecionado. Para analisar a evolução
                temporal, selecione dois ou mais anos na barra lateral.
                """
            )
            st.divider()

        st.markdown("### 🔥 Períodos críticos")

        ordem_dias = [
            "Segunda-feira",
            "Terça-feira",
            "Quarta-feira",
            "Quinta-feira",
            "Sexta-feira",
            "Sábado",
            "Domingo"
        ]

        ordem_periodos = [
            "Madrugada",
            "Manhã",
            "Tarde",
            "Noite"
        ]

        heatmap_periodos = pd.pivot_table(
            df_filtrado,
            values="acidentes",
            index="dia_semana",
            columns="periodo_dia",
            aggfunc="sum",
            fill_value=0
        )

        heatmap_periodos = heatmap_periodos.reindex(
            index=ordem_dias,
            columns=ordem_periodos,
            fill_value=0
        )

        fig_heatmap = px.imshow(
            heatmap_periodos,
            text_auto=True,
            aspect="auto",
            title="Acidentes por Dia da Semana e Período do Dia",
            labels={
                "x": "Período do Dia",
                "y": "Dia da Semana",
                "color": "Acidentes"
            }
        )

        st.plotly_chart(
            fig_heatmap,
            use_container_width=True
        )

        if not heatmap_periodos.empty:

            combinacao_critica = heatmap_periodos.stack().idxmax()
            maior_valor = heatmap_periodos.stack().max()

            dia_critico = combinacao_critica[0]
            periodo_critico = combinacao_critica[1]

            st.info(
                f"""
                **Período de maior destaque:** considerando os filtros
                selecionados, a combinação com maior número de acidentes é
                **{dia_critico} durante a {periodo_critico.lower()}**,
                com **{maior_valor:,.0f} acidentes**.
                """.replace(",", ".")
            )

# ---------------------------------------------------------
# ABA 3 - ANÁLISE REGIONAL
# ---------------------------------------------------------

with aba_regional:

    st.subheader("📍 Análise regional")

    st.write(
        """
        Esta seção apresenta a distribuição dos acidentes por região
        e por estado, permitindo identificar as áreas com maiores
        volumes de ocorrências dentro dos filtros selecionados.
        """
    )

    if df_filtrado.empty:

        st.warning(
            "Nenhum registro foi encontrado para a combinação de filtros selecionada."
        )

    else:

        acidentes_por_regiao = (
            df_filtrado.groupby("regiao", as_index=False)["acidentes"]
            .sum()
            .sort_values("acidentes", ascending=False)
        )

        acidentes_por_estado = (
            df_filtrado.groupby("uf", as_index=False)["acidentes"]
            .sum()
            .sort_values("acidentes", ascending=False)
        )

        fig_regional = px.bar(
            acidentes_por_regiao,
            x="regiao",
            y="acidentes",
            title="Total de Acidentes por Região",
            labels={
                "regiao": "Região",
                "acidentes": "Quantidade de Acidentes"
            }
        )

        st.plotly_chart(
            fig_regional,
            use_container_width=True
        )

        fig_estados = px.bar(
            acidentes_por_estado,
            x="acidentes",
            y="uf",
            orientation="h",
            title="Ranking de Acidentes por Estado",
            labels={
                "uf": "Estado",
                "acidentes": "Quantidade de Acidentes"
            }
        )

        fig_estados.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            }
        )

        st.plotly_chart(
            fig_estados,
            use_container_width=True
        )

        regiao_lider = acidentes_por_regiao.iloc[0]
        estado_lider = acidentes_por_estado.iloc[0]

        st.info(
            f"""
            **Interpretação:** considerando os filtros selecionados,
            a região com maior número de acidentes é
            **{regiao_lider["regiao"]}**, com
            **{regiao_lider["acidentes"]:,.0f} ocorrências**.

            O estado com maior número de acidentes é
            **{estado_lider["uf"]}**, com
            **{estado_lider["acidentes"]:,.0f} ocorrências**.
            """.replace(",", ".")
        )

# ---------------------------------------------------------
# ABA 4 - GRAVIDADE E RISCO
# ---------------------------------------------------------

with aba_gravidade:

    st.subheader("⚠️ Gravidade e risco")

    st.write(
        """
        Esta seção analisa os registros classificados como Grave ou Crítico,
        buscando identificar padrões relacionados ao tipo de acidente,
        período do dia, condição de visibilidade e volume de chuva.
        """
    )

    if df_filtrado.empty:

        st.warning(
            "Nenhum registro foi encontrado para a combinação de filtros selecionada."
        )

    else:

        # -------------------------------------------------
        # ACIDENTES GRAVES E CRÍTICOS
        # -------------------------------------------------

        df_graves = df_filtrado[
            df_filtrado["nivel_gravidade"].isin(["Grave", "Crítico"])
        ]

        if df_graves.empty:

            st.warning(
                "Não há registros classificados como Grave ou Crítico "
                "para os filtros selecionados."
            )

        else:

            # ---------------------------------------------
            # GRAVES E CRÍTICOS POR TIPO DE ACIDENTE
            # ---------------------------------------------

            graves_por_tipo = (
                df_graves.groupby(
                    "tipo_acidente",
                    as_index=False
                )["acidentes"]
                .sum()
                .sort_values(
                    "acidentes",
                    ascending=False
                )
            )

            fig_graves_tipo = px.bar(
                graves_por_tipo,
                x="tipo_acidente",
                y="acidentes",
                title="Acidentes Graves e Críticos por Tipo",
                labels={
                    "tipo_acidente": "Tipo de Acidente",
                    "acidentes": "Quantidade de Acidentes"
                }
            )

            st.plotly_chart(
                fig_graves_tipo,
                use_container_width=True
            )

            # ---------------------------------------------
            # GRAVES E CRÍTICOS POR PERÍODO E VISIBILIDADE
            # ---------------------------------------------

            graves_por_periodo = (
                df_graves.groupby(
                    "periodo_dia",
                    as_index=False
                )["acidentes"]
                .sum()
                .sort_values(
                    "acidentes",
                    ascending=False
                )
            )

            graves_por_visibilidade = (
                df_graves.groupby(
                    "visibilidade",
                    as_index=False
                )["acidentes"]
                .sum()
                .sort_values(
                    "acidentes",
                    ascending=False
                )
            )

            coluna_risco1, coluna_risco2 = st.columns(2)

            with coluna_risco1:

                fig_graves_periodo = px.bar(
                    graves_por_periodo,
                    x="periodo_dia",
                    y="acidentes",
                    title="Graves e Críticos por Período do Dia",
                    labels={
                        "periodo_dia": "Período do Dia",
                        "acidentes": "Quantidade de Acidentes"
                    }
                )

                st.plotly_chart(
                    fig_graves_periodo,
                    use_container_width=True
                )

            with coluna_risco2:

                fig_graves_visibilidade = px.bar(
                    graves_por_visibilidade,
                    x="visibilidade",
                    y="acidentes",
                    title="Graves e Críticos por Visibilidade",
                    labels={
                        "visibilidade": "Visibilidade",
                        "acidentes": "Quantidade de Acidentes"
                    }
                )

                st.plotly_chart(
                    fig_graves_visibilidade,
                    use_container_width=True
                )

            # ---------------------------------------------
            # INTERPRETAÇÃO DOS GRAVES E CRÍTICOS
            # ---------------------------------------------

            tipo_grave_destaque = graves_por_tipo.iloc[0]
            periodo_grave_destaque = graves_por_periodo.iloc[0]
            visibilidade_grave_destaque = graves_por_visibilidade.iloc[0]

            st.info(
                f"""
                **Interpretação:** entre os registros classificados como
                Grave ou Crítico, o tipo de acidente com maior número de
                ocorrências é **{tipo_grave_destaque["tipo_acidente"]}**,
                com **{formatar_numero(tipo_grave_destaque["acidentes"])} acidentes**.

                O período do dia com maior concentração é
                **{periodo_grave_destaque["periodo_dia"]}**, com
                **{formatar_numero(periodo_grave_destaque["acidentes"])} ocorrências**.

                A condição de visibilidade com maior número de acidentes
                graves e críticos é
                **{visibilidade_grave_destaque["visibilidade"]}**, com
                **{formatar_numero(visibilidade_grave_destaque["acidentes"])} ocorrências**.
                """
            )

        # -------------------------------------------------
        # CHUVA X ACIDENTES
        # -------------------------------------------------

        st.divider()

        st.markdown("### 🌧️ Relação entre chuva e acidentes")

        st.write(
            """
            Esta análise investiga a relação entre o volume de chuva
            e a quantidade de acidentes, considerando os filtros selecionados.
            """
        )

        fig_chuva = px.scatter(
            df_filtrado,
            x="chuva_mm",
            y="acidentes",
            title="Relação entre Volume de Chuva e Quantidade de Acidentes",
            labels={
                "chuva_mm": "Volume de Chuva (mm)",
                "acidentes": "Quantidade de Acidentes"
            },
            hover_data=[
                "ano",
                "regiao",
                "uf",
                "cidade",
                "tipo_acidente"
            ]
        )

        st.plotly_chart(
            fig_chuva,
            use_container_width=True
        )

        # -------------------------------------------------
        # CORRELAÇÃO ENTRE CHUVA E ACIDENTES
        # -------------------------------------------------

        correlacao_chuva = df_filtrado["chuva_mm"].corr(
            df_filtrado["acidentes"]
        )

        if pd.isna(correlacao_chuva):

            st.info(
                """
                Não foi possível calcular a correlação entre chuva e acidentes
                para os filtros selecionados, pois não há variação suficiente
                nos dados disponíveis.
                """
            )

        else:

            valor_absoluto = abs(correlacao_chuva)

            if valor_absoluto < 0.05:
                intensidade = "praticamente inexistente"

            elif valor_absoluto < 0.20:
                intensidade = "muito fraca"

            elif valor_absoluto < 0.40:
                intensidade = "fraca"

            elif valor_absoluto < 0.60:
                intensidade = "moderada"

            elif valor_absoluto < 0.80:
                intensidade = "forte"

            else:
                intensidade = "muito forte"

            if correlacao_chuva > 0:
                direcao = "positiva"

            elif correlacao_chuva < 0:
                direcao = "negativa"

            else:
                direcao = "nula"

            st.info(
                f"""
                **Correlação entre chuva e acidentes:** {correlacao_chuva:.3f}

                A relação linear observada é **{intensidade} e {direcao}**.

                Esse resultado representa apenas uma associação estatística
                presente nos dados selecionados e não indica relação de causalidade.
                """
            )
# ---------------------------------------------------------
# ABA 5 - EXPLORAR DADOS
# ---------------------------------------------------------

with aba_dados:

    st.subheader("🔎 Exploração detalhada dos dados")

    st.write(
        f"Registros da base correspondentes aos filtros selecionados: "
        f"**{len(df_filtrado)}**"
    )

    # -----------------------------------------------------
    # BASE DE DADOS FILTRADA
    # -----------------------------------------------------

    st.markdown("### 📋 Registros da base")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------------------------------
    # TABELA DINÂMICA
    # -----------------------------------------------------

    st.markdown("### 📊 Tabela dinâmica — Região × Tipo de acidente")

    st.write(
        """
        A tabela abaixo apresenta a quantidade total de acidentes
        para cada combinação de região e tipo de acidente,
        considerando os filtros selecionados.
        """
    )

    if df_filtrado.empty:

        st.warning(
            "Não existem dados disponíveis para gerar a tabela dinâmica."
        )

    else:

        tabela_dinamica = pd.pivot_table(
            df_filtrado,
            values="acidentes",
            index="regiao",
            columns="tipo_acidente",
            aggfunc="sum",
            margins=True,
            margins_name="Total"
        )

        st.dataframe(
            tabela_dinamica,
            use_container_width=True
        )
# ---------------------------------------------------------
# CONCLUSÃO EXECUTIVA
# ---------------------------------------------------------

st.divider()

st.subheader("📝 Conclusão Executiva")

if df_filtrado.empty:

    st.warning(
        "Não há dados disponíveis para gerar a conclusão "
        "com os filtros selecionados."
    )

else:

    total_acidentes_conclusao = df_filtrado["acidentes"].sum()
    total_mortes_conclusao = df_filtrado["mortes"].sum()

    regiao_conclusao = (
        df_filtrado.groupby("regiao")["acidentes"]
        .sum()
        .idxmax()
    )

    estado_conclusao = (
        df_filtrado.groupby("uf")["acidentes"]
        .sum()
        .idxmax()
    )

    tipo_conclusao = (
        df_filtrado.groupby("tipo_acidente")["acidentes"]
        .sum()
        .idxmax()
    )

    periodo_conclusao = (
        df_filtrado.groupby("periodo_dia")["acidentes"]
        .sum()
        .idxmax()
    )

    st.markdown(
        f"""
        Considerando os filtros atualmente selecionados, foram registrados
        **{total_acidentes_conclusao:,.0f} acidentes** e
        **{total_mortes_conclusao:,.0f} mortes**.

        A região com maior número de acidentes é **{regiao_conclusao}**,
        enquanto o estado de maior destaque é **{estado_conclusao}**.
        O tipo de acidente predominante é **{tipo_conclusao}** e o período
        do dia com maior número de ocorrências é **{periodo_conclusao}**.

        Os resultados apresentados representam os padrões encontrados na
        base simulada e devem ser interpretados de acordo com os filtros
        aplicados pelo usuário.
        """.replace(",", ".")
    )

# ---------------------------------------------------------
# RODAPÉ
# ---------------------------------------------------------

st.divider()

st.caption(
    "Projeto acadêmico desenvolvido por Laura Ribeiro Mota | "
    "Disciplina: Linguagens de Programação | "
    "Docente: Alexandre Neves Louzada"
)