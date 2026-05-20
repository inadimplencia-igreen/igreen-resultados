import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, date
import io
import base64
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="iGreen Performance", page_icon=None, layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* ── BASE ── */
.stApp { background-color: #004d20; }
[data-testid="stSidebar"] {
    background: #003318;
    border-right: 1px solid #005a25;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #e8f5e9;
    border: 1px solid #c8e6c9;
    border-radius: 10px;
    padding: 18px 20px !important;
    border-top: 3px solid #00c853;
}
[data-testid="stMetricValue"] {
    color: #1b5e20 !important;
    font-size: 22px !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #2e7d32 !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: #00c853 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.3px;
    box-shadow: 0 2px 8px rgba(0,200,83,0.3) !important;
}
.stButton > button:hover {
    background: #00e676 !important;
    box-shadow: 0 4px 12px rgba(0,200,83,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── TYPOGRAPHY ── */
h1 { color: #ffffff !important; font-size: 20px !important; font-weight: 700 !important; letter-spacing: -0.3px; }
h2 { color: #e8f5e9 !important; font-size: 16px !important; font-weight: 600 !important; }
h3 { color: #81c784 !important; font-size: 10px !important; font-weight: 600 !important;
     text-transform: uppercase; letter-spacing: 2px; }
p  { color: #c8e6c9 !important; font-size: 13px; }
hr { border: none !important; border-top: 1px solid #005a25 !important; margin: 14px 0 !important; }

/* ── INPUTS ── */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background: #e8f5e9 !important;
    border: 1px solid #a5d6a7 !important;
    color: #1b5e20 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #00c853 !important;
    box-shadow: 0 0 0 2px rgba(0,200,83,0.2) !important;
}
.stTextInput input::placeholder { color: #81c784 !important; }

/* ── SELECTS ── */
.stSelectbox > div > div {
    background: #e8f5e9 !important;
    border: 1px solid #a5d6a7 !important;
    color: #1b5e20 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] .stRadio label {
    color: #a5d6a7 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 4px 0 !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: #a5d6a7 !important;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #ffffff !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #003318 !important;
    border-radius: 6px !important;
    padding: 3px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #81c784 !important;
    border-radius: 5px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 7px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: #00c853 !important;
    color: #ffffff !important;
}

/* ── CHECKBOXES ── */
.stCheckbox label {
    color: #e8f5e9 !important;
    font-size: 13px !important;
}
.stCheckbox label span { color: #e8f5e9 !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > div {
    background: #e8f5e9 !important;
    border: 1.5px dashed #a5d6a7 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] * { color: #2e7d32 !important; }

/* ── ALERTS ── */
.stSuccess > div {
    background: #e8f5e9 !important;
    border: 1px solid #a5d6a7 !important;
    color: #2e7d32 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
.stWarning > div {
    background: #fff8e1 !important;
    border: 1px solid #ffe082 !important;
    color: #f57f17 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
.stError > div {
    background: #ffebee !important;
    border: 1px solid #ef9a9a !important;
    color: #c62828 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
.stInfo > div {
    background: #e3f2fd !important;
    border: 1px solid #90caf9 !important;
    color: #1565c0 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}

/* ── DATA TABLE ── */
[data-testid="stDataFrame"] {
    border: 1px solid #a5d6a7 !important;
    border-radius: 8px !important;
    background: #e8f5e9 !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: #e8f5e9 !important;
    border: 1px solid #a5d6a7 !important;
    border-radius: 6px !important;
    color: #1b5e20 !important;
    font-size: 13px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #004d20; }
::-webkit-scrollbar-thumb { background: #00c853; border-radius: 2px; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.viewerBadge_container__1QSob { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

/* ── CUSTOM ── */
.val-preview { color: #00c853; font-weight: 700; font-size: 16px; padding-top: 30px; }
.sec-label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px;
    color: #81c784; font-weight: 600; margin-bottom: 6px;
}
div[data-testid="stVerticalBlock"] label { color: #c8e6c9 !important; font-size: 12px !important; }
/* Card sections */
.card-section {
    background: #e8f5e9;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
    border: 1px solid #c8e6c9;
}
/* Page body padding */
.block-container { padding: 2rem 2rem 2rem !important; max-width: 1200px !important; }
</style>
""", unsafe_allow_html=True)

# ── DADOS ──────────────────────────────────────
USUARIOS = {
    "tamires": {"senha":"tamires123","equipe":"tamires","role":"admin",  "nome":"Tamires"},
    "luciano": {"senha":"luciano123","equipe":"luciano","role":"gestor", "nome":"Luciano"},
    "deborah": {"senha":"deborah123","equipe":"deborah","role":"gestor", "nome":"Déborah"},
    "veloso":  {"senha":"veloso123", "equipe":None,     "role":"diretor","nome":"Veloso"},
    "moyara":  {"senha":"moyara123", "equipe":None,     "role":"diretor","nome":"Moyara"},
}
EQUIPES = {
    "luciano":{"nome":"Luciano","emoji":"","cor":"#2daf5c"},
    "deborah":{"nome":"Déborah","emoji":"","cor":"#a855f7"},
    "tamires":{"nome":"Tamires","emoji":"","cor":"#f97316"},
    "metcool":{"nome":"MetCool","emoji":"","cor":"#3b82f6"},
}
MESES_NOMES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

CRITERIOS = [
    {"id":"c1","num":"1º","nome":"Abertura e Identificação","peso":5,
     "itens":["Saudação adequada","Identificação do operador e da empresa","Sem conversas paralelas fora do mudo"],"obrigatorio":False},
    {"id":"c2","num":"2º","nome":"Comunicação e Postura","peso":5,
     "itens":["Clareza na fala e respeito com o cliente","Tom respeitoso, sem ironia ou pressão","Escuta ativa — não interromper"],"obrigatorio":False},
    {"id":"c3","num":"3º","nome":"Diagnóstico da Dívida","peso":10,
     "itens":["Questionar o motivo da inadimplência","Recorda do contrato? Recebeu boleto? Tem acesso ao app? Previsão de pagamento?"],"obrigatorio":False},
    {"id":"c4","num":"4º","nome":"Negociação","peso":40,
     "itens":["Argumentação de benefícios do pagamento pontual","! Obrigatório: perguntar sobre dúvidas em boletos","! Obrigatório: perguntar sobre acesso ao app","! Obrigatório: falar sobre iGreen Club (mín. 2)"],"obrigatorio":True},
    {"id":"c5","num":"5º","nome":"Conformidade","peso":20,
     "itens":["Questionar o motivo do cancelamento","Não ameaçar ou constranger"],"obrigatorio":False},
    {"id":"c6","num":"6º","nome":"Registros e Procedimentos","peso":10,
     "itens":["Registro correto no sistema","Classificação adequada da ligação"],"obrigatorio":False},
    {"id":"c7","num":"7º","nome":"Encerramento","peso":10,
     "itens":["Esclarecimento do acordo fechado","Agradecimento e cordialidade"],"obrigatorio":False},
]

ERROS_CRITICOS = [
    {"id":"e1","nome":"Informação incorreta","desc":"Passou informação incorreta, incompleta ou errada ao cliente"},
    {"id":"e2","nome":"Postura ríspida","desc":"Agiu de forma ríspida ou ameaçadora"},
    {"id":"e3","nome":"Linguagem agressiva","desc":"Usar linguajar agressivo com o cliente"},
    {"id":"e4","nome":"Retenção de ligação","desc":"Segurar a ligação até dar o tempo legível para cota"},
    {"id":"e5","nome":"Contra-argumentação indevida","desc":"Cliente reclama do desconto e você oferta conta única"},
]

FAIXAS_PONTOS = [
    (0,   60,  0),
    (61,  70,  300),
    (71,  80,  500),
    (81,  90,  700),
    (91,  99,  1000),
    (100, 100, 1100),
]

OPERADORES_PADRAO = {
    "luciano": [
        ("Jennifer Silveira",True),("Paulo Roberto",False),("Samires Barros",False),
        ("Maycow Gabriel",False),("Otaides Junior",False),("Heverton Tavares",False),
        ("Camila Nara",False),("Caua Alves",False),("Eduarda Sanqueta",False),
        ("Jheniffer Santos",False),("Ketie Silva",False),("Emanuel Cardoso",False),
        ("Victória Silva",False),("Grasielli Santos",False),("Laura Silva",False),
        ("Michelle Batista",False),("Lorenzzo Pereira",False),("Diogo Oliveira",False),
        ("Maria Paulino",False),("Gabrielle Martins",False),("Marcos Martins",False),
    ],
    "deborah": [
        ("Mikael Dias",False),("Amanda Eduarda",False),("Larissa Barcelos",False),
        ("Nicole Amaral",False),("Sara Rocha",False),("Isabelly Araujo",False),("Silye Paula",False),
    ],
    "tamires": [
        ("Danilo Rodrigues",True),("Raiane Pereira",False),("Wynara Dos Reis",False),
        ("Esteffany Souza",False),("André Gomes",False),("Wanessa Cardoso",False),
        ("Larisse Garcia",False),("Arthur Alves",False),
    ],
    "metcool": [],
}

# ── MONGODB ────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
    return client[st.secrets["mongo"]["db"]]

def buscar_operadores(equipe_id):
    return list(get_db().operadores.find({"equipeId":equipe_id}).sort("nome",1))

def salvar_operador(equipe_id, nome, pleno=False):
    import uuid
    op_id = str(uuid.uuid4())[:12].replace("-","")
    get_db().operadores.insert_one({"_id":op_id,"equipeId":equipe_id,"nome":nome,"pleno":pleno,"criadoEm":datetime.now()})
    return op_id

def excluir_operador(op_id):
    get_db().operadores.delete_one({"_id":op_id})

def atualizar_operador(op_id, nome, pleno):
    get_db().operadores.update_one({"_id":op_id},{"$set":{"nome":nome,"pleno":pleno}})

def salvar_meta_operador(mes_ano, equipe_id, op_id, valor):
    doc_id = f"meta_op__{mes_ano}__{equipe_id}__{op_id}"
    get_db().metas.update_one({"_id":doc_id},{"$set":{"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,"opId":op_id,"valor":valor}},upsert=True)

def buscar_metas_equipe(mes_ano, equipe_id):
    docs = list(get_db().metas.find({"mesAno":mes_ano,"equipeId":equipe_id}))
    return {d["opId"]:d.get("valor",0) for d in docs if "opId" in d}

def salvar_meta_gestora(mes_ano, equipe_id, meta, target_pct):
    doc_id = f"meta_gest__{mes_ano}__{equipe_id}"
    get_db().metas.update_one({"_id":doc_id},{"$set":{"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,"metaGestora":meta,"targetPct":target_pct,"tipo":"gestora"}},upsert=True)

def buscar_meta_gestora(mes_ano, equipe_id):
    doc_id = f"meta_gest__{mes_ano}__{equipe_id}"
    return get_db().metas.find_one({"_id":doc_id}) or {"metaGestora":0,"targetPct":125}

def criar_lancamento(mes_ano, equipe_id, data_ref, label, agentes_data, total, vg, sem_int, dt, td):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    doc_id = f"lanc__{mes_ano}__{equipe_id}__{ts}"
    get_db().lancamentos.insert_one({"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,"dataRef":data_ref,"label":label,"agentes":agentes_data,"totalEquipe":total,"valorGeral":vg,"semInteracao":sem_int,"diasTrabalhados":dt,"totalDias":td,"criadoEm":datetime.now()})
    return doc_id

def buscar_lancamentos(mes_ano, equipe_id):
    # Busca na coleção nova (lancamentos)
    novos = list(get_db().lancamentos.find({"mesAno":mes_ano,"equipeId":equipe_id}).sort("criadoEm",-1))
    
    # Busca também na coleção antiga (resultados) para não perder dados anteriores
    antigos_raw = list(get_db().resultados.find({"mesAno":mes_ano,"equipeId":equipe_id}))
    antigos = []
    for d in antigos_raw:
        # Converte formato antigo para novo
        antigos.append({
            "_id": d["_id"],
            "mesAno": d["mesAno"],
            "equipeId": d["equipeId"],
            "label": d.get("semanaId", "Registro anterior"),
            "dataRef": d.get("atualizadoEm",""),
            "agentes": d.get("agentes",{}),
            "totalEquipe": d.get("totalEquipe",0),
            "valorGeral": d.get("valorGeral",0),
            "semInteracao": d.get("semInteracao",0),
            "diasTrabalhados": d.get("diasTrabalhados",0),
            "totalDias": d.get("totalDias",22),
            "criadoEm": d.get("atualizadoEm", datetime.now()),
        })
    
    todos = novos + antigos
    todos.sort(key=lambda x: x.get("criadoEm", datetime.now()), reverse=True)
    return todos

def buscar_lancamentos_mes_todas(mes_ano):
    return list(get_db().lancamentos.find({"mesAno":mes_ano}).sort("criadoEm",-1))

def excluir_lancamento(doc_id):
    get_db().lancamentos.delete_one({"_id":doc_id})

def salvar_monitoria(equipe_id, op_id, op_nome, protocolo, obs, criterios_resultado, erros_criticos_marcados, nota, mes_ano):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    doc_id = f"mon__{equipe_id}__{op_id}__{ts}"
    get_db().monitorias.insert_one({
        "_id":doc_id,"equipeId":equipe_id,"opId":op_id,"opNome":op_nome,
        "protocolo":protocolo,"observacao":obs,
        "criterios":criterios_resultado,"errosCriticos":erros_criticos_marcados,
        "nota":nota,"mesAno":mes_ano,"criadoEm":datetime.now()
    })
    return doc_id

def buscar_monitorias_operador(op_id):
    return list(get_db().monitorias.find({"opId":op_id}).sort("criadoEm",-1))

def buscar_monitorias_equipe(equipe_id, mes_ano=None):
    # Nunca apaga — sempre busca tudo, filtra só se necessário
    filtro = {"equipeId": equipe_id}
    if mes_ano:
        filtro["mesAno"] = mes_ano
    return list(get_db().monitorias.find(filtro).sort("criadoEm", -1))

def buscar_todas_monitorias(mes_ano=None):
    filtro = {"mesAno":mes_ano} if mes_ano else {}
    return list(get_db().monitorias.find(filtro).sort("criadoEm",-1))

def excluir_monitoria(doc_id):
    get_db().monitorias.delete_one({"_id":doc_id})

def salvar_processamento(mes_ano, equipe_id, df):
    doc_id = f"proc__{mes_ano}__{equipe_id}"
    get_db().processamentos.update_one({"_id":doc_id},{"$set":{"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,"registros":df.to_dict("records"),"atualizadoEm":datetime.now()}},upsert=True)

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
    return pd.concat(frames,ignore_index=True) if frames else pd.DataFrame()

def listar_meses_processados():
    return sorted(get_db().processamentos.distinct("mesAno"),reverse=True)

def listar_meses_monitorias(equipe_id):
    return sorted(get_db().monitorias.distinct("mesAno", {"equipeId": equipe_id}), reverse=True)

# ── HELPERS ────────────────────────────────────
def fmt_brl(v):
    if v is None or v == "": return "R$ 0,00"
    try: return "R$ "+f"{float(v):_.2f}".replace(".",",").replace("_",".")
    except: return "R$ 0,00"

def parse_brl(s):
    if not s: return 0.0
    try: return float(str(s).replace("R$","").replace(".","").replace(",",".").strip())
    except: return 0.0

def fmt_input(v):
    if not v or float(v)==0: return ""
    return f"{float(v):_.2f}".replace(".",",").replace("_",".")

def calc_projecao(valor,dias_trab,total_dias):
    if not dias_trab or dias_trab<=0: return 0
    return (valor/dias_trab)*total_dias

def calc_variacao(atual,anterior):
    if not anterior or anterior==0: return None
    return ((atual-anterior)/anterior)*100

def cor_pct(pct):
    if pct>=80: return "#2daf5c"
    if pct>=50: return "#f0a500"
    return "#e03c3c"

def status_pct(pct):
    if pct>=80: return "OK"
    if pct>=50: return "Regular"
    return "Baixo"

def calc_pontos(media):
    for lo,hi,pts in FAIXAS_PONTOS:
        if lo<=media<=hi: return pts
    return 0

def calc_media_operador(op_id, mes_ano=None):
    monts = buscar_monitorias_operador(op_id)
    if mes_ano:
        monts = [m for m in monts if m.get("mesAno") == mes_ano]
    if not monts: return 0, 0
    notas = [m["nota"] for m in monts if "nota" in m]
    if not notas: return 0, 0
    return round(sum(notas)/len(notas),1), len(notas)

def get_meses_disponiveis():
    hoje = datetime.now(); meses=[]
    for i in range(6):
        m=hoje.month-i; a=hoje.year
        if m<=0: m+=12; a-=1
        meses.append(f"{MESES_NOMES[m-1]}-{a}")
    return meses

def get_todos_meses_ano(ano=None):
    if not ano: ano=datetime.now().year
    return [f"{m}-{ano}" for m in MESES_NOMES]

def get_anos_disponiveis():
    hoje=datetime.now()
    return [str(hoje.year),str(hoje.year-1)]

def aging_faixa(dias):
    if pd.isna(dias): return "ND"
    if dias<=30: return "D0-30"
    if dias<=60: return "D31-60"
    if dias<=90: return "D61-90"
    return "D90+"

def header_page(titulo,sub=""):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#003318,#004d20);border:1px solid #005a25;
                border-radius:12px;padding:22px 28px;margin-bottom:24px;
                border-left:4px solid #00c853;box-shadow:0 4px 20px rgba(0,0,0,0.2)">
        <h1 style="margin:0;color:#ffffff;font-size:20px;font-weight:700">{titulo}</h1>
        {"<p style='color:#81c784;margin:4px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px'>"+sub+"</p>" if sub else ""}
    </div>
    """,unsafe_allow_html=True)

def val_input(label, key, placeholder="0"):
    """Campo numérico com preview R$ em tempo real"""
    c1,c2 = st.columns([2,1])
    with c1:
        v = st.number_input(label, min_value=0.0, step=100.0, format="%.2f", key=key, value=0.0)
    with c2:
        st.markdown(f"<div class='val-preview'>{fmt_brl(v)}</div>", unsafe_allow_html=True)
    return v

def seletor_equipe(default=None):
    u = st.session_state.usuario
    if u["role"] == "admin":
        eq_opts   = list(EQUIPES.keys())
        eq_labels = [f"{EQUIPES[e]['emoji']} Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        default_idx = eq_opts.index(default) if default and default in eq_opts else 0
        sel = st.selectbox("Gerenciando equipe:", eq_labels, index=default_idx, key="admin_eq_sel")
        return eq_opts[eq_labels.index(sel)]
    return u["equipe"]

# ── PROCESSAMENTO BASES ────────────────────────
def processar_bases(pagos_file, chat_file, lig_file, disp_file, equipe_id, mes_ano):
    def ler(f):
        if f is None: return None
        try: return pd.read_csv(f,header=0) if f.name.endswith(".csv") else pd.read_excel(f,header=0)
        except: return None

    df_pagos = ler(pagos_file)
    if df_pagos is None or df_pagos.empty: return None,["Arquivo PAGOS inválido!"]

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
            df_pagos[col] = pd.to_datetime(df_pagos[col],dayfirst=True,errors="coerce")

    if "valor" in df_pagos.columns:
        df_pagos["valor"] = pd.to_numeric(df_pagos["valor"].astype(str).str.replace("R$","").str.replace(".","").str.replace(",",".").str.strip(),errors="coerce").fillna(0)

    df_pagos["uc_cpf"] = df_pagos["uc_cpf"].astype(str).str.strip()

    contatos = []
    for arq,nome in [(chat_file,"CHAT"),(lig_file,"LIGACOES"),(disp_file,"DISPAROS")]:
        df = ler(arq)
        if df is not None and len(df.columns)>=2:
            dc = pd.DataFrame()
            dc["uc_cpf"]       = df.iloc[:,0].astype(str).str.strip()
            dc["data_contato"] = pd.to_datetime(df.iloc[:,1],dayfirst=True,errors="coerce")
            contatos.append(dc)

    primeiro_contato = pd.DataFrame()
    if contatos:
        df_todos = pd.concat(contatos,ignore_index=True).dropna(subset=["data_contato"])
        primeiro_contato = df_todos.groupby("uc_cpf")["data_contato"].min().reset_index().rename(columns={"data_contato":"primeiro_contato"})

    df_res = df_pagos.merge(primeiro_contato,on="uc_cpf",how="left") if not primeiro_contato.empty else df_pagos.copy()
    if "primeiro_contato" not in df_res.columns: df_res["primeiro_contato"] = pd.NaT

    df_res["diferenca_dias"] = (df_res["data_pagamento"]-df_res["primeiro_contato"]).dt.days

    def classif(row):
        if pd.isna(row["primeiro_contato"]): return "ND"
        if row["diferenca_dias"]>=0: return "Elegível"
        return "Não Elegível"

    df_res["elegibilidade"] = df_res.apply(classif,axis=1)
    df_res["dias_vencidos"]  = (df_res["data_pagamento"]-df_res["data_vencimento"]).dt.days
    df_res["aging"]          = df_res["dias_vencidos"].apply(aging_faixa)

    for col in ["data_vencimento","data_pagamento","primeiro_contato"]:
        if col in df_res.columns:
            df_res[col] = df_res[col].dt.strftime("%Y-%m-%d").where(df_res[col].notna(),other=None)

    df_res["equipe"]  = equipe_id
    df_res["mes_ano"] = mes_ano
    return df_res,[]

# ── PDF MONITORIA ──────────────────────────────
def gerar_pdf_monitoria(op_nome, protocolo, obs, criterios_resultado, erros_marcados, nota, media, n_monitorias, mes_ano):
    pontos = calc_pontos(media)
    linhas = []
    linhas.append(f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a1a1a;margin:0;padding:0}}
.header{{background:linear-gradient(135deg,#0a2414,#1a6b35);color:#fff;padding:32px 40px;}}
.logo{{font-size:24px;font-weight:800;color:#2daf5c;letter-spacing:2px}}
.subtitle{{font-size:13px;color:#5a9a70;margin-top:4px}}
.body{{padding:32px 40px}}
.info-row{{display:flex;gap:32px;margin-bottom:24px;background:#f8fdf9;border-radius:10px;padding:16px 20px;border-left:4px solid #2daf5c}}
.info-item .lbl{{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;font-weight:600}}
.info-item .val{{font-size:15px;font-weight:700;color:#0a2414;margin-top:2px}}
table{{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px}}
thead th{{background:#0a2414;color:#fff;padding:10px 14px;text-align:left;font-weight:600}}
tbody tr:nth-child(even){{background:#f0f9f3}}
tbody td{{padding:10px 14px;border-bottom:1px solid #e0ede5;vertical-align:top}}
.passou{{color:#1a6b35;font-weight:700}}.nao{{color:#c0392b;font-weight:700}}
.nota-box{{background:linear-gradient(135deg,#0a2414,#1a6b35);color:#fff;border-radius:12px;padding:24px 32px;text-align:center;margin-bottom:24px}}
.nota-num{{font-size:48px;font-weight:800;color:#2daf5c}}
.media-box{{background:#f0f9f3;border:1px solid #c3e6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px;display:flex;gap:32px}}
.critico{{background:#fdf0f0;border:1px solid #f5c6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px}}
.critico h4{{color:#c0392b;margin:0 0 8px 0}}
.obs-box{{background:#f8fdf9;border:1px solid #c3e6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px}}
.footer{{background:#f0f9f3;padding:16px 40px;text-align:center;font-size:11px;color:#5a9a70;border-top:2px solid #2daf5c}}
</style></head><body>
<div class='header'>
  <div class='logo'>🌿 iGREEN ENERGY</div>
  <div class='subtitle'>Relatório de Monitoria — Inadimplência Comercial</div>
</div>
<div class='body'>
<div class='info-row'>
  <div class='info-item'><div class='lbl'>Operador</div><div class='val'>{op_nome}</div></div>
  <div class='info-item'><div class='lbl'>Protocolo</div><div class='val'>{protocolo}</div></div>
  <div class='info-item'><div class='lbl'>Mês</div><div class='val'>{mes_ano.replace('-',' ')}</div></div>
  <div class='info-item'><div class='lbl'>Data</div><div class='val'>{datetime.now().strftime('%d/%m/%Y')}</div></div>
</div>""")

    if erros_marcados:
        linhas.append(f"<div class='critico'><h4>⚠ MONITORIA ZERADA — Erro Crítico</h4>")
        for e in erros_marcados:
            linhas.append(f"<div>• <strong>{e['nome']}</strong>: {e['desc']}</div>")
        linhas.append("</div>")

    linhas.append("""<table>
<thead><tr><th>#</th><th>Critério</th><th>Itens Avaliados</th><th>Peso</th><th>Resultado</th></tr></thead><tbody>""")

    for c in criterios_resultado:
        passou_txt = "<span class='passou'>✓ Passou</span>" if c["passou"] else "<span class='nao'>✗ Não passou</span>"
        itens_html = "<br>".join([f"• {i}" for i in c["itens"]])
        linhas.append(f"<tr><td>{c['num']}</td><td><strong>{c['nome']}</strong></td><td>{itens_html}</td><td style='text-align:center;font-weight:700;color:#{'1a6b35' if c['peso']>=20 else '0a2414'}'>{c['peso']}</td><td>{passou_txt}</td></tr>")

    linhas.append("</tbody></table>")

    linhas.append(f"""
<div class='nota-box'>
  <div style='font-size:13px;color:#5a9a70;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Nota desta Monitoria</div>
  <div class='nota-num'>{nota:.0f}%</div>
</div>
<div class='media-box'>
  <div><div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70'>Média Geral ({n_monitorias} monitorias)</div>
       <div style='font-size:24px;font-weight:800;color:#0a2414'>{media:.1f}%</div></div>
  <div><div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70'>Pontuação Atual</div>
       <div style='font-size:24px;font-weight:800;color:#1a6b35'>{pontos} pts</div></div>
  <div><div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70'>Faixa</div>
       <div style='font-size:18px;font-weight:700;color:#0a2414'>{'Abaixo 61%' if media<61 else '61-70%' if media<=70 else '71-80%' if media<=80 else '81-90%' if media<=90 else '91-99%' if media<=99 else '100%'}</div></div>
</div>""")

    if obs:
        linhas.append(f"<div class='obs-box'><strong>📝 Observações:</strong><br>{obs}</div>")

    linhas.append(f"""</div>
<div class='footer'>iGreen Energy · Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} · Inadimplência Comercial</div>
</body></html>""")

    return "".join(linhas)

# ── LOGIN ──────────────────────────────────────
def tela_login():
    c1,c2,c3 = st.columns([1,1.2,1])
    with c2:
        st.markdown("""
        <div style="background:#003318;border-radius:16px;padding:40px 32px;box-shadow:0 8px 32px rgba(0,0,0,0.3);border:1px solid #005a25">
        <div style="text-align:center;padding:0 0 28px">
            <div style="width:64px;height:64px;background:linear-gradient(135deg,#1a6b35,#2daf5c);
                    border-radius:16px;display:inline-flex;align-items:center;justify-content:center;
                    font-weight:900;font-size:32px;color:white;margin-bottom:14px;
                    box-shadow:0 4px 16px rgba(0,0,0,0.3)">G</div>
            <div style="font-size:24px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;margin-bottom:4px">
                iGreen Performance
            </div>
            <div style="width:36px;height:2px;background:#00c853;margin:6px auto 10px"></div>
            <p style="color:#5a9a70;font-size:11px;text-transform:uppercase;letter-spacing:2px;margin:0">
                Painel de Gestão de Inadimplência
            </p>
        </div>
        """,unsafe_allow_html=True)
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px'>E-MAIL</p>",unsafe_allow_html=True)
        usuario = st.text_input("usuario_input", placeholder="seu@email.com", label_visibility="collapsed")
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px;margin-top:12px'>SENHA</p>",unsafe_allow_html=True)
        senha   = st.text_input("senha_input", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if st.button("Entrar",use_container_width=True):
            u = USUARIOS.get(usuario.lower().strip())
            if u and u["senha"]==senha.strip():
                st.session_state.usuario={"id":usuario.lower(),**u}; st.rerun()
            else: st.error("Usuário ou senha incorretos.")
        st.markdown('<p style="text-align:center;color:#1a4d2e;font-size:11px;margin-top:24px">iGreen Energy © 2026</p>',unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────
def render_sidebar():
    u = st.session_state.usuario
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
                <div style="width:38px;height:38px;background:linear-gradient(135deg,#1a6b35,#2daf5c);
                            border-radius:10px;display:flex;align-items:center;justify-content:center;
                            font-weight:900;font-size:20px;color:white;letter-spacing:-1px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.3)">G</div>
                <div>
                <div style="color:#ffffff;font-weight:700;font-size:14px">i<span style='color:#2daf5c'>Green</span></div>
                <div style="color:#5a9a70;font-size:10px;text-transform:uppercase;letter-spacing:1px">Performance</div>
            </div>
            </div>
            <div style="background:rgba(0,200,83,0.1);border:1px solid rgba(0,200,83,0.2);
                        border-radius:8px;padding:10px 12px;margin-bottom:16px">
                <div style="color:#00c853;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px">
                    {'Diretoria' if u['role']=='diretor' else 'Admin' if u['role']=='admin' else 'Gestor'}
                </div>
                <div style="color:#ffffff;font-size:14px;font-weight:600;margin-top:2px">{u['nome']}</div>
            </div>
        </div><hr>
        """,unsafe_allow_html=True)

        st.markdown("<p style='font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#5a9a70;margin-bottom:4px'>PERÍODO</p>", unsafe_allow_html=True)
        anos  = get_anos_disponiveis()
        ano   = st.selectbox("Ano",anos,label_visibility="collapsed")
        meses = get_todos_meses_ano(int(ano))
        mes_labels = [m.split("-")[0] for m in meses]
        mes_idx    = datetime.now().month-1
        mes_sel    = st.selectbox("Mês",mes_labels,index=mes_idx,label_visibility="collapsed")
        mes_ano    = f"{mes_sel}-{ano}"

        st.markdown("<hr>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#5a9a70;margin-bottom:4px'>NAVEGAÇÃO</p>", unsafe_allow_html=True)

        if u["role"]=="diretor":
            pags=["Quadro de Resultados","Dashboard Executivo","Análise de Projeção","Monitorias","Histórico"]
        elif u["role"]=="admin":
            pags=["Quadro de Resultados","Lançamento","Dashboard Executivo","Análise de Projeção","Monitorias","Upload de Bases","Histórico","Operadores","Metas"]
        else:
            pags=["Quadro de Resultados","Lançamento","Análise de Projeção","Monitorias","Upload de Bases","Histórico","Operadores","Metas"]

        pag = st.radio("",pags,label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)
        if st.button("Sair",use_container_width=True):
            del st.session_state.usuario; st.rerun()

    return mes_ano, pag

# ── OPERADORES ─────────────────────────────────
def pagina_operadores():
    u = st.session_state.usuario
    header_page("Operadores","Gerencie os operadores da equipe")
    equipe_id = seletor_equipe(u["equipe"])
    eq = EQUIPES[equipe_id]

    with st.expander("Cadastrar Novo Operador",expanded=False):
        c1,c2,c3 = st.columns([3,1,1])
        with c1: novo_nome = st.text_input("Nome",placeholder="Nome completo")
        with c2: novo_pleno = st.checkbox("Pleno")
        with c3:
            st.markdown("<div style='margin-top:28px'>",unsafe_allow_html=True)
            if st.button("Cadastrar",use_container_width=True):
                if novo_nome.strip():
                    salvar_operador(equipe_id,novo_nome.strip(),novo_pleno)
                    st.success(f"✅ {novo_nome} cadastrado!"); st.rerun()
                else: st.error("Digite o nome.")
            st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("---")
    ops = buscar_operadores(equipe_id)

    if not ops:
        st.info("Nenhum operador cadastrado.")
        padrao = OPERADORES_PADRAO.get(equipe_id,[])
        if padrao:
            if st.button("Importar Operadores Padrão",use_container_width=True):
                for nome,pleno in padrao:
                    salvar_operador(equipe_id,nome,pleno)
                st.success(f"✅ {len(padrao)} operadores importados!"); st.rerun()
        return

    st.markdown(f"**{len(ops)} operadores — {eq['emoji']} Equipe {eq['nome']}**")
    for op in ops:
        c1,c2,c3,c4 = st.columns([3,1,1,1])
        with c1: nn = st.text_input("n",value=op["nome"],label_visibility="collapsed",key=f"n_{op['_id']}")
        with c2: np_ = st.checkbox("Pleno",value=op.get("pleno",False),key=f"p_{op['_id']}")
        with c3:
            if st.button("Salvar",key=f"s_{op['_id']}",help="Salvar"):
                atualizar_operador(op["_id"],nn,np_); st.success("Salvo!"); st.rerun()
        with c4:
            if st.button("Excluir",key=f"d_{op['_id']}",help="Excluir"):
                excluir_operador(op["_id"]); st.warning(f"{op['nome']} removido."); st.rerun()

# ── METAS ──────────────────────────────────────
def pagina_metas(mes_ano):
    u = st.session_state.usuario
    header_page("Metas",mes_ano.replace("-"," "))
    equipe_id = seletor_equipe(u["equipe"])
    eq = EQUIPES[equipe_id]
    ops = buscar_operadores(equipe_id)

    if not ops:
        st.warning("Cadastre operadores primeiro."); return

    st.markdown("### Meta da Gestora")
    meta_gest_doc = buscar_meta_gestora(mes_ano,equipe_id)
    c1,c2,c3 = st.columns([2,1,1])
    with c1:
        mg_val = st.number_input("Meta Base do Mês (R$)",min_value=0.0,step=1000.0,format="%.2f",
            value=float(meta_gest_doc.get("metaGestora",0)),key="meta_gest_val")
    with c2:
        target_pct = st.number_input("Target (%)",min_value=100,max_value=200,
            value=int(meta_gest_doc.get("targetPct",125)),key="target_pct")
    with c3:
        target_val = mg_val*(target_pct/100)
        st.markdown(f"<div style='padding-top:28px;color:#2daf5c;font-weight:700;font-size:16px'>{fmt_brl(target_val)}</div>",unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Metas por Operador")
    metas_salvas = buscar_metas_equipe(mes_ano,equipe_id)
    metas_novas  = {}

    c1,c2 = st.columns([3,2])
    c1.markdown("**Operador**"); c2.markdown("**Meta Mensal (R$)**")

    for op in ops:
        meta_salva = float(metas_salvas.get(op["_id"],0))
        c1,c2 = st.columns([3,2])
        with c1:
            st.markdown(f"<div style='padding-top:10px;color:#e0f0e8'>{'[P] ' if op.get('pleno') else ''}{op['nome']}</div>",unsafe_allow_html=True)
        with c2:
            v = st.number_input("m",label_visibility="collapsed",min_value=0.0,step=100.0,
                format="%.2f",value=meta_salva,key=f"mg_{mes_ano}_{op['_id']}")
            metas_novas[op["_id"]] = v

    st.markdown("---")
    if st.button("Salvar Metas",use_container_width=True):
        for op_id,val in metas_novas.items():
            salvar_meta_operador(mes_ano,equipe_id,op_id,val)
        salvar_meta_gestora(mes_ano,equipe_id,mg_val,target_pct)
        st.success("✅ Metas salvas!"); st.rerun()

# ── LANÇAMENTO ─────────────────────────────────
def pagina_lancamento(mes_ano):
    u = st.session_state.usuario
    header_page("Lançamento de Resultado",mes_ano.replace("-"," "))
    equipe_id = seletor_equipe(u["equipe"])
    eq = EQUIPES[equipe_id]
    ops = buscar_operadores(equipe_id)

    if not ops:
        st.warning("⚠ Cadastre operadores primeiro em 👥 Operadores."); return

    metas_salvas  = buscar_metas_equipe(mes_ano,equipe_id)
    meta_gest_doc = buscar_meta_gestora(mes_ano,equipe_id)

    st.markdown("### Configuração do Lançamento")
    c1,c2,c3 = st.columns([2,1,1])
    with c1:
        hoje = date.today()
        data_sel = st.date_input("Data do Resultado",value=hoje,
                                  min_value=date(hoje.year,1,1),max_value=date(hoje.year,12,31))
        eh_fechamento = st.checkbox("Fechamento do Mês")
        label = "Fechamento do Mês" if eh_fechamento else data_sel.strftime("%d/%m/%Y")
    with c2:
        dt = st.number_input("Dias Trabalhados",min_value=0,max_value=31,value=0)
    with c3:
        td = st.number_input("Total de Dias no Mês",min_value=1,max_value=31,value=22)

    st.markdown("---")
    # Valor Geral
    c1,c2 = st.columns([2,1])
    with c1:
        vg = st.number_input("Valor Total Geral Recebido (R$)",min_value=0.0,step=100.0,format="%.2f",key="vg_lanc")
    with c2:
        st.markdown(f"<div class='val-preview'>{fmt_brl(vg)}</div>",unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Valores por Operador")

    c1,c2,c3,c4,c5 = st.columns([3,2,2,2,2])
    c1.markdown("**Operador**"); c2.markdown("**Meta**")
    c3.markdown("**Valor Recebido (R$)**"); c4.markdown("**Projeção**"); c5.markdown("**% Meta**")

    vi = {}
    for op in ops:
        meta = float(metas_salvas.get(op["_id"],0))
        c1,c2,c3,c4,c5 = st.columns([3,2,2,2,2])
        with c1: st.markdown(f"<div style='padding-top:10px;color:#e0f0e8;font-weight:500'>{'[P] ' if op.get('pleno') else ''}{op['nome']}</div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div style='padding-top:10px;color:#5a9a70'>{fmt_brl(meta) if meta>0 else '—'}</div>",unsafe_allow_html=True)
        with c3:
            val = st.number_input("v",label_visibility="collapsed",min_value=0.0,step=100.0,format="%.2f",key=f"vl_{equipe_id}_{op['_id']}")
        proj = calc_projecao(val,dt,td)
        pct  = (val/meta*100) if meta>0 else 0
        with c4: st.markdown(f"<div style='padding-top:10px;color:#5a9a70'>{fmt_brl(proj) if proj>0 else '—'}</div>",unsafe_allow_html=True)
        with c5: st.markdown(f"<div style='padding-top:10px;color:{cor_pct(pct)};font-weight:700'>{status_pct(pct) if meta>0 else '⚪'} {f'{pct:.1f}%' if meta>0 else '—'}</div>",unsafe_allow_html=True)
        vi[op["_id"]] = val

    tc  = sum(vi.values())
    sem = max(0,vg-tc)
    mg  = float(meta_gest_doc.get("metaGestora",0))
    pct_gest = (tc/mg*100) if mg>0 else 0

    st.markdown("---")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Com Interação",fmt_brl(tc))
    c2.metric("Sem Interação",fmt_brl(sem))
    c3.metric("Total Geral",  fmt_brl(vg))
    c4.metric("Projeção",     fmt_brl(calc_projecao(tc,dt,td)))
    c5.metric(f"Meta ({pct_gest:.1f}%)",fmt_brl(mg))

    st.markdown("---")
    col_btn1, col_btn2 = st.columns([1,3])
    with col_btn1:
        salvar = st.button("Salvar Lançamento", use_container_width=True)
    with col_btn2:
        if "ultimo_salvo" in st.session_state:
            st.success(f"✅ {st.session_state.ultimo_salvo}")

    if salvar:
        if not any(v>0 for v in vi.values()):
            st.warning("Preencha pelo menos um valor.")
        else:
            agentes_data = {op["_id"]:{"valorRecebido":vi[op["_id"]],"nome":op["nome"]} for op in ops}
            criar_lancamento(mes_ano,equipe_id,str(data_sel),label,agentes_data,tc,vg,sem,dt,td)
            st.session_state.ultimo_salvo = f"Lançamento de {label} salvo com sucesso!"
            st.rerun()

# ── QUADRO DE RESULTADOS ───────────────────────
def pagina_quadro(mes_ano):
    u = st.session_state.usuario
    is_dir = u["role"] in ["diretor"]
    is_admin = u["role"] == "admin"
    equipes_ver = list(EQUIPES.keys()) if (is_dir or is_admin) else [u["equipe"]]

    header_page("Quadro de Resultados",mes_ano.replace("-"," "))

    for equipe_id in equipes_ver:
        eq  = EQUIPES[equipe_id]
        ops = buscar_operadores(equipe_id)
        lancs = buscar_lancamentos(mes_ano,equipe_id)
        if not lancs: continue

        ultimo = lancs[0]
        meta_gest_doc = buscar_meta_gestora(mes_ano,equipe_id)
        metas_ops     = buscar_metas_equipe(mes_ano,equipe_id)
        mg       = float(meta_gest_doc.get("metaGestora",0))
        tpct     = int(meta_gest_doc.get("targetPct",125))
        # RECEBIDO = valor geral informado pela gestora (não soma dos operadores)
        vg_geral = float(ultimo.get("valorGeral",0))
        tc_ops   = float(ultimo.get("totalEquipe",0))  # soma dos operadores
        dt       = int(ultimo.get("diasTrabalhados",0))
        td       = int(ultimo.get("totalDias",22))
        proj     = calc_projecao(vg_geral,dt,td)
        pct_mg   = (vg_geral/mg*100) if mg>0 else 0
        target_v = mg*(tpct/100)
        pct_tg   = (vg_geral/target_v*100) if target_v>0 else 0

        sem_int = max(0, vg_geral - tc_ops)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;
                    border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid #00c853;box-shadow:0 2px 12px rgba(0,0,0,0.15)">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <div style="font-size:16px;font-weight:700;color:#ffffff">Equipe {eq['nome']} · {ultimo.get('label','')}</div>
                <div style="text-align:center">
                    <div style="color:#5a9a70;font-size:10px;text-transform:uppercase">% Meta</div>
                    <div style="color:{cor_pct(pct_mg)};font-size:22px;font-weight:800">{pct_mg:.1f}%</div>
                </div>
            </div>
            <div style="display:flex;gap:24px;margin-top:12px;flex-wrap:wrap">
                <div><span style="color:#5a9a70;font-size:11px">RECEBIDO GERAL</span><br><span style="color:#2daf5c;font-weight:700;font-size:15px">{fmt_brl(vg_geral)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">COM INTERAÇÃO</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(tc_ops)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">SEM INTERAÇÃO</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(sem_int)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">META</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(mg)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(proj)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">DIAS</span><br><span style="color:#e0f0e8;font-weight:600">{dt}/{td}</span></div>
            </div>
        </div>
        """,unsafe_allow_html=True)

        if ops:
            rows = []
            for op in ops:
                val  = float(ultimo.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0))
                meta = float(metas_ops.get(op["_id"],0))
                proj_op = calc_projecao(val,dt,td)
                pct  = (val/meta*100) if meta>0 else 0
                pleno_label = " ★" if op.get("pleno") else ""
            rows.append({"Status":status_pct(pct) if meta>0 else "—","Operador":op["nome"]+pleno_label,"Recebido":fmt_brl(val),"Meta":fmt_brl(meta) if meta>0 else "—","% Meta":f"{pct:.1f}%" if meta>0 else "—","Projeção":fmt_brl(proj_op) if proj_op>0 else "—","_v":val})
            df = pd.DataFrame(rows).sort_values("_v",ascending=False).drop(columns=["_v"]).reset_index(drop=True)
            df.index = range(1,len(df)+1)
            st.dataframe(df,use_container_width=True,height=min(600,(len(df)+1)*38+40))
        st.markdown("---")

    if st.button("Exportar Excel"):
        out = io.BytesIO()
        with pd.ExcelWriter(out,engine="xlsxwriter") as writer:
            for equipe_id in equipes_ver:
                ops = buscar_operadores(equipe_id)
                if not ops: continue
                lancs = buscar_lancamentos(mes_ano,equipe_id)
                if not lancs: continue
                ultimo = lancs[0]; metas_ops = buscar_metas_equipe(mes_ano,equipe_id)
                rows=[{"Operador":op["nome"],"Recebido":float(ultimo.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0)),"Meta":float(metas_ops.get(op["_id"],0))} for op in ops]
                pd.DataFrame(rows).to_excel(writer,sheet_name=f"{EQUIPES[equipe_id]['nome']}",index=False)
        st.download_button("⬇️ Baixar Excel",data=out.getvalue(),file_name=f"iGreen_{mes_ano}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── MONITORIAS ─────────────────────────────────
def pagina_monitorias(mes_ano):
    u = st.session_state.usuario
    is_dir = u["role"] == "diretor"

    header_page("Monitorias","Avaliação de qualidade · Inadimplência Comercial")

    if is_dir:
        pagina_monitorias_diretor(mes_ano)
        return

    equipe_id = seletor_equipe(u["equipe"])
    ops = buscar_operadores(equipe_id)

    t1,t2 = st.tabs(["Nova Monitoria","Histórico de Monitorias"])

    with t1:
        if not ops:
            st.warning("Cadastre operadores primeiro."); return

        st.markdown("### Operador e Protocolo")
        c1,c2 = st.columns([2,2])
        with c1:
            op_nomes = [op["nome"] for op in ops]
            op_sel   = st.selectbox("Operador",op_nomes)
            op_obj   = next(o for o in ops if o["nome"]==op_sel)
        with c2:
            protocolo = st.text_input("Protocolo da Ligação",placeholder="Ex: 20260520-001")

        obs = st.text_area("Observações",placeholder="Anotações sobre a monitoria...",height=80)

        st.markdown("---")
        st.markdown("### Erros Críticos — Zera a Monitoria")
        erros_marcados = []
        c1,c2 = st.columns(2)
        for i,ec in enumerate(ERROS_CRITICOS):
            with (c1 if i%2==0 else c2):
                if st.checkbox(f"🔴 {ec['nome']} — {ec['desc']}",key=f"ec_{ec['id']}"):
                    erros_marcados.append(ec)

        st.markdown("---")
        st.markdown("### Critérios de Avaliação")

        zerada = len(erros_marcados)>0
        criterios_resultado = []
        nota = 0 if zerada else 100

        if zerada:
            st.error("MONITORIA ZERADA — Erro crítico marcado!")
            for c in CRITERIOS:
                criterios_resultado.append({**c,"passou":False})
        else:
            for crit in CRITERIOS:
                cor_borda = "#f0a500" if crit["obrigatorio"] else "#1a4d2e"
                st.markdown(f"""
                <div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;
                            padding:14px 18px;margin-bottom:8px">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                        <span style="color:#1b5e20;font-weight:600">{crit['num']} {crit['nome']}</span>
                        <span style="background:{'rgba(240,165,0,0.2)' if crit['obrigatorio'] else 'rgba(45,175,92,0.1)'};
                               color:{'#f0a500' if crit['obrigatorio'] else '#2daf5c'};
                               padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">
                            Peso {crit['peso']} {'⚠️ Obrigatório' if crit['obrigatorio'] else ''}
                        </span>
                    </div>
                """,unsafe_allow_html=True)
                for item in crit["itens"]:
                    obrig_style = "color:#f0a500;font-weight:600" if "Obrigatório" in item else "color:#b8d4c0"
                    st.markdown(f"<div style='font-size:12px;{obrig_style};margin-left:8px'>• {item}</div>",unsafe_allow_html=True)
                passou = st.checkbox(f"✓ Critério passou",key=f"cr_{crit['id']}",value=True)
                st.markdown("</div>",unsafe_allow_html=True)
                if not passou:
                    nota -= crit["peso"]
                criterios_resultado.append({**crit,"passou":passou})

        nota = max(0,nota)

        st.markdown("---")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#003318,#004d20);border-radius:12px;
                    padding:20px 24px;text-align:center;margin-bottom:16px">
            <div style="color:#5a9a70;font-size:12px;text-transform:uppercase;letter-spacing:1px">Nota desta Monitoria</div>
            <div style="color:{'#2daf5c' if nota>=80 else '#f0a500' if nota>=60 else '#e03c3c'};
                         font-size:48px;font-weight:800;margin:8px 0">{nota:.0f}%</div>
        </div>
        """,unsafe_allow_html=True)

        if st.button("Salvar Monitoria",use_container_width=True):
            if not protocolo.strip():
                st.error("⚠ Preencha o protocolo da ligação!"); return
            doc_id = salvar_monitoria(equipe_id,op_obj["_id"],op_sel,protocolo,obs,criterios_resultado,erros_marcados,nota,mes_ano)
            media, n = calc_media_operador(op_obj["_id"], mes_ano)
            st.success(f"Monitoria salva! Nota: {nota:.0f}% | Média de {mes_ano.replace('-',' ')}: {media:.1f}% ({n} monitorias) | Pontos: {calc_pontos(media)}")

            media_mes, n_mes = calc_media_operador(op_obj["_id"], mes_ano)
            html = gerar_pdf_monitoria(op_sel,protocolo,obs,criterios_resultado,erros_marcados,nota,media_mes,n_mes,mes_ano)
            b64  = base64.b64encode(html.encode()).decode()
            st.markdown(f'<a href="data:text/html;base64,{b64}" download="Monitoria_{op_sel.replace(" ","_")}_{protocolo}.html" style="display:inline-block;background:linear-gradient(135deg,#1a6b35,#2daf5c);color:white;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:8px">📥 Baixar Relatório PDF</a>',unsafe_allow_html=True)

    with t2:
        meses_com_mon = listar_meses_monitorias(equipe_id)

        if not meses_com_mon:
            st.info("Nenhuma monitoria registrada ainda.")
        else:
            meses_sel = st.multiselect(
                "Filtrar por mês:",
                options=meses_com_mon,
                default=meses_com_mon[:1],
                key="mon_mes_filtro"
            )

            if not meses_sel:
                st.info("Selecione pelo menos um mês.")
            else:
                monts = []
                for ms in meses_sel:
                    monts += buscar_monitorias_equipe(equipe_id, ms)
                monts.sort(key=lambda x: str(x.get("mesAno","")) + str(x.get("criadoEm","")), reverse=True)

                if not monts:
                    st.info("Nenhuma monitoria nos meses selecionados.")
                else:
                    for mes_atual in meses_sel:
                        monts_mes = [m for m in monts if m.get("mesAno") == mes_atual]
                        if not monts_mes: continue

                        ops_unicos = list({m["opId"]: m["opNome"] for m in monts_mes}.items())
                        medias = [calc_media_operador(op_id, mes_atual)[0] for op_id,_ in ops_unicos]
                        media_equipe_mes = sum(medias)/len(medias) if medias else 0

                        # Cabeçalho do mês
                        st.markdown(f"""
                        <div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;
                                    padding:14px 20px;margin:16px 0 12px;
                                    display:flex;justify-content:space-between;align-items:center">
                            <div style="color:#1b5e20;font-weight:700;font-size:16px">{mes_atual.replace('-',' ')}</div>
                            <div style="text-align:right">
                                <div style="color:#2e7d32;font-size:10px;text-transform:uppercase;letter-spacing:1px">Média da Equipe</div>
                                <div style="color:#00c853;font-size:22px;font-weight:800">{media_equipe_mes:.1f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        for m in monts_mes:
                            media_op, n_op = calc_media_operador(m["opId"], mes_atual)
                            pontos_op = calc_pontos(media_op)
                            nota = float(m.get("nota", 0))
                            cor_nota = "#2e7d32" if nota >= 80 else "#f57f17" if nota >= 60 else "#c62828"
                            status_nota = "Aprovado" if nota >= 60 else "Reprovado"

                            # Card de cada monitoria
                            st.markdown(f"""
                            <div style="background:#ffffff;border:1px solid #c8e6c9;border-radius:10px;
                                        padding:16px 20px;margin-bottom:10px;
                                        border-left:4px solid {cor_nota}">
                                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
                                    <div>
                                        <div style="color:#1b5e20;font-weight:700;font-size:15px">{m['opNome']}</div>
                                        <div style="color:#555;font-size:12px;margin-top:2px">
                                            Protocolo: <strong>{m.get('protocolo','—')}</strong> &nbsp;·&nbsp;
                                            Data: <strong>{str(m.get('criadoEm',''))[:10]}</strong>
                                        </div>
                                    </div>
                                    <div style="display:flex;gap:20px;text-align:center">
                                        <div>
                                            <div style="font-size:10px;color:#666;text-transform:uppercase">Nota</div>
                                            <div style="font-size:20px;font-weight:800;color:{cor_nota}">{nota:.0f}%</div>
                                        </div>
                                        <div>
                                            <div style="font-size:10px;color:#666;text-transform:uppercase">Média {mes_atual.split('-')[0]}</div>
                                            <div style="font-size:20px;font-weight:800;color:#1b5e20">{media_op:.1f}%</div>
                                        </div>
                                        <div>
                                            <div style="font-size:10px;color:#666;text-transform:uppercase">Pontos</div>
                                            <div style="font-size:20px;font-weight:800;color:#2e7d32">{pontos_op}</div>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                            # Critérios
                            crits = m.get("criterios", [])
                            if crits:
                                st.markdown("""
                                <div style="margin-top:12px;border-top:1px solid #e0e0e0;padding-top:10px">
                                    <div style="font-size:11px;color:#666;text-transform:uppercase;
                                                letter-spacing:1px;margin-bottom:8px;font-weight:600">
                                        Critérios Avaliados
                                    </div>
                                """, unsafe_allow_html=True)
                                crit_html = ""
                                for c in crits:
                                    passou = c.get("passou", True)
                                    cor_c = "#2e7d32" if passou else "#c62828"
                                    bg_c  = "#f1f8f1" if passou else "#fff5f5"
                                    ic    = "✓" if passou else "✗"
                                    crit_html += (
                                        f"<div style='display:flex;justify-content:space-between;"
                                        f"padding:6px 12px;background:{bg_c};border-radius:6px;"
                                        f"margin-bottom:4px;border-left:3px solid {cor_c}'>"
                                        f"<span style='color:#333;font-size:13px'>{c.get('num','')} {c.get('nome','')}</span>"
                                        f"<span style='color:{cor_c};font-weight:700;font-size:13px'>{ic} {('Passou' if passou else 'Não passou')}</span></div>"
                                    )
                                st.markdown(crit_html + "</div>", unsafe_allow_html=True)

                            # Erros críticos
                            erros = m.get("errosCriticos", [])
                            if erros:
                                erros_html = "<div style='margin-top:8px'><div style='font-size:11px;color:#c62828;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;font-weight:600'>Erros Críticos</div>"
                                for e in erros:
                                    erros_html += (
                                        f"<div style='padding:6px 12px;background:#ffebee;"
                                        f"border-radius:6px;margin-bottom:4px;border-left:3px solid #e53935;"
                                        f"color:#c62828;font-size:13px'>"
                                        f"<strong>{e.get('nome','')}</strong> — {e.get('desc','')}</div>"
                                    )
                                st.markdown(erros_html + "</div>", unsafe_allow_html=True)

                            # Observação
                            if m.get("observacao"):
                                st.markdown(
                                    f"<div style='margin-top:8px;padding:8px 12px;background:#f9fbe7;"
                                    f"border-radius:6px;border-left:3px solid #c6e02b;"
                                    f"color:#555;font-size:13px'>"
                                    f"<strong>Observação:</strong> {m['observacao']}</div>",
                                    unsafe_allow_html=True
                                )

                            st.markdown("</div>", unsafe_allow_html=True)

                            # Botões PDF e Excluir
                            col_pdf, col_del, col_esp = st.columns([2,2,6])
                            html_pdf = gerar_pdf_monitoria(
                                m["opNome"], m.get("protocolo",""), m.get("observacao",""),
                                m.get("criterios",[]), m.get("errosCriticos",[]),
                                nota, media_op, n_op, mes_atual
                            )
                            b64 = base64.b64encode(html_pdf.encode()).decode()
                            with col_pdf:
                                st.markdown(
                                    f'<a href="data:text/html;base64,{b64}" '
                                    f'download="Monitoria_{m["opNome"].replace(" ","_")}_{m.get("protocolo","")}.html" '
                                    f'style="display:block;background:#00c853;color:white;text-align:center;'
                                    f'padding:8px 16px;border-radius:6px;text-decoration:none;'
                                    f'font-weight:600;font-size:13px">Baixar PDF</a>',
                                    unsafe_allow_html=True
                                )
                            with col_del:
                                if st.button("Excluir", key=f"del_{m['_id']}"):
                                    excluir_monitoria(m["_id"])
                                    st.warning("Monitoria excluída."); st.rerun()
                            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def pagina_monitorias_diretor(mes_ano):
    st.markdown("### Visão Geral — Monitorias por Equipe")
    equipes_ids = list(EQUIPES.keys())

    for equipe_id in equipes_ids:
        eq   = EQUIPES[equipe_id]
        ops  = buscar_operadores(equipe_id)
        if not ops: continue
        monts = buscar_monitorias_equipe(equipe_id,mes_ano)
        if not monts: continue

        medias_ops = {}
        for op in ops:
            media,n = calc_media_operador(op["_id"], mes_ano)  # média mensal
            if n>0: medias_ops[op["nome"]] = (media,n,calc_pontos(media))

        if not medias_ops: continue

        media_equipe = sum(m[0] for m in medias_ops.values())/len(medias_ops)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;
                    border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid #00c853;box-shadow:0 2px 12px rgba(0,0,0,0.15)">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="font-size:15px;font-weight:700;color:#ffffff">{eq['emoji']} Equipe {eq['nome']}</div>
                <div style="text-align:right">
                    <div style="color:#5a9a70;font-size:10px;text-transform:uppercase">Média da Equipe</div>
                    <div style="color:{cor_pct(media_equipe)};font-size:24px;font-weight:800">{media_equipe:.1f}%</div>
                </div>
            </div>
        </div>
        """,unsafe_allow_html=True)

        rows = [{"Operador":nome,"Média":f"{m[0]:.1f}%","Monitorias":m[1],"Pontos":m[2]} for nome,(m) in sorted(medias_ops.items(),key=lambda x:-x[1][0])]
        df = pd.DataFrame(rows)
        df.index = range(1,len(df)+1)
        st.dataframe(df,use_container_width=True)
        st.markdown("---")

# ── ANÁLISE DE PROJEÇÃO ────────────────────────
def pagina_analise_projecao(mes_ano):
    u = st.session_state.usuario
    is_dir  = u["role"] in ["diretor","admin"]
    equipes_ver = list(EQUIPES.keys()) if is_dir else [u["equipe"]]

    header_page("Análise de Projeção",f"Comparativo com mês anterior · {mes_ano.replace('-',' ')}")

    partes = mes_ano.split("-")
    mes_idx = MESES_NOMES.index(partes[0])
    ano_int = int(partes[1])
    mes_ant = f"{MESES_NOMES[11]}-{ano_int-1}" if mes_idx==0 else f"{MESES_NOMES[mes_idx-1]}-{ano_int}"

    st.markdown(f"<p style='color:#5a9a70'>Comparando <strong style='color:#2daf5c'>{mes_ano.replace('-',' ')}</strong> vs <strong style='color:#e0f0e8'>{mes_ant.replace('-',' ')}</strong></p>",unsafe_allow_html=True)
    st.markdown("---")

    for equipe_id in equipes_ver:
        eq  = EQUIPES[equipe_id]
        ops = buscar_operadores(equipe_id)
        if not ops: continue

        lancs_at = buscar_lancamentos(mes_ano,equipe_id)
        lancs_an = buscar_lancamentos(mes_ant, equipe_id)
        if not lancs_at: continue

        ul_at = lancs_at[0]; ul_an = lancs_an[0] if lancs_an else {}
        dt_at = int(ul_at.get("diasTrabalhados",0)); td_at = int(ul_at.get("totalDias",22))
        dt_an = int(ul_an.get("diasTrabalhados",0)) if ul_an else 0
        td_an = int(ul_an.get("totalDias",22))      if ul_an else 22
        tc_at = float(ul_at.get("totalEquipe",0));   tc_an = float(ul_an.get("totalEquipe",0)) if ul_an else 0
        proj_at = calc_projecao(tc_at,dt_at,td_at);  proj_an = calc_projecao(tc_an,dt_an,td_an) if tc_an>0 else 0
        var_eq  = calc_variacao(proj_at,proj_an)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;
                    border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid #00c853;box-shadow:0 2px 12px rgba(0,0,0,0.15)">
            <div style="font-size:15px;font-weight:700;color:#ffffff;margin-bottom:10px">{eq['emoji']} Equipe {eq['nome']}</div>
            <div style="display:flex;gap:24px;flex-wrap:wrap">
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO ATUAL</span><br>
                     <span style="color:#2daf5c;font-weight:700;font-size:15px">{fmt_brl(proj_at)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO MÊS ANT.</span><br>
                     <span style="color:#e0f0e8;font-weight:600">{fmt_brl(proj_an)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">VARIAÇÃO</span><br>
                     <span style="color:{'#2daf5c' if (var_eq or 0)>=0 else '#e03c3c'};font-weight:700">
                        {'↑' if (var_eq or 0)>=0 else '↓'} {f'{abs(var_eq):.1f}%' if var_eq is not None else '—'}
                     </span></div>
            </div>
        </div>
        """,unsafe_allow_html=True)

        rows = []
        for op in ops:
            val_at = float(ul_at.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0))
            val_an = float(ul_an.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0)) if ul_an else 0
            proj_op_at = calc_projecao(val_at,dt_at,td_at)
            proj_op_an = calc_projecao(val_an,dt_an,td_an) if val_an>0 else 0
            var_op = calc_variacao(proj_op_at,proj_op_an)
            rows.append({"Operador":("★ " if op.get("pleno") else "")+op["nome"],"Proj. Atual":fmt_brl(proj_op_at) if proj_op_at>0 else "—","Proj. Mês Ant.":fmt_brl(proj_op_an) if proj_op_an>0 else "—","Variação":f"{'↑' if (var_op or 0)>=0 else '↓'} {abs(var_op):.1f}%" if var_op is not None else "—","_p":proj_op_at})
        df = pd.DataFrame(rows).sort_values("_p",ascending=False).drop(columns=["_p"]).reset_index(drop=True)
        df.index = range(1,len(df)+1)
        st.dataframe(df,use_container_width=True)
        st.markdown("---")

# ── HISTÓRICO ──────────────────────────────────
def pagina_historico(mes_ano):
    u = st.session_state.usuario
    is_admin = u["role"] == "admin"
    equipe_id = seletor_equipe(u["equipe"]) if u["role"] in ["admin","gestor"] else u["equipe"]

    header_page("Histórico",mes_ano.replace("-"," "))

    t1,t2 = st.tabs(["Lançamentos","Bases Processadas"])

    with t1:
        if not equipe_id: st.info("Use o Dashboard Executivo para histórico completo."); return
        lancs = buscar_lancamentos(mes_ano,equipe_id)
        ops   = buscar_operadores(equipe_id)
        if not lancs: st.info("Nenhum lançamento para este mês.")
        else:
            for lanc in lancs:
                dt_str = str(lanc.get("criadoEm",""))[:16]
                with st.expander(f"📅 {lanc.get('label','')} — {fmt_brl(lanc.get('totalEquipe',0))} — {dt_str}",expanded=False):
                    rows = [{"Operador":op["nome"],"Valor":fmt_brl(float(lanc.get("agentes",{}).get(op["_id"],{}).get("valorRecebido",0)))} for op in ops]
                    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Com Interação",fmt_brl(lanc.get("totalEquipe",0)))
                    c2.metric("Sem Interação",fmt_brl(lanc.get("semInteracao",0)))
                    c3.metric("Total Geral",  fmt_brl(lanc.get("valorGeral",0)))
                    if st.button(f"🗑️ Excluir",key=f"del_{lanc['_id']}"):
                        excluir_lancamento(lanc["_id"]); st.warning("Excluído!"); st.rerun()

    with t2:
        mp = listar_meses_processados()
        if not mp: st.info("Nenhuma base processada.")
        else:
            mh = st.selectbox("Selecione o mês",mp)
            df = buscar_processamentos(mh,equipe_id)
            if df.empty: st.info("Sem dados.")
            else:
                df["valor"] = pd.to_numeric(df["valor"],errors="coerce").fillna(0)
                c1,c2,c3 = st.columns(3)
                c1.metric("Valor Elegível",fmt_brl(df[df["elegibilidade"]=="Elegível"]["valor"].sum()))
                c2.metric("Boletos",f'{len(df):,}'); c3.metric("Clientes",f'{df["uc_cpf"].nunique():,}')
                st.dataframe(df[["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging"]].head(100),use_container_width=True)

# ── DASHBOARD EXECUTIVO ─────────────────────────
def pagina_dashboard_executivo():
    header_page("Dashboard Executivo","Gestão de Inadimplência Comercial")
    mp = listar_meses_processados()
    if not mp: st.info("📭 Nenhuma base processada ainda."); return

    c1,c2,c3 = st.columns(3)
    with c1: mes_f = st.selectbox("Mês",["Todos"]+mp)
    with c2: eq_f  = st.selectbox("Equipe",["Todas","luciano","deborah","tamires"])
    df = buscar_processamentos(None if mes_f=="Todos" else mes_f, None if eq_f=="Todas" else eq_f)
    if df.empty: st.warning("Nenhum dado."); return

    df["valor"] = pd.to_numeric(df["valor"],errors="coerce").fillna(0)
    with c3:
        forns = ["Todas"]+sorted(df["fornecedora"].dropna().unique().tolist())
        forn_f = st.selectbox("Fornecedora",forns)
    if forn_f!="Todas": df = df[df["fornecedora"]==forn_f]

    st.markdown("---")
    elig=df[df["elegibilidade"]=="Elegível"]; nelig=df[df["elegibilidade"]=="Não Elegível"]; nd=df[df["elegibilidade"]=="ND"]
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Valor Recuperado",fmt_brl(elig["valor"].sum()))
    c2.metric("Clientes Únicos",f'{df["uc_cpf"].nunique():,}')
    c3.metric("Boletos",f'{len(df):,}')
    c4.metric("Elegíveis",f'{len(elig):,}')
    c5.metric("Não Elegíveis",f'{len(nelig):,}')
    c6.metric("ND",f'{len(nd):,}')
    st.markdown("---")

    t1,t2,t3,t4 = st.tabs(["Aging","Fornecedoras","Evolução","Por Equipe"])
    with t1:
        ag=df.groupby("aging").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        ag["Valor"]=ag["Valor"].apply(fmt_brl)
        st.dataframe(ag.rename(columns={"aging":"Faixa"}),use_container_width=True,hide_index=True)
        st.bar_chart(df.groupby("aging")["uc_cpf"].count(),color="#2daf5c")
    with t2:
        fdf=df.groupby("fornecedora").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        fdf["Valor"]=fdf["Valor"].apply(fmt_brl)
        st.dataframe(fdf.rename(columns={"fornecedora":"Fornecedora"}),use_container_width=True,hide_index=True)
    with t3:
        da=buscar_processamentos()
        if not da.empty:
            da["valor"]=pd.to_numeric(da["valor"],errors="coerce").fillna(0)
            evol=da[da["elegibilidade"]=="Elegível"].groupby("_mes_ano")["valor"].sum().reset_index()
            evol.columns=["Mês","Valor"]
            st.bar_chart(evol.sort_values("Mês").set_index("Mês"),color="#2daf5c")
    with t4:
        edf=df.groupby("_equipe").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        edf["Equipe"]=edf["_equipe"].map(lambda x:EQUIPES.get(x,{}).get("nome",x))
        edf["Valor"]=edf["Valor"].apply(fmt_brl)
        st.dataframe(edf[["Equipe","Boletos","Clientes","Valor"]],use_container_width=True,hide_index=True)

    st.markdown("---")
    if st.button("Exportar Excel"):
        out=io.BytesIO()
        with pd.ExcelWriter(out,engine="xlsxwriter") as w:
            df.to_excel(w,sheet_name="Dados",index=False)
            elig.to_excel(w,sheet_name="Elegíveis",index=False)
        st.download_button("⬇️ Baixar",data=out.getvalue(),file_name=f"iGreen_{mes_f}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── UPLOAD ─────────────────────────────────────
def pagina_upload(mes_ano):
    u = st.session_state.usuario
    header_page("Upload de Bases Mensais","Aceita .xlsx e .csv · Processamento automático")
    equipe_id = seletor_equipe(u["equipe"] or "tamires")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### PAGOS *(obrigatório)*")
        pf = st.file_uploader("Arquivo PAGOS",type=["xlsx","csv"],label_visibility="collapsed",key="pagos")
        st.markdown("#### LIGAÇÕES")
        lf = st.file_uploader("Arquivo LIGAÇÕES",type=["xlsx","csv"],label_visibility="collapsed",key="lig")
    with c2:
        st.markdown("#### CHAT")
        cf = st.file_uploader("Arquivo CHAT",type=["xlsx","csv"],label_visibility="collapsed",key="chat")
        st.markdown("#### DISPAROS")
        df_u = st.file_uploader("Arquivo DISPAROS",type=["xlsx","csv"],label_visibility="collapsed",key="disp")


    # Status badges - clean HTML, no Streamlit widgets
    def badge(nome, carregado, obrigatorio=False):
        if carregado:
            return f"<div style='background:#e8f5e9;border:1px solid #a5d6a7;border-radius:6px;padding:8px 14px;font-size:12px;font-weight:600;color:#2e7d32;display:inline-block'>✓ {nome} carregado</div>"
        elif obrigatorio:
            return f"<div style='background:#fff8e1;border:1px solid #ffe082;border-radius:6px;padding:8px 14px;font-size:12px;font-weight:600;color:#f57f17;display:inline-block'>⏳ {nome} aguardando</div>"
        else:
            return f"<div style='background:#f5f5f5;border:1px solid #e0e0e0;border-radius:6px;padding:8px 14px;font-size:12px;color:#757575;display:inline-block'>{nome} (opcional)</div>"

    st.markdown(
        f"<div style='display:flex;gap:12px;flex-wrap:wrap;margin:16px 0'>"
        f"{badge('PAGOS', bool(pf), True)}"
        f"{badge('CHAT', bool(cf))}"
        f"{badge('LIGAÇÕES', bool(lf))}"
        f"{badge('DISPAROS', bool(df_u))}"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    if st.button("PROCESSAR MÊS",use_container_width=True):
        if not pf: st.error("⚠ PAGOS é obrigatório!"); return
        with st.spinner("Processando bases..."):
            df_res,erros = processar_bases(pf,cf,lf,df_u,equipe_id,mes_ano)
        for e in erros: st.error(e)
        if df_res is not None and not df_res.empty:
            salvar_processamento(mes_ano,equipe_id,df_res)
            elig = df_res[df_res["elegibilidade"]=="Elegível"]
            st.success(f"✅ {len(df_res):,} registros processados!")
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Valor Elegível",fmt_brl(elig["valor"].sum()))
            c2.metric("Boletos",f"{len(df_res):,}")
            c3.metric("Clientes",f"{df_res['uc_cpf'].nunique():,}")
            c4.metric("Elegíveis",f"{len(elig):,}")
            c5.metric("Não Elegíveis",f"{len(df_res[df_res['elegibilidade']=='Não Elegível']):,}")
            st.dataframe(df_res[["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging"]].head(50),use_container_width=True)

# ── MAIN ───────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login(); return

    mes_ano,pagina = render_sidebar()
    u = st.session_state.usuario

    if u["role"]=="diretor":
        if "Quadro"      in pagina: pagina_quadro(mes_ano)
        elif "Dashboard" in pagina: pagina_dashboard_executivo()
        elif "Projeção"  in pagina: pagina_analise_projecao(mes_ano)
        elif "Monitorias" in pagina: pagina_monitorias(mes_ano)
        elif "Histórico" in pagina: pagina_historico(mes_ano)

    elif u["role"]=="admin":
        if "Quadro"      in pagina: pagina_quadro(mes_ano)
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano)
        elif "Dashboard"  in pagina: pagina_dashboard_executivo()
        elif "Projeção"   in pagina: pagina_analise_projecao(mes_ano)
        elif "Monitorias" in pagina: pagina_monitorias(mes_ano)
        elif "Upload"     in pagina: pagina_upload(mes_ano)
        elif "Histórico"  in pagina: pagina_historico(mes_ano)
        elif "Operadores" in pagina: pagina_operadores()
        elif "Metas"      in pagina: pagina_metas(mes_ano)

    else:
        if "Quadro"      in pagina: pagina_quadro(mes_ano)
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano)
        elif "Projeção"   in pagina: pagina_analise_projecao(mes_ano)
        elif "Monitorias" in pagina: pagina_monitorias(mes_ano)
        elif "Upload"     in pagina: pagina_upload(mes_ano)
        elif "Histórico"  in pagina: pagina_historico(mes_ano)
        elif "Operadores" in pagina: pagina_operadores()
        elif "Metas"      in pagina: pagina_metas(mes_ano)

if __name__=="__main__":
    main()
