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
# ─── CSS ──────────────────────────────────────────────────────────────────────
# Carregar background em base64
import base64
with open("data/bg.png", "rb") as _f:
    _bg64 = base64.b64encode(_f.read()).decode()

st.markdown(f"""
<style>
  /* ── Fundo com imagem do projeto ── */
  .main {{
      background-image: url("data:image/png;base64,{_bg64}") !important;
      background-size: cover !important;
      background-attachment: fixed !important;
      background-position: center !important;
  }}
  .block-container {{
      background: transparent !important;
      padding-top: 0.8rem !important;
  }}

  /* ── Sidebar branca com borda verde ── */
  [data-testid="stSidebar"] {{
      background-color: {BRANCO} !important;
      border-right: 4px solid {VERDE} !important;
  }}
  [data-testid="stSidebar"] * {{ color: {VERDE} !important; }}
  [data-testid="stSidebar"] .stRadio label {{
      font-size: 0.85rem; font-weight: 500;
      color: #333 !important; padding: 4px 0;
  }}

  /* ── Header topo ── */
  .header-bar {{
      background: {VERDE}; color: {BRANCO};
      padding: 9px 20px; font-size: 13px; font-weight: 600;
      border-radius: 6px; margin-bottom: 14px;
      text-align: center; letter-spacing: 0.4px;
  }}

  /* ── KPI cards — efeito vidro ── */
  .kpi-wrap {{
      background: rgba(255,255,255,0.55) !important;
      backdrop-filter: blur(10px) !important;
      -webkit-backdrop-filter: blur(10px) !important;
      border-radius: 8px;
      padding: 14px 16px 10px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      border-top: 4px solid {VERDE2};
      height: 100%;
  }}
  .kpi-wrap.am {{ border-top-color: {AMARELO}; }}
  .kpi-wrap.az {{ border-top-color: #2f4c9c; }}
  .kpi-wrap.la {{ border-top-color: #bf5b17; }}
  .kpi-wrap.ro {{ border-top-color: #C62828; }}
  .kpi-num  {{ font-size: 2rem; font-weight: 800; color: {VERDE}; line-height: 1.1; }}
  .kpi-lbl  {{ font-size: 0.74rem; color: #555; margin-top: 3px; }}

  /* ── Títulos de seção ── */
  .sec-title {{
      font-size: 0.92rem; font-weight: 700; color: {VERDE};
      border-bottom: 2px solid {AMARELO};
      padding-bottom: 3px; margin: 16px 0 8px;
  }}

  /* ── Gráficos e tabelas — fundo transparente/vidro ── */
  [data-testid="stPlotlyChart"] > div {{
      background: rgba(255,255,255,0.45) !important;
      backdrop-filter: blur(8px) !important;
      -webkit-backdrop-filter: blur(8px) !important;
      border-radius: 10px !important;
      padding: 6px !important;
  }}
  [data-testid="stDataFrame"] > div {{
      background: rgba(255,255,255,0.55) !important;
      backdrop-filter: blur(8px) !important;
      -webkit-backdrop-filter: blur(8px) !important;
      border-radius: 10px !important;
  }}

  /* ── Expander de filtros — vidro ── */
  [data-testid="stExpander"] {{
      background: rgba(255,255,255,0.55) !important;
      backdrop-filter: blur(10px) !important;
      -webkit-backdrop-filter: blur(10px) !important;
      border-radius: 8px !important;
      border: 1px solid rgba(255,255,255,0.7) !important;
  }}
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

LAYOUT = dict(margin=dict(t=6,b=6,l=6,r=6), paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)", font_family="Arial")


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:20px 0 12px'>
      <div style='font-size:1.8rem;font-weight:900;color:{VERDE};letter-spacing:2px;'>SEUC/RS</div>
      <div style='font-size:0.65rem;color:#888;margin-top:2px;line-height:1.5;'>
        Sistema Estadual de<br>Unidades de Conservação<br>Rio Grande do Sul
      </div>
    </div>
    <hr style='border-color:#e0e0e0;margin:4px 0 12px'>
    """, unsafe_allow_html=True)

    pagina = st.radio("", [
        "🏠  Visão Geral",
        "📋  Cadastro e Regularização",
        "🌍  Cobertura Espacial",
        "⚙️  Implementação e Efetividade",
        "🗺️  Informações Geoespaciais",
    ], label_visibility="collapsed")

    st.markdown(f"""
    <hr style='border-color:#e0e0e0;margin:16px 0 8px'>
    <div style='font-size:0.6rem;color:#999;text-align:center;padding-bottom:10px;'>
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
if pagina == "🏠  Visão Geral":

    # Banner principal — fiel ao Power BI (fundo vermelho + aba verde SEUC/RS)
    st.markdown(f"""
    <div style='display:flex;align-items:stretch;margin-bottom:32px;
                box-shadow:0 4px 16px rgba(0,0,0,0.13);border-radius:6px;overflow:hidden;'>
      <div style='background:#CC0000;padding:28px 32px;flex:1;'>
        <div style='font-size:1rem;font-weight:600;color:white;line-height:1.3;'>
          Plataforma oficial de dados do<br>
          Sistema Estadual de Unidades de Conservação do
        </div>
        <div style='font-size:2.4rem;font-weight:900;color:white;line-height:1.1;margin-top:4px;'>
          Rio Grande do Sul
        </div>
        <div style='height:5px;background:{AMARELO};margin-top:14px;border-radius:2px;'></div>
      </div>
      <div style='background:{VERDE};writing-mode:vertical-rl;text-orientation:mixed;
                  transform:rotate(180deg);padding:18px 14px;
                  font-size:1.5rem;font-weight:900;color:white;letter-spacing:3px;
                  display:flex;align-items:center;justify-content:center;min-width:64px;'>
        SEUC/RS
      </div>
    </div>

    <style>
    .card-menu {{
        background: white;
        border-radius: 12px;
        border: 1.5px solid #e0e0e0;
        padding: 32px 24px 24px;
        text-align: center;
        transition: box-shadow 0.25s, border-color 0.25s;
        cursor: default;
        height: 100%;
        position: relative;
        overflow: hidden;
    }}
    .card-menu:hover {{
        box-shadow: 0 6px 24px rgba(26,92,42,0.15);
        border-color: {VERDE};
    }}
    .card-menu .icone {{
        font-size: 3.5rem;
        margin-bottom: 14px;
        display: block;
    }}
    .card-menu .titulo {{
        font-size: 1rem;
        font-weight: 800;
        color: {VERDE};
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 14px;
    }}
    .card-menu .texto {{
        font-size: 0.82rem;
        color: #444;
        line-height: 1.65;
        text-align: justify;
        display: none;
    }}
    .card-menu:hover .texto {{
        display: block;
    }}
    .card-menu:hover .icone {{
        display: none;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 3 cards lado a lado
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class='card-menu'>
          <span class='icone'>🌿</span>
          <div class='titulo'>SEUC/RS</div>
          <div class='texto'>
            Este painel é resultado da elaboração do Plano do Sistema Estadual de Unidades de
            Conservação do Rio Grande do Sul, iniciativa coordenada pela SEMA que possibilitou
            a organização e disponibilização pública de dados da relação de Unidades de
            Conservação e outras áreas naturais protegidas existentes no Estado. Esta plataforma
            está integrada ao Cadastro do SEUC/RS mas inclui também em sua amostra UCs e áreas
            não cadastradas, perpassando as diferentes esferas de governo e reservas particulares
            do patrimônio natural.
          </div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='card-menu'>
          <span class='icone'>⚙️</span>
          <div class='titulo'>Como Funciona</div>
          <div class='texto'>
            Como qualquer base de dados, é necessária a atualização e o preenchimento de lacunas
            de informação periodicamente. Se você é gestor, proprietário de UC ou área natural
            protegida do RS ainda não adequada ao SNUC/SEUC ou ainda se tem interesse em
            cadastrar ou inserir informações oficiais, acesse aqui para entrar em contato.
          </div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class='card-menu'>
          <span class='icone'>💡</span>
          <div class='titulo'>Importância</div>
          <div class='texto'>
            Esta plataforma tem por finalidade popularizar a consulta e o acesso a dados e
            informações oficiais e atualizadas das Unidades de Conservação do Estado do Rio
            Grande do Sul para a sociedade em geral, permitindo a pesquisa e/ou o
            acompanhamento de indicadores sobre o estado de implementação do SEUC/RS.
          </div>
        </div>""", unsafe_allow_html=True)

    # Rodapé informativo
    st.markdown(f"""
    <div style='margin-top:32px;padding:14px 20px;background:#f5f5f5;border-radius:8px;
                border-left:4px solid {AMARELO};font-size:0.78rem;color:#555;'>
      <strong style='color:{VERDE};'>SEMA-RS</strong> &nbsp;·&nbsp;
      Secretaria do Meio Ambiente e Infraestrutura do Rio Grande do Sul &nbsp;·&nbsp;
      Dados atualizados 2024 &nbsp;·&nbsp; {len(base)} Unidades de Conservação catalogadas
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CADASTRO E REGULARIZAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📋  Cadastro e Regularização":

    # ── 5 Filtros ──────────────────────────────────────────────────────────
    # CSS para traduzir textos do multiselect para português
    st.markdown("""
    <style>
    [data-baseweb="select"] [data-testid="stMultiSelectChevronButton"] ~ div span,
    span[data-testid="stMultiSelectPlaceholder"] { display: none !important; }
    div[data-baseweb="select"] input::placeholder { color: #999; font-size: 0.8rem; }
    button[data-testid="stBaseButton-secondary"] span { font-size: 0.75rem; }
    </style>
    """, unsafe_allow_html=True)

    with st.expander("🔎 Filtros", expanded=True):
        fc1,fc2,fc3,fc4,fc5 = st.columns(5)
        f_bio = fc1.multiselect("Bioma",
                    sorted(base["Bioma"].dropna().unique()),
                    placeholder="Selecione...", key="cr_b")
        f_tip = fc2.multiselect("Tipo",
                    sorted(base["NomenclaturaSNUC"].dropna().unique()),
                    placeholder="Selecione...", key="cr_t")
        f_grp = fc3.multiselect("Grupo",
                    sorted(base["Grupo"].dropna().unique()),
                    placeholder="Selecione...", key="cr_g")
        f_esf = fc4.multiselect("Esfera",
                    sorted(base["Esfera"].dropna().unique()),
                    placeholder="Selecione...", key="cr_e")
        f_cat = fc5.multiselect("Categoria SNUC",
                    sorted(base["Categoria SNUC"].dropna().unique()),
                    placeholder="Selecione...", key="cr_c")

    df = base.copy()
    if f_bio: df = df[df["Bioma"].isin(f_bio)]
    if f_tip: df = df[df["NomenclaturaSNUC"].isin(f_tip)]
    if f_grp: df = df[df["Grupo"].isin(f_grp)]
    if f_esf: df = df[df["Esfera"].isin(f_esf)]
    if f_cat: df = df[df["Categoria SNUC"].isin(f_cat)]

    # ── 4 KPI cards ────────────────────────────────────────────────────────
    k1,k2,k3,k4 = st.columns(4)
    kpi(k1, f"{df['Área poligonal (ha)'].sum():,.2f}", "Áreas Protegidas (ha)")
    kpi(k2, df["CNUC_b"].sum() + df[df["Cadastro do SEUC/RS"]=="Sim"].shape[0]//2,
        "Unidades de Conservação", "am")
    area_nat = df[df["ANP_UC"]=="Área natural protegida"].shape[0]
    kpi(k3, area_nat, "Áreas Naturais Protegidas", "az")
    kpi(k4, len(df), "Áreas Protegidas no RS", "la")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Linha 1: 5 roscas ──────────────────────────────────────────────────
    sec("Distribuição por categoria")
    r1,r2,r3,r4,r5 = st.columns(5)

    def rosca(col, titulo, serie, mapa_cores=None, key=""):
        d = serie.value_counts().reset_index()
        d.columns = ["cat","n"]
        total = d["n"].sum()
        # Calcular labels externos: "N (X%)" igual ao Power BI
        d["pct"] = (d["n"] / total * 100).round(0).astype(int)
        d["label"] = d.apply(lambda r: f"{r['n']} ({r['pct']}%)", axis=1)
        kwargs = dict(color="cat", color_discrete_map=mapa_cores) if mapa_cores else \
                 dict(color_discrete_sequence=["#2f4c9c","#2E7D32","#bf5b17","#7f8080","#f9b60e"])
        fig = px.pie(d, names="cat", values="n", hole=0.55,
                     custom_data=["label"], **kwargs)
        fig.update_traces(
            texttemplate="%{customdata[0]}",
            textposition="outside",
            textfont_size=10,
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
            pull=[0.02]*len(d),
        )
        # Total no centro — fonte menor
        fig.add_annotation(
            text=f"<b>{total}</b>", x=0.5, y=0.5,
            font=dict(size=13, color=VERDE),
            showarrow=False
        )
        fig.update_layout(
            **LAYOUT, height=210,
            showlegend=True,
            legend=dict(orientation="h", y=-0.18, font_size=9,
                        x=0.5, xanchor="center"),
        )
        col.markdown(f"<div class='sec-title' style='font-size:0.78rem;'>{titulo}</div>",
                     unsafe_allow_html=True)
        col.plotly_chart(fig, use_container_width=True, key=f"rosca_{key}")

    rosca(r1, "Esfera", df["Esfera"],
          {"Federal":"#2f4c9c","Estadual":"#2E7D32","Municipal":"#bf5b17"}, key="esfera")
    rosca(r2, "SEUC", df["Cadastro do SEUC/RS"],
          {"Sim":"#2E7D32","Não":"#CFD8DC"}, key="seuc")
    rosca(r3, "CNUC", df["CNUC"],
          {"Sim":"#2E7D32","Não":"#CFD8DC"}, key="cnuc")
    rosca(r4, "SNUC", df["CadastroSNUC"].map({True:"Sim",False:"Não"}) if df["CadastroSNUC"].dtype==bool
                      else df["CadastroSNUC"],
          {"Sim":"#2E7D32","Não":"#CFD8DC"}, key="snuc")
    rosca(r5, "Grupo", df["Grupo"],
          {"Proteção Integral":"#1A5C2A","Uso Sustentável":"#f9b60e","Não se aplica":"#7f8080"},
          key="grupo")

    # ── Linha 2: barras SNUC + barras Biomas ───────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)

    with g1:
        sec("Categoria SNUC")
        d = df["Categoria SNUC"].value_counts().reset_index()
        d.columns = ["Categoria","n"]
        d = d.sort_values("Categoria")  # ordem alfabética igual ao Power BI
        fig = go.Figure(go.Bar(
            x=d["Categoria"], y=d["n"],
            marker_color="#7BC8F0",
            marker_line_width=0,
            text=d["n"],
            textposition="outside",
            textfont=dict(size=11, color="#444"),
        ))
        fig.update_layout(
            **LAYOUT,
            height=260,
            bargap=0,          # sem espaço entre barras = efeito degrau
            xaxis=dict(showgrid=False, showline=False, tickfont_size=10),
            yaxis=dict(showgrid=False, showticklabels=False, showline=False),
        )
        st.plotly_chart(fig, use_container_width=True, key="snuc_bar")

    with g2:
        sec("Biomas")
        d = df["Bioma"].value_counts().reset_index()
        d.columns = ["Bioma","n"]
        d = d.sort_values("n", ascending=True)
        fig = px.bar(d, x="n", y="Bioma", orientation="h",
                     color="Bioma", color_discrete_map=COR_BIOMA)
        fig.update_traces(texttemplate="%{x}", textposition="outside")
        fig.update_layout(**LAYOUT, height=280, showlegend=False,
                          xaxis_title="", yaxis_title="",
                          xaxis=dict(showgrid=False, showticklabels=False))
        st.plotly_chart(fig, use_container_width=True)

    # ── Tabela ─────────────────────────────────────────────────────────────
    sec("Listagem de UCs")
    cols_tab = ["Nome","Bioma","Esfera","Plano de Manejo","Cadastro do SEUC/RS",
                "CNUC","Grupo","Área poligonal (ha)","Órgão gestor"]
    st.dataframe(
        df[[c for c in cols_tab if c in df.columns]].reset_index(drop=True),
        use_container_width=True, height=220
    )

    # ── Gráfico temporal: área acumulada ───────────────────────────────────
    sec("Área acumulada (ha)")
    df_t = df.dropna(subset=["Ano de criação"]).copy()
    df_t["Ano de criação"] = df_t["Ano de criação"].astype(int)
    df_t = df_t.sort_values("Ano de criação")
    df_t["Área acumulada"] = df_t["Área poligonal (ha)"].cumsum()
    anos_grp = df_t.groupby("Ano de criação")["Área acumulada"].max().reset_index()
    fig_t = px.area(anos_grp, x="Ano de criação", y="Área acumulada",
                    color_discrete_sequence=[VERDE2],
                    labels={"Área acumulada":"Área (ha)","Ano de criação":"Ano"})
    fig_t.update_traces(
        line_color=VERDE,
        fillcolor="rgba(46,125,50,0.18)",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} ha<extra></extra>",
    )
    # Anotações nos picos visíveis
    for _, row in anos_grp[anos_grp["Ano de criação"].isin(
            [1950,1960,1970,1980,1990,2000,2010,2020])].iterrows():
        fig_t.add_annotation(
            x=row["Ano de criação"], y=row["Área acumulada"],
            text=f"{row['Área acumulada']/1000:.0f} Mil",
            showarrow=False, yshift=12, font_size=9, font_color="#444"
        )
    fig_t.update_layout(**LAYOUT, height=220,
                        xaxis_title="", yaxis_title="ha",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#eee"))
    st.plotly_chart(fig_t, use_container_width=True)


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
