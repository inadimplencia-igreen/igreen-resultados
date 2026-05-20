import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import io
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="iGreen | Gestão Inadimplência", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #071a0e; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0a2414,#071a0e); border-right:1px solid #1a4d2e; }
[data-testid="stMetric"] { background:linear-gradient(135deg,#0a2414,#0d2e1a); border:1px solid #1a4d2e; border-radius:12px; padding:20px !important; border-left:3px solid #2daf5c; }
[data-testid="stMetricValue"] { color:#ffffff !important; font-size:24px !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { color:#5a9a70 !important; font-size:11px !important; text-transform:uppercase; letter-spacing:1px; }
[data-testid="stMetricDelta"] { font-size:12px !important; }
.stButton > button { background:linear-gradient(135deg,#1a6b35,#2daf5c) !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important; }
.stButton > button:hover { background:linear-gradient(135deg,#2daf5c,#3dd670) !important; }
h1 { color:#ffffff !important; font-size:22px !important; font-weight:700 !important; }
h2 { color:#e0f0e8 !important; font-size:18px !important; }
h3 { color:#5a9a70 !important; font-size:12px !important; text-transform:uppercase; letter-spacing:1.5px; }
hr { border-color:#1a4d2e !important; }
p, label { color:#b8d4c0 !important; }
.stTextInput input, .stNumberInput input { background:#0a2414 !important; border:1px solid #1a4d2e !important; color:#e0f0e8 !important; border-radius:8px !important; }
[data-testid="stFileUploader"] { background:#0a2414 !important; border:2px dashed #1a4d2e !important; border-radius:12px !important; }
.stTabs [data-baseweb="tab-list"] { background:#0a2414 !important; border-radius:8px !important; padding:4px !important; }
.stTabs [data-baseweb="tab"] { color:#5a9a70 !important; border-radius:6px !important; }
.stTabs [aria-selected="true"] { background:#1a6b35 !important; color:#ffffff !important; }
.stSelectbox > div > div { background:#0a2414 !important; border:1px solid #1a4d2e !important; color:#e0f0e8 !important; }
[data-testid="stSidebar"] .stRadio label { color:#b8d4c0 !important; font-size:13px !important; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#071a0e; }
::-webkit-scrollbar-thumb { background:#1a4d2e; border-radius:3px; }
.pcp-card { background:linear-gradient(135deg,#0a2414,#0d2e1a); border:1px solid #1a4d2e; border-radius:12px; padding:20px; margin-bottom:8px; }
.pcp-verde { border-left:4px solid #2daf5c !important; }
.pcp-amarelo { border-left:4px solid #f0a500 !important; }
.pcp-vermelho { border-left:4px solid #e03c3c !important; }
</style>
""", unsafe_allow_html=True)

# ── DADOS ─────────────────────────────────────
USUARIOS = {
    "tamires": {"senha":"tamires123","equipe":"tamires","role":"admin",  "nome":"Tamires"},
    "luciano": {"senha":"luciano123","equipe":"luciano","role":"gestor", "nome":"Luciano"},
    "deborah": {"senha":"deborah123","equipe":"deborah","role":"gestor", "nome":"Déborah"},
    "veloso":  {"senha":"veloso123", "equipe":None,     "role":"diretor","nome":"Veloso"},
    "moyara":  {"senha":"moyara123", "equipe":None,     "role":"diretor","nome":"Moyara"},
}
EQUIPES = {
    "luciano":{"nome":"Luciano","emoji":"🟢","cor":"#2daf5c"},
    "deborah":{"nome":"Déborah","emoji":"🟣","cor":"#a855f7"},
    "tamires":{"nome":"Tamires","emoji":"🟠","cor":"#f97316"},
    "metcool":{"nome":"MetCool","emoji":"🔵","cor":"#3b82f6"},
}
AGENTES = [
    {"id":"jennifer-silveira","nome":"Jennifer Silveira","equipe":"luciano","pleno":True},
    {"id":"paulo-roberto","nome":"Paulo Roberto","equipe":"luciano","pleno":False},
    {"id":"samires-barros","nome":"Samires Barros","equipe":"luciano","pleno":False},
    {"id":"maycow-gabriel","nome":"Maycow Gabriel","equipe":"luciano","pleno":False},
    {"id":"otaides-junior","nome":"Otaides Junior","equipe":"luciano","pleno":False},
    {"id":"heverton-tavares","nome":"Heverton Tavares","equipe":"luciano","pleno":False},
    {"id":"camila-nara","nome":"Camila Nara","equipe":"luciano","pleno":False},
    {"id":"caua-alves","nome":"Caua Alves","equipe":"luciano","pleno":False},
    {"id":"eduarda-sanqueta","nome":"Eduarda Sanqueta","equipe":"luciano","pleno":False},
    {"id":"jheniffer-santos","nome":"Jheniffer Santos","equipe":"luciano","pleno":False},
    {"id":"ketie-silva","nome":"Ketie Silva","equipe":"luciano","pleno":False},
    {"id":"emanuel-cardoso","nome":"Emanuel Cardoso","equipe":"luciano","pleno":False},
    {"id":"victoria-silva","nome":"Victória Silva","equipe":"luciano","pleno":False},
    {"id":"grasielli-santos","nome":"Grasielli Santos","equipe":"luciano","pleno":False},
    {"id":"laura-silva","nome":"Laura Silva","equipe":"luciano","pleno":False},
    {"id":"michelle-batista","nome":"Michelle Batista","equipe":"luciano","pleno":False},
    {"id":"lorenzzo-pereira","nome":"Lorenzzo Pereira","equipe":"luciano","pleno":False},
    {"id":"diogo-oliveira","nome":"Diogo Oliveira","equipe":"luciano","pleno":False},
    {"id":"maria-paulino","nome":"Maria Paulino","equipe":"luciano","pleno":False},
    {"id":"gabrielle-martins","nome":"Gabrielle Martins","equipe":"luciano","pleno":False},
    {"id":"marcos-martins","nome":"Marcos Martins","equipe":"luciano","pleno":False},
    {"id":"mikael-dias","nome":"Mikael Dias","equipe":"deborah","pleno":False},
    {"id":"amanda-eduarda","nome":"Amanda Eduarda","equipe":"deborah","pleno":False},
    {"id":"larissa-barcelos","nome":"Larissa Barcelos","equipe":"deborah","pleno":False},
    {"id":"nicole-amaral","nome":"Nicole Amaral","equipe":"deborah","pleno":False},
    {"id":"sara-rocha","nome":"Sara Rocha","equipe":"deborah","pleno":False},
    {"id":"isabelly-araujo","nome":"Isabelly Araujo","equipe":"deborah","pleno":False},
    {"id":"silye-paula","nome":"Silye Paula","equipe":"deborah","pleno":False},
    {"id":"danilo-rodrigues","nome":"Danilo Rodrigues","equipe":"tamires","pleno":True},
    {"id":"raiane-pereira","nome":"Raiane Pereira","equipe":"tamires","pleno":False},
    {"id":"wynara-dos-reis","nome":"Wynara Dos Reis","equipe":"tamires","pleno":False},
    {"id":"esteffany-souza","nome":"Esteffany Souza","equipe":"tamires","pleno":False},
    {"id":"andre-gomes","nome":"André Gomes","equipe":"tamires","pleno":False},
    {"id":"wanessa-cardoso","nome":"Wanessa Cardoso","equipe":"tamires","pleno":False},
    {"id":"larisse-garcia","nome":"Larisse Garcia","equipe":"tamires","pleno":False},
    {"id":"arthur-alves","nome":"Arthur Alves","equipe":"tamires","pleno":False},
]
SEMANAS = [
    ("sem1-qua","1ª Semana — Quarta"),("sem1-sex","1ª Semana — Sexta"),
    ("sem2-qua","2ª Semana — Quarta"),("sem2-sex","2ª Semana — Sexta"),
    ("sem3-qua","3ª Semana — Quarta"),("sem3-sex","3ª Semana — Sexta"),
    ("sem4-qua","4ª Semana — Quarta"),("sem4-sex","4ª Semana — Sexta"),
    ("fechamento","Fechamento do Mês"),
]
MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

# ── MONGODB ────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
    return client[st.secrets["mongo"]["db"]]

def salvar_resultado(mes_ano, semana_id, equipe_id, dados):
    # Salva APENAS os dados desta semana/equipe — nunca toca em outros documentos
    doc_id = f"{mes_ano}__{semana_id}__{equipe_id}"
    get_db().resultados.update_one(
        {"_id": doc_id},
        {"$set": {"_id":doc_id,"mesAno":mes_ano,"semanaId":semana_id,
                  "equipeId":equipe_id,**dados,"atualizadoEm":datetime.now()}},
        upsert=True
    )

def buscar_resultado_especifico(mes_ano, semana_id, equipe_id):
    # Busca APENAS o documento desta semana/equipe
    doc_id = f"{mes_ano}__{semana_id}__{equipe_id}"
    return get_db().resultados.find_one({"_id": doc_id}) or {}

def buscar_resultados_mes(mes_ano):
    docs = list(get_db().resultados.find({"mesAno": mes_ano}))
    return {d["_id"]: d for d in docs}

def salvar_config(mes_ano, equipe_id, tipo, dados):
    doc_id = f"{tipo}__{mes_ano}__{equipe_id}"
    get_db().configuracoes.update_one(
        {"_id": doc_id},
        {"$set": {"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,**dados}},
        upsert=True
    )

def buscar_config(mes_ano, equipe_id, tipo):
    doc_id = f"{tipo}__{mes_ano}__{equipe_id}"
    return get_db().configuracoes.find_one({"_id": doc_id}) or {}

def salvar_processamento(mes_ano, equipe_id, df):
    doc_id = f"proc__{mes_ano}__{equipe_id}"
    get_db().processamentos.update_one(
        {"_id": doc_id},
        {"$set": {"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,
                  "registros":df.to_dict("records"),"atualizadoEm":datetime.now()}},
        upsert=True
    )

def buscar_processamentos(mes_ano=None, equipe_id=None):
    filtro = {}
    if mes_ano:   filtro["mesAno"]   = mes_ano
    if equipe_id: filtro["equipeId"] = equipe_id
    docs = list(get_db().processamentos.find(filtro))
    frames = []
    for d in docs:
        if d.get("registros"):
            df = pd.DataFrame(d["registros"])
            df["_equipe"]  = d["equipeId"]
            df["_mes_ano"] = d["mesAno"]
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def listar_meses_processados():
    return sorted(get_db().processamentos.distinct("mesAno"), reverse=True)

# ── HELPERS ────────────────────────────────────
def fmt_brl(v):
    if v is None or v == "" : return "R$ 0,00"
    try:
        return "R$ " + f"{float(v):_.2f}".replace(".", ",").replace("_", ".")
    except:
        return "R$ 0,00"

def parse_brl(s):
    if not s: return 0.0
    try:
        return float(str(s).replace("R$","").replace(".","").replace(",",".").strip())
    except:
        return 0.0

def fmt_input(v):
    # Formata valor salvo para exibir no input
    if not v or float(v) == 0: return ""
    return f"{float(v):_.2f}".replace(".", ",").replace("_", ".")

def calc_projecao(valor, dias_trab, total_dias):
    if not dias_trab or dias_trab <= 0: return 0
    return (valor / dias_trab) * total_dias

def calc_variacao(atual, anterior):
    if not anterior or anterior == 0: return None
    return ((atual - anterior) / anterior) * 100

def get_semana_anterior(semana_id):
    ids = [s[0] for s in SEMANAS]
    idx = ids.index(semana_id) if semana_id in ids else -1
    return ids[idx-1] if idx > 0 else None

def get_meses_disponiveis():
    hoje = datetime.now(); meses = []
    for i in range(6):
        m = hoje.month - i; a = hoje.year
        if m <= 0: m += 12; a -= 1
        meses.append(f"{MESES[m-1]}-{a}")
    return meses

def cor_pct(pct):
    if pct >= 80: return "#2daf5c"
    if pct >= 50: return "#f0a500"
    return "#e03c3c"

def status_pct(pct):
    if pct >= 80: return "🟢"
    if pct >= 50: return "🟡"
    return "🔴"

def aging_faixa(dias):
    if pd.isna(dias): return "ND"
    if dias <= 30: return "D0-30"
    if dias <= 60: return "D31-60"
    if dias <= 90: return "D61-90"
    return "D90+"

# ── PROCESSAMENTO ──────────────────────────────
def processar_bases(pagos_file, chat_file, lig_file, disp_file, equipe_id, mes_ano):
    def ler(f):
        if f is None: return None
        try:
            return pd.read_csv(f, header=0) if f.name.endswith(".csv") else pd.read_excel(f, header=0)
        except: return None

    df_pagos = ler(pagos_file)
    if df_pagos is None or df_pagos.empty:
        return None, ["Arquivo PAGOS inválido ou vazio!"]

    cols = list(df_pagos.columns)
    mapa = {}
    if len(cols)>=1: mapa[cols[0]]="uc_cpf"
    if len(cols)>=2: mapa[cols[1]]="data_vencimento"
    if len(cols)>=3: mapa[cols[2]]="data_pagamento"
    if len(cols)>=4: mapa[cols[3]]="valor"
    if len(cols)>=5: mapa[cols[4]]="fornecedora"
    df_pagos = df_pagos.rename(columns=mapa)

    for col in ["data_vencimento","data_pagamento"]:
        if col in df_pagos.columns:
            df_pagos[col] = pd.to_datetime(df_pagos[col], dayfirst=True, errors="coerce")

    if "valor" in df_pagos.columns:
        df_pagos["valor"] = pd.to_numeric(
            df_pagos["valor"].astype(str).str.replace("R$","").str.replace(".","").str.replace(",",".").str.strip(),
            errors="coerce"
        ).fillna(0)

    df_pagos["uc_cpf"] = df_pagos["uc_cpf"].astype(str).str.strip()

    contatos = []
    for arq, nome in [(chat_file,"CHAT"),(lig_file,"LIGACOES"),(disp_file,"DISPAROS")]:
        df = ler(arq)
        if df is not None and len(df.columns) >= 2:
            dc = pd.DataFrame()
            dc["uc_cpf"]       = df.iloc[:,0].astype(str).str.strip()
            dc["data_contato"] = pd.to_datetime(df.iloc[:,1], dayfirst=True, errors="coerce")
            contatos.append(dc)

    primeiro_contato = pd.DataFrame()
    if contatos:
        df_todos = pd.concat(contatos, ignore_index=True).dropna(subset=["data_contato"])
        primeiro_contato = df_todos.groupby("uc_cpf")["data_contato"].min().reset_index().rename(columns={"data_contato":"primeiro_contato"})

    if not primeiro_contato.empty:
        df_res = df_pagos.merge(primeiro_contato, on="uc_cpf", how="left")
    else:
        df_res = df_pagos.copy()
        df_res["primeiro_contato"] = pd.NaT

    df_res["diferenca_dias"] = (df_res["data_pagamento"] - df_res["primeiro_contato"]).dt.days

    def classif(row):
        if pd.isna(row["primeiro_contato"]): return "ND"
        if row["diferenca_dias"] >= 0: return "Elegível"
        return "Não Elegível"

    df_res["elegibilidade"] = df_res.apply(classif, axis=1)
    df_res["dias_vencidos"]  = (df_res["data_pagamento"] - df_res["data_vencimento"]).dt.days
    df_res["aging"]          = df_res["dias_vencidos"].apply(aging_faixa)

    for col in ["data_vencimento","data_pagamento","primeiro_contato"]:
        if col in df_res.columns:
            df_res[col] = df_res[col].dt.strftime("%Y-%m-%d").where(df_res[col].notna(), other=None)

    df_res["equipe"]  = equipe_id
    df_res["mes_ano"] = mes_ano
    return df_res, []

# ── LOGIN ──────────────────────────────────────
def tela_login():
    c1, c2, c3 = st.columns([1,1.2,1])
    with c2:
        st.markdown("""
        <div style="text-align:center;padding:48px 0 32px">
            <div style="width:72px;height:72px;background:linear-gradient(135deg,#1a6b35,#2daf5c);border-radius:18px;display:inline-flex;align-items:center;justify-content:center;font-size:36px;font-weight:800;color:white;margin-bottom:16px;box-shadow:0 8px 32px rgba(45,175,92,0.4)">G</div>
            <h1 style="color:#ffffff;margin:0;font-size:24px">iGreen Resultados</h1>
            <p style="color:#5a9a70;margin:6px 0 0;font-size:13px">Gestão de Inadimplência Comercial</p>
        </div>
        """, unsafe_allow_html=True)
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha   = st.text_input("Senha", type="password", placeholder="••••••••")
        if st.button("Entrar", use_container_width=True):
            u = USUARIOS.get(usuario.lower().strip())
            if u and u["senha"] == senha.strip():
                st.session_state.usuario = {"id": usuario.lower(), **u}
                st.rerun()
            else:
                st.error("⚠ Usuário ou senha incorretos.")
        st.markdown('<p style="text-align:center;color:#1a4d2e;font-size:11px;margin-top:32px">iGreen Energy © 2026</p>', unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────
def render_sidebar():
    u = st.session_state.usuario
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
                <div style="width:40px;height:40px;background:linear-gradient(135deg,#1a6b35,#2daf5c);border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;color:white">G</div>
                <div><div style="color:#ffffff;font-weight:700;font-size:14px">iGreen</div><div style="color:#5a9a70;font-size:11px">Inadimplência</div></div>
            </div>
            <div style="background:rgba(45,175,92,0.1);border:1px solid rgba(45,175,92,0.2);border-radius:8px;padding:10px 12px;margin-bottom:16px">
                <div style="color:#2daf5c;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px">{'👔 Diretoria' if u['role']=='diretor' else '⚙️ Admin' if u['role']=='admin' else '👤 Gestor'}</div>
                <div style="color:#ffffff;font-size:14px;font-weight:600;margin-top:2px">{u['nome']}</div>
            </div>
        </div><hr>
        """, unsafe_allow_html=True)

        st.markdown("**📅 Período**")
        mes = st.selectbox("Mês", get_meses_disponiveis(), label_visibility="collapsed")
        slabels = [s[1] for s in SEMANAS]
        slabel  = st.selectbox("Semana", slabels, label_visibility="collapsed")
        sid     = SEMANAS[slabels.index(slabel)][0]

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**📌 Navegação**")

        if u["role"] == "diretor":
            pags = ["📊 Dashboard Executivo", "🏆 Quadro de Resultados", "📋 Histórico"]
        elif u["role"] == "admin":
            pags = ["📊 Dashboard Executivo", "🏆 Quadro de Resultados", "✏️ Lançamento", "📁 Upload de Bases", "📋 Histórico", "👥 Agentes"]
        else:
            pags = ["🏆 Quadro de Resultados", "✏️ Lançamento", "📁 Upload de Bases", "📋 Histórico"]

        pag = st.radio("", pags, label_visibility="collapsed")
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("⏻ Sair", use_container_width=True):
            del st.session_state.usuario; st.rerun()

    return mes, sid, slabel, pag

# ── LANÇAMENTO ─────────────────────────────────
def pagina_lancamento(mes_ano, semana_id, semana_label):
    u         = st.session_state.usuario
    equipe_id = u["equipe"]
    agentes   = [a for a in AGENTES if a["equipe"] == equipe_id]

    # Carrega dados SOMENTE desta semana/equipe
    dados_salvos = buscar_resultado_especifico(mes_ano, semana_id, equipe_id)
    config_dias  = buscar_config(mes_ano, equipe_id, "dias")
    metas_cfg    = buscar_config(mes_ano, equipe_id, "metas")
    metas_salvas = metas_cfg.get("metas", {})

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:14px;padding:20px 24px;margin-bottom:20px;border-left:4px solid #2daf5c">
        <h1 style="margin:0">✏️ Lançamento de Resultado</h1>
        <p style="color:#5a9a70;margin:4px 0 0;font-size:13px">{semana_label} · {mes_ano.replace('-',' ')} · Equipe {EQUIPES[equipe_id]['nome']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Config período
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        vg_salvo = dados_salvos.get("valorGeral", 0)
        vgs = st.text_input(
            "💰 Valor Total Geral Recebido (R$)",
            value=fmt_input(vg_salvo),
            placeholder="Ex: 85.000,00"
        )
    with col2:
        dt = st.number_input("📅 Dias Trabalhados", min_value=0, max_value=31,
                              value=int(config_dias.get("diasTrabalhados", 0)))
    with col3:
        td = st.number_input("📅 Total de Dias no Mês", min_value=1, max_value=31,
                              value=int(config_dias.get("totalDias", 22)))

    st.markdown("---")

    # Tabela de agentes
    st.markdown("### 👤 Valores por Agente")

    cols_header = st.columns([3,2,2,2,2])
    for h, t in zip(cols_header, ["**Agente**","**Meta (R$)**","**Valor Recebido (R$)**","**Projeção**","**% Meta**"]):
        h.markdown(t)

    vi = {}
    mi = {}

    for a in agentes:
        # Carrega valor salvo DESTE agente nesta semana
        val_salvo  = dados_salvos.get("agentes", {}).get(a["id"], {}).get("valorRecebido", 0)
        meta_salva = metas_salvas.get(a["id"], 0)

        cols = st.columns([3,2,2,2,2])
        nome_label = f"{'⭐ ' if a['pleno'] else ''}{a['nome']}"
        cols[0].markdown(f"<div style='padding-top:10px;color:#e0f0e8;font-weight:500'>{nome_label}</div>", unsafe_allow_html=True)

        meta_str = cols[1].text_input("m", label_visibility="collapsed",
            value=fmt_input(meta_salva), placeholder="R$ 0,00", key=f"m_{semana_id}_{a['id']}")

        val_str = cols[2].text_input("v", label_visibility="collapsed",
            value=fmt_input(val_salvo), placeholder="R$ 0,00", key=f"v_{semana_id}_{a['id']}")

        val  = parse_brl(val_str)
        meta = parse_brl(meta_str)
        proj = calc_projecao(val, dt, td)
        pct  = (val/meta*100) if meta > 0 else 0
        c    = cor_pct(pct)
        s    = status_pct(pct)

        cols[3].markdown(f"<div style='padding-top:10px;color:#5a9a70;font-weight:600'>{fmt_brl(proj) if proj > 0 else '—'}</div>", unsafe_allow_html=True)
        cols[4].markdown(f"<div style='padding-top:10px;color:{c};font-weight:700'>{s} {f'{pct:.1f}%' if meta > 0 else '—'}</div>", unsafe_allow_html=True)

        vi[a["id"]] = val
        mi[a["id"]] = meta

    # Totais
    tc  = sum(vi.values())
    vg  = parse_brl(vgs)
    sem = max(0, vg - tc)

    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🤝 Com Interação",  fmt_brl(tc))
    c2.metric("🔕 Sem Interação",  fmt_brl(sem))
    c3.metric("💰 Total Geral",    fmt_brl(vg))
    c4.metric("📈 Projeção Equipe", fmt_brl(calc_projecao(tc, dt, td)))

    st.markdown("---")

    col1, col2 = st.columns([1,3])
    with col1:
        if st.button("💾 Salvar Resultado", use_container_width=True):
            # Salva APENAS dados desta semana/equipe
            agentes_data = {a["id"]: {"valorRecebido": vi[a["id"]]} for a in agentes}
            salvar_resultado(mes_ano, semana_id, equipe_id, {
                "agentes":     agentes_data,
                "totalEquipe": tc,
                "valorGeral":  vg,
                "semInteracao": sem,
            })
            salvar_config(mes_ano, equipe_id, "metas", {"metas": mi})
            salvar_config(mes_ano, equipe_id, "dias",  {"diasTrabalhados": dt, "totalDias": td})
            st.success("✅ Resultado salvo com sucesso!")
            st.rerun()

    with col2:
        if st.button("📊 Gerar Quadro de Resultado", use_container_width=True):
            st.session_state["ver_quadro"] = True
            st.session_state["quadro_mes"] = mes_ano
            st.session_state["quadro_sem"] = semana_id
            st.rerun()

# ── QUADRO PCP ─────────────────────────────────
def pagina_quadro_resultado(mes_ano, semana_id, semana_label):
    u         = st.session_state.usuario
    is_dir    = u["role"] == "diretor"
    equipes_ver = list(EQUIPES.keys()) if is_dir else [u["equipe"]]

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:14px;padding:20px 24px;margin-bottom:20px;border-left:4px solid #2daf5c">
        <h1 style="margin:0">🏆 Quadro de Resultados</h1>
        <p style="color:#5a9a70;margin:4px 0 0;font-size:13px">{semana_label} · {mes_ano.replace('-',' ')}</p>
    </div>
    """, unsafe_allow_html=True)

    for equipe_id in equipes_ver:
        eq      = EQUIPES[equipe_id]
        agentes = [a for a in AGENTES if a["equipe"] == equipe_id]
        if not agentes: continue

        dados      = buscar_resultado_especifico(mes_ano, semana_id, equipe_id)
        config_dias = buscar_config(mes_ano, equipe_id, "dias")
        metas_cfg   = buscar_config(mes_ano, equipe_id, "metas")
        metas       = metas_cfg.get("metas", {})
        dt = config_dias.get("diasTrabalhados", 0)
        td = config_dias.get("totalDias", 22)

        total_eq    = dados.get("totalEquipe", 0)
        meta_eq     = sum(metas.get(a["id"], 0) for a in agentes)
        proj_eq     = calc_projecao(total_eq, dt, td)
        pct_eq      = (total_eq/meta_eq*100) if meta_eq > 0 else 0
        c_eq        = cor_pct(pct_eq)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid {eq['cor']}">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="font-size:16px;font-weight:700;color:#ffffff">{eq['emoji']} Equipe {eq['nome']}</div>
                <div style="text-align:right">
                    <span style="color:{c_eq};font-size:20px;font-weight:800">{pct_eq:.1f}%</span>
                    <span style="color:#5a9a70;font-size:12px;margin-left:8px">da meta</span>
                </div>
            </div>
            <div style="display:flex;gap:24px;margin-top:8px">
                <div><span style="color:#5a9a70;font-size:11px">RECEBIDO</span><br><span style="color:#2daf5c;font-weight:700">{fmt_brl(total_eq)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">META</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(meta_eq)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(proj_eq)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">DIAS</span><br><span style="color:#e0f0e8;font-weight:600">{dt}/{td}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabela de agentes estilo PCP
        rows = []
        for a in agentes:
            val  = dados.get("agentes", {}).get(a["id"], {}).get("valorRecebido", 0)
            meta = metas.get(a["id"], 0)
            proj = calc_projecao(val, dt, td)
            pct  = (val/meta*100) if meta > 0 else 0
            rows.append({
                "Status":          status_pct(pct) if meta > 0 else "⚪",
                "Agente":          ("⭐ " if a["pleno"] else "") + a["nome"],
                "Recebido":        fmt_brl(val),
                "Meta":            fmt_brl(meta) if meta > 0 else "—",
                "% Meta":          f"{pct:.1f}%" if meta > 0 else "—",
                "Projeção":        fmt_brl(proj) if proj > 0 else "—",
                "_pct": pct, "_val": val
            })

        df = (pd.DataFrame(rows)
              .sort_values("_val", ascending=False)
              .drop(columns=["_pct","_val"])
              .reset_index(drop=True))
        df.index = range(1, len(df)+1)
        st.dataframe(df, use_container_width=True, height=min(600, (len(df)+1)*38+40))
        st.markdown("---")

    # Export Excel
    if st.button("📥 Exportar Excel", use_container_width=False):
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            for equipe_id in equipes_ver:
                eq      = EQUIPES[equipe_id]
                agentes = [a for a in AGENTES if a["equipe"] == equipe_id]
                if not agentes: continue
                dados      = buscar_resultado_especifico(mes_ano, semana_id, equipe_id)
                metas_cfg  = buscar_config(mes_ano, equipe_id, "metas")
                config_dias = buscar_config(mes_ano, equipe_id, "dias")
                metas      = metas_cfg.get("metas", {})
                dt = config_dias.get("diasTrabalhados", 0)
                td = config_dias.get("totalDias", 22)
                rows = []
                for a in agentes:
                    val  = dados.get("agentes", {}).get(a["id"], {}).get("valorRecebido", 0)
                    meta = metas.get(a["id"], 0)
                    proj = calc_projecao(val, dt, td)
                    pct  = (val/meta*100) if meta > 0 else 0
                    rows.append({"Agente": a["nome"],"Recebido": val,"Meta": meta,"% Meta": f"{pct:.1f}%","Projeção": proj})
                pd.DataFrame(rows).to_excel(writer, sheet_name=f"Equipe {eq['nome']}", index=False)
        st.download_button("⬇️ Baixar Excel", data=out.getvalue(),
            file_name=f"iGreen_Resultado_{mes_ano}_{semana_id}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── DASHBOARD EXECUTIVO ─────────────────────────
def pagina_dashboard_executivo():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:14px;padding:20px 24px;margin-bottom:20px;border-left:4px solid #2daf5c">
        <h1 style="margin:0">📊 Dashboard Executivo</h1>
        <p style="color:#5a9a70;margin:4px 0 0;font-size:13px">Gestão de Inadimplência Comercial · Visão consolidada</p>
    </div>
    """, unsafe_allow_html=True)

    meses_proc = listar_meses_processados()
    if not meses_proc:
        st.info("📭 Nenhuma base processada ainda. Aguarde o upload das equipes.")
        return

    c1,c2,c3 = st.columns(3)
    with c1: mes_f  = st.selectbox("📅 Mês",      ["Todos"] + meses_proc)
    with c2: eq_f   = st.selectbox("👥 Equipe",   ["Todas","luciano","deborah","tamires"])
    df = buscar_processamentos(None if mes_f=="Todos" else mes_f, None if eq_f=="Todas" else eq_f)

    if df.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    with c3:
        forns   = ["Todas"] + sorted(df["fornecedora"].dropna().unique().tolist())
        forn_f  = st.selectbox("🏢 Fornecedora", forns)
    if forn_f != "Todas":
        df = df[df["fornecedora"] == forn_f]

    st.markdown("---")
    elig  = df[df["elegibilidade"] == "Elegível"]
    nelig = df[df["elegibilidade"] == "Não Elegível"]
    nd    = df[df["elegibilidade"] == "ND"]

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("💰 Valor Recuperado",  fmt_brl(elig["valor"].sum()))
    c2.metric("👥 Clientes Únicos",   f'{df["uc_cpf"].nunique():,}')
    c3.metric("📋 Boletos",           f'{len(df):,}')
    c4.metric("✅ Elegíveis",         f'{len(elig):,}')
    c5.metric("❌ Não Elegíveis",     f'{len(nelig):,}')
    c6.metric("⬜ ND",               f'{len(nd):,}')

    st.markdown("---")
    t1,t2,t3,t4 = st.tabs(["📊 Aging","🏢 Fornecedoras","📅 Evolução Mensal","👥 Por Equipe"])

    with t1:
        st.markdown("#### Aging — Distribuição por Faixa")
        ag = df.groupby("aging").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        ag["Valor"] = ag["Valor"].apply(fmt_brl)
        ag = ag.rename(columns={"aging":"Faixa"})
        st.dataframe(ag, use_container_width=True, hide_index=True)
        st.bar_chart(df.groupby("aging")["uc_cpf"].count(), color="#2daf5c")

    with t2:
        st.markdown("#### Resultado por Fornecedora")
        fdf = df.groupby("fornecedora").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        fdf["Valor"] = fdf["Valor"].apply(fmt_brl)
        st.dataframe(fdf.rename(columns={"fornecedora":"Fornecedora"}), use_container_width=True, hide_index=True)

    with t3:
        st.markdown("#### Evolução Mensal")
        dfall = buscar_processamentos()
        if not dfall.empty:
            dfall["valor"] = pd.to_numeric(dfall["valor"], errors="coerce").fillna(0)
            evol = dfall[dfall["elegibilidade"]=="Elegível"].groupby("_mes_ano")["valor"].sum().reset_index()
            evol.columns = ["Mês","Valor"]
            st.bar_chart(evol.sort_values("Mês").set_index("Mês"), color="#2daf5c")

    with t4:
        st.markdown("#### Por Equipe")
        edf = df.groupby("_equipe").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        edf["Equipe"] = edf["_equipe"].map(lambda x: EQUIPES.get(x,{}).get("nome",x))
        edf["Valor"]  = edf["Valor"].apply(fmt_brl)
        st.dataframe(edf[["Equipe","Boletos","Clientes","Valor"]], use_container_width=True, hide_index=True)

    st.markdown("---")
    if st.button("📥 Exportar Excel"):
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="xlsxwriter") as w:
            df.to_excel(w, sheet_name="Dados Completos", index=False)
            elig.to_excel(w, sheet_name="Elegíveis", index=False)
        st.download_button("⬇️ Baixar Excel", data=out.getvalue(),
            file_name=f"iGreen_Inadimplencia_{mes_f}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── UPLOAD ─────────────────────────────────────
def pagina_upload():
    u = st.session_state.usuario
    equipe_id = u["equipe"] or "tamires"

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:14px;padding:20px 24px;margin-bottom:20px;border-left:4px solid #2daf5c">
        <h1 style="margin:0">📁 Upload de Bases Mensais</h1>
        <p style="color:#5a9a70;margin:4px 0 0;font-size:13px">Aceita .xlsx e .csv · O sistema processa automaticamente</p>
    </div>
    """, unsafe_allow_html=True)

    mes_proc = st.selectbox("📅 Mês de Referência", get_meses_disponiveis())

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### 📄 PAGOS *(obrigatório)*")
        pf   = st.file_uploader("PAGOS",    type=["xlsx","csv"], label_visibility="collapsed", key="pagos")
        st.markdown("#### 📞 LIGAÇÕES")
        lf   = st.file_uploader("LIGAÇÕES", type=["xlsx","csv"], label_visibility="collapsed", key="lig")
    with c2:
        st.markdown("#### 💬 CHAT")
        cf   = st.file_uploader("CHAT",     type=["xlsx","csv"], label_visibility="collapsed", key="chat")
        st.markdown("#### 📣 DISPAROS")
        df_u = st.file_uploader("DISPAROS", type=["xlsx","csv"], label_visibility="collapsed", key="disp")

    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    for col,arq,nome in [(c1,pf,"PAGOS"),(c2,cf,"CHAT"),(c3,lf,"LIGAÇÕES"),(c4,df_u,"DISPAROS")]:
        with col:
            st.success(f"✅ {nome}") if arq else st.warning(f"⏳ {nome}")

    st.markdown("---")
    if st.button("⚡ PROCESSAR MÊS", use_container_width=True):
        if not pf:
            st.error("⚠ O arquivo PAGOS é obrigatório!")
            return
        with st.spinner("Processando bases..."):
            df_res, erros = processar_bases(pf, cf, lf, df_u, equipe_id, mes_proc)
        for e in erros: st.error(e)
        if df_res is not None and not df_res.empty:
            salvar_processamento(mes_proc, equipe_id, df_res)
            elig = df_res[df_res["elegibilidade"] == "Elegível"]
            st.success(f"✅ {len(df_res):,} registros processados e salvos!")
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("💰 Valor Elegível",  fmt_brl(elig["valor"].sum()))
            c2.metric("📋 Boletos",         f"{len(df_res):,}")
            c3.metric("👥 Clientes",        f"{df_res['uc_cpf'].nunique():,}")
            c4.metric("✅ Elegíveis",       f"{len(elig):,}")
            c5.metric("❌ Não Elegíveis",   f"{len(df_res[df_res['elegibilidade']=='Não Elegível']):,}")
            st.markdown("#### Prévia")
            st.dataframe(df_res[["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging"]].head(50), use_container_width=True)

# ── HISTÓRICO ──────────────────────────────────
def pagina_historico(mes_ano):
    u = st.session_state.usuario
    equipe_id = u["equipe"]

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:14px;padding:20px 24px;margin-bottom:20px;border-left:4px solid #2daf5c">
        <h1 style="margin:0">📋 Histórico</h1>
        <p style="color:#5a9a70;margin:4px 0 0;font-size:13px">{mes_ano.replace('-',' ')}</p>
    </div>
    """, unsafe_allow_html=True)

    t1,t2 = st.tabs(["📈 Resultados por Semana","📁 Bases Processadas"])

    with t1:
        if not equipe_id:
            st.info("Use o Dashboard Executivo para histórico completo.")
            return

        agentes    = [a for a in AGENTES if a["equipe"] == equipe_id]
        resultados = buscar_resultados_mes(mes_ano)
        scoms      = [s for s in SEMANAS if f"{mes_ano}__{s[0]}__{equipe_id}" in resultados]

        if not scoms:
            st.info("Nenhum resultado lançado para este mês ainda.")
        else:
            cols = st.columns(min(len(scoms), 4))
            for i,(sid,sl) in enumerate(scoms):
                tot = resultados[f"{mes_ano}__{sid}__{equipe_id}"].get("totalEquipe",0)
                ant = resultados.get(f"{mes_ano}__{scoms[i-1][0]}__{equipe_id}",{}).get("totalEquipe",0) if i>0 else 0
                v   = calc_variacao(tot, ant)
                with cols[i%4]:
                    st.metric(sl, fmt_brl(tot), delta=f"{v:+.1f}% vs anterior" if v is not None else None)

            rows = []
            for a in agentes:
                row = {"Agente": a["nome"] + (" ⭐" if a["pleno"] else "")}
                for sid,sl in scoms:
                    val = resultados[f"{mes_ano}__{sid}__{equipe_id}"].get("agentes",{}).get(a["id"],{}).get("valorRecebido",0)
                    row[sl] = fmt_brl(val) if val > 0 else "—"
                rows.append(row)
            df = pd.DataFrame(rows)
            df.index = range(1, len(df)+1)
            st.dataframe(df, use_container_width=True)

    with t2:
        mp = listar_meses_processados()
        if not mp:
            st.info("Nenhuma base processada ainda.")
        else:
            mh = st.selectbox("Selecione o mês", mp)
            df = buscar_processamentos(mh, equipe_id)
            if df.empty:
                st.info("Sem dados para este mês.")
            else:
                df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
                c1,c2,c3 = st.columns(3)
                c1.metric("Valor Elegível", fmt_brl(df[df["elegibilidade"]=="Elegível"]["valor"].sum()))
                c2.metric("Boletos",        f'{len(df):,}')
                c3.metric("Clientes",       f'{df["uc_cpf"].nunique():,}')
                st.dataframe(df[["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging"]].head(100), use_container_width=True)

                if st.button("📥 Exportar Excel"):
                    out = io.BytesIO()
                    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
                        df.to_excel(w, index=False)
                    st.download_button("⬇️ Baixar", data=out.getvalue(),
                        file_name=f"iGreen_{mh}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── AGENTES ────────────────────────────────────
def pagina_agentes():
    u = st.session_state.usuario
    st.markdown("## 👥 Agentes Cadastrados")
    eqs = list(EQUIPES.keys()) if u["role"] in ["admin","diretor"] else [u["equipe"]]
    for eq_id in eqs:
        eq  = EQUIPES[eq_id]
        ags = [a for a in AGENTES if a["equipe"] == eq_id]
        with st.expander(f"{eq['emoji']} Equipe {eq['nome']} — {len(ags)} agentes", expanded=True):
            if not ags: st.info("Sem agentes.")
            else:
                rows = [{"#":i+1,"Nome":a["nome"]+(" ⭐" if a["pleno"] else ""),"Nível":"Pleno" if a["pleno"] else "Operador"} for i,a in enumerate(ags)]
                st.dataframe(pd.DataFrame(rows).set_index("#"), use_container_width=True)

# ── MAIN ───────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login()
        return

    mes_ano, semana_id, semana_label, pagina = render_sidebar()
    u = st.session_state.usuario

    if u["role"] == "diretor":
        if "Dashboard"  in pagina: pagina_dashboard_executivo()
        elif "Quadro"   in pagina: pagina_quadro_resultado(mes_ano, semana_id, semana_label)
        elif "Histórico" in pagina: pagina_historico(mes_ano)

    elif u["role"] == "admin":
        if "Dashboard"  in pagina: pagina_dashboard_executivo()
        elif "Quadro"   in pagina: pagina_quadro_resultado(mes_ano, semana_id, semana_label)
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano, semana_id, semana_label)
        elif "Upload"   in pagina: pagina_upload()
        elif "Histórico" in pagina: pagina_historico(mes_ano)
        elif "Agentes"  in pagina: pagina_agentes()

    else:  # gestor
        if "Quadro"     in pagina: pagina_quadro_resultado(mes_ano, semana_id, semana_label)
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano, semana_id, semana_label)
        elif "Upload"   in pagina: pagina_upload()
        elif "Histórico" in pagina: pagina_historico(mes_ano)

if __name__ == "__main__":
    main()
