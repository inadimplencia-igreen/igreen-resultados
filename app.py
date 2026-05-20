import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, date
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
</style>
""", unsafe_allow_html=True)

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
MESES_NOMES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

# ── MONGODB ────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
    return client[st.secrets["mongo"]["db"]]

# ── OPERADORES (dinâmico por equipe) ──────────
def buscar_operadores(equipe_id):
    docs = list(get_db().operadores.find({"equipeId": equipe_id}).sort("nome", 1))
    return docs

def salvar_operador(equipe_id, nome, pleno=False):
    import uuid
    op_id = str(uuid.uuid4())[:12].replace("-","")
    get_db().operadores.insert_one({
        "_id": op_id, "equipeId": equipe_id,
        "nome": nome, "pleno": pleno,
        "criadoEm": datetime.now()
    })
    return op_id

def excluir_operador(op_id):
    get_db().operadores.delete_one({"_id": op_id})

def atualizar_operador(op_id, nome, pleno):
    get_db().operadores.update_one({"_id": op_id}, {"$set": {"nome": nome, "pleno": pleno}})

# ── METAS ──────────────────────────────────────
def salvar_meta_operador(mes_ano, equipe_id, op_id, valor):
    doc_id = f"meta_op__{mes_ano}__{equipe_id}__{op_id}"
    get_db().metas.update_one(
        {"_id": doc_id},
        {"$set": {"_id": doc_id, "mesAno": mes_ano, "equipeId": equipe_id,
                  "opId": op_id, "valor": valor}},
        upsert=True
    )

def buscar_metas_equipe(mes_ano, equipe_id):
    docs = list(get_db().metas.find({"mesAno": mes_ano, "equipeId": equipe_id}))
    return {d["opId"]: d.get("valor", 0) for d in docs}

def salvar_meta_gestora(mes_ano, equipe_id, meta, target_pct):
    doc_id = f"meta_gest__{mes_ano}__{equipe_id}"
    get_db().metas.update_one(
        {"_id": doc_id},
        {"$set": {"_id": doc_id, "mesAno": mes_ano, "equipeId": equipe_id,
                  "metaGestora": meta, "targetPct": target_pct, "tipo": "gestora"}},
        upsert=True
    )

def buscar_meta_gestora(mes_ano, equipe_id):
    doc_id = f"meta_gest__{mes_ano}__{equipe_id}"
    doc = get_db().metas.find_one({"_id": doc_id})
    return doc or {"metaGestora": 0, "targetPct": 100}

# ── LANÇAMENTOS ────────────────────────────────
def criar_lancamento(mes_ano, equipe_id, data_ref, label, agentes_data, total, vg, sem_int, dt, td):
    ts    = datetime.now().strftime("%Y%m%d%H%M%S%f")
    doc_id = f"lanc__{mes_ano}__{equipe_id}__{ts}"
    get_db().lancamentos.insert_one({
        "_id": doc_id, "mesAno": mes_ano, "equipeId": equipe_id,
        "dataRef": data_ref, "label": label,
        "agentes": agentes_data, "totalEquipe": total,
        "valorGeral": vg, "semInteracao": sem_int,
        "diasTrabalhados": dt, "totalDias": td,
        "criadoEm": datetime.now()
    })
    return doc_id

def buscar_lancamentos(mes_ano, equipe_id):
    docs = list(get_db().lancamentos.find(
        {"mesAno": mes_ano, "equipeId": equipe_id}
    ).sort("criadoEm", -1))
    return docs

def buscar_lancamentos_mes_todas(mes_ano):
    docs = list(get_db().lancamentos.find({"mesAno": mes_ano}).sort("criadoEm", -1))
    return docs

def excluir_lancamento(doc_id):
    get_db().lancamentos.delete_one({"_id": doc_id})

def buscar_ultimo_lancamento(mes_ano, equipe_id):
    doc = get_db().lancamentos.find_one(
        {"mesAno": mes_ano, "equipeId": equipe_id},
        sort=[("criadoEm", -1)]
    )
    return doc or {}

def buscar_todos_lancamentos_equipe(equipe_id):
    docs = list(get_db().lancamentos.find({"equipeId": equipe_id}).sort("criadoEm", -1))
    return docs

# ── BASES PROCESSADAS ──────────────────────────
def salvar_processamento(mes_ano, equipe_id, df):
    doc_id = f"proc__{mes_ano}__{equipe_id}"
    get_db().processamentos.update_one(
        {"_id": doc_id},
        {"$set": {"_id": doc_id, "mesAno": mes_ano, "equipeId": equipe_id,
                  "registros": df.to_dict("records"), "atualizadoEm": datetime.now()}},
        upsert=True
    )

def buscar_processamentos(mes_ano=None, equipe_id=None):
    filtro = {}
    if mes_ano:   filtro["mesAno"]   = mes_ano
    if equipe_id: filtro["equipeId"] = equipe_id
    docs   = list(get_db().processamentos.find(filtro))
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
    if v is None or v == "": return "R$ 0,00"
    try: return "R$ " + f"{float(v):_.2f}".replace(".", ",").replace("_", ".")
    except: return "R$ 0,00"

def parse_brl(s):
    if not s: return 0.0
    try: return float(str(s).replace("R$","").replace(".","").replace(",",".").strip())
    except: return 0.0

def fmt_input(v):
    if not v or float(v) == 0: return ""
    return f"{float(v):_.2f}".replace(".", ",").replace("_", ".")

def calc_projecao(valor, dias_trab, total_dias):
    if not dias_trab or dias_trab <= 0: return 0
    return (valor / dias_trab) * total_dias

def calc_variacao(atual, anterior):
    if not anterior or anterior == 0: return None
    return ((atual - anterior) / anterior) * 100

def cor_pct(pct):
    if pct >= 80: return "#2daf5c"
    if pct >= 50: return "#f0a500"
    return "#e03c3c"

def status_pct(pct):
    if pct >= 80: return "🟢"
    if pct >= 50: return "🟡"
    return "🔴"

def get_mes_ano_atual():
    hoje = datetime.now()
    return f"{MESES_NOMES[hoje.month-1]}-{hoje.year}"

def get_todos_meses_ano(ano=None):
    if not ano: ano = datetime.now().year
    return [f"{m}-{ano}" for m in MESES_NOMES]

def get_anos_disponiveis():
    hoje = datetime.now()
    return [str(hoje.year), str(hoje.year - 1)]

def aging_faixa(dias):
    if pd.isna(dias): return "ND"
    if dias <= 30: return "D0-30"
    if dias <= 60: return "D31-60"
    if dias <= 90: return "D61-90"
    return "D90+"

def header_page(titulo, sub=""):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;
                border-radius:14px;padding:20px 24px;margin-bottom:20px;border-left:4px solid #2daf5c">
        <h1 style="margin:0">{titulo}</h1>
        {"<p style='color:#5a9a70;margin:4px 0 0;font-size:13px'>" + sub + "</p>" if sub else ""}
    </div>
    """, unsafe_allow_html=True)

# ── PROCESSAMENTO DE BASES ─────────────────────
def processar_bases(pagos_file, chat_file, lig_file, disp_file, equipe_id, mes_ano):
    def ler(f):
        if f is None: return None
        try: return pd.read_csv(f, header=0) if f.name.endswith(".csv") else pd.read_excel(f, header=0)
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
        primeiro_contato = df_todos.groupby("uc_cpf")["data_contato"].min().reset_index().rename(
            columns={"data_contato":"primeiro_contato"})

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
    c1,c2,c3 = st.columns([1,1.2,1])
    with c2:
        st.markdown("""
        <div style="text-align:center;padding:48px 0 32px">
            <div style="width:72px;height:72px;background:linear-gradient(135deg,#1a6b35,#2daf5c);
                        border-radius:18px;display:inline-flex;align-items:center;justify-content:center;
                        font-size:36px;font-weight:800;color:white;margin-bottom:16px;
                        box-shadow:0 8px 32px rgba(45,175,92,0.4)">G</div>
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
                <div style="width:40px;height:40px;background:linear-gradient(135deg,#1a6b35,#2daf5c);
                            border-radius:10px;display:flex;align-items:center;justify-content:center;
                            font-weight:800;font-size:18px;color:white">G</div>
                <div><div style="color:#ffffff;font-weight:700;font-size:14px">iGreen</div>
                     <div style="color:#5a9a70;font-size:11px">Inadimplência</div></div>
            </div>
            <div style="background:rgba(45,175,92,0.1);border:1px solid rgba(45,175,92,0.2);
                        border-radius:8px;padding:10px 12px;margin-bottom:16px">
                <div style="color:#2daf5c;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px">
                    {'👔 Diretoria' if u['role']=='diretor' else '⚙️ Admin' if u['role']=='admin' else '👤 Gestor'}
                </div>
                <div style="color:#ffffff;font-size:14px;font-weight:600;margin-top:2px">{u['nome']}</div>
            </div>
        </div><hr>
        """, unsafe_allow_html=True)

        # Seletor de ano e mês
        st.markdown("**📅 Período**")
        anos   = get_anos_disponiveis()
        ano    = st.selectbox("Ano", anos, label_visibility="collapsed")
        meses  = get_todos_meses_ano(int(ano))
        mes_labels = [m.split("-")[0] for m in meses]
        mes_idx    = datetime.now().month - 1
        mes_sel    = st.selectbox("Mês", mes_labels, index=mes_idx, label_visibility="collapsed")
        mes_ano    = f"{mes_sel}-{ano}"

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**📌 Navegação**")

        if u["role"] == "diretor":
            pags = ["🏆 Quadro de Resultados", "📊 Dashboard Executivo",
                    "📈 Análise de Projeção", "📋 Histórico"]
        elif u["role"] == "admin":
            pags = ["🏆 Quadro de Resultados", "✏️ Lançamento",
                    "📊 Dashboard Executivo", "📈 Análise de Projeção",
                    "📁 Upload de Bases", "📋 Histórico",
                    "👥 Operadores", "🎯 Metas"]
        else:
            pags = ["🏆 Quadro de Resultados", "✏️ Lançamento",
                    "📈 Análise de Projeção", "📁 Upload de Bases",
                    "📋 Histórico", "👥 Operadores", "🎯 Metas"]

        pag = st.radio("", pags, label_visibility="collapsed")
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("⏻ Sair", use_container_width=True):
            del st.session_state.usuario; st.rerun()

    return mes_ano, pag

# ── OPERADORES ─────────────────────────────────
def pagina_operadores():
    u = st.session_state.usuario
    equipe_id = u["equipe"]
    eq = EQUIPES[equipe_id]

    header_page("👥 Operadores", f"Equipe {eq['nome']} · Gerencie seus operadores")

    # Cadastro
    with st.expander("➕ Cadastrar Novo Operador", expanded=False):
        c1,c2,c3 = st.columns([3,1,1])
        with c1: novo_nome = st.text_input("Nome do Operador", placeholder="Nome completo")
        with c2: novo_pleno = st.checkbox("Pleno")
        with c3:
            st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
            if st.button("➕ Cadastrar", use_container_width=True):
                if novo_nome.strip():
                    salvar_operador(equipe_id, novo_nome.strip(), novo_pleno)
                    st.success(f"✅ {novo_nome} cadastrado!")
                    st.rerun()
                else:
                    st.error("Digite o nome do operador.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    OPERADORES_PADRAO = {
        "luciano": [
            ("Jennifer Silveira", True),("Paulo Roberto", False),("Samires Barros", False),
            ("Maycow Gabriel", False),("Otaides Junior", False),("Heverton Tavares", False),
            ("Camila Nara", False),("Caua Alves", False),("Eduarda Sanqueta", False),
            ("Jheniffer Santos", False),("Ketie Silva", False),("Emanuel Cardoso", False),
            ("Victória Silva", False),("Grasielli Santos", False),("Laura Silva", False),
            ("Michelle Batista", False),("Lorenzzo Pereira", False),("Diogo Oliveira", False),
            ("Maria Paulino", False),("Gabrielle Martins", False),("Marcos Martins", False),
        ],
        "deborah": [
            ("Mikael Dias", False),("Amanda Eduarda", False),("Larissa Barcelos", False),
            ("Nicole Amaral", False),("Sara Rocha", False),("Isabelly Araujo", False),("Silye Paula", False),
        ],
        "tamires": [
            ("Danilo Rodrigues", True),("Raiane Pereira", False),("Wynara Dos Reis", False),
            ("Esteffany Souza", False),("André Gomes", False),("Wanessa Cardoso", False),
            ("Larisse Garcia", False),("Arthur Alves", False),
        ],
        "metcool": [],
    }
    ops = buscar_operadores(equipe_id)
    if not ops:
        st.info("Nenhum operador cadastrado ainda.")
        padrao = OPERADORES_PADRAO.get(equipe_id, [])
        if padrao:
            if st.button("📥 Importar Operadores Padrão", use_container_width=True):
                for nome, pleno in padrao:
                    salvar_operador(equipe_id, nome, pleno)
                st.success(f"✅ {len(padrao)} operadores importados!")
                st.rerun()
        return
    st.markdown(f"**{len(ops)} operadores cadastrados**")

    for op in ops:
        c1,c2,c3,c4 = st.columns([3,1,1,1])
        with c1:
            novo_n = st.text_input("n", value=op["nome"], label_visibility="collapsed",
                                    key=f"n_{op['_id']}")
        with c2:
            novo_p = st.checkbox("Pleno", value=op.get("pleno", False), key=f"p_{op['_id']}")
        with c3:
            if st.button("💾", key=f"s_{op['_id']}", help="Salvar"):
                atualizar_operador(op["_id"], novo_n, novo_p)
                st.success("Salvo!")
                st.rerun()
        with c4:
            if st.button("🗑️", key=f"d_{op['_id']}", help="Excluir"):
                excluir_operador(op["_id"])
                st.warning(f"{op['nome']} removido.")
                st.rerun()

# ── METAS ──────────────────────────────────────
def pagina_metas(mes_ano):
    u = st.session_state.usuario
    equipe_id = u["equipe"]
    eq = EQUIPES[equipe_id]
    ops = buscar_operadores(equipe_id)

    header_page("🎯 Metas", f"Equipe {eq['nome']} · {mes_ano.replace('-',' ')}")

    if not ops:
        st.warning("Cadastre operadores primeiro em 👥 Operadores.")
        return

    # Meta da gestora
    st.markdown("### 🏆 Meta da Gestora")
    meta_gest_doc = buscar_meta_gestora(mes_ano, equipe_id)
    c1,c2,c3 = st.columns([2,1,1])
    with c1:
        meta_gest_str = st.text_input("💰 Meta Base do Mês (R$)",
            value=fmt_input(meta_gest_doc.get("metaGestora", 0)),
            placeholder="Ex: 1.600.000,00", key="meta_gest")
    with c2:
        target_pct = st.number_input("🎯 Target (%)", min_value=100, max_value=200,
            value=int(meta_gest_doc.get("targetPct", 125)), key="target_pct")
    with c3:
        mg = parse_brl(meta_gest_str)
        target_val = mg * (target_pct / 100)
        st.markdown(f"<div style='padding-top:28px;color:#2daf5c;font-weight:700'>{fmt_brl(target_val)}</div>",
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 👤 Metas por Operador")

    metas_salvas = buscar_metas_equipe(mes_ano, equipe_id)
    metas_novas  = {}

    cols_h = st.columns([3,2])
    cols_h[0].markdown("**Operador**")
    cols_h[1].markdown("**Meta Mensal (R$)**")

    for op in ops:
        meta_salva = metas_salvas.get(op["_id"], 0)
        c1,c2 = st.columns([3,2])
        with c1:
            st.markdown(f"<div style='padding-top:10px;color:#e0f0e8'>{'⭐ ' if op.get('pleno') else ''}{op['nome']}</div>",
                        unsafe_allow_html=True)
        with c2:
            val = st.text_input("m", label_visibility="collapsed",
                value=fmt_input(meta_salva), placeholder="R$ 0,00",
                key=f"mg_{mes_ano}_{op['_id']}")
            metas_novas[op["_id"]] = parse_brl(val)

    st.markdown("---")
    if st.button("💾 Salvar Todas as Metas", use_container_width=True):
        for op_id, val in metas_novas.items():
            salvar_meta_operador(mes_ano, equipe_id, op_id, val)
        salvar_meta_gestora(mes_ano, equipe_id,
                            parse_brl(meta_gest_str), target_pct)
        st.success("✅ Metas salvas com sucesso!")
        st.rerun()

# ── LANÇAMENTO ─────────────────────────────────
def pagina_lancamento(mes_ano):
    u = st.session_state.usuario
    equipe_id = u["equipe"]
    eq = EQUIPES[equipe_id]
    ops = buscar_operadores(equipe_id)

    header_page("✏️ Lançamento de Resultado", f"Equipe {eq['nome']} · {mes_ano.replace('-',' ')}")

    if not ops:
        st.warning("⚠ Cadastre operadores primeiro em 👥 Operadores.")
        return

    metas_salvas  = buscar_metas_equipe(mes_ano, equipe_id)
    meta_gest_doc = buscar_meta_gestora(mes_ano, equipe_id)

    # Config do lançamento
    st.markdown("### ⚙️ Configuração do Lançamento")
    c1,c2,c3,c4 = st.columns([2,1,1,1])
    with c1:
        hoje = date.today()
        data_sel = st.date_input("📅 Data do Resultado", value=hoje,
                                  min_value=date(hoje.year,1,1),
                                  max_value=date(hoje.year,12,31))
        eh_fechamento = st.checkbox("📌 Este é o Fechamento do Mês")
        label = "Fechamento do Mês" if eh_fechamento else data_sel.strftime("%d/%m/%Y")
    with c2:
        dt = st.number_input("Dias Trabalhados", min_value=0, max_value=31, value=0)
    with c3:
        td = st.number_input("Total de Dias no Mês", min_value=1, max_value=31, value=22)
    with c4:
        vgs = st.text_input("💰 Valor Geral (R$)", placeholder="Ex: 200.000,00")

    st.markdown("---")
    st.markdown("### 👤 Valores por Operador")

    cols_h = st.columns([3,2,2,2,2])
    for h,t in zip(cols_h, ["**Operador**","**Meta**","**Valor Recebido (R$)**","**Projeção**","**% Meta**"]):
        h.markdown(t)

    vi = {}
    for op in ops:
        meta = metas_salvas.get(op["_id"], 0)
        c1,c2,c3,c4,c5 = st.columns([3,2,2,2,2])
        c1.markdown(f"<div style='padding-top:10px;color:#e0f0e8;font-weight:500'>{'⭐ ' if op.get('pleno') else ''}{op['nome']}</div>",
                    unsafe_allow_html=True)
        c2.markdown(f"<div style='padding-top:10px;color:#5a9a70'>{fmt_brl(meta) if meta > 0 else '—'}</div>",
                    unsafe_allow_html=True)
        val_str = c3.text_input("v", label_visibility="collapsed",
                                 placeholder="R$ 0,00", key=f"vl_{op['_id']}")
        val  = parse_brl(val_str)
        proj = calc_projecao(val, dt, td)
        pct  = (val/meta*100) if meta > 0 else 0
        c4.markdown(f"<div style='padding-top:10px;color:#5a9a70'>{fmt_brl(proj) if proj > 0 else '—'}</div>",
                    unsafe_allow_html=True)
        c5.markdown(f"<div style='padding-top:10px;color:{cor_pct(pct)};font-weight:700'>{status_pct(pct) if meta > 0 else '⚪'} {f'{pct:.1f}%' if meta > 0 else '—'}</div>",
                    unsafe_allow_html=True)
        vi[op["_id"]] = val

    tc  = sum(vi.values())
    vg  = parse_brl(vgs)
    sem = max(0, vg - tc)
    mg  = meta_gest_doc.get("metaGestora", 0)
    tpct = meta_gest_doc.get("targetPct", 125)
    pct_gest = (tc/mg*100) if mg > 0 else 0

    st.markdown("---")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("🤝 Com Interação",  fmt_brl(tc))
    c2.metric("🔕 Sem Interação",  fmt_brl(sem))
    c3.metric("💰 Total Geral",    fmt_brl(vg))
    c4.metric("📈 Projeção",       fmt_brl(calc_projecao(tc, dt, td)))
    c5.metric(f"🎯 Meta ({pct_gest:.1f}%)", fmt_brl(mg))

    st.markdown("---")
    if st.button("💾 Salvar Lançamento", use_container_width=True):
        if not any(v > 0 for v in vi.values()):
            st.warning("⚠ Preencha pelo menos um valor antes de salvar.")
            return
        agentes_data = {op["_id"]: {"valorRecebido": vi[op["_id"]], "nome": op["nome"]} for op in ops}
        criar_lancamento(mes_ano, equipe_id, str(data_sel), label,
                         agentes_data, tc, vg, sem, dt, td)
        st.success(f"✅ Lançamento de {label} salvo com sucesso!")
        st.rerun()

# ── QUADRO DE RESULTADOS ───────────────────────
def pagina_quadro(mes_ano):
    u = st.session_state.usuario
    is_dir = u["role"] == "diretor"
    equipes_ver = list(EQUIPES.keys()) if is_dir else [u["equipe"]]

    header_page("🏆 Quadro de Resultados", mes_ano.replace("-"," "))

    for equipe_id in equipes_ver:
        eq  = EQUIPES[equipe_id]
        ops = buscar_operadores(equipe_id)
        if not ops and not is_dir: continue

        lancs = buscar_lancamentos(mes_ano, equipe_id)
        if not lancs:
            st.info(f"{eq['emoji']} Equipe {eq['nome']} — Nenhum lançamento ainda.")
            continue

        # Pega o lançamento mais recente
        ultimo = lancs[0]
        meta_gest_doc = buscar_meta_gestora(mes_ano, equipe_id)
        metas_ops     = buscar_metas_equipe(mes_ano, equipe_id)
        mg   = meta_gest_doc.get("metaGestora", 0)
        tpct = meta_gest_doc.get("targetPct", 125)
        tc   = ultimo.get("totalEquipe", 0)
        dt   = ultimo.get("diasTrabalhados", 0)
        td   = ultimo.get("totalDias", 22)
        proj = calc_projecao(tc, dt, td)
        pct_mg   = (tc/mg*100) if mg > 0 else 0
        target_v = mg * (tpct/100)
        pct_tg   = (tc/target_v*100) if target_v > 0 else 0

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;
                    border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid {eq['cor']}">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <div style="font-size:16px;font-weight:700;color:#ffffff">{eq['emoji']} Equipe {eq['nome']} · {ultimo.get('label','')}</div>
                <div style="display:flex;gap:16px">
                    <div style="text-align:center">
                        <div style="color:#5a9a70;font-size:10px;text-transform:uppercase">% Meta</div>
                        <div style="color:{cor_pct(pct_mg)};font-size:22px;font-weight:800">{pct_mg:.1f}%</div>
                    </div>
                    <div style="text-align:center">
                        <div style="color:#5a9a70;font-size:10px;text-transform:uppercase">% Target {tpct}%</div>
                        <div style="color:{cor_pct(pct_tg)};font-size:22px;font-weight:800">{pct_tg:.1f}%</div>
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:24px;margin-top:12px;flex-wrap:wrap">
                <div><span style="color:#5a9a70;font-size:11px">RECEBIDO</span><br>
                     <span style="color:#2daf5c;font-weight:700;font-size:15px">{fmt_brl(tc)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">META</span><br>
                     <span style="color:#e0f0e8;font-weight:600">{fmt_brl(mg)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">TARGET {tpct}%</span><br>
                     <span style="color:#e0f0e8;font-weight:600">{fmt_brl(target_v)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO</span><br>
                     <span style="color:#e0f0e8;font-weight:600">{fmt_brl(proj)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">DIAS</span><br>
                     <span style="color:#e0f0e8;font-weight:600">{dt}/{td}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabela operadores
        rows = []
        for op in ops:
            val  = ultimo.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0)
            meta = metas_ops.get(op["_id"], 0)
            proj_op = calc_projecao(val, dt, td)
            pct  = (val/meta*100) if meta > 0 else 0
            rows.append({
                "Status":   status_pct(pct) if meta > 0 else "⚪",
                "Operador": ("⭐ " if op.get("pleno") else "") + op["nome"],
                "Recebido": fmt_brl(val),
                "Meta":     fmt_brl(meta) if meta > 0 else "—",
                "% Meta":   f"{pct:.1f}%" if meta > 0 else "—",
                "Projeção": fmt_brl(proj_op) if proj_op > 0 else "—",
                "_v": val
            })

        df = pd.DataFrame(rows).sort_values("_v", ascending=False).drop(columns=["_v"]).reset_index(drop=True)
        df.index = range(1, len(df)+1)
        st.dataframe(df, use_container_width=True, height=min(600,(len(df)+1)*38+40))
        st.markdown("---")

    # Export
    if st.button("📥 Exportar Excel"):
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            for equipe_id in equipes_ver:
                eq   = EQUIPES[equipe_id]
                ops  = buscar_operadores(equipe_id)
                if not ops: continue
                lancs = buscar_lancamentos(mes_ano, equipe_id)
                if not lancs: continue
                ultimo = lancs[0]
                metas_ops = buscar_metas_equipe(mes_ano, equipe_id)
                rows = []
                for op in ops:
                    val  = ultimo.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0)
                    meta = metas_ops.get(op["_id"],0)
                    pct  = (val/meta*100) if meta > 0 else 0
                    rows.append({"Operador":op["nome"],"Recebido":val,"Meta":meta,"% Meta":f"{pct:.1f}%"})
                pd.DataFrame(rows).to_excel(writer, sheet_name=f"Equipe {eq['nome']}", index=False)
        st.download_button("⬇️ Baixar Excel", data=out.getvalue(),
            file_name=f"iGreen_Resultado_{mes_ano}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── HISTÓRICO ──────────────────────────────────
def pagina_historico(mes_ano):
    u = st.session_state.usuario
    equipe_id = u["equipe"]

    header_page("📋 Histórico", mes_ano.replace("-"," "))

    t1,t2 = st.tabs(["📈 Lançamentos de Resultado","📁 Bases Processadas"])

    with t1:
        if not equipe_id:
            st.info("Selecione uma equipe específica para ver lançamentos.")
            return

        lancs = buscar_lancamentos(mes_ano, equipe_id)
        ops   = buscar_operadores(equipe_id)
        if not lancs:
            st.info("Nenhum lançamento para este mês.")
        else:
            for lanc in lancs:
                with st.expander(f"📅 {lanc.get('label','')} — {fmt_brl(lanc.get('totalEquipe',0))} — {lanc.get('criadoEm','')[:16] if lanc.get('criadoEm') else ''}", expanded=False):
                    rows = []
                    for op in ops:
                        val = lanc.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0)
                        rows.append({"Operador": op["nome"], "Valor": fmt_brl(val)})
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Com Interação", fmt_brl(lanc.get("totalEquipe",0)))
                    c2.metric("Sem Interação", fmt_brl(lanc.get("semInteracao",0)))
                    c3.metric("Total Geral",   fmt_brl(lanc.get("valorGeral",0)))
                    st.markdown("---")
                    if st.button(f"🗑️ Excluir este lançamento", key=f"del_{lanc['_id']}"):
                        excluir_lancamento(lanc["_id"])
                        st.warning("Lançamento excluído!")
                        st.rerun()

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

# ── ANÁLISE DE PROJEÇÃO ────────────────────────
def pagina_analise_projecao(mes_ano):
    u = st.session_state.usuario
    is_dir = u["role"] == "diretor"
    equipes_ver = list(EQUIPES.keys()) if is_dir else [u["equipe"]]

    header_page("📈 Análise de Projeção", f"Comparativo com mês anterior · {mes_ano.replace('-',' ')}")

    # Mês anterior
    partes = mes_ano.split("-")
    mes_idx = MESES_NOMES.index(partes[0])
    ano_int = int(partes[1])
    if mes_idx == 0:
        mes_ant = f"{MESES_NOMES[11]}-{ano_int-1}"
    else:
        mes_ant = f"{MESES_NOMES[mes_idx-1]}-{ano_int}"

    st.markdown(f"<p style='color:#5a9a70'>Comparando <strong style='color:#2daf5c'>{mes_ano.replace('-',' ')}</strong> vs <strong style='color:#e0f0e8'>{mes_ant.replace('-',' ')}</strong></p>", unsafe_allow_html=True)
    st.markdown("---")

    for equipe_id in equipes_ver:
        eq  = EQUIPES[equipe_id]
        ops = buscar_operadores(equipe_id)
        if not ops: continue

        lancs_atual = buscar_lancamentos(mes_ano, equipe_id)
        lancs_ant   = buscar_lancamentos(mes_ant,  equipe_id)

        if not lancs_atual:
            st.info(f"{eq['emoji']} Equipe {eq['nome']} — Sem lançamentos no mês atual.")
            continue

        ultimo_atual = lancs_atual[0]
        ultimo_ant   = lancs_ant[0] if lancs_ant else {}

        dt_at = ultimo_atual.get("diasTrabalhados", 0)
        td_at = ultimo_atual.get("totalDias", 22)
        dt_an = ultimo_ant.get("diasTrabalhados", 0) if ultimo_ant else 0
        td_an = ultimo_ant.get("totalDias", 22) if ultimo_ant else 22

        tc_at = ultimo_atual.get("totalEquipe", 0)
        tc_an = ultimo_ant.get("totalEquipe", 0) if ultimo_ant else 0
        proj_at = calc_projecao(tc_at, dt_at, td_at)
        proj_an = calc_projecao(tc_an, dt_an, td_an) if tc_an > 0 else 0
        var_eq  = calc_variacao(proj_at, proj_an)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;
                    border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid {eq['cor']}">
            <div style="font-size:15px;font-weight:700;color:#ffffff;margin-bottom:10px">{eq['emoji']} Equipe {eq['nome']}</div>
            <div style="display:flex;gap:24px;flex-wrap:wrap">
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO ATUAL</span><br>
                     <span style="color:#2daf5c;font-weight:700;font-size:15px">{fmt_brl(proj_at)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO MÊS ANT.</span><br>
                     <span style="color:#e0f0e8;font-weight:600">{fmt_brl(proj_an)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">VARIAÇÃO</span><br>
                     <span style="color:{cor_pct(100 if (var_eq or 0)>=0 else 0)};font-weight:700;font-size:15px">
                        {'↑' if (var_eq or 0)>=0 else '↓'} {abs(var_eq):.1f}% {"vs mês ant." if var_eq is not None else "sem comparativo"}
                     </span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Por operador
        rows = []
        for op in ops:
            val_at  = ultimo_atual.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0)
            val_an  = ultimo_ant.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0) if ultimo_ant else 0
            proj_op_at = calc_projecao(val_at, dt_at, td_at)
            proj_op_an = calc_projecao(val_an, dt_an, td_an) if val_an > 0 else 0
            var_op  = calc_variacao(proj_op_at, proj_op_an)
            rows.append({
                "Operador":       ("⭐ " if op.get("pleno") else "") + op["nome"],
                "Proj. Atual":    fmt_brl(proj_op_at) if proj_op_at > 0 else "—",
                "Proj. Mês Ant.": fmt_brl(proj_op_an) if proj_op_an > 0 else "—",
                "Variação":       f"{'↑' if (var_op or 0)>=0 else '↓'} {abs(var_op):.1f}%" if var_op is not None else "—",
                "_proj": proj_op_at
            })

        df = pd.DataFrame(rows).sort_values("_proj", ascending=False).drop(columns=["_proj"]).reset_index(drop=True)
        df.index = range(1, len(df)+1)
        st.dataframe(df, use_container_width=True)
        st.markdown("---")

# ── DASHBOARD EXECUTIVO ─────────────────────────
def pagina_dashboard_executivo():
    header_page("📊 Dashboard Executivo", "Gestão de Inadimplência Comercial · Visão consolidada")

    meses_proc = listar_meses_processados()
    if not meses_proc:
        st.info("📭 Nenhuma base processada ainda.")
        return

    c1,c2,c3 = st.columns(3)
    with c1: mes_f = st.selectbox("📅 Mês", ["Todos"] + meses_proc)
    with c2: eq_f  = st.selectbox("👥 Equipe", ["Todas","luciano","deborah","tamires"])

    df = buscar_processamentos(None if mes_f=="Todos" else mes_f, None if eq_f=="Todas" else eq_f)
    if df.empty:
        st.warning("Nenhum dado encontrado.")
        return

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    with c3:
        forns  = ["Todas"] + sorted(df["fornecedora"].dropna().unique().tolist())
        forn_f = st.selectbox("🏢 Fornecedora", forns)
    if forn_f != "Todas":
        df = df[df["fornecedora"] == forn_f]

    st.markdown("---")
    elig  = df[df["elegibilidade"]=="Elegível"]
    nelig = df[df["elegibilidade"]=="Não Elegível"]
    nd    = df[df["elegibilidade"]=="ND"]

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
        ag = df.groupby("aging").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        ag["Valor"] = ag["Valor"].apply(fmt_brl)
        st.dataframe(ag.rename(columns={"aging":"Faixa"}), use_container_width=True, hide_index=True)
        st.bar_chart(df.groupby("aging")["uc_cpf"].count(), color="#2daf5c")

    with t2:
        fdf = df.groupby("fornecedora").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        fdf["Valor"] = fdf["Valor"].apply(fmt_brl)
        st.dataframe(fdf.rename(columns={"fornecedora":"Fornecedora"}), use_container_width=True, hide_index=True)

    with t3:
        dfall = buscar_processamentos()
        if not dfall.empty:
            dfall["valor"] = pd.to_numeric(dfall["valor"], errors="coerce").fillna(0)
            evol = dfall[dfall["elegibilidade"]=="Elegível"].groupby("_mes_ano")["valor"].sum().reset_index()
            evol.columns = ["Mês","Valor"]
            st.bar_chart(evol.sort_values("Mês").set_index("Mês"), color="#2daf5c")

    with t4:
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
            file_name=f"iGreen_{mes_f}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── UPLOAD ─────────────────────────────────────
def pagina_upload(mes_ano):
    u = st.session_state.usuario
    equipe_id = u["equipe"] or "tamires"

    header_page("📁 Upload de Bases Mensais", "Aceita .xlsx e .csv · Processamento automático")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### 📄 PAGOS *(obrigatório)*")
        pf = st.file_uploader("PAGOS",    type=["xlsx","csv"], label_visibility="collapsed", key="pagos")
        st.markdown("#### 📞 LIGAÇÕES")
        lf = st.file_uploader("LIGAÇÕES", type=["xlsx","csv"], label_visibility="collapsed", key="lig")
    with c2:
        st.markdown("#### 💬 CHAT")
        cf = st.file_uploader("CHAT",     type=["xlsx","csv"], label_visibility="collapsed", key="chat")
        st.markdown("#### 📣 DISPAROS")
        df_u = st.file_uploader("DISPAROS",type=["xlsx","csv"], label_visibility="collapsed", key="disp")

    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    for col,arq,nome in [(c1,pf,"PAGOS"),(c2,cf,"CHAT"),(c3,lf,"LIGAÇÕES"),(c4,df_u,"DISPAROS")]:
        with col:
            st.success(f"✅ {nome}") if arq else st.warning(f"⏳ {nome}")

    st.markdown("---")
    if st.button("⚡ PROCESSAR MÊS", use_container_width=True):
        if not pf:
            st.error("⚠ PAGOS é obrigatório!")
            return
        with st.spinner("Processando..."):
            df_res, erros = processar_bases(pf, cf, lf, df_u, equipe_id, mes_ano)
        for e in erros: st.error(e)
        if df_res is not None and not df_res.empty:
            salvar_processamento(mes_ano, equipe_id, df_res)
            elig = df_res[df_res["elegibilidade"]=="Elegível"]
            st.success(f"✅ {len(df_res):,} registros processados!")
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("💰 Valor Elegível",  fmt_brl(elig["valor"].sum()))
            c2.metric("📋 Boletos",         f"{len(df_res):,}")
            c3.metric("👥 Clientes",        f"{df_res['uc_cpf'].nunique():,}")
            c4.metric("✅ Elegíveis",       f"{len(elig):,}")
            c5.metric("❌ Não Elegíveis",   f"{len(df_res[df_res['elegibilidade']=='Não Elegível']):,}")
            st.dataframe(df_res[["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging"]].head(50), use_container_width=True)

# ── MAIN ───────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login()
        return

    mes_ano, pagina = render_sidebar()
    u = st.session_state.usuario

    if u["role"] == "diretor":
        if "Quadro"     in pagina: pagina_quadro(mes_ano)
        elif "Dashboard" in pagina: pagina_dashboard_executivo()
        elif "Projeção"  in pagina: pagina_analise_projecao(mes_ano)
        elif "Histórico" in pagina: pagina_historico(mes_ano)

    elif u["role"] == "admin":
        if "Quadro"      in pagina: pagina_quadro(mes_ano)
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano)
        elif "Dashboard"  in pagina: pagina_dashboard_executivo()
        elif "Projeção"   in pagina: pagina_analise_projecao(mes_ano)
        elif "Upload"     in pagina: pagina_upload(mes_ano)
        elif "Histórico"  in pagina: pagina_historico(mes_ano)
        elif "Operadores" in pagina: pagina_operadores()
        elif "Metas"      in pagina: pagina_metas(mes_ano)

    else:  # gestor
        if "Quadro"      in pagina: pagina_quadro(mes_ano)
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano)
        elif "Projeção"   in pagina: pagina_analise_projecao(mes_ano)
        elif "Upload"     in pagina: pagina_upload(mes_ano)
        elif "Histórico"  in pagina: pagina_historico(mes_ano)
        elif "Operadores" in pagina: pagina_operadores()
        elif "Metas"      in pagina: pagina_metas(mes_ano)

if __name__ == "__main__":
    main()
