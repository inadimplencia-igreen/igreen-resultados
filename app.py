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
.stApp { background-color: #0a1628; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d2137,#0a1628); border-right:1px solid #1e3a5f; }
[data-testid="stMetric"] { background:linear-gradient(135deg,#0d2137,#112940); border:1px solid #1e3a5f; border-radius:12px; padding:20px !important; border-left:3px solid #2daf5c; }
[data-testid="stMetricValue"] { color:#ffffff !important; font-size:26px !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { color:#7fa8c9 !important; font-size:11px !important; text-transform:uppercase; letter-spacing:1px; }
.stButton > button { background:linear-gradient(135deg,#1a6b35,#2daf5c) !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important; }
.stButton > button:hover { background:linear-gradient(135deg,#2daf5c,#3dd670) !important; }
h1 { color:#ffffff !important; font-size:22px !important; font-weight:700 !important; }
h2 { color:#e6edf3 !important; font-size:18px !important; }
h3 { color:#7fa8c9 !important; font-size:12px !important; text-transform:uppercase; letter-spacing:1.5px; }
hr { border-color:#1e3a5f !important; }
p, label { color:#c9d8e8 !important; }
.stTextInput input, .stNumberInput input { background:#0d2137 !important; border:1px solid #1e3a5f !important; color:#e6edf3 !important; border-radius:8px !important; }
[data-testid="stFileUploader"] { background:#0d2137 !important; border:2px dashed #1e3a5f !important; border-radius:12px !important; }
.stTabs [data-baseweb="tab-list"] { background:#0d2137 !important; border-radius:8px !important; padding:4px !important; }
.stTabs [data-baseweb="tab"] { color:#7fa8c9 !important; border-radius:6px !important; }
.stTabs [aria-selected="true"] { background:#1a6b35 !important; color:#ffffff !important; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#0a1628; }
::-webkit-scrollbar-thumb { background:#1e3a5f; border-radius:3px; }
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
    doc_id = f"{mes_ano}__{semana_id}__{equipe_id}"
    get_db().resultados.update_one({"_id":doc_id},{"$set":{"_id":doc_id,"mesAno":mes_ano,"semanaId":semana_id,"equipeId":equipe_id,**dados,"atualizadoEm":datetime.now()}},upsert=True)

def buscar_resultados_mes(mes_ano):
    docs = list(get_db().resultados.find({"mesAno":mes_ano}))
    return {d["_id"]:d for d in docs}

def salvar_config(mes_ano, equipe_id, tipo, dados):
    doc_id = f"{tipo}__{mes_ano}__{equipe_id}"
    get_db().configuracoes.update_one({"_id":doc_id},{"$set":{"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,**dados}},upsert=True)

def buscar_config(mes_ano, equipe_id, tipo):
    doc_id = f"{tipo}__{mes_ano}__{equipe_id}"
    return get_db().configuracoes.find_one({"_id":doc_id}) or {}

def salvar_processamento(mes_ano, equipe_id, df):
    doc_id = f"proc__{mes_ano}__{equipe_id}"
    get_db().processamentos.update_one({"_id":doc_id},{"$set":{"_id":doc_id,"mesAno":mes_ano,"equipeId":equipe_id,"registros":df.to_dict("records"),"atualizadoEm":datetime.now()}},upsert=True)

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
    return pd.concat(frames,ignore_index=True) if frames else pd.DataFrame()

def listar_meses_processados():
    return sorted(get_db().processamentos.distinct("mesAno"),reverse=True)

# ── HELPERS ────────────────────────────────────
def fmt_brl(v):
    if not v and v!=0: return "R$ 0,00"
    return "R$ "+f"{float(v):_.2f}".replace(".",",").replace("_",".")

def calc_projecao(valor,dias_trab,total_dias):
    if not dias_trab or dias_trab<=0: return 0
    return (valor/dias_trab)*total_dias

def calc_variacao(atual,anterior):
    if not anterior or anterior==0: return None
    return ((atual-anterior)/anterior)*100

def get_semana_anterior(semana_id):
    ids=[s[0] for s in SEMANAS]
    idx=ids.index(semana_id) if semana_id in ids else -1
    return ids[idx-1] if idx>0 else None

def get_meses_disponiveis():
    hoje=datetime.now(); meses=[]
    for i in range(6):
        m=hoje.month-i; a=hoje.year
        if m<=0: m+=12; a-=1
        meses.append(f"{MESES[m-1]}-{a}")
    return meses

def aging_faixa(dias):
    if pd.isna(dias): return "ND"
    if dias<=30: return "D0-30"
    if dias<=60: return "D31-60"
    if dias<=90: return "D61-90"
    return "D90+"

# ── PROCESSAMENTO ──────────────────────────────
def processar_bases(pagos_file, chat_file, lig_file, disp_file, equipe_id, mes_ano):
    def ler(f):
        if f is None: return None
        try:
            return pd.read_csv(f,header=0) if f.name.endswith(".csv") else pd.read_excel(f,header=0)
        except: return None

    df_pagos = ler(pagos_file)
    if df_pagos is None: return None,["Arquivo PAGOS inválido!"]

    cols = list(df_pagos.columns)
    mapa = {}
    if len(cols)>=1: mapa[cols[0]]="uc_cpf"
    if len(cols)>=2: mapa[cols[1]]="data_vencimento"
    if len(cols)>=3: mapa[cols[2]]="data_pagamento"
    if len(cols)>=4: mapa[cols[3]]="valor"
    if len(cols)>=5: mapa[cols[4]]="fornecedora"
    df_pagos=df_pagos.rename(columns=mapa)

    for col in ["data_vencimento","data_pagamento"]:
        if col in df_pagos.columns:
            df_pagos[col]=pd.to_datetime(df_pagos[col],dayfirst=True,errors="coerce")

    if "valor" in df_pagos.columns:
        df_pagos["valor"]=pd.to_numeric(df_pagos["valor"].astype(str).str.replace("R$","").str.replace(".","").str.replace(",",".").str.strip(),errors="coerce").fillna(0)

    df_pagos["uc_cpf"]=df_pagos["uc_cpf"].astype(str).str.strip()

    contatos=[]
    for arq,nome in [(chat_file,"CHAT"),(lig_file,"LIGACOES"),(disp_file,"DISPAROS")]:
        df=ler(arq)
        if df is not None and len(df.columns)>=2:
            dc=pd.DataFrame()
            dc["uc_cpf"]=df.iloc[:,0].astype(str).str.strip()
            dc["data_contato"]=pd.to_datetime(df.iloc[:,1],dayfirst=True,errors="coerce")
            dc["tipo"]=nome
            contatos.append(dc)

    primeiro_contato=pd.DataFrame()
    if contatos:
        df_todos=pd.concat(contatos,ignore_index=True).dropna(subset=["data_contato"])
        primeiro_contato=df_todos.groupby("uc_cpf")["data_contato"].min().reset_index().rename(columns={"data_contato":"primeiro_contato"})

    if not primeiro_contato.empty:
        df_res=df_pagos.merge(primeiro_contato,on="uc_cpf",how="left")
    else:
        df_res=df_pagos.copy(); df_res["primeiro_contato"]=pd.NaT

    df_res["diferenca_dias"]=(df_res["data_pagamento"]-df_res["primeiro_contato"]).dt.days

    def classif(row):
        if pd.isna(row["primeiro_contato"]): return "ND"
        if row["diferenca_dias"]>=0: return "Elegível"
        return "Não Elegível"
    df_res["elegibilidade"]=df_res.apply(classif,axis=1)
    df_res["dias_vencidos"]=(df_res["data_pagamento"]-df_res["data_vencimento"]).dt.days
    df_res["aging"]=df_res["dias_vencidos"].apply(aging_faixa)

    for col in ["data_vencimento","data_pagamento","primeiro_contato"]:
        if col in df_res.columns:
            df_res[col]=df_res[col].dt.strftime("%Y-%m-%d").where(df_res[col].notna(),other=None)

    df_res["equipe"]=equipe_id; df_res["mes_ano"]=mes_ano
    return df_res,[]

# ── LOGIN ──────────────────────────────────────
def tela_login():
    c1,c2,c3=st.columns([1,1.2,1])
    with c2:
        st.markdown("""
        <div style="text-align:center;padding:48px 0 32px">
            <div style="width:72px;height:72px;background:linear-gradient(135deg,#1a6b35,#2daf5c);border-radius:18px;display:inline-flex;align-items:center;justify-content:center;font-size:36px;font-weight:800;color:white;margin-bottom:16px;box-shadow:0 8px 32px rgba(45,175,92,0.4)">G</div>
            <h1 style="color:#ffffff;margin:0;font-size:24px">iGreen Resultados</h1>
            <p style="color:#7fa8c9;margin:6px 0 0;font-size:13px">Gestão de Inadimplência Comercial</p>
        </div>
        """,unsafe_allow_html=True)
        usuario=st.text_input("Usuário",placeholder="Digite seu usuário")
        senha=st.text_input("Senha",type="password",placeholder="••••••••")
        if st.button("Entrar",use_container_width=True):
            u=USUARIOS.get(usuario.lower().strip())
            if u and u["senha"]==senha.strip():
                st.session_state.usuario={"id":usuario.lower(),**u}; st.rerun()
            else: st.error("⚠ Usuário ou senha incorretos.")

# ── SIDEBAR ────────────────────────────────────
def render_sidebar():
    u=st.session_state.usuario
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
                <div style="width:40px;height:40px;background:linear-gradient(135deg,#1a6b35,#2daf5c);border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;color:white">G</div>
                <div><div style="color:#ffffff;font-weight:700;font-size:14px">iGreen</div><div style="color:#7fa8c9;font-size:11px">Inadimplência</div></div>
            </div>
            <div style="background:rgba(45,175,92,0.1);border:1px solid rgba(45,175,92,0.2);border-radius:8px;padding:10px 12px;margin-bottom:16px">
                <div style="color:#2daf5c;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px">{'👔 Diretoria' if u['role']=='diretor' else '⚙️ Admin' if u['role']=='admin' else '👤 Gestor'}</div>
                <div style="color:#ffffff;font-size:14px;font-weight:600;margin-top:2px">{u['nome']}</div>
            </div>
        </div><hr>
        """,unsafe_allow_html=True)

        st.markdown("**📅 Período**")
        mes=st.selectbox("Mês",get_meses_disponiveis(),label_visibility="collapsed")
        slabels=[s[1] for s in SEMANAS]
        slabel=st.selectbox("Semana",slabels,label_visibility="collapsed")
        sid=SEMANAS[slabels.index(slabel)][0]
        st.markdown("<hr>",unsafe_allow_html=True)
        st.markdown("**📌 Navegação**")

        if u["role"]=="diretor":
            pags=["📊 Dashboard Executivo","📈 Resultados Operadores","📋 Histórico"]
        elif u["role"]=="admin":
            pags=["📊 Dashboard Executivo","📈 Resultados Operadores","📁 Upload de Bases","✏️ Lançamento","📋 Histórico","👥 Agentes"]
        else:
            pags=["📊 Dashboard Equipe","✏️ Lançamento","📁 Upload de Bases","📋 Histórico"]

        pag=st.radio("",pags,label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)
        if st.button("⏻ Sair",use_container_width=True):
            del st.session_state.usuario; st.rerun()
    return mes,sid,slabel,pag

# ── UPLOAD ─────────────────────────────────────
def pagina_upload():
    u=st.session_state.usuario
    equipe_id=u["equipe"] or "tamires"
    st.markdown("## 📁 Upload de Bases Mensais")
    mes_proc=st.selectbox("📅 Mês de Referência",get_meses_disponiveis())
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### 📄 PAGOS *(obrigatório)*")
        pf=st.file_uploader("PAGOS",type=["xlsx","csv"],label_visibility="collapsed",key="pagos")
        st.markdown("#### 📞 LIGAÇÕES")
        lf=st.file_uploader("LIGAÇÕES",type=["xlsx","csv"],label_visibility="collapsed",key="lig")
    with c2:
        st.markdown("#### 💬 CHAT")
        cf=st.file_uploader("CHAT",type=["xlsx","csv"],label_visibility="collapsed",key="chat")
        st.markdown("#### 📣 DISPAROS")
        df_up=st.file_uploader("DISPAROS",type=["xlsx","csv"],label_visibility="collapsed",key="disp")

    st.markdown("---")
    c1,c2,c3,c4=st.columns(4)
    for col,arq,nome in [(c1,pf,"PAGOS"),(c2,cf,"CHAT"),(c3,lf,"LIGAÇÕES"),(c4,df_up,"DISPAROS")]:
        with col:
            st.success(f"✅ {nome}") if arq else st.warning(f"⏳ {nome}")

    st.markdown("---")
    if st.button("⚡ PROCESSAR MÊS",use_container_width=True):
        if not pf: st.error("⚠ PAGOS é obrigatório!"); return
        with st.spinner("Processando..."):
            df_res,erros=processar_bases(pf,cf,lf,df_up,equipe_id,mes_proc)
        for e in erros: st.error(e)
        if df_res is not None and not df_res.empty:
            salvar_processamento(mes_proc,equipe_id,df_res)
            elig=df_res[df_res["elegibilidade"]=="Elegível"]
            st.success(f"✅ {len(df_res):,} registros processados e salvos!")
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("💰 Valor Elegível",fmt_brl(elig["valor"].sum()))
            c2.metric("📋 Boletos",f"{len(df_res):,}")
            c3.metric("👥 Clientes",f"{df_res['uc_cpf'].nunique():,}")
            c4.metric("✅ Elegíveis",f"{len(elig):,}")
            c5.metric("❌ Não Elegíveis",f"{len(df_res[df_res['elegibilidade']=='Não Elegível']):,}")
            st.markdown("#### Prévia")
            st.dataframe(df_res[["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging"]].head(50),use_container_width=True)

# ── DASHBOARD EXECUTIVO ─────────────────────────
def pagina_dashboard_executivo():
    st.markdown("""<div style="background:linear-gradient(135deg,#0d2137,#112940);border:1px solid #1e3a5f;border-radius:14px;padding:24px 28px;margin-bottom:24px;border-left:4px solid #2daf5c"><h1 style="margin:0">📊 Dashboard Executivo</h1><p style="color:#7fa8c9;margin:6px 0 0;font-size:13px">Gestão de Inadimplência Comercial · Visão consolidada</p></div>""",unsafe_allow_html=True)
    meses_proc=listar_meses_processados()
    if not meses_proc: st.info("📭 Nenhuma base processada ainda."); return

    c1,c2,c3=st.columns(3)
    with c1: mes_f=st.selectbox("📅 Mês",["Todos"]+meses_proc)
    with c2: eq_f=st.selectbox("👥 Equipe",["Todas","luciano","deborah","tamires"])

    df=buscar_processamentos(None if mes_f=="Todos" else mes_f, None if eq_f=="Todas" else eq_f)
    if df.empty: st.warning("Nenhum dado encontrado."); return
    df["valor"]=pd.to_numeric(df["valor"],errors="coerce").fillna(0)

    with c3:
        forns=["Todas"]+sorted(df["fornecedora"].dropna().unique().tolist())
        forn_f=st.selectbox("🏢 Fornecedora",forns)
    if forn_f!="Todas": df=df[df["fornecedora"]==forn_f]

    st.markdown("---")
    elig=df[df["elegibilidade"]=="Elegível"]
    nelig=df[df["elegibilidade"]=="Não Elegível"]
    nd=df[df["elegibilidade"]=="ND"]

    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric("💰 Valor Recuperado",fmt_brl(elig["valor"].sum()))
    c2.metric("👥 Clientes Únicos",f'{df["uc_cpf"].nunique():,}')
    c3.metric("📋 Boletos",f'{len(df):,}')
    c4.metric("✅ Elegíveis",f'{len(elig):,}')
    c5.metric("❌ Não Elegíveis",f'{len(nelig):,}')
    c6.metric("⬜ ND",f'{len(nd):,}')
    st.markdown("---")

    t1,t2,t3,t4=st.tabs(["📊 Aging","🏢 Fornecedoras","📅 Evolução Mensal","👥 Por Equipe"])
    with t1:
        st.markdown("#### Aging — Distribuição por Faixa")
        ag=df.groupby("aging").agg(Valor=("valor","sum"),Boletos=("uc_cpf","count"),Clientes=("uc_cpf","nunique")).reset_index()
        ag["Valor"]=ag["Valor"].apply(fmt_brl)
        ag=ag.rename(columns={"aging":"Faixa"})
        st.dataframe(ag,use_container_width=True,hide_index=True)
        bdf=df.groupby("aging")["uc_cpf"].count()
        st.bar_chart(bdf,color="#2daf5c")

    with t2:
        st.markdown("#### Resultado por Fornecedora")
        fdf=df.groupby("fornecedora").agg(
            Boletos=("uc_cpf","count"),
            Clientes=("uc_cpf","nunique"),
            Valor_Total=("valor","sum"),
        ).reset_index().rename(columns={"fornecedora":"Fornecedora"})
        fdf["Valor_Total"]=fdf["Valor_Total"].apply(fmt_brl)
        st.dataframe(fdf,use_container_width=True,hide_index=True)

    with t3:
        st.markdown("#### Evolução Mensal")
        dfall=buscar_processamentos()
        if not dfall.empty:
            dfall["valor"]=pd.to_numeric(dfall["valor"],errors="coerce").fillna(0)
            evol=dfall[dfall["elegibilidade"]=="Elegível"].groupby("_mes_ano")["valor"].sum().reset_index()
            evol.columns=["Mês","Valor"]
            st.bar_chart(evol.sort_values("Mês").set_index("Mês"),color="#2daf5c")

    with t4:
        st.markdown("#### Por Equipe")
        edf=df.groupby("_equipe").agg(
            Boletos=("uc_cpf","count"),
            Clientes=("uc_cpf","nunique"),
            Valor=("valor","sum"),
        ).reset_index()
        edf["Equipe"]=edf["_equipe"].map(lambda x: EQUIPES.get(x,{}).get("nome",x))
        edf["Valor"]=edf["Valor"].apply(fmt_brl)
        st.dataframe(edf[["Equipe","Boletos","Clientes","Valor"]],use_container_width=True,hide_index=True)

    st.markdown("---")
    if st.button("📥 Exportar Excel Completo"):
        out=io.BytesIO()
        with pd.ExcelWriter(out,engine="xlsxwriter") as w:
            df.to_excel(w,sheet_name="Dados Completos",index=False)
            elig.to_excel(w,sheet_name="Elegíveis",index=False)
        st.download_button("⬇️ Baixar Excel",data=out.getvalue(),
            file_name=f"iGreen_{mes_f}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── DASHBOARD EQUIPE ───────────────────────────
def pagina_dashboard_equipe(mes_ano,semana_id,semana_label):
    u=st.session_state.usuario; equipe_id=u["equipe"]
    equipe=EQUIPES[equipe_id]; agentes=[a for a in AGENTES if a["equipe"]==equipe_id]
    resultados=buscar_resultados_mes(mes_ano)
    config_dias=buscar_config(mes_ano,equipe_id,"dias")
    metas_cfg=buscar_config(mes_ano,equipe_id,"metas")
    dias_trab=config_dias.get("diasTrabalhados",0); total_dias=config_dias.get("totalDias",22)
    metas=metas_cfg.get("metas",{}); sem_ant_id=get_semana_anterior(semana_id)

    def gv(ag_id,sem=semana_id):
        return resultados.get(f"{mes_ano}__{sem}__{equipe_id}",{}).get("agentes",{}).get(ag_id,{}).get("valorRecebido",0)
    def te(sem=semana_id): return sum(gv(a["id"],sem) for a in agentes)

    ta=te(); tant=te(sem_ant_id) if sem_ant_id else 0
    me=sum(metas.get(a["id"],0) for a in agentes)
    proj=calc_projecao(ta,dias_trab,total_dias); vs=calc_variacao(ta,tant)

    st.markdown(f"""<div style="background:linear-gradient(135deg,#0d2137,#112940);border:1px solid #1e3a5f;border-radius:14px;padding:24px 28px;margin-bottom:24px;border-left:4px solid {equipe['cor']}"><h1 style="margin:0">Dashboard de Gestão da Equipe</h1><p style="color:#7fa8c9;margin:6px 0 0;font-size:13px">{equipe['emoji']} Equipe {equipe['nome']} · {semana_label} · {mes_ano.replace('-',' ')}</p></div>""",unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("💰 Total Recebido",fmt_brl(ta),delta=f"{vs:+.1f}% vs sem. ant." if vs is not None else None)
    c2.metric("🎯 Meta da Equipe",fmt_brl(me),delta=f"{(ta/me*100):.0f}% atingido" if me>0 else None)
    c3.metric("📈 Projeção do Mês",fmt_brl(proj))
    c4.metric("📅 Dias Trabalhados",f"{dias_trab} / {total_dias}")
    st.markdown("---"); st.markdown("#### Resultado por Agente")

    rows=[]
    for a in agentes:
        v=gv(a["id"]); va=gv(a["id"],sem_ant_id) if sem_ant_id else 0
        m=metas.get(a["id"],0); p=calc_projecao(v,dias_trab,total_dias)
        vs2=calc_variacao(v,va); pm=(v/m*100) if m>0 else 0
        rows.append({"Agente":a["nome"]+(" ⭐" if a["pleno"] else ""),"Valor Recebido":fmt_brl(v),"Meta":fmt_brl(m) if m>0 else "—","% Meta":f"{pm:.1f}%" if m>0 else "—","Projeção":fmt_brl(p) if p>0 else "—","vs Sem. Ant.":f"{'↑' if (vs2 or 0)>=0 else '↓'} {abs(vs2):.1f}%" if vs2 is not None else "—","_v":v})

    dft=pd.DataFrame(rows).sort_values("_v",ascending=False).drop(columns=["_v"])
    dft.index=range(1,len(dft)+1)
    st.dataframe(dft,use_container_width=True,height=min(600,(len(dft)+1)*38+40))

# ── LANÇAMENTO ─────────────────────────────────
def pagina_lancamento(mes_ano,semana_id,semana_label):
    u=st.session_state.usuario; equipe_id=u["equipe"]
    agentes=[a for a in AGENTES if a["equipe"]==equipe_id]
    resultados=buscar_resultados_mes(mes_ano)
    config_dias=buscar_config(mes_ano,equipe_id,"dias")
    metas_cfg=buscar_config(mes_ano,equipe_id,"metas")
    dados=resultados.get(f"{mes_ano}__{semana_id}__{equipe_id}",{})
    ms=metas_cfg.get("metas",{})

    st.markdown(f"## ✏️ Lançamento — {semana_label} — {mes_ano.replace('-',' ')}")
    c1,c2,c3=st.columns([2,1,1])
    with c1: vgs=st.text_input("Valor Total Geral Recebido (R$)",value=f"{dados.get('valorGeral',0):.2f}".replace(".",",") if dados.get("valorGeral") else "",placeholder="Ex: 85000,00")
    with c2: dt=st.number_input("Dias Trabalhados",min_value=0,max_value=31,value=int(config_dias.get("diasTrabalhados",0)))
    with c3: td=st.number_input("Total de Dias no Mês",min_value=1,max_value=31,value=int(config_dias.get("totalDias",22)))

    st.markdown("---"); st.markdown("#### 👤 Valores por Agente")
    for h,t in zip(st.columns([3,2,2,2,2]),["**Agente**","**Meta (R$)**","**Valor Recebido (R$)**","**Projeção**","**% Meta**"]): h.markdown(t)

    vi={}; mi={}
    for a in agentes:
        vs_=dados.get("agentes",{}).get(a["id"],{}).get("valorRecebido",0)
        ms_=ms.get(a["id"],0)
        cols=st.columns([3,2,2,2,2])
        cols[0].markdown(f"<div style='padding-top:8px;color:#e6edf3'>{'⭐ ' if a['pleno'] else ''}{a['nome']}</div>",unsafe_allow_html=True)
        mstr=cols[1].text_input("m",label_visibility="collapsed",value=f"{ms_:.2f}".replace(".",",") if ms_ else "",placeholder="0,00",key=f"m_{a['id']}")
        vstr=cols[2].text_input("v",label_visibility="collapsed",value=f"{vs_:.2f}".replace(".",",") if vs_ else "",placeholder="0,00",key=f"v_{a['id']}")
        try: v=float(vstr.replace(".","").replace(",",".")) if vstr else 0
        except: v=0
        try: m=float(mstr.replace(".","").replace(",",".")) if mstr else 0
        except: m=0
        p=calc_projecao(v,dt,td); pm=(v/m*100) if m>0 else 0
        cor="#3fb950" if pm>=80 else "#d29922" if pm>=50 else "#f85149"
        cols[3].markdown(f"<div style='padding-top:8px;color:#7fa8c9'>{fmt_brl(p) if p>0 else '—'}</div>",unsafe_allow_html=True)
        cols[4].markdown(f"<div style='padding-top:8px;color:{cor}'>{f'{pm:.1f}%' if m>0 else '—'}</div>",unsafe_allow_html=True)
        vi[a["id"]]=v; mi[a["id"]]=m

    tc=sum(vi.values())
    try: vg=float(vgs.replace(".","").replace(",",".")) if vgs else 0
    except: vg=0
    st.markdown("---")
    c1,c2,c3=st.columns(3)
    c1.metric("🤝 Com Interação",fmt_brl(tc))
    c2.metric("🔕 Sem Interação",fmt_brl(max(0,vg-tc)))
    c3.metric("📈 Projeção",fmt_brl(calc_projecao(tc,dt,td)))

    if st.button("💾 Salvar Resultado",use_container_width=True):
        salvar_resultado(mes_ano,semana_id,equipe_id,{"agentes":{a["id"]:{"valorRecebido":vi[a["id"]]} for a in agentes},"totalEquipe":tc,"valorGeral":vg,"semInteracao":max(0,vg-tc)})
        salvar_config(mes_ano,equipe_id,"metas",{"metas":mi})
        salvar_config(mes_ano,equipe_id,"dias",{"diasTrabalhados":dt,"totalDias":td})
        st.success("✅ Salvo!"); st.rerun()

# ── HISTÓRICO ──────────────────────────────────
def pagina_historico(mes_ano):
    u=st.session_state.usuario; equipe_id=u["equipe"]
    st.markdown(f"## 📋 Histórico — {mes_ano.replace('-',' ')}")
    t1,t2=st.tabs(["📈 Resultados Operadores","📁 Bases Processadas"])

    with t1:
        if not equipe_id: st.info("Perfil diretor — use Dashboard Executivo para histórico de bases."); return
        agentes=[a for a in AGENTES if a["equipe"]==equipe_id]
        resultados=buscar_resultados_mes(mes_ano)
        scoms=[s for s in SEMANAS if f"{mes_ano}__{s[0]}__{equipe_id}" in resultados]
        if not scoms: st.info("Nenhum resultado lançado ainda.")
        else:
            cols=st.columns(min(len(scoms),4))
            for i,(sid,sl) in enumerate(scoms):
                tot=resultados[f"{mes_ano}__{sid}__{equipe_id}"].get("totalEquipe",0)
                ant=resultados.get(f"{mes_ano}__{scoms[i-1][0]}__{equipe_id}",{}).get("totalEquipe",0) if i>0 else 0
                v=calc_variacao(tot,ant)
                with cols[i%4]: st.metric(sl,fmt_brl(tot),delta=f"{v:+.1f}% vs anterior" if v is not None else None)
            rows=[{"Agente":a["nome"]+(" ⭐" if a["pleno"] else ""),**{sl:fmt_brl(resultados[f"{mes_ano}__{sid}__{equipe_id}"].get("agentes",{}).get(a["id"],{}).get("valorRecebido",0)) for sid,sl in scoms}} for a in agentes]
            df=pd.DataFrame(rows); df.index=range(1,len(df)+1)
            st.dataframe(df,use_container_width=True)

    with t2:
        mp=listar_meses_processados()
        if not mp: st.info("Nenhuma base processada ainda.")
        else:
            mh=st.selectbox("Selecione o mês",mp)
            df=buscar_processamentos(mh,equipe_id)
            if df.empty: st.info("Sem dados para este mês.")
            else:
                df["valor"]=pd.to_numeric(df["valor"],errors="coerce").fillna(0)
                c1,c2,c3=st.columns(3)
                c1.metric("Valor Elegível",fmt_brl(df[df["elegibilidade"]=="Elegível"]["valor"].sum()))
                c2.metric("Boletos",f'{len(df):,}'); c3.metric("Clientes",f'{df["uc_cpf"].nunique():,}')
                st.dataframe(df[["uc_cpf","data_pagamento","valor","fornecedora","elegibilidade","aging"]].head(100),use_container_width=True)
                if st.button("📥 Exportar Excel"):
                    out=io.BytesIO()
                    with pd.ExcelWriter(out,engine="xlsxwriter") as w: df.to_excel(w,index=False)
                    st.download_button("⬇️ Baixar",data=out.getvalue(),file_name=f"iGreen_{mh}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── RESULTADOS DIRETOR ─────────────────────────
def pagina_resultados_diretor(mes_ano,semana_id,semana_label):
    eqs=["luciano","deborah","tamires","metcool"]
    resultados=buscar_resultados_mes(mes_ano); sa=get_semana_anterior(semana_id)
    def gt(eq,sem=semana_id): return resultados.get(f"{mes_ano}__{sem}__{eq}",{}).get("totalEquipe",0)
    tg=sum(gt(e) for e in eqs); tga=sum(gt(e,sa) for e in eqs) if sa else 0; vg=calc_variacao(tg,tga)

    st.markdown(f"""<div style="background:linear-gradient(135deg,#0d2137,#112940);border:1px solid #1e3a5f;border-radius:14px;padding:24px 28px;margin-bottom:24px;border-left:4px solid #2daf5c"><h1 style="margin:0">Resultados — Todas as Equipes</h1><p style="color:#7fa8c9;margin:6px 0 0;font-size:13px">{semana_label} · {mes_ano.replace('-',' ')}</p></div>""",unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("💰 Total Com Interação",fmt_brl(tg),delta=f"{vg:+.1f}% vs sem. ant." if vg is not None else None)
    c2.metric("🔕 Sem Interação",fmt_brl(sum(resultados.get(f"{mes_ano}__{semana_id}__{e}",{}).get("semInteracao",0) for e in eqs)))
    c3.metric("📊 Total Geral",fmt_brl(sum(resultados.get(f"{mes_ano}__{semana_id}__{e}",{}).get("valorGeral",0) for e in eqs)))
    c4.metric("👥 Equipes Ativas",len([e for e in eqs if gt(e)>0]))
    st.markdown("---")
    cols=st.columns(4)
    for i,eq_id in enumerate(eqs):
        eq=EQUIPES[eq_id]; com=gt(eq_id); ant=gt(eq_id,sa) if sa else 0; v=calc_variacao(com,ant)
        with cols[i]: st.metric(f"{eq['emoji']} {eq['nome']}",fmt_brl(com),delta=f"{v:+.1f}% vs sem. ant." if v is not None else None)
    st.markdown("---")
    for eq_id in eqs:
        eq=EQUIPES[eq_id]; ags=[a for a in AGENTES if a["equipe"]==eq_id]
        if not ags: continue
        key=f"{mes_ano}__{semana_id}__{eq_id}"; dados=resultados.get(key,{})
        with st.expander(f"{eq['emoji']} Equipe {eq['nome']} — {fmt_brl(gt(eq_id))}",expanded=False):
            rows=[{"Agente":a["nome"]+(" ⭐" if a["pleno"] else ""),"Valor":fmt_brl(dados.get("agentes",{}).get(a["id"],{}).get("valorRecebido",0))} for a in sorted(ags,key=lambda x:dados.get("agentes",{}).get(x["id"],{}).get("valorRecebido",0),reverse=True)]
            df=pd.DataFrame(rows); df.index=range(1,len(df)+1)
            st.dataframe(df,use_container_width=True)

# ── AGENTES ────────────────────────────────────
def pagina_agentes():
    st.markdown("## 👥 Agentes Cadastrados")
    u=st.session_state.usuario
    eqs=list(EQUIPES.keys()) if u["role"] in ["admin","diretor"] else [u["equipe"]]
    for eq_id in eqs:
        eq=EQUIPES[eq_id]; ags=[a for a in AGENTES if a["equipe"]==eq_id]
        with st.expander(f"{eq['emoji']} Equipe {eq['nome']} — {len(ags)} agentes",expanded=True):
            if not ags: st.info("Sem agentes.")
            else:
                rows=[{"#":i+1,"Nome":a["nome"]+(" ⭐" if a["pleno"] else ""),"Nível":"Pleno" if a["pleno"] else "Operador"} for i,a in enumerate(ags)]
                st.dataframe(pd.DataFrame(rows).set_index("#"),use_container_width=True)

# ── MAIN ───────────────────────────────────────
def main():
    if "usuario" not in st.session_state: tela_login(); return
    mes_ano,semana_id,semana_label,pagina=render_sidebar()
    u=st.session_state.usuario

    if u["role"]=="diretor":
        if "Dashboard Executivo" in pagina: pagina_dashboard_executivo()
        elif "Resultados" in pagina: pagina_resultados_diretor(mes_ano,semana_id,semana_label)
        elif "Histórico" in pagina: pagina_historico(mes_ano)
    elif u["role"]=="admin":
        if "Dashboard Executivo" in pagina: pagina_dashboard_executivo()
        elif "Resultados" in pagina: pagina_resultados_diretor(mes_ano,semana_id,semana_label)
        elif "Upload" in pagina: pagina_upload()
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano,semana_id,semana_label)
        elif "Histórico" in pagina: pagina_historico(mes_ano)
        elif "Agentes" in pagina: pagina_agentes()
    else:
        if "Dashboard" in pagina: pagina_dashboard_equipe(mes_ano,semana_id,semana_label)
        elif "Lançamento" in pagina: pagina_lancamento(mes_ano,semana_id,semana_label)
        elif "Upload" in pagina: pagina_upload()
        elif "Histórico" in pagina: pagina_historico(mes_ano)

if __name__=="__main__": main()
