import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, date
import base64
import re
import io
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="iGreen Monitorias",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #f0f7f0 !important; }
[data-testid="stSidebar"] { background: #f5fbf5 !important; border-right: 1px solid #d0e8d0 !important; }
[data-testid="stSidebar"] .stRadio > div > p { display: none !important; }
[data-testid="stSidebar"] .stRadio label {
    color: #2d4a2d !important; font-size: 13px !important; font-weight: 500 !important;
    padding: 10px 16px !important; display: flex !important; align-items: center !important;
    border-radius: 8px !important; margin: 1px 0 !important; width: 100% !important;
    background: #ffffff !important; border: 1px solid #d8ead8 !important;
    min-height: 40px !important; transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #edf7ed !important; border-color: #2e7d32 !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
    color: #ffffff !important; background: #2e7d32 !important; border-color: #2e7d32 !important; font-weight: 600 !important;
}
[data-testid="stMetric"] { background: #ffffff !important; border: 1px solid #e0e8e0 !important; border-radius: 10px !important; padding: 16px 20px !important; border-top: 3px solid #2e7d32 !important; }
[data-testid="stMetricValue"] { color: #1a2e1a !important; font-size: 16px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #5a8a5a !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.stButton > button { background: #f0f7f0 !important; color: #2e7d32 !important; border: 1px solid #c8e0c8 !important; border-radius: 6px !important; font-weight: 500 !important; font-size: 12px !important; }
.stButton > button:hover { background: #2e7d32 !important; color: #ffffff !important; }
h1 { color: #1a2e1a !important; font-size: 20px !important; font-weight: 700 !important; }
h2 { color: #2d4a2d !important; font-size: 16px !important; font-weight: 600 !important; }
p { color: #1a3a1a !important; font-size: 13px; }
hr { border: none !important; border-top: 1px solid #e0e8e0 !important; margin: 14px 0 !important; }
.stTextInput input, .stNumberInput input, .stTextArea textarea { background: #ffffff !important; border: 1px solid #c8e0c8 !important; color: #1a2e1a !important; border-radius: 8px !important; font-size: 13px !important; }
.stSelectbox > div > div { background: #ffffff !important; border: 1px solid #c8e0c8 !important; color: #1a2e1a !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab-list"] { background: #f0f7f0 !important; border-radius: 8px !important; padding: 4px !important; border: 1px solid #c8e0c8 !important; }
.stTabs [data-baseweb="tab"] { color: #5a8a5a !important; border-radius: 6px !important; font-size: 12px !important; }
.stTabs [aria-selected="true"] { background: #2e7d32 !important; color: #ffffff !important; }
.stSuccess > div { background: #f0faf0 !important; border-left: 3px solid #2e7d32 !important; color: #2e7d32 !important; border-radius: 8px !important; }
.stError > div { background: #fff5f5 !important; border-left: 3px solid #c62828 !important; color: #c62828 !important; border-radius: 8px !important; }
.stWarning > div { background: #fffbf0 !important; border-left: 3px solid #f0c000 !important; color: #8a6a00 !important; border-radius: 8px !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
[data-testid="stSidebar"] { display: flex !important; visibility: visible !important; width: 260px !important; min-width: 260px !important; }
.block-container { padding: 2rem 2rem 2rem !important; max-width: 1200px !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES ──────────────────────────────────
USUARIOS = {
    "tamires": {"senha": "9cd2r11QvOqD8a", "equipe": "tamires", "role": "admin",  "nome": "Tamires"},
    "luciano": {"senha": "TCLemDjWSGv!yz", "equipe": "luciano", "role": "gestor", "nome": "Luciano"},
    "deborah": {"senha": "L4f10IJo5bGJ3O", "equipe": "deborah", "role": "gestor", "nome": "Déborah"},
    "veloso":  {"senha": "U2B!niJH7W96rL", "equipe": None,      "role": "diretor","nome": "Veloso"},
    "moyara":  {"senha": "ug8omeP4Cvt3nl", "equipe": None,      "role": "diretor","nome": "Moyara"},
    "gabriel": {"senha": "gabriel123",      "equipe": "metcool", "role": "gestor", "nome": "Gabriel"},
}

EQUIPES = {
    "luciano": {"nome": "Luciano", "cor": "#2daf5c"},
    "deborah": {"nome": "Déborah", "cor": "#a855f7"},
    "tamires": {"nome": "Tamires", "cor": "#f97316"},
    "metcool": {"nome": "Meet Call", "cor": "#3b82f6"},
}

MESES_NOMES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

SEMANAS_MONITORIA = [
    "1ª Semana — 1ª Monitoria", "1ª Semana — 2ª Monitoria",
    "2ª Semana — 1ª Monitoria", "2ª Semana — 2ª Monitoria",
    "3ª Semana — 1ª Monitoria", "3ª Semana — 2ª Monitoria",
    "4ª Semana — 1ª Monitoria", "4ª Semana — 2ª Monitoria",
]

# ── NOVOS CRITÉRIOS (Ficha iGreen 2026) ────────
CRITERIOS_PADRAO = [
    {
        "id": "c1", "num": "1º", "nome": "Abertura e Identificação", "peso": 5, "obrigatorio": False,
        "itens": [
            "Realiza a primeira interação em até 5 segundos após o início da ligação",
            "Chama o cliente pelo nome",
            "Apresenta-se pelo próprio nome",
            "Identifica a empresa como iGreen"
        ]
    },
    {
        "id": "c2", "num": "2º", "nome": "Comunicação e Postura", "peso": 30, "obrigatorio": False,
        "itens": [
            "Utiliza tom cordial e empático",
            "Demonstra interesse, engajamento e senso de urgência na tratativa",
            "Apresenta 'sorriso na voz', escuta ativa e postura colaborativa/positiva",
            "Utiliza comunicação clara e adequada",
            "Evita erros de pronúncia e vícios de linguagem (gírias, gerundismo, abreviações inadequadas)"
        ]
    },
    {
        "id": "c3", "num": "3º", "nome": "Diagnóstico da Dívida", "peso": 25, "obrigatorio": False,
        "itens": [
            "Realiza perguntas claras, objetivas e relevantes para compreender a situação",
            "Identifica corretamente o motivo da inadimplência",
            "Verifica se o cliente se recorda do contrato",
            "Confirma se o cliente recebeu o boleto",
            "Investiga a previsão de pagamento e demais informações necessárias"
        ]
    },
    {
        "id": "c4", "num": "4º", "nome": "Registros e Procedimentos", "peso": 5, "obrigatorio": False,
        "itens": [
            "Realiza o registro correto no sistema",
            "Classifica adequadamente a ligação"
        ]
    },
    {
        "id": "c5", "num": "5º", "nome": "Conformidade / Condução da Retenção", "peso": 10, "obrigatorio": False,
        "itens": [
            "Identifica a causa do cancelamento e conduz a tratativa de forma assertiva",
            "Utiliza argumentos personalizados para superar objeções",
            "Demonstra criatividade, percepção e persuasão",
            "Atua na causa-raiz da objeção e conduz a retenção de acordo com a situação do cliente"
        ]
    },
    {
        "id": "c6", "num": "6º", "nome": "iGreen Club — apresentação e benefícios", "peso": 20, "obrigatorio": True,
        "itens": [
            "! Obrigatório: Verifica se o cliente já possui o aplicativo iGreen Club",
            "! Obrigatório: Apresenta verbalmente pelo menos 2 vantagens/benefícios do iGreen Club durante a ligação"
        ]
    },
    {
        "id": "c7", "num": "7º", "nome": "Encerramento", "peso": 5, "obrigatorio": False,
        "itens": [
            "Realiza o encerramento de forma adequada e cordial",
            "Pergunta se o cliente possui alguma dúvida ou necessidade adicional",
            "Quando houver negociação, reforça as condições da negociação realizada"
        ]
    },
]

ERROS_CRITICOS_PADRAO = [
    {"id": "e1", "nome": "Postura ríspida, desrespeitosa ou antiética",
     "desc": "Rudeza, impaciência, irritação, pressão indevida, desrespeito, ironia, deboche, linguagem de baixo calão, conversas paralelas em canal aberto, difamação/calúnia contra a iGreen ou parceiros"},
    {"id": "e2", "nome": "Falha grave na abertura ou encerramento",
     "desc": "Não realizar a primeira interação em até 10 segundos ou efetuar desconexão/encerramento inadequado sem conclusão da tratativa"},
    {"id": "e3", "nome": "Abandono do cliente",
     "desc": "Não responder quando o cliente retornar durante uma pausa ou consulta"},
    {"id": "e4", "nome": "Informação incorreta, incompleta ou inverídica",
     "desc": "Com potencial de causar prejuízo financeiro ou de imagem, incluindo prometer boleto, ligação, priorização ou qualquer ação não realizada, bem como envio incorreto de boleto"},
    {"id": "e5", "nome": "Falha grave na argumentação de retenção",
     "desc": "Não realizar tentativa efetiva de retenção diante de intenção clara de cancelamento, não buscar superar a objeção ou não apresentar alternativa que poderia evitar o cancelamento"},
    {"id": "e6", "nome": "Retenção indevida da ligação",
     "desc": "Manter o cliente em espera/linha sem necessidade ou justificativa"},
]

FAIXAS_PONTOS = [(0,70,0),(71,80,300),(81,90,500),(91,95,700),(96,99,1000),(100,100,1100)]

# ── MONGODB ─────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(
        st.secrets["mongo"]["uri"],
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=15000,
        maxPoolSize=10,
        retryWrites=True,
    )
    return client[st.secrets["mongo"]["db"]]

def get_criterios():
    try:
        doc = get_db().configuracoes.find_one({"_id": "criterios_monitoria"})
        if doc and doc.get("criterios"):
            return doc["criterios"]
    except:
        pass
    return CRITERIOS_PADRAO

def salvar_criterios(c):
    get_db().configuracoes.update_one(
        {"_id": "criterios_monitoria"},
        {"$set": {"_id": "criterios_monitoria", "criterios": c, "atualizadoEm": datetime.now()}},
        upsert=True
    )

def get_erros_criticos():
    try:
        doc = get_db().configuracoes.find_one({"_id": "erros_criticos_monitoria"})
        if doc and doc.get("erros"):
            return doc["erros"]
    except:
        pass
    return ERROS_CRITICOS_PADRAO

def salvar_erros_criticos(e):
    get_db().configuracoes.update_one(
        {"_id": "erros_criticos_monitoria"},
        {"$set": {"_id": "erros_criticos_monitoria", "erros": e, "atualizadoEm": datetime.now()}},
        upsert=True
    )

@st.cache_data(ttl=3600)
def buscar_operadores(eq):
    ops = list(get_db().operadores.find({"equipeId": eq}).sort("nome", 1))
    vistos = set()
    unicos = []
    for op in ops:
        nome_norm = op.get("nome", "").strip().lower()
        if nome_norm not in vistos:
            vistos.add(nome_norm)
            unicos.append(op)
    return unicos

def salvar_operador(eq, nome, pleno=False):
    oid = re.sub(r'[^a-z0-9]', '-', nome.lower().strip())
    oid = re.sub(r'-+', '-', oid).strip('-')
    oid = f"{eq[:3]}-{oid}"[:40]
    if not get_db().operadores.find_one({"_id": oid}):
        get_db().operadores.insert_one({"_id": oid, "equipeId": eq, "nome": nome, "pleno": pleno, "criadoEm": datetime.now()})
    return oid

def atualizar_operador(oid, nome, pleno):
    get_db().operadores.update_one({"_id": oid}, {"$set": {"nome": nome, "pleno": pleno}})

def excluir_operador(oid):
    get_db().operadores.delete_one({"_id": oid})

def salvar_monitoria(eq, oid, onome, prot, obs, crits, erros, nota, ma, semana=None):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    get_db().monitorias.insert_one({
        "_id": f"mon__{eq}__{oid}__{ts}",
        "equipeId": eq, "opId": oid, "opNome": onome,
        "protocolo": prot, "observacao": obs,
        "criterios": crits, "errosCriticos": erros,
        "nota": nota, "mesAno": ma, "semana_mon": semana,
        "criadoEm": datetime.now()
    })

def buscar_monitorias_operador(oid):
    op_doc = get_db().operadores.find_one({"_id": oid})
    ids_busca = [oid]
    if op_doc and op_doc.get('vinculadoA'):
        ids_busca.append(op_doc['vinculadoA'])
    return list(get_db().monitorias.find({"opId": {"$in": ids_busca}}).sort("criadoEm", -1))

def buscar_monitorias_equipe(eq, ma=None):
    f = {"equipeId": eq}
    if ma:
        f["mesAno"] = ma
    return list(get_db().monitorias.find(f).sort("criadoEm", -1))

def excluir_monitoria(did):
    get_db().monitorias.delete_one({"_id": did})

@st.cache_data(ttl=3600)
def buscar_senha_usuario(uid):
    try:
        doc = get_db().usuarios_senhas.find_one({"_id": uid})
        if doc and doc.get("senha"):
            return doc["senha"]
    except:
        pass
    u = USUARIOS.get(uid)
    if u:
        return u.get("senha")
    return None

def salvar_senha_usuario(uid, nova_senha):
    get_db().usuarios_senhas.update_one(
        {"_id": uid},
        {"$set": {"_id": uid, "senha": nova_senha, "atualizadoEm": datetime.now()}},
        upsert=True
    )
    buscar_senha_usuario.clear()

# ── HELPERS ─────────────────────────────────────
def calc_pontos(media):
    import math
    m = math.floor(media + 0.5)
    for de, ate, pts in FAIXAS_PONTOS:
        if de <= m <= ate:
            return pts
    return 0

def calc_media_operador(oid, ma=None):
    monts = buscar_monitorias_operador(oid)
    if ma:
        monts = [m for m in monts if m.get("mesAno") == ma]
    if not monts:
        return 0, 0
    notas = [m["nota"] for m in monts if "nota" in m]
    if not notas:
        return 0, 0
    return round(sum(notas) / len(notas), 1), len(notas)

def get_status_media(media):
    if media == 0:   return "Zerada",      "#e53935", "#ffebee"
    if media >= 91:  return "Excelente",   "#2e7d32", "#e8f5e9"
    if media >= 81:  return "Bom",         "#1565c0", "#e3f2fd"
    if media >= 71:  return "Regular",     "#f57f17", "#fff8e1"
    return "Em desenvolvimento", "#6d4c41", "#efebe9"

def get_iniciais(nome):
    p = nome.strip().split()
    if len(p) >= 2:
        return (p[0][0] + p[1][0]).upper()
    return nome[:2].upper()

CORES_INICIAIS = ["#1565c0","#2e7d32","#6a1b9a","#bf360c","#00695c","#4527a0","#ad1457","#0277bd","#558b2f","#4e342e"]

def get_cor_inicial(nome):
    return CORES_INICIAIS[sum(ord(c) for c in nome) % len(CORES_INICIAIS)]

def get_todos_meses_ano(ano=None):
    if not ano:
        ano = datetime.now().year
    return [f"{m}-{ano}" for m in MESES_NOMES]

def get_anos_disponiveis():
    hoje = datetime.now()
    return [str(hoje.year), str(hoje.year - 1)]

def header_page(titulo, sub=""):
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #c8e0c8;border-radius:12px;
                padding:22px 28px;margin-bottom:24px;border-left:4px solid #2e7d32;
                box-shadow:0 2px 8px rgba(0,0,0,0.06)">
        <h1 style="margin:0;color:#1a2e1a;font-size:20px;font-weight:700">{titulo}</h1>
        {"<p style='color:#5a8a5a;margin:4px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px'>"+sub+"</p>" if sub else ""}
    </div>""", unsafe_allow_html=True)

def gerar_pdf_monitoria(onome, prot, obs, crits, erros, nota, media, n_mon, ma):
    pontos = calc_pontos(media)
    L = []
    L.append(f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a1a1a;margin:0;padding:0}}
.hdr{{background:#0a2414;color:#fff;padding:32px 40px}}
.logo{{font-size:24px;font-weight:800;color:#2daf5c}}
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
<div class='hdr'><div class='logo'>iGREEN ENERGY</div>
<div style='font-size:13px;color:#5a9a70;margin-top:4px'>Relatório de Monitoria</div></div>
<div class='body'>
<div class='irow'>
  <div><div class='lbl'>Operador</div><div class='val'>{onome}</div></div>
  <div><div class='lbl'>Protocolo</div><div class='val'>{prot}</div></div>
  <div><div class='lbl'>Mês</div><div class='val'>{ma.replace('-',' ')}</div></div>
  <div><div class='lbl'>Data</div><div class='val'>{datetime.now().strftime('%d/%m/%Y')}</div></div>
</div>""")
    if erros:
        L.append("<div class='crit'><strong>MONITORIA ZERADA — Erro Crítico</strong><br>")
        for e in erros:
            L.append(f"• {e['nome']}<br>")
        L.append("</div>")
    L.append("<table><thead><tr><th>#</th><th>Critério</th><th>Peso</th><th>Resultado</th></tr></thead><tbody>")
    for c in crits:
        p = "<span class='ok'>Passou</span>" if c["passou"] else "<span class='no'>Não passou</span>"
        L.append(f"<tr><td>{c['num']}</td><td>{c['nome']}</td><td>{c['peso']}</td><td>{p}</td></tr>")
    L.append("</tbody></table>")
    L.append(f"<div class='nbox'><div style='font-size:13px;color:#5a9a70'>Nota desta Monitoria</div><div class='nnum'>{nota:.0f}%</div></div>")
    L.append(f"<div class='mbox'><div><div class='lbl'>Média ({n_mon} monitorias)</div><div style='font-size:24px;font-weight:800'>{media:.2f}%</div></div><div><div class='lbl'>Pontuação</div><div style='font-size:24px;font-weight:800;color:#1a6b35'>{pontos} pts</div></div></div>")
    if obs:
        L.append(f"<div class='obs'><strong>Observações:</strong><br>{obs}</div>")
    L.append(f"</div><div class='foot'>iGreen Energy · {datetime.now().strftime('%d/%m/%Y às %H:%M')}</div></body></html>")
    return "".join(L)

def gerar_relatorio_monitorias(eq, ma):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    ops = buscar_operadores(eq)
    monitorias = buscar_monitorias_equipe(eq, ma)

    for op in ops:
        vid = op.get('vinculadoA')
        if vid:
            mons_vinc = list(get_db().monitorias.find({"opId": vid, "mesAno": ma}))
            for m in mons_vinc:
                m['opId'] = op['_id']
                m['opNome'] = op['nome']
            monitorias.extend(mons_vinc)

    if not monitorias:
        return None

    semanas = SEMANAS_MONITORIA
    dados = {}
    for m in monitorias:
        oid = m.get('opId')
        nome = m.get('opNome', '')
        sem = m.get('semana_mon', '')
        nota = float(m.get('nota', 0))
        if oid not in dados:
            dados[oid] = {'nome': nome, 'semanas': {}}
        if sem not in dados[oid]['semanas']:
            dados[oid]['semanas'][sem] = []
        dados[oid]['semanas'][sem].append(nota)

    wb = Workbook()
    ws = wb.active
    ws.title = f"Monitorias {ma}"

    cores_semanas = ["DCE9FF","DCE9FF","FFEFD5","FFEFD5","E8FFE8","E8FFE8","FFE4FF","FFE4FF"]
    verde = "1A3D2B"
    branco = "FFFFFF"
    cinza = "F2F4F3"

    ws.merge_cells("A1:A2")
    ws["A1"] = "Analista"
    ws["A1"].font = Font(bold=True, color=branco)
    ws["A1"].fill = PatternFill("solid", start_color=verde)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["A"].width = 30

    semana_grupos = [("1ª Semana", 2, 3), ("2ª Semana", 4, 5), ("3ª Semana", 6, 7), ("4ª Semana", 8, 9)]
    for label, col_ini, col_fim in semana_grupos:
        letra_ini = get_column_letter(col_ini)
        letra_fim = get_column_letter(col_fim)
        ws.merge_cells(f"{letra_ini}1:{letra_fim}1")
        ws[f"{letra_ini}1"] = label
        ws[f"{letra_ini}1"].font = Font(bold=True, color=verde)
        ws[f"{letra_ini}1"].alignment = Alignment(horizontal="center")
        ws[f"{letra_ini}1"].fill = PatternFill("solid", start_color=cores_semanas[col_ini-2])

    for i, col in enumerate(range(2, 10)):
        letra = get_column_letter(col)
        ws[f"{letra}2"] = "1ª Monitoria" if i % 2 == 0 else "2ª Monitoria"
        ws[f"{letra}2"].font = Font(bold=True)
        ws[f"{letra}2"].fill = PatternFill("solid", start_color=cores_semanas[i])
        ws[f"{letra}2"].alignment = Alignment(horizontal="center")
        ws.column_dimensions[letra].width = 12

    ws.merge_cells("J1:J2")
    ws["J1"] = "MÉDIA"
    ws["J1"].font = Font(bold=True, color=branco)
    ws["J1"].fill = PatternFill("solid", start_color=verde)
    ws["J1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["J"].width = 10

    row = 3
    medias_semana = {s: [] for s in semanas}

    for oid, info in sorted(dados.items(), key=lambda x: x[1]['nome']):
        ws[f"A{row}"] = info['nome']
        if row % 2 == 0:
            ws[f"A{row}"].fill = PatternFill("solid", start_color=cinza)

        notas_brutas_op = []
        for i, sem in enumerate(semanas):
            col = i + 2
            letra = get_column_letter(col)
            notas = info['semanas'].get(sem, [])
            if notas:
                media = sum(notas) / len(notas)
                ws[f"{letra}{row}"] = f"{int(round(media))}%"
                ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
                ws[f"{letra}{row}"].fill = PatternFill("solid", start_color=cores_semanas[i])
                notas_brutas_op.extend(notas)
                medias_semana[sem].append(media)
            else:
                ws[f"{letra}{row}"] = "—"
                ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
                ws[f"{letra}{row}"].fill = PatternFill("solid", start_color=cores_semanas[i])

        if notas_brutas_op:
            media_op = sum(notas_brutas_op) / len(notas_brutas_op)
            ws[f"J{row}"] = f"{int(round(media_op))}%"
            ws[f"J{row}"].font = Font(bold=True)
            ws[f"J{row}"].alignment = Alignment(horizontal="center")

        row += 1

    ws[f"A{row}"] = "Média Equipe"
    ws[f"A{row}"].font = Font(bold=True, color="2D6A4F")
    ws[f"A{row}"].fill = PatternFill("solid", start_color="D8F3DC")

    for i, sem in enumerate(semanas):
        col = i + 2
        letra = get_column_letter(col)
        if medias_semana[sem]:
            m = sum(medias_semana[sem]) / len(medias_semana[sem])
            ws[f"{letra}{row}"] = f"{int(round(m))}%"
            ws[f"{letra}{row}"].font = Font(bold=True, color="2D6A4F")
            ws[f"{letra}{row}"].fill = PatternFill("solid", start_color="D8F3DC")
            ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
        else:
            ws[f"{letra}{row}"] = "—"
            ws[f"{letra}{row}"].fill = PatternFill("solid", start_color="D8F3DC")
            ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")

    medias_ops = []
    for oid, info in dados.items():
        todas = [n for notas in info["semanas"].values() for n in notas]
        if todas:
            medias_ops.append(sum(todas) / len(todas))

    if medias_ops:
        media_geral = sum(medias_ops) / len(medias_ops)
        ws[f"J{row}"] = f"{int(round(media_geral))}%"
        ws[f"J{row}"].font = Font(bold=True, color="2D6A4F")
        ws[f"J{row}"].fill = PatternFill("solid", start_color="D8F3DC")
        ws[f"J{row}"].alignment = Alignment(horizontal="center")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ── LOGIN ────────────────────────────────────────
def tela_login():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="background:#003318;border-radius:16px;padding:40px 32px;
        box-shadow:0 8px 32px rgba(0,0,0,0.3);border:1px solid #005a25">
        <div style="text-align:center;padding:0 0 28px">
            <div style="font-size:28px;font-weight:800;color:#ffffff;margin-bottom:4px">iGreen</div>
            <div style="width:36px;height:2px;background:#00c853;margin:6px auto 10px"></div>
            <p style="color:#5a9a70;font-size:11px;text-transform:uppercase;letter-spacing:2px;margin:0">Monitorias de Qualidade</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px'>USUÁRIO</p>", unsafe_allow_html=True)
        usuario = st.text_input("u", placeholder="seu usuário", label_visibility="collapsed")
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px;margin-top:12px'>SENHA</p>", unsafe_allow_html=True)
        senha = st.text_input("s", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Entrar", use_container_width=True):
            uid = usuario.lower().strip()
            u = USUARIOS.get(uid)
            if u:
                senha_correta = buscar_senha_usuario(uid) or u.get("senha")
                if senha_correta and senha.strip() == senha_correta:
                    st.session_state.usuario = {"id": uid, **u}
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
            else:
                st.error("Usuário ou senha incorretos.")
        st.markdown('<p style="text-align:center;color:#1a4d2e;font-size:11px;margin-top:24px">iGreen Energy © 2026</p>', unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────
def render_sidebar():
    u = st.session_state.usuario
    role_label = 'Administrador' if u['role'] == 'admin' else 'Diretoria' if u['role'] in ['diretor','diretor_upload'] else 'Gestor'
    with st.sidebar:
        st.markdown(
            f"<div style='padding:16px 12px 8px'>"
            f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px'>"
            f"<div style='width:34px;height:34px;background:#2e7d32;border-radius:8px;"
            f"display:flex;align-items:center;justify-content:center;font-weight:900;font-size:16px;color:#fff'>iG</div>"
            f"<div><span style='color:#2e7d32;font-weight:700;font-size:15px'>iGreen</span>"
            f"<span style='color:#1a2e1a;font-weight:700;font-size:15px'> Monitorias</span></div>"
            f"</div></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='margin:0 8px 12px;background:#f0f7f0;border:1px solid #c8e0c8;"
            f"border-radius:8px;padding:10px 12px'>"
            f"<div style='color:#2e7d32;font-weight:700;font-size:14px'>{u['nome']}</div>"
            f"<div style='color:#5a8a5a;font-size:11px'>{role_label}</div>"
            f"</div>", unsafe_allow_html=True)

        anos = get_anos_disponiveis()
        ano = st.selectbox('Ano', anos, label_visibility='collapsed')
        meses = get_todos_meses_ano(int(ano))
        mes_labels = [m.split('-')[0] for m in meses]
        mes_sel = st.selectbox('Mês', mes_labels, index=datetime.now().month - 1, label_visibility='collapsed')
        mes_ano = f'{mes_sel}-{ano}'
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if u['role'] == 'admin':
            pags = ['Monitorias', 'Operadores', 'Critérios', 'Minha Conta']
        elif u['role'] == 'diretor':
            pags = ['Monitorias', 'Minha Conta']
        else:
            pags = ['Monitorias', 'Operadores', 'Minha Conta']

        pag = st.radio('Menu', pags, label_visibility='collapsed', index=0)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button('Sair', use_container_width=True):
            del st.session_state.usuario
            st.rerun()
    return mes_ano, pag

# ── OPERADORES ───────────────────────────────────
def pagina_operadores():
    u = st.session_state.usuario
    header_page("Operadores", "Gerencie os operadores da equipe")

    if u['role'] == 'admin':
        eq_opts = list(EQUIPES.keys())
        eq_labels = [f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        eq_sel = st.selectbox("Equipe:", eq_labels, key="op_eq_sel")
        eq = eq_opts[eq_labels.index(eq_sel)]
    else:
        eq = u.get('equipe')

    with st.expander("Cadastrar Novo Operador", expanded=False):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1: nn = st.text_input("Nome", placeholder="Nome completo", key="op_nome_input")
        with c2: np_op = st.checkbox("Pleno", key="op_pleno_input")
        with c3:
            st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
            if st.button("Cadastrar", use_container_width=True, key="op_add_btn"):
                if nn.strip():
                    salvar_operador(eq, nn.strip(), np_op)
                    buscar_operadores.cache_clear()
                    st.success(f"✅ {nn} cadastrado!")
                    st.rerun()
                else:
                    st.error("Digite o nome.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    ops = buscar_operadores(eq)
    if not ops:
        st.info("Nenhum operador cadastrado.")
        return

    for op in ops:
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1: nn = st.text_input("n", value=op["nome"], label_visibility="collapsed", key=f"n_{op['_id']}")
        with c2: np = st.checkbox("Pleno", value=op.get("pleno", False), key=f"p_{op['_id']}")
        with c3:
            if st.button("Salvar", key=f"s_{op['_id']}"): atualizar_operador(op["_id"], nn, np); buscar_operadores.cache_clear(); st.rerun()
        with c4:
            if st.button("Excluir", key=f"d_{op['_id']}"): excluir_operador(op["_id"]); buscar_operadores.cache_clear(); st.rerun()

# ── MONITORIAS ───────────────────────────────────
def pagina_monitorias(ma):
    u = st.session_state.usuario

    if u['role'] == 'diretor':
        pagina_monitorias_diretor(ma)
        return

    if u['role'] == 'admin':
        eq_opts = list(EQUIPES.keys())
        eq_labels = [f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        eq_sel = st.selectbox("Equipe:", eq_labels, key="mon_eq_sel")
        eq = eq_opts[eq_labels.index(eq_sel)]
    else:
        eq = u.get('equipe')

    ops = buscar_operadores(eq)
    if not ops:
        st.warning("Cadastre operadores primeiro.")
        return

    header_page("Monitorias", f"Equipe {EQUIPES.get(eq, {}).get('nome', '')} · {ma.replace('-', ' ')}")

    # Botão relatório
    rel = gerar_relatorio_monitorias(eq, ma)
    if rel:
        st.download_button(
            "⬇️ Baixar Relatório de Monitorias (.xlsx)",
            rel,
            file_name=f"monitorias_{eq}_{ma}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_rel_mon_topo"
        )

    if "mon_op_sel" not in st.session_state: st.session_state.mon_op_sel = None

    if st.session_state.mon_op_sel is None:
        ultimo = st.session_state.pop("mon_ultimo_salvo", None)
        if ultimo:
            st.success(f"Monitoria salva! {ultimo['nome']} — Nota: {ultimo['nota']:.0f}% | Média: {ultimo['media']:.2f}% | Pontos: {ultimo['pontos']}")
            st.markdown(f'<a href="data:text/html;base64,{ultimo["b64"]}" download="Mon_{ultimo["nome"].replace(" ","_")}.html" style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:12px;margin-bottom:12px">Baixar PDF</a>', unsafe_allow_html=True)

        # Resumo equipe
        monts_eq = buscar_monitorias_equipe(eq, ma)
        if monts_eq:
            medias_eq = [calc_media_operador(op["_id"], ma)[0] for op in ops if calc_media_operador(op["_id"], ma)[1] > 0]
            if medias_eq:
                me_eq = sum(medias_eq) / len(medias_eq)
                st_txt, st_cor, _ = get_status_media(me_eq)
                st.markdown(
                    f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:10px;"
                    f"padding:12px 20px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center'>"
                    f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px'>MÉDIA DA EQUIPE — {ma.replace('-',' ').upper()}</div>"
                    f"<div style='color:{st_cor};font-size:22px;font-weight:800;margin-top:2px'>{me_eq:.2f}%</div></div>"
                    f"<div style='text-align:right'><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase'>STATUS</div>"
                    f"<div style='color:{st_cor};font-size:13px;font-weight:600'>{st_txt}</div></div>"
                    f"</div>", unsafe_allow_html=True)

        st.markdown(f"<div style='color:#5a8a5a;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px'>{len(ops)} operadores</div>", unsafe_allow_html=True)

        for i in range(0, len(ops), 4):
            cols = st.columns(4)
            for j, op in enumerate(ops[i:i+4]):
                media, n = calc_media_operador(op["_id"], ma)
                st_txt, st_cor, st_bg = get_status_media(media)
                ini = get_iniciais(op["nome"])
                cini = get_cor_inicial(op["nome"])
                pontos_op = calc_pontos(media)
                with cols[j]:
                    st.markdown(f"""<div style="background:#ffffff;border:1px solid #c8e0c8;border-radius:12px;
                        padding:16px;text-align:center;margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,0.06)">
                        <div style="width:44px;height:44px;background:{cini};border-radius:50%;display:inline-flex;
                        align-items:center;justify-content:center;color:white;font-weight:700;font-size:15px;margin-bottom:8px">{ini}</div>
                        <div style="color:#1a2e1a;font-weight:700;font-size:12px;margin-bottom:4px">{op['nome']}{'  ★' if op.get('pleno') else ''}</div>
                        <div style="color:{st_cor};font-size:20px;font-weight:800">{round(media)}%</div>
                        <div style="color:#5a8a5a;font-size:10px">{n} monitoria{'s' if n != 1 else ''}</div>
                        <div style="color:#2e7d32;font-size:11px;font-weight:600;margin-top:2px">{pontos_op} pts</div>
                    </div>""", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("+ Nova", key=f"nova_{op['_id']}", use_container_width=True):
                            st.session_state.mon_op_sel = op
                            st.rerun()
                    with c2:
                        if st.button("Histórico", key=f"hist_{op['_id']}", use_container_width=True):
                            st.session_state.mon_op_sel = op
                            st.session_state.mon_modo = "historico"
                            st.rerun()
        return

    op = st.session_state.mon_op_sel
    media_op, n_op = calc_media_operador(op["_id"], ma)

    if st.button("← Voltar"):
        st.session_state.mon_op_sel = None
        st.session_state.pop("mon_modo", None)
        st.rerun()

    st.markdown(f"<div style='background:#e8f5e9;border:1px solid #c8e0c8;border-radius:8px;padding:10px 16px;margin-bottom:12px'>"
                f"<span style='color:#2e7d32;font-weight:700;font-size:15px'>👤 {op['nome']}</span>"
                f"<span style='color:#5a8a5a;font-size:12px;margin-left:12px'>Média: {media_op:.0f}% · {n_op} monitoria{'s' if n_op != 1 else ''}</span></div>", unsafe_allow_html=True)
    st.markdown("---")

    t1, t2 = st.tabs(["Nova Monitoria", "Monitorias do Mês"])

    with t1:
        monts_op_mes = [m for m in buscar_monitorias_equipe(eq, ma) if m["opId"] == op["_id"]]
        semanas_usadas = {m.get("semana_mon", "") for m in monts_op_mes}

        semanas_opts = []
        for s in SEMANAS_MONITORIA:
            if s in semanas_usadas:
                semanas_opts.append(f"🔴 {s} — JÁ REGISTRADA")
            else:
                semanas_opts.append(f"✅ {s}")

        semana_sel = st.selectbox("Qual monitoria é esta?", semanas_opts, key="semana_sel")
        semana = SEMANAS_MONITORIA[semanas_opts.index(semana_sel)]
        semana_bloqueada = semana in semanas_usadas

        if semana_bloqueada:
            st.error(f"⛔ A **{semana}** já foi registrada para {op['nome']} em {ma.replace('-',' ')}.")

        prot = st.text_input("Protocolo da Ligação", placeholder="Ex: 20260520-001", key="prot_input")
        obs = st.text_area("Observações", placeholder="Anotações...", height=70, key="obs_input")
        st.markdown("---")

        crits_usar = get_criterios()
        erros_usar = get_erros_criticos()

        # Erros críticos
        st.markdown("<p style='color:#c62828;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>ERROS CRÍTICOS — Qualquer um zera a monitoria</p>", unsafe_allow_html=True)
        erros_m = []
        c1, c2 = st.columns(2)
        for i, ec in enumerate(erros_usar):
            with (c1 if i % 2 == 0 else c2):
                if st.checkbox(f"{ec['nome']}", key=f"ec_{ec['id']}", help=ec['desc']):
                    erros_m.append(ec)

        st.markdown("---")
        zerada = len(erros_m) > 0
        crits_r = []
        nota = 0 if zerada else 100

        if zerada:
            st.error("MONITORIA ZERADA — Erro crítico marcado!")
            for c in crits_usar:
                crits_r.append({**c, "passou": False})
        else:
            st.markdown("<p style='color:#e53935;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>CRITÉRIOS — MARQUE O QUE NÃO FOI FEITO</p>", unsafe_allow_html=True)
            for crit in crits_usar:
                c1, c2 = st.columns([8, 1])
                with c1:
                    nao_passou = st.checkbox(f"{crit['num']} {crit['nome']}", key=f"cr_{crit['id']}", value=False)
                with c2:
                    st.markdown(f"<div style='padding-top:6px;color:#e53935;font-size:12px;font-weight:600;text-align:right'>−{crit['peso']} pts</div>", unsafe_allow_html=True)
                if crit.get('itens'):
                    for it in crit['itens']:
                        cor_it = "#f87171" if "obrigatório" in it.lower() or "!" in it else "#34d399"
                        st.markdown(f"<div style='padding:3px 0 3px 24px;font-size:12px;color:{cor_it};line-height:1.5'>• {it}</div>", unsafe_allow_html=True)
                passou = not nao_passou
                if not passou:
                    nota -= crit["peso"]
                crits_r.append({**crit, "passou": passou})

        nota = max(0, nota)
        pontos_perdidos = 100 - nota
        cn = "#2e7d32" if nota >= 80 else "#f57f17" if nota >= 60 else "#c62828"
        st.markdown(
            f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:10px;padding:14px 20px;margin-top:16px;"
            f"display:flex;justify-content:space-between;align-items:center'>"
            f"<div><div style='color:#5a8a5a;font-size:11px'>Pontuação final (máx. 100 pts)</div>"
            f"<div style='color:#5a8a5a;font-size:11px'>Pontos perdidos: {pontos_perdidos}</div></div>"
            f"<div style='color:{cn};font-size:36px;font-weight:800'>{round(nota)}</div>"
            f"</div>", unsafe_allow_html=True)

        sk_salvo = f"mon_salvo_{op['_id']}_{semana}_{ma}"
        if not st.session_state.get(sk_salvo):
            if st.button("Salvar Monitoria", use_container_width=True, key="btn_salvar_mon", disabled=semana_bloqueada):
                if not prot.strip():
                    st.error("Preencha o Protocolo da Ligação!")
                else:
                    eq_save = u.get('equipe') or (list(EQUIPES.keys())[0] if u['role'] == 'admin' else 'tamires')
                    # Para admin, pegar a equipe do seletor
                    if u['role'] == 'admin':
                        eq_opts_s = list(EQUIPES.keys())
                        eq_labels_s = [f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts_s]
                        eq_save = eq_opts_s[0]
                        for eq_o in eq_opts_s:
                            ops_o = buscar_operadores(eq_o)
                            if any(o['_id'] == op['_id'] for o in ops_o):
                                eq_save = eq_o
                                break
                    salvar_monitoria(eq_save, op["_id"], op["nome"], prot, obs, crits_r, erros_m, nota, ma, semana=semana)
                    mm, nm = calc_media_operador(op["_id"], ma)
                    html = gerar_pdf_monitoria(op["nome"], prot, obs, crits_r, erros_m, nota, mm, nm, ma)
                    b64 = base64.b64encode(html.encode()).decode()
                    st.session_state[sk_salvo] = {"nome": op["nome"], "nota": nota, "media": mm, "pontos": calc_pontos(mm), "b64": b64, "prot": prot}
        else:
            salvo = st.session_state[sk_salvo]
            cn2 = "#2e7d32" if salvo['nota'] >= 80 else "#f57f17" if salvo['nota'] >= 60 else "#c62828"
            st.markdown(
                f"<div style='background:#f0faf0;border:2px solid #2e7d32;border-radius:12px;padding:20px 24px;margin:16px 0'>"
                f"<div style='color:#2e7d32;font-weight:700;font-size:15px;margin-bottom:8px'>✓ Monitoria salva!</div>"
                f"<div style='color:#1a2e1a;font-size:13px'>Nota: <strong style='color:{cn2}'>{salvo['nota']:.0f}%</strong> | "
                f"Média: <strong>{salvo['media']:.2f}%</strong> | Pontos: <strong>{salvo['pontos']}</strong></div>"
                f"</div>", unsafe_allow_html=True)
            st.markdown(
                f'<a href="data:text/html;base64,{salvo["b64"]}" '
                f'download="Monitoria_{salvo["nome"].replace(" ","_")}_{salvo["prot"]}.html" '
                f'style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;'
                f'padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600;font-size:13px;margin-bottom:12px">'
                f'⬇ Baixar PDF da Monitoria</a>', unsafe_allow_html=True)
            if st.button("Concluir e Voltar", use_container_width=True, key="btn_concluir_mon"):
                ultimo = st.session_state.pop(sk_salvo, None)
                st.session_state.mon_op_sel = None
                if ultimo:
                    st.session_state["mon_ultimo_salvo"] = ultimo
                st.rerun()

    with t2:
        monts2 = buscar_monitorias_operador(op["_id"])
        monts2 = [m for m in monts2 if m.get("mesAno") == ma]
        if not monts2:
            st.info(f"Nenhuma monitoria para {op['nome']} em {ma.replace('-',' ')}.")
        else:
            ordem_semanas = {s: i for i, s in enumerate(SEMANAS_MONITORIA)}
            monts2 = sorted(monts2, key=lambda x: ordem_semanas.get(x.get("semana_mon", ""), 99))
            for m in monts2:
                nm = float(m.get("nota", 0))
                cm = "#2e7d32" if nm >= 80 else "#f57f17" if nm >= 60 else "#c62828"
                st.markdown(
                    f"<div style='background:#f8fdf8;border:1px solid #c8e0c8;border-radius:10px;"
                    f"padding:14px 18px;margin-bottom:8px;border-left:3px solid {cm}'>"
                    f"<div style='color:#1a2e1a;font-weight:600'>{m.get('semana_mon','—')}</div>"
                    f"<div style='color:#5a8a5a;font-size:11px'>Protocolo: {m.get('protocolo','—')} · {str(m.get('criadoEm',''))[:10]}</div>"
                    f"<div style='color:{cm};font-size:18px;font-weight:800'>{int(nm)}%</div></div>", unsafe_allow_html=True)
                with st.expander("Ver detalhes"):
                    for c in m.get("criterios", []):
                        passou = c.get("passou", True)
                        cc = "#2e7d32" if passou else "#c62828"
                        st.markdown(
                            f"<div style='display:flex;justify-content:space-between;padding:6px 12px;"
                            f"background:#f0f7f0;border-radius:6px;margin-bottom:4px;border-left:3px solid {cc}'>"
                            f"<span style='color:#1a2e1a;font-size:12px'>{c.get('num','')} {c.get('nome','')}</span>"
                            f"<span style='color:{cc};font-weight:600;font-size:12px'>{'Passou' if passou else 'Não passou'}</span></div>", unsafe_allow_html=True)
                    if m.get("observacao"):
                        st.markdown(f"<div style='padding:8px 12px;background:#f0f7f0;border-radius:6px;border-left:3px solid #5a8a5a;color:#2d4a2d;font-size:12px'><strong>Obs:</strong> {m['observacao']}</div>", unsafe_allow_html=True)
                    mm2, nm2 = calc_media_operador(op["_id"], ma)
                    hp = gerar_pdf_monitoria(op["nome"], m.get("protocolo", ""), m.get("observacao", ""), m.get("criterios", []), m.get("errosCriticos", []), nm, mm2, nm2, ma)
                    b64h = base64.b64encode(hp.encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64h}" download="Mon_{op["nome"].replace(" ","_")}.html" style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;padding:5px 12px;border-radius:5px;text-decoration:none;font-size:12px;margin-top:6px">⬇ Baixar PDF</a>', unsafe_allow_html=True)
                    st.markdown("---")
                    if st.button("Excluir", key=f"del_op_{m['_id']}"):
                        excluir_monitoria(m["_id"])
                        st.rerun()

def pagina_monitorias_diretor(ma):
    header_page("Monitorias", f"Visão Geral · {ma.replace('-',' ')}")
    if "dir_op_sel" not in st.session_state: st.session_state.dir_op_sel = None
    if "dir_eq_sel" not in st.session_state: st.session_state.dir_eq_sel = None

    if st.session_state.dir_op_sel:
        op = st.session_state.dir_op_sel
        eq = st.session_state.dir_eq_sel
        media_op, n_op = calc_media_operador(op["_id"], ma)
        st_txt, st_cor, _ = get_status_media(media_op)
        if st.button("← Voltar"):
            st.session_state.dir_op_sel = None
            st.session_state.dir_eq_sel = None
            st.rerun()
        st.markdown(f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:12px;padding:16px 20px;margin-bottom:16px'>"
                    f"<div style='color:#1a2e1a;font-weight:700;font-size:16px'>{op['nome']}</div>"
                    f"<div style='color:#5a8a5a;font-size:12px'>Equipe {EQUIPES.get(eq,{}).get('nome','—')} · {ma.replace('-',' ')} · Média: <strong style='color:{st_cor}'>{media_op:.2f}%</strong></div></div>", unsafe_allow_html=True)
        monts_op = [m for m in buscar_monitorias_equipe(eq, ma) if m["opId"] == op["_id"]]
        if not monts_op:
            st.info("Nenhuma monitoria registrada neste mês.")
        else:
            for m in monts_op:
                nm = float(m.get("nota", 0))
                cm = "#2e7d32" if nm >= 80 else "#f57f17" if nm >= 60 else "#c62828"
                st.markdown(f"<div style='background:#f8fdf8;border:1px solid #c8e0c8;border-radius:10px;padding:14px 18px;margin-bottom:8px;border-left:3px solid {cm}'>"
                            f"<div style='color:#1a2e1a;font-weight:600'>{m.get('semana_mon','—')}</div>"
                            f"<div style='color:#5a8a5a;font-size:11px'>Protocolo: {m.get('protocolo','—')}</div>"
                            f"<div style='color:{cm};font-size:18px;font-weight:800'>{nm:.0f}%</div></div>", unsafe_allow_html=True)
                with st.expander("Ver detalhes"):
                    for c in m.get("criterios", []):
                        passou = c.get("passou", True)
                        cc = "#2e7d32" if passou else "#c62828"
                        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:6px 12px;background:#f0f7f0;border-radius:6px;margin-bottom:4px;border-left:3px solid {cc}'><span style='color:#1a2e1a;font-size:12px'>{c.get('num','')} {c.get('nome','')}</span><span style='color:{cc};font-weight:600;font-size:12px'>{'Passou' if passou else 'Não passou'}</span></div>", unsafe_allow_html=True)
        return

    linhas_eq = ""
    todas_medias = []
    for eq_pre in ["luciano", "deborah", "tamires"]:
        ops_pre = buscar_operadores(eq_pre)
        medias_pre = [calc_media_operador(op["_id"], ma)[0] for op in ops_pre if calc_media_operador(op["_id"], ma)[1] > 0]
        if medias_pre:
            me_pre = sum(medias_pre) / len(medias_pre)
            nome_eq = EQUIPES.get(eq_pre, {}).get("nome", eq_pre)
            cor_me = "#2e7d32" if me_pre >= 80 else "#f57f17" if me_pre >= 60 else "#c62828"
            linhas_eq += f"<div style='display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #e8f0e8'><span style='color:#2d4a2d;font-size:13px;font-weight:500'>{nome_eq}</span><span style='color:{cor_me};font-size:15px;font-weight:700'>{me_pre:.2f}%</span></div>"
            todas_medias.append(me_pre)

    if todas_medias:
        mg = sum(todas_medias) / len(todas_medias)
        cor_mg = "#2e7d32" if mg >= 80 else "#f57f17" if mg >= 60 else "#c62828"
        linhas_eq += f"<div style='border-top:1px solid #c8e0c8;margin-top:6px;padding-top:8px;display:flex;justify-content:space-between;align-items:center'><span style='color:#2d4a2d;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px'>Média Geral</span><span style='color:{cor_mg};font-size:22px;font-weight:800'>{mg:.2f}%</span></div>"
        st.markdown(f"<div style='background:#ffffff;border:1px solid #c8e0c8;border-radius:12px;padding:16px 24px;margin-bottom:20px;border-left:4px solid #2e7d32'>{linhas_eq}</div>", unsafe_allow_html=True)

    for eq in EQUIPES:
        ops = buscar_operadores(eq)
        if not ops: continue
        monts = buscar_monitorias_equipe(eq, ma)
        if not monts: continue
        medias = {op["nome"]: (op, calc_media_operador(op["_id"], ma)) for op in ops}
        medias = {k: v for k, v in medias.items() if v[1][1] > 0}
        if not medias: continue
        me = sum(v[1][0] for v in medias.values()) / len(medias)
        cor = "#2e7d32" if me >= 80 else "#f57f17" if me >= 60 else "#c62828"
        st.markdown(f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:3px solid #2e7d32'><div style='display:flex;justify-content:space-between;align-items:center'><div style='font-size:15px;font-weight:700;color:#1a2e1a'>Equipe {EQUIPES[eq]['nome']}</div><div style='text-align:right'><div style='color:#5a8a5a;font-size:10px;text-transform:uppercase'>MÉDIA</div><div style='color:{cor};font-size:24px;font-weight:800'>{me:.2f}%</div></div></div></div>", unsafe_allow_html=True)
        cols_op = st.columns(4)
        for idx_op, (nome, (op_obj, (media, n))) in enumerate(sorted(medias.items(), key=lambda x: -x[1][1][0])):
            st_txt, st_cor, _ = get_status_media(media)
            with cols_op[idx_op % 4]:
                st.markdown(f"<div style='background:#ffffff;border:1px solid #c8e0c8;border-radius:10px;padding:12px;text-align:center;margin-bottom:8px'><div style='color:#1a2e1a;font-weight:600;font-size:12px'>{nome}</div><div style='color:{st_cor};font-size:18px;font-weight:800'>{media:.2f}%</div><div style='color:#5a8a5a;font-size:10px'>{n} monitoria{'s' if n!=1 else ''}</div></div>", unsafe_allow_html=True)
                if st.button("Ver detalhes", key=f"dir_op_{op_obj['_id']}", use_container_width=True):
                    st.session_state.dir_op_sel = op_obj
                    st.session_state.dir_eq_sel = eq
                    st.rerun()
        st.markdown("---")

# ── CRITÉRIOS ────────────────────────────────────
def pagina_criterios():
    header_page("Critérios de Monitoria", "Configure os critérios de avaliação")
    crits = get_criterios()
    erros = get_erros_criticos()
    t1, t2 = st.tabs(["Critérios de Avaliação", "Erros Críticos"])
    with t1:
        st.markdown("**Distribuição: 100 pontos totais. Alterações valem apenas para novas monitorias.**")
        total_peso = sum(c['peso'] for c in crits)
        st.markdown(f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:8px;padding:10px 16px;margin-bottom:16px'>"
                    f"<span style='color:#2e7d32;font-weight:700'>Total configurado: {total_peso} pts</span>"
                    f"{'  ✅' if total_peso == 100 else '  ⚠️ Deve somar 100'}</div>", unsafe_allow_html=True)
        st.markdown("---")
        ce = []
        for i, c in enumerate(crits):
            with st.expander(f"{c['num']} {c['nome']} — {c['peso']} pts", expanded=False):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1: nm = st.text_input("Nome", value=c["nome"], key=f"cn_{i}")
                with col2: ps = st.number_input("Peso", min_value=1, max_value=100, value=int(c["peso"]), key=f"cp_{i}")
                with col3: ob = st.checkbox("Obrigatório", value=c.get("obrigatorio", False), key=f"co_{i}")
                it = st.text_area("Itens (um por linha)", value="\n".join(c.get("itens", [])), height=100, key=f"ci_{i}")
                ce.append({"id": c["id"], "num": c["num"], "nome": nm, "peso": ps, "obrigatorio": ob,
                           "itens": [x.strip() for x in it.split("\n") if x.strip()]})
        st.markdown("---")
        if st.button("Salvar Critérios", use_container_width=True):
            salvar_criterios(ce)
            st.success("Critérios salvos!")
            st.rerun()
    with t2:
        st.markdown("**Erros que zeram a monitoria automaticamente.**")
        st.markdown("---")
        ee = []
        for i, e in enumerate(erros):
            col1, col2 = st.columns([2, 3])
            with col1: ne = st.text_input("Nome", value=e["nome"], key=f"en_{i}")
            with col2: de = st.text_input("Descrição", value=e["desc"], key=f"ed_{i}")
            ee.append({"id": e["id"], "nome": ne, "desc": de})
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Salvar Erros Críticos", use_container_width=True):
                salvar_erros_criticos(ee)
                st.success("Salvo!")
                st.rerun()
        with col2:
            if st.button("Adicionar Erro", use_container_width=True):
                ee.append({"id": f"e{len(erros)+1}", "nome": "Novo erro", "desc": "Descrição"})
                salvar_erros_criticos(ee)
                st.rerun()

# ── MINHA CONTA ──────────────────────────────────
def pagina_minha_conta():
    u = st.session_state.usuario
    header_page('Minha Conta', u['nome'])
    st.markdown("### 🔒 Alterar Senha")
    sa = st.text_input('Senha atual', type='password', placeholder='senha atual')
    sn = st.text_input('Nova senha', type='password', placeholder='mín. 8 caracteres')
    sc2 = st.text_input('Confirmar senha', type='password', placeholder='repita a nova senha')
    if st.button('Salvar Senha', use_container_width=True):
        uid = u['id']
        sc = buscar_senha_usuario(uid) or u.get('senha')
        if not sa: st.error('Digite a senha atual.')
        elif sa != sc: st.error('Senha atual incorreta.')
        elif len(sn) < 8: st.error('Mínimo 8 caracteres.')
        elif sn != sc2: st.error('Confirmação não confere.')
        else:
            salvar_senha_usuario(uid, sn)
            st.success('✅ Senha alterada com sucesso!')

# ── MAIN ─────────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login()
        return

    ma, pag = render_sidebar()
    u = st.session_state.usuario

    if 'Monitorias' in pag:
        pagina_monitorias(ma)
    elif 'Operadores' in pag:
        pagina_operadores()
    elif 'Critérios' in pag and u['role'] == 'admin':
        pagina_criterios()
    elif 'Minha Conta' in pag:
        pagina_minha_conta()

if __name__ == "__main__":
    main()
