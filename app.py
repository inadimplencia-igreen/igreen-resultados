import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, date
import io
import base64
import re
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Inadimplência Performance", page_icon="logo.png", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* ── BASE — tema claro corporativo ── */
.stApp { background-color: #eef6ee !important; --text-color: #1a3a1a; --text-muted: #5a8a5a; --bg-card: #ffffff; --border-color: #c8e0c8; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #f5fbf5 !important;
    border-right: 1px solid #d0e8d0 !important;
}

/* ── Esconde label Menu do radio ── */
[data-testid="stSidebar"] .stRadio > div > p { display: none !important; }

/* ── SIDEBAR NAV — cards padronizados ── */
[data-testid="stSidebar"] .stRadio > div {
    gap: 3px !important;
    padding: 0 8px !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #2d4a2d !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    display: flex !important;
    align-items: center !important;
    border-radius: 8px !important;
    margin: 1px 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
    transition: all 0.15s !important;
    background: #ffffff !important;
    border: 1px solid #d8ead8 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    min-height: 40px !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #1a3a1a !important;
    background: #edf7ed !important;
    border-color: #2e7d32 !important;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: inherit !important;
    white-space: nowrap !important;
    font-size: 13px !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
    color: #ffffff !important;
    background: #2e7d32 !important;
    border-color: #2e7d32 !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(46,125,50,0.2) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e0e8e0 !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    border-top: 3px solid #2e7d32 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stMetricValue"] { color: #1a2e1a !important; font-size: 16px !important; font-weight: 700 !important; white-space: nowrap !important; overflow: visible !important; }
[data-testid="stMetricLabel"] { color: #5a8a5a !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }

/* ── BUTTONS ── */
.stButton > button {
    background: #f0f7f0 !important;
    color: #2e7d32 !important;
    border: 1px solid #c8e0c8 !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    padding: 6px 14px !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #2e7d32 !important;
    color: #ffffff !important;
    border-color: #2e7d32 !important;
}

/* ── TYPOGRAPHY ── */
h1 { color: #1a2e1a !important; font-size: 20px !important; font-weight: 700 !important; }
h2 { color: #2d4a2d !important; font-size: 16px !important; font-weight: 600 !important; }
h3 { color: #5a8a5a !important; font-size: 10px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 2px; }
p  { color: #1a3a1a !important; font-size: 13px; }
hr { border: none !important; border-top: 1px solid #e0e8e0 !important; margin: 14px 0 !important; }

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid #c8e0c8 !important;
    color: #1a2e1a !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 2px rgba(46,125,50,0.12) !important;
}
.stTextInput input::placeholder { color: #9ab89a !important; }

/* ── SELECTS ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid #c8e0c8 !important;
    color: #1a2e1a !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
.stSelectbox > div > div > div {
    color: #1a2e1a !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: calc(100% - 32px) !important;
}
[data-baseweb="select"] { background: #ffffff !important; }
[data-baseweb="select"] > div { background: #ffffff !important; color: #1a2e1a !important; }
[data-baseweb="select"] input { opacity: 0 !important; position: absolute !important; width: 0 !important; height: 0 !important; pointer-events: none !important; }
[data-baseweb="select"] svg { display: none !important; }
[data-baseweb="popover"] { background: #ffffff !important; border: 1px solid #c8e0c8 !important; border-radius: 8px !important; z-index: 99999 !important; }
[data-baseweb="menu"] { background: #ffffff !important; }
[role="option"] { background: #ffffff !important; color: #1a2e1a !important; padding: 8px 14px !important; }
[role="option"]:hover, [aria-selected="true"][role="option"] { background: #e8f5e8 !important; color: #1a2e1a !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f0f7f0 !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 3px !important;
    border: 1px solid #c8e0c8 !important;
}
.stTabs [data-baseweb="tab"] { color: #5a8a5a !important; border-radius: 6px !important; font-size: 12px !important; font-weight: 500 !important; padding: 7px 14px !important; }
.stTabs [aria-selected="true"] { background: #2e7d32 !important; color: #ffffff !important; }

/* ── CHECKBOXES ── */
.stCheckbox label { color: #2d4a2d !important; font-size: 13px !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > div {
    background: #f8fdf8 !important;
    border: 1.5px dashed #c8e0c8 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] * { color: #5a8a5a !important; }

/* ── ALERTS ── */
.stSuccess > div { background: #f0faf0 !important; border: 1px solid #c8e0c8 !important; color: #2e7d32 !important; border-radius: 8px !important; font-size: 13px !important; border-left: 3px solid #2e7d32 !important; }
.stWarning > div { background: #fffbf0 !important; border: 1px solid #f0e0a0 !important; color: #8a6a00 !important; border-radius: 8px !important; font-size: 13px !important; border-left: 3px solid #f0c000 !important; }
.stError > div { background: #fff5f5 !important; border: 1px solid #f0c0c0 !important; color: #c62828 !important; border-radius: 8px !important; font-size: 13px !important; border-left: 3px solid #c62828 !important; }
.stInfo > div { background: #f0f8ff !important; border: 1px solid #b0d0f0 !important; color: #1565c0 !important; border-radius: 8px !important; font-size: 13px !important; border-left: 3px solid #1565c0 !important; }

/* ── DATA TABLE ── */
[data-testid="stDataFrame"] { border: 1px solid #e0e8e0 !important; border-radius: 10px !important; background: #ffffff !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader { background: #f8fdf8 !important; border: 1px solid #c8e0c8 !important; border-radius: 8px !important; color: #2d4a2d !important; font-size: 13px !important; }
.streamlit-expanderContent { background: #ffffff !important; border: 1px solid #c8e0c8 !important; border-top: none !important; border-radius: 0 0 8px 8px !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #f0f7f0; }
::-webkit-scrollbar-thumb { background: #c8e0c8; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #2e7d32; }

/* ── Esconde ícones arrow do expander ── */
.streamlit-expanderHeader svg { display: none !important; }
.streamlit-expanderHeader [data-testid="stExpanderToggleIcon"] { display: none !important; }
details summary svg { display: none !important; }

/* ── HIDE STREAMLIT CHROME ── */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
button[data-testid="baseButton-header"] { display: none !important; }
.st-emotion-cache-1egp75k { display: none !important; }
[data-testid="stSidebarContent"] > div:first-child > div:first-child { display: none !important; }
button[kind="header"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.viewerBadge_container__1QSob { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

/* ── SIDEBAR SEMPRE VISÍVEL ── */
[data-testid="stSidebar"] { display: flex !important; visibility: visible !important; opacity: 1 !important; width: 260px !important; min-width: 260px !important; transform: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: flex !important; }

/* ── LAYOUT ── */
.block-container { padding: 2rem 2rem 2rem !important; max-width: 1200px !important; }
div[data-testid="stVerticalBlock"] label { color: #3a5a3a !important; font-size: 12px !important; }

/* ── FORNECEDORAS sem quebra ── */
.forn-nome { white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; max-width: 160px !important; display: inline-block !important; }
</style>
""", unsafe_allow_html=True)

LOGO_B64 = "data:image/webp;base64,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"

def _get_usuarios():
    def _s(key, fallback):
        try: return st.secrets["usuarios"][key]
        except: return fallback
    return {
        "tamires": {"senha": _s("tamires","9cd2r11QvOqD8a"), "equipe":"tamires","role":"admin",  "nome":"Tamires"},
        "luciano": {"senha": _s("luciano","TCLemDjWSGv!yz"), "equipe":"luciano","role":"gestor", "nome":"Luciano"},
        "deborah": {"senha": _s("deborah","L4f10IJo5bGJ3O"), "equipe":"deborah","role":"gestor", "nome":"Déborah"},
        "veloso":  {"senha": _s("veloso", "U2B!niJH7W96rL"), "equipe":None,    "role":"diretor","nome":"Veloso"},
        "moyara":  {"senha": _s("moyara", "ug8omeP4Cvt3nl"), "equipe":None,    "role":"diretor","nome":"Moyara"},
        "gabriel": {"senha": _s("gabriel","gabriel123"),   "equipe":"metcool","role":"gestor", "nome":"Gabriel"},
    }

USUARIOS = _get_usuarios()
EQUIPES = {
    "luciano":{"nome":"Luciano","cor":"#2daf5c"},
    "deborah":{"nome":"Déborah","cor":"#a855f7"},
    "tamires":{"nome":"Tamires","cor":"#f97316"},
    "metcool":{"nome":"Meet Call","cor":"#3b82f6"},
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
CRITERIOS_CHAT_PADRAO = [
    {"id":"cc1","num":"1º","nome":"Abertura e Identificação","peso":10,"itens":["Saudação adequada","Identificação correta do operador e da empresa"],"obrigatorio":False},
    {"id":"cc2","num":"2º","nome":"Comunicação e Postura","peso":15,"itens":["Clareza na comunicação","Tom respeitoso (sem pressão excessiva, ironia)","Ausência de gírias, vícios de linguagem ou informalidade excessiva","Não ameaçar ou constranger"],"obrigatorio":False},
    {"id":"cc3","num":"3º","nome":"Negociação/Conformidade","peso":40,"itens":["Apresentação clara de propostas","Seguir script de Retenção (incluir benefícios e disponibilidade das faturas dentro do aplicativo)","Escrita correta"],"obrigatorio":True},
    {"id":"cc4","num":"4º","nome":"Registro e Procedimentos","peso":20,"itens":["Registro correto no sistema","Classificação adequada do atendimento (tabulação)"],"obrigatorio":False},
    {"id":"cc5","num":"5º","nome":"Encerramento","peso":15,"itens":["Esclarecimento do acordo fechado","Agradecimento e cordialidade","Encerramento de atendimento"],"obrigatorio":False},
]
ERROS_CRITICOS_CHAT_PADRAO = [
    {"id":"ec1","nome":"Informação incorreta","desc":"Passou informação incorreta ao cliente"},
    {"id":"ec2","nome":"Postura ríspida","desc":"Agiu de forma ríspida ou ameaçadora"},
    {"id":"ec3","nome":"Linguagem agressiva","desc":"Linguagem agressiva por escrito"},
    {"id":"ec4","nome":"Ignorou mensagem","desc":"Ignorou mensagem/deixou sem resposta (Encerramento sem conclusão)"},
    {"id":"ec5","nome":"Desconto fora da regra","desc":"Ofereceu desconto fora da regra"},
    {"id":"ec6","nome":"Boleto inválido","desc":"Enviou boleto inválido e finalizou sem verificar"},
]
FAIXAS_PONTOS = [(0,70,0),(71,80,300),(81,90,500),(91,95,700),(96,99,1000),(100,100,1100)]
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
    "metcool":[("Leilson Gomes",False),("Hannah Vitoria",False),("Kesia Lima",False),("Renata Ribeiro",False),("Thayna Guerreiro Ferreira",False),("Kimberlyn da Silva",False),("Vitor Eder",False),("Laiza Teixeira",False),("Glaucio Fernandes",False),("Thais de Fatima",False),("Mayara Leal",False),("Ivone Coutinho",False),("Aline Cristine",False),("Anderson Soares da Silva",False),("Michelle Pereira",False),("Maria Ferreira",False),("Mariana Matias",False),("Jessica Faria Albertino Miranda Vieira",False),("Lorrane Moura",False),("Jennifer Edjane",False),("Haissa Batista",False),("Bruna de Barros Santanna",False)],
}
FORNECEDORAS_TODAS = ["COTESA/MOVE","ULTRA","VANTAGE","FARO","BOM FUTURO","SUNCLICK","ATUA","GEDISA","SUNNE","SOLATIO","EDP","FIT","GV","COMERC"]
FORNECEDORAS_POR_GESTOR = {
    "luciano": ["COMERC"],
    "tamires": ["VANTAGE","BOM FUTURO","COTESA/MOVE","SUNCLICK","FARO","ULTRA","GEDISA"],
    "deborah": ["SUNNE","SOLATIO","EDP","FIT","GV"],
    "metcool": ["COMERC"],
}
OPERADORES_MEETCALL = ['Leilson Gomes', 'Hannah Vitoria', 'Kesia Lima', 'Renata Ribeiro', 'Thayna Guerreiro Ferreira', 'Kimberlyn da Silva', 'Vitor Eder', 'Laiza Teixeira', 'Glaucio Fernandes', 'Thais de Fatima', 'Mayara Leal', 'Ivone Coutinho', 'Aline Cristine', 'Anderson Soares da Silva', 'Michelle Pereira', 'Maria Ferreira', 'Mariana Matias', 'Jessica Faria Albertino Miranda Vieira', 'Lorrane Moura', 'Jennifer Edjane', 'Haissa Batista', 'Bruna de Barros Santanna']
CORES_FORN = {"COTESA/MOVE":"#1b5e20","ULTRA":"#0d47a1","VANTAGE":"#e65100","FARO":"#b71c1c","BOM FUTURO":"#4a148c","SUNCLICK":"#004d40","ATUA":"#37474f","GEDISA":"#006064","SUNNE":"#f57f17","SOLATIO":"#4527a0","EDP":"#0277bd","FIT":"#2e7d32","GV":"#558b2f","COMERC":"#37474f"}

# ── MONGODB ────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(
        st.secrets["mongo"]["uri"],
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=15000,
        maxPoolSize=20,
        minPoolSize=2,
        retryWrites=True,
        w="majority"
    )
    return client[st.secrets["mongo"]["db"]]

def get_criterios():
    try:
        doc = get_db().configuracoes.find_one({"_id":"criterios_monitoria"})
        if doc and doc.get("criterios"): return doc["criterios"]
    except: pass
    return CRITERIOS_PADRAO

def salvar_criterios(c):
    get_db().configuracoes.update_one({"_id":"criterios_monitoria"},{"$set":{"_id":"criterios_monitoria","criterios":c,"atualizadoEm":datetime.now()}},upsert=True)

def get_criterios_chat():
    try:
        doc = get_db().configuracoes.find_one({"_id":"criterios_chat_monitoria"})
        if doc and doc.get("criterios"): return doc["criterios"]
    except: pass
    return CRITERIOS_CHAT_PADRAO

def salvar_criterios_chat(c):
    get_db().configuracoes.update_one({"_id":"criterios_chat_monitoria"},{"$set":{"_id":"criterios_chat_monitoria","criterios":c,"atualizadoEm":datetime.now()}},upsert=True)

def get_erros_criticos_chat():
    try:
        doc = get_db().configuracoes.find_one({"_id":"erros_criticos_chat_monitoria"})
        if doc and doc.get("erros"): return doc["erros"]
    except: pass
    return ERROS_CRITICOS_CHAT_PADRAO

def salvar_erros_criticos_chat(e):
    get_db().configuracoes.update_one({"_id":"erros_criticos_chat_monitoria"},{"$set":{"_id":"erros_criticos_chat_monitoria","erros":e,"atualizadoEm":datetime.now()}},upsert=True)

def get_erros_criticos():
    try:
        doc = get_db().configuracoes.find_one({"_id":"erros_criticos_monitoria"})
        if doc and doc.get("erros"): return doc["erros"]
    except: pass
    return ERROS_CRITICOS_PADRAO

def salvar_erros_criticos(e):
    get_db().configuracoes.update_one({"_id":"erros_criticos_monitoria"},{"$set":{"_id":"erros_criticos_monitoria","erros":e,"atualizadoEm":datetime.now()}},upsert=True)

def migrar_meetcall_para_luciano():
    try:
        db = get_db()
        for nome in OPERADORES_MEETCALL:
            oid_luc = re.sub(r'[^a-z0-9]','-',nome.lower().strip())
            oid_luc = re.sub(r'-+','-',oid_luc).strip('-')
            oid_luc = f"luc-{oid_luc}"[:40]
            if not db.operadores.find_one({"_id":oid_luc}):
                db.operadores.insert_one({"_id":oid_luc,"equipeId":"luciano","nome":nome,"pleno":False,"meetcall":True,"criadoEm":datetime.now()})
            oid_mc = re.sub(r'[^a-z0-9]','-',nome.lower().strip())
            oid_mc = re.sub(r'-+','-',oid_mc).strip('-')
            oid_mc = f"mc-{oid_mc}"[:40]
            existentes = list(db.operadores.find({"equipeId":"metcool","nome":nome}))
            if len(existentes) > 1:
                for ex in existentes[1:]: db.operadores.delete_one({"_id":ex["_id"]})
            if not db.operadores.find_one({"_id":oid_mc}):
                db.operadores.insert_one({"_id":oid_mc,"equipeId":"metcool","nome":nome,"pleno":False,"meetcall":True,"criadoEm":datetime.now()})
    except: pass

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

@st.cache_data(ttl=3600)
def buscar_operadores(eq):
    ops = list(get_db().operadores.find({"equipeId":eq}).sort("nome",1))
    # Deduplica por nome (evita operadores duplicados)
    vistos = set()
    unicos = []
    for op in ops:
        nome_norm = op.get("nome","").strip().lower()
        if nome_norm not in vistos:
            vistos.add(nome_norm)
            unicos.append(op)
    return unicos

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

@st.cache_data(ttl=300)
def buscar_metas_equipe(ma, eq):
    return {d["opId"]:d.get("valor",0) for d in get_db().metas.find({"mesAno":ma,"equipeId":eq}) if "opId" in d}

def salvar_meta_gestora(ma, eq, meta, tpct):
    did = f"meta_gest__{ma}__{eq}"
    get_db().metas.update_one({"_id":did},{"$set":{"_id":did,"mesAno":ma,"equipeId":eq,"metaGestora":meta,"targetPct":tpct,"tipo":"gestora"}},upsert=True)

def buscar_meta_gestora(ma, eq):
    return get_db().metas.find_one({"_id":f"meta_gest__{ma}__{eq}"}) or {"metaGestora":0,"targetPct":125}

def salvar_lancamento_meetcall(ma, total_ligacoes, rec_geral, rec_geral_total=0):
    get_db().metas.update_one(
        {"_id":f"meetcall__{ma}"},
        {"$set":{"_id":f"meetcall__{ma}","mesAno":ma,"totalLigacoes":total_ligacoes,"recGeral":rec_geral,"recGeralTotal":rec_geral_total,"atualizadoEm":datetime.now()}},
        upsert=True)

def buscar_lancamento_meetcall(ma):
    return get_db().metas.find_one({"_id":f"meetcall__{ma}"}) or {}

def criar_lancamento(ma, eq, data_ref, label, agentes, total, sem_int, dt, td, rec_geral=0):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    get_db().lancamentos.insert_one({"_id":f"lanc__{ma}__{eq}__{ts}","mesAno":ma,"equipeId":eq,"dataRef":data_ref,"label":label,"agentes":agentes,"totalEquipe":total,"semInteracao":sem_int,"diasTrabalhados":dt,"totalDias":td,"recGeral":rec_geral,"criadoEm":datetime.now()})

@st.cache_data(ttl=300)
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

def salvar_monitoria(eq, oid, onome, prot, obs, crits, erros, nota, ma, semana=None, tipo="ligacao"):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    get_db().monitorias.insert_one({"_id":f"mon__{eq}__{oid}__{ts}","equipeId":eq,"opId":oid,"opNome":onome,"protocolo":prot,"observacao":obs,"criterios":crits,"errosCriticos":erros,"nota":nota,"mesAno":ma,"semana_mon":semana,"tipo":tipo,"criadoEm":datetime.now()})

def buscar_monitorias_operador(oid): return list(get_db().monitorias.find({"opId":oid}).sort("criadoEm",-1))

def buscar_monitorias_equipe(eq, ma=None):
    f = {"equipeId":eq}
    if ma: f["mesAno"] = ma
    return list(get_db().monitorias.find(f).sort("criadoEm",-1))

def excluir_monitoria(did): get_db().monitorias.delete_one({"_id":did})

def salvar_processamento(ma, eq, df, usuario_nome=""):
    get_db().processamentos.update_one({"_id":f"proc__{ma}__{eq}"},{"$set":{"_id":f"proc__{ma}__{eq}","mesAno":ma,"equipeId":eq,"registros":df.to_dict("records"),"usuarioNome":usuario_nome,"atualizadoEm":datetime.now()}},upsert=True)
    try: salvar_historico_processamento(ma,eq,usuario_nome,df)
    except: pass

def buscar_ultimo_processamento(ma, eq):
    doc = get_db().processamentos.find_one({"mesAno":ma,"equipeId":eq},sort=[("criadoEm",-1)])
    if not doc: return {}
    if doc.get("registros"):
        try:
            df = pd.DataFrame(doc["registros"])
            df["valor"] = pd.to_numeric(df.get("valor", pd.Series(dtype=float)), errors="coerce").fillna(0)
            if "elegibilidade" in df.columns:
                elig = df[df["elegibilidade"]=="Elegível"]
            else:
                elig = df
            doc["valorElegivel"]     = float(elig["valor"].sum())
            doc["boletosElegiveis"]  = len(elig)
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
    get_db().usuarios_senhas.update_one(
        {"_id": uid},
        {"$set": {"_id": uid, "senha": nova_senha, "atualizadoEm": datetime.now()}},
        upsert=True)
    buscar_senha_usuario.clear()

@st.cache_data(ttl=3600)
def buscar_senha_usuario(uid):
    try:
        doc = get_db().usuarios_senhas.find_one({"_id": uid})
        if doc and doc.get("senha"):
            return doc["senha"]
    except: pass
    u = USUARIOS.get(uid)
    if u: return u.get("senha")
    return None

def salvar_historico_processamento(mes_ano, equipe_id, usuario_nome, df):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    doc_id = f"hist_proc__{mes_ano}__{equipe_id}__{ts}"
    df_num = df.copy()
    df_num["valor"] = pd.to_numeric(df_num.get("valor", pd.Series(dtype=float)), errors="coerce").fillna(0)
    elig = df_num[df_num["elegibilidade"]=="Elegível"] if "elegibilidade" in df_num.columns else df_num
    fornecedoras = sorted(df_num["fornecedora"].dropna().unique().tolist()) if "fornecedora" in df_num.columns else []
    get_db().historico_processamentos.insert_one({
        "_id": doc_id,
        "mesAno": mes_ano,
        "equipeId": equipe_id,
        "usuarioNome": usuario_nome,
        "fornecedoras": fornecedoras,
        "totalBoletos": len(df_num),
        "boletosElegiveis": len(elig),
        "valorElegivel": float(elig["valor"].sum()),
        "valorTotal": float(df_num["valor"].sum()),
        "criadoEm": datetime.now()
    })

def buscar_historico_geral(mes_ano=None, equipe_id=None):
    filtro = {}
    if mes_ano: filtro["mesAno"] = mes_ano
    if equipe_id: filtro["equipeId"] = equipe_id
    novos = list(get_db().historico_processamentos.find(filtro).sort("criadoEm", -1))
    ids_ja_vistos = set(f"{h['mesAno']}__{h['equipeId']}" for h in novos)
    procs = list(get_db().processamentos.find(filtro).sort("atualizadoEm", -1))
    antigos = []
    for p in procs:
        chave = f"{p['mesAno']}__{p['equipeId']}"
        if chave in ids_ja_vistos:
            continue
        val = 0.0; boletos = 0; forns = []
        try:
            df = pd.DataFrame(p.get("registros", []))
            if not df.empty:
                df["valor"] = pd.to_numeric(df.get("valor", pd.Series(dtype=float)), errors="coerce").fillna(0)
                elig = df[df["elegibilidade"]=="Elegível"] if "elegibilidade" in df.columns else df
                val = float(elig["valor"].sum())
                boletos = len(elig)
                forns = sorted(df["fornecedora"].dropna().unique().tolist()) if "fornecedora" in df.columns else []
        except: pass
        antigos.append({
            "_id": p["_id"],
            "mesAno": p["mesAno"],
            "equipeId": p["equipeId"],
            "usuarioNome": p.get("usuarioNome", EQUIPES.get(p["equipeId"],{}).get("nome","—")),
            "fornecedoras": forns,
            "totalBoletos": boletos,
            "boletosElegiveis": boletos,
            "valorElegivel": val,
            "criadoEm": p.get("atualizadoEm", datetime.now()),
        })
    todos = novos + antigos
    todos.sort(key=lambda x: x.get("criadoEm", datetime.now()), reverse=True)
    return todos

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

def parse_brl(s):
    """Converte string no formato R$ 1.234.567,89 para float."""
    if s is None: return 0.0
    s = str(s).strip().replace("R$","").replace(" ","").strip()
    # Formato BR: ponto como milhar, vírgula como decimal
    if "," in s:
        s = s.replace(".","").replace(",",".")
    else:
        s = s.replace(".","")
    try: return float(s)
    except: return 0.0

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
    import math
    m=math.floor(media+0.5)
    if m<=70: return 0
    if m<=80: return 300
    if m<=90: return 500
    if m<=95: return 700
    if m<=99: return 1000
    if m>=100: return 1100
    return 0

def calc_media_operador(oid, ma=None):
    monts = buscar_monitorias_operador(oid)
    if ma: monts=[m for m in monts if m.get("mesAno")==ma]
    if not monts: return 0,0
    notas=[m["nota"] for m in monts if "nota" in m]
    if not notas: return 0,0
    media=sum(notas)/len(notas)
    return round(media,1),len(notas)

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
    <div style="background:#ffffff;border:1px solid #c8e0c8;
                border-radius:12px;padding:22px 28px;margin-bottom:24px;
                border-left:4px solid #2e7d32;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
        <h1 style="margin:0;color:#1a2e1a;font-size:20px;font-weight:700">{titulo}</h1>
        {"<p style='color:#5a8a5a;margin:4px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px'>"+sub+"</p>" if sub else ""}
    </div>""",unsafe_allow_html=True)

def seletor_equipe(default=None, key_suffix=""):
    u=st.session_state.usuario
    if u["role"] in ["gestor","diretor"]:
        return u["equipe"]
    if u["role"]=="admin":
        eq_opts=list(EQUIPES.keys())
        eq_labels=[f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        default_idx=eq_opts.index(default) if default and default in eq_opts else 0
        import traceback
        caller=traceback.extract_stack()[-2].name
        sel=st.selectbox("Gerenciando equipe:",eq_labels,index=default_idx,key=f"admin_eq_{caller}{key_suffix}")
        return eq_opts[eq_labels.index(sel)]
    return u["equipe"]

def importar_excel_operadores(arquivo, ops):
    import unicodedata
    def norm_nome(s):
        s = unicodedata.normalize('NFKD', str(s).strip()).encode('ascii','ignore').decode().upper()
        return re.sub(r'\s+', ' ', s).strip()
    def limpar_valor(v):
        s = str(v).strip()
        try:
            f = float(v)
            if f > 0: return f
        except: pass
        s = s.replace('R$','').replace(' ','').strip()
        if ',' in s:
            s = s.replace('.','').replace(',','.')
        else:
            s = s.replace('.','')
        try: return float(s)
        except: return 0.0

    try: df = pd.read_excel(arquivo, header=0)
    except Exception as e: return None, f"Erro ao ler arquivo: {e}"

    col_nome = None
    for c in df.columns:
        cn = norm_nome(str(c))
        if any(x in cn for x in ['OPERADOR','NOME','AGENTE','COLABORADOR','ATENDENTE']):
            col_nome = c; break
    if not col_nome:
        for c in df.columns:
            if df[c].dtype == object:
                col_nome = c; break
    if not col_nome: return None, "Coluna de nome não encontrada"

    col_val = None
    for c in df.columns:
        if c == col_nome: continue
        cn = norm_nome(str(c))
        if any(x in cn for x in ['VALOR','RECEBIDO','PAGO','RECEBIMENTO','RECEBI']):
            col_val = c; break
    if not col_val:
        for c in df.columns:
            if c == col_nome: continue
            try:
                vals = df[c].apply(limpar_valor)
                if vals.sum() > 0: col_val = c; break
            except: pass
    if not col_val: return None, "Coluna de valor não encontrada"

    col_lig = None
    for c in df.columns:
        if c in [col_nome, col_val]: continue
        cn = norm_nome(str(c))
        if any(x in cn for x in ['LIGAC','LIG','CALL','ATEND']):
            col_lig = c; break

    ops_norm = {norm_nome(op['nome']): op for op in ops}
    resultados = []
    for _, row in df.iterrows():
        nome_excel = str(row[col_nome]).strip()
        if not nome_excel or nome_excel.lower() in ['nan','none','']: continue
        valor = limpar_valor(row[col_val])
        ligacoes = int(limpar_valor(row[col_lig])) if col_lig and col_lig in row else 0
        nome_norm = norm_nome(nome_excel)
        primeiro_nome = nome_norm.split()[0] if nome_norm.split() else ''
        match = ops_norm.get(nome_norm)
        status = 'exato'
        if not match:
            matches_pn = [op for n, op in ops_norm.items() if n.startswith(primeiro_nome + ' ') or n == primeiro_nome]
            if len(matches_pn) == 1:
                match = matches_pn[0]; status = 'primeiro_nome'
            elif len(matches_pn) > 1:
                partes = nome_norm.split()
                if len(partes) >= 2:
                    dois_nomes = ' '.join(partes[:2])
                    matches_2n = [op for n, op in ops_norm.items() if n.startswith(dois_nomes)]
                    if len(matches_2n) == 1:
                        match = matches_2n[0]; status = 'dois_nomes'
                    else:
                        status = 'ambiguo'
                else:
                    status = 'ambiguo'
        resultados.append({'nome_excel': nome_excel,'op': match,'valor': valor,'ligacoes': ligacoes,'status': status,'col_lig': col_lig is not None})

    return resultados, None

def get_val_op(ag, oid, onome):
    for k,v in ag.items():
        if isinstance(v,dict) and v.get("nome","").strip().lower()==onome.strip().lower():
            return float(v.get("valorRecebido",0))
    if oid in ag:
        v=ag[oid]
        return float(v.get("valorRecebido",0) if isinstance(v,dict) else v)
    return 0.0

# ── CORREÇÃO PRINCIPAL: normalizar_cpf com zfill(11) ──
def normalizar_cpf(s):
    s=str(s).strip()
    # Converte notação científica e float do Excel (ex: 1.23457E+10, 12345678909.0)
    try:
        f=float(s)
        if f>0: s=str(int(round(f)))
    except: pass
    # Remove formatação
    s=s.replace(".","").replace("-","").replace("/","").replace(" ","")
    # Garante 11 dígitos com zeros à esquerda (CPF pode ter zero inicial)
    if s.isdigit() and len(s)<=11:
        s=s.zfill(11)
    return s

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
            <img src="data:image/webp;base64,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" style="width:72px;height:72px;border-radius:16px;object-fit:cover;margin-bottom:14px;box-shadow:0 4px 16px rgba(0,0,0,0.2)"/>
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
                senha_correta = buscar_senha_usuario(uid) or u.get("senha")
                if senha_correta and senha.strip() == senha_correta:
                    st.session_state.usuario={"id":uid,**u}; st.rerun()
                else: st.error("Usuário ou senha incorretos.")
            else: st.error("Usuário ou senha incorretos.")
        st.markdown('<p style="text-align:center;color:#1a4d2e;font-size:11px;margin-top:24px">iGreen Energy © 2026</p>',unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────
def _mini_operadores(u):
    eq = u.get("equipe")
    if not eq:
        st.info("Disponível apenas para gestores.")
        return
    ops = buscar_operadores(eq)
    st.markdown(f"<p style='font-size:11px;color:#5a9a70;margin-bottom:8px'>{len(ops)} operadores — Equipe {EQUIPES[eq]['nome']}</p>",unsafe_allow_html=True)
    nn = st.text_input("Nome do novo operador",placeholder="Nome completo",key="mc_op_nome")
    np = st.checkbox("Pleno",key="mc_op_pleno")
    if st.button("Adicionar",use_container_width=True,key="mc_op_add"):
        if nn.strip(): salvar_operador(eq,nn.strip(),np); st.success(f"{nn} adicionado!"); st.rerun()
        else: st.error("Digite o nome.")
    if ops:
        st.markdown("---")
        for op in ops:
            c1,c2,c3 = st.columns([3,1,1])
            with c1: ne = st.text_input("",value=op["nome"],key=f"mc_n_{op['_id']}",label_visibility="collapsed")
            with c2:
                if st.button("V",key=f"mc_s_{op['_id']}"):
                    atualizar_operador(op["_id"],ne,op.get("pleno",False)); st.rerun()
            with c3:
                if st.button("X",key=f"mc_d_{op['_id']}"):
                    excluir_operador(op["_id"]); st.rerun()

def _mini_criterios():
    crits = get_criterios()
    ce = []
    for i,c in enumerate(crits):
        with st.expander(f"{c['num']} {c['nome']}",expanded=False):
            nm = st.text_input("Nome",value=c["nome"],key=f"mcc_n_{i}")
            ps = st.number_input("Peso",min_value=1,max_value=100,value=int(c["peso"]),key=f"mcc_p_{i}")
            ob = st.checkbox("Obrigatório",value=c.get("obrigatorio",False),key=f"mcc_o_{i}")
            it = st.text_area("Itens",value="\n".join(c.get("itens",[])),height=80,key=f"mcc_i_{i}")
            ce.append({"id":c["id"],"num":c["num"],"nome":nm,"peso":ps,"obrigatorio":ob,"itens":[x.strip() for x in it.split("\n") if x.strip()]})
    if st.button("Salvar Critérios",use_container_width=True,key="mc_crit_save"):
        salvar_criterios(ce); st.success("Salvo!"); st.rerun()

DARK_CSS = """
.stApp { background-color: #0d1117 !important; --text-color: #e6edf3; --text-muted: #8b949e; --bg-card: #161b22; --border-color: #30363d; }
[data-testid="stSidebar"] { background: #161b22 !important; border-right: 1px solid #30363d !important; }
[data-testid="stSidebar"] .stRadio label { color: #e6edf3 !important; background: #21262d !important; border: 1px solid #30363d !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stRadio label:hover { background: #2d333b !important; color: #ffffff !important; border-color: #3fb950 !important; }
[data-testid="stSidebar"] .stRadio label[data-checked="true"] { background: #238636 !important; color: #ffffff !important; border-color: #3fb950 !important; font-weight: 600 !important; }
[data-testid="stMetric"] { background: #161b22 !important; border: 1px solid #30363d !important; border-top: 2px solid #3fb950 !important; }
[data-testid="stMetricValue"] { color: #e6edf3 !important; font-size: 16px !important; white-space: nowrap !important; overflow: visible !important; }
[data-testid="stMetricLabel"] { color: #7ee787 !important; }
.stButton > button { background: #21262d !important; color: #7ee787 !important; border: 1px solid #30363d !important; }
.stButton > button:hover { background: #238636 !important; color: #ffffff !important; border-color: #3fb950 !important; }
h1 { color: #e6edf3 !important; } h2 { color: #c9d1d9 !important; } p { color: #8b949e !important; }
hr { border-top: 1px solid #30363d !important; }
.stTextInput input, .stNumberInput input, .stTextArea textarea { background: #0d1117 !important; border: 1px solid #30363d !important; color: #e6edf3 !important; }
.stSelectbox > div > div { background: #161b22 !important; border: 1px solid #30363d !important; color: #e6edf3 !important; }
[data-baseweb="select"] { background: #161b22 !important; }
[data-baseweb="select"] > div { background: #161b22 !important; color: #e6edf3 !important; }
[data-baseweb="popover"] { background: #161b22 !important; border: 1px solid #30363d !important; }
[role="option"] { background: #161b22 !important; color: #e6edf3 !important; }
[role="option"]:hover { background: #21262d !important; }
.stTabs [data-baseweb="tab-list"] { background: #161b22 !important; border: 1px solid #30363d !important; }
.stTabs [data-baseweb="tab"] { color: #8b949e !important; }
.stTabs [aria-selected="true"] { background: #238636 !important; color: #ffffff !important; }
.stCheckbox label { color: #c9d1d9 !important; }
[data-testid="stFileUploader"] > div { background: #161b22 !important; border: 1.5px dashed #30363d !important; }
.stSuccess > div { background: #0f2117 !important; border-left: 3px solid #3fb950 !important; color: #7ee787 !important; }
.stError > div { background: #2d1117 !important; border-left: 3px solid #f85149 !important; color: #ffa198 !important; }
.stWarning > div { background: #271a00 !important; border-left: 3px solid #d29922 !important; color: #e3b341 !important; }
.stInfo > div { background: #0c2d6b !important; border-left: 3px solid #388bfd !important; color: #79c0ff !important; }
[data-testid="stDataFrame"] { border: 1px solid #30363d !important; background: #161b22 !important; }
[data-testid="stDataFrame"] * { color: #e6edf3 !important; }
.streamlit-expanderHeader { background: #161b22 !important; border: 1px solid #30363d !important; color: #c9d1d9 !important; }
.streamlit-expanderContent { background: #0d1117 !important; border: 1px solid #30363d !important; }
div[data-testid="stVerticalBlock"] label { color: #8b949e !important; }
.block-container { background: #0d1117 !important; }
"""

def render_sidebar():
    u=st.session_state.usuario
    role_label='Administrador' if u['role']=='admin' else 'Diretoria' if u['role']=='diretor' else 'Gestor'
    with st.sidebar:
        st.markdown(
            f"<div style='padding:16px 12px 8px'>"
            f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px'>"
            f"<div style='width:34px;height:34px;background:#2e7d32;border-radius:8px;"
            f"display:flex;align-items:center;justify-content:center;font-weight:900;font-size:16px;color:#fff'><img src='data:image/webp;base64,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' style='width:28px;height:28px;border-radius:6px;object-fit:cover'/></div>"
            f"<div><span style='color:#2e7d32;font-weight:700;font-size:15px'>iGreen</span>"
            f"<span style='color:#1a2e1a;font-weight:700;font-size:15px'> Performance</span></div>"
            f"</div></div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='margin:0 8px 12px;background:#f0f7f0;border:1px solid #c8e0c8;"
            f"border-radius:8px;padding:10px 12px'>"
            f"<div style='color:#2e7d32;font-weight:700;font-size:14px'>{u['nome']}</div>"
            f"<div style='color:#5a8a5a;font-size:11px'>{role_label}</div>"
            f"</div>",
            unsafe_allow_html=True)
        anos=get_anos_disponiveis()
        ano=st.selectbox('Ano',anos,label_visibility='collapsed')
        meses=get_todos_meses_ano(int(ano))
        mes_labels=[m.split('-')[0] for m in meses]
        mes_sel=st.selectbox('Mês',mes_labels,index=datetime.now().month-1,label_visibility='collapsed')
        mes_ano=f'{mes_sel}-{ano}'
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if u['role']=='diretor':
            pags=['Quadro de Resultados','Visualização RCA','Análise dos Operadores','Monitorias','Análise de Inadimplência','Metas','Minha Conta']
        elif u['role']=='admin':
            pags=['Quadro de Resultados','Lançamento','Visualização RCA','Análise dos Operadores','Monitorias','Upload de Bases','Análise de Inadimplência','Metas','Minha Conta']
        elif u.get('equipe')=='metcool':
            pags=['Meet Call','Análise dos Operadores','Monitorias','Minha Conta']
        else:
            pags=['Quadro de Resultados','Lançamento','Meet Call','Análise dos Operadores','Monitorias','Upload de Bases','Análise de Inadimplência','Metas','Minha Conta']
        pag=st.radio('Menu',pags,label_visibility='collapsed',index=0)
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if st.button('Sair',use_container_width=True,key='btn_sair'):
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
    for op in ops:
        c1,c2,c3,c4=st.columns([3,1,1,1])
        with c1: nn=st.text_input("n",value=op["nome"],label_visibility="collapsed",key=f"n_{op['_id']}")
        with c2: np=st.checkbox("Pleno",value=op.get("pleno",False),key=f"p_{op['_id']}")
        with c3:
            if st.button("Salvar",key=f"s_{op['_id']}"): atualizar_operador(op["_id"],nn,np); st.rerun()
        with c4:
            if st.button("Excluir",key=f"d_{op['_id']}"): excluir_operador(op["_id"]); st.rerun()


def processar_base_unica(arquivo, eq, ma):
    import unicodedata
    def norm(s): return unicodedata.normalize('NFKD',str(s).upper().strip()).encode('ascii','ignore').decode()
    try: xls=pd.ExcelFile(arquivo)
    except Exception as e: return None,[f"Erro: {e}"],[]
    abas_norm=[norm(a) for a in xls.sheet_names]; abas_orig=xls.sheet_names

    aba_pagos=None
    for i,a in enumerate(abas_norm):
        if any(p in a for p in ["PAGO","PAGAM","RECEB","BASE","BAIXA","PAGT","RESULT"]):
            aba_pagos=abas_orig[i]; break
    if not aba_pagos:
        for i,a in enumerate(abas_norm):
            if not any(x in a for x in ["CHAT","LIG","DISPAR","CONTATO"]):
                aba_pagos=abas_orig[i]; break
    if not aba_pagos: aba_pagos=abas_orig[0]

    df=pd.read_excel(xls,sheet_name=aba_pagos,header=0).reset_index(drop=True)
    df["_row_id"]=df.index

    col_cpf=col_val=col_dpag=col_dvenc=col_forn=None
    for c in df.columns:
        cn=norm(str(c))
        if not col_cpf and ("CPF" in cn or "IDENTIFICADOR" in cn or "IDENTIF" in cn) and "CLIENTE" not in cn and "NOME" not in cn: col_cpf=c
        if not col_val  and any(x in cn for x in ["VALOR","VLR","VL_","PAGAR","TOTAL","VAL_TOT","RECEB"]): col_val=c
        if not col_dpag and any(x in cn for x in ["PAGAM","PAGTO","DT_PAG","DATA_PAG","BAIXA","DT_BAI","DATA DE PAG","DATAPAG","DATA PAG","DATA PAGAMENTO"]): col_dpag=c
        if not col_dvenc and any(x in cn for x in ["VENC","DATA DE VENC","DT_VENC","DATAVENC","DATA VENC","DATA VENCIMENTO","VENCIMENTO"]): col_dvenc=c
        if not col_forn and any(x in cn for x in ["FORNEC","DISTRIB","EMPRESA","CONCESS","FORNECEDOR","FORNECEDORA","FORN"]): col_forn=c

    mapa={}
    if col_cpf:  mapa[col_cpf]="uc_cpf"
    if col_val:  mapa[col_val]="valor"
    if col_dpag: mapa[col_dpag]="data_pagamento"
    if col_dvenc: mapa[col_dvenc]="data_vencimento"
    if col_forn: mapa[col_forn]="fornecedora"
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
            cc=next((c for c in dc.columns if norm(str(c)) in ["CPF","IDENTIFICADOR","IDENTIF","IDENTIFICACAO"]),dc.columns[0])
            cd=next((c for c in dc.columns if any(x in norm(str(c)) for x in ["DATA","DT_","BAIXA","CONTATO","INTERAC","LIGAC","CHAT","DISPAR","PAGAM"])),dc.columns[1] if len(dc.columns)>1 else dc.columns[0])
            dd=pd.DataFrame({"uc_cpf":dc[cc].apply(normalizar_cpf),"data_contato":pd.to_datetime(dc[cd],dayfirst=True,errors="coerce").dt.normalize()}).dropna(subset=["data_contato"])
            dd=dd[dd["uc_cpf"].str.len()>=8]
            dd=dd[~dd["uc_cpf"].str.match(r"^0+$")]
            dd=dd[dd["uc_cpf"]!="nan"]
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

def pagina_metas(ma):
    u=st.session_state.usuario
    header_page("Metas",ma.replace("-"," "))
    if u["role"]=="diretor":
        eq_opts=list(EQUIPES.keys())
        eq_labels=[f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        eq_sel=st.selectbox("Selecionar equipe:",eq_labels,key="dir_eq_metas")
        eq=eq_opts[eq_labels.index(eq_sel)]
    else:
        eq=seletor_equipe(u.get("equipe") or "luciano")
    ops_todos=buscar_operadores(eq)
    # Luciano: exclui Meet Call das metas
    ops = [op for op in ops_todos if op["nome"] not in OPERADORES_MEETCALL] if eq=="luciano" else ops_todos
    if not ops: st.warning("Cadastre operadores primeiro."); return
    buscar_metas_equipe.clear()
    st.markdown("### Meta da Gestora")
    mg_doc=buscar_meta_gestora(ma,eq)
    c1,c2=st.columns([2,1])
    with c1: mg_val=st.number_input("Meta Base (R$)",min_value=0.0,step=1000.0,format="%.2f",value=float(mg_doc.get("metaGestora",0)),key="mg_val")
    tpct=100
    with c2: st.markdown(f"<div style='padding-top:28px;color:#2daf5c;font-weight:700;font-size:16px'>{fmt_brl(mg_val)}</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Metas por Operador")
    ms=buscar_metas_equipe(ma,eq); mn={}
    for op in ops:
        c1,c2=st.columns([3,2])
        with c1: st.markdown(f"<div style='padding-top:10px;color:#1a3a1a'>{'[P] ' if op.get('pleno') else ''}{op['nome']}</div>",unsafe_allow_html=True)
        with c2: mn[op["_id"]]=st.number_input("m",label_visibility="collapsed",min_value=0.0,step=100.0,format="%.2f",value=float(ms.get(op["_id"],0)),key=f"mg_{ma}_{op['_id']}")
    st.markdown("---")
    if st.button("Salvar Metas",use_container_width=True):
        for oid,v in mn.items(): salvar_meta_operador(ma,eq,oid,v)
        salvar_meta_gestora(ma,eq,mg_val,tpct)
        buscar_metas_equipe.clear()
        st.session_state["meta_salva_msg"] = f"✅ Metas da Equipe {EQUIPES.get(eq,{}).get('nome',eq)} salvas com sucesso!"
        st.rerun()
    if st.session_state.get("meta_salva_msg"):
        st.success(st.session_state.pop("meta_salva_msg"))

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
    with c2: dt=st.number_input("Dias Trabalhados *",min_value=0,max_value=31,value=0,key=f"dt_{eq}_{ma}")
    with c3: td=st.number_input("Total Dias do Mês *",min_value=0,max_value=31,value=0,key=f"td_{eq}_{ma}")
    up_atual=buscar_ultimo_processamento(ma,eq)
    rec_auto=float(up_atual.get("valorElegivel",0)) if up_atual else 0
    rec_anterior=rec_auto
    if rec_anterior==0:
        lancs_ant=buscar_lancamentos(ma,eq)
        for l in lancs_ant:
            if l.get("recGeral",0)>0:
                rec_anterior=float(l["recGeral"]); break
    usar_rec_manual=st.checkbox("Inserir Recebido Geral manualmente",key=f"rec_manual_chk_{eq}_{ma}")
    if usar_rec_manual:
        rec_geral_manual=st.number_input("Recebido Geral (R$)",min_value=0.0,step=100.0,format="%.2f",value=float(rec_anterior or 0),key=f"rec_geral_manual_{eq}_{ma}")
    else:
        rec_geral_manual=rec_anterior
    st.markdown("---")
    st.markdown("### Valores por Operador")
    mostrar_imp = st.checkbox("Importar via Excel", key=f"chk_imp_{eq}_{ma}")
    arq_imp = None
    if mostrar_imp:
        arq_imp = st.file_uploader("Planilha Excel (.xlsx)", type=["xlsx"], key=f"imp_{eq}_{ma}")
    if arq_imp:
        arq_imp.seek(0)
        resultados_imp, erro_imp = importar_excel_operadores(arq_imp, ops)
        if erro_imp:
            st.error(erro_imp)
        elif resultados_imp:
                st.markdown("**Prévia do lançamento:**")
                prev_rows = []
                for r in resultados_imp:
                    if r['status'] == 'ambiguo':
                        icone = " Ambíguo"
                    elif r['op'] is None:
                        icone = " Não encontrado"
                    else:
                        icone = "" + r['op']['nome']
                    row = {"Excel": r['nome_excel'], "Sistema": icone, "Valor": fmt_brl(r['valor'])}
                    if r['col_lig']: row["Lig. +5s"] = r['ligacoes']
                    prev_rows.append(row)
                st.dataframe(pd.DataFrame(prev_rows), use_container_width=True, hide_index=True)
                pode_importar = all(r['op'] is not None and r['status'] != 'ambiguo' for r in resultados_imp if r['valor'] > 0)
                if not pode_importar:
                    st.warning("Alguns operadores não foram identificados. Corrija manualmente os campos abaixo.")
                if st.button("Confirmar Importação", use_container_width=True, key=f"imp_confirmar_{eq}_{ma}"):
                    for r in resultados_imp:
                        if r['op'] and r['status'] != 'ambiguo' and r['valor'] > 0:
                            # Ignorar operadores Meet Call no lançamento do Luciano
                            if r['op'].get('nome','') in OPERADORES_MEETCALL:
                                continue
                            st.session_state[f"op_{eq}_{ma}_{r['op']['_id']}"] = r['valor']
                            if r['col_lig']:
                                st.session_state[f"lig_{eq}_{ma}_{r['op']['_id']}"] = r['ligacoes']
                    st.success("Valores importados! Revise e salve.")
                    st.rerun()
    vi={}; lig_vi={}
    # No lançamento do Luciano: mostrar APENAS operadores iGreen (sem Meet Call)
    ops_igreen=[op for op in ops if op["nome"] not in OPERADORES_MEETCALL]
    grupos=[]
    grupos.append(("",None,ops_igreen))
    for grupo_nome,grupo_cor,grupo_ops in grupos:
        if grupo_nome:
            st.markdown(f"<p style='color:{grupo_cor};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:12px 0 4px'>{grupo_nome}</p>",unsafe_allow_html=True)
        for op in grupo_ops:
            meta=float(ms.get(op["_id"],0))
            c1,c2,c3=st.columns([3,2,2])
            with c1: st.markdown(f"<div style='padding-top:10px;color:var(--text-color,#1a3a1a);font-weight:500'>{'★ ' if op.get('pleno') else ''}{op['nome']}</div>",unsafe_allow_html=True)
            with c2: st.markdown(f"<div style='padding-top:10px;color:#2e7d32;font-size:13px;font-weight:500'>{fmt_brl(meta) if meta>0 else '—'}</div>",unsafe_allow_html=True)
            with c3: vi[op["_id"]]=st.number_input("v",label_visibility="collapsed",min_value=0.0,step=100.0,format="%.2f",key=f"op_{eq}_{ma}_{op['_id']}")
            lig_vi[op["_id"]]=st.number_input("Lig. acima 5s",label_visibility="visible",min_value=0,step=1,value=0,key=f"lig_{eq}_{ma}_{op['_id']}")
    tc=sum(vi.values())
    st.markdown("---")
    usar_manual=st.checkbox("Inserir valor total manualmente",key=f"manual_{eq}_{ma}")
    if usar_manual:
        tc_manual=st.number_input("Valor Total com Interação (R$)",min_value=0.0,step=100.0,format="%.2f",value=tc,key=f"tc_manual_{eq}_{ma}")
        tc=tc_manual
    st.markdown(f"<div style='background:#0a2414;border-radius:8px;padding:12px 16px;margin-bottom:16px'><span style='color:#5a9a70;font-size:11px'>TOTAL COM INTERAÇÃO</span><br><span style='color:#2daf5c;font-size:20px;font-weight:700'>{fmt_brl(tc)}</span></div>",unsafe_allow_html=True)
    if st.button("Salvar Lançamento",use_container_width=True,key=f"btn_{eq}_{ma}"):
        errs=[]
        if dt==0: errs.append("Dias Trabalhados é obrigatório.")
        if td==0: errs.append("Total de Dias do Mês é obrigatório.")
        if errs:
            for e in errs: st.error(e)
        else:
            label="Fechamento do Mês" if eh_fech else data_sel.strftime("%d/%m/%Y")
            ag={op["_id"]:{"valorRecebido":vi.get(op["_id"],0),"nome":op["nome"],"ligacoes":lig_vi.get(op["_id"],0)} for op in ops if op["nome"] not in OPERADORES_MEETCALL}
            tc_real=sum(float(v.get("valorRecebido",0)) for v in ag.values())
            criar_lancamento(ma,eq,str(data_sel),label,ag,tc_real,0,dt,td,rec_geral_manual)
            # Limpar caches para atualizar quadro instantaneamente
            buscar_lancamentos.clear()
            buscar_metas_equipe.clear()
            st.session_state.ultimo_salvo=f"✅ Lançamento de {label} salvo com sucesso! Total: {fmt_brl(tc_real)}"
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
    eqs_vis=["luciano","deborah","tamires"]
    # Para admin e diretor: mostrar Luciano, Déborah, Tamires + Meet Call separado
    # Ordem fixa: Luciano, Meet Call, Déborah, Tamires
    eqs_base=["luciano","metcool","deborah","tamires"]
    if is_adm or is_dir:
        eqs=eqs_base
    elif u.get("equipe")=="metcool": eqs=["metcool"]
    else: eqs=[u["equipe"]]
    header_page("Quadro de Resultados", ma.replace("-"," ").upper())
    if is_dir:
        tot_rec=tot_ci=tot_si=tot_meta=tot_proj=0
        equipes_data=[]
        for eq_r in ["luciano","metcool","deborah","tamires"]:
            try:
                lancs_r=buscar_lancamentos(ma,eq_r)
                if not lancs_r: continue
                ul_r=lancs_r[0]
                mg_r=float(buscar_meta_gestora(ma,eq_r).get("metaGestora",0))
                if eq_r=="metcool":
                    tc_r=sum(float(v.get("valorRecebido",0)) for v in ul_r.get("agentes",{}).values() if isinstance(v,dict))
                elif eq_r=="luciano":
                    tc_r=sum(float(v.get("valorRecebido",0)) for v in ul_r.get("agentes",{}).values() if isinstance(v,dict) and v.get("nome","") not in OPERADORES_MEETCALL)
                else:
                    tc_r=sum(float(v.get("valorRecebido",0)) for v in ul_r.get("agentes",{}).values() if isinstance(v,dict))
                dt_r=int(ul_r.get("diasTrabalhados",0)); td_r=int(ul_r.get("totalDias",22))
                up_r=buscar_ultimo_processamento(ma,eq_r)
                rg_r=float(up_r.get("valorElegivel",0)) if up_r else 0
                if rg_r==0:
                    if ul_r.get("recGeral",0)>0: rg_r=float(ul_r["recGeral"])
                    else:
                        for l in lancs_r[1:]:
                            if l.get("recGeral",0)>0: rg_r=float(l["recGeral"]); break
                if eq_r=="metcool":
                    mc_doc_r=buscar_lancamento_meetcall(ma)
                    rg_mc_r=float(mc_doc_r.get("recGeralTotal",mc_doc_r.get("recGeral",0)))
                    if rg_mc_r>0: rg_r=rg_mc_r
                si_r=max(0,rg_r-tc_r); proj_r=calc_projecao(rg_r,dt_r,td_r)
                pct_r=(rg_r/mg_r*100) if mg_r>0 else 0
                tot_rec+=rg_r; tot_ci+=tc_r; tot_si+=si_r; tot_meta+=mg_r; tot_proj+=proj_r
                nome_eq = "Meet Call" if eq_r=="metcool" else EQUIPES[eq_r]["nome"]
                equipes_data.append({"nome":nome_eq,"rg":rg_r,"ci":tc_r,"si":si_r,"meta":mg_r,"proj":proj_r,"pct":pct_r})
            except: pass
        equipes_data.sort(key=lambda x: x["pct"], reverse=True)
        if equipes_data:
            pct_t=(tot_rec/tot_meta*100) if tot_meta>0 else 0
            cv_t=cor_pct(pct_t)
            linhas=""
            for ed in equipes_data:
                cv_e=cor_pct(ed["pct"])
                row=(
                    "<div style='display:flex;justify-content:space-between;align-items:center;"
                    "padding:14px 16px;border-bottom:1px solid #1e3a1e;flex-wrap:wrap;gap:8px'>"
                    f"<div style='color:#ffffff;font-weight:700;font-size:14px;min-width:130px'>Equipe {ed['nome']}</div>"
                    "<div style='display:flex;gap:16px;flex-wrap:wrap;flex:1'>"
                    f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>RECEBIDO</div><div style='color:#00c853;font-weight:700;font-size:14px'>{fmt_brl(ed['rg'])}</div></div>"
                    f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>COM INTER.</div><div style='color:#e8f5e9;font-size:14px'>{fmt_brl(ed['ci'])}</div></div>"
                    f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>SEM INTER.</div><div style='color:#8ab89a;font-size:14px'>{fmt_brl(ed['si'])}</div></div>"
                    f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>META</div><div style='color:#8ab89a;font-size:14px'>{fmt_brl(ed['meta'])}</div></div>"
                    f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>PROJEÇÃO</div><div style='color:#8ab89a;font-size:14px'>{fmt_brl(ed['proj'])}</div></div>"
                    "</div>"
                    f"<div style='color:{cv_e};font-size:16px;font-weight:800'>{ed['pct']:.1f}%</div>"
                    "</div>"
                )
                linhas+=row
            total_row=(
                "<div style='padding:14px 16px;background:#051005;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
                "<div style='color:#ffffff;font-weight:800;font-size:14px'>TOTAL GERAL</div>"
                "<div style='display:flex;gap:16px;flex-wrap:wrap;flex:1'>"
                f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>RECEBIDO</div><div style='color:#00c853;font-weight:800;font-size:17px'>{fmt_brl(tot_rec)}</div></div>"
                f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>COM INTER.</div><div style='color:#ffffff;font-weight:700;font-size:15px'>{fmt_brl(tot_ci)}</div></div>"
                f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>SEM INTER.</div><div style='color:#8ab89a;font-size:15px'>{fmt_brl(tot_si)}</div></div>"
                f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>META</div><div style='color:#8ab89a;font-size:15px'>{fmt_brl(tot_meta)}</div></div>"
                f"<div><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>PROJEÇÃO</div><div style='color:#8ab89a;font-size:15px'>{fmt_brl(tot_proj)}</div></div>"
                "</div>"
                f"<div style='text-align:right'><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase'>% META</div><div style='color:{cv_t};font-size:22px;font-weight:800'>{pct_t:.1f}%</div></div>"
                "</div>"
            )
            st.markdown(
                "<div style='background:linear-gradient(135deg,#0a1f0a,#0d2a0d);border:1px solid #1e3a1e;"
                "border-radius:14px;margin-bottom:16px;overflow:hidden;border-left:3px solid #00c853'>"
                +linhas+total_row+"</div>",
                unsafe_allow_html=True)
        st.markdown("---")
    for eq in eqs:
        try:
            ops=buscar_operadores(eq); lancs=buscar_lancamentos(ma,eq)
        except:
            st.error("Erro ao conectar ao banco. Tente recarregar."); continue
        if not lancs: continue
        ul=lancs[0]; mg_doc=buscar_meta_gestora(ma,eq); mops=buscar_metas_equipe(ma,eq)
        mg=float(mg_doc.get("metaGestora",0))
        # Com Interação: para Luciano exclui Meet Call; para metcool só Meet Call
        if eq=="luciano":
            tc=sum(float(v.get("valorRecebido",0)) for v in ul.get("agentes",{}).values() if isinstance(v,dict) and v.get("nome","") not in OPERADORES_MEETCALL)
        elif eq=="metcool":
            tc=sum(float(v.get("valorRecebido",0)) for v in ul.get("agentes",{}).values() if isinstance(v,dict))
        else:
            tc=sum(float(v.get("valorRecebido",0)) for v in ul.get("agentes",{}).values() if isinstance(v,dict))
        dt=int(ul.get("diasTrabalhados",0)); td=int(ul.get("totalDias",22))
        up=buscar_ultimo_processamento(ma,eq)
        rec_geral=float(up.get("valorElegivel",0)) if up else 0
        if rec_geral==0:
            if ul.get("recGeral",0)>0:
                rec_geral=float(ul["recGeral"])
            else:
                for l in lancs[1:]:
                    if l.get("recGeral",0)>0:
                        rec_geral=float(l["recGeral"]); break
        # Para metcool: recGeral vem do lancamento_meetcall (recGeralTotal)
        if eq=="metcool":
            mc_doc=buscar_lancamento_meetcall(ma)
            rg_mc=float(mc_doc.get("recGeralTotal",mc_doc.get("recGeral",0)))
            if rg_mc>0: rec_geral=rg_mc

        sem=max(0, rec_geral - tc)
        proj=calc_projecao(rec_geral, dt, td)
        pct=(rec_geral/mg*100) if mg>0 else 0
        cv=cor_pct(pct)
        rg_mc=ci_mc=mg_mc=si_mc=proj_mc=pct_mc=0.0; cv_mc="#e03c3c"; dt_mc=dt; td_mc=td
        if eq=="luciano":
            try:
                ci_mc=sum(float(v.get("valorRecebido",0)) for k,v in ul.get("agentes",{}).items() if isinstance(v,dict) and v.get("nome","") in OPERADORES_MEETCALL)
                lancs_mc=buscar_lancamentos(ma,"metcool")
                if lancs_mc:
                    ul_mc=lancs_mc[0]
                    rg_mc=float(ul_mc.get("totalEquipe",0))
                    dt_mc=int(ul_mc.get("diasTrabalhados",dt)); td_mc=int(ul_mc.get("totalDias",td))
                mg_mc=float(buscar_meta_gestora(ma,"metcool").get("metaGestora",0))
                si_mc=max(0,rg_mc-ci_mc); proj_mc=calc_projecao(rg_mc,dt_mc,td_mc)
                pct_mc=(rg_mc/mg_mc*100) if mg_mc>0 else 0; cv_mc=cor_pct(pct_mc)
            except: pass

        st.markdown(
            f"<div style='background:linear-gradient(135deg,#0a1f0a,#0d2a0d);border:1px solid #1e3a1e;"
            f"border-radius:14px;padding:20px 24px;margin-bottom:6px;border-left:3px solid #00c853'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:14px'>"
            f"<div style='font-size:15px;font-weight:700;color:#ffffff'>Equipe {EQUIPES[eq]['nome']} · {ul.get('label','')}</div>"
            f"<div style='text-align:right'><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px'>% META</div>"
            f"<div style='color:{cv};font-size:24px;font-weight:800'>{pct:.1f}%</div></div></div>"
            f"<div style='display:flex;gap:28px;flex-wrap:wrap'>"
            f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:3px'>RECEBIDO GERAL</div>"
            f"<div style='color:#00c853;font-weight:700;font-size:16px'>{fmt_brl(rec_geral)}</div></div>"
            f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:3px'>COM INTERAÇÃO</div>"
            f"<div style='color:#ffffff;font-weight:600;font-size:14px'>{fmt_brl(tc)}</div></div>"
            f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:3px'>SEM INTERAÇÃO</div>"
            f"<div style='color:#8ab89a;font-weight:600;font-size:14px'>{fmt_brl(sem)}</div></div>"
            f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:3px'>META</div>"
            f"<div style='color:#8ab89a;font-weight:600;font-size:14px'>{fmt_brl(mg)}</div></div>"
            f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:3px'>PROJEÇÃO</div>"
            f"<div style='color:#8ab89a;font-weight:600;font-size:14px'>{fmt_brl(proj)}</div></div>"
            f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:3px'>DIAS</div>"
            f"<div style='color:#8ab89a;font-weight:600;font-size:14px'>{dt}/{td}</div></div>"
            f"</div>"
            +
            f"</div>", unsafe_allow_html=True)
        k=f"show_ops_{eq}"
        if k not in st.session_state: st.session_state[k]=False
        nome_eq_btn = "Meet Call" if eq=="metcool" else EQUIPES[eq]['nome']
        if st.button(f"{'Ocultar' if st.session_state[k] else 'Exibir'} Operadores — {nome_eq_btn}",key=f"btn_ops_{eq}",use_container_width=True):
            st.session_state[k]=not st.session_state[k]; st.rerun()

        show=st.session_state[k]
        if show and ops:
            if eq=="luciano":
                ops_ig=[op for op in ops if op["nome"] not in OPERADORES_MEETCALL]
                rows=[]
                for op in ops_ig:
                    v=get_val_op(ul.get("agentes",{}),op["_id"],op["nome"])
                    meta=float(mops.get(op["_id"],0)); pc=(v/meta*100) if meta>0 else 0
                    proj_op=calc_projecao(v,dt,td) if v>0 else 0
                    lig_op=int(ul.get("agentes",{}).get(op["_id"],{}).get("ligacoes",0) if isinstance(ul.get("agentes",{}).get(op["_id"]),dict) else 0)
                    rows.append({"Operador":op["nome"]+(" ★" if op.get("pleno") else ""),"Recebido":fmt_brl(v) if v>0 else "—","Meta":fmt_brl(meta) if meta>0 else "—","% Meta":f"{pc:.1f}%" if meta>0 else "—","Projeção":fmt_brl(proj_op) if v>0 else "—","Lig. +5s":lig_op if lig_op>0 else "—","_v":v})
                df=pd.DataFrame(rows).sort_values("_v",ascending=False).drop(columns=["_v"]).reset_index(drop=True)
                df.index=range(1,len(df)+1)
                st.dataframe(df,use_container_width=True,height=min(400,(len(df)+1)*38+40))
            else:
                rows=[]
                for op in ops:
                    v=get_val_op(ul.get("agentes",{}),op["_id"],op["nome"])
                    meta=float(mops.get(op["_id"],0)); pc=(v/meta*100) if meta>0 else 0
                    proj_op=calc_projecao(v,dt,td) if v>0 else 0
                    rows.append({"Status":status_pct(pc) if meta>0 else "—","Operador":op["nome"]+(" ★" if op.get("pleno") else ""),"Recebido":fmt_brl(v) if v>0 else "—","Meta":fmt_brl(meta) if meta>0 else "—","% Meta":f"{pc:.1f}%" if meta>0 else "—","Projeção":fmt_brl(proj_op) if v>0 else "—","_v":v})
                df=pd.DataFrame(rows).sort_values("_v",ascending=False).drop(columns=["_v"]).reset_index(drop=True)
                df.index=range(1,len(df)+1)
                st.dataframe(df,use_container_width=True,height=min(600,(len(df)+1)*38+40))
        if up and up.get("registros"):
            try:
                df_proc=pd.DataFrame(up["registros"])
                if "fornecedora" in df_proc.columns and "valor" in df_proc.columns:
                    df_proc["valor"]=pd.to_numeric(df_proc["valor"],errors="coerce").fillna(0)
                    elig_proc=df_proc[df_proc["elegibilidade"]=="Elegível"] if "elegibilidade" in df_proc.columns else df_proc
                    forn_grp=elig_proc.groupby("fornecedora")["valor"].sum().reset_index()
                    forn_grp=forn_grp[forn_grp["valor"]>0].sort_values("valor",ascending=False)
                    if not forn_grp.empty:
                        total_forn=forn_grp["valor"].sum()
                        st.markdown("<p style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin:12px 0 6px'>POR FORNECEDORA</p>",unsafe_allow_html=True)
                        forn_rows=[{"Fornecedora":str(r["fornecedora"]),"Valor Recebido":fmt_brl(r["valor"])} for _,r in forn_grp.iterrows()]
                        forn_rows.append({"Fornecedora":"TOTAL GERAL","Valor Recebido":fmt_brl(total_forn)})
                        df_forn=pd.DataFrame(forn_rows); df_forn.index=range(1,len(df_forn)+1)
                        st.dataframe(df_forn,use_container_width=True,hide_index=False)
            except: pass

        st.markdown("---")



# ── MONITORIAS ─────────────────────────────────
def pagina_monitorias(ma):
    u=st.session_state.usuario
    header_page("Monitorias","Avaliação de qualidade")
    if u["role"]=="diretor": pagina_monitorias_diretor(ma); return
    eq=seletor_equipe(u["equipe"]); ops=buscar_operadores(eq)
    if not ops: st.warning("Cadastre operadores primeiro."); return
    if "mon_op_sel" not in st.session_state: st.session_state.mon_op_sel=None
    if "mon_modo" not in st.session_state: st.session_state.mon_modo=None
    if st.session_state.mon_op_sel is None:
        ultimo=st.session_state.pop("mon_ultimo_salvo",None)
        if ultimo:
            st.success(f"Monitoria salva! {ultimo['nome']} — Nota: {ultimo['nota']:.0f}% | Média: {ultimo['media']:.1f}% | Pontos: {ultimo['pontos']}")
            st.markdown(f'<a href="data:text/html;base64,{ultimo["b64"]}" download="Mon_{ultimo["nome"].replace(" ","_")}.html" style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:12px;margin-bottom:12px">Baixar PDF</a>',unsafe_allow_html=True)
        monts_eq=buscar_monitorias_equipe(eq,ma)
        if monts_eq:
            medias_eq=[calc_media_operador(op["_id"],ma)[0] for op in ops if calc_media_operador(op["_id"],ma)[1]>0]
            if medias_eq:
                me_eq=sum(medias_eq)/len(medias_eq)
                st_txt,st_cor,_=get_status_media(me_eq)
                st.markdown(
                    f"<div style='background:#0a1a0a;border:1px solid #1e3a1e;border-radius:10px;"
                    f"padding:12px 20px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center'>"
                    f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px'>MEDIA DA EQUIPE — {ma.replace('-',' ').upper()}</div>"
                    f"<div style='color:{st_cor};font-size:22px;font-weight:800;margin-top:2px'>{me_eq:.1f}%</div></div>"
                    f"<div style='text-align:right'><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase'>STATUS</div>"
                    f"<div style='color:{st_cor};font-size:13px;font-weight:600'>{st_txt}</div></div>"
                    f"</div>",unsafe_allow_html=True)
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px'><div style='color:#81c784;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600'>Selecione um operador</div><div style='color:#a5d6a7;font-size:12px'>{len(ops)} operadores · {ma.replace('-',' ')}</div></div>",unsafe_allow_html=True)
        for i in range(0,len(ops),4):
            cols=st.columns(4)
            for j,op in enumerate(ops[i:i+4]):
                media,n=calc_media_operador(op["_id"],ma)
                st_txt,st_cor,st_bg=get_status_media(media)
                ini=get_iniciais(op["nome"]); cini=get_cor_inicial(op["nome"])
                with cols[j]:
                    pontos_op=calc_pontos(media)
                    st.markdown(f"""<div style="background:#ffffff;border:1px solid #c8e0c8;border-radius:12px;padding:16px;text-align:center;margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,0.06)">
                        <div style="width:44px;height:44px;background:{cini};border-radius:50%;display:inline-flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:15px;margin-bottom:8px">{ini}</div>
                        <div style="color:#1a2e1a;font-weight:700;font-size:12px;margin-bottom:4px">{op['nome']}{'  ★' if op.get('pleno') else ''}</div>
                        <div style="color:{st_cor};font-size:20px;font-weight:800">{round(media)}%</div>
                        <div style="color:#5a8a5a;font-size:10px">{n} monitoria{'s' if n!=1 else ''}</div>
                        <div style="color:#2e7d32;font-size:11px;font-weight:600;margin-top:2px">{pontos_op} pts</div>
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
    if st.button("← Voltar"): st.session_state.mon_op_sel=None; st.session_state.mon_modo=None; st.rerun()
    st.markdown(f"<div style='background:#e8f5e9;border:1px solid #c8e0c8;border-radius:8px;padding:10px 16px;margin-bottom:12px'><span style='color:#2e7d32;font-weight:700;font-size:15px'>👤 {op['nome']}</span><span style='color:#5a8a5a;font-size:12px;margin-left:12px'>Média: {media_op:.0f}% · {n_op} monitoria{'s' if n_op!=1 else ''}</span></div>",unsafe_allow_html=True)
    st.markdown("---")
    t1,t2=st.tabs(["Nova Monitoria","Monitorias do Mês"])
    with t1:
        semana=st.selectbox("Qual monitoria é esta?",SEMANAS_MONITORIA,key="semana_sel")
        tipo_mon=st.radio("Tipo de Monitoria",["📞 Ligação","💬 Chat"],horizontal=True,key="tipo_mon_sel")
        tipo_key="ligacao" if "Ligação" in tipo_mon else "chat"
        prot_label="Protocolo da Ligação" if tipo_key=="ligacao" else "ID/Protocolo do Chat"
        prot=st.text_input(prot_label,placeholder="Ex: 20260520-001",key="prot_input")
        obs=st.text_area("Observações",placeholder="Anotações...",height=70,key="obs_input")
        st.markdown("---")
        # Carregar critérios e erros conforme tipo
        crits_usar = get_criterios() if tipo_key=="ligacao" else get_criterios_chat()
        erros_usar = get_erros_criticos() if tipo_key=="ligacao" else get_erros_criticos_chat()
        erros_m=[]; c1,c2=st.columns(2)
        for i,ec in enumerate(erros_usar):
            with (c1 if i%2==0 else c2):
                if st.checkbox(f"{ec['nome']}",key=f"ec_{ec['id']}_{tipo_key}"): erros_m.append(ec)
        st.markdown("---")
        zerada=len(erros_m)>0; crits_r=[]; nota=0 if zerada else 100
        if zerada:
            st.error("MONITORIA ZERADA — Erro crítico marcado!")
            for c in crits_usar: crits_r.append({**c,"passou":False})
        else:
            st.markdown("<p style='color:#e53935;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>ITENS DE QUALIDADE — MARQUE O QUE NÃO FOI FEITO</p>",unsafe_allow_html=True)
            for crit in crits_usar:
                c1,c2=st.columns([8,1])
                with c1: nao_passou=st.checkbox(f"{crit['nome']}",key=f"cr_{crit['id']}_{tipo_key}",value=False)
                with c2: st.markdown(f"<div style='padding-top:6px;color:#e53935;font-size:12px;font-weight:600;text-align:right'>−{crit['peso']} pts</div>",unsafe_allow_html=True)
                if crit.get('itens'):
                    for it in crit['itens']:
                        cor_it = "#f87171" if "obrigatório" in it.lower() or "!" in it else "#34d399"
                        st.markdown(f"<div style='padding:3px 0 3px 24px;font-size:12px;color:{cor_it};line-height:1.5'>• {it}</div>",unsafe_allow_html=True)
                passou=not nao_passou
                if not passou: nota-=crit["peso"]
                crits_r.append({**crit,"passou":passou})
        nota=max(0,nota)
        pontos_perdidos=100-nota
        cn="#2e7d32" if nota>=80 else "#f57f17" if nota>=60 else "#c62828"
        st.markdown(
            f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:10px;padding:14px 20px;margin-top:16px;display:flex;justify-content:space-between;align-items:center'>"
            f"<div><div style='color:#5a8a5a;font-size:11px'>Pontuação final (máx. 100 pts)</div>"
            f"<div style='color:#5a8a5a;font-size:11px'>Pontos perdidos: {pontos_perdidos}</div></div>"
            f"<div style='color:{cn};font-size:36px;font-weight:800'>{round(nota)}</div>"
            f"</div>",unsafe_allow_html=True)
        sk_salvo=f"mon_salvo_{op['_id']}_{semana}_{ma}_{tipo_key}"
        if not st.session_state.get(sk_salvo):
            if st.button("Salvar Monitoria",use_container_width=True,key="btn_salvar_mon"):
                if not prot.strip(): st.error(f"Preencha o {prot_label}!")
                else:
                    salvar_monitoria(eq,op["_id"],op["nome"],prot,obs,crits_r,erros_m,nota,ma,semana=semana,tipo=tipo_key)
                    mm,nm=calc_media_operador(op["_id"],ma)
                    html=gerar_pdf_monitoria(op["nome"],prot,obs,crits_r,erros_m,nota,mm,nm,ma)
                    b64=base64.b64encode(html.encode()).decode()
                    st.session_state[sk_salvo]={"nome":op["nome"],"nota":nota,"media":mm,"pontos":calc_pontos(mm),"b64":b64,"prot":prot}
                    st.rerun()
        else:
            salvo=st.session_state[sk_salvo]
            cn2="#2e7d32" if salvo['nota']>=80 else "#f57f17" if salvo['nota']>=60 else "#c62828"
            st.markdown(
                f"<div style='background:#0a1a0a;border:2px solid #00c853;border-radius:12px;padding:20px 24px;margin:16px 0'>"
                f"<div style='color:#00c853;font-weight:700;font-size:15px;margin-bottom:8px'>✓ Monitoria salva!</div>"
                f"<div style='color:#e8f5e9;font-size:13px'>Operador: <strong>{salvo['nome']}</strong></div>"
                f"<div style='color:#e8f5e9;font-size:13px'>Nota: <strong style='color:{cn2}'>{salvo['nota']:.0f}%</strong> | "
                f"Média: <strong>{salvo['media']:.1f}%</strong> | Pontos: <strong>{salvo['pontos']}</strong></div>"
                f"</div>",unsafe_allow_html=True)
            st.markdown(
                f'<a href="data:text/html;base64,{salvo["b64"]}" '
                f'download="Monitoria_{salvo["nome"].replace(" ","_")}_{salvo["prot"]}.html" '
                f'style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;'
                f'padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600;font-size:13px;margin-bottom:12px">'
                f'⬇ Baixar PDF da Monitoria</a>',
                unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
            if st.button("Concluir e Voltar",use_container_width=True,key="btn_concluir_mon"):
                ultimo=st.session_state.pop(sk_salvo,None)
                st.session_state.mon_op_sel=None
                st.session_state.mon_modo=None
                if ultimo: st.session_state["mon_ultimo_salvo"]=ultimo
                st.rerun()
    with t2:
        monts2=[m for m in buscar_monitorias_equipe(eq,ma) if m["opId"]==op["_id"]]
        if not monts2: st.info(f"Nenhuma monitoria para {op['nome']} em {ma.replace('-',' ')}.")
        else:
            ordem_semanas={s:i for i,s in enumerate(SEMANAS_MONITORIA)}
            monts2=sorted(monts2,key=lambda x:ordem_semanas.get(x.get("semana_mon",""),99))
            for m in monts2:
                nm=float(m.get("nota",0)); cm="#2e7d32" if nm>=80 else "#f57f17" if nm>=60 else "#c62828"
                st.markdown(f"<div style='background:#f8fdf8;border:1px solid #c8e0c8;border-radius:10px;padding:14px 18px;margin-bottom:8px;border-left:3px solid {cm}'><div style='color:#1a2e1a;font-weight:600'>{m.get('semana_mon','—')}</div><div style='color:#5a8a5a;font-size:11px'>Protocolo: {m.get('protocolo','—')} · {str(m.get('criadoEm',''))[:10]}</div><div style='color:{cm};font-size:18px;font-weight:800'>{int(nm)}%</div></div>",unsafe_allow_html=True)
                with st.expander("Ver detalhes"):
                    for c in m.get("criterios",[]):
                        passou=c.get("passou",True); cc="#2e7d32" if passou else "#c62828"
                        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:6px 12px;background:#f0f7f0;border-radius:6px;margin-bottom:4px;border-left:3px solid {cc}'><span style='color:#1a2e1a;font-size:12px'>{c.get('num','')} {c.get('nome','')}</span><span style='color:{cc};font-weight:600;font-size:12px'>{'Passou' if passou else 'Não passou'}</span></div>",unsafe_allow_html=True)
                    if m.get("observacao"): st.markdown(f"<div style='padding:8px 12px;background:#f0f7f0;border-radius:6px;border-left:3px solid #5a8a5a;color:#2d4a2d;font-size:12px'><strong>Obs:</strong> {m['observacao']}</div>",unsafe_allow_html=True)
                    mm2,nm2=calc_media_operador(op["_id"],ma)
                    hp=gerar_pdf_monitoria(op["nome"],m.get("protocolo",""),m.get("observacao",""),m.get("criterios",[]),m.get("errosCriticos",[]),nm,mm2,nm2,ma)
                    b64h=base64.b64encode(hp.encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64h}" download="Mon_{op["nome"].replace(" ","_")}_{m.get("semana_mon","").replace(" ","_").replace("—","")}.html" style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;padding:5px 12px;border-radius:5px;text-decoration:none;font-size:12px;margin-top:6px">⬇ Baixar PDF</a>',unsafe_allow_html=True)
                c1x,c2x=st.columns(2)
                with c2x:
                    if st.button("Excluir",key=f"del_op_{m['_id']}"): excluir_monitoria(m["_id"]); st.rerun()

def pagina_monitorias_diretor(ma):
    if "dir_op_sel" not in st.session_state: st.session_state.dir_op_sel=None
    if "dir_eq_sel" not in st.session_state: st.session_state.dir_eq_sel=None
    if st.session_state.dir_op_sel:
        op=st.session_state.dir_op_sel; eq=st.session_state.dir_eq_sel
        media_op,n_op=calc_media_operador(op["_id"],ma)
        st_txt,st_cor,_=get_status_media(media_op)
        if st.button("← Voltar"):
            st.session_state.dir_op_sel=None; st.session_state.dir_eq_sel=None; st.rerun()
        st.markdown(f"<div style='background:#0a1a0a;border:1px solid #1e3a1e;border-radius:12px;padding:16px 20px;margin-bottom:16px'><div style='color:#fff;font-weight:700;font-size:16px'>{op['nome']}</div><div style='color:#3a6a4a;font-size:12px'>Equipe {EQUIPES.get(eq,{}).get('nome','—')} · {ma.replace('-',' ')} · Média: <strong style='color:{st_cor}'>{media_op:.1f}%</strong></div></div>",unsafe_allow_html=True)
        monts_op=[m for m in buscar_monitorias_equipe(eq,ma) if m["opId"]==op["_id"]]
        if not monts_op: st.info("Nenhuma monitoria registrada neste mês.")
        else:
            for m in monts_op:
                nm=float(m.get("nota",0)); cm="#2e7d32" if nm>=80 else "#f57f17" if nm>=60 else "#c62828"
                st.markdown(f"<div style='background:#0a1a0a;border:1px solid #1e3a1e;border-radius:10px;padding:14px 18px;margin-bottom:8px;border-left:3px solid {cm}'><div style='color:#fff;font-weight:600'>{m.get('semana_mon','—')}</div><div style='color:#3a6a4a;font-size:11px'>Protocolo: {m.get('protocolo','—')} · {str(m.get('criadoEm',''))[:10]}</div><div style='color:{cm};font-size:18px;font-weight:800'>{nm:.0f}%</div></div>",unsafe_allow_html=True)
                with st.expander("Ver detalhes"):
                    for c in m.get("criterios",[]):
                        passou=c.get("passou",True); cc="#2e7d32" if passou else "#c62828"
                        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:6px 12px;background:#0a1a0a;border-radius:6px;margin-bottom:4px;border-left:3px solid {cc}'><span style='color:#e8f5e9;font-size:12px'>{c.get('num','')} {c.get('nome','')}</span><span style='color:{cc};font-weight:600;font-size:12px'>{'Passou' if passou else 'Nao passou'}</span></div>",unsafe_allow_html=True)
                    if m.get("observacao"): st.markdown(f"<div style='padding:8px 12px;background:#0a1a0a;border-radius:6px;border-left:3px solid #3a6a4a;color:#8ab89a;font-size:12px'><strong>Obs:</strong> {m['observacao']}</div>",unsafe_allow_html=True)
                    hp=gerar_pdf_monitoria(m["opNome"],m.get("protocolo",""),m.get("observacao",""),m.get("criterios",[]),m.get("errosCriticos",[]),nm,media_op,n_op,ma)
                    b64=base64.b64encode(hp.encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64}" download="Mon_{m["opNome"].replace(" ","_")}.html" style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;padding:5px 12px;border-radius:5px;text-decoration:none;font-size:12px">Baixar PDF</a>',unsafe_allow_html=True)
        return
    st.markdown("### Visão Geral — Monitorias por Equipe")
    todas_medias=[]
    for eq in EQUIPES:
        ops=buscar_operadores(eq)
        if not ops: continue
        monts=buscar_monitorias_equipe(eq,ma)
        if not monts: continue
        medias={op["nome"]:(op,calc_media_operador(op["_id"],ma)) for op in ops}
        medias={k:v for k,v in medias.items() if v[1][1]>0}
        if not medias: continue
        me=sum(v[1][0] for v in medias.values())/len(medias)
        todas_medias.append(me)
        st.markdown(f"<div style='background:#0a1a0a;border:1px solid #1e3a1e;border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:3px solid #00c853'><div style='display:flex;justify-content:space-between;align-items:center'><div style='font-size:15px;font-weight:700;color:#fff'>Equipe {EQUIPES[eq]['nome']}</div><div style='text-align:right'><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase'>MEDIA DA EQUIPE</div><div style='color:{cor_pct(me)};font-size:24px;font-weight:800'>{me:.1f}%</div></div></div></div>",unsafe_allow_html=True)
        cols_op=st.columns(4)
        for idx_op,(nome,(op_obj,(media,n))) in enumerate(sorted(medias.items(),key=lambda x:-x[1][1][0])):
            st_txt,st_cor,_=get_status_media(media)
            with cols_op[idx_op%4]:
                st.markdown(f"<div style='background:#0d1a0d;border:1px solid #1e3a1e;border-radius:10px;padding:12px;text-align:center;margin-bottom:8px'><div style='color:#fff;font-weight:600;font-size:12px'>{nome}</div><div style='color:{st_cor};font-size:18px;font-weight:800'>{media:.1f}%</div><div style='color:#3a6a4a;font-size:10px'>{n} monitoria{'s' if n!=1 else ''}</div></div>",unsafe_allow_html=True)
                if st.button("Ver detalhes",key=f"dir_op_{op_obj['_id']}",use_container_width=True):
                    st.session_state.dir_op_sel=op_obj; st.session_state.dir_eq_sel=eq; st.rerun()
        st.markdown("---")
    if todas_medias:
        mg=sum(todas_medias)/len(todas_medias)
        st.markdown(f"<div style='background:#001a0a;border:2px solid #1e3a1e;border-radius:12px;padding:20px 24px;text-align:center'><div style='color:#3a6a4a;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px'>MEDIA GERAL</div><div style='color:{cor_pct(mg)};font-size:32px;font-weight:800'>{mg:.1f}%</div></div>",unsafe_allow_html=True)

# ── ANÁLISE DOS OPERADORES ─────────────────────
def pagina_analise_operadores(ma):
    u=st.session_state.usuario
    eqs=list(EQUIPES.keys()) if u["role"] in ["diretor","admin"] else [u["equipe"]]
    header_page("Análise dos Operadores",f"Resultado comparativo · {ma.replace('-',' ')}")
    idx=MESES_NOMES.index(ma.split("-")[0]); ano=int(ma.split("-")[1])
    ma_ant=f"{MESES_NOMES[11]}-{ano-1}" if idx==0 else f"{MESES_NOMES[idx-1]}-{ano}"
    st.markdown("---")
    for eq in eqs:
        ops=buscar_operadores(eq)
        if not ops: continue
        lat=buscar_lancamentos(ma,eq); lan=buscar_lancamentos(ma_ant,eq)
        if not lat: continue
        ul=lat[0]; ul_an=lan[0] if lan else None
        mops=buscar_metas_equipe(ma,eq)
        rows=[]
        for op in ops:
            vat=get_val_op(ul.get("agentes",{}),op["_id"],op["nome"])
            van=get_val_op(ul_an.get("agentes",{}),op["_id"],op["nome"]) if ul_an else 0
            meta=float(mops.get(op["_id"],0))
            pct=(vat/meta*100) if meta>0 else 0
            var_op=calc_variacao(vat,van)
            sv="↑" if (var_op or 0)>=0 else "↓"
            rows.append({"Operador":("★ " if op.get("pleno") else "")+op["nome"],"Recebido":fmt_brl(vat) if vat>0 else "—","Meta":fmt_brl(meta) if meta>0 else "—","% Meta":f"{pct:.1f}%" if meta>0 else "—","Mês Ant.":fmt_brl(van) if van>0 else "—","Variação":f"{sv} {abs(var_op):.1f}%" if var_op is not None else "—","_v":vat})
        st.markdown(f"**Equipe {EQUIPES[eq]['nome']}**")
        df=pd.DataFrame(rows).sort_values("_v",ascending=False).drop(columns=["_v"]).reset_index(drop=True)
        df.index=range(1,len(df)+1)
        st.dataframe(df,use_container_width=True)
        st.markdown("---")

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
    elig=df[df["elegibilidade"]=="Elegível"] if "elegibilidade" in df.columns else df
    with c3:
        forns=["Todas"]+sorted(df["fornecedora"].dropna().unique().tolist())
        ff=st.selectbox("Fornecedora",forns)
    if ff!="Todas":
        df=df[df["fornecedora"]==ff]
        elig=elig[elig["fornecedora"]==ff] if "fornecedora" in elig.columns else elig
    st.markdown("---")
    val_rec=float(elig["valor"].sum()) if not elig.empty else 0
    cli_unic=int(elig["uc_cpf"].nunique()) if "uc_cpf" in elig.columns and not elig.empty else 0
    tot_bol=len(elig)
    c1,c2,c3=st.columns(3)
    c1.metric("Valor Recuperado",fmt_brl(val_rec))
    c2.metric("Clientes Únicos",f"{cli_unic:,}")
    c3.metric("Total Boletos",f"{tot_bol:,}")
    st.markdown("---")
    t1,t2,t3,t4=st.tabs(["Aging","Fornecedoras","Evolução","Por Equipe"])
    with t1:
        if "aging" in df.columns:
            ag=df.groupby("aging").agg(Boletos=("uc_cpf","count"),Valor=("valor","sum")).reset_index()
            ag["Valor"]=ag["Valor"].apply(fmt_brl)
            st.dataframe(ag.rename(columns={"aging":"Faixa"}),use_container_width=True,hide_index=True)
    with t2:
        if "fornecedora" in df.columns:
            fdf=df.groupby("fornecedora").agg(Boletos=("uc_cpf","count"),Valor=("valor","sum")).reset_index()
            fdf=fdf.sort_values("Valor",ascending=False)
            fdf["Valor"]=fdf["Valor"].apply(fmt_brl)
            st.dataframe(fdf.rename(columns={"fornecedora":"Fornecedora"})[["Fornecedora","Boletos","Valor"]],use_container_width=True,hide_index=True)
    with t3:
        da=buscar_processamentos()
        if not da.empty:
            da["valor"]=pd.to_numeric(da["valor"],errors="coerce").fillna(0)
            da_elig=da[da["elegibilidade"]=="Elegível"] if "elegibilidade" in da.columns else da
            if "_mes_ano" in da_elig.columns:
                ev=da_elig.groupby("_mes_ano")["valor"].sum().reset_index()
                ev.columns=["Mês","Valor"]
                st.bar_chart(ev.sort_values("Mês").set_index("Mês"),color="#2daf5c")
    with t4:
        if "_equipe" in df.columns:
            ed=df.groupby("_equipe").agg(Boletos=("uc_cpf","count"),Valor=("valor","sum")).reset_index()
            ed["Equipe"]=ed["_equipe"].map(lambda x:EQUIPES.get(x,{}).get("nome",x))
            ed["Valor"]=ed["Valor"].apply(fmt_brl)
            st.dataframe(ed[["Equipe","Boletos","Valor"]],use_container_width=True,hide_index=True)


def pagina_upload(ma):
    u=st.session_state.usuario
    header_page('Upload de Bases Mensais','Processamento automatico')
    eq=seletor_equipe(u['equipe'] or 'tamires')
    col_up,col_hist=st.columns([1,1])

    with col_up:
        st.markdown('<p style="color:#3a6a4a;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">PROCESSAR BASE</p>',unsafe_allow_html=True)
        st.markdown('<div style="background:#0d1a0d;border:1px solid #1e3a1e;border-radius:10px;padding:12px 16px;margin-bottom:12px;font-size:12px;color:#5a9a70;line-height:1.8">'
            'Suba um <strong style="color:#e8f5e9">.xlsx</strong> com as abas:<br>'
            '<strong>PAGOS</strong> | <strong>CHAT</strong> | <strong>LIGACOES</strong> | <strong>DISPAROS</strong>'
            '</div>',unsafe_allow_html=True)
        arq=st.file_uploader('Planilha (.xlsx)',type=['xlsx'],label_visibility='collapsed',key='base_unica')
        if arq:
            try:
                xls=pd.ExcelFile(arq)
                ah=' | '.join(xls.sheet_names)
                arq.seek(0)
                st.markdown(f'<div style="background:#0a1a0a;border:1px solid #1e3a1e;border-radius:6px;padding:8px 12px;margin:8px 0;color:#5a9a70;font-size:12px"><strong style="color:#e8f5e9">{arq.name}</strong><br>Abas: {ah}</div>',unsafe_allow_html=True)
            except: pass
        if st.button('PROCESSAR',use_container_width=True):
            if not arq: st.error('Selecione a planilha antes de processar!'); return
            arq.seek(0)
            with st.spinner('Processando...'):
                df_res,erros,abas=processar_base_unica(arq,eq,ma)
            for e in erros: st.error(e)
            if df_res is not None and not df_res.empty:
                st.session_state['df_proc_temp']=df_res
                st.session_state['proc_eq']=eq
                st.session_state['proc_ma']=ma
                st.session_state['proc_abas']=abas
                st.rerun()
        if (st.session_state.get('df_proc_temp') is not None and
            st.session_state.get('proc_eq')==eq and
            st.session_state.get('proc_ma')==ma):
            df_res=st.session_state['df_proc_temp']
            abas=st.session_state.get('proc_abas',[])
            elig=df_res[df_res['elegibilidade']=='Elegível'] if 'elegibilidade' in df_res.columns else df_res
            ve=elig['valor'].sum() if 'valor' in elig.columns else 0
            ce=elig['uc_cpf'].nunique() if 'uc_cpf' in elig.columns else 0
            if abas: st.info(f"Abas: {', '.join(abas)}")
            st.success(f"{len(df_res):,} registros processados!")
            c1,c2,c3=st.columns(3)
            c1.metric('Valor Recebido',fmt_brl(ve))
            c2.metric('Boletos',f'{len(elig):,}')
            c3.metric('Clientes',f'{ce:,}')
            st.markdown('---')
            col1,col2=st.columns(2)
            with col1:
                if st.button('Salvar Resultado',use_container_width=True,key='btn_salvar_proc'):
                    salvar_processamento(ma,eq,df_res,st.session_state.usuario.get('nome',''))
                    st.session_state['df_proc_temp']=None
                    st.success('Resultado salvo!')
                    st.rerun()
            with col2:
                if st.button('Descartar',use_container_width=True,key='btn_desc'):
                    st.session_state['df_proc_temp']=None; st.rerun()
            cols_show=[c for c in ['uc_cpf','data_pagamento','valor','fornecedora','elegibilidade','aging'] if c in df_res.columns]
            st.dataframe(df_res[cols_show].head(30) if cols_show else df_res.head(30),use_container_width=True)

    with col_hist:
        st.markdown('<p style="color:#3a6a4a;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">HISTORICO DE BASES PROCESSADAS</p>',unsafe_allow_html=True)
        u_hist=st.session_state.usuario
        if u_hist['role'] in ['admin','diretor']:
            hist_geral=buscar_historico_geral()
        else:
            hist_geral=buscar_historico_geral(equipe_id=u_hist.get('equipe'))
        if not hist_geral:
            st.info('Nenhuma base processada ainda.')
        else:
            for h in hist_geral:
                forns=h.get('fornecedoras',[])
                forn_str=', '.join(forns[:3])+('...' if len(forns)>3 else '') if forns else '---'
                equipe_nome=EQUIPES.get(h.get('equipeId',''),{}).get('nome','---')
                usuario_nome=h.get('usuarioNome') or equipe_nome
                data_str=str(h.get('criadoEm',''))[:16]
                val=float(h.get('valorElegivel',0))
                st.markdown(
                    f"<div style='background:#0a1a0a;border:1px solid #1e3a1e;border-radius:10px;"
                    f"padding:12px 16px;margin-bottom:6px;border-left:3px solid #00c853'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px'>"
                    f"<div>"
                    f"<div style='color:#ffffff;font-weight:600;font-size:13px'>{equipe_nome} -- {h.get('mesAno','').replace('-',' ')}</div>"
                    f"<div style='color:#3a6a4a;font-size:11px;margin-top:2px'>Por: {usuario_nome} | {data_str}</div>"
                    f"<div style='color:#3a6a4a;font-size:11px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px'>Fornecedoras: {forn_str}</div>"
                    f"</div>"
                    f"<div style='text-align:right'>"
                    f"<div style='color:#00c853;font-weight:700;font-size:14px'>{fmt_brl(val)}</div>"
                    f"<div style='color:#3a6a4a;font-size:11px'>{h.get('boletosElegiveis',0):,} boletos</div>"
                    f"</div></div></div>",
                    unsafe_allow_html=True)
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            if st.button('Exportar Historico Excel',use_container_width=True,key='btn_exp_hist'):
                rows=[{'Gestor':h.get('usuarioNome','---'),'Equipe':EQUIPES.get(h.get('equipeId',''),{}).get('nome','---'),'Mes':h.get('mesAno','---'),'Fornecedoras':', '.join(h.get('fornecedoras',[])),'Valor Recebido':fmt_brl(h.get('valorElegivel',0)),'Boletos':h.get('boletosElegiveis',0),'Data':str(h.get('criadoEm',''))[:16]} for h in hist_geral]
                out=io.BytesIO()
                with pd.ExcelWriter(out,engine='xlsxwriter') as w: pd.DataFrame(rows).to_excel(w,index=False)
                st.download_button('Baixar Excel',data=out.getvalue(),file_name='historico_bases.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key='dl_hist_exp')

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
    with c3:
        eq=seletor_equipe(u.get("equipe") or "tamires",key_suffix="_inad") if (is_adm or is_dir) else u["equipe"]
    if is_dir or is_adm:
        forns_disp = ["Todas"] + FORNECEDORAS_TODAS
    else:
        forns_disp = ["Todas"] + FORNECEDORAS_POR_GESTOR.get(eq or u.get("equipe",""), FORNECEDORAS_TODAS)
    with c2:
        fs=st.selectbox("Fornecedora", forns_disp, key="inad_forn")
    st.markdown("---")
    doc=buscar_inadimplencia(ms,eq or "tamires")
    dados=doc.get("dados",{}) if doc else {}
    with st.expander("Subir planilha de inadimplência",expanded=not bool(dados)):
        st.markdown("<p style='color:#555;font-size:13px'>Suba a planilha com as abas por fornecedora.</p>",unsafe_allow_html=True)
        arq_i=st.file_uploader("Planilha de inadimplência (.xlsx)",type=["xlsx"],key="arq_inad")
        if arq_i and st.button("Processar planilha",key="btn_proc_inad"):
            st.info("Estrutura da planilha ainda sendo mapeada. Use a edição manual por enquanto.")
    st.markdown("---")
    edit=st.checkbox("Editar manualmente",key="edit_inad")
    if is_dir or is_adm:
        forns_usuario = FORNECEDORAS_TODAS
    else:
        forns_usuario = FORNECEDORAS_POR_GESTOR.get(u.get('equipe',''), FORNECEDORAS_TODAS)
    lista = forns_usuario if fs=='Todas' else [fs]
    st.markdown("""<style>
    .it{width:100%;border-collapse:collapse;font-size:11px}
    .it th{background:#1b5e20;color:#fff;padding:6px 8px;text-align:center;border:1px solid #145214;white-space:nowrap}
    .it th.thl{text-align:left}.it th.ths{background:#2e7d32;font-size:10px}
    .it td{border:1px solid #c8e6c9;padding:5px 8px;text-align:right;font-size:11px;color:#1b5e20;background:#fff}
    .it td.tdn{text-align:left;font-weight:600;background:#f1f8f1}
    .it td.tdp{color:#e53935;font-weight:600}.it td.tdf{color:#1565c0;font-weight:500}
    .it tr.trt td{background:#e8f5e9;font-weight:700}
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

# ── MINHA CONTA ──────────────────────────────
def pagina_minha_conta():
    u=st.session_state.usuario
    header_page('Minha Conta', u['nome'])
    t1,t2,t3=st.tabs(['🔒  Senha','👥  Operadores','📋  Critérios'])
    with t1:
        st.markdown('<p style="color:#5a9a70;font-size:13px;margin-bottom:20px">Altere sua senha de acesso</p>',unsafe_allow_html=True)
        sa =st.text_input('Senha atual',    type='password',placeholder='senha atual',   key='mc_sa')
        sn =st.text_input('Nova senha',     type='password',placeholder='mín. 8 caracteres',key='mc_sn')
        sc2=st.text_input('Confirmar senha',type='password',placeholder='repita a nova senha',key='mc_sc')
        if st.button('Salvar Senha',key='mc_btn_senha',use_container_width=True):
            uid=u['id']; sc=u.get('senha')
            try:
                doc=get_db().usuarios_senhas.find_one({'_id':uid})
                if doc and doc.get('senha'): sc=doc['senha']
            except: pass
            if not sa: st.error('Digite a senha atual.')
            elif sa!=sc: st.error('Senha atual incorreta.')
            elif len(sn)<8: st.error('Mínimo 8 caracteres.')
            elif sn!=sc2: st.error('Confirmação não confere.')
            else: salvar_senha_usuario(uid,sn); buscar_senha_usuario.clear(); st.success('✅ Senha alterada com sucesso!')
    with t2:
        # Diretor pode editar operadores de qualquer equipe
        if u["role"]=="diretor":
            eq_opts=list(EQUIPES.keys())
            eq_labels=[f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
            eq_sel=st.selectbox("Selecionar equipe:",eq_labels,key="dir_eq_ops")
            eq=eq_opts[eq_labels.index(eq_sel)]
        else:
            eq=u.get('equipe')
        if not eq:
            st.info('Gestão de operadores disponível apenas para gestores.')
        else:
            st.markdown(f'**Equipe {EQUIPES.get(eq,{}).get("nome",eq)}**')
            st.markdown('---')
            c1,c2,c3=st.columns([3,1,1])
            with c1: nn=st.text_input('Nome completo',placeholder='Nome do operador',key='mc_op_novo')
            with c2: np=st.checkbox('Pleno',key='mc_op_pleno')
            with c3:
                st.markdown("<div style='margin-top:28px'>",unsafe_allow_html=True)
                if st.button('Adicionar',use_container_width=True,key='mc_op_add'):
                    if nn.strip():
                        salvar_operador(eq,nn.strip(),np)
                        buscar_operadores.clear()
                        st.success(f"✅ {nn} adicionado com sucesso!"); st.rerun()
                    else: st.error('Digite o nome.')
                st.markdown('</div>',unsafe_allow_html=True)
            st.markdown('---')
            ops=buscar_operadores(eq)
            if not ops: st.info('Nenhum operador cadastrado.')
            else:
                for op in ops:
                    c1,c2,c3,c4=st.columns([3,1,1,1])
                    with c1: ne=st.text_input('',value=op['nome'],key=f'mc_n_{op["_id"]}',label_visibility='collapsed')
                    with c2: npl=st.checkbox('Pleno',value=op.get('pleno',False),key=f'mc_pl_{op["_id"]}')
                    with c3:
                        if st.button('Salvar',key=f'mc_s_{op["_id"]}',use_container_width=True):
                            atualizar_operador(op['_id'],ne,npl)
                            buscar_operadores.clear()
                            st.success(f"✅ {ne} atualizado com sucesso!"); st.rerun()
                    with c4:
                        if st.button('Excluir',key=f'mc_d_{op["_id"]}',use_container_width=True):
                            excluir_operador(op['_id']); st.rerun()
    with t3:
        crits=get_criterios()
        st.markdown('**Critérios de avaliação das monitorias**')
        st.markdown('---')
        ce=[]
        for i,c in enumerate(crits):
            with st.expander(f"{c['num']} {c['nome']} — Peso {c['peso']}",expanded=False):
                c1,c2,c3=st.columns([3,1,1])
                with c1: nm=st.text_input('Nome',value=c['nome'],key=f'mc_cn_{i}')
                with c2: ps=st.number_input('Peso',min_value=1,max_value=100,value=int(c['peso']),key=f'mc_cp_{i}')
                with c3: ob=st.checkbox('Obrigatório',value=c.get('obrigatorio',False),key=f'mc_co_{i}')
                it=st.text_area('Itens (um por linha)',value='\n'.join(c.get('itens',[])),height=80,key=f'mc_ci_{i}')
                ce.append({'id':c['id'],'num':c['num'],'nome':nm,'peso':ps,'obrigatorio':ob,'itens':[x.strip() for x in it.split('\n') if x.strip()]})
        st.markdown('---')
        if st.button('Salvar Critérios',use_container_width=True,key='mc_crit_save'):
            salvar_criterios(ce); st.success('Critérios salvos!'); st.rerun()

# ── MEET CALL ─────────────────────────────────
def pagina_meetcall(ma):
    u=st.session_state.usuario
    if u.get("equipe") not in ["metcool","luciano"] and u["role"] not in ["admin","diretor"]:
        st.warning("Acesso restrito."); return
    header_page("Meet Call","Lançamento da equipe Meet Call")
    ops_mc=buscar_operadores("metcool")
    if not ops_mc:
        st.warning("Nenhum operador cadastrado na Meet Call.")
        return
    ms_mc=buscar_metas_equipe(ma,"metcool")
    mg_mc=float(buscar_meta_gestora(ma,"metcool").get("metaGestora",0))
    if st.session_state.get("mc_ultimo_salvo"):
        st.success(st.session_state.mc_ultimo_salvo)
        st.session_state.mc_ultimo_salvo=""

    st.markdown("### Configuração")
    c1,c2,c3=st.columns([2,1,1])
    with c1:
        hoje=date.today()
        data_sel=st.date_input("Data *",value=hoje,key=f"mc_data_{ma}")
        eh_fech=st.checkbox("Fechamento do Mês",key=f"mc_fech_{ma}")
    with c2: dt_mc=st.number_input("Dias Trabalhados *",min_value=0,max_value=31,value=0,key=f"mc_dt_{ma}")
    with c3: td_mc=st.number_input("Total Dias *",min_value=0,max_value=31,value=0,key=f"mc_td_{ma}")

    # Recebido Geral
    mc_doc=buscar_lancamento_meetcall(ma)
    rg_atual=float(mc_doc.get("recGeralTotal",mc_doc.get("recGeral",0)))
    st.markdown("---")
    usar_rg_manual=st.checkbox("Inserir Recebido Geral manualmente",key=f"mc_rg_chk_{ma}")
    if usar_rg_manual:
        rg_str=st.text_input("Recebido Geral (R$)",value=fmt_brl(rg_atual) if rg_atual>0 else "",placeholder="R$ 0,00",key=f"mc_rg_manual_{ma}")
        rg_total=parse_brl(rg_str)
    else:
        rg_total=rg_atual

    st.markdown("---")
    st.markdown("### Valores por Operador")

    # Importar via Excel
    mostrar_imp_mc=st.checkbox("Importar via Excel",key=f"chk_imp_mc_{ma}")
    if mostrar_imp_mc:
        arq_imp_mc=st.file_uploader("Planilha Excel (.xlsx)",type=["xlsx"],key=f"imp_mc_{ma}")
        if arq_imp_mc:
            arq_imp_mc.seek(0)
            res_mc,err_mc=importar_excel_operadores(arq_imp_mc,ops_mc)
            if err_mc:
                st.error(err_mc)
            elif res_mc:
                prev_mc=[]
                for r in res_mc:
                    icone=r['op']['nome'] if r['op'] and r['status']!='ambiguo' else ("Ambíguo" if r['status']=='ambiguo' else "Não encontrado")
                    row={"Excel":r['nome_excel'],"Sistema":icone,"Valor":fmt_brl(r['valor'])}
                    prev_mc.append(row)
                st.dataframe(pd.DataFrame(prev_mc),use_container_width=True,hide_index=True)
                if st.button("Confirmar Importação",use_container_width=True,key=f"imp_mc_confirmar_{ma}"):
                    for r in res_mc:
                        if r['op'] and r['status']!='ambiguo' and r['valor']>0:
                            st.session_state[f"mc_op_{ma}_{r['op']['_id']}"]=r['valor']
                    st.success("Valores importados! Revise e salve.")
                    st.rerun()

    vi_mc={}
    for op in ops_mc:
        meta=float(ms_mc.get(op["_id"],0))
        c1,c2,c3=st.columns([3,2,2])
        with c1: st.markdown(f"<div style='padding-top:10px;color:#1a3a1a;font-weight:500'>{op['nome']}</div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div style='padding-top:10px;color:#2e7d32;font-size:13px'>{fmt_brl(meta) if meta>0 else '—'}</div>",unsafe_allow_html=True)
        with c3:
            mc_op_key=f"mc_op_{ma}_{op['_id']}"
            val_mc=st.session_state.get(mc_op_key,0.0)
            vi_mc[op["_id"]]=st.number_input("v",label_visibility="collapsed",min_value=0.0,step=100.0,format="%.2f",value=float(val_mc) if val_mc else 0.0,key=mc_op_key)

    tc_mc=sum(vi_mc.values())
    sem_mc=max(0,rg_total-tc_mc) if rg_total>0 else 0
    pct_mc=(rg_total/mg_mc*100) if mg_mc>0 else 0

    st.markdown("---")
    c1,c2,c3=st.columns(3)
    c1.metric("Recebido Geral",fmt_brl(rg_total))
    c2.metric("Com Interação",fmt_brl(tc_mc))
    c3.metric("Sem Interação",fmt_brl(sem_mc))
    st.markdown(f"<div style='background:#0a2414;border-radius:8px;padding:12px 16px;margin:12px 0 16px'><span style='color:#5a9a70;font-size:11px'>META: {fmt_brl(mg_mc)} | % META: {pct_mc:.1f}%</span></div>",unsafe_allow_html=True)

    if st.button("Salvar Lançamento Meet Call",use_container_width=True,key="mc_salvar"):
        errs=[]
        if dt_mc==0: errs.append("Dias Trabalhados é obrigatório.")
        if td_mc==0: errs.append("Total de Dias é obrigatório.")
        if tc_mc==0: errs.append("Preencha pelo menos um valor de operador.")
        if errs:
            for e in errs: st.error(e)
        else:
            label="Fechamento do Mês" if eh_fech else data_sel.strftime("%d/%m/%Y")
            ag_mc={op["_id"]:{"valorRecebido":vi_mc[op["_id"]],"nome":op["nome"]} for op in ops_mc}
            criar_lancamento(ma,"metcool",str(data_sel),label,ag_mc,tc_mc,0,dt_mc,td_mc)
            salvar_lancamento_meetcall(ma,0,tc_mc,rg_total)
            buscar_lancamentos.clear()
            st.session_state.mc_ultimo_salvo=f"✅ Lançamento de {label} salvo com sucesso! Total: {fmt_brl(tc_mc)}"
            st.rerun()

    # Histórico
    lancs_mc=buscar_lancamentos(ma,"metcool")
    if lancs_mc:
        st.markdown("---")
        st.markdown("<p style='color:#5a8a5a;font-size:11px;text-transform:uppercase;margin-bottom:8px'>Lançamentos do mês</p>",unsafe_allow_html=True)
        for lanc in reversed(lancs_mc):
            soma=sum(float(v.get("valorRecebido",0) if isinstance(v,dict) else v) for v in lanc.get("agentes",{}).values())
            with st.expander(f"{lanc.get('label','')} — {fmt_brl(soma)}"):
                rows=[{"Operador":op["nome"],"Valor":fmt_brl(get_val_op(lanc.get("agentes",{}),op["_id"],op["nome"]))} for op in ops_mc]
                st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                if st.button("Excluir",key=f"mc_del_{lanc['_id']}"): excluir_lancamento(lanc["_id"]); st.rerun()

# ── MAIN ───────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login()
        return
    if "ids_corrigidos" not in st.session_state:
        st.session_state.ids_corrigidos=True
    if 'meetcall_limpo' not in st.session_state:
        st.session_state.meetcall_limpo = True
        try:
            db = get_db()
            for nome in OPERADORES_MEETCALL:
                ops_dup = list(db.operadores.find({"equipeId":"metcool","nome":nome}).sort("criadoEm",1))
                if len(ops_dup) > 1:
                    for op_dup in ops_dup[1:]: db.operadores.delete_one({"_id":op_dup["_id"]})
                ops_dup2 = list(db.operadores.find({"equipeId":"luciano","nome":nome}).sort("criadoEm",1))
                if len(ops_dup2) > 1:
                    for op_dup2 in ops_dup2[1:]: db.operadores.delete_one({"_id":op_dup2["_id"]})
        except: pass
    if 'meetcall_migrado' not in st.session_state:
        st.session_state.meetcall_migrado=True
        try: migrar_meetcall_para_luciano()
        except: pass
    ma,pag=render_sidebar()
    u=st.session_state.usuario
    area = st.empty()
    with area.container():
        if u["role"]=="diretor":
            if   "Quadro"        in pag: pagina_quadro(ma)
            elif "Visualização"  in pag: pagina_dashboard_executivo()
            elif "Operadores"    in pag: pagina_analise_operadores(ma)
            elif "Monitorias"    in pag: pagina_monitorias(ma)
            elif "Inadimplência" in pag: pagina_inadimplencia(ma)
            elif "Metas"         in pag: pagina_metas(ma)
            elif "Minha Conta"   in pag: pagina_minha_conta()
        elif u["role"]=="admin":
            if   "Quadro"        in pag: pagina_quadro(ma)
            elif "Lançamento"    in pag: pagina_lancamento(ma)
            elif "Visualização"  in pag: pagina_dashboard_executivo()
            elif "Operadores"    in pag: pagina_analise_operadores(ma)
            elif "Monitorias"    in pag: pagina_monitorias(ma)
            elif "Meet Call"     in pag: pagina_meetcall(ma)
            elif "Upload"        in pag: pagina_upload(ma)
            elif "Inadimplência" in pag: pagina_inadimplencia(ma)
            elif "Metas"         in pag: pagina_metas(ma)
            elif "Minha Conta"   in pag: pagina_minha_conta()
        elif u.get("equipe")=="metcool":
            if   "Meet Call"     in pag: pagina_meetcall(ma)
            elif "Operadores"    in pag: pagina_analise_operadores(ma)
            elif "Monitorias"    in pag: pagina_monitorias(ma)
            elif "Minha Conta"   in pag: pagina_minha_conta()
        else:
            if   "Quadro"        in pag: pagina_quadro(ma)
            elif "Lançamento"    in pag: pagina_lancamento(ma)
            elif "Operadores"    in pag: pagina_analise_operadores(ma)
            elif "Monitorias"    in pag: pagina_monitorias(ma)
            elif "Meet Call"     in pag: pagina_meetcall(ma)
            elif "Upload"        in pag: pagina_upload(ma)
            elif "Inadimplência" in pag: pagina_inadimplencia(ma)
            elif "Metas"         in pag: pagina_metas(ma)
            elif "Minha Conta"   in pag: pagina_minha_conta()

if __name__=="__main__":
    main()
