import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# ─── CONFIGURAÇÃO ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEUC/RS",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CORES ────────────────────────────────────────────────────────────────────
VERDE   = "#1A5C2A"
VERDE2  = "#2E7D32"
AMARELO = "#FFD600"
CINZA   = "#F4F4F4"
BRANCO  = "#FFFFFF"

COR_ESFERA = {"Federal": "#1565C0", "Estadual": "#2E7D32", "Municipal": "#E65100"}
COR_GRUPO  = {"Proteção Integral": "#1B5E20", "Uso Sustentável": "#F57F17", "Não se aplica": "#607D8B"}
COR_BIOMA  = {
    "Mata Atlântica":                   "#2E7D32",
    "Pampa":                            "#F9A825",
    "Costeiro-Marinho":                 "#0277BD",
    "Mata Atlântica, Pampa":            "#558B2F",
    "Mata Atlântica, Costeiro-Marinho": "#00838F",
    "Pampa, Costeiro-Marinho":          "#6A1B9A",
}

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  [data-testid="stSidebar"] {{
      background: linear-gradient(180deg, {VERDE} 0%, #0f3d1a 100%) !important;
  }}
  [data-testid="stSidebar"] * {{ color: {BRANCO} !important; }}
  [data-testid="stSidebar"] .stRadio label {{ font-size: 0.88rem; }}
  .block-container {{ padding-top: 0.8rem !important; }}
  .header-bar {{
      background: {VERDE};
      color: {BRANCO};
      padding: 9px 20px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      margin-bottom: 14px;
      text-align: center;
      letter-spacing: 0.4px;
  }}
  .kpi-wrap {{
      background: {BRANCO};
      border-radius: 8px;
      padding: 14px 16px 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      border-top: 4px solid {VERDE2};
      height: 100%;
  }}
  .kpi-wrap.am {{ border-top-color: {AMARELO}; }}
  .kpi-wrap.az {{ border-top-color: #1565C0; }}
  .kpi-wrap.la {{ border-top-color: #E65100; }}
  .kpi-wrap.ro {{ border-top-color: #C62828; }}
  .kpi-num  {{ font-size: 2rem; font-weight: 800; color: {VERDE}; line-height: 1.1; }}
  .kpi-lbl  {{ font-size: 0.74rem; color: #666; margin-top: 3px; }}
  .sec-title {{
      font-size: 0.92rem; font-weight: 700; color: {VERDE};
      border-bottom: 2px solid {AMARELO};
      padding-bottom: 3px; margin: 16px 0 8px;
  }}
  .main {{ background-color: {CINZA}; }}
</style>
""", unsafe_allow_html=True)


# ─── DADOS ────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    base  = pd.read_excel("data/BaseSeuc.xlsx")
    bio   = pd.read_excel("data/BIOMAS_SCM_12M.xlsx")
    mun   = pd.read_excel("data/Municipios.xlsx")
    bmap  = pd.read_excel("data/BioMap.xlsx")
    base["Ano de criação"]      = pd.to_numeric(base["Ano de criação"], errors="coerce")
    base["Área poligonal (ha)"] = pd.to_numeric(base["Área poligonal (ha)"], errors="coerce").fillna(0)
    bio["Area_ha"]              = pd.to_numeric(bio["Area_ha"], errors="coerce").fillna(0)
    for col in ["Plano de Manejo","Conselho Gestor","CNUC","Shapefile dos limites","ZA"]:
        if col in base.columns:
            base[col+"_b"] = base[col].astype(str).str.strip().str.lower() == "sim"
    return base, bio, mun, bmap

@st.cache_data
def load_geo():
    with open("data/RS_Municipios_2024.geojson") as f:
        mun_geo = json.load(f)
    with open("data/RS_Biomas_SCM.geojson") as f:
        bio_geo = json.load(f)
    return mun_geo, bio_geo

base, bio, mun, bmap = load()
mun_geo, bio_geo     = load_geo()


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def kpi(col, num, lbl, cls=""):
    col.markdown(f"""
    <div class='kpi-wrap {cls}'>
      <div class='kpi-num'>{num}</div>
      <div class='kpi-lbl'>{lbl}</div>
    </div>""", unsafe_allow_html=True)

def sec(txt):
    st.markdown(f"<div class='sec-title'>{txt}</div>", unsafe_allow_html=True)

LAYOUT = dict(margin=dict(t=6,b=6,l=6,r=6), paper_bgcolor="white",
              plot_bgcolor="white", font_family="Arial")


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:20px 0 12px'>
      <div style='font-size:1.8rem;font-weight:900;color:{AMARELO};letter-spacing:2px;'>SEUC/RS</div>
      <div style='font-size:0.65rem;color:#bbb;margin-top:2px;line-height:1.5;'>
        Sistema Estadual de<br>Unidades de Conservação<br>Rio Grande do Sul
      </div>
    </div>
    <hr style='border-color:#ffffff22;margin:4px 0 12px'>
    """, unsafe_allow_html=True)

    pagina = st.radio("", [
        "🏠  Menu / Visão Geral",
        "📋  Cadastro e Regularização",
        "🌍  Cobertura Espacial",
        "⚙️  Implementação e Efetividade",
        "🗺️  Informações Geoespaciais",
    ], label_visibility="collapsed")

    st.markdown(f"""
    <hr style='border-color:#ffffff22;margin:16px 0 8px'>
    <div style='font-size:0.6rem;color:#888;text-align:center;padding-bottom:10px;'>
      SEMA-RS &nbsp;·&nbsp; Dados: SEUC/RS<br>v1.0
    </div>""", unsafe_allow_html=True)


# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='header-bar'>
  Plataforma oficial de dados do Sistema Estadual de Unidades de Conservação do Rio Grande do Sul &nbsp;|&nbsp; SEUC/RS
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MENU
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "🏠  Menu / Visão Geral":
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,{VERDE} 55%,#2E7D32);
                border-radius:10px;padding:28px 36px;margin-bottom:20px;color:white;'>
      <div style='font-size:.85rem;opacity:.75;margin-bottom:4px;'>Plataforma oficial de dados do</div>
      <div style='font-size:1.7rem;font-weight:900;line-height:1.2;'>
        Sistema Estadual de Unidades de Conservação<br>
        <span style='color:{AMARELO};font-size:2.1rem;'>Rio Grande do Sul</span>
      </div>
      <div style='margin-top:12px;font-size:.82rem;opacity:.8;'>
        {len(base)} unidades de conservação catalogadas &nbsp;·&nbsp; Dados atualizados 2024
      </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, len(base), "Unidades de Conservação")
    kpi(c2, f"{base['Área poligonal (ha)'].sum():,.0f} ha", "Área Total", "am")
    kpi(c3, base["Plano de Manejo_b"].sum(), "Com Plano de Manejo", "az")
    kpi(c4, base["Conselho Gestor_b"].sum(), "Com Conselho Gestor", "la")

    st.markdown("<br>", unsafe_allow_html=True)
    g1,g2,g3 = st.columns(3)

    with g1:
        sec("UCs por Esfera")
        d = base["Esfera"].value_counts().reset_index()
        fig = px.pie(d, names="Esfera", values="count", color="Esfera",
                     color_discrete_map=COR_ESFERA, hole=0.48)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        fig.update_layout(**LAYOUT, height=230, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        sec("UCs por Bioma")
        d = base["Bioma"].value_counts().reset_index()
        fig = px.bar(d, x="count", y="Bioma", orientation="h",
                     color="Bioma", color_discrete_map=COR_BIOMA)
        fig.update_traces(texttemplate="%{x}", textposition="outside")
        fig.update_layout(**LAYOUT, height=230, showlegend=False,
                          yaxis_title="", xaxis_title="Qtd")
        st.plotly_chart(fig, use_container_width=True)

    with g3:
        sec("UCs por Grupo SNUC")
        d = base["Grupo"].value_counts().reset_index()
        fig = px.pie(d, names="Grupo", values="count", color="Grupo",
                     color_discrete_map=COR_GRUPO, hole=0.48)
        fig.update_traces(textinfo="percent+label", textfont_size=10)
        fig.update_layout(**LAYOUT, height=230, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    sec("Evolução da criação de UCs por ano")
    d = base.dropna(subset=["Ano de criação"]).groupby(
        ["Ano de criação","Esfera"]).size().reset_index(name="n")
    fig = px.area(d, x="Ano de criação", y="n", color="Esfera",
                  color_discrete_map=COR_ESFERA)
    fig.update_layout(**LAYOUT, height=240,
                      xaxis_title="Ano", yaxis_title="UCs criadas",
                      legend=dict(orientation="h", y=1.08, font_size=11))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# CADASTRO E REGULARIZAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📋  Cadastro e Regularização":
    with st.expander("🔎 Filtros", expanded=True):
        fc1,fc2,fc3,fc4 = st.columns(4)
        f_esf = fc1.multiselect("Esfera",  sorted(base["Esfera"].dropna().unique()),
                                default=sorted(base["Esfera"].dropna().unique()), key="cr_e")
        f_bio = fc2.multiselect("Bioma",   sorted(base["Bioma"].dropna().unique()),
                                default=sorted(base["Bioma"].dropna().unique()), key="cr_b")
        f_grp = fc3.multiselect("Grupo",   sorted(base["Grupo"].dropna().unique()),
                                default=sorted(base["Grupo"].dropna().unique()), key="cr_g")
        f_cat = fc4.multiselect("Categoria", sorted(base["Categoria SNUC"].dropna().unique()),
                                default=sorted(base["Categoria SNUC"].dropna().unique()), key="cr_c")
    df = base.copy()
    if f_esf: df = df[df["Esfera"].isin(f_esf)]
    if f_bio: df = df[df["Bioma"].isin(f_bio)]
    if f_grp: df = df[df["Grupo"].isin(f_grp)]
    if f_cat: df = df[df["Categoria SNUC"].isin(f_cat)]

    c1,c2,c3,c4,c5 = st.columns(5)
    kpi(c1, len(df), "Total de UCs")
    kpi(c2, f"{df['Área poligonal (ha)'].sum():,.0f}", "Área Total (ha)", "am")
    kpi(c3, df["CNUC_b"].sum(), "Cadastradas no CNUC", "az")
    kpi(c4, df["Shapefile dos limites_b"].sum(), "Com Shapefile", "")
    kpi(c5, df["Plano de Manejo_b"].sum(), "Com Plano de Manejo", "la")

    st.markdown("<br>", unsafe_allow_html=True)
    g1,g2,g3 = st.columns(3)
    with g1:
        sec("Por Esfera")
        d = df["Esfera"].value_counts().reset_index()
        fig = px.pie(d, names="Esfera", values="count", color="Esfera",
                     color_discrete_map=COR_ESFERA, hole=0.5)
        fig.update_traces(textinfo="percent+value")
        fig.update_layout(**LAYOUT, height=220, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        sec("Por Grupo SNUC")
        d = df["Grupo"].value_counts().reset_index()
        fig = px.pie(d, names="Grupo", values="count", color="Grupo",
                     color_discrete_map=COR_GRUPO, hole=0.5)
        fig.update_traces(textinfo="percent+value", textfont_size=9)
        fig.update_layout(**LAYOUT, height=220, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with g3:
        sec("Por Bioma")
        d = df["Bioma"].value_counts().reset_index()
        fig = px.pie(d, names="Bioma", values="count", color="Bioma",
                     color_discrete_map=COR_BIOMA, hole=0.5)
        fig.update_traces(textinfo="percent+value", textfont_size=9)
        fig.update_layout(**LAYOUT, height=220, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    g4,g5 = st.columns(2)
    with g4:
        sec("Categoria SNUC")
        d = df["Categoria SNUC"].value_counts().reset_index()
        fig = px.bar(d, x="Categoria SNUC", y="count", color_discrete_sequence=[VERDE2])
        fig.update_traces(texttemplate="%{y}", textposition="outside")
        fig.update_layout(**LAYOUT, height=230, xaxis_title="", yaxis_title="Qtd")
        st.plotly_chart(fig, use_container_width=True)
    with g5:
        sec("Criação por ano e esfera")
        d = df.dropna(subset=["Ano de criação"]).groupby(
            ["Ano de criação","Esfera"]).size().reset_index(name="n")
        fig = px.area(d, x="Ano de criação", y="n", color="Esfera",
                      color_discrete_map=COR_ESFERA)
        fig.update_layout(**LAYOUT, height=230, xaxis_title="Ano", yaxis_title="Criadas",
                          legend=dict(orientation="h", y=1.08, font_size=10))
        st.plotly_chart(fig, use_container_width=True)

    sec("Listagem de UCs")
    cols = ["Código","Nome","Bioma","Grupo","Esfera","Categoria SNUC",
            "Ano de criação","Área poligonal (ha)","CNUC","Plano de Manejo","Conselho Gestor"]
    st.dataframe(df[[c for c in cols if c in df.columns]].reset_index(drop=True),
                 use_container_width=True, height=280)


# ══════════════════════════════════════════════════════════════════════════════
# COBERTURA ESPACIAL — com mapa de biomas
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🌍  Cobertura Espacial":
    with st.expander("🔎 Filtros", expanded=True):
        fc1,fc2,fc3 = st.columns(3)
        f_esf2 = fc1.multiselect("Esfera", sorted(bio["Esfera_UC"].dropna().unique()),
                                  default=sorted(bio["Esfera_UC"].dropna().unique()), key="ce_e")
        f_bio2 = fc2.multiselect("Bioma SCM", sorted(bio["Bioma_SCM"].dropna().unique()),
                                  default=sorted(bio["Bioma_SCM"].dropna().unique()), key="ce_b")
        f_grp2 = fc3.multiselect("Grupo UC", sorted(bio["Grupo_UC"].dropna().unique()),
                                  default=sorted(bio["Grupo_UC"].dropna().unique()), key="ce_g")
    db = bio.copy()
    if f_esf2: db = db[db["Esfera_UC"].isin(f_esf2)]
    if f_bio2: db = db[db["Bioma_SCM"].isin(f_bio2)]
    if f_grp2: db = db[db["Grupo_UC"].isin(f_grp2)]

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, db["Código"].nunique(), "UCs com dados geoespaciais")
    kpi(c2, f"{db['Area_ha'].sum():,.0f}", "Área Total (ha)", "am")
    kpi(c3, f"{db['Area_ha'].sum()/100:,.1f}", "Área Total (km²)", "az")
    kpi(c4, db["Bioma_SCM"].nunique(), "Biomas presentes", "la")

    # Mapa de biomas
    st.markdown("<br>", unsafe_allow_html=True)
    sec("Mapa de Biomas do RS")

    CORES_MAPA = {
        "Mata Atlântica":                   "#2E7D32",
        "Pampa":                            "#F9A825",
        "Costeiro-Marinho":                 "#0277BD",
        "Mata Atlântica, Pampa":            "#8BC34A",
        "Mata Atlântica, Costeiro-Marinho": "#00ACC1",
        "Pampa, Costeiro-Marinho":          "#AB47BC",
    }

    fig_map = go.Figure()
    for feat in bio_geo["features"]:
        nome = feat["properties"]["name"]
        cor  = CORES_MAPA.get(nome, "#999999")
        geom = feat["geometry"]
        # Normaliza: Polygon → lista de rings, MultiPolygon → achata tudo
        if geom["type"] == "Polygon":
            all_rings = geom["coordinates"]
        else:  # MultiPolygon
            all_rings = [ring for poly in geom["coordinates"] for ring in poly]
        polys = [all_rings]  # mantém compatibilidade com loop abaixo
        for poly in [all_rings]:
            for ring in poly:
                # Coordenadas podem ser [lon, lat] ou [lon, lat, alt]
                lons = [pt[0] for pt in ring]
                lats = [pt[1] for pt in ring]
            fig_map.add_trace(go.Scattergeo(
                lon=lons, lat=lats, mode="lines",
                fill="toself", fillcolor=cor + "99",
                line=dict(color=cor, width=1),
                name=nome,
                hovertemplate=f"<b>{nome}</b><extra></extra>",
                showlegend=True,
            ))

    # Remover duplicatas na legenda
    seen = set()
    for trace in fig_map.data:
        if trace.name in seen:
            trace.showlegend = False
        seen.add(trace.name)

    fig_map.update_layout(
        geo=dict(
            scope="south america",
            center=dict(lat=-29.5, lon=-53.0),
            projection_scale=8,
            showland=True, landcolor="#f5f5f5",
            showocean=True, oceancolor="#dce8f5",
            showcoastlines=True, coastlinecolor="#aaa",
            showframe=False,
            bgcolor="white",
        ),
        height=420,
        margin=dict(t=6,b=6,l=6,r=6),
        legend=dict(orientation="v", x=1.01, y=0.5, font_size=11,
                    bgcolor="rgba(255,255,255,0.85)", bordercolor="#ccc", borderwidth=1),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    g1,g2 = st.columns(2)
    with g1:
        sec("Área (ha) por Bioma SCM")
        d = db.groupby("Bioma_SCM")["Area_ha"].sum().reset_index()
        d = d.sort_values("Area_ha")
        fig = px.bar(d, x="Area_ha", y="Bioma_SCM", orientation="h",
                     color="Bioma_SCM", color_discrete_map=COR_BIOMA)
        fig.update_traces(texttemplate="%{x:,.0f} ha", textposition="outside")
        fig.update_layout(**LAYOUT, height=260, showlegend=False,
                          yaxis_title="", xaxis_title="Hectares")
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        sec("Área (ha) por Esfera")
        d = db.groupby("Esfera_UC")["Area_ha"].sum().reset_index()
        fig = px.pie(d, names="Esfera_UC", values="Area_ha", color="Esfera_UC",
                     color_discrete_map=COR_ESFERA, hole=0.5)
        fig.update_traces(texttemplate="%{label}<br>%{percent:.1%}")
        fig.update_layout(**LAYOUT, height=260, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    sec("Detalhamento geoespacial")
    cols_b = ["Código","Nome_UC","Esfera_UC","Grupo_UC","Bioma_SCM","Area_ha","SNUC","CNUC"]
    st.dataframe(db[[c for c in cols_b if c in db.columns]].reset_index(drop=True),
                 use_container_width=True, height=260)


# ══════════════════════════════════════════════════════════════════════════════
# IMPLEMENTAÇÃO E EFETIVIDADE
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "⚙️  Implementação e Efetividade":
    with st.expander("🔎 Filtros", expanded=True):
        fc1,fc2,fc3 = st.columns(3)
        f_esf3 = fc1.multiselect("Esfera", sorted(base["Esfera"].dropna().unique()),
                                  default=sorted(base["Esfera"].dropna().unique()), key="ie_e")
        f_grp3 = fc2.multiselect("Grupo",  sorted(base["Grupo"].dropna().unique()),
                                  default=sorted(base["Grupo"].dropna().unique()), key="ie_g")
        f_cat3 = fc3.multiselect("Categoria", sorted(base["Categoria SNUC"].dropna().unique()),
                                  default=sorted(base["Categoria SNUC"].dropna().unique()), key="ie_c")
    di = base.copy()
    if f_esf3: di = di[di["Esfera"].isin(f_esf3)]
    if f_grp3: di = di[di["Grupo"].isin(f_grp3)]
    if f_cat3: di = di[di["Categoria SNUC"].isin(f_cat3)]
    total = len(di)

    inds = {
        "Plano de Manejo":       di["Plano de Manejo_b"].sum(),
        "Conselho Gestor":       di["Conselho Gestor_b"].sum(),
        "Zona de Amortecimento": di["ZA_b"].sum(),
        "CNUC":                  di["CNUC_b"].sum(),
        "Shapefile":             di["Shapefile dos limites_b"].sum(),
    }

    cols_kpi = st.columns(5)
    cls_list = ["","am","az","","la"]
    for i, (k,v) in enumerate(inds.items()):
        pct = v/total*100 if total else 0
        kpi(cols_kpi[i], f"{v}/{total}", f"{k} ({pct:.0f}%)", cls_list[i])

    st.markdown("<br>", unsafe_allow_html=True)
    g1,g2 = st.columns([1.2,1])
    with g1:
        sec("Indicadores — Com vs Sem")
        df_ind = pd.DataFrame({
            "Indicador": list(inds.keys()),
            "Com": list(inds.values()),
            "Sem": [total-v for v in inds.values()],
        })
        fig = go.Figure()
        fig.add_bar(name="Com", x=df_ind["Indicador"], y=df_ind["Com"],
                    marker_color=VERDE2, text=df_ind["Com"], textposition="inside",
                    insidetextanchor="middle")
        fig.add_bar(name="Sem", x=df_ind["Indicador"], y=df_ind["Sem"],
                    marker_color="#CFD8DC", text=df_ind["Sem"], textposition="inside",
                    insidetextanchor="middle")
        fig.update_layout(**LAYOUT, barmode="stack", height=280,
                          yaxis_title="Qtd UCs",
                          legend=dict(orientation="h", y=1.08, font_size=11))
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        sec("% de implementação")
        pcts = {k: v/total*100 for k,v in inds.items()}
        cores = [VERDE2 if v>=50 else AMARELO if v>=25 else "#EF5350" for v in pcts.values()]
        fig = go.Figure(go.Bar(
            x=list(pcts.values()), y=list(pcts.keys()), orientation="h",
            marker_color=cores,
            text=[f"{v:.1f}%" for v in pcts.values()], textposition="outside",
        ))
        fig.update_layout(**LAYOUT, height=280,
                          xaxis=dict(range=[0,105], title="%"), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    g3,g4 = st.columns(2)
    with g3:
        sec("Plano de Manejo por Esfera")
        pm = di.groupby("Esfera")["Plano de Manejo_b"].agg(Com="sum",Total="count").reset_index()
        pm["Sem"] = pm["Total"] - pm["Com"]
        fig = go.Figure()
        fig.add_bar(name="Com PM", x=pm["Esfera"], y=pm["Com"], marker_color=VERDE2)
        fig.add_bar(name="Sem PM", x=pm["Esfera"], y=pm["Sem"], marker_color="#CFD8DC")
        fig.update_layout(**LAYOUT, barmode="stack", height=240,
                          legend=dict(orientation="h", y=1.08, font_size=10))
        st.plotly_chart(fig, use_container_width=True)
    with g4:
        sec("Conselho Gestor por Esfera")
        cg = di.groupby("Esfera")["Conselho Gestor_b"].agg(Com="sum",Total="count").reset_index()
        cg["Sem"] = cg["Total"] - cg["Com"]
        fig = go.Figure()
        fig.add_bar(name="Com CG", x=cg["Esfera"], y=cg["Com"], marker_color="#1565C0")
        fig.add_bar(name="Sem CG", x=cg["Esfera"], y=cg["Sem"], marker_color="#CFD8DC")
        fig.update_layout(**LAYOUT, barmode="stack", height=240,
                          legend=dict(orientation="h", y=1.08, font_size=10))
        st.plotly_chart(fig, use_container_width=True)

    sec("Detalhamento de implementação")
    cols_ie = ["Código","Nome","Esfera","Grupo","Categoria SNUC","Plano de Manejo",
               "Fase do Plano de Manejo","Conselho Gestor","ZA","CNUC","Shapefile dos limites"]
    st.dataframe(di[[c for c in cols_ie if c in di.columns]].reset_index(drop=True),
                 use_container_width=True, height=260)


# ══════════════════════════════════════════════════════════════════════════════
# INFORMAÇÕES GEOESPACIAIS — com mapa de municípios
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🗺️  Informações Geoespaciais":
    with st.expander("🔎 Filtros", expanded=True):
        fc1,fc2 = st.columns(2)
        f_bio4 = fc1.multiselect("Bioma", sorted(bmap["Bioma"].dropna().unique()),
                                  default=sorted(bmap["Bioma"].dropna().unique()), key="ge_b")
        f_mun4 = fc2.multiselect("Município",
                                  sorted(mun["Municípios_1"].dropna().unique()), key="ge_m")
    dg = bmap.copy()
    if f_bio4: dg = dg[dg["Bioma"].isin(f_bio4)]
    dm = mun.copy()
    if f_mun4: dm = dm[dm["Municípios_1"].isin(f_mun4)]
    if f_mun4: dg = dg[dg["Código"].isin(dm["Código"].unique())]

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, len(dg), "UCs no filtro")
    kpi(c2, dg["Bioma"].nunique(), "Biomas", "am")
    kpi(c3, dm["Municípios_1"].nunique(), "Municípios", "az")
    kpi(c4, dm["Código"].nunique(), "UCs com dados municipais", "")

    # Mapa de municípios colorido por quantidade de UCs
    st.markdown("<br>", unsafe_allow_html=True)
    sec("Mapa — Municípios do RS com UCs")

    ucs_por_mun = (dm.groupby("Municípios_1")["Código"].nunique()
                   .reset_index().rename(columns={"Código":"n_ucs","Municípios_1":"NM_MUN"}))

    # Adicionar n_ucs às propriedades do GeoJSON
    mun_dict = dict(zip(ucs_por_mun["NM_MUN"], ucs_por_mun["n_ucs"]))
    for feat in mun_geo["features"]:
        nm = feat["properties"].get("NM_MUN","")
        feat["properties"]["n_ucs"] = mun_dict.get(nm, 0)

    fig_mun = px.choropleth(
        ucs_por_mun,
        geojson=mun_geo,
        locations="NM_MUN",
        featureidkey="properties.NM_MUN",
        color="n_ucs",
        color_continuous_scale=[
            [0.0, "#f0f4f0"],
            [0.2, "#a5d6a7"],
            [0.5, "#4caf50"],
            [0.8, "#2E7D32"],
            [1.0, "#1A5C2A"],
        ],
        labels={"n_ucs": "Nº de UCs"},
        hover_name="NM_MUN",
        hover_data={"n_ucs": True, "NM_MUN": False},
    )
    fig_mun.update_geos(
        fitbounds="locations", visible=False,
        bgcolor="white",
    )
    fig_mun.update_layout(
        height=440,
        margin=dict(t=6,b=6,l=6,r=6),
        paper_bgcolor="white",
        coloraxis_colorbar=dict(title="Nº de UCs", thickness=14, len=0.6),
    )
    st.plotly_chart(fig_mun, use_container_width=True)

    g1,g2 = st.columns(2)
    with g1:
        sec("Top 20 municípios com mais UCs")
        top = (dm.groupby("Municípios_1")["Código"].nunique()
               .reset_index().rename(columns={"Código":"UCs","Municípios_1":"Município"})
               .sort_values("UCs", ascending=False).head(20))
        fig = px.bar(top, x="UCs", y="Município", orientation="h",
                     color_discrete_sequence=[VERDE2])
        fig.update_traces(texttemplate="%{x}", textposition="outside")
        fig.update_layout(**LAYOUT, height=420,
                          yaxis=dict(autorange="reversed"),
                          xaxis_title="Nº de UCs", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        sec("UCs por Bioma")
        d = dg["Bioma"].value_counts().reset_index()
        fig = px.pie(d, names="Bioma", values="count", color="Bioma",
                     color_discrete_map=COR_BIOMA, hole=0.46)
        fig.update_traces(textinfo="percent+label", textfont_size=10)
        fig.update_layout(**LAYOUT, height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    t1,t2 = st.columns(2)
    with t1:
        sec("UCs geoespaciais")
        st.dataframe(dg[["Código","Nome","Bioma"]].reset_index(drop=True),
                     use_container_width=True, height=220)
    with t2:
        sec("UCs × Municípios")
        cols_m = [c for c in ["Código","Nome","Municípios_1","UF"] if c in dm.columns]
        st.dataframe(dm[cols_m].reset_index(drop=True),
                     use_container_width=True, height=220)
