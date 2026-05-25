# 🌿 iGreen Resultados — Streamlit + MongoDB

## PASSO 1 — Liberar IP no MongoDB (2 min)

1. Acesse https://cloud.mongodb.com
2. Menu esquerdo → **Segurança → Acesso à Rede**
3. Clique em **"+ Adicionar endereço IP"**
4. Clique em **"Permitir acesso de qualquer lugar"** → preenche 0.0.0.0/0
5. Clique em **Confirmar**

---

## PASSO 2 — Subir no GitHub (5 min)

1. Acesse https://github.com/inadimplencia-igreen
2. Clique em **"New repository"**
3. Nome: `igreen-resultados`
4. Marque **Public** → **Create repository**
5. Na pasta `igreen-streamlit` do seu computador, abra o terminal e execute:

```bash
git init
git add .
git commit -m "primeiro commit"
git branch -M main
git remote add origin https://github.com/inadimplencia-igreen/igreen-resultados.git
git push -u origin main
```

---

## PASSO 3 — Publicar no Streamlit Cloud (5 min)

1. Acesse https://share.streamlit.io
2. Faça login com **GitHub**
3. Clique em **"New app"**
4. Configure:
   - **Repository:** `inadimplencia-igreen/igreen-resultados`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Clique em **"Advanced settings"**
6. Em **Secrets**, cole exatamente isso (com sua senha):

```toml
[mongo]
db  = "igreen_resultados"
```

7. Clique em **"Deploy!"**
8. Aguarde ~2 minutos. Seu site estará online! 🎉

---


⚠️ Para trocar as senhas edite o arquivo `app.py` na seção `USUARIOS`.

---

## Funcionalidades

- ✅ Login por perfil
- ✅ Lançamento quarta e sexta
- ✅ Meta editável por agente
- ✅ Dias trabalhados e total editáveis
- ✅ Projeção automática
- ✅ ↑↓ vs semana anterior
- ✅ Histórico por mês
- ✅ Veloso vê tudo consolidado
- ✅ Export Excel
- ✅ MongoDB Atlas — dados nunca somem
- ✅ Tema escuro iGreen
