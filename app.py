import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import io
import xlsxwriter

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="iGreen Resultados",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado — tema escuro iGreen
st.markdown("""
<style>
/* Fundo geral */
.stApp { background-color: #0d1117; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] .stRadio label {
    color: #8b949e !important;
    font-size: 14px;
}

/* Cards de métrica */
[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricValue"] { color: #2daf5c !important; font-size: 28px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 12px !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Tabelas */
[data-testid="stDataFrame"] { border: 1px solid #30363d; border-radius: 8px; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}

/* Botões */
.stButton button {
    background: #2daf5c !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton button:hover { background: #1a6b35 !important; }

/* Headers */
h1 { color: #e6edf3 !important; font-size: 22px !important; }
h2 { color: #e6edf3 !important; font-size: 18px !important; }
h3 { color: #8b949e !important; font-size: 13px !important; text-transform: uppercase; letter-spacing: 1px; }

/* Divider */
hr { border-color: #30363d !important; }

/* Badge verde */
.badge-verde {
    background: rgba(45,175,92,0.15);
    color: #2daf5c;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-roxo {
    background: rgba(168,85,247,0.15);
    color: #a855f7;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-laranja {
    background: rgba(249,115,22,0.15);
    color: #f97316;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.card-bloco {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
}
.variacao-up   { color: #3fb950; font-weight: 600; }
.variacao-down { color: #f85149; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DADOS — AGENTES E EQUIPES
# ─────────────────────────────────────────────
EQUIPES = {
    "luciano": {"nome": "Luciano",  "emoji": "🟢", "cor": "#2daf5c"},
    "deborah": {"nome": "Déborah",  "emoji": "🟣", "cor": "#a855f7"},
    "tamires": {"nome": "Tamires",  "emoji": "🟠", "cor": "#f97316"},
    "metcool": {"nome": "MetCool",  "emoji": "🔵", "cor": "#3b82f6", "sub": "luciano"},
}

AGENTES = [
    # Luciano
    {"id": "jennifer-silveira",  "nome": "Jennifer Silveira",  "equipe": "luciano", "pleno": True},
    {"id": "paulo-roberto",      "nome": "Paulo Roberto",      "equipe": "luciano", "pleno": False},
    {"id": "samires-barros",     "nome": "Samires Barros",     "equipe": "luciano", "pleno": False},
    {"id": "maycow-gabriel",     "nome": "Maycow Gabriel",     "equipe": "luciano", "pleno": False},
    {"id": "otaides-junior",     "nome": "Otaides Junior",     "equipe": "luciano", "pleno": False},
    {"id": "heverton-tavares",   "nome": "Heverton Tavares",   "equipe": "luciano", "pleno": False},
    {"id": "camila-nara",        "nome": "Camila Nara",        "equipe": "luciano", "pleno": False},
    {"id": "caua-alves",         "nome": "Caua Alves",         "equipe": "luciano", "pleno": False},
    {"id": "eduarda-sanqueta",   "nome": "Eduarda Sanqueta",   "equipe": "luciano", "pleno": False},
    {"id": "jheniffer-santos",   "nome": "Jheniffer Santos",   "equipe": "luciano", "pleno": False},
    {"id": "ketie-silva",        "nome": "Ketie Silva",        "equipe": "luciano", "pleno": False},
    {"id": "emanuel-cardoso",    "nome": "Emanuel Cardoso",    "equipe": "luciano", "pleno": False},
    {"id": "victoria-silva",     "nome": "Victória Silva",     "equipe": "luciano", "pleno": False},
    {"id": "grasielli-santos",   "nome": "Grasielli Santos",   "equipe": "luciano", "pleno": False},
    {"id": "laura-silva",        "nome": "Laura Silva",        "equipe": "luciano", "pleno": False},
    {"id": "michelle-batista",   "nome": "Michelle Batista",   "equipe": "luciano", "pleno": False},
    {"id": "lorenzzo-pereira",   "nome": "Lorenzzo Pereira",   "equipe": "luciano", "pleno": False},
    {"id": "diogo-oliveira",     "nome": "Diogo Oliveira",     "equipe": "luciano", "pleno": False},
    {"id": "maria-paulino",      "nome": "Maria Paulino",      "equipe": "luciano", "pleno": False},
    {"id": "gabrielle-martins",  "nome": "Gabrielle Martins",  "equipe": "luciano", "pleno": False},
    {"id": "marcos-martins",     "nome": "Marcos Martins",     "equipe": "luciano", "pleno": False},
    # Déborah
    {"id": "mikael-dias",        "nome": "Mikael Dias",        "equipe": "deborah", "pleno": False},
    {"id": "amanda-eduarda",     "nome": "Amanda Eduarda",     "equipe": "deborah", "pleno": False},
    {"id": "larissa-barcelos",   "nome": "Larissa Barcelos",   "equipe": "deborah", "pleno": False},
    {"id": "nicole-amaral",      "nome": "Nicole Amaral",      "equipe": "deborah", "pleno": False},
    {"id": "sara-rocha",         "nome": "Sara Rocha",         "equipe": "deborah", "pleno": False},
    {"id": "isabelly-araujo",    "nome": "Isabelly Araujo",    "equipe": "deborah", "pleno": False},
    {"id": "silye-paula",        "nome": "Silye Paula",        "equipe": "deborah", "pleno": False},
    # Tamires
    {"id": "danilo-rodrigues",   "nome": "Danilo Rodrigues",   "equipe": "tamires", "pleno": True},
    {"id": "raiane-pereira",     "nome": "Raiane Pereira",     "equipe": "tamires", "pleno": False},
    {"id": "wynara-dos-reis",    "nome": "Wynara Dos Reis",    "equipe": "tamires", "pleno": False},
    {"id": "esteffany-souza",    "nome": "Esteffany Souza",    "equipe": "tamires", "pleno": False},
    {"id": "andre-gomes",        "nome": "André Gomes",        "equipe": "tamires", "pleno": False},
    {"id": "wanessa-cardoso",    "nome": "Wanessa Cardoso",    "equipe": "tamires", "pleno": False},
    {"id": "larisse-garcia",     "nome": "Larisse Garcia",     "equipe": "tamires", "pleno": False},
    {"id": "arthur-alves",       "nome": "Arthur Alves",       "equipe": "tamires", "pleno": False},
]

USUARIOS = {
    "luciano": {"senha": "luciano123", "equipe": "luciano", "role": "lider",   "nome": "Luciano"},
    "deborah": {"senha": "deborah123", "equipe": "deborah", "role": "lider",   "nome": "Déborah"},
    "tamires": {"senha": "tamires123", "equipe": "tamires", "role": "lider",   "nome": "Tamires"},
    "veloso":  {"senha": "veloso123",  "equipe": None,      "role": "diretor", "nome": "Veloso"},
}

SEMANAS = [
    ("sem1-qua", "1ª Semana — Quarta"),
    ("sem1-sex", "1ª Semana — Sexta"),
    ("sem2-qua", "2ª Semana — Quarta"),
    ("sem2-sex", "2ª Semana — Sexta"),
    ("sem3-qua", "3ª Semana — Quarta"),
    ("sem3-sex", "3ª Semana — Sexta"),
    ("sem4-qua", "4ª Semana — Quarta"),
    ("sem4-sex", "4ª Semana — Sexta"),
    ("fechamento", "Fechamento do Mês"),
]

MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

# ─────────────────────────────────────────────
# MONGODB
# ─────────────────────────────────────────────
@st.cache_resource
def get_db():
    uri = st.secrets["mongo"]["uri"]
    client = MongoClient(uri)
    return client[st.secrets["mongo"]["db"]]

def salvar_resultado(mes_ano, semana_id, equipe_id, dados):
    db = get_db()
    doc_id = f"{mes_ano}__{semana_id}__{equipe_id}"
    db.resultados.update_one(
        {"_id": doc_id},
        {"$set": {"_id": doc_id, "mesAno": mes_ano, "semanaId": semana_id,
                  "equipeId": equipe_id, **dados, "atualizadoEm": datetime.now()}},
        upsert=True
    )

def buscar_resultados_mes(mes_ano):
    db = get_db()
    docs = list(db.resultados.find({"mesAno": mes_ano}))
    return {d["_id"]: d for d in docs}

def salvar_config(mes_ano, equipe_id, tipo, dados):
    db = get_db()
    doc_id = f"{tipo}__{mes_ano}__{equipe_id}"
    db.configuracoes.update_one(
        {"_id": doc_id},
        {"$set": {"_id": doc_id, "mesAno": mes_ano, "equipeId": equipe_id, **dados}},
        upsert=True
    )

def buscar_config(mes_ano, equipe_id, tipo):
    db = get_db()
    doc_id = f"{tipo}__{mes_ano}__{equipe_id}"
    return db.configuracoes.find_one({"_id": doc_id}) or {}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt_brl(v):
    if not v: return "R$ 0,00"
    return f"R$ {float(v):_.2f}".replace(".", ",").replace("_", ".")

def calc_projecao(valor, dias_trab, total_dias):
    if not dias_trab or dias_trab <= 0: return 0
    return (valor / dias_trab) * total_dias

def calc_variacao(atual, anterior):
    if not anterior or anterior == 0: return None
    return ((atual - anterior) / anterior) * 100

def variacao_str(atual, anterior):
    v = calc_variacao(atual, anterior)
    if v is None: return "—"
    seta = "↑" if v >= 0 else "↓"
    cor  = "variacao-up" if v >= 0 else "variacao-down"
    return f'<span class="{cor}">{seta} {abs(v):.1f}%</span>'

def get_semana_anterior(semana_id):
    ids = [s[0] for s in SEMANAS]
    idx = ids.index(semana_id) if semana_id in ids else -1
    return ids[idx - 1] if idx > 0 else None

def get_meses_disponiveis():
    hoje = datetime.now()
    meses = []
    for i in range(6):
        m = hoje.month - i
        a = hoje.year
        if m <= 0:
            m += 12
            a -= 1
        meses.append(f"{MESES[m-1]}-{a}")
    return meses

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def tela_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0 20px">
            <div style="width:64px;height:64px;background:#2daf5c;border-radius:16px;
                        display:inline-flex;align-items:center;justify-content:center;
                        font-size:32px;font-weight:800;color:white;margin-bottom:12px">G</div>
            <h2 style="color:#e6edf3;margin:0">iGreen Resultados</h2>
            <p style="color:#8b949e;margin:4px 0 0">Inadimplência Comercial</p>
        </div>
        """, unsafe_allow_html=True)

        usuario = st.text_input("Usuário", placeholder="luciano / deborah / tamires / veloso")
        senha   = st.text_input("Senha", type="password", placeholder="••••••••")

        if st.button("Entrar", use_container_width=True):
            u = USUARIOS.get(usuario.lower().strip())
            if u and u["senha"] == senha.strip():
                st.session_state.usuario = {"id": usuario.lower(), **u}
                st.rerun()
            else:
                st.error("⚠ Usuário ou senha incorretos.")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    u = st.session_state.usuario
    eq = EQUIPES.get(u["equipe"]) if u["equipe"] else None

    with st.sidebar:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0 16px">
            <div style="width:36px;height:36px;background:#2daf5c;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;
                        font-weight:800;font-size:16px;color:white;flex-shrink:0">G</div>
            <div>
                <div style="color:#e6edf3;font-weight:600;font-size:14px">iGreen</div>
                <div style="color:#8b949e;font-size:11px">Resultados</div>
            </div>
        </div>
        <hr style="margin:0 0 12px">
        """, unsafe_allow_html=True)

        # Usuário logado
        badge = f'<span class="badge-{"verde" if u["role"]=="diretor" else "verde"}">{u["nome"]}</span>'
        st.markdown(f'<div style="margin-bottom:16px">{badge}</div>', unsafe_allow_html=True)

        # Período
        st.markdown("**Período**")
        meses_disp = get_meses_disponiveis()
        mes_selecionado = st.selectbox("Mês", meses_disp, label_visibility="collapsed")

        semana_labels = [s[1] for s in SEMANAS]
        semana_label  = st.selectbox("Semana", semana_labels, label_visibility="collapsed")
        semana_id     = SEMANAS[semana_labels.index(semana_label)][0]

        st.markdown("<hr>", unsafe_allow_html=True)

        # Navegação
        if u["role"] == "diretor":
            paginas = ["📊 Visão Geral", "📋 Histórico", "👥 Agentes"]
        else:
            paginas = ["📊 Dashboard", "✏️ Lançamento", "📋 Histórico", "👥 Agentes"]

        pagina = st.radio("", paginas, label_visibility="collapsed")

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("⏻ Sair", use_container_width=True):
            del st.session_state.usuario
            st.rerun()

    return mes_selecionado, semana_id, semana_label, pagina

# ─────────────────────────────────────────────
# PÁGINA: DASHBOARD (líderes)
# ─────────────────────────────────────────────
def pagina_dashboard(mes_ano, semana_id, semana_label):
    u          = st.session_state.usuario
    equipe_id  = u["equipe"]
    equipe     = EQUIPES[equipe_id]
    agentes    = [a for a in AGENTES if a["equipe"] == equipe_id]

    resultados = buscar_resultados_mes(mes_ano)
    config_dias = buscar_config(mes_ano, equipe_id, "dias")
    metas_cfg   = buscar_config(mes_ano, equipe_id, "metas")

    dias_trab  = config_dias.get("diasTrabalhados", 0)
    total_dias = config_dias.get("totalDias", 22)
    metas      = metas_cfg.get("metas", {})

    sem_ant_id = get_semana_anterior(semana_id)

    def get_valor(ag_id, sem=semana_id):
        key = f"{mes_ano}__{sem}__{equipe_id}"
        return resultados.get(key, {}).get("agentes", {}).get(ag_id, {}).get("valorRecebido", 0)

    def total_equipe(sem=semana_id):
        return sum(get_valor(a["id"], sem) for a in agentes)

    total_atual = total_equipe()
    total_ant   = total_equipe(sem_ant_id) if sem_ant_id else 0
    meta_equipe = sum(metas.get(a["id"], 0) for a in agentes)
    projecao    = calc_projecao(total_atual, dias_trab, total_dias)

    # Header
    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;
                padding:20px 24px;margin-bottom:20px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
                <h1 style="margin:0;font-size:20px">Dashboard de Gestão da Equipe</h1>
                <p style="color:#8b949e;margin:4px 0 0;font-size:13px">
                    Resultado por agente · {semana_label} · {mes_ano.replace("-", " ")}
                </p>
            </div>
            <span class="badge-{'verde' if equipe_id=='luciano' else 'roxo' if equipe_id=='deborah' else 'laranja'}">
                {equipe['emoji']} Equipe {equipe['nome']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Cards principais
    v_sem = calc_variacao(total_atual, total_ant)
    pct_meta = (total_atual / meta_equipe * 100) if meta_equipe > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_str = f"{v_sem:+.1f}% vs semana ant." if v_sem is not None else None
        st.metric("💰 Total Recebido", fmt_brl(total_atual), delta=delta_str)
    with c2:
        st.metric("🎯 Meta da Equipe", fmt_brl(meta_equipe),
                  delta=f"{pct_meta:.0f}% atingido" if meta_equipe > 0 else None)
    with c3:
        st.metric("📈 Projeção do Mês", fmt_brl(projecao))
    with c4:
        st.metric("📅 Dias Trabalhados", f"{dias_trab} / {total_dias}")

    st.markdown("---")

    # Tabela de agentes
    st.markdown("#### Resultado por Agente")

    rows = []
    for a in agentes:
        val     = get_valor(a["id"])
        val_ant = get_valor(a["id"], sem_ant_id) if sem_ant_id else 0
        meta    = metas.get(a["id"], 0)
        proj    = calc_projecao(val, dias_trab, total_dias)
        v_s     = calc_variacao(val, val_ant)
        pct_m   = (val / meta * 100) if meta > 0 else 0

        rows.append({
            "Agente":        a["nome"] + (" ⭐" if a["pleno"] else ""),
            "Valor Recebido": fmt_brl(val),
            "Meta":           fmt_brl(meta) if meta > 0 else "—",
            "% Meta":         f"{pct_m:.1f}%" if meta > 0 else "—",
            "Projeção":       fmt_brl(proj) if proj > 0 else "—",
            "vs Sem. Ant.":   f"{'↑' if (v_s or 0) >= 0 else '↓'} {abs(v_s):.1f}%" if v_s is not None else "—",
            "_val": val,
        })

    df = pd.DataFrame(rows).sort_values("_val", ascending=False).drop(columns=["_val"])
    df.index = range(1, len(df) + 1)
    st.dataframe(df, use_container_width=True, height=min(600, (len(df) + 1) * 38 + 40))

    # Resumo
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Recebido",       fmt_brl(total_atual))
    col2.metric("Faltam para Meta",     fmt_brl(max(0, meta_equipe - total_atual)))
    col3.metric("Projeção Final",       fmt_brl(projecao))
    col4.metric("Agentes c/ Resultado", len([a for a in agentes if get_valor(a["id"]) > 0]))

# ─────────────────────────────────────────────
# PÁGINA: LANÇAMENTO
# ─────────────────────────────────────────────
def pagina_lancamento(mes_ano, semana_id, semana_label):
    u         = st.session_state.usuario
    equipe_id = u["equipe"]
    agentes   = [a for a in AGENTES if a["equipe"] == equipe_id]

    resultados  = buscar_resultados_mes(mes_ano)
    config_dias = buscar_config(mes_ano, equipe_id, "dias")
    metas_cfg   = buscar_config(mes_ano, equipe_id, "metas")

    key_atual = f"{mes_ano}__{semana_id}__{equipe_id}"
    dados_atuais = resultados.get(key_atual, {})
    metas_salvas = metas_cfg.get("metas", {})

    st.markdown(f"## ✏️ Lançamento — {semana_label} — {mes_ano.replace('-', ' ')}")

    # Config dias
    st.markdown("#### ⚙️ Configuração do Período")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        valor_geral_str = st.text_input(
            "Valor Total Geral Recebido (R$)",
            value=f"{dados_atuais.get('valorGeral', 0):.2f}".replace(".", ",") if dados_atuais.get("valorGeral") else "",
            placeholder="Ex: 85000,00"
        )
    with col2:
        dias_trab = st.number_input("Dias Trabalhados", min_value=0, max_value=31,
                                     value=int(config_dias.get("diasTrabalhados", 0)))
    with col3:
        total_dias = st.number_input("Total de Dias no Mês", min_value=1, max_value=31,
                                      value=int(config_dias.get("totalDias", 22)))

    st.markdown("---")
    st.markdown("#### 👤 Valores por Agente")

    valores_input = {}
    metas_input   = {}

    # Cabeçalho
    hcols = st.columns([3, 2, 2, 2, 2])
    hcols[0].markdown("**Agente**")
    hcols[1].markdown("**Meta (R$)**")
    hcols[2].markdown("**Valor Recebido (R$)**")
    hcols[3].markdown("**Projeção**")
    hcols[4].markdown("**% Meta**")

    for a in agentes:
        val_salvo  = dados_atuais.get("agentes", {}).get(a["id"], {}).get("valorRecebido", 0)
        meta_salva = metas_salvas.get(a["id"], 0)

        cols = st.columns([3, 2, 2, 2, 2])
        nome_label = f"{'⭐ ' if a['pleno'] else ''}{a['nome']}"
        cols[0].markdown(f"<div style='padding-top:8px;color:#e6edf3'>{nome_label}</div>", unsafe_allow_html=True)

        meta_str = cols[1].text_input(
            f"meta_{a['id']}", label_visibility="collapsed",
            value=f"{meta_salva:.2f}".replace(".", ",") if meta_salva else "",
            placeholder="0,00", key=f"meta_{a['id']}"
        )
        val_str = cols[2].text_input(
            f"val_{a['id']}", label_visibility="collapsed",
            value=f"{val_salvo:.2f}".replace(".", ",") if val_salvo else "",
            placeholder="0,00", key=f"val_{a['id']}"
        )

        try:
            val  = float(val_str.replace(".", "").replace(",", ".")) if val_str else 0
            meta = float(meta_str.replace(".", "").replace(",", ".")) if meta_str else 0
        except:
            val = 0; meta = 0

        proj = calc_projecao(val, dias_trab, total_dias)
        pct  = (val / meta * 100) if meta > 0 else 0

        cols[3].markdown(f"<div style='padding-top:8px;color:#8b949e'>{fmt_brl(proj) if proj > 0 else '—'}</div>", unsafe_allow_html=True)
        cor_pct = "#3fb950" if pct >= 80 else "#d29922" if pct >= 50 else "#f85149"
        cols[4].markdown(f"<div style='padding-top:8px;color:{cor_pct}'>{f'{pct:.1f}%' if meta > 0 else '—'}</div>", unsafe_allow_html=True)

        valores_input[a["id"]] = val
        metas_input[a["id"]]   = meta

    # Mini resumo
    total_com = sum(valores_input.values())
    try:
        vg = float(valor_geral_str.replace(".", "").replace(",", ".")) if valor_geral_str else 0
    except:
        vg = 0
    sem_int = max(0, vg - total_com)
    proj_eq = calc_projecao(total_com, dias_trab, total_dias)

    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    r1.metric("🤝 Com Interação", fmt_brl(total_com))
    r2.metric("🔕 Sem Interação", fmt_brl(sem_int))
    r3.metric("📈 Projeção",      fmt_brl(proj_eq))

    if st.button("💾 Salvar Resultado", use_container_width=True):
        agentes_data = {a["id"]: {"valorRecebido": valores_input[a["id"]]} for a in agentes}
        salvar_resultado(mes_ano, semana_id, equipe_id, {
            "agentes": agentes_data,
            "totalEquipe": total_com,
            "valorGeral": vg,
            "semInteracao": sem_int,
        })
        salvar_config(mes_ano, equipe_id, "metas", {"metas": metas_input})
        salvar_config(mes_ano, equipe_id, "dias",  {"diasTrabalhados": dias_trab, "totalDias": total_dias})
        st.success("✅ Resultado salvo com sucesso!")
        st.rerun()

# ─────────────────────────────────────────────
# PÁGINA: HISTÓRICO
# ─────────────────────────────────────────────
def pagina_historico(mes_ano):
    u         = st.session_state.usuario
    equipe_id = u["equipe"]
    agentes   = [a for a in AGENTES if a["equipe"] == equipe_id]

    resultados = buscar_resultados_mes(mes_ano)

    semanas_com_dados = [
        s for s in SEMANAS
        if f"{mes_ano}__{s[0]}__{equipe_id}" in resultados
    ]

    st.markdown(f"## 📋 Histórico — {mes_ano.replace('-', ' ')}")

    if not semanas_com_dados:
        st.info("Nenhum resultado lançado para este mês ainda.")
        return

    # Cards por semana
    cols = st.columns(min(len(semanas_com_dados), 4))
    for i, (sem_id, sem_label) in enumerate(semanas_com_dados):
        key   = f"{mes_ano}__{sem_id}__{equipe_id}"
        total = resultados[key].get("totalEquipe", 0)
        ant   = resultados.get(f"{mes_ano}__{semanas_com_dados[i-1][0]}__{equipe_id}", {}).get("totalEquipe", 0) if i > 0 else 0
        v     = calc_variacao(total, ant)
        delta = f"{v:+.1f}% vs anterior" if v is not None else None
        with cols[i % 4]:
            st.metric(sem_label, fmt_brl(total), delta=delta)

    st.markdown("---")

    # Tabela histórico
    rows = []
    for a in agentes:
        row = {"Agente": a["nome"] + (" ⭐" if a["pleno"] else "")}
        for sem_id, sem_label in semanas_com_dados:
            key = f"{mes_ano}__{sem_id}__{equipe_id}"
            val = resultados[key].get("agentes", {}).get(a["id"], {}).get("valorRecebido", 0)
            row[sem_label] = fmt_brl(val) if val > 0 else "—"
        rows.append(row)

    df = pd.DataFrame(rows)
    df.index = range(1, len(df) + 1)
    st.dataframe(df, use_container_width=True)

    # Export Excel
    if st.button("📥 Exportar Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Histórico", index=True)
        st.download_button(
            "⬇️ Baixar Excel",
            data=output.getvalue(),
            file_name=f"iGreen_Resultado_{mes_ano}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ─────────────────────────────────────────────
# PÁGINA: VISÃO GERAL (Veloso)
# ─────────────────────────────────────────────
def pagina_visao_geral(mes_ano, semana_id, semana_label):
    resultados = buscar_resultados_mes(mes_ano)
    equipes_ids = ["luciano", "deborah", "tamires", "metcool"]
    sem_ant_id  = get_semana_anterior(semana_id)

    def get_total(eq, sem=semana_id):
        return resultados.get(f"{mes_ano}__{sem}__{eq}", {}).get("totalEquipe", 0)
    def get_sem_int(eq):
        return resultados.get(f"{mes_ano}__{semana_id}__{eq}", {}).get("semInteracao", 0)
    def get_geral(eq):
        return resultados.get(f"{mes_ano}__{semana_id}__{eq}", {}).get("valorGeral", 0)

    total_geral      = sum(get_total(eq) for eq in equipes_ids)
    total_geral_ant  = sum(get_total(eq, sem_ant_id) for eq in equipes_ids) if sem_ant_id else 0
    total_sem_int    = sum(get_sem_int(eq) for eq in equipes_ids)
    total_val_geral  = sum(get_geral(eq) for eq in equipes_ids)

    v_geral = calc_variacao(total_geral, total_geral_ant)

    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;
                padding:20px 24px;margin-bottom:20px">
        <h1 style="margin:0;font-size:20px">Dashboard de Gestão da Equipe</h1>
        <p style="color:#8b949e;margin:4px 0 0;font-size:13px">
            Visão consolidada · {semana_label} · {mes_ano.replace("-", " ")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#1c2128;border:1px solid #30363d;border-radius:8px;
                padding:8px 16px;margin-bottom:16px;font-size:12px;color:#8b949e">
        <strong style="color:#e6edf3">Filtros automáticos aplicados</strong>
        · Equipes: Luciano · Déborah · Tamires · MetCool
        · Período: {semana_label}
    </div>
    """, unsafe_allow_html=True)

    # Cards consolidados
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Com Interação", fmt_brl(total_geral),
              delta=f"{v_geral:+.1f}% vs sem. ant." if v_geral is not None else None)
    c2.metric("🔕 Sem Interação",  fmt_brl(total_sem_int))
    c3.metric("📊 Total Geral",    fmt_brl(total_val_geral))
    c4.metric("📈 Projeção Total", fmt_brl(total_geral))

    st.markdown("---")
    st.markdown("#### Por Equipe")

    cols = st.columns(4)
    for i, eq_id in enumerate(equipes_ids):
        eq  = EQUIPES[eq_id]
        com = get_total(eq_id)
        ant = get_total(eq_id, sem_ant_id) if sem_ant_id else 0
        v   = calc_variacao(com, ant)
        with cols[i]:
            st.metric(
                f"{eq['emoji']} Equipe {eq['nome']}",
                fmt_brl(com),
                delta=f"{v:+.1f}% vs sem. ant." if v is not None else None
            )

    st.markdown("---")

    # Tabela por equipe
    for eq_id in equipes_ids:
        eq      = EQUIPES[eq_id]
        agentes = [a for a in AGENTES if a["equipe"] == eq_id]
        if not agentes:
            st.markdown(f"**{eq['emoji']} Equipe {eq['nome']}** — Sem agentes cadastrados ainda.")
            continue

        key  = f"{mes_ano}__{semana_id}__{eq_id}"
        dados = resultados.get(key, {})

        with st.expander(f"{eq['emoji']} Equipe {eq['nome']} — Total: {fmt_brl(get_total(eq_id))}", expanded=True):
            rows = []
            for a in sorted(agentes, key=lambda x: dados.get("agentes", {}).get(x["id"], {}).get("valorRecebido", 0), reverse=True):
                val = dados.get("agentes", {}).get(a["id"], {}).get("valorRecebido", 0)
                rows.append({
                    "Agente":         a["nome"] + (" ⭐" if a["pleno"] else ""),
                    "Valor Recebido": fmt_brl(val) if val > 0 else "—",
                    "_val": val
                })
            df = pd.DataFrame(rows).drop(columns=["_val"])
            df.index = range(1, len(df) + 1)
            st.dataframe(df, use_container_width=True)

    # Export Excel Veloso
    st.markdown("---")
    if st.button("📥 Exportar Excel Completo (Veloso)"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            # Resumo
            resumo_rows = []
            for eq_id in equipes_ids:
                eq = EQUIPES[eq_id]
                resumo_rows.append({
                    "Equipe": eq["nome"],
                    "Com Interação": get_total(eq_id),
                    "Sem Interação": get_sem_int(eq_id),
                    "Total Geral":   get_geral(eq_id),
                })
            pd.DataFrame(resumo_rows).to_excel(writer, sheet_name="Resumo Geral", index=False)

            # Por equipe
            for eq_id in equipes_ids:
                eq      = EQUIPES[eq_id]
                agentes = [a for a in AGENTES if a["equipe"] == eq_id]
                if not agentes: continue
                key   = f"{mes_ano}__{semana_id}__{eq_id}"
                dados = resultados.get(key, {})
                rows  = [{"Agente": a["nome"], "Valor Recebido": dados.get("agentes", {}).get(a["id"], {}).get("valorRecebido", 0)} for a in agentes]
                pd.DataFrame(rows).to_excel(writer, sheet_name=f"Equipe {eq['nome']}", index=False)

        st.download_button(
            "⬇️ Baixar Excel",
            data=output.getvalue(),
            file_name=f"iGreen_Veloso_{mes_ano}_{semana_id}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ─────────────────────────────────────────────
# PÁGINA: AGENTES
# ─────────────────────────────────────────────
def pagina_agentes():
    u = st.session_state.usuario
    st.markdown("## 👥 Agentes Cadastrados")

    equipes_mostrar = list(EQUIPES.keys()) if u["role"] == "diretor" else [u["equipe"]]

    for eq_id in equipes_mostrar:
        eq      = EQUIPES[eq_id]
        agentes = [a for a in AGENTES if a["equipe"] == eq_id]
        sub_txt = f" *(sub-equipe de {EQUIPES[eq['sub']]['nome']})*" if "sub" in eq else ""

        with st.expander(f"{eq['emoji']} Equipe {eq['nome']}{sub_txt} — {len(agentes)} agentes", expanded=True):
            if not agentes:
                st.info("Nenhum agente cadastrado ainda.")
            else:
                rows = [{"#": i+1, "Nome": a["nome"] + (" ⭐" if a["pleno"] else ""),
                         "Nível": "Pleno" if a["pleno"] else "Operador"} for i, a in enumerate(agentes)]
                df = pd.DataFrame(rows).set_index("#")
                st.dataframe(df, use_container_width=True)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login()
        return

    mes_ano, semana_id, semana_label, pagina = render_sidebar()
    u = st.session_state.usuario

    if u["role"] == "diretor":
        if "Visão Geral" in pagina:
            pagina_visao_geral(mes_ano, semana_id, semana_label)
        elif "Histórico" in pagina:
            pagina_historico(mes_ano)
        elif "Agentes" in pagina:
            pagina_agentes()
    else:
        if "Dashboard" in pagina:
            pagina_dashboard(mes_ano, semana_id, semana_label)
        elif "Lançamento" in pagina:
            pagina_lancamento(mes_ano, semana_id, semana_label)
        elif "Histórico" in pagina:
            pagina_historico(mes_ano)
        elif "Agentes" in pagina:
            pagina_agentes()

if __name__ == "__main__":
    main()
