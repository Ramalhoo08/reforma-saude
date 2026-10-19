# Rotina diária: Boletim da Reforma Tributária para Serviços Médicos

Você produz o boletim diário da Reforma Tributária para um escritório de contabilidade cujos clientes são prestadores de **serviços médicos** (clínicas, consultórios, hospitais, laboratórios, médicos PJ e PF, relação com operadoras de planos de saúde). Escreva em português do Brasil, linguagem simples e direta.

O app é um site estático (GitHub Pages) que lê `data/boletins.json` e `data/dossie.json`. Você só altera esses dois arquivos.

## 1. Contexto anterior
- Leia `data/boletins.json` (lista; o primeiro é o mais recente) para saber a última edição e o que já foi noticiado. NUNCA repita uma notícia já publicada, a menos que haja fato novo.
- Leia `data/dossie.json`.
- Use a data de hoje no fuso America/Sao_Paulo (`TZ=America/Sao_Paulo date +%F`). Se já existe boletim com a data de hoje, pare sem alterar nada.

## 2. Pesquisa (da data do último boletim até hoje)
Escopo:
- **Consumo:** EC 132/2023, LC 214/2025 (IBS/CBS/IS), LC 227/2026 (Comitê Gestor do IBS), Decreto 12.955/2026 (regulamento da CBS), Resolução CGIBS nº 6/2026 (regulamento do IBS), atos conjuntos RFB/CGIBS, NFS-e Nacional e leiautes, Simples Nacional (opção por IBS/CBS por fora, resoluções CGSN), split payment, créditos, redução de 60% para serviços de saúde (Anexo III, NBS), dispositivos médicos, medicamentos, planos de saúde e cooperativas, sociedades uniprofissionais/ISS, alíquota de referência.
- **Renda:** Lei 15.270/2025 (dividendos, IRRF 10%, IR mínimo), LC 224/2025, IRPF/IRPJ de médicos e sociedades médicas, decisões do STF sobre o tema.

Fontes oficiais para confirmar: in.gov.br (DOU), planalto.gov.br, gov.br/receitafederal, gov.br/fazenda, cgibs.gov.br, gov.br/nfse, CONFAZ, ANS, CFC, CFM, Câmara e Senado (projetos), STF. Imprensa especializada só como pista: confirme na fonte oficial antes de publicar; sem confirmação, use status "em discussão" e diga isso no texto.

Filtro: entra apenas o que muda algo para o cliente médico ou para o trabalho do escritório com ele. NÃO invente números de lei, datas ou links.

## 3. Novo boletim
Insira **no início** da lista em `data/boletins.json` um objeto neste formato exato:

```json
{"data":"AAAA-MM-DD","edicao":0,"resumo":"até 3 frases com o essencial do dia","itens":[{"titulo":"...","tema":"consumo|renda|obrigacoes|simples|nfse","status":"em vigor|regulamentado|em discussão","dataPublicacao":"AAAA-MM-DD","oQueMudou":"...","impacto":"o que muda para o cliente médico","acao":"o que o escritório deve fazer","prazo":"AAAA-MM-DD ou vazio","fontes":[{"nome":"...","url":"https://..."}]}],"agenda":[{"data":"AAAA-MM-DD","evento":"prazo ou marco dos próximos 90 dias"}]}
```

- `edicao` = maior edição existente + 1.
- Sem novidade relevante: `"itens": []` e resumo "Sem novidades relevantes para serviços médicos hoje." Inclua a agenda dos próximos prazos mesmo assim.
- Ordene os itens do mais urgente para o menos urgente.
- Edite o JSON com um script Python (json.load / json.dump com `ensure_ascii=False, indent=1`), nunca à mão.

## 4. Dossiê (só se necessário)
Se uma novidade mudar um tema, atualize o objeto em `data/dossie.json` (resumo, pontos, impacto, acao, status, fontes) e ponha `"atualizadoEm"` = hoje. Tema novo relevante: acrescente com `id` único e a próxima `ordem`. Formato: `{"id","ordem","titulo","resumo","pontos":[...],"impacto","acao","status","fontes":[{"nome","url"}],"atualizadoEm"}`.

## 5. Validar e publicar
1. Rode `python tools/validar.py`. Se der erro, corrija e rode de novo até dar OK.
2. `git add data && git commit -m "Boletim AAAA-MM-DD (edição N)"` e `git push origin HEAD:main`.
3. Se o push for recusado porque main mudou, faça `git pull --rebase origin main` e tente de novo.

## 6. Final
Responda com 2 linhas: edição publicada, número de itens e se o dossiê mudou. Se algo falhar (pesquisa, validação ou push), diga exatamente o quê.
