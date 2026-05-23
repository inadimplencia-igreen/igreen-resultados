import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, date
import io
import base64
import re
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Inadimplência Performance", page_icon="logo.png", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #004d20; }
[data-testid="stSidebar"] { background: #003318; border-right: 1px solid #005a25; }
[data-testid="stMetric"] { background: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 10px; padding: 18px 20px !important; border-top: 3px solid #00c853; }
[data-testid="stMetricValue"] { color: #1b5e20 !important; font-size: 22px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #2e7d32 !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }
.stButton > button { background: #00c853 !important; color: white !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; font-size: 13px !important; padding: 10px 20px !important; box-shadow: 0 2px 8px rgba(0,200,83,0.3) !important; }
.stButton > button:hover { background: #00e676 !important; transform: translateY(-1px) !important; }
h1 { color: #ffffff !important; font-size: 20px !important; font-weight: 700 !important; }
h2 { color: #e8f5e9 !important; font-size: 16px !important; font-weight: 600 !important; }
h3 { color: #81c784 !important; font-size: 10px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 2px; }
p  { color: #c8e6c9 !important; font-size: 13px; }
hr { border: none !important; border-top: 1px solid #005a25 !important; margin: 14px 0 !important; }
.stTextInput input, .stNumberInput input, .stTextArea textarea { background: #e8f5e9 !important; border: 1px solid #a5d6a7 !important; color: #1b5e20 !important; border-radius: 6px !important; font-size: 13px !important; }
.stSelectbox > div > div { background: #e8f5e9 !important; border: 1px solid #a5d6a7 !important; color: #1b5e20 !important; border-radius: 6px !important; font-size: 13px !important; }
[data-testid="stSidebar"] .stRadio label { color: #a5d6a7 !important; font-size: 12px !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { color: #a5d6a7 !important; }
.stTabs [data-baseweb="tab-list"] { background: #003318 !important; border-radius: 6px !important; padding: 3px !important; }
.stTabs [data-baseweb="tab"] { color: #81c784 !important; border-radius: 5px !important; font-size: 12px !important; font-weight: 500 !important; padding: 7px 14px !important; }
.stTabs [aria-selected="true"] { background: #00c853 !important; color: #ffffff !important; }
.stCheckbox label { color: #e8f5e9 !important; font-size: 13px !important; }
[data-testid="stFileUploader"] > div { background: #e8f5e9 !important; border: 1.5px dashed #a5d6a7 !important; border-radius: 8px !important; }
[data-testid="stFileUploader"] * { color: #2e7d32 !important; }
.stSuccess > div { background: #e8f5e9 !important; border: 1px solid #a5d6a7 !important; color: #2e7d32 !important; border-radius: 6px !important; }
.stWarning > div { background: #fff8e1 !important; border: 1px solid #ffe082 !important; color: #f57f17 !important; border-radius: 6px !important; }
.stError > div { background: #ffebee !important; border: 1px solid #ef9a9a !important; color: #c62828 !important; border-radius: 6px !important; }
.stInfo > div { background: #e3f2fd !important; border: 1px solid #90caf9 !important; color: #1565c0 !important; border-radius: 6px !important; }
[data-testid="stDataFrame"] { border: 1px solid #a5d6a7 !important; border-radius: 8px !important; }
.streamlit-expanderHeader { background: #e8f5e9 !important; border: 1px solid #a5d6a7 !important; border-radius: 6px !important; color: #1b5e20 !important; font-size: 13px !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #004d20; }
::-webkit-scrollbar-thumb { background: #00c853; border-radius: 2px; }
#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stVerticalBlock"] label { color: #c8e6c9 !important; font-size: 12px !important; }
.block-container { padding: 2rem 2rem 2rem !important; max-width: 1200px !important; }
</style>
""", unsafe_allow_html=True)

def _get_usuarios():
    """Lê senhas dos Secrets do Streamlit — nunca ficam expostas no código."""
    try:
        s = st.secrets["usuarios"]
        return {
            "tamires": {"senha": s["tamires"], "equipe":"tamires","role":"admin",  "nome":"Tamires"},
            "luciano": {"senha": s["luciano"], "equipe":"luciano","role":"gestor", "nome":"Luciano"},
            "deborah": {"senha": s["deborah"], "equipe":"deborah","role":"gestor", "nome":"Déborah"},
            "veloso":  {"senha": s["veloso"],  "equipe":None,     "role":"diretor","nome":"Veloso"},
            "moyara":  {"senha": s["moyara"],  "equipe":None,     "role":"diretor","nome":"Moyara"},
        }
    except:
        st.error("Configuração de usuários ausente nos Secrets do Streamlit.")
        st.stop()

USUARIOS = _get_usuarios()
EQUIPES = {
    "luciano":{"nome":"Luciano","cor":"#2daf5c"},
    "deborah":{"nome":"Déborah","cor":"#a855f7"},
    "tamires":{"nome":"Tamires","cor":"#f97316"},
    "metcool":{"nome":"MetCool","cor":"#3b82f6"},
}
MESES_NOMES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
CRITERIOS_PADRAO = [
    {"id":"c1","num":"1º","nome":"Abertura e Identificação","peso":5,"itens":["Saudação adequada","Identificação do operador e da empresa","Sem conversas paralelas fora do mudo"],"obrigatorio":False},
    {"id":"c2","num":"2º","nome":"Comunicação e Postura","peso":5,"itens":["Clareza na fala e respeito com o cliente","Tom respeitoso, sem ironia ou pressão","Escuta ativa — não interromper"],"obrigatorio":False},
    {"id":"c3","num":"3º","nome":"Diagnóstico da Dívida","peso":10,"itens":["Questionar o motivo da inadimplência","Recorda do contrato? Recebeu boleto? Tem acesso ao app? Previsão de pagamento?"],"obrigatorio":False},
    {"id":"c4","num":"4º","nome":"Negociação","peso":40,"itens":["Argumentação de benefícios do pagamento pontual","! Obrigatório: perguntar sobre dúvidas em boletos","! Obrigatório: perguntar sobre acesso ao app","! Obrigatório: falar sobre iGreen Club (mín. 2)"],"obrigatorio":True},
    {"id":"c5","num":"5º","nome":"Conformidade","peso":20,"itens":["Questionar o motivo do cancelamento","Não ameaçar ou constranger"],"obrigatorio":False},
    {"id":"c6","num":"6º","nome":"Registros e Procedimentos","peso":10,"itens":["Registro correto no sistema","Classificação adequada da ligação"],"obrigatorio":False},
    {"id":"c7","num":"7º","nome":"Encerramento","peso":10,"itens":["Esclarecimento do acordo fechado","Agradecimento e cordialidade"],"obrigatorio":False},
]
ERROS_CRITICOS_PADRAO = [
    {"id":"e1","nome":"Informação incorreta","desc":"Passou informação incorreta, incompleta ou errada ao cliente"},
    {"id":"e2","nome":"Postura ríspida","desc":"Agiu de forma ríspida ou ameaçadora"},
    {"id":"e3","nome":"Linguagem agressiva","desc":"Usar linguajar agressivo com o cliente"},
    {"id":"e4","nome":"Retenção de ligação","desc":"Segurar a ligação até dar o tempo legível para cota"},
    {"id":"e5","nome":"Contra-argumentação indevida","desc":"Cliente reclama do desconto e você oferta conta única"},
]
FAIXAS_PONTOS = [(0,60,0),(61,70,300),(71,80,500),(81,90,700),(91,99,1000),(100,100,1100)]
SEMANAS_MONITORIA = [
    "1ª Semana — 1ª Monitoria","1ª Semana — 2ª Monitoria",
    "2ª Semana — 1ª Monitoria","2ª Semana — 2ª Monitoria",
    "3ª Semana — 1ª Monitoria","3ª Semana — 2ª Monitoria",
    "4ª Semana — 1ª Monitoria","4ª Semana — 2ª Monitoria",
]
OPERADORES_PADRAO = {
    "luciano":[("Jennifer Silveira",True),("Paulo Roberto",False),("Samires Barros",False),("Maycow Gabriel",False),("Otaides Junior",False),("Heverton Tavares",False),("Camila Nara",False),("Caua Alves",False),("Eduarda Sanqueta",False),("Jheniffer Santos",False),("Ketie Silva",False),("Emanuel Cardoso",False),("Victória Silva",False),("Grasielli Santos",False),("Laura Silva",False),("Michelle Batista",False),("Lorenzzo Pereira",False),("Diogo Oliveira",False),("Maria Paulino",False),("Gabrielle Martins",False),("Marcos Martins",False)],
    "deborah":[("Mikael Dias",False),("Amanda Eduarda",False),("Larissa Barcelos",False),("Nicole Amaral",False),("Sara Rocha",False),("Isabelly Araujo",False),("Silye Paula",False)],
    "tamires":[("Danilo Rodrigues",True),("Raiane Pereira",False),("Wynara Dos Reis",False),("Esteffany Souza",False),("André Gomes",False),("Wanessa Cardoso",False),("Larisse Garcia",False),("Arthur Alves",False)],
    "metcool":[],
}
FORNECEDORAS_TODAS = ["COTESA/MOVE","ULTRA","VANTAGE","FARO","BOM FUTURO","SUNCLICK","ATUA"]
CORES_FORN = {"COTESA/MOVE":"#1b5e20","ULTRA":"#0d47a1","VANTAGE":"#e65100","FARO":"#b71c1c","BOM FUTURO":"#4a148c","SUNCLICK":"#004d40","ATUA":"#37474f"}

# ── MONGODB ────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(st.secrets["mongo"]["uri"], serverSelectionTimeoutMS=5000)
    return client[st.secrets["mongo"]["db"]]

def get_criterios():
    try:
        doc = get_db().configuracoes.find_one({"_id":"criterios_monitoria"})
        if doc and doc.get("criterios"): return doc["criterios"]
    except: pass
    return CRITERIOS_PADRAO

def salvar_criterios(c):
    get_db().configuracoes.update_one({"_id":"criterios_monitoria"},{"$set":{"_id":"criterios_monitoria","criterios":c,"atualizadoEm":datetime.now()}},upsert=True)

def get_erros_criticos():
    try:
        doc = get_db().configuracoes.find_one({"_id":"erros_criticos_monitoria"})
        if doc and doc.get("erros"): return doc["erros"]
    except: pass
    return ERROS_CRITICOS_PADRAO

def salvar_erros_criticos(e):
    get_db().configuracoes.update_one({"_id":"erros_criticos_monitoria"},{"$set":{"_id":"erros_criticos_monitoria","erros":e,"atualizadoEm":datetime.now()}},upsert=True)

def corrigir_ids_operadores():
    db = get_db()
    for op in list(db.operadores.find({})):
        eq = op.get("equipeId",""); nome = op.get("nome","")
        if not nome: continue
        nid = re.sub(r'[^a-z0-9]','-',nome.lower().strip())
        nid = re.sub(r'-+','-',nid).strip('-')
        idc = f"{eq[:3]}-{nid}"[:40]
        if op["_id"] != idc:
            if not db.operadores.find_one({"_id":idc}):
                db.operadores.insert_one({"_id":idc,"equipeId":eq,"nome":nome,"pleno":op.get("pleno",False),"criadoEm":op.get("criadoEm",datetime.now())})
            db.operadores.delete_one({"_id":op["_id"]})

def buscar_operadores(eq): return list(get_db().operadores.find({"equipeId":eq}).sort("nome",1))

def salvar_operador(eq, nome, pleno=False):
    oid = re.sub(r'[^a-z0-9]','-',nome.lower().strip())
    oid = re.sub(r'-+','-',oid).strip('-')
    oid = f"{eq[:3]}-{oid}"[:40]
    if not get_db().operadores.find_one({"_id":oid}):
        get_db().operadores.insert_one({"_id":oid,"equipeId":eq,"nome":nome,"pleno":pleno,"criadoEm":datetime.now()})
    return oid

def excluir_operador(oid): get_db().operadores.delete_one({"_id":oid})
def atualizar_operador(oid, nome, pleno): get_db().operadores.update_one({"_id":oid},{"$set":{"nome":nome,"pleno":pleno}})

def salvar_meta_operador(ma, eq, oid, v):
    did = f"meta_op__{ma}__{eq}__{oid}"
    get_db().metas.update_one({"_id":did},{"$set":{"_id":did,"mesAno":ma,"equipeId":eq,"opId":oid,"valor":v}},upsert=True)

def buscar_metas_equipe(ma, eq):
    return {d["opId"]:d.get("valor",0) for d in get_db().metas.find({"mesAno":ma,"equipeId":eq}) if "opId" in d}

def salvar_meta_gestora(ma, eq, meta, tpct):
    did = f"meta_gest__{ma}__{eq}"
    get_db().metas.update_one({"_id":did},{"$set":{"_id":did,"mesAno":ma,"equipeId":eq,"metaGestora":meta,"targetPct":tpct,"tipo":"gestora"}},upsert=True)

def buscar_meta_gestora(ma, eq):
    return get_db().metas.find_one({"_id":f"meta_gest__{ma}__{eq}"}) or {"metaGestora":0,"targetPct":125}

def criar_lancamento(ma, eq, data_ref, label, agentes, total, sem_int, dt, td):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    get_db().lancamentos.insert_one({"_id":f"lanc__{ma}__{eq}__{ts}","mesAno":ma,"equipeId":eq,"dataRef":data_ref,"label":label,"agentes":agentes,"totalEquipe":total,"semInteracao":sem_int,"diasTrabalhados":dt,"totalDias":td,"criadoEm":datetime.now()})

def buscar_lancamentos(ma, eq):
    novos = list(get_db().lancamentos.find({"mesAno":ma,"equipeId":eq}).sort("criadoEm",-1))
    antigos = []
    for d in get_db().resultados.find({"mesAno":ma,"equipeId":eq}):
        antigos.append({"_id":d["_id"],"mesAno":d["mesAno"],"equipeId":d["equipeId"],"label":d.get("semanaId","Registro anterior"),"dataRef":d.get("atualizadoEm",""),"agentes":d.get("agentes",{}),"totalEquipe":d.get("totalEquipe",0),"valorGeral":d.get("valorGeral",0),"semInteracao":d.get("semInteracao",0),"diasTrabalhados":d.get("diasTrabalhados",0),"totalDias":d.get("totalDias",22),"criadoEm":d.get("atualizadoEm",datetime.now())})
    todos = novos + antigos
    todos.sort(key=lambda x: x.get("criadoEm",datetime.now()), reverse=True)
    return todos

def excluir_lancamento(did):
    if get_db().lancamentos.delete_one({"_id":did}).deleted_count == 0:
        get_db().resultados.delete_one({"_id":did})

def salvar_monitoria(eq, oid, onome, prot, obs, crits, erros, nota, ma, semana=None):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    get_db().monitorias.insert_one({"_id":f"mon__{eq}__{oid}__{ts}","equipeId":eq,"opId":oid,"opNome":onome,"protocolo":prot,"observacao":obs,"criterios":crits,"errosCriticos":erros,"nota":nota,"mesAno":ma,"semana_mon":semana,"criadoEm":datetime.now()})

def buscar_monitorias_operador(oid): return list(get_db().monitorias.find({"opId":oid}).sort("criadoEm",-1))

def buscar_monitorias_equipe(eq, ma=None):
    f = {"equipeId":eq}
    if ma: f["mesAno"] = ma
    return list(get_db().monitorias.find(f).sort("criadoEm",-1))

def excluir_monitoria(did): get_db().monitorias.delete_one({"_id":did})

def salvar_processamento(ma, eq, df):
    get_db().processamentos.update_one({"_id":f"proc__{ma}__{eq}"},{"$set":{"_id":f"proc__{ma}__{eq}","mesAno":ma,"equipeId":eq,"registros":df.to_dict("records"),"atualizadoEm":datetime.now()}},upsert=True)

def buscar_ultimo_processamento(ma, eq):
    doc = get_db().processamentos.find_one({"mesAno":ma,"equipeId":eq},sort=[("criadoEm",-1)])
    if not doc: return {}
    if not doc.get("valorElegivel") and doc.get("registros"):
        try:
            df = pd.DataFrame(doc["registros"])
            if "elegibilidade" in df.columns and "valor" in df.columns:
                elig = df[df["elegibilidade"]=="Elegível"]
                doc["valorElegivel"] = float(elig["valor"].sum())
                doc["boletosElegiveis"] = len(elig)
                doc["clientesElegiveis"] = int(elig["uc_cpf"].nunique()) if "uc_cpf" in elig.columns else 0
        except: pass
    return doc

def buscar_historico_processamentos(ma, eq): return list(get_db().processamentos.find({"mesAno":ma,"equipeId":eq}).sort("criadoEm",-1))
def excluir_processamento(did): get_db().processamentos.delete_one({"_id":did})

def buscar_processamentos(ma=None, eq=None):
    f = {}
    if ma: f["mesAno"]=ma
    if eq: f["equipeId"]=eq
    frames = []
    for d in get_db().processamentos.find(f):
        if d.get("registros"):
            df = pd.DataFrame(d["registros"])
            df["_equipe"]=d["equipeId"]; df["_mes_ano"]=d["mesAno"]
            frames.append(df)
    return pd.concat(frames,ignore_index=True) if frames else pd.DataFrame()

def listar_meses_processados(): return sorted(get_db().processamentos.distinct("mesAno"),reverse=True)

def salvar_senha_usuario(uid, nova_senha):
    """Salva senha do usuário no MongoDB — nunca no código."""
    get_db().usuarios_senhas.update_one(
        {"_id": uid},
        {"$set": {"_id": uid, "senha": nova_senha, "atualizadoEm": datetime.now()}},
        upsert=True)

def buscar_senha_usuario(uid):
    """Busca senha customizada do usuário. Se não tiver, usa a dos Secrets."""
    doc = get_db().usuarios_senhas.find_one({"_id": uid})
    if doc and doc.get("senha"):
        return doc["senha"]
    try:
        return st.secrets["usuarios"][uid]
    except:
        return None

def salvar_inadimplencia(ma, eq, dados):
    did = f"inadimp__{ma}__{eq}"
    get_db().inadimplencia.update_one({"_id":did},{"$set":{"_id":did,"mesAno":ma,"equipeId":eq,"dados":dados,"atualizadoEm":datetime.now()}},upsert=True)

def buscar_inadimplencia(ma, eq): return get_db().inadimplencia.find_one({"_id":f"inadimp__{ma}__{eq}"})
def listar_meses_inadimplencia(): return sorted(get_db().inadimplencia.distinct("mesAno"),reverse=True)

# ── HELPERS ────────────────────────────────────
def fmt_brl(v):
    if v is None or v=="": return "R$ 0,00"
    try: return "R$ "+f"{float(v):_.2f}".replace(".",",").replace("_",".")
    except: return "R$ 0,00"

def fmt_brl_td(v):
    if not v or float(v)==0: return "—"
    return "R$ "+f"{float(v):_.2f}".replace(".",",").replace("_",".")

def calc_projecao(v, dt, td):
    if not dt or dt<=0: return 0
    return (v/dt)*td

def calc_variacao(atual, ant):
    if not ant or ant==0: return None
    return ((atual-ant)/ant)*100

def cor_pct(p):
    if p>=80: return "#2daf5c"
    if p>=50: return "#f0a500"
    return "#e03c3c"

def status_pct(p):
    if p>=80: return "Ótimo"
    if p>=50: return "Regular"
    return "Abaixo"

def calc_pontos(media):
    for lo,hi,pts in FAIXAS_PONTOS:
        if lo<=media<=hi: return pts
    return 0

def calc_media_operador(oid, ma=None):
    monts = buscar_monitorias_operador(oid)
    if ma: monts=[m for m in monts if m.get("mesAno")==ma]
    if not monts: return 0,0
    notas=[m["nota"] for m in monts if "nota" in m]
    if not notas: return 0,0
    return round(sum(notas)/len(notas),1),len(notas)

def get_status_media(media):
    if media==0:   return "Zerada","#e53935","#ffebee"
    if media>=91:  return "Excelente","#2e7d32","#e8f5e9"
    if media>=81:  return "Bom","#1565c0","#e3f2fd"
    if media>=71:  return "Regular","#f57f17","#fff8e1"
    return "Em desenvolvimento","#6d4c41","#efebe9"

def get_iniciais(nome):
    p=nome.strip().split()
    if len(p)>=2: return (p[0][0]+p[1][0]).upper()
    return nome[:2].upper()

CORES_INICIAIS=["#1565c0","#2e7d32","#6a1b9a","#bf360c","#00695c","#4527a0","#ad1457","#0277bd","#558b2f","#4e342e"]
def get_cor_inicial(nome): return CORES_INICIAIS[sum(ord(c) for c in nome)%len(CORES_INICIAIS)]

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

def header_page(titulo, sub=""):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#003318,#004d20);border:1px solid #005a25;
                border-radius:12px;padding:22px 28px;margin-bottom:24px;
                border-left:4px solid #00c853;box-shadow:0 4px 20px rgba(0,0,0,0.2)">
        <h1 style="margin:0;color:#ffffff;font-size:20px;font-weight:700">{titulo}</h1>
        {"<p style='color:#81c784;margin:4px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px'>"+sub+"</p>" if sub else ""}
    </div>""",unsafe_allow_html=True)

def seletor_equipe(default=None, key_suffix=""):
    u=st.session_state.usuario
    if u["role"]=="admin":
        eq_opts=list(EQUIPES.keys())
        eq_labels=[f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        default_idx=eq_opts.index(default) if default and default in eq_opts else 0
        import traceback
        caller=traceback.extract_stack()[-2].name
        sel=st.selectbox("Gerenciando equipe:",eq_labels,index=default_idx,key=f"admin_eq_{caller}{key_suffix}")
        return eq_opts[eq_labels.index(sel)]
    return u["equipe"]

def get_val_op(ag, oid, onome):
    for k,v in ag.items():
        if isinstance(v,dict) and v.get("nome","").strip().lower()==onome.strip().lower():
            return float(v.get("valorRecebido",0))
    if oid in ag:
        v=ag[oid]
        return float(v.get("valorRecebido",0) if isinstance(v,dict) else v)
    return 0.0

def normalizar_cpf(s):
    s=str(s).strip()
    try: s=str(int(float(s)))
    except: s=s.replace(".","").replace("-","").replace("/","").replace(" ","")
    if s.isdigit() and len(s)<11: s=s.zfill(11)
    return s

def processar_base_unica(arquivo, eq, ma):
    import unicodedata
    def norm(s): return unicodedata.normalize('NFKD',str(s).upper().strip()).encode('ascii','ignore').decode()
    try: xls=pd.ExcelFile(arquivo)
    except Exception as e: return None,[f"Erro: {e}"],[]
    abas_norm=[norm(a) for a in xls.sheet_names]; abas_orig=xls.sheet_names
    aba_pagos=next((abas_orig[i] for i,a in enumerate(abas_norm) if any(p in a for p in ["PAGO","PAGAM","RECEB","BASE"])),abas_orig[0])
    df=pd.read_excel(xls,sheet_name=aba_pagos,header=0).reset_index(drop=True)
    df["_row_id"]=df.index
    col_cpf=col_val=col_dpag=col_dvenc=col_forn=None
    for c in df.columns:
        cn=norm(str(c))
        if not col_cpf  and any(x in cn for x in ["CPF","UC","INSTAL","MATRICUL","COD_C","CODIGO_C","ID_C","NUM_C"]): col_cpf=c
        if not col_val  and any(x in cn for x in ["VALOR","VLR","VL_"]): col_val=c
        if not col_dpag and any(x in cn for x in ["PAGAM","PAGTO","DT_PAG","DATA_PAG","BAIXA","DT_BAI"]): col_dpag=c
        if not col_dvenc and "VENC" in cn: col_dvenc=c
        if not col_forn and any(x in cn for x in ["FORNEC","DISTRIB","EMPRESA","CONCESS"]): col_forn=c
    mapa={}
    if col_cpf:   mapa[col_cpf]="uc_cpf"
    if col_val:   mapa[col_val]="valor"
    if col_dpag:  mapa[col_dpag]="data_pagamento"
    if col_dvenc: mapa[col_dvenc]="data_vencimento"
    if col_forn:  mapa[col_forn]="fornecedora"
    df=df.rename(columns=mapa)
    if "uc_cpf" in df.columns: df["uc_cpf"]=df["uc_cpf"].apply(normalizar_cpf)
    if "data_pagamento" in df.columns: df["data_pagamento"]=pd.to_datetime(df["data_pagamento"],dayfirst=True,errors="coerce").dt.normalize()
    if "data_vencimento" in df.columns: df["data_vencimento"]=pd.to_datetime(df["data_vencimento"],dayfirst=True,errors="coerce").dt.normalize()
    if "valor" in df.columns:
        def cv(v):
            s=str(v).strip().replace("R$","").replace(" ","")
            try: return float(s)
            except:
                try: return float(s.replace(".","").replace(",","."))
                except: return 0.0
        df["valor"]=df["valor"].apply(cv)
    contatos=[]; abas_lidas=[]
    for busca,nome in [("CHAT","CHAT"),("LIG","LIGAÇÕES"),("DISPAR","DISPAROS")]:
        aba=next((abas_orig[i] for i,a in enumerate(abas_norm) if busca in a),None)
        if not aba: continue
        try:
            dc=pd.read_excel(xls,sheet_name=aba,header=0)
            if dc.empty or len(dc.columns)<2: continue
            cc=next((c for c in dc.columns if any(x in norm(str(c)) for x in ["CPF","UC","INSTAL","MATRICUL","COD","CLIENT"])),dc.columns[0])
            cd=next((c for c in dc.columns if any(x in norm(str(c)) for x in ["DATA","DT_","BAIXA","CONTATO","INTERAC","LIGAC","CHAT","DISPAR","PAGAM"])),dc.columns[1] if len(dc.columns)>1 else dc.columns[0])
            dd=pd.DataFrame({"uc_cpf":dc[cc].apply(normalizar_cpf),"data_contato":pd.to_datetime(dc[cd],dayfirst=True,errors="coerce").dt.normalize()}).dropna(subset=["data_contato"])
            dd=dd[dd["uc_cpf"].str.len()>=3]
            if not dd.empty: contatos.append(dd); abas_lidas.append(nome)
        except: pass
    if contatos:
        pc=pd.concat(contatos,ignore_index=True).groupby("uc_cpf",as_index=False)["data_contato"].min()
        df["primeiro_contato"]=df["uc_cpf"].map(dict(zip(pc["uc_cpf"],pc["data_contato"])))
    else: df["primeiro_contato"]=pd.NaT
    df=df.drop(columns=["_row_id"],errors="ignore").reset_index(drop=True)
    df["data_pagamento"]=pd.to_datetime(df["data_pagamento"],errors="coerce").dt.normalize()
    df["primeiro_contato"]=pd.to_datetime(df["primeiro_contato"],errors="coerce").dt.normalize()
    df["diferenca_dias"]=(df["data_pagamento"]-df["primeiro_contato"]).dt.days
    def classif(row):
        if pd.isna(row.get("primeiro_contato")): return "ND"
        d=row.get("diferenca_dias")
        if pd.isna(d): return "ND"
        return "Elegível" if int(d)>=0 else "Não Elegível"
    df["elegibilidade"]=df.apply(classif,axis=1)
    if "data_vencimento" in df.columns: df["dias_vencidos"]=(df["data_pagamento"]-df["data_vencimento"]).dt.days
    else: df["dias_vencidos"]=None
    df["aging"]=df["dias_vencidos"].apply(aging_faixa)
    for col in ["data_vencimento","data_pagamento","primeiro_contato"]:
        if col in df.columns:
            try: df[col]=pd.to_datetime(df[col],errors="coerce").dt.strftime("%Y-%m-%d").where(pd.to_datetime(df[col],errors="coerce").notna(),other=None)
            except: pass
    df["equipe"]=eq; df["mes_ano"]=ma
    return df,[],abas_lidas

def gerar_pdf_monitoria(onome, prot, obs, crits, erros, nota, media, n_mon, ma):
    pontos=calc_pontos(media)
    L=[]
    L.append(f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a1a1a;margin:0;padding:0}}
.hdr{{background:#0a2414;color:#fff;padding:32px 40px}}.logo{{font-size:24px;font-weight:800;color:#2daf5c}}
.body{{padding:32px 40px}}
.irow{{display:flex;gap:32px;margin-bottom:24px;background:#f8fdf9;border-radius:10px;padding:16px 20px;border-left:4px solid #2daf5c}}
.lbl{{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;font-weight:600}}
.val{{font-size:15px;font-weight:700;color:#0a2414;margin-top:2px}}
table{{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px}}
thead th{{background:#0a2414;color:#fff;padding:10px 14px;text-align:left}}
tbody tr:nth-child(even){{background:#f0f9f3}}
tbody td{{padding:10px 14px;border-bottom:1px solid #e0ede5}}
.ok{{color:#1a6b35;font-weight:700}}.no{{color:#c0392b;font-weight:700}}
.nbox{{background:#0a2414;color:#fff;border-radius:12px;padding:24px;text-align:center;margin-bottom:24px}}
.nnum{{font-size:48px;font-weight:800;color:#2daf5c}}
.mbox{{background:#f0f9f3;border:1px solid #c3e6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px;display:flex;gap:32px}}
.crit{{background:#fdf0f0;border:1px solid #f5c6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px}}
.obs{{background:#f8fdf9;border:1px solid #c3e6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px}}
.foot{{background:#f0f9f3;padding:16px 40px;text-align:center;font-size:11px;color:#5a9a70;border-top:2px solid #2daf5c}}
</style></head><body>
<div class='hdr'><div class='logo'>iGREEN ENERGY</div><div style='font-size:13px;color:#5a9a70;margin-top:4px'>Relatório de Monitoria</div></div>
<div class='body'>
<div class='irow'>
  <div><div class='lbl'>Operador</div><div class='val'>{onome}</div></div>
  <div><div class='lbl'>Protocolo</div><div class='val'>{prot}</div></div>
  <div><div class='lbl'>Mês</div><div class='val'>{ma.replace('-',' ')}</div></div>
  <div><div class='lbl'>Data</div><div class='val'>{datetime.now().strftime('%d/%m/%Y')}</div></div>
</div>""")
    if erros:
        L.append("<div class='crit'><strong>MONITORIA ZERADA — Erro Crítico</strong><br>")
        for e in erros: L.append(f"• {e['nome']}: {e['desc']}<br>")
        L.append("</div>")
    L.append("<table><thead><tr><th>#</th><th>Critério</th><th>Peso</th><th>Resultado</th></tr></thead><tbody>")
    for c in crits:
        p="<span class='ok'>Passou</span>" if c["passou"] else "<span class='no'>Não passou</span>"
        L.append(f"<tr><td>{c['num']}</td><td>{c['nome']}</td><td>{c['peso']}</td><td>{p}</td></tr>")
    L.append("</tbody></table>")
    L.append(f"<div class='nbox'><div style='font-size:13px;color:#5a9a70'>Nota desta Monitoria</div><div class='nnum'>{nota:.0f}%</div></div>")
    L.append(f"<div class='mbox'><div><div class='lbl'>Média ({n_mon} monitorias)</div><div style='font-size:24px;font-weight:800'>{media:.1f}%</div></div><div><div class='lbl'>Pontuação</div><div style='font-size:24px;font-weight:800;color:#1a6b35'>{pontos} pts</div></div></div>")
    if obs: L.append(f"<div class='obs'><strong>Observações:</strong><br>{obs}</div>")
    L.append(f"</div><div class='foot'>iGreen Energy · {datetime.now().strftime('%d/%m/%Y às %H:%M')}</div></body></html>")
    return "".join(L)

# ── LOGIN ──────────────────────────────────────
def tela_login():
    c1,c2,c3=st.columns([1,1.2,1])
    with c2:
        st.markdown("""<div style="background:#003318;border-radius:16px;padding:40px 32px;box-shadow:0 8px 32px rgba(0,0,0,0.3);border:1px solid #005a25">
        <div style="text-align:center;padding:0 0 28px">
            <div style="width:64px;height:64px;background:linear-gradient(135deg,#1a6b35,#2daf5c);border-radius:16px;display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:32px;color:white;margin-bottom:14px">G</div>
            <div style="font-size:24px;font-weight:800;color:#ffffff;margin-bottom:4px">iGreen Performance</div>
            <div style="width:36px;height:2px;background:#00c853;margin:6px auto 10px"></div>
            <p style="color:#5a9a70;font-size:11px;text-transform:uppercase;letter-spacing:2px;margin:0">Painel de Gestão de Inadimplência</p>
        </div>""",unsafe_allow_html=True)
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px'>USUÁRIO</p>",unsafe_allow_html=True)
        usuario=st.text_input("u",placeholder="seu usuário",label_visibility="collapsed")
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px;margin-top:12px'>SENHA</p>",unsafe_allow_html=True)
        senha=st.text_input("s",type="password",placeholder="••••••••",label_visibility="collapsed")
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if st.button("Entrar",use_container_width=True):
            uid = usuario.lower().strip()
            u = USUARIOS.get(uid)
            if u:
                senha_correta = buscar_senha_usuario(uid)
                if senha_correta and senha.strip() == senha_correta:
                    st.session_state.usuario={"id":uid,**u}; st.rerun()
                else: st.error("Usuário ou senha incorretos.")
            else: st.error("Usuário ou senha incorretos.")
        st.markdown('<p style="text-align:center;color:#1a4d2e;font-size:11px;margin-top:24px">iGreen Energy © 2026</p>',unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────
def render_sidebar():
    u=st.session_state.usuario
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
                <div style="width:38px;height:38px;background:linear-gradient(135deg,#1a6b35,#2daf5c);border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:20px;color:white">G</div>
                <div>
                    <div style="color:#ffffff;font-weight:700;font-size:14px">i<span style='color:#2daf5c'>Green</span></div>
                    <div style="color:#5a9a70;font-size:10px;text-transform:uppercase;letter-spacing:1px">Performance</div>
                </div>
            </div>
            <div style="background:rgba(0,200,83,0.1);border:1px solid rgba(0,200,83,0.2);border-radius:8px;padding:10px 12px;margin-bottom:16px">
                <div style="color:#00c853;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px">{'Diretoria' if u['role']=='diretor' else 'Admin' if u['role']=='admin' else 'Gestor'}</div>
                <div style="color:#ffffff;font-size:14px;font-weight:600;margin-top:2px">{u['nome']}</div>
            </div>
        </div><hr>
        """,unsafe_allow_html=True)
        st.markdown("<p style='font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#5a9a70;margin-bottom:4px'>PERÍODO</p>",unsafe_allow_html=True)
        anos=get_anos_disponiveis()
        ano=st.selectbox("Ano",anos,label_visibility="collapsed")
        meses=get_todos_meses_ano(int(ano))
        mes_labels=[m.split("-")[0] for m in meses]
        mes_sel=st.selectbox("Mês",mes_labels,index=datetime.now().month-1,label_visibility="collapsed")
        mes_ano=f"{mes_sel}-{ano}"
        st.markdown("<hr>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#5a9a70;margin-bottom:4px'>NAVEGAÇÃO</p>",unsafe_allow_html=True)
        if u["role"]=="diretor":
            pags=["Quadro de Resultados","Visualização RCA","Análise de Projeção","Monitorias","Análise de Inadimplência"]
        elif u["role"]=="admin":
            pags=["Quadro de Resultados","Lançamento","Visualização RCA","Análise de Projeção","Monitorias","Upload de Bases","Análise de Inadimplência","Operadores","Metas","Critérios"]
        else:
            pags=["Quadro de Resultados","Lançamento","Análise de Projeção","Monitorias","Upload de Bases","Análise de Inadimplência","Operadores","Metas"]
        pag=st.radio("",pags,label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)

        # ── MINHA CONTA
        with st.expander("⚙️ Minha Conta"):
            st.markdown("<p style='font-size:11px;color:#a5d6a7;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Trocar Senha</p>",unsafe_allow_html=True)
            senha_at  = st.text_input("Senha atual",  type="password", key="conta_senha_at",  placeholder="••••••••")
            senha_nova = st.text_input("Nova senha",   type="password", key="conta_senha_nova", placeholder="mín. 8 caracteres")
            senha_conf = st.text_input("Confirmar nova senha", type="password", key="conta_senha_conf", placeholder="repita a nova senha")
            if st.button("Salvar Nova Senha", use_container_width=True, key="btn_trocar_senha"):
                uid = u["id"]
                senha_correta = buscar_senha_usuario(uid)
                if not senha_at: st.error("Digite a senha atual.")
                elif senha_at != senha_correta: st.error("Senha atual incorreta.")
                elif len(senha_nova) < 8: st.error("Nova senha deve ter pelo menos 8 caracteres.")
                elif senha_nova != senha_conf: st.error("Confirmação não confere.")
                else:
                    salvar_senha_usuario(uid, senha_nova)
                    st.success("Senha alterada com sucesso!")

        if st.button("Sair",use_container_width=True):
            del st.session_state.usuario; st.rerun()
    return mes_ano,pag

# ── OPERADORES ─────────────────────────────────
def pagina_operadores():
    u=st.session_state.usuario
    header_page("Operadores","Gerencie os operadores da equipe")
    eq=seletor_equipe(u["equipe"])
    with st.expander("Cadastrar Novo Operador",expanded=False):
        c1,c2,c3=st.columns([3,1,1])
        with c1: nn=st.text_input("Nome",placeholder="Nome completo")
        with c2: np=st.checkbox("Pleno")
        with c3:
            st.markdown("<div style='margin-top:28px'>",unsafe_allow_html=True)
            if st.button("Cadastrar",use_container_width=True):
                if nn.strip(): salvar_operador(eq,nn.strip(),np); st.success(f"{nn} cadastrado!"); st.rerun()
                else: st.error("Digite o nome.")
            st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("---")
    ops=buscar_operadores(eq)
    if not ops:
        st.info("Nenhum operador cadastrado.")
        padrao=OPERADORES_PADRAO.get(eq,[])
        if padrao:
            if st.button("Importar Operadores Padrão",use_container_width=True):
                for nome,pleno in padrao:
                    oid=re.sub(r'[^a-z0-9]','-',nome.lower().strip())
                    oid=re.sub(r'-+','-',oid).strip('-')
                    oid=f"{eq[:3]}-{oid}"[:40]
                    if not get_db().operadores.find_one({"_id":oid}):
                        get_db().operadores.insert_one({"_id":oid,"equipeId":eq,"nome":nome,"pleno":pleno,"criadoEm":datetime.now()})
                st.success("Importados!"); st.rerun()
        return
    st.markdown(f"**{len(ops)} operadores — Equipe {EQUIPES[eq]['nome']}**")
    for op in ops:
        c1,c2,c3,c4=st.columns([3,1,1,1])
        with c1: nn=st.text_input("n",value=op["nome"],label_visibility="collapsed",key=f"n_{op['_id']}")
        with c2: np=st.checkbox("Pleno",value=op.get("pleno",False),key=f"p_{op['_id']}")
        with c3:
            if st.button("Salvar",key=f"s_{op['_id']}"): atualizar_operador(op["_id"],nn,np); st.success("Salvo!"); st.rerun()
        with c4:
            if st.button("Excluir",key=f"d_{op['_id']}"): excluir_operador(op["_id"]); st.rerun()

# ── METAS ──────────────────────────────────────
def pagina_metas(ma):
    u=st.session_state.usuario
    header_page("Metas",ma.replace("-"," "))
    eq=seletor_equipe(u["equipe"])
    ops=buscar_operadores(eq)
    if not ops: st.warning("Cadastre operadores primeiro."); return
    st.markdown("### Meta da Gestora")
    mg_doc=buscar_meta_gestora(ma,eq)
    c1,c2,c3=st.columns([2,1,1])
    with c1: mg_val=st.number_input("Meta Base (R$)",min_value=0.0,step=1000.0,format="%.2f",value=float(mg_doc.get("metaGestora",0)),key="mg_val")
    with c2: tpct=st.number_input("Target (%)",min_value=100,max_value=200,value=int(mg_doc.get("targetPct",125)),key="tpct")
    with c3: st.markdown(f"<div style='padding-top:28px;color:#2daf5c;font-weight:700;font-size:16px'>{fmt_brl(mg_val*(tpct/100))}</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Metas por Operador")
    ms=buscar_metas_equipe(ma,eq); mn={}
    for op in ops:
        c1,c2=st.columns([3,2])
        with c1: st.markdown(f"<div style='padding-top:10px;color:#e0f0e8'>{'[P] ' if op.get('pleno') else ''}{op['nome']}</div>",unsafe_allow_html=True)
        with c2: mn[op["_id"]]=st.number_input("m",label_visibility="collapsed",min_value=0.0,step=100.0,format="%.2f",value=float(ms.get(op["_id"],0)),key=f"mg_{ma}_{op['_id']}")
    st.markdown("---")
    if st.button("Salvar Metas",use_container_width=True):
        for oid,v in mn.items(): salvar_meta_operador(ma,eq,oid,v)
        salvar_meta_gestora(ma,eq,mg_val,tpct)
        st.success("Metas salvas!"); st.rerun()

# ── LANÇAMENTO ─────────────────────────────────
def pagina_lancamento(ma):
    u=st.session_state.usuario
    header_page("Lançamento de Resultado",ma.replace("-"," "))
    eq=seletor_equipe(u["equipe"])
    ops=buscar_operadores(eq)
    if not ops: st.warning("Cadastre operadores primeiro."); return
    ms=buscar_metas_equipe(ma,eq)
    if st.session_state.get("ultimo_salvo"):
        st.success(st.session_state.ultimo_salvo)
        st.session_state.ultimo_salvo=""
    st.markdown("### Configuração do Lançamento")
    c1,c2,c3=st.columns([2,1,1])
    with c1:
        hoje=date.today()
        data_sel=st.date_input("Data do Resultado *",value=hoje,min_value=date(hoje.year,1,1),max_value=date(hoje.year,12,31),key=f"data_{eq}_{ma}")
        eh_fech=st.checkbox("Fechamento do Mês",key=f"fech_{eq}_{ma}")
    with c2:
        dt=st.number_input("Dias Trabalhados *",min_value=0,max_value=31,value=0,key=f"dt_{eq}_{ma}")
    with c3:
        td=st.number_input("Total Dias do Mês *",min_value=0,max_value=31,value=0,key=f"td_{eq}_{ma}")
    st.markdown("<p style='color:#81c784;font-size:11px;margin-top:4px'>* Campos obrigatórios — preenchidos a cada lançamento</p>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Valores por Operador")
    cols_h=st.columns([3,2,2])
    cols_h[0].markdown("**Operador**"); cols_h[1].markdown("**Meta**"); cols_h[2].markdown("**Valor Recebido (R$)**")
    vi={}
    for op in ops:
        meta=float(ms.get(op["_id"],0))
        c1,c2,c3=st.columns([3,2,2])
        with c1: st.markdown(f"<div style='padding-top:10px;color:#e0f0e8;font-weight:500'>{'★ ' if op.get('pleno') else ''}{op['nome']}</div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div style='padding-top:10px;color:#5a9a70;font-size:13px'>{fmt_brl(meta) if meta>0 else '—'}</div>",unsafe_allow_html=True)
        with c3: vi[op["_id"]]=st.number_input("v",label_visibility="collapsed",min_value=0.0,step=100.0,format="%.2f",key=f"op_{eq}_{ma}_{op['_id']}")
    tc=sum(vi.values())
    st.markdown("---")
    st.markdown(f"<div style='background:#0a2414;border-radius:8px;padding:12px 16px;margin-bottom:16px'><span style='color:#5a9a70;font-size:11px'>TOTAL COM INTERAÇÃO</span><br><span style='color:#2daf5c;font-size:20px;font-weight:700'>{fmt_brl(tc)}</span></div>",unsafe_allow_html=True)
    if st.button("Salvar Lançamento",use_container_width=True,key=f"btn_{eq}_{ma}"):
        errs=[]
        if dt==0: errs.append("Dias Trabalhados é obrigatório.")
        if td==0: errs.append("Total de Dias do Mês é obrigatório.")
        if not data_sel: errs.append("Data do Resultado é obrigatória.")
        if tc==0: errs.append("Preencha pelo menos um valor de operador.")
        if errs:
            for e in errs: st.error(e)
        else:
            label="Fechamento do Mês" if eh_fech else data_sel.strftime("%d/%m/%Y")
            ag={op["_id"]:{"valorRecebido":vi[op["_id"]],"nome":op["nome"]} for op in ops}
            criar_lancamento(ma,eq,str(data_sel),label,ag,tc,0,dt,td)
            st.session_state.ultimo_salvo=f"Lançamento de {label} salvo! Total: {fmt_brl(tc)}"
            st.rerun()
    st.markdown("---")
    lancs=buscar_lancamentos(ma,eq)
    if lancs:
        st.markdown("<p style='color:#81c784;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Lançamentos do mês</p>",unsafe_allow_html=True)
        for lanc in reversed(lancs):
            soma=sum(float(v.get("valorRecebido",0) if isinstance(v,dict) else v) for v in lanc.get("agentes",{}).values())
            with st.expander(f"{lanc.get('label','')} — {fmt_brl(soma)}"):
                rows=[{"Operador":op["nome"],"Valor":fmt_brl(get_val_op(lanc.get("agentes",{}),op["_id"],op["nome"]))} for op in ops]
                st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                if st.button("Excluir",key=f"del_{lanc['_id']}"): excluir_lancamento(lanc["_id"]); st.rerun()

# ── QUADRO DE RESULTADOS ───────────────────────
def pagina_quadro(ma):
    u=st.session_state.usuario
    is_dir=u["role"]=="diretor"; is_adm=u["role"]=="admin"
    eqs=list(EQUIPES.keys()) if (is_dir or is_adm) else [u["equipe"]]
    header_page("Quadro de Resultados",ma.replace("-"," "))
    for eq in eqs:
        ops=buscar_operadores(eq); lancs=buscar_lancamentos(ma,eq)
        if not lancs: continue
        ul=lancs[0]; mg_doc=buscar_meta_gestora(ma,eq); mops=buscar_metas_equipe(ma,eq)
        mg=float(mg_doc.get("metaGestora",0))
        tc=sum(float(v.get("valorRecebido",0)) for v in ul.get("agentes",{}).values() if isinstance(v,dict))
        dt=int(ul.get("diasTrabalhados",0)); td=int(ul.get("totalDias",22))
        proj=calc_projecao(tc,dt,td); pct=( tc/mg*100) if mg>0 else 0
        up=buscar_ultimo_processamento(ma,eq)
        vg=float(up.get("valorElegivel",ul.get("valorGeral",0)))
        sem=max(0,vg-tc)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid #00c853;box-shadow:0 2px 12px rgba(0,0,0,0.15)">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <div style="font-size:16px;font-weight:700;color:#ffffff">Equipe {EQUIPES[eq]['nome']} · {ul.get('label','')}</div>
                <div style="text-align:center"><div style="color:#5a9a70;font-size:10px;text-transform:uppercase">% Meta</div>
                    <div style="color:{cor_pct(pct)};font-size:22px;font-weight:800">{pct:.1f}%</div></div>
            </div>
            <div style="display:flex;gap:24px;margin-top:12px;flex-wrap:wrap">
                <div><span style="color:#5a9a70;font-size:11px">COM INTERAÇÃO</span><br><span style="color:#2daf5c;font-weight:700;font-size:15px">{fmt_brl(tc)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">SEM INTERAÇÃO</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(sem)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">META</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(mg)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(proj)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">DIAS</span><br><span style="color:#e0f0e8;font-weight:600">{dt}/{td}</span></div>
            </div>
        </div>""",unsafe_allow_html=True)
        # Diretor: oculta operadores por padrão
        show=True
        if is_dir:
            k=f"show_ops_{eq}"
            if k not in st.session_state: st.session_state[k]=False
            if st.button(f"{'Ocultar' if st.session_state[k] else 'Exibir'} Operadores — {EQUIPES[eq]['nome']}",key=f"btn_ops_{eq}"):
                st.session_state[k]=not st.session_state[k]; st.rerun()
            show=st.session_state[k]
        if show and ops:
            rows=[]
            for op in ops:
                v=get_val_op(ul.get("agentes",{}),op["_id"],op["nome"])
                meta=float(mops.get(op["_id"],0)); po=calc_projecao(v,dt,td); pc=(v/meta*100) if meta>0 else 0
                rows.append({"Status":status_pct(pc) if meta>0 else "—","Operador":op["nome"]+(" ★" if op.get("pleno") else ""),"Recebido":fmt_brl(v) if v>0 else "—","Meta":fmt_brl(meta) if meta>0 else "—","% Meta":f"{pc:.1f}%" if meta>0 else "—","Projeção":fmt_brl(po) if po>0 else "—","_v":v})
            df=pd.DataFrame(rows).sort_values("_v",ascending=False).drop(columns=["_v"]).reset_index(drop=True)
            df.index=range(1,len(df)+1)
            st.dataframe(df,use_container_width=True,height=min(600,(len(df)+1)*38+40))
        st.markdown("---")
    if st.button("Exportar Excel"):
        out=io.BytesIO()
        with pd.ExcelWriter(out,engine="xlsxwriter") as w:
            for eq in eqs:
                ops_e=buscar_operadores(eq); lancs_e=buscar_lancamentos(ma,eq)
                if not ops_e or not lancs_e: continue
                ul=lancs_e[0]; me=buscar_metas_equipe(ma,eq)
                rows=[{"Operador":op["nome"],"Recebido":get_val_op(ul.get("agentes",{}),op["_id"],op["nome"]),"Meta":float(me.get(op["_id"],0))} for op in ops_e]
                pd.DataFrame(rows).to_excel(w,sheet_name=EQUIPES[eq]["nome"],index=False)
        st.download_button("Baixar Excel",data=out.getvalue(),file_name=f"iGreen_{ma}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── MONITORIAS ─────────────────────────────────
def pagina_monitorias(ma):
    u=st.session_state.usuario
    header_page("Monitorias","Avaliação de qualidade · Inadimplência Comercial")
    if u["role"]=="diretor": pagina_monitorias_diretor(ma); return
    eq=seletor_equipe(u["equipe"]); ops=buscar_operadores(eq)
    if not ops: st.warning("Cadastre operadores primeiro."); return
    if "mon_op_sel" not in st.session_state: st.session_state.mon_op_sel=None
    if "mon_modo"   not in st.session_state: st.session_state.mon_modo=None

    if st.session_state.mon_op_sel is None:
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px'><div style='color:#81c784;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600'>Selecione um operador</div><div style='color:#a5d6a7;font-size:12px'>{len(ops)} operadores · {ma.replace('-',' ')}</div></div>",unsafe_allow_html=True)
        for i in range(0,len(ops),4):
            cols=st.columns(4)
            for j,op in enumerate(ops[i:i+4]):
                media,n=calc_media_operador(op["_id"],ma)
                st_txt,st_cor,st_bg=get_status_media(media)
                ini=get_iniciais(op["nome"]); cini=get_cor_inicial(op["nome"])
                with cols[j]:
                    st.markdown(f"""<div style="background:#ffffff;border:1px solid #c8e6c9;border-radius:12px;padding:16px;text-align:center;margin-bottom:8px">
                        <div style="width:48px;height:48px;background:{cini};border-radius:50%;display:inline-flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:16px;margin-bottom:8px">{ini}</div>
                        <div style="color:#1b5e20;font-weight:700;font-size:13px;margin-bottom:6px">{op['nome']}{'  ★' if op.get('pleno') else ''}</div>
                        <div style="background:{st_bg};color:{st_cor};font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;display:inline-block;margin-bottom:6px">{st_txt}</div>
                        <div style="color:#555;font-size:12px">Média: <strong style="color:{st_cor}">{media:.1f}%</strong></div>
                        <div style="color:#888;font-size:11px">{n} monitoria{'s' if n!=1 else ''} no mês</div>
                    </div>""",unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        if st.button("+ Nova",key=f"nova_{op['_id']}",use_container_width=True):
                            st.session_state.mon_op_sel=op; st.session_state.mon_modo="nova"; st.rerun()
                    with c2:
                        if st.button("Histórico",key=f"hist_{op['_id']}",use_container_width=True):
                            st.session_state.mon_op_sel=op; st.session_state.mon_modo="historico"; st.rerun()
        return

    op=st.session_state.mon_op_sel
    media_op,n_op=calc_media_operador(op["_id"],ma)
    st_txt,st_cor,st_bg=get_status_media(media_op)
    ini=get_iniciais(op["nome"]); cini=get_cor_inicial(op["nome"])
    st.markdown(f"""<div style="background:#ffffff;border:1px solid #c8e6c9;border-radius:12px;padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:16px">
        <div style="width:52px;height:52px;background:{cini};border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:18px;flex-shrink:0">{ini}</div>
        <div style="flex:1"><div style="color:#1b5e20;font-weight:700;font-size:16px">{op['nome']}</div><div style="color:#555;font-size:12px;margin-top:2px">{ma.replace('-',' ')}</div></div>
        <div style="display:flex;gap:20px;text-align:center">
            <div><div style="color:#666;font-size:10px;text-transform:uppercase">Média</div><div style="color:{st_cor};font-size:20px;font-weight:800">{media_op:.1f}%</div></div>
            <div><div style="color:#666;font-size:10px;text-transform:uppercase">Status</div><div style="background:{st_bg};color:{st_cor};font-size:12px;font-weight:600;padding:4px 10px;border-radius:20px;margin-top:2px">{st_txt}</div></div>
            <div><div style="color:#666;font-size:10px;text-transform:uppercase">Monitorias</div><div style="color:#1b5e20;font-size:20px;font-weight:800">{n_op}</div></div>
        </div>
    </div>""",unsafe_allow_html=True)
    if st.button("← Voltar"): st.session_state.mon_op_sel=None; st.session_state.mon_modo=None; st.rerun()
    st.markdown("---")
    t1,t2=st.tabs(["Nova Monitoria","Monitorias do Mês"])

    with t1:
        semana=st.selectbox("Qual monitoria é esta?",SEMANAS_MONITORIA,key="semana_sel")
        # Aviso se já existe
        monts_op=[m for m in buscar_monitorias_equipe(eq,ma) if m["opId"]==op["_id"]]
        ja_tem=[m for m in monts_op if m.get("semana_mon")==semana]
        if ja_tem:
            st.markdown(f"""<div style="background:#ffebee;border:1px solid #ef9a9a;border-radius:8px;padding:12px 16px;margin-bottom:12px;border-left:4px solid #e53935">
                <span style="color:#c62828;font-weight:700;font-size:13px">Atenção: já existe uma monitoria registrada para "{semana}" deste operador neste mês. Você pode salvar mesmo assim, mas ficará como ocorrência adicional.</span>
            </div>""",unsafe_allow_html=True)
        prot=st.text_input("Protocolo da Ligação",placeholder="Ex: 20260520-001",key="prot_input")
        obs=st.text_area("Observações",placeholder="Anotações...",height=70,key="obs_input")
        st.markdown("---")
        st.markdown("### Erros Críticos — Zera a Monitoria")
        erros_m=[]; c1,c2=st.columns(2)
        for i,ec in enumerate(get_erros_criticos()):
            with (c1 if i%2==0 else c2):
                if st.checkbox(f"{ec['nome']} — {ec['desc']}",key=f"ec_{ec['id']}"): erros_m.append(ec)
        st.markdown("---")
        st.markdown("### Critérios de Avaliação")
        zerada=len(erros_m)>0; crits_r=[]; nota=0 if zerada else 100
        if zerada:
            st.error("MONITORIA ZERADA — Erro crítico marcado!")
            for c in get_criterios(): crits_r.append({**c,"passou":False})
        else:
            for crit in get_criterios():
                ct="#c62828" if crit["obrigatorio"] else "#1b5e20"
                cb="#ef9a9a" if crit["obrigatorio"] else "#a5d6a7"
                bg="#fff5f5" if crit["obrigatorio"] else "#e8f5e9"
                ih="".join([f"<div style='font-size:13px;color:{'#b71c1c' if 'obrigatório' in it.lower() else '#333'};font-weight:{'700' if 'obrigatório' in it.lower() else '400'};padding:3px 0 3px 12px;border-left:2px solid {'#ef9a9a' if 'obrigatório' in it.lower() else '#c8e6c9'};margin-bottom:4px'>• {it}</div>" for it in crit["itens"]])
                st.markdown(f"""<div style="background:{bg};border:1px solid {cb};border-radius:10px;padding:14px 18px;margin-bottom:10px">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                        <span style="color:{ct};font-weight:700;font-size:15px">{crit['num']} {crit['nome']}</span>
                        <span style="background:rgba(0,0,0,0.06);color:{ct};padding:3px 12px;border-radius:20px;font-size:12px;font-weight:600">Peso {crit['peso']} {'— Obrigatório' if crit['obrigatorio'] else ''}</span>
                    </div><div style="margin-bottom:10px">{ih}</div></div>""",unsafe_allow_html=True)
                passou=st.checkbox(f"{crit['num']} {crit['nome']} — passou",key=f"cr_{crit['id']}",value=True)
                if not passou: nota-=crit["peso"]
                crits_r.append({**crit,"passou":passou})
        nota=max(0,nota)
        cn="#2e7d32" if nota>=80 else "#f57f17" if nota>=60 else "#c62828"
        st.markdown(f"""<div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:12px;padding:16px 24px;text-align:center;margin:16px 0">
            <div style="color:#2e7d32;font-size:11px;text-transform:uppercase;letter-spacing:1px">Nota desta Monitoria</div>
            <div style="color:{cn};font-size:44px;font-weight:800;margin:6px 0">{nota:.0f}%</div>
            <div style="color:#555;font-size:12px">{semana}</div>
        </div>""",unsafe_allow_html=True)
        sk=f"mon_salvo_{op['_id']}_{semana}_{ma}"
        if st.session_state.get(sk):
            st.success("Monitoria já salva! Selecione outro operador ou semana para continuar.")
        else:
            if st.button("Salvar Monitoria",use_container_width=True):
                if not prot.strip(): st.error("Preencha o protocolo da ligação!")
                else:
                    salvar_monitoria(eq,op["_id"],op["nome"],prot,obs,crits_r,erros_m,nota,ma,semana=semana)
                    st.session_state[sk]=True
                    mm,nm=calc_media_operador(op["_id"],ma)
                    st.success(f"Salva! Nota: {nota:.0f}% | Média: {mm:.1f}% | Pontos: {calc_pontos(mm)}")
                    html=gerar_pdf_monitoria(op["nome"],prot,obs,crits_r,erros_m,nota,mm,nm,ma)
                    b64=base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64}" download="Monitoria_{op["nome"].replace(" ","_")}_{prot}.html" style="display:inline-block;background:#00c853;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:8px">Baixar PDF</a>',unsafe_allow_html=True)

    with t2:
        monts2=[m for m in buscar_monitorias_equipe(eq,ma) if m["opId"]==op["_id"]]
        if not monts2: st.info(f"Nenhuma monitoria para {op['nome']} em {ma.replace('-',' ')}.")
        else:
            st.markdown(f"**{len(monts2)} monitoria(s)**")
            for m in monts2:
                nm=float(m.get("nota",0)); cm="#2e7d32" if nm>=80 else "#f57f17" if nm>=60 else "#c62828"
                st.markdown(f"""<div style="background:#ffffff;border:1px solid #c8e6c9;border-radius:10px;padding:14px 18px;margin-bottom:8px;border-left:4px solid {cm}">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                        <div><div style="color:#1b5e20;font-weight:600;font-size:14px">{m.get('semana_mon','—')}</div>
                            <div style="color:#555;font-size:12px;margin-top:2px">Protocolo: <strong>{m.get('protocolo','—')}</strong> · {str(m.get('criadoEm',''))[:10]}</div></div>
                        <div style="text-align:center"><div style="font-size:10px;color:#666;text-transform:uppercase">Nota</div>
                            <div style="font-size:18px;font-weight:800;color:{cm}">{nm:.0f}%</div></div>
                    </div></div>""",unsafe_allow_html=True)
                with st.expander("Ver detalhes"):
                    ch="".join([f"<div style='display:flex;justify-content:space-between;padding:6px 12px;background:{'#f1f8f1' if c.get('passou',True) else '#fff5f5'};border-radius:6px;margin-bottom:4px;border-left:3px solid {'#2e7d32' if c.get('passou',True) else '#c62828'}'><span style='color:#333;font-size:13px'>{c.get('num','')} {c.get('nome','')}</span><span style='color:{'#2e7d32' if c.get('passou',True) else '#c62828'};font-weight:700;font-size:13px'>{'Passou' if c.get('passou',True) else 'Não passou'}</span></div>" for c in m.get("criterios",[])])
                    if ch: st.markdown(ch,unsafe_allow_html=True)
                    if m.get("observacao"): st.markdown(f"<div style='margin-top:8px;padding:8px 12px;background:#f9fbe7;border-radius:6px;border-left:3px solid #cddc39;color:#555;font-size:13px'><strong>Obs:</strong> {m['observacao']}</div>",unsafe_allow_html=True)
                cp,cd,_=st.columns([2,2,6])
                hp=gerar_pdf_monitoria(m["opNome"],m.get("protocolo",""),m.get("observacao",""),m.get("criterios",[]),m.get("errosCriticos",[]),nm,media_op,n_op,ma)
                b64=base64.b64encode(hp.encode()).decode()
                with cp: st.markdown(f'<a href="data:text/html;base64,{b64}" download="Mon_{m["opNome"].replace(" ","_")}.html" style="display:block;background:#00c853;color:white;text-align:center;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:600;font-size:13px">Baixar PDF</a>',unsafe_allow_html=True)
                with cd:
                    if st.button("Excluir",key=f"del_op_{m['_id']}"): excluir_monitoria(m["_id"]); st.rerun()

def pagina_monitorias_diretor(ma):
    st.markdown("### Visão Geral — Monitorias por Equipe")
    for eq in EQUIPES:
        ops=buscar_operadores(eq)
        if not ops: continue
        monts=buscar_monitorias_equipe(eq,ma)
        if not monts: continue
        medias={op["nome"]:calc_media_operador(op["_id"],ma) for op in ops}
        medias={k:v for k,v in medias.items() if v[1]>0}
        if not medias: continue
        me=sum(m[0] for m in medias.values())/len(medias)
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid #00c853">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="font-size:15px;font-weight:700;color:#ffffff">Equipe {EQUIPES[eq]['nome']}</div>
                <div style="text-align:right"><div style="color:#5a9a70;font-size:10px;text-transform:uppercase">Média da Equipe</div>
                    <div style="color:{cor_pct(me)};font-size:24px;font-weight:800">{me:.1f}%</div></div>
            </div></div>""",unsafe_allow_html=True)
        rows=[{"Operador":n,"Média":f"{m[0]:.1f}%","Monitorias":m[1],"Pontos":calc_pontos(m[0])} for n,m in sorted(medias.items(),key=lambda x:-x[1][0])]
        df=pd.DataFrame(rows); df.index=range(1,len(df)+1)
        st.dataframe(df,use_container_width=True); st.markdown("---")

# ── ANÁLISE DE PROJEÇÃO ────────────────────────
def pagina_analise_projecao(ma):
    u=st.session_state.usuario
    eqs=list(EQUIPES.keys()) if u["role"] in ["diretor","admin"] else [u["equipe"]]
    header_page("Análise de Projeção",f"Comparativo proporcional · {ma.replace('-',' ')}")
    idx=MESES_NOMES.index(ma.split("-")[0]); ano=int(ma.split("-")[1])
    ma_ant=f"{MESES_NOMES[11]}-{ano-1}" if idx==0 else f"{MESES_NOMES[idx-1]}-{ano}"
    st.markdown(f"<p style='color:#5a9a70'>Comparando <strong style='color:#2daf5c'>{ma.replace('-',' ')}</strong> vs <strong style='color:#e0f0e8'>{ma_ant.replace('-',' ')}</strong> — mesmo período proporcional</p>",unsafe_allow_html=True)
    st.markdown("---")
    for eq in eqs:
        ops=buscar_operadores(eq)
        if not ops: continue
        lat=buscar_lancamentos(ma,eq); lan=buscar_lancamentos(ma_ant,eq)
        if not lat: continue
        ul=lat[0]; dt=int(ul.get("diasTrabalhados",0)); td=int(ul.get("totalDias",22)); tc=float(ul.get("totalEquipe",0))
        proj_at=calc_projecao(tc,dt,td)
        ul_an=None; proj_an=0; dt_an=0; td_an=22
        if lan:
            ul_an=min(lan,key=lambda x:abs(int(x.get("diasTrabalhados",0))-dt))
            dt_an=int(ul_an.get("diasTrabalhados",0)); td_an=int(ul_an.get("totalDias",22))
            proj_an=calc_projecao(float(ul_an.get("totalEquipe",0)),dt_an,td_an)
        var=calc_variacao(proj_at,proj_an)
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a2414,#0d2e1a);border:1px solid #1a4d2e;border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:4px solid #00c853">
            <div style="font-size:15px;font-weight:700;color:#ffffff;margin-bottom:10px">Equipe {EQUIPES[eq]['nome']}</div>
            <div style="display:flex;gap:24px;flex-wrap:wrap">
                <div><span style="color:#5a9a70;font-size:11px">PROJEÇÃO ATUAL ({dt} dias)</span><br><span style="color:#2daf5c;font-weight:700;font-size:15px">{fmt_brl(proj_at)}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">MÊS ANT. ({dt_an} dias equiv.)</span><br><span style="color:#e0f0e8;font-weight:600">{fmt_brl(proj_an) if proj_an else '—'}</span></div>
                <div><span style="color:#5a9a70;font-size:11px">VARIAÇÃO</span><br><span style="color:{'#2daf5c' if (var or 0)>=0 else '#e03c3c'};font-weight:700">{'↑' if (var or 0)>=0 else '↓'} {f'{abs(var):.1f}%' if var is not None else '—'}</span></div>
            </div></div>""",unsafe_allow_html=True)
        rows=[]
        for op in ops:
            vat=get_val_op(ul.get("agentes",{}),op["_id"],op["nome"])
            van=get_val_op(ul_an.get("agentes",{}),op["_id"],op["nome"]) if ul_an else 0
            pat=calc_projecao(vat,dt,td); pan=calc_projecao(van,dt_an,td_an) if van>0 else 0
            vo=calc_variacao(pat,pan)
            rows.append({"Operador":("★ " if op.get("pleno") else "")+op["nome"],"Proj. Atual":fmt_brl(pat) if pat>0 else "—","Proj. Mês Ant.":fmt_brl(pan) if pan>0 else "—","Variação":f"{'↑' if (vo or 0)>=0 else '↓'} {abs(vo):.1f}%" if vo is not None else "—","_p":pat})
        df=pd.DataFrame(rows).sort_values("_p",ascending=False).drop(columns=["_p"]).reset_index(drop=True)
        df.index=range(1,len(df)+1)
        st.dataframe(df,use_container_width=True); st.markdown("---")

# ── VISUALIZAÇÃO RCA ───────────────────────────
def pagina_dashboard_executivo():
    header_page("Visualização RCA","Gestão de Inadimplência Comercial")
    mp=listar_meses_processados()
    if not mp: st.info("Nenhuma base processada ainda."); return
    c1,c2,c3=st.columns(3)
    with c1: mf=st.selectbox("Mês",["Todos"]+mp)
    with c2: ef=st.selectbox("Equipe",["Todas","luciano","deborah","tamires"])
    df=buscar_processamentos(None if mf=="Todos" else mf, None if ef=="Todas" else ef)
    if df.empty: st.warning("Nenhum dado."); return
    df["valor"]=pd.to_numeric(df["valor"],errors="coerce").fillna(0)
    with c3:
        forns=["Todas"]+sorted(df["fornecedora"].dropna().unique().tolist())
        ff=st.selectbox("Fornecedora",forns)
    if ff!="Todas": df=df[df["fornecedora"]==ff]
    st.markdown("---")
    elig=df[df["elegibilidade"]=="Elegível"]; nelig=df[df["elegibilidade"]=="Não Elegível"]; nd=df[df["elegibilidade"]=="ND"]
    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric("Valor Recuperado",fmt_brl(elig["valor"].sum()))
    c2.metric("Clientes Únicos",f'{df["uc_cpf"].nunique():,}')
    c3.metric("Boletos",f'{len(df):,}')
    c4.metric("Elegíveis",f'{len(elig):,}')
    c5.metric("Não Elegíveis",f'{len(nelig):,}')
    c6.metric("ND",f'{len(nd):,}')
    st.markdown("---")
    t1,t2,t3,t4=st.tabs(["Aging","Fornecedoras","Evolução","Por Equipe"])
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
            ev=da[da["elegibilidade"]=="Elegível"].groupby("_mes_ano")["valor"].sum().reset_index()
            ev.columns=["Mês","Valor"]
            st.bar_chart(ev.sort_values("Mês").set_index("Mês"),color="#2daf5c")
    with t4:
        ed=df.groupby("_equipe").agg(Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique"),Valor=("valor","sum")).reset_index()
        ed["Equipe"]=ed["_equipe"].map(lambda x:EQUIPES.get(x,{}).get("nome",x))
        ed["Valor"]=ed["Valor"].apply(fmt_brl)
        st.dataframe(ed[["Equipe","Boletos","Clientes","Valor"]],use_container_width=True,hide_index=True)
    st.markdown("---")
    if st.button("Exportar Excel"):
        out=io.BytesIO()
        with pd.ExcelWriter(out,engine="xlsxwriter") as w:
            df.to_excel(w,sheet_name="Dados",index=False)
            elig.to_excel(w,sheet_name="Elegíveis",index=False)
        st.download_button("Baixar",data=out.getvalue(),file_name=f"iGreen_{mf}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── UPLOAD ─────────────────────────────────────
def pagina_upload(ma):
    u=st.session_state.usuario
    header_page("Upload de Bases Mensais","Planilha única com abas · Processamento automático")
    eq=seletor_equipe(u["equipe"] or "tamires")
    st.markdown("""<div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;padding:14px 18px;margin-bottom:16px">
        <div style="color:#1b5e20;font-weight:700;margin-bottom:8px">Como preparar a planilha:</div>
        <div style="color:#333;font-size:13px;line-height:1.8">Suba um único arquivo <strong>.xlsx</strong> com as abas:<br>
        <strong>PAGOS</strong> — obrigatória &nbsp;·&nbsp; <strong>CHAT</strong> — opcional &nbsp;·&nbsp; <strong>LIGAÇÕES</strong> — opcional &nbsp;·&nbsp; <strong>DISPAROS</strong> — opcional</div>
    </div>""",unsafe_allow_html=True)
    arq=st.file_uploader("Selecione a planilha (.xlsx)",type=["xlsx"],label_visibility="collapsed",key="base_unica")
    if arq:
        try:
            xls=pd.ExcelFile(arq)
            ah=" · ".join([f"<strong>{a}</strong>" for a in xls.sheet_names])
            arq.seek(0)
            st.markdown(f"<div style='background:#e8f5e9;border:1px solid #a5d6a7;border-radius:6px;padding:10px 14px;margin:8px 0;color:#2e7d32;font-size:13px'><strong>{arq.name}</strong> · Abas: {ah}</div>",unsafe_allow_html=True)
        except: pass
    st.markdown("---")
    if st.button("PROCESSAR MÊS",use_container_width=True):
        if not arq: st.error("Selecione a planilha antes de processar!"); return
        arq.seek(0)
        with st.spinner("Processando bases..."):
            df_res,erros,abas=processar_base_unica(arq,eq,ma)
        for e in erros: st.error(e)
        if df_res is not None and not df_res.empty:
            st.session_state["df_proc_temp"]=df_res; st.session_state["proc_eq"]=eq
            st.session_state["proc_ma"]=ma; st.session_state["proc_abas"]=abas
            st.rerun()
    if (st.session_state.get("df_proc_temp") is not None and
        st.session_state.get("proc_eq")==eq and st.session_state.get("proc_ma")==ma):
        df_res=st.session_state["df_proc_temp"]
        abas=st.session_state.get("proc_abas",[])
        elig=df_res[df_res["elegibilidade"]=="Elegível"]
        ve=elig["valor"].sum() if "valor" in elig.columns else 0
        ce=elig["uc_cpf"].nunique() if "uc_cpf" in elig.columns else 0
        if abas: st.info(f"Abas processadas: {', '.join(abas)}")
        st.success(f"{len(df_res):,} registros processados!")
        c1,c2,c3=st.columns(3)
        c1.metric("Valor Recebido",fmt_brl(ve)); c2.metric("Boletos Pagos",f"{len(elig):,}"); c3.metric("Clientes Pagos",f"{ce:,}")
        st.markdown("---")
        col1,col2=st.columns(2)
        with col1:
            if st.button("Salvar Resultado",use_container_width=True,key="btn_salvar_proc"):
                salvar_processamento(ma,eq,df_res); st.session_state["df_proc_temp"]=None; st.success("Resultado salvo!"); st.rerun()
        with col2:
            if st.button("Descartar",use_container_width=True,key="btn_desc"): st.session_state["df_proc_temp"]=None; st.rerun()
        st.markdown("---")
        cols=[ c for c in ["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging","diferenca_dias","primeiro_contato"] if c in df_res.columns]
        st.dataframe(df_res[cols].head(50) if cols else df_res.head(50),use_container_width=True)
        out=io.BytesIO()
        with pd.ExcelWriter(out,engine="xlsxwriter") as w:
            df_res.to_excel(w,sheet_name="Todos",index=False); elig.to_excel(w,sheet_name="Elegíveis",index=False)
        st.download_button("Baixar Excel",data=out.getvalue(),file_name=f"Resultado_{eq}_{ma}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("---")
    hist=buscar_historico_processamentos(ma,eq)
    hist=[p for p in hist if p.get("valorElegivel") is not None or p.get("label") is not None]
    if hist:
        st.markdown("<p style='color:#81c784;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Histórico</p>",unsafe_allow_html=True)
        for i,proc in enumerate(hist):
            ant=hist[i+1] if i+1<len(hist) else None
            v=float(proc.get("valorElegivel",0)); va=float(ant.get("valorElegivel",0)) if ant else 0
            diff=v-va if ant else 0; sinal="+" if diff>=0 else ""
            label=proc.get("label") or str(proc.get("criadoEm",""))[:16]
            with st.expander(f"{label} — {fmt_brl(v)}"):
                c1,c2,c3,c4=st.columns(4)
                c1.metric("Valor",fmt_brl(v)); c2.metric("Boletos",f"{proc.get('boletosElegiveis',0):,}"); c3.metric("Clientes",f"{proc.get('clientesElegiveis',0):,}")
                if ant: c4.metric("Evolução",f"{sinal}{fmt_brl(abs(diff))}")
                if proc.get("registros"):
                    dfh=pd.DataFrame(proc["registros"]); out2=io.BytesIO()
                    with pd.ExcelWriter(out2,engine="xlsxwriter") as w: dfh.to_excel(w,index=False)
                    st.download_button("Baixar Excel",data=out2.getvalue(),file_name=f"Base_{label.replace('/','-').replace(':','-')}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key=f"dl_{proc['_id']}")
                if st.button("Excluir",key=f"del_proc_{proc['_id']}"): excluir_processamento(proc["_id"]); st.rerun()

# ── ANÁLISE DE INADIMPLÊNCIA ───────────────────
def pagina_inadimplencia(ma):
    u=st.session_state.usuario
    is_dir=u["role"]=="diretor"; is_adm=u["role"]=="admin"
    header_page("Análise de Inadimplência","Taxa de recuperação por faixa e fornecedora")
    FAIXAS=["D30","D31-60","D61-90","D90+"]

    c1,c2,c3=st.columns(3)
    with c1:
        md=listar_meses_inadimplencia() or [ma]
        if ma not in md: md=[ma]+md
        ms=st.selectbox("Mês",md,key="inad_mes")
    with c2:
        fs=st.selectbox("Fornecedora",["Todas"]+FORNECEDORAS_TODAS,key="inad_forn")
    with c3:
        eq=seletor_equipe(u.get("equipe") or "tamires",key_suffix="_inad") if (is_adm or is_dir) else u["equipe"]

    st.markdown("---")
    doc=buscar_inadimplencia(ms,eq or "tamires")
    dados=doc.get("dados",{}) if doc else {}

    with st.expander("Subir planilha de inadimplência",expanded=not bool(dados)):
        st.markdown("<p style='color:#555;font-size:13px'>Suba a planilha com as abas por fornecedora. Quando as colunas forem mapeadas, os dados preenchem automaticamente.</p>",unsafe_allow_html=True)
        arq_i=st.file_uploader("Planilha de inadimplência (.xlsx)",type=["xlsx"],key="arq_inad")
        if arq_i and st.button("Processar planilha",key="btn_proc_inad"):
            st.info("Estrutura da planilha ainda sendo mapeada. Use a edição manual por enquanto e envie a planilha para conectarmos as colunas.")

    st.markdown("---")
    edit=st.checkbox("Editar manualmente",key="edit_inad")
    lista=FORNECEDORAS_TODAS if fs=="Todas" else [fs]

    st.markdown("""<style>
    .it{width:100%;border-collapse:collapse;font-size:11px}
    .it th{background:#1b5e20;color:#fff;padding:6px 8px;text-align:center;border:1px solid #145214;white-space:nowrap}
    .it th.thl{text-align:left}.it th.ths{background:#2e7d32;font-size:10px}
    .it td{border:1px solid #c8e6c9;padding:5px 8px;text-align:right;font-size:11px;color:#1b5e20;background:#fff}
    .it td.tdn{text-align:left;font-weight:600;background:#f1f8f1}
    .it td.tdp{color:#e53935;font-weight:600}.it td.tdf{color:#1565c0;font-weight:500}
    .it tr.trt td{background:#e8f5e9;font-weight:700}
    .it tr.trm td{background:#f9fbe7;font-size:10px;color:#555}
    </style>""",unsafe_allow_html=True)

    html='<div style="overflow-x:auto"><table class="it"><thead>'
    html+='<tr><th class="thl" rowspan="2">Fornecedoras</th>'
    for f in FAIXAS: html+=f'<th colspan="4">{f}</th>'
    html+='<th colspan="3">Total</th></tr><tr>'
    for _ in FAIXAS: html+='<th class="ths">Pagos R$</th><th class="ths">Vencidos R$</th><th class="ths">%Faixa</th><th class="ths">%Inad</th>'
    html+='<th class="ths">Pagos R$</th><th class="ths">Vencidos R$</th><th class="ths">%Inad Geral</th>'
    html+='</tr></thead><tbody>'

    tots={f:{"p":0,"v":0} for f in FAIXAS}; tots["T"]={"p":0,"v":0}
    for forn in lista:
        cor=CORES_FORN.get(forn,"#333"); fd=dados.get(forn,{})
        html+=f'<tr><td class="tdn"><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:{cor};margin-right:6px"></span>{forn}</td>'
        tp=tv=0
        for faixa in FAIXAS:
            p=float(fd.get(faixa,{}).get("pagos",0)); v=float(fd.get(faixa,{}).get("vencidos",0))
            pf=(p/(p+v)*100) if (p+v)>0 else 0; pi=(v/(p+v)*100) if (p+v)>0 else 0
            tots[faixa]["p"]+=p; tots[faixa]["v"]+=v; tp+=p; tv+=v
            html+=f'<td>{fmt_brl_td(p)}</td><td>{fmt_brl_td(v)}</td><td class="tdf">{pf:.1f}%</td><td class="tdp">{pi:.1f}%</td>'
        tots["T"]["p"]+=tp; tots["T"]["v"]+=tv
        pg=(tv/(tp+tv)*100) if (tp+tv)>0 else 0
        html+=f'<td>{fmt_brl_td(tp)}</td><td>{fmt_brl_td(tv)}</td><td class="tdp">{pg:.1f}%</td></tr>'

    html+='<tr class="trt"><td class="tdn">TOTAL</td>'
    for f in FAIXAS:
        tp2=tots[f]["p"]; tv2=tots[f]["v"]; pf2=(tp2/(tp2+tv2)*100) if (tp2+tv2)>0 else 0; pi2=(tv2/(tp2+tv2)*100) if (tp2+tv2)>0 else 0
        html+=f'<td>{fmt_brl_td(tp2)}</td><td>{fmt_brl_td(tv2)}</td><td class="tdf">{pf2:.1f}%</td><td class="tdp">{pi2:.1f}%</td>'
    tpt=tots["T"]["p"]; tvt=tots["T"]["v"]; pgt=(tvt/(tpt+tvt)*100) if (tpt+tvt)>0 else 0
    html+=f'<td>{fmt_brl_td(tpt)}</td><td>{fmt_brl_td(tvt)}</td><td class="tdp">{pgt:.1f}%</td></tr>'
    html+='</tbody></table></div>'
    st.markdown(html,unsafe_allow_html=True)

    # Rodapé
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
    cols_r=st.columns(4)
    for idx,f in enumerate(FAIXAS):
        tp2=tots[f]["p"]; tv2=tots[f]["v"]
        pf2=(tp2/(tp2+tv2)*100) if (tp2+tv2)>0 else 0; pi2=(tv2/(tp2+tv2)*100) if (tp2+tv2)>0 else 0
        with cols_r[idx]:
            st.markdown(f"""<div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:8px;padding:10px;text-align:center">
                <div style="font-size:11px;font-weight:600;color:#2e7d32;margin-bottom:6px">{f}</div>
                <div style="display:flex;justify-content:center;gap:16px">
                    <div><div style="font-size:9px;color:#555;text-transform:uppercase">%Faixa</div><div style="font-size:14px;font-weight:700;color:#1565c0">{pf2:.1f}%</div></div>
                    <div><div style="font-size:9px;color:#555;text-transform:uppercase">%Inad</div><div style="font-size:14px;font-weight:700;color:#e53935">{pi2:.1f}%</div></div>
                </div></div>""",unsafe_allow_html=True)

    if edit:
        st.markdown("---")
        st.markdown("### Edição Manual")
        nd={}
        for forn in lista:
            st.markdown(f"**{forn}**"); fd=dados.get(forn,{}); nd[forn]={}
            cols_e=st.columns(4)
            for idx_f,f in enumerate(FAIXAS):
                with cols_e[idx_f]:
                    st.markdown(f"<div style='font-size:11px;color:#2e7d32;font-weight:600;margin-bottom:4px'>{f}</div>",unsafe_allow_html=True)
                    p=st.number_input(f"Pagos {f}",min_value=0.0,step=100.0,format="%.2f",value=float(fd.get(f,{}).get("pagos",0)),key=f"ip_{forn}_{f}",label_visibility="collapsed")
                    st.markdown("<div style='font-size:10px;color:#555;margin-bottom:2px'>Pagos R$</div>",unsafe_allow_html=True)
                    v=st.number_input(f"Vencidos {f}",min_value=0.0,step=100.0,format="%.2f",value=float(fd.get(f,{}).get("vencidos",0)),key=f"iv_{forn}_{f}",label_visibility="collapsed")
                    st.markdown("<div style='font-size:10px;color:#e53935;margin-bottom:2px'>Vencidos R$</div>",unsafe_allow_html=True)
                    nd[forn][f]={"pagos":p,"vencidos":v}
            st.markdown("---")
        if st.button("Salvar Dados de Inadimplência",use_container_width=True):
            salvar_inadimplencia(ms,eq or "tamires",nd); st.success("Dados salvos!"); st.rerun()

    st.markdown("---")
    if st.button("Exportar Excel"):
        rows=[{"Fornecedora":f,**{f"{faixa} Pagos":float(dados.get(f,{}).get(faixa,{}).get("pagos",0)) for faixa in FAIXAS},**{f"{faixa} Vencidos":float(dados.get(f,{}).get(faixa,{}).get("vencidos",0)) for faixa in FAIXAS}} for f in lista]
        out=io.BytesIO()
        with pd.ExcelWriter(out,engine="xlsxwriter") as w: pd.DataFrame(rows).to_excel(w,index=False)
        st.download_button("Baixar Excel",data=out.getvalue(),file_name=f"Inadimplencia_{ms}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── CRITÉRIOS ─────────────────────────────────
def pagina_criterios():
    header_page("Critérios de Monitoria","Configure os critérios de avaliação")
    crits=get_criterios(); erros=get_erros_criticos()
    t1,t2=st.tabs(["Critérios de Avaliação","Erros Críticos"])
    with t1:
        st.markdown("**Alterações valem apenas para novas monitorias.**"); st.markdown("---")
        ce=[]
        for i,c in enumerate(crits):
            with st.expander(f"{c['num']} {c['nome']} — Peso {c['peso']}",expanded=False):
                col1,col2,col3=st.columns([3,1,1])
                with col1: nm=st.text_input("Nome",value=c["nome"],key=f"cn_{i}")
                with col2: ps=st.number_input("Peso",min_value=1,max_value=100,value=int(c["peso"]),key=f"cp_{i}")
                with col3: ob=st.checkbox("Obrigatório",value=c.get("obrigatorio",False),key=f"co_{i}")
                it=st.text_area("Itens (um por linha)",value="\n".join(c.get("itens",[])),height=100,key=f"ci_{i}")
                ce.append({"id":c["id"],"num":c["num"],"nome":nm,"peso":ps,"obrigatorio":ob,"itens":[x.strip() for x in it.split("\n") if x.strip()]})
        st.markdown("---")
        if st.button("Salvar Critérios",use_container_width=True): salvar_criterios(ce); st.success("Critérios salvos!"); st.rerun()
    with t2:
        st.markdown("**Erros que zeram a monitoria automaticamente.**"); st.markdown("---")
        ee=[]
        for i,e in enumerate(erros):
            col1,col2=st.columns([2,3])
            with col1: ne=st.text_input("Nome",value=e["nome"],key=f"en_{i}")
            with col2: de=st.text_input("Descrição",value=e["desc"],key=f"ed_{i}")
            ee.append({"id":e["id"],"nome":ne,"desc":de})
        st.markdown("---")
        col1,col2=st.columns(2)
        with col1:
            if st.button("Salvar Erros Críticos",use_container_width=True): salvar_erros_criticos(ee); st.success("Salvo!"); st.rerun()
        with col2:
            if st.button("Adicionar Erro",use_container_width=True):
                ee.append({"id":f"e{len(erros)+1}","nome":"Novo erro","desc":"Descrição"}); salvar_erros_criticos(ee); st.rerun()

# ── MAIN ───────────────────────────────────────
def main():
    if "ids_corrigidos" not in st.session_state:
        try: corrigir_ids_operadores()
        except: pass
        st.session_state.ids_corrigidos=True
    if "usuario" not in st.session_state: tela_login(); return
    ma,pag=render_sidebar()
    u=st.session_state.usuario
    if u["role"]=="diretor":
        if   "Quadro"        in pag: pagina_quadro(ma)
        elif "Visualização"  in pag: pagina_dashboard_executivo()
        elif "Projeção"      in pag: pagina_analise_projecao(ma)
        elif "Monitorias"    in pag: pagina_monitorias(ma)
        elif "Inadimplência" in pag: pagina_inadimplencia(ma)
    elif u["role"]=="admin":
        if   "Quadro"        in pag: pagina_quadro(ma)
        elif "Lançamento"    in pag: pagina_lancamento(ma)
        elif "Visualização"  in pag: pagina_dashboard_executivo()
        elif "Projeção"      in pag: pagina_analise_projecao(ma)
        elif "Monitorias"    in pag: pagina_monitorias(ma)
        elif "Upload"        in pag: pagina_upload(ma)
        elif "Inadimplência" in pag: pagina_inadimplencia(ma)
        elif "Operadores"    in pag: pagina_operadores()
        elif "Metas"         in pag: pagina_metas(ma)
        elif "Critérios"     in pag: pagina_criterios()
    else:
        if   "Quadro"        in pag: pagina_quadro(ma)
        elif "Lançamento"    in pag: pagina_lancamento(ma)
        elif "Projeção"      in pag: pagina_analise_projecao(ma)
        elif "Monitorias"    in pag: pagina_monitorias(ma)
        elif "Upload"        in pag: pagina_upload(ma)
        elif "Inadimplência" in pag: pagina_inadimplencia(ma)
        elif "Operadores"    in pag: pagina_operadores()
        elif "Metas"         in pag: pagina_metas(ma)

if __name__=="__main__":
    main()
