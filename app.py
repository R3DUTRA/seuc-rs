import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── CONFIGURAÇÃO DA PÁGINA ────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEUC/RS",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CORES & ESTILOS ───────────────────────────────────────────────────────────
VERDE_ESCURO   = "#1A5C2A"
VERDE_MEDIO    = "#2E7D32"
AMARELO        = "#FFD600"
CINZA_FUNDO    = "#F0F0F0"
BRANCO         = "#FFFFFF"
TEXTO_ESCURO   = "#1C1C1C"

COR_ESFERA  = {"Federal": "#1565C0", "Estadual": "#2E7D32", "Municipal": "#E65100"}
COR_GRUPO   = {"Proteção Integral": "#1B5E20", "Uso Sustentável": "#F57F17", "Não se aplica": "#607D8B"}
COR_BIOMA   = {
    "Mata Atlântica":                   "#2E7D32",
    "Pampa":                            "#F9A825",
    "Costeiro-Marinho":                 "#0277BD",
    "Mata Atlântica, Pampa":            "#558B2F",
    "Mata Atlântica, Costeiro-Marinho": "#00838F",
    "Pampa, Costeiro-Marinho":          "#6A1B9A",
}

st.markdown(f"""
<style>
  /* Reset sidebar padrão do Streamlit */
  [data-testid="stSidebar"] {{
      background-color: {VERDE_ESCURO} !important;
      padding-top: 0 !important;
  }}
  [data-testid="stSidebar"] * {{
      color: {BRANCO} !important;
  }}
  /* Header topo */
  .header-bar {{
      background-color: {VERDE_ESCURO};
      color: {BRANCO};
      padding: 10px 20px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 4px;
      margin-bottom: 18px;
      text-align: center;
      letter-spacing: 0.3px;
  }}
  /* KPI cards */
  .kpi-card {{
      background: {BRANCO};
      border-left: 5px solid {VERDE_MEDIO};
      border-radius: 6px;
      padding: 14px 18px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.08);
      margin-bottom: 6px;
  }}
  .kpi-card.amarelo {{ border-left-color: {AMARELO}; }}
  .kpi-card.azul    {{ border-left-color: #1565C0; }}
  .kpi-card.laranja {{ border-left-color: #E65100; }}
  .kpi-number {{
      font-size: 2.2rem;
      font-weight: 800;
      color: {VERDE_ESCURO};
      line-height: 1.1;
  }}
  .kpi-label {{
      font-size: 0.78rem;
      color: #555;
      margin-top: 2px;
  }}
  /* Seção titulo */
  .section-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: {VERDE_ESCURO};
      border-bottom: 2px solid {AMARELO};
      padding-bottom: 4px;
      margin: 18px 0 10px 0;
  }}
  /* Nav item ativo na sidebar */
  .nav-ativo {{
      background-color: {AMARELO};
      color: {TEXTO_ESCURO} !important;
      border-radius: 5px;
      padding: 4px 8px;
      font-weight: 700;
  }}
  /* Tabela */
  .dataframe {{ font-size: 12px; }}
  /* Fundo geral */
  .main {{ background-color: {CINZA_FUNDO}; }}
  /* Remover padding excessivo */
  .block-container {{ padding-top: 1rem !important; }}
</style>
""", unsafe_allow_html=True)


# ─── CARGA DE DADOS ────────────────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    base      = pd.read_excel("data/BaseSeuc.xlsx")
    biomas    = pd.read_excel("data/BIOMAS_SCM_12M.xlsx")
    municipios= pd.read_excel("data/Municipios.xlsx")
    biomap    = pd.read_excel("data/BioMap.xlsx")

    # Limpezas básicas
    base["Ano de criação"] = pd.to_numeric(base["Ano de criação"], errors="coerce")
    base["Área poligonal (ha)"] = pd.to_numeric(base["Área poligonal (ha)"], errors="coerce").fillna(0)
    biomas["Area_ha"] = pd.to_numeric(biomas["Area_ha"], errors="coerce").fillna(0)

    # Flag simples Sim/Não
    for col in ["Plano de Manejo", "Conselho Gestor", "CNUC", "Shapefile dos limites", "ZA"]:
        if col in base.columns:
            base[col + "_bool"] = base[col].str.strip().str.lower() == "sim"

    return base, biomas, municipios, biomap

base, biomas, municipios, biomap = carregar_dados()


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 18px 0 10px 0;'>
        <div style='font-size:1.5rem; font-weight:900; letter-spacing:1px; color:#FFD600;'>SEUC/RS</div>
        <div style='font-size:0.68rem; color:#ccc; margin-top:2px;'>Sistema Estadual de UCs</div>
        <div style='font-size:0.68rem; color:#ccc;'>Rio Grande do Sul</div>
    </div>
    <hr style='border-color:#ffffff33; margin:8px 0;'>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "Navegação",
        ["🏠 Menu", "📋 Cadastro e Regularização", "🌍 Cobertura Espacial",
         "⚙️ Implementação e Efetividade", "🗺️ Informações Geoespaciais"],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#ffffff33; margin:16px 0 8px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.65rem; color:#aaa; text-align:center; padding-bottom:10px;'>
        SEMA-RS · Dados: SEUC/RS<br>
        Versão 1.0
    </div>
    """, unsafe_allow_html=True)


# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='header-bar'>
    Plataforma oficial de dados do Sistema Estadual de Unidades de Conservação do Rio Grande do Sul &nbsp;|&nbsp; SEUC/RS
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — MENU
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "🏠 Menu":
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {VERDE_ESCURO} 60%, #2E7D32);
                border-radius: 10px; padding: 32px 40px; margin-bottom: 24px;
                color: white;'>
        <div style='font-size:1rem; opacity:0.8; margin-bottom:6px;'>Plataforma oficial de dados do</div>
        <div style='font-size:2rem; font-weight:900; line-height:1.15;'>
            Sistema Estadual de Unidades de Conservação<br>
            <span style='color:{AMARELO}; font-size:2.5rem;'>Rio Grande do Sul</span>
        </div>
        <div style='margin-top:14px; font-size:0.9rem; opacity:0.85;'>
            225 unidades de conservação catalogadas · Dados atualizados 2024
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs rápidos
    c1, c2, c3, c4 = st.columns(4)
    total_ucs  = len(base)
    area_total = base["Área poligonal (ha)"].sum()
    com_pm     = base["Plano de Manejo_bool"].sum()
    com_cg     = base["Conselho Gestor_bool"].sum()

    for col, num, label, cls in [
        (c1, f"{total_ucs}", "Unidades de Conservação", ""),
        (c2, f"{area_total:,.0f} ha", "Área Total Catalogada", "amarelo"),
        (c3, f"{com_pm}", "UCs com Plano de Manejo", "azul"),
        (c4, f"{com_cg}", "UCs com Conselho Gestor", "laranja"),
    ]:
        col.markdown(f"""
        <div class='kpi-card {cls}'>
            <div class='kpi-number'>{num}</div>
            <div class='kpi-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    # Gráfico por Esfera
    with c1:
        st.markdown("<div class='section-title'>UCs por Esfera</div>", unsafe_allow_html=True)
        df_esfera = base["Esfera"].value_counts().reset_index()
        df_esfera.columns = ["Esfera", "Total"]
        fig = px.pie(df_esfera, names="Esfera", values="Total",
                     color="Esfera", color_discrete_map=COR_ESFERA,
                     hole=0.45)
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=240,
                          legend=dict(orientation="h", y=-0.15, font_size=11),
                          showlegend=True)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)

    # Gráfico por Bioma
    with c2:
        st.markdown("<div class='section-title'>UCs por Bioma</div>", unsafe_allow_html=True)
        df_bioma = base["Bioma"].value_counts().reset_index()
        df_bioma.columns = ["Bioma", "Total"]
        fig2 = px.bar(df_bioma, x="Total", y="Bioma", orientation="h",
                      color="Bioma", color_discrete_map=COR_BIOMA)
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=240,
                           showlegend=False, yaxis_title="", xaxis_title="Qtd")
        fig2.update_traces(texttemplate="%{x}", textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    # Gráfico por Grupo
    with c3:
        st.markdown("<div class='section-title'>UCs por Grupo SNUC</div>", unsafe_allow_html=True)
        df_grupo = base["Grupo"].value_counts().reset_index()
        df_grupo.columns = ["Grupo", "Total"]
        fig3 = px.pie(df_grupo, names="Grupo", values="Total",
                      color="Grupo", color_discrete_map=COR_GRUPO, hole=0.45)
        fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=240,
                           legend=dict(orientation="h", y=-0.15, font_size=10))
        fig3.update_traces(textinfo="percent+label", textfont_size=10)
        st.plotly_chart(fig3, use_container_width=True)

    # Linha do tempo criação
    st.markdown("<div class='section-title'>Evolução da criação de UCs por ano</div>", unsafe_allow_html=True)
    df_ano = base.dropna(subset=["Ano de criação"])
    df_ano = df_ano.groupby(["Ano de criação", "Esfera"]).size().reset_index(name="Criadas")
    fig_time = px.area(df_ano, x="Ano de criação", y="Criadas", color="Esfera",
                       color_discrete_map=COR_ESFERA, line_group="Esfera")
    fig_time.update_layout(height=250, margin=dict(t=10, b=10, l=10, r=10),
                           xaxis_title="Ano", yaxis_title="UCs Criadas",
                           legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_time, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — CADASTRO E REGULARIZAÇÃO (CR)
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📋 Cadastro e Regularização":

    # ── Filtros ──
    with st.expander("🔎 Filtros", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        f_esfera  = fc1.multiselect("Esfera", sorted(base["Esfera"].dropna().unique()),
                                    default=sorted(base["Esfera"].dropna().unique()))
        f_bioma   = fc2.multiselect("Bioma",  sorted(base["Bioma"].dropna().unique()),
                                    default=sorted(base["Bioma"].dropna().unique()))
        f_grupo   = fc3.multiselect("Grupo SNUC", sorted(base["Grupo"].dropna().unique()),
                                    default=sorted(base["Grupo"].dropna().unique()))
        f_cat     = fc4.multiselect("Categoria SNUC",
                                    sorted(base["Categoria SNUC"].dropna().unique()),
                                    default=sorted(base["Categoria SNUC"].dropna().unique()))

    df = base.copy()
    if f_esfera: df = df[df["Esfera"].isin(f_esfera)]
    if f_bioma:  df = df[df["Bioma"].isin(f_bioma)]
    if f_grupo:  df = df[df["Grupo"].isin(f_grupo)]
    if f_cat:    df = df[df["Categoria SNUC"].isin(f_cat)]

    # ── KPIs ──
    k1, k2, k3, k4, k5 = st.columns(5)
    for col, num, label, cls in [
        (k1, len(df), "Total de UCs", ""),
        (k2, f"{df['Área poligonal (ha)'].sum():,.0f}", "Área Total (ha)", "amarelo"),
        (k3, df["CNUC_bool"].sum(), "Cadastradas no CNUC", "azul"),
        (k4, df["Shapefile dos limites_bool"].sum(), "Com Shapefile", ""),
        (k5, df["Plano de Manejo_bool"].sum(), "Com Plano de Manejo", "laranja"),
    ]:
        col.markdown(f"""
        <div class='kpi-card {cls}'>
            <div class='kpi-number'>{num}</div>
            <div class='kpi-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráficos linha 1 ──
    g1, g2, g3 = st.columns(3)

    with g1:
        st.markdown("<div class='section-title'>Por Esfera</div>", unsafe_allow_html=True)
        d = df["Esfera"].value_counts().reset_index()
        d.columns = ["Esfera","n"]
        fig = px.pie(d, names="Esfera", values="n", color="Esfera",
                     color_discrete_map=COR_ESFERA, hole=0.5)
        fig.update_traces(textinfo="percent+value")
        fig.update_layout(height=230, margin=dict(t=5,b=30,l=5,r=5),
                          legend=dict(orientation="h", y=-0.2, font_size=10))
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown("<div class='section-title'>Por Grupo SNUC</div>", unsafe_allow_html=True)
        d = df["Grupo"].value_counts().reset_index()
        d.columns = ["Grupo","n"]
        fig = px.pie(d, names="Grupo", values="n", color="Grupo",
                     color_discrete_map=COR_GRUPO, hole=0.5)
        fig.update_traces(textinfo="percent+value")
        fig.update_layout(height=230, margin=dict(t=5,b=30,l=5,r=5),
                          legend=dict(orientation="h", y=-0.25, font_size=9))
        st.plotly_chart(fig, use_container_width=True)

    with g3:
        st.markdown("<div class='section-title'>Por Bioma</div>", unsafe_allow_html=True)
        d = df["Bioma"].value_counts().reset_index()
        d.columns = ["Bioma","n"]
        fig = px.pie(d, names="Bioma", values="n", color="Bioma",
                     color_discrete_map=COR_BIOMA, hole=0.5)
        fig.update_traces(textinfo="percent+value", textfont_size=9)
        fig.update_layout(height=230, margin=dict(t=5,b=30,l=5,r=5),
                          legend=dict(orientation="h", y=-0.3, font_size=9))
        st.plotly_chart(fig, use_container_width=True)

    # ── Gráficos linha 2 ──
    g4, g5 = st.columns(2)

    with g4:
        st.markdown("<div class='section-title'>Categoria SNUC</div>", unsafe_allow_html=True)
        d = df["Categoria SNUC"].value_counts().reset_index()
        d.columns = ["Categoria","n"]
        fig = px.bar(d, x="Categoria", y="n",
                     color_discrete_sequence=[VERDE_MEDIO])
        fig.update_layout(height=230, margin=dict(t=5,b=5,l=5,r=5),
                          xaxis_title="", yaxis_title="Qtd")
        fig.update_traces(texttemplate="%{y}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with g5:
        st.markdown("<div class='section-title'>Evolução por Esfera (ano de criação)</div>",
                    unsafe_allow_html=True)
        d = df.dropna(subset=["Ano de criação"]).groupby(
            ["Ano de criação","Esfera"]).size().reset_index(name="n")
        fig = px.area(d, x="Ano de criação", y="n", color="Esfera",
                      color_discrete_map=COR_ESFERA)
        fig.update_layout(height=230, margin=dict(t=5,b=5,l=5,r=5),
                          xaxis_title="Ano", yaxis_title="UCs Criadas",
                          legend=dict(orientation="h", y=1.1, font_size=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Tabela ──
    st.markdown("<div class='section-title'>Listagem de UCs</div>", unsafe_allow_html=True)
    colunas_tabela = ["Código","Nome","Bioma","Grupo","Esfera","Categoria SNUC",
                      "Ano de criação","Área poligonal (ha)","CNUC","Plano de Manejo",
                      "Conselho Gestor","Shapefile dos limites"]
    cols_disp = [c for c in colunas_tabela if c in df.columns]
    st.dataframe(df[cols_disp].reset_index(drop=True), use_container_width=True, height=300)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — COBERTURA ESPACIAL (CE)
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🌍 Cobertura Espacial":

    # ── Filtros ──
    with st.expander("🔎 Filtros", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        f_esfera2 = fc1.multiselect("Esfera", sorted(biomas["Esfera_UC"].dropna().unique()),
                                    default=sorted(biomas["Esfera_UC"].dropna().unique()),
                                    key="ce_esfera")
        f_bioma2  = fc2.multiselect("Bioma SCM", sorted(biomas["Bioma_SCM"].dropna().unique()),
                                    default=sorted(biomas["Bioma_SCM"].dropna().unique()),
                                    key="ce_bioma")
        f_grupo2  = fc3.multiselect("Grupo UC", sorted(biomas["Grupo_UC"].dropna().unique()),
                                    default=sorted(biomas["Grupo_UC"].dropna().unique()),
                                    key="ce_grupo")

    db = biomas.copy()
    if f_esfera2: db = db[db["Esfera_UC"].isin(f_esfera2)]
    if f_bioma2:  db = db[db["Bioma_SCM"].isin(f_bioma2)]
    if f_grupo2:  db = db[db["Grupo_UC"].isin(f_grupo2)]

    # ── KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    area_tot   = db["Area_ha"].sum()
    area_km2   = db["Area_KM2_1"].sum() if "Area_KM2_1" in db.columns else area_tot / 100
    n_ucs      = db["Código"].nunique()
    n_biomas   = db["Bioma_SCM"].nunique()

    for col, num, label, cls in [
        (k1, n_ucs,             "UCs com dados geoespaciais", ""),
        (k2, f"{area_tot:,.0f}","Área Total (ha)", "amarelo"),
        (k3, f"{area_km2:,.1f}","Área Total (km²)", "azul"),
        (k4, n_biomas,          "Biomas presentes", "laranja"),
    ]:
        col.markdown(f"""
        <div class='kpi-card {cls}'>
            <div class='kpi-number'>{num}</div>
            <div class='kpi-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("<div class='section-title'>Área (ha) por Bioma SCM</div>",
                    unsafe_allow_html=True)
        d = db.groupby("Bioma_SCM")["Area_ha"].sum().reset_index()
        d.columns = ["Bioma","Área (ha)"]
        d = d.sort_values("Área (ha)", ascending=True)
        fig = px.bar(d, x="Área (ha)", y="Bioma", orientation="h",
                     color="Bioma", color_discrete_map=COR_BIOMA)
        fig.update_layout(height=280, margin=dict(t=5,b=5,l=5,r=5),
                          showlegend=False, yaxis_title="", xaxis_title="Hectares")
        fig.update_traces(texttemplate="%{x:,.0f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown("<div class='section-title'>Área (ha) por Esfera</div>",
                    unsafe_allow_html=True)
        d = db.groupby("Esfera_UC")["Area_ha"].sum().reset_index()
        d.columns = ["Esfera","Área (ha)"]
        fig = px.pie(d, names="Esfera", values="Área (ha)", color="Esfera",
                     color_discrete_map=COR_ESFERA, hole=0.5)
        fig.update_traces(textinfo="percent+label+value",
                          texttemplate="%{label}<br>%{percent:.1%}<br>%{value:,.0f} ha")
        fig.update_layout(height=280, margin=dict(t=5,b=30,l=5,r=5),
                          legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    g3, g4 = st.columns(2)

    with g3:
        st.markdown("<div class='section-title'>Quantidade de UCs por Bioma SCM</div>",
                    unsafe_allow_html=True)
        d = db.groupby("Bioma_SCM")["Código"].nunique().reset_index()
        d.columns = ["Bioma","UCs"]
        fig = px.bar(d, x="Bioma", y="UCs", color="Bioma",
                     color_discrete_map=COR_BIOMA)
        fig.update_layout(height=250, margin=dict(t=5,b=5,l=5,r=5),
                          showlegend=False, xaxis_title="", yaxis_title="Qtd UCs")
        fig.update_traces(texttemplate="%{y}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with g4:
        st.markdown("<div class='section-title'>Área (ha) por Categoria SNUC</div>",
                    unsafe_allow_html=True)
        if "SNUC" in db.columns:
            d = db.groupby("SNUC")["Area_ha"].sum().reset_index()
            d.columns = ["Categoria","Área (ha)"]
            d = d.sort_values("Área (ha)", ascending=False)
            fig = px.bar(d, x="Categoria", y="Área (ha)",
                         color_discrete_sequence=[VERDE_MEDIO])
            fig.update_layout(height=250, margin=dict(t=5,b=5,l=5,r=5),
                              xaxis_title="", yaxis_title="Hectares")
            fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

    # ── Tabela ──
    st.markdown("<div class='section-title'>Detalhamento geoespacial</div>", unsafe_allow_html=True)
    colunas_bio = ["Código","Nome_UC","Esfera_UC","Grupo_UC","Bioma_SCM","Area_ha",
                   "Area_KM2_1","SNUC","CNUC","Órgão","PM"]
    cols_b = [c for c in colunas_bio if c in db.columns]
    st.dataframe(db[cols_b].reset_index(drop=True), use_container_width=True, height=280)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — IMPLEMENTAÇÃO E EFETIVIDADE (IE)
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "⚙️ Implementação e Efetividade":

    # ── Filtros ──
    with st.expander("🔎 Filtros", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        f_esf3 = fc1.multiselect("Esfera", sorted(base["Esfera"].dropna().unique()),
                                  default=sorted(base["Esfera"].dropna().unique()),
                                  key="ie_esfera")
        f_grp3 = fc2.multiselect("Grupo SNUC", sorted(base["Grupo"].dropna().unique()),
                                  default=sorted(base["Grupo"].dropna().unique()),
                                  key="ie_grupo")
        f_cat3 = fc3.multiselect("Categoria SNUC",
                                  sorted(base["Categoria SNUC"].dropna().unique()),
                                  default=sorted(base["Categoria SNUC"].dropna().unique()),
                                  key="ie_cat")

    di = base.copy()
    if f_esf3: di = di[di["Esfera"].isin(f_esf3)]
    if f_grp3: di = di[di["Grupo"].isin(f_grp3)]
    if f_cat3: di = di[di["Categoria SNUC"].isin(f_cat3)]

    total = len(di)

    # ── KPIs ──
    k1, k2, k3, k4, k5 = st.columns(5)
    for col, num, label, cls in [
        (k1, f"{di['Plano de Manejo_bool'].sum()} / {total}", "Plano de Manejo", ""),
        (k2, f"{di['Conselho Gestor_bool'].sum()} / {total}", "Conselho Gestor", "amarelo"),
        (k3, f"{di['ZA_bool'].sum()} / {total}", "Zona de Amortecimento", "azul"),
        (k4, f"{di['CNUC_bool'].sum()} / {total}", "Cadastradas CNUC", ""),
        (k5, f"{di['Shapefile dos limites_bool'].sum()} / {total}", "Com Shapefile", "laranja"),
    ]:
        pct = int(num.split("/")[0].strip()) / total * 100 if total > 0 else 0
        col.markdown(f"""
        <div class='kpi-card {cls}'>
            <div class='kpi-number'>{num}</div>
            <div class='kpi-label'>{label}<br>
              <span style='font-size:0.85rem;color:{VERDE_ESCURO};font-weight:700;'>{pct:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Indicadores de implementação ──
    indicadores = {
        "Plano de Manejo":      di["Plano de Manejo_bool"].sum(),
        "Conselho Gestor":      di["Conselho Gestor_bool"].sum(),
        "Zona de Amortecimento":di["ZA_bool"].sum(),
        "CNUC":                 di["CNUC_bool"].sum(),
        "Shapefile":            di["Shapefile dos limites_bool"].sum(),
    }

    g1, g2 = st.columns([1.2, 1])

    with g1:
        st.markdown("<div class='section-title'>Indicadores de implementação</div>",
                    unsafe_allow_html=True)
        df_ind = pd.DataFrame({
            "Indicador": list(indicadores.keys()),
            "Com": list(indicadores.values()),
            "Sem": [total - v for v in indicadores.values()],
        })
        fig = go.Figure()
        fig.add_bar(name="Com", x=df_ind["Indicador"], y=df_ind["Com"],
                    marker_color=VERDE_MEDIO, text=df_ind["Com"],
                    textposition="inside")
        fig.add_bar(name="Sem", x=df_ind["Indicador"], y=df_ind["Sem"],
                    marker_color="#CFD8DC", text=df_ind["Sem"],
                    textposition="inside")
        fig.update_layout(barmode="stack", height=300,
                          margin=dict(t=5,b=5,l=5,r=5),
                          yaxis_title="Qtd UCs",
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown("<div class='section-title'>% Implementação</div>",
                    unsafe_allow_html=True)
        pcts = {k: v/total*100 for k,v in indicadores.items()}
        fig2 = go.Figure(go.Bar(
            x=list(pcts.values()),
            y=list(pcts.keys()),
            orientation="h",
            marker_color=[VERDE_MEDIO if v >= 50 else AMARELO if v >= 25 else "#EF5350"
                          for v in pcts.values()],
            text=[f"{v:.1f}%" for v in pcts.values()],
            textposition="outside",
        ))
        fig2.update_layout(height=300, margin=dict(t=5,b=5,l=5,r=5),
                           xaxis=dict(range=[0,105], title="%"),
                           yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Por Esfera ──
    g3, g4 = st.columns(2)

    with g3:
        st.markdown("<div class='section-title'>Plano de Manejo por Esfera</div>",
                    unsafe_allow_html=True)
        pm_esfera = di.groupby("Esfera")["Plano de Manejo_bool"].agg(
            Com="sum", Total="count"
        ).reset_index()
        pm_esfera["Sem"] = pm_esfera["Total"] - pm_esfera["Com"]
        fig3 = go.Figure()
        fig3.add_bar(name="Com PM", x=pm_esfera["Esfera"], y=pm_esfera["Com"],
                     marker_color=VERDE_MEDIO)
        fig3.add_bar(name="Sem PM", x=pm_esfera["Esfera"], y=pm_esfera["Sem"],
                     marker_color="#CFD8DC")
        fig3.update_layout(barmode="stack", height=250,
                           margin=dict(t=5,b=5,l=5,r=5),
                           legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig3, use_container_width=True)

    with g4:
        st.markdown("<div class='section-title'>Conselho Gestor por Esfera</div>",
                    unsafe_allow_html=True)
        cg_esfera = di.groupby("Esfera")["Conselho Gestor_bool"].agg(
            Com="sum", Total="count"
        ).reset_index()
        cg_esfera["Sem"] = cg_esfera["Total"] - cg_esfera["Com"]
        fig4 = go.Figure()
        fig4.add_bar(name="Com CG", x=cg_esfera["Esfera"], y=cg_esfera["Com"],
                     marker_color="#1565C0")
        fig4.add_bar(name="Sem CG", x=cg_esfera["Esfera"], y=cg_esfera["Sem"],
                     marker_color="#CFD8DC")
        fig4.update_layout(barmode="stack", height=250,
                           margin=dict(t=5,b=5,l=5,r=5),
                           legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Tabela ──
    st.markdown("<div class='section-title'>Detalhamento de implementação</div>",
                unsafe_allow_html=True)
    cols_ie = ["Código","Nome","Esfera","Grupo","Categoria SNUC",
               "Plano de Manejo","Fase do Plano de Manejo",
               "Conselho Gestor","ZA","CNUC","Shapefile dos limites",
               "Quadro funcional","Número de servidores efetivos"]
    cols_ie_disp = [c for c in cols_ie if c in di.columns]
    st.dataframe(di[cols_ie_disp].reset_index(drop=True), use_container_width=True, height=280)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 5 — INFORMAÇÕES GEOESPACIAIS (GE)
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🗺️ Informações Geoespaciais":

    # ── Filtros ──
    with st.expander("🔎 Filtros", expanded=True):
        fc1, fc2 = st.columns(2)
        f_bioma4  = fc1.multiselect("Bioma", sorted(biomap["Bioma"].dropna().unique()),
                                    default=sorted(biomap["Bioma"].dropna().unique()),
                                    key="ge_bioma")
        todos_mun = sorted(municipios["Municípios_1"].dropna().unique())
        f_mun4    = fc2.multiselect("Município", todos_mun, key="ge_mun")

    # Join: biomap + municipios + base
    dg = biomap.copy()
    if f_bioma4: dg = dg[dg["Bioma"].isin(f_bioma4)]

    dm = municipios.copy()
    if f_mun4:   dm = dm[dm["Municípios_1"].isin(f_mun4)]

    # UCs filtradas por município (se filtro ativo)
    codigos_mun = dm["Código"].unique()
    if f_mun4:
        dg = dg[dg["Código"].isin(codigos_mun)]

    # Join com BaseSeuc
    dg_full = dg.merge(
        base[["Código","Esfera","Grupo","Categoria SNUC","Área poligonal (ha)",
              "Plano de Manejo","Conselho Gestor","Ano de criação","Órgão gestor"]],
        on="Código", how="left"
    )

    # ── KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    mun_count = dm["Municípios_1"].nunique() if not f_mun4 else len(f_mun4)
    for col, num, label, cls in [
        (k1, len(dg),          "UCs no filtro", ""),
        (k2, dg["Bioma"].nunique(), "Biomas", "amarelo"),
        (k3, mun_count,        "Municípios", "azul"),
        (k4, dm["Código"].nunique(), "UCs com dados municipais", ""),
    ]:
        col.markdown(f"""
        <div class='kpi-card {cls}'>
            <div class='kpi-number'>{num}</div>
            <div class='kpi-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    g1, g2 = st.columns(2)

    with g1:
        st.markdown("<div class='section-title'>UCs por Bioma</div>", unsafe_allow_html=True)
        d = dg["Bioma"].value_counts().reset_index()
        d.columns = ["Bioma","n"]
        fig = px.pie(d, names="Bioma", values="n", color="Bioma",
                     color_discrete_map=COR_BIOMA, hole=0.45)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(height=270, margin=dict(t=5,b=30,l=5,r=5),
                          legend=dict(orientation="h", y=-0.25, font_size=9))
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown("<div class='section-title'>UCs por Esfera (dados GE)</div>",
                    unsafe_allow_html=True)
        if "Esfera" in dg_full.columns:
            d = dg_full["Esfera"].value_counts().reset_index()
            d.columns = ["Esfera","n"]
            fig = px.bar(d, x="Esfera", y="n", color="Esfera",
                         color_discrete_map=COR_ESFERA)
            fig.update_traces(texttemplate="%{y}", textposition="outside")
            fig.update_layout(height=270, margin=dict(t=5,b=5,l=5,r=5),
                              showlegend=False, yaxis_title="Qtd")
            st.plotly_chart(fig, use_container_width=True)

    # ── Top 10 municípios com mais UCs ──
    st.markdown("<div class='section-title'>Top municípios com mais UCs</div>",
                unsafe_allow_html=True)
    top_mun = (dm.groupby("Municípios_1")["Código"].nunique()
               .reset_index().rename(columns={"Código":"UCs","Municípios_1":"Município"})
               .sort_values("UCs", ascending=False).head(20))
    fig_top = px.bar(top_mun, x="UCs", y="Município", orientation="h",
                     color_discrete_sequence=[VERDE_MEDIO])
    fig_top.update_traces(texttemplate="%{x}", textposition="outside")
    fig_top.update_layout(height=420, margin=dict(t=5,b=5,l=5,r=10),
                          yaxis=dict(autorange="reversed"),
                          xaxis_title="Nº de UCs", yaxis_title="")
    st.plotly_chart(fig_top, use_container_width=True)

    # ── Tabelas ──
    t1, t2 = st.columns(2)

    with t1:
        st.markdown("<div class='section-title'>UCs geoespaciais</div>",
                    unsafe_allow_html=True)
        cols_g = ["Código","Nome","Bioma"]
        st.dataframe(dg[cols_g].reset_index(drop=True),
                     use_container_width=True, height=250)

    with t2:
        st.markdown("<div class='section-title'>UCs × Municípios</div>",
                    unsafe_allow_html=True)
        cols_m = ["Código","Nome","Municípios_1","UF"]
        cols_m_disp = [c for c in cols_m if c in dm.columns]
        st.dataframe(dm[cols_m_disp].reset_index(drop=True),
                     use_container_width=True, height=250)
