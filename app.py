def gerar_relatorio_monitorias(eq, ma):
    """Gera relatório de monitorias no formato: analista x semana."""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    ops = buscar_operadores(eq)
    monitorias = buscar_monitorias_equipe(eq, ma)

    if not monitorias:
        return None

    # Usar exatamente os valores de SEMANAS_MONITORIA como chaves
    semanas = SEMANAS_MONITORIA  # ["1ª Semana — 1ª Monitoria", ...]

    # Mapear monitorias por opId e semana_mon
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

    if not dados:
        return None

    # Criar Excel
    wb = Workbook()
    ws = wb.active
    ws.title = f"Monitorias {ma}"

    # Cores
    cores_semanas = ["DCE9FF", "DCE9FF", "FFEFD5", "FFEFD5", "E8FFE8", "E8FFE8", "FFE4FF", "FFE4FF"]
    verde = "1A3D2B"
    branco = "FFFFFF"
    cinza = "F2F4F3"

    # Cabeçalho linha 1 — Semanas agrupadas (4 grupos de 2 colunas cada)
    ws.merge_cells("A1:A2")
    ws["A1"] = "Analista"
    ws["A1"].font = Font(bold=True, color=branco)
    ws["A1"].fill = PatternFill("solid", start_color=verde)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["A"].width = 30

    semana_grupos = [
        ("1ª Semana", 2, 3),
        ("2ª Semana", 4, 5),
        ("3ª Semana", 6, 7),
        ("4ª Semana", 8, 9),
    ]
    for label, col_ini, col_fim in semana_grupos:
        letra_ini = get_column_letter(col_ini)
        letra_fim = get_column_letter(col_fim)
        ws.merge_cells(f"{letra_ini}1:{letra_fim}1")
        ws[f"{letra_ini}1"] = label
        ws[f"{letra_ini}1"].font = Font(bold=True, color=verde)
        ws[f"{letra_ini}1"].alignment = Alignment(horizontal="center")
        ws[f"{letra_ini}1"].fill = PatternFill("solid", start_color=cores_semanas[col_ini - 2])

    # Cabeçalho linha 2 — 1ª Monitoria / 2ª Monitoria
    for i, col in enumerate(range(2, 10)):
        letra = get_column_letter(col)
        ws[f"{letra}2"] = "1ª Monitoria" if i % 2 == 0 else "2ª Monitoria"
        ws[f"{letra}2"].font = Font(bold=True)
        ws[f"{letra}2"].fill = PatternFill("solid", start_color=cores_semanas[i])
        ws[f"{letra}2"].alignment = Alignment(horizontal="center")
        ws.column_dimensions[letra].width = 14

    # MÉDIA
    ws.merge_cells("J1:J2")
    ws["J1"] = "MÉDIA"
    ws["J1"].font = Font(bold=True, color=branco)
    ws["J1"].fill = PatternFill("solid", start_color=verde)
    ws["J1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["J"].width = 10

    # Dados por operador
    row = 3
    medias_semana = {s: [] for s in semanas}

    for oid, info in sorted(dados.items(), key=lambda x: x[1]['nome']):
        ws[f"A{row}"] = info['nome']
        if row % 2 == 0:
            ws[f"A{row}"].fill = PatternFill("solid", start_color=cinza)

        notas_op = []
        for i, sem in enumerate(semanas):
            col = i + 2
            letra = get_column_letter(col)
            notas = info['semanas'].get(sem, [])
            if notas:
                media = sum(notas) / len(notas)
                ws[f"{letra}{row}"] = f"{int(round(media))}%"
                ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
                ws[f"{letra}{row}"].fill = PatternFill("solid", start_color=cores_semanas[i])
                notas_op.append(media)
                medias_semana[sem].append(media)
            else:
                ws[f"{letra}{row}"] = "—"
                ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
                ws[f"{letra}{row}"].fill = PatternFill("solid", start_color=cores_semanas[i])

        if notas_op:
            media_op = sum(notas_op) / len(notas_op)
            ws[f"J{row}"] = f"{int(round(media_op))}%"
            ws[f"J{row}"].font = Font(bold=True)
            ws[f"J{row}"].alignment = Alignment(horizontal="center")

        row += 1

    # Linha média equipe
    ws[f"A{row}"] = "Média Equipe"
    ws[f"A{row}"].font = Font(bold=True, color="2D6A4F")
    ws[f"A{row}"].fill = PatternFill("solid", start_color="D8F3DC")

    todas_medias = []
    for i, sem in enumerate(semanas):
        col = i + 2
        letra = get_column_letter(col)
        if medias_semana[sem]:
            m = sum(medias_semana[sem]) / len(medias_semana[sem])
            ws[f"{letra}{row}"] = f"{int(round(m))}%"
            ws[f"{letra}{row}"].font = Font(bold=True, color="2D6A4F")
            ws[f"{letra}{row}"].fill = PatternFill("solid", start_color="D8F3DC")
            ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
            todas_medias.append(m)
        else:
            ws[f"{letra}{row}"] = "—"
            ws[f"{letra}{row}"].fill = PatternFill("solid", start_color="D8F3DC")
            ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")

    if todas_medias:
        media_geral = sum(todas_medias) / len(todas_medias)
        ws[f"J{row}"] = f"{int(round(media_geral))}%"
        ws[f"J{row}"].font = Font(bold=True, color="2D6A4F")
        ws[f"J{row}"].fill = PatternFill("solid", start_color="D8F3DC")
        ws[f"J{row}"].alignment = Alignment(horizontal="center")

    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 20

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()
