"""Teste sem internet do radar. Uso: python tools/test_radar.py"""
from radar import extrair, ler_rss

HTML = """<html><head><title>x</title><script>var a = "29/10/2026";</script></head><body>
<nav><a href="/servicos/consultar-dividas-e-pendencias">Consultar dívidas e pendências do contribuinte</a></nav>
<span>29/10/2026 16h09</span>
<a href="/receitafederal/pt-br/assuntos/noticias/2026/outubro/cooperativas-30-novembro">Receita e CGIBS discutem ampliar prazo das cooperativas</a>
<a href="#topo">Voltar ao topo da página de notícias</a>
</body></html>"""

texto = extrair(HTML, "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/outubro", r"/noticias/2026/outubro/.")
assert "29/10/2026 16h09" in texto, texto
assert ("[Receita e CGIBS discutem ampliar prazo das cooperativas]"
        "(https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/outubro/cooperativas-30-novembro)") in texto, texto
assert "Consultar dívidas" not in texto, "menu não deveria entrar"
assert "topo" not in texto, "âncora interna não deveria entrar"
assert texto.count("29/10/2026") == 1, "data dentro de <script> não deveria entrar"

RSS = """<rss><channel><item><title>TCU calcula CBS em 11,3% - Agência Brasil</title>
<link>https://news.google.com/rss/articles/abc</link><pubDate>Wed, 28 Oct 2026 21:30:00 GMT</pubDate>
<source url="https://agenciabrasil.ebc.com.br">Agência Brasil</source></item></channel></rss>"""

[n] = ler_rss(RSS)
assert n["titulo"] == "TCU calcula CBS em 11,3%", n
assert n["veiculo"] == "Agência Brasil" and n["site"] == "https://agenciabrasil.ebc.com.br", n
assert n["quando"] == "2026-10-28 18:30", n  # convertido para o horário de São Paulo
print("OK: radar")
