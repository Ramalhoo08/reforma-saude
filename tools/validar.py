"""Valida data/boletins.json e data/dossie.json antes de publicar. Uso: python tools/validar.py"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUS = {"em vigor", "regulamentado", "em discussão"}
erros = []


def fontes(lista, onde):
    if not isinstance(lista, list) or not lista:
        erros.append(f"{onde}: precisa de ao menos uma fonte")
        return
    for f in lista:
        if not isinstance(f, dict) or not str(f.get("url", "")).startswith("https://"):
            erros.append(f"{onde}: fonte sem url https -> {f}")


boletins = json.loads((ROOT / "data/boletins.json").read_text(encoding="utf-8"))
dossie = json.loads((ROOT / "data/dossie.json").read_text(encoding="utf-8"))

if not isinstance(boletins, list) or not boletins:
    erros.append("boletins.json deve ser uma lista não vazia")
    boletins = []
datas = [b.get("data") for b in boletins]
if len(set(datas)) != len(datas):
    erros.append("boletins.json tem datas repetidas")
edicoes = [b.get("edicao") for b in boletins]
if len(set(edicoes)) != len(edicoes):
    erros.append("boletins.json tem edições repetidas")

for b in boletins:
    onde = f"boletim {b.get('data')}"
    if not DATA.match(str(b.get("data", ""))):
        erros.append(f"{onde}: data inválida")
    if not isinstance(b.get("edicao"), int):
        erros.append(f"{onde}: edicao deve ser número inteiro")
    if not str(b.get("resumo", "")).strip():
        erros.append(f"{onde}: resumo vazio")
    for i, it in enumerate(b.get("itens", [])):
        o = f"{onde} item {i + 1}"
        for k in ("titulo", "oQueMudou", "impacto", "acao"):
            if not str(it.get(k, "")).strip():
                erros.append(f"{o}: campo {k} vazio")
        if it.get("alcance", "saúde") not in ("saúde", "geral"):
            erros.append(f"{o}: alcance deve ser 'saúde' ou 'geral'")
        if it.get("status") not in STATUS:
            erros.append(f"{o}: status deve ser um de {sorted(STATUS)}")
        for k in ("dataPublicacao", "prazo"):
            if it.get(k) and not DATA.match(str(it[k])):
                erros.append(f"{o}: {k} fora do formato AAAA-MM-DD")
        fontes(it.get("fontes"), o)
    for a in b.get("agenda", []):
        if not DATA.match(str(a.get("data", ""))) or not str(a.get("evento", "")).strip():
            erros.append(f"{onde}: agenda inválida -> {a}")

ids = [d.get("id") for d in dossie]
if len(set(ids)) != len(ids):
    erros.append("dossie.json tem ids repetidos")
for d in dossie:
    o = f"dossiê {d.get('id')}"
    for k in ("titulo", "resumo", "impacto", "acao"):
        if not str(d.get(k, "")).strip():
            erros.append(f"{o}: campo {k} vazio")
    if d.get("status") not in STATUS:
        erros.append(f"{o}: status inválido")
    if not isinstance(d.get("ordem"), int):
        erros.append(f"{o}: ordem deve ser número inteiro")
    fontes(d.get("fontes"), o)

if erros:
    print("ERROS:\n- " + "\n- ".join(erros))
    sys.exit(1)
print(f"OK: {len(boletins)} boletins, {len(dossie)} temas no dossiê")
