"""Baixa o radar de notícias da reforma para a rotina diária (a nuvem do Claude não acessa sites).

Uso: python tools/radar.py PASTA_DE_SAIDA
Gera noticias.json (Google Notícias), paginas/*.md (páginas de notícias oficiais) e status.json.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

SP = timezone(timedelta(hours=-3))  # São Paulo não tem horário de verão desde 2019
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
JANELAS = (1, 2, 7)  # o Google devolve no máximo 100 notícias por busca: janelas curtas garantem as do dia
CONSULTAS = {
    "reforma": '"reforma tributária"',
    "ibs_cbs": '(IBS OR CBS OR "Imposto Seletivo" OR "alíquota de referência" OR "Comitê Gestor")',
    "saude": 'reforma tributária (saúde OR médicos OR clínicas OR hospitais OR "planos de saúde" OR cooperativas OR laboratórios)',
    "simples_nfse": '("Simples Nacional" OR "NFS-e" OR "split payment" OR DeRE) (IBS OR CBS OR reforma)',
    "renda": '("tributação de dividendos" OR "IR mínimo" OR "imposto mínimo" OR "Lei 15.270" OR "reforma da renda" OR "isenção do IR")',
}
MESES = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
DATA = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")


def baixar(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def google_noticias(consulta, dias):
    q = urllib.parse.quote(f"{consulta} when:{dias}d")
    return ler_rss(baixar(f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"))


def ler_rss(xml):
    itens = []
    for it in ET.fromstring(xml).iter("item"):
        fonte = it.find("source")
        veiculo = fonte.text.strip() if fonte is not None and fonte.text else ""
        titulo = (it.findtext("title") or "").strip()
        if veiculo and titulo.endswith(" - " + veiculo):
            titulo = titulo[: -len(veiculo) - 3]
        try:
            quando = parsedate_to_datetime(it.findtext("pubDate")).astimezone(SP).strftime("%Y-%m-%d %H:%M")
        except (TypeError, ValueError):
            quando = ""
        itens.append({"quando": quando, "veiculo": veiculo, "titulo": titulo,
                      "site": fonte.get("url", "") if fonte is not None else "",
                      "link_google": it.findtext("link") or ""})
    return itens


class Texto(HTMLParser):
    """HTML -> linhas de texto, com links longos como [texto](url): mantém manchetes, datas e endereços."""
    PULAR = {"script", "style", "noscript", "svg", "head"}

    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base, self.linhas, self.pulo, self.link, self.buf = base, [], 0, None, []

    def handle_starttag(self, tag, attrs):
        if tag in self.PULAR:
            self.pulo += 1
        elif tag == "a" and not self.pulo:
            self.link, self.buf = dict(attrs).get("href"), []

    def handle_endtag(self, tag):
        if tag in self.PULAR and self.pulo:
            self.pulo -= 1
        elif tag == "a" and self.link is not None:
            texto = " ".join(" ".join(self.buf).split())
            if len(texto) >= 25 and not self.link.startswith(("#", "javascript:", "mailto:")):
                self.linhas.append(f"[{texto}]({urllib.parse.urljoin(self.base, self.link)})")
            elif texto:
                self.linhas.append(texto)
            self.link = None

    def handle_data(self, data):
        if self.pulo:
            return
        if self.link is not None:
            self.buf.append(data)
        elif data.strip():
            self.linhas.append(" ".join(data.split()))


def pagina(url, manchete):
    return extrair(baixar(url), url, manchete)


def extrair(html, url, manchete):
    p = Texto(url)
    p.feed(html)
    # Guarda só linhas com data e manchetes (links cujo endereço casa com o padrão de notícia): o resto é menu e rodapé
    uteis = [l for l in p.linhas if DATA.search(l) or (l.startswith("[") and re.search(manchete, l.rsplit("](", 1)[-1]))]
    return "\n".join(dict.fromkeys(uteis))


def paginas(agora):
    mes = [(agora.year, agora.month)]
    if agora.day <= 3:
        anterior = agora.replace(day=1) - timedelta(days=1)
        mes.append((anterior.year, anterior.month))
    # nome: (endereço da lista, padrão do endereço de uma notícia)
    lista = {f"receita-{a}-{m:02d}": (f"https://www.gov.br/receitafederal/pt-br/assuntos/noticias/{a}/{MESES[m - 1]}",
                                       rf"/noticias/{a}/{MESES[m - 1]}/.") for a, m in mes}
    lista.update({
        "fazenda": ("https://www.gov.br/fazenda/pt-br/assuntos/noticias", r"/noticias/20\d\d/."),
        "senado": ("https://www12.senado.leg.br/noticias/ultimas", r"/noticias/materias/."),
        "cgibs": ("https://www.cgibs.gov.br/", r"cgibs\.gov\.br/."),
        "fenacon": ("https://fenacon.org.br/reforma-tributaria/", r"fenacon\.org\.br/(reforma-tributaria|noticias)/."),
    })
    return lista


def main(saida):
    agora = datetime.now(SP)
    saida = Path(saida)
    (saida / "paginas").mkdir(parents=True, exist_ok=True)
    status = {"gerado_em": agora.strftime("%Y-%m-%d %H:%M"), "fontes": {}}

    noticias = {}
    for nome, consulta in CONSULTAS.items():
        for dias in JANELAS:
            fonte = f"google:{nome}:{dias}d"
            try:
                itens = google_noticias(consulta, dias)
                status["fontes"][fonte] = f"ok, {len(itens)} notícias"
            except Exception as e:  # uma fonte fora do ar não pode derrubar o radar
                status["fontes"][fonte] = f"erro: {e}"
                continue
            for it in itens:
                chave = it["titulo"].lower()
                if chave not in noticias:
                    noticias[chave] = {**it, "radares": []}
                if nome not in noticias[chave]["radares"]:
                    noticias[chave]["radares"].append(nome)
    lista = sorted(noticias.values(), key=lambda n: n["quando"], reverse=True)
    (saida / "noticias.json").write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")

    for nome, (url, manchete) in paginas(agora).items():
        try:
            texto = pagina(url, manchete)
            (saida / "paginas" / f"{nome}.md").write_text(f"# {nome}\nFonte: {url}\n\n{texto}\n", encoding="utf-8")
            status["fontes"][f"pagina:{nome}"] = f"ok, {texto.count(chr(10)) + 1} linhas"
        except Exception as e:
            status["fontes"][f"pagina:{nome}"] = f"erro: {e}"

    (saida / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False, indent=1))
    if not lista:
        sys.exit("radar vazio: nenhuma fonte do Google Notícias respondeu")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "radar")
