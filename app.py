import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, base64, re, unicodedata

def slugify(txt):
    """ASCII puro — a key do botão e o seletor CSS precisam ser idênticos."""
    t = unicodedata.normalize("NFKD", str(txt))
    t = t.encode("ascii", "ignore").decode()
    return re.sub(r"\W+", "_", t).strip("_")

st.set_page_config(page_title="SEUC/RS", page_icon="🌿",
                   layout="wide", initial_sidebar_state="expanded")

# ── Cores ──────────────────────────────────────────────────────────────────────
VERDE  = "#1A5C2A"
VERDE2 = "#2E7D32"
AMAR   = "#FFD600"
AZUL   = "#6a9ab0"      # cor única para barras
AZUL_CLARO = "#a8d5f5"  # preenchimento das barras (estilo Power BI)
AZUL_BORDA = "#2196f3"  # borda das barras
BRANCO = "#FFFFFF"

PAL_ROSCA = ["#5b7fa6","#4a8c5c","#a67c5b","#c5cfc5","#8fae8f","#9b8fb0"]
COR_SN    = {"Sim":"#4a8c5c","Não":"#c5cfc5","Não se aplica":"#9b8fb0"}
COR_ESF_R = {"Federal":"#5b7fa6","Estadual":"#4a8c5c","Municipal":"#a67c5b"}
COR_GRP_R = {"Proteção Integral":"#4a8c5c","Uso Sustentável":"#8fae8f","Não se aplica":"#c5cfc5"}
COR_BIOMA_MAPA = {
    "Mata Atlântica":                   "#4a8c5c",
    "Pampa":                            "#c9b96e",
    "Costeiro-Marinho":                 "#5b7fa6",
    "Mata Atlântica, Pampa":            "#8fae8f",
    "Mata Atlântica, Costeiro-Marinho": "#7a9eb0",
    "Pampa, Costeiro-Marinho":          "#9b8fb0",
}

# ── Fundo base64 ───────────────────────────────────────────────────────────────
with open("data/bg_v3.jpg","rb") as _f:
    _BG = base64.b64encode(_f.read()).decode()

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""<style>
/* fundo */
[data-testid="stAppViewContainer"]>.main{{
  background-image:url("data:image/jpeg;base64,{_BG}") !important;
  background-size:cover!important; background-attachment:fixed!important;
  background-position:center top!important;
}}
.block-container{{background:transparent!important;padding-top:.8rem!important;
  max-width:100%!important;}}
/* sidebar */
[data-testid="stSidebar"]{{background:{BRANCO}!important;
  border-right:4px solid {VERDE}!important;}}
[data-testid="stSidebar"] *{{color:{VERDE}!important;}}
[data-testid="stSidebar"] .stRadio label{{font-size:.85rem;font-weight:500;
  color:#333!important;padding:4px 0;}}
/* header */
.hdr{{background:{VERDE};color:#fff;padding:9px 20px;font-size:13px;
  font-weight:600;border-radius:6px;margin-bottom:14px;text-align:center;}}
/* kpi */
.kpi{{background:rgba(255,255,255,.62);backdrop-filter:blur(12px);
  -webkit-backdrop-filter:blur(12px);border-radius:8px;padding:14px 16px 10px;
  box-shadow:0 2px 10px rgba(0,0,0,.07);border-top:4px solid {VERDE2};}}
.kpi.am{{border-top-color:{AMAR};}} .kpi.az{{border-top-color:#2f4c9c;}}
.kpi.la{{border-top-color:#bf5b17;}}
.kpi-n{{font-size:1.9rem;font-weight:800;color:{VERDE};line-height:1.1;}}
.kpi-l{{font-size:.73rem;color:#555;margin-top:3px;}}
/* seção */
.st{{font-size:.9rem;font-weight:700;color:{VERDE};
  border-bottom:2px solid {AMAR};padding-bottom:3px;margin:14px 0 6px;}}
/* glassmorphism nos charts e tabelas + moldura cinza clara arredondada */
[data-testid="stPlotlyChart"]>div{{
  background:rgba(255,255,255,.52)!important;
  backdrop-filter:blur(10px)!important;-webkit-backdrop-filter:blur(10px)!important;
  border:1px solid #dcdcdc!important;
  border-radius:12px!important;
  padding:6px!important;
  overflow:hidden!important;
  box-shadow:0 1px 3px rgba(0,0,0,.04)!important;}}
[data-testid="stDataFrame"]>div{{
  background:rgba(255,255,255,.62)!important;
  backdrop-filter:blur(10px)!important;
  border:1px solid #dcdcdc!important;
  border-radius:12px!important;
  overflow:hidden!important;
  box-shadow:0 1px 3px rgba(0,0,0,.04)!important;}}
[data-testid="stExpander"]{{background:rgba(255,255,255,.62)!important;
  backdrop-filter:blur(12px)!important;border-radius:12px!important;
  border:1px solid #dcdcdc!important;}}

/* ═══ ELIMINAR TODA barra de rolagem dos gráficos Plotly ═══ */
[data-testid="stPlotlyChart"],
[data-testid="stPlotlyChart"] .stPlotlyChart,
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container,
[data-testid="stPlotlyChart"] .svg-container,
[data-testid="stPlotlyChart"] .plotly,
[data-testid="stPlotlyChart"] .main-svg{{
  overflow:hidden!important;
  overflow-x:hidden!important;
  overflow-y:hidden!important;
  scrollbar-width:none!important;
  -ms-overflow-style:none!important;
  padding:0!important;
  max-height:none!important;
}}
[data-testid="stPlotlyChart"] *::-webkit-scrollbar,
[data-testid="stPlotlyChart"]::-webkit-scrollbar{{
  display:none!important; width:0!important; height:0!important;
}}
/* containers pais não devem cortar nem rolar */
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="column"],
[data-testid="stHorizontalBlock"]{{
  overflow:visible!important;
}}
/* modebar do plotly some (evita altura extra) */
.modebar{{display:none!important;}}

/* ═══ cursor: mãozinha nos gráficos, nunca a cruz de arrasto ═══ */
[data-testid="stPlotlyChart"] .nsewdrag,
[data-testid="stPlotlyChart"] .drag,
[data-testid="stPlotlyChart"] .draglayer,
[data-testid="stPlotlyChart"] .draglayer *,
[data-testid="stPlotlyChart"] .points path,
[data-testid="stPlotlyChart"] .point,
[data-testid="stPlotlyChart"] .trace,
[data-testid="stPlotlyChart"] .slice,
[data-testid="stPlotlyChart"] .bars path,
[data-testid="stPlotlyChart"] .js-plotly-plot .plotly .cursor-crosshair,
[data-testid="stPlotlyChart"] .js-plotly-plot .plotly .cursor-move,
[data-testid="stPlotlyChart"] .js-plotly-plot .plotly .cursor-pointer{{
  cursor:pointer!important;
}}
/* neutraliza as classes de cursor que o Plotly injeta inline */
[data-testid="stPlotlyChart"] .cursor-ew-resize,
[data-testid="stPlotlyChart"] .cursor-ns-resize,
[data-testid="stPlotlyChart"] .cursor-nesw-resize,
[data-testid="stPlotlyChart"] .cursor-nwse-resize,
[data-testid="stPlotlyChart"] .cursor-col-resize,
[data-testid="stPlotlyChart"] .cursor-row-resize{{
  cursor:pointer!important;
}}

/* ═══ legenda clicável (pills) abaixo das roscas ═══ */
.lg-wrap [data-testid="stButton"]{{margin:0!important;}}
.lg-wrap [data-testid="stButton"] button,
div[data-testid="column"] [data-testid="stButton"] button.lgbtn{{
  all:unset;
}}
[data-testid="column"] [data-testid="stButton"] button{{
  display:flex!important;
  align-items:center!important;
  justify-content:flex-start!important;
  gap:6px!important;
  padding:0 9px!important;
  min-height:0!important;
  height:23px!important;
  font-size:.655rem!important;
  font-weight:500!important;
  line-height:1!important;
  border-radius:12px!important;
  margin:0 0 3px 0!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  background:rgba(255,255,255,.72)!important;
  border:1px solid rgba(0,0,0,.10)!important;
  color:#4a4a4a!important;
  box-shadow:none!important;
  transition:background .12s,border-color .12s!important;
}}
[data-testid="column"] [data-testid="stButton"] button:hover{{
  background:rgba(255,255,255,.95)!important;
  border-color:rgba(0,0,0,.22)!important;
}}
[data-testid="column"] [data-testid="stButton"] button p{{
  font-size:.655rem!important;
  font-weight:500!important;
  margin:0!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
}}
/* o botão "Limpar" não é pill */
.st-key-cr_limpar button{{
  height:32px!important; border-radius:6px!important;
  justify-content:center!important; font-size:.72rem!important;
}}
</style>""", unsafe_allow_html=True)

# ── Dados ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    base = pd.read_excel("data/BaseSeuc.xlsx")
    bio  = pd.read_excel("data/BIOMAS_SCM_12M.xlsx")
    mun  = pd.read_excel("data/Municipios.xlsx")
    bmap = pd.read_excel("data/BioMap.xlsx")
    base["Ano de criação"]      = pd.to_numeric(base["Ano de criação"],errors="coerce")
    base["Área poligonal (ha)"] = pd.to_numeric(base["Área poligonal (ha)"],errors="coerce").fillna(0)
    bio["Area_ha"]              = pd.to_numeric(bio["Area_ha"],errors="coerce").fillna(0)
    for c in ["Plano de Manejo","Conselho Gestor","CNUC","Shapefile dos limites","ZA"]:
        if c in base.columns:
            base[c+"_b"] = base[c].astype(str).str.strip().str.lower()=="sim"
    return base,bio,mun,bmap

@st.cache_data
def load_geo():
    def _to2d(coords):
        """Remove a 3ª coordenada (altitude) — o Plotly só aceita [lon, lat]."""
        if isinstance(coords[0], (int, float)):
            return coords[:2]
        return [_to2d(c) for c in coords]

    with open("data/RS_Municipios_2024.geojson") as f: mg=json.load(f)
    with open("data/RS_Biomas_SCM.geojson")     as f: bg=json.load(f)
    with open("data/RS_Biomas_simp.geojson")    as f: bs=json.load(f)

    for _f in bg["features"]:
        _f["geometry"]["coordinates"] = _to2d(_f["geometry"]["coordinates"])
        _f["id"] = _f["properties"]["name"]
    for _f in mg["features"]:
        _f["geometry"]["coordinates"] = _to2d(_f["geometry"]["coordinates"])

    return mg,bg,bs

base,bio,mun,bmap        = load()
mun_geo,bio_geo,bio_simp = load_geo()

# ── Helpers ────────────────────────────────────────────────────────────────────
def kpi(col,num,lbl,cls=""):
    col.markdown(f"<div class='kpi {cls}'><div class='kpi-n'>{num}</div>"
                 f"<div class='kpi-l'>{lbl}</div></div>",unsafe_allow_html=True)
def sec(t):
    st.markdown(f"<div class='st'>{t}</div>",unsafe_allow_html=True)

# Plotly layout base — transparente, sem scroll
LY = dict(margin=dict(t=30,b=10,l=10,r=10),
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font_family="Arial",
          font_color="#333")

def chart(fig, h, key):
    """Renderiza gráfico com altura fixa via CSS inline para eliminar scroll."""
    fig.update_layout(height=h)
    st.plotly_chart(fig, use_container_width=True, key=key,
                    config={"displayModeBar":False})

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""<div style='text-align:center;padding:20px 0 10px'>
      <div style='font-size:1.8rem;font-weight:900;color:{VERDE};'>SEUC/RS</div>
      <div style='font-size:.63rem;color:#888;line-height:1.5;'>
        Sistema Estadual de<br>Unidades de Conservação<br>Rio Grande do Sul</div>
    </div><hr style='border-color:#e0e0e0;margin:4px 0 12px'>""",
    unsafe_allow_html=True)
    pag = st.radio("",["🏠  Visão Geral","📋  Cadastro e Regularização",
        "🌍  Cobertura Espacial","⚙️  Implementação e Efetividade",
        "🗺️  Informações Geoespaciais"],label_visibility="collapsed")
    st.markdown(f"""<hr style='border-color:#e0e0e0;margin:16px 0 8px'>
    <div style='font-size:.6rem;color:#999;text-align:center;padding-bottom:10px;'>
      SEMA-RS · Dados: SEUC/RS · v1.0</div>""",unsafe_allow_html=True)

st.markdown("<div class='hdr'>Plataforma oficial de dados do Sistema Estadual de "
            "Unidades de Conservação do Rio Grande do Sul | SEUC/RS</div>",
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════
if pag=="🏠  Visão Geral":
    st.markdown(f"""
    <div style='display:flex;align-items:stretch;margin-bottom:28px;
         box-shadow:0 4px 16px rgba(0,0,0,.13);border-radius:6px;overflow:hidden;'>
      <div style='background:#CC0000;padding:28px 32px;flex:1;'>
        <div style='font-size:1rem;font-weight:600;color:#fff;line-height:1.3;'>
          Plataforma oficial de dados do<br>Sistema Estadual de Unidades de Conservação do</div>
        <div style='font-size:2.3rem;font-weight:900;color:#fff;line-height:1.1;margin-top:4px;'>
          Rio Grande do Sul</div>
        <div style='height:5px;background:{AMAR};margin-top:14px;border-radius:2px;'></div>
      </div>
      <div style='background:{VERDE};writing-mode:vertical-rl;transform:rotate(180deg);
           padding:18px 14px;font-size:1.4rem;font-weight:900;color:#fff;
           letter-spacing:3px;display:flex;align-items:center;min-width:60px;'>
        SEUC/RS</div>
    </div>
    <style>
    .card-m{{background:rgba(255,255,255,.7);backdrop-filter:blur(10px);
      border-radius:12px;border:1.5px solid #e0e0e0;padding:28px 22px 22px;
      text-align:center;height:100%;}}
    .card-m:hover{{box-shadow:0 6px 24px rgba(26,92,42,.15);border-color:{VERDE};}}
    .card-m .ico{{font-size:3.2rem;margin-bottom:12px;display:block;}}
    .card-m .tit{{font-size:.95rem;font-weight:800;color:{VERDE};
      letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;}}
    .card-m .txt{{font-size:.8rem;color:#444;line-height:1.65;text-align:justify;
      display:none;}}
    .card-m:hover .txt{{display:block;}} .card-m:hover .ico{{display:none;}}
    </style>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='card-m'><span class='ico'>🌿</span>
        <div class='tit'>SEUC/RS</div><div class='txt'>Este painel é resultado da elaboração
        do Plano do Sistema Estadual de Unidades de Conservação do Rio Grande do Sul,
        iniciativa coordenada pela SEMA que possibilitou a organização e disponibilização
        pública de dados da relação de Unidades de Conservação e outras áreas naturais
        protegidas existentes no Estado. Esta plataforma está integrada ao Cadastro do
        SEUC/RS mas inclui também em sua amostra UCs e áreas não cadastradas, perpassando
        as diferentes esferas de governo e reservas particulares do patrimônio natural.
        </div></div>""",unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='card-m'><span class='ico'>⚙️</span>
        <div class='tit'>Como Funciona</div><div class='txt'>Como qualquer base de dados,
        é necessária a atualização e o preenchimento de lacunas de informação
        periodicamente. Se você é gestor, proprietário de UC ou área natural protegida do
        RS ainda não adequada ao SNUC/SEUC ou ainda se tem interesse em cadastrar ou
        inserir informações oficiais, acesse aqui para entrar em contato.
        </div></div>""",unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='card-m'><span class='ico'>💡</span>
        <div class='tit'>Importância</div><div class='txt'>Esta plataforma tem por
        finalidade popularizar a consulta e o acesso a dados e informações oficiais e
        atualizadas das Unidades de Conservação do Estado do Rio Grande do Sul para a
        sociedade em geral, permitindo a pesquisa e/ou o acompanhamento de indicadores
        sobre o estado de implementação do SEUC/RS.
        </div></div>""",unsafe_allow_html=True)

    st.markdown(f"""<div style='margin-top:28px;padding:12px 18px;
      background:rgba(255,255,255,.6);backdrop-filter:blur(10px);border-radius:8px;
      border-left:4px solid {AMAR};font-size:.77rem;color:#555;'>
      <strong style='color:{VERDE};'>SEMA-RS</strong> · Secretaria do Meio Ambiente e
      Infraestrutura do RS · Dados atualizados 2024 · {len(base)} UCs catalogadas
    </div>""",unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CADASTRO E REGULARIZAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# CADASTRO E REGULARIZAÇÃO  —  com cross-filter (clique nos gráficos)
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# CADASTRO E REGULARIZAÇÃO  —  cross-filter
# ══════════════════════════════════════════════════════════════════════════════
elif pag=="📋  Cadastro e Regularização":

    # ── Filtros de menu ───────────────────────────────────────────────────────
    with st.expander("🔎 Filtros",expanded=True):
        c1,c2,c3,c4,c5 = st.columns(5)
        fb = c1.multiselect("Bioma",   sorted(base["Bioma"].dropna().unique()),            placeholder="Selecione...",key="cr_b")
        ft = c2.multiselect("Tipo",    sorted(base["NomenclaturaSNUC"].dropna().unique()), placeholder="Selecione...",key="cr_t")
        fg = c3.multiselect("Grupo",   sorted(base["Grupo"].dropna().unique()),            placeholder="Selecione...",key="cr_g")
        fe = c4.multiselect("Esfera",  sorted(base["Esfera"].dropna().unique()),           placeholder="Selecione...",key="cr_e")
        fc = c5.multiselect("Cat. SNUC",sorted(base["Categoria SNUC"].dropna().unique()),  placeholder="Selecione...",key="cr_c")

        _an = pd.to_numeric(base["Ano de criação"], errors="coerce").dropna()
        ANO_MIN, ANO_MAX = int(_an.min()), int(_an.max())
        pc1, pc2 = st.columns([3,2])
        periodo = pc1.slider("Período de criação", ANO_MIN, ANO_MAX,
                             (ANO_MIN, ANO_MAX), key="cr_per")
        anos_esp = pc2.multiselect(
            "Ano específico",
            sorted(_an.astype(int).unique(), reverse=True),
            placeholder="Todos os anos do período", key="cr_ano")

    df0 = base.copy()
    if fb: df0=df0[df0["Bioma"].isin(fb)]
    if ft: df0=df0[df0["NomenclaturaSNUC"].isin(ft)]
    if fg: df0=df0[df0["Grupo"].isin(fg)]
    if fe: df0=df0[df0["Esfera"].isin(fe)]
    if fc: df0=df0[df0["Categoria SNUC"].isin(fc)]

    # ── CROSS-FILTER ──────────────────────────────────────────────────────────
    # Roscas: seleção via legenda clicável (botões) -> st.session_state["xf_<col>"]
    # Barras: seleção via on_select do Plotly (bar emite plotly_selected)
    COLS_ROSCA = ["Esfera","Cadastro do SEUC/RS","CNUC","CadastroSNUC","Grupo"]
    XF_BARRA   = {"snuc_bar":("Categoria SNUC","x"), "bio_bar":("Bioma","y")}

    def _ev(key, campo):
        """Devolve TODOS os valores selecionados — permite intervalo/múltiplos."""
        ev = st.session_state.get(key)
        if not ev:
            return None
        try:
            pts = ev["selection"]["points"]
        except (KeyError, TypeError):
            return None
        if not pts:
            return None
        vals = [p.get(campo) for p in pts if p.get(campo) is not None]
        return vals or None

    # SEL guarda sempre LISTA de valores -> suporta clique único e intervalo
    SEL = {}
    for _c in COLS_ROSCA:
        _v = st.session_state.get(f"xf_{_c}")
        if _v is not None:
            SEL[_c] = [_v]
    for _k,(_c,_campo) in XF_BARRA.items():
        _v = _ev(_k,_campo)
        if _v is not None:
            SEL[_c] = _v
    # Ano: slider de período + seleção de anos avulsos (sem interação no gráfico)
    _slider_ativo = (periodo[0] != ANO_MIN or periodo[1] != ANO_MAX)
    if anos_esp:
        _alvo = [a for a in anos_esp if periodo[0] <= a <= periodo[1]] \
                if _slider_ativo else list(anos_esp)
        if _alvo:
            SEL["Ano de criação"] = _alvo
        else:
            st.warning(
                f"Os anos escolhidos ({', '.join(str(a) for a in anos_esp)}) estão "
                f"fora do período {periodo[0]}–{periodo[1]}. "
                f"Ajuste o slider ou troque os anos.")
            SEL["Ano de criação"] = [-1]     # nenhum resultado, em vez de todos
    elif _slider_ativo:
        SEL["Ano de criação"] = list(range(periodo[0], periodo[1]+1))

    def toggle_xf(coluna, valor):
        """Clicar de novo no mesmo item desmarca."""
        atual = st.session_state.get(f"xf_{coluna}")
        st.session_state[f"xf_{coluna}"] = None if atual == valor else valor

    def xfilter(d, exceto=None):
        for coluna, valores in SEL.items():
            if coluna == exceto or coluna not in d.columns:
                continue
            serie = d[coluna]
            if pd.api.types.is_numeric_dtype(serie):
                # o Plotly devolve 2000.0; a coluna pode ser int64 -> comparar como número
                alvo = set()
                for v in valores:
                    try:
                        alvo.add(float(v))
                    except (TypeError, ValueError):
                        pass
                d = d[serie.astype(float).isin(alvo)]
            else:
                d = d[serie.astype(str).isin({str(v) for v in valores})]
        return d

    df = xfilter(df0)

    def _rotulo(vals):
        """Texto do chip: valor único, intervalo de anos ou contagem."""
        nums = []
        for v in vals:
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                pass
        todos_num = len(nums) == len(vals) and nums
        if len(vals) == 1:
            return f"{int(nums[0])}" if todos_num and nums[0].is_integer() else str(vals[0])
        if todos_num:
            return f"{int(min(nums))}–{int(max(nums))}"
        return f"{len(vals)} itens"

    # ── Barra de seleção ativa ────────────────────────────────────────────────
    if SEL:
        bc1, bc2 = st.columns([5,1])
        chips = " ".join(
            f"<span style='background:{AMAR};color:#333;padding:3px 10px;"
            f"border-radius:12px;font-size:.72rem;margin-right:6px;'>"
            f"{c}: <b>{_rotulo(v)}</b></span>" for c,v in SEL.items())
        bc1.markdown(
            f"<div style='background:rgba(255,255,255,.65);backdrop-filter:blur(8px);"
            f"border-radius:8px;padding:8px 12px;margin-bottom:8px;'>"
            f"<span style='font-size:.72rem;color:#666;margin-right:8px;'>"
            f"Filtro por clique:</span>{chips}</div>", unsafe_allow_html=True)
        if bc2.button("✕ Limpar", key="cr_limpar", use_container_width=True):
            for _c in COLS_ROSCA:
                st.session_state.pop(f"xf_{_c}", None)
            for _k in XF_BARRA:
                st.session_state.pop(_k, None)
            st.rerun()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1,k2,k3,k4 = st.columns(4)
    kpi(k1,f"{df['Área poligonal (ha)'].sum():,.2f}","Áreas Protegidas (ha)")
    kpi(k2,df["CadastroSNUC"].astype(str).str.lower().eq("sim").sum(),"Unidades de Conservação","am")
    kpi(k3,df[df["ANP_UC"]=="Área natural protegida"].shape[0],"Áreas Naturais Protegidas","az")
    kpi(k4,len(df),"Áreas Protegidas no RS","la")

    st.markdown("<br>",unsafe_allow_html=True)

    # ── 5 roscas com legenda clicável ─────────────────────────────────────────
    sec("Distribuição por categoria  ·  clique na legenda para filtrar")
    r1,r2,r3,r4,r5 = st.columns(5)
    CINZA_OFF = "#dcdcdc"

    def rosca(col, titulo, coluna, cmap, key):
        d_src = xfilter(df0, exceto=coluna)
        d = d_src[coluna].value_counts().reset_index()
        d.columns=["cat","n"]
        col.markdown(f"<div class='st' style='font-size:.76rem;'>{titulo}</div>",
                     unsafe_allow_html=True)
        if d.empty:
            col.caption("sem dados")
            return
        total = int(d["n"].sum())
        sel_aqui = SEL.get(coluna)
        cores = [(cmap.get(c,"#bbb") if (sel_aqui is None or str(c)==str(sel_aqui))
                  else CINZA_OFF) for c in d["cat"]]
        fig = px.pie(d, names="cat", values="n", hole=0.50)
        fig.update_traces(
            marker=dict(colors=cores,
                        line=dict(color="rgba(255,255,255,.85)",width=1)),
            domain=dict(x=[0.06,0.94], y=[0.04,0.98]),
            texttemplate="%{value}<br>%{percent:.0%}",
            textposition="inside", textfont_size=9,
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b> — %{value}<extra></extra>",
            sort=False,
        )
        fig.add_annotation(text=f"<b>{total}</b>", x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=13,color=VERDE), showarrow=False)
        fig.update_layout(
            margin=dict(t=2,b=2,l=2,r=2),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_family="Arial", font_color="#333", height=170,
            showlegend=False, dragmode=False,
        )
        col.plotly_chart(fig, use_container_width=True, key=key,
                         config={"displayModeBar":False, "staticPlot":False})

        # legenda em pills — CSS por botão dá a bolinha na cor da fatia
        css = []
        for cat, cor in zip(d["cat"], cores):
            slug = slugify(f"lg_{key}_{cat}")
            ativo = (sel_aqui is not None and str(cat) == str(sel_aqui))
            cor_bolinha = cmap.get(cat, "#bbb") if (sel_aqui is None or ativo) else CINZA_OFF
            css.append(
                f".st-key-{slug} button::before{{content:'';display:inline-block;"
                f"width:7px;height:7px;min-width:7px;border-radius:50%;"
                f"background:{cor_bolinha};}}")
            if ativo:
                c = cmap.get(cat, "#bbb")
                css.append(
                    f".st-key-{slug} button{{background:{c}22!important;"
                    f"border-color:{c}!important;color:#2b2b2b!important;}}"
                    f".st-key-{slug} button:hover{{background:{c}33!important;}}")
        col.markdown("<style>" + "".join(css) + "</style>", unsafe_allow_html=True)

        for cat in d["cat"]:
            cat = str(cat)
            col.button(
                cat,
                key=slugify(f"lg_{key}_{cat}"),
                on_click=toggle_xf, args=(coluna, cat),
                use_container_width=True,
                help=f"Filtrar por {cat}",
            )

    rosca(r1,"Esfera","Esfera",              COR_ESF_R, "r_esf")
    rosca(r2,"SEUC",  "Cadastro do SEUC/RS", COR_SN,    "r_seuc")
    rosca(r3,"CNUC",  "CNUC",                COR_SN,    "r_cnuc")
    rosca(r4,"SNUC",  "CadastroSNUC",        COR_SN,    "r_snuc")
    rosca(r5,"Grupo", "Grupo",               COR_GRP_R, "r_grp")

    # ── barras clicáveis ──────────────────────────────────────────────────────
    st.markdown("<br>",unsafe_allow_html=True)
    g1,g2 = st.columns(2)

    with g1:
        sec("Categoria SNUC")
        d_src = xfilter(df0, exceto="Categoria SNUC")
        d = d_src["Categoria SNUC"].value_counts().reset_index()
        d.columns=["cat","n"]; d=d.sort_values("cat")
        sel_aqui = SEL.get("Categoria SNUC")
        _on = (lambda c: sel_aqui is None or str(c) in {str(x) for x in sel_aqui})
        fill   = [(AZUL_CLARO if _on(c) else CINZA_OFF)   for c in d["cat"]]
        fig=go.Figure(go.Bar(x=d["cat"],y=d["n"],
            marker=dict(color=fill, line=dict(width=0)),
            text=d["n"],textposition="outside",textfont_size=11,
            hovertemplate="<b>%{x}</b> — %{y}<extra></extra>"))
        fig.update_layout(**LY, height=360, bargap=0, dragmode=False,
            xaxis=dict(showgrid=False,showline=False,tickfont_size=10,fixedrange=True),
            yaxis=dict(showgrid=False,showticklabels=False,showline=False,
                       fixedrange=True, range=[0,d["n"].max()*1.3]))
        st.plotly_chart(fig, use_container_width=True, key="snuc_bar",
                        on_select="rerun", selection_mode="points",
                        config={"displayModeBar":False})

    with g2:
        sec("Biomas")
        d_src = xfilter(df0, exceto="Bioma")
        d = d_src["Bioma"].value_counts().reset_index()
        d.columns=["b","n"]; d=d.sort_values("n",ascending=True)
        sel_aqui = SEL.get("Bioma")
        _on = (lambda b: sel_aqui is None or str(b) in {str(x) for x in sel_aqui})
        fill  = [(AZUL_CLARO if _on(b) else CINZA_OFF) for b in d["b"]]
        fig=go.Figure(go.Bar(x=d["n"],y=d["b"],orientation="h",
            marker=dict(color=fill, line=dict(width=0)),
            text=d["n"],textposition="outside",textfont_size=11,
            hovertemplate="<b>%{y}</b> — %{x}<extra></extra>"))
        fig.update_layout(**LY, height=360, dragmode=False,
            xaxis=dict(showgrid=False,showticklabels=False,fixedrange=True,
                       range=[0,d["n"].max()*1.3]),
            yaxis=dict(showgrid=False,tickfont_size=10,fixedrange=True))
        st.plotly_chart(fig, use_container_width=True, key="bio_bar",
                        on_select="rerun", selection_mode="points",
                        config={"displayModeBar":False})

    # ── tabela ────────────────────────────────────────────────────────────────
    sec("Listagem de UCs")
    cols_t=["Nome","Bioma","Esfera","Plano de Manejo","Cadastro do SEUC/RS",
            "CNUC","Grupo","Área poligonal (ha)","Órgão gestor"]
    st.dataframe(df[[c for c in cols_t if c in df.columns]].reset_index(drop=True),
                 use_container_width=True,height=240)

    # ── área acumulada (clicável: ponto = ano, arrasto = intervalo) ───────────
    sec("Área acumulada (ha)")
    d_ac = xfilter(df0, exceto="Ano de criação")
    dt = d_ac.dropna(subset=["Ano de criação"]).copy()
    if dt.empty:
        st.caption("Sem UCs com ano de criação para a seleção atual.")
    else:
        dt["Ano de criação"]=dt["Ano de criação"].astype(int)
        dt=dt.sort_values("Ano de criação")
        dt["Acum"]=dt["Área poligonal (ha)"].cumsum()
        ag=dt.groupby("Ano de criação")["Acum"].max().reset_index()

        anos_sel = SEL.get("Ano de criação")

        # janela visível do eixo X: acompanha o filtro de ano
        if anos_sel:
            _sel_int = sorted({int(float(a)) for a in anos_sel})
            x0, x1 = _sel_int[0], _sel_int[-1]
            if x0 == x1:            # ano único: abre uma folga para dar contexto
                x0, x1 = x0 - 2, x1 + 2
            else:
                folga = max(1, round((x1 - x0) * 0.04))
                x0, x1 = x0 - folga, x1 + folga
        else:
            x0, x1 = int(ag["Ano de criação"].min()), int(ag["Ano de criação"].max())

        # Y: base sempre em zero — truncar o eixo num gráfico de área distorce
        # a leitura, porque a superfície preenchida sugere magnitude desde 0.
        _vis = ag[(ag["Ano de criação"] >= x0) & (ag["Ano de criação"] <= x1)]
        _ymax = float(_vis["Acum"].max()) if not _vis.empty else float(ag["Acum"].max())
        y0, y1 = 0.0, _ymax * 1.15

        fig=go.Figure()
        # área
        fig.add_trace(go.Scatter(
            x=ag["Ano de criação"], y=ag["Acum"],
            mode="lines", fill="tozeroy",
            line=dict(color=AZUL_BORDA, width=2.2),
            fillcolor="rgba(168,213,245,.45)",
            hoverinfo="skip", showlegend=False,
        ))
        # pontos
        fig.add_trace(go.Scatter(
            x=ag["Ano de criação"], y=ag["Acum"],
            mode="markers",
            marker=dict(color=VERDE, size=6,
                        line=dict(color="white", width=1)),
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} ha<extra></extra>",
            showlegend=False,
        ))
        # anotações: escolhidas dentro da janela visível
        if not _vis.empty:
            _n = min(6, len(_vis))
            _passo = max(1, len(_vis)//_n)
            for _,row in _vis.iloc[::_passo].iterrows():
                fig.add_annotation(x=row["Ano de criação"],y=row["Acum"],
                    text=f"{row['Acum']/1000:.0f} Mil",
                    showarrow=False,yshift=14,font_size=9,font_color="#444")
        fig.update_layout(**LY,height=300, dragmode=False,
            xaxis=dict(showgrid=False,fixedrange=True,title="",
                       range=[x0, x1]),
            yaxis=dict(showgrid=True,gridcolor="#eee",title="ha",
                       fixedrange=True, range=[y0, y1]))
        chart(fig,300,"acum")


# ══════════════════════════════════════════════════════════════════════════════
# COBERTURA ESPACIAL
# ══════════════════════════════════════════════════════════════════════════════
elif pag=="🌍  Cobertura Espacial":
    with st.expander("🔎 Filtros",expanded=True):
        c1,c2,c3=st.columns(3)
        fe2=c1.multiselect("Esfera",   sorted(bio["Esfera_UC"].dropna().unique()), placeholder="Selecione...",key="ce_e")
        fb2=c2.multiselect("Bioma SCM",sorted(bio["Bioma_SCM"].dropna().unique()),placeholder="Selecione...",key="ce_b")
        fg2=c3.multiselect("Grupo UC", sorted(bio["Grupo_UC"].dropna().unique()),  placeholder="Selecione...",key="ce_g")
    db=bio.copy()
    if fe2: db=db[db["Esfera_UC"].isin(fe2)]
    if fb2: db=db[db["Bioma_SCM"].isin(fb2)]
    if fg2: db=db[db["Grupo_UC"].isin(fg2)]

    k1,k2,k3,k4=st.columns(4)
    kpi(k1,db["Código"].nunique(),"UCs com dados geoespaciais")
    kpi(k2,f"{db['Area_ha'].sum():,.0f}","Área Total (ha)","am")
    kpi(k3,f"{db['Area_ha'].sum()/100:,.1f}","Área Total (km²)","az")
    kpi(k4,db["Bioma_SCM"].nunique(),"Biomas presentes","la")

    # ── Mapa de biomas — coordenadas planas, sem basemap ──────────────────────
    sec("Mapa de Biomas do RS")

    import math

    # bounds globais para a projeção
    _lons, _lats = [], []
    for _f in bio_simp["features"]:
        for _poly in _f["geometry"]["coordinates"]:
            for _ring in _poly:
                for _p in _ring:
                    _lons.append(_p[0]); _lats.append(_p[1])
    _lat_med = (min(_lats) + max(_lats)) / 2
    _kx = math.cos(math.radians(_lat_med))   # corrige achatamento longitudinal

    fig_m = go.Figure()
    # features já vêm ordenadas por área (maior primeiro = desenha embaixo)
    for _f in bio_simp["features"]:
        nome = _f["properties"]["name"]
        cor  = COR_BIOMA_MAPA.get(nome, "#aaaaaa")
        xs, ys = [], []
        for _poly in _f["geometry"]["coordinates"]:
            for _ring in _poly:
                xs.extend([p[0] * _kx for p in _ring] + [None])
                ys.extend([p[1] for p in _ring] + [None])
        fig_m.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines",
            fill="toself",
            fillcolor=cor,
            line=dict(color="rgba(255,255,255,0.9)", width=0.7),
            name=nome,
            hoverinfo="name",
            hoveron="fills",
        ))

    fig_m.update_layout(
        height=620,
        margin=dict(t=4, b=4, l=4, r=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Arial",
        xaxis=dict(visible=False, showgrid=False, zeroline=False,
                   scaleanchor="y", scaleratio=1, fixedrange=True),
        yaxis=dict(visible=False, showgrid=False, zeroline=False,
                   fixedrange=True),
        legend=dict(orientation="h", y=-0.02, x=0.5, xanchor="center",
                    font_size=11, title_text="",
                    bgcolor="rgba(255,255,255,0.55)",
                    bordercolor="rgba(0,0,0,0.08)", borderwidth=1),
        dragmode=False,
    )
    st.plotly_chart(fig_m, use_container_width=True, key="mapa_bio",
                    config={"displayModeBar": False, "scrollZoom": False})

    g1,g2=st.columns(2)
    with g1:
        sec("Área (ha) por Bioma SCM")
        d=db.groupby("Bioma_SCM")["Area_ha"].sum().reset_index().sort_values("Area_ha")
        fig=go.Figure(go.Bar(x=d["Area_ha"],y=d["Bioma_SCM"],orientation="h",
            marker_color=AZUL,marker_line_width=0,
            text=[f"{v:,.0f}" for v in d["Area_ha"]],textposition="outside"))
        fig.update_layout(**LY,height=360,
            xaxis=dict(showgrid=False,showticklabels=False,
                       range=[0,d["Area_ha"].max()*1.35]),
            yaxis=dict(showgrid=False,tickfont_size=10))
        chart(fig,360,"ce_bar1")
    with g2:
        sec("Área (ha) por Esfera")
        d=db.groupby("Esfera_UC")["Area_ha"].sum().reset_index()
        fig=px.pie(d,names="Esfera_UC",values="Area_ha",hole=0.52,
                   color="Esfera_UC",color_discrete_map=COR_ESF_R)
        fig.update_traces(texttemplate="%{label}<br>%{percent:.0%}",
                          textposition="inside",textfont_size=10)
        fig.update_layout(**LY,height=360,
            legend=dict(orientation="h",y=-.1,x=.5,xanchor="center",font_size=10))
        chart(fig,360,"ce_pie")

    sec("Detalhamento geoespacial")
    cb=["Código","Nome_UC","Esfera_UC","Grupo_UC","Bioma_SCM","Area_ha","SNUC","CNUC"]
    st.dataframe(db[[c for c in cb if c in db.columns]].reset_index(drop=True),
                 use_container_width=True,height=260)


# ══════════════════════════════════════════════════════════════════════════════
# IMPLEMENTAÇÃO E EFETIVIDADE
# ══════════════════════════════════════════════════════════════════════════════
elif pag=="⚙️  Implementação e Efetividade":
    with st.expander("🔎 Filtros",expanded=True):
        c1,c2,c3=st.columns(3)
        fe3=c1.multiselect("Esfera",   sorted(base["Esfera"].dropna().unique()),        placeholder="Selecione...",key="ie_e")
        fg3=c2.multiselect("Grupo",    sorted(base["Grupo"].dropna().unique()),          placeholder="Selecione...",key="ie_g")
        fc3=c3.multiselect("Categoria",sorted(base["Categoria SNUC"].dropna().unique()),placeholder="Selecione...",key="ie_c")
    di=base.copy()
    if fe3: di=di[di["Esfera"].isin(fe3)]
    if fg3: di=di[di["Grupo"].isin(fg3)]
    if fc3: di=di[di["Categoria SNUC"].isin(fc3)]
    total=len(di)

    inds={"Plano de Manejo":di["Plano de Manejo_b"].sum(),
          "Conselho Gestor":di["Conselho Gestor_b"].sum(),
          "Zona de Amortec.":di["ZA_b"].sum(),
          "CNUC":di["CNUC_b"].sum(),
          "Shapefile":di["Shapefile dos limites_b"].sum()}

    kcs=st.columns(5)
    cls=["","am","az","","la"]
    for i,(k,v) in enumerate(inds.items()):
        p=v/total*100 if total else 0
        kpi(kcs[i],f"{v}/{total}",f"{k} ({p:.0f}%)",cls[i])

    st.markdown("<br>",unsafe_allow_html=True)
    g1,g2=st.columns([1.2,1])
    with g1:
        sec("Indicadores — Com vs Sem")
        di2=pd.DataFrame({"Ind":list(inds.keys()),
            "Com":list(inds.values()),
            "Sem":[total-v for v in inds.values()]})
        fig=go.Figure()
        fig.add_bar(name="Com",x=di2["Ind"],y=di2["Com"],
            marker_color=VERDE2,text=di2["Com"],textposition="inside",
            insidetextanchor="middle")
        fig.add_bar(name="Sem",x=di2["Ind"],y=di2["Sem"],
            marker_color="#CFD8DC",text=di2["Sem"],textposition="inside",
            insidetextanchor="middle")
        fig.update_layout(**LY,barmode="stack",height=340,
            yaxis_title="Qtd UCs",
            legend=dict(orientation="h",y=1.08,font_size=11))
        chart(fig,340,"ie_stack")
    with g2:
        sec("% de implementação")
        pcts={k:v/total*100 for k,v in inds.items()}
        cors=[VERDE2 if v>=50 else AMAR if v>=25 else "#EF5350" for v in pcts.values()]
        fig=go.Figure(go.Bar(x=list(pcts.values()),y=list(pcts.keys()),
            orientation="h",marker_color=cors,
            text=[f"{v:.0f}%" for v in pcts.values()],textposition="outside"))
        fig.update_layout(**LY,height=340,
            xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
            yaxis=dict(tickfont_size=10))
        chart(fig,340,"ie_pct")

    g3,g4=st.columns(2)
    with g3:
        sec("Plano de Manejo por Esfera")
        pm=di.groupby("Esfera")["Plano de Manejo_b"].agg(Com="sum",Total="count").reset_index()
        pm["Sem"]=pm["Total"]-pm["Com"]
        fig=go.Figure()
        fig.add_bar(name="Com PM",x=pm["Esfera"],y=pm["Com"],marker_color=VERDE2)
        fig.add_bar(name="Sem PM",x=pm["Esfera"],y=pm["Sem"],marker_color="#CFD8DC")
        fig.update_layout(**LY,barmode="stack",height=320,
            legend=dict(orientation="h",y=1.08,font_size=10))
        chart(fig,320,"ie_pm")
    with g4:
        sec("Conselho Gestor por Esfera")
        cg=di.groupby("Esfera")["Conselho Gestor_b"].agg(Com="sum",Total="count").reset_index()
        cg["Sem"]=cg["Total"]-cg["Com"]
        fig=go.Figure()
        fig.add_bar(name="Com CG",x=cg["Esfera"],y=cg["Com"],marker_color="#5b7fa6")
        fig.add_bar(name="Sem CG",x=cg["Esfera"],y=cg["Sem"],marker_color="#CFD8DC")
        fig.update_layout(**LY,barmode="stack",height=320,
            legend=dict(orientation="h",y=1.08,font_size=10))
        chart(fig,320,"ie_cg")

    sec("Detalhamento de implementação")
    ci=["Código","Nome","Esfera","Grupo","Categoria SNUC","Plano de Manejo",
        "Fase do Plano de Manejo","Conselho Gestor","ZA","CNUC","Shapefile dos limites"]
    st.dataframe(di[[c for c in ci if c in di.columns]].reset_index(drop=True),
                 use_container_width=True,height=260)


# ══════════════════════════════════════════════════════════════════════════════
# INFORMAÇÕES GEOESPACIAIS
# ══════════════════════════════════════════════════════════════════════════════
elif pag=="🗺️  Informações Geoespaciais":
    with st.expander("🔎 Filtros",expanded=True):
        c1,c2=st.columns(2)
        fb4=c1.multiselect("Bioma",     sorted(bmap["Bioma"].dropna().unique()),         placeholder="Selecione...",key="ge_b")
        fm4=c2.multiselect("Município", sorted(mun["Municípios_1"].dropna().unique()),   placeholder="Selecione...",key="ge_m")
    dg=bmap.copy(); dm=mun.copy()
    if fb4: dg=dg[dg["Bioma"].isin(fb4)]
    if fm4: dm=dm[dm["Municípios_1"].isin(fm4)]; dg=dg[dg["Código"].isin(dm["Código"].unique())]

    k1,k2,k3,k4=st.columns(4)
    kpi(k1,len(dg),"UCs no filtro")
    kpi(k2,dg["Bioma"].nunique(),"Biomas","am")
    kpi(k3,dm["Municípios_1"].nunique(),"Municípios","az")
    kpi(k4,dm["Código"].nunique(),"UCs com dados municipais","")

    sec("Mapa — Municípios do RS com UCs")
    upm=(dm.groupby("Municípios_1")["Código"].nunique().reset_index()
         .rename(columns={"Código":"n","Municípios_1":"NM_MUN"}))
    md=dict(zip(upm["NM_MUN"],upm["n"]))
    for feat in mun_geo["features"]:
        feat["properties"]["n_ucs"]=md.get(feat["properties"].get("NM_MUN",""),0)
    fig_mn=px.choropleth(upm,geojson=mun_geo,locations="NM_MUN",
        featureidkey="properties.NM_MUN",color="n",
        color_continuous_scale=[[0,"#e8f5e9"],[.3,"#81c784"],[.7,"#2E7D32"],[1,"#1A5C2A"]],
        labels={"n":"Nº UCs"},hover_name="NM_MUN")
    fig_mn.update_geos(fitbounds="locations",visible=False,
                       bgcolor="rgba(0,0,0,0)")
    fig_mn.update_layout(height=500,margin=dict(t=0,b=0,l=0,r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Nº UCs",thickness=14,len=.6))
    st.plotly_chart(fig_mn,use_container_width=True,key="ge_map",
                    config={"displayModeBar":False})

    g1,g2=st.columns(2)
    with g1:
        sec("Top 20 municípios com mais UCs")
        top=(dm.groupby("Municípios_1")["Código"].nunique().reset_index()
             .rename(columns={"Código":"UCs","Municípios_1":"Município"})
             .sort_values("UCs",ascending=False).head(20))
        fig=go.Figure(go.Bar(x=top["UCs"],y=top["Município"],orientation="h",
            marker_color=AZUL,marker_line_width=0,
            text=top["UCs"],textposition="outside"))
        fig.update_layout(**LY,height=560,
            yaxis=dict(autorange="reversed",tickfont_size=10),
            xaxis=dict(showgrid=False,showticklabels=False,
                       range=[0,top["UCs"].max()*1.25]))
        chart(fig,560,"ge_mun_bar")
    with g2:
        sec("UCs por Bioma")
        d=dg["Bioma"].value_counts().reset_index()
        COR_BIO_S={"Mata Atlântica":"#4a8c5c","Pampa":"#c9b96e",
                   "Costeiro-Marinho":"#5b7fa6","Mata Atlântica, Pampa":"#8fae8f",
                   "Mata Atlântica, Costeiro-Marinho":"#7a9eb0",
                   "Pampa, Costeiro-Marinho":"#9b8fb0"}
        fig=px.pie(d,names="Bioma",values="count",hole=0.52,
                   color="Bioma",color_discrete_map=COR_BIO_S)
        fig.update_traces(texttemplate="%{value}<br>%{percent:.0%}",
                          textposition="inside",textfont_size=10,
                          insidetextorientation="horizontal")
        fig.update_layout(**LY,height=560,showlegend=True,
            legend=dict(orientation="v",x=1.01,y=.5,font_size=10))
        chart(fig,560,"ge_bio_pie")

    t1,t2=st.columns(2)
    with t1:
        sec("UCs geoespaciais")
        st.dataframe(dg[["Código","Nome","Bioma"]].reset_index(drop=True),
                     use_container_width=True,height=240)
    with t2:
        sec("UCs × Municípios")
        cm=[c for c in ["Código","Nome","Municípios_1","UF"] if c in dm.columns]
        st.dataframe(dm[cm].reset_index(drop=True),
                     use_container_width=True,height=240)
