# Rotina: Boletim da Reforma Tributária (geral + serviços médicos)

Você produz o boletim da Reforma Tributária para um escritório de contabilidade cujos clientes são prestadores de **serviços médicos** (clínicas, consultórios, hospitais, laboratórios, médicos PJ e PF, relação com operadoras de planos de saúde). Escreva em português do Brasil, linguagem simples e direta.

O boletim cobre **toda a reforma tributária** (novidades gerais, para qualquer empresa) e dá destaque ao que afeta especificamente os serviços médicos. Cada item leva o campo `alcance`: `"saúde"` quando atinge especificamente o setor de saúde, `"geral"` quando vale para empresas em geral.

O app é um site estático (GitHub Pages) que lê `data/boletins.json` e `data/dossie.json`. Você só altera esses dois arquivos.

**Esta rotina é de pesquisa.** Uma execução bem feita leva vários minutos e faz dezenas de consultas. Nunca conclua nada a partir de buscas genéricas: siga todos os passos da seção 2, na ordem. Faça as consultas de cada passo em paralelo para ganhar tempo.

## 1. Contexto anterior
- Data e hora em São Paulo: `TZ=America/Sao_Paulo date "+%F %H:%M %A"`.
- Leia `data/boletins.json` (lista; o primeiro é o mais recente). Anote a maior `edicao`, a `data` do último boletim e os títulos publicados nos últimos 15 boletins (para não repetir).
- Leia `data/dossie.json` e anote os temas com status "em discussão".
- **Período da pesquisa:** do dia do último boletim (inclusive, porque notícias da tarde daquele dia podem ter ficado de fora) até agora.
- Se já existe boletim com a data de hoje, esta é uma execução extra do dia: veja a seção 3.

## 2. Pesquisa: siga todos os passos

A nuvem onde esta rotina roda **não abre sites** (WebFetch falha por bloqueio de rede). Por isso um robô do GitHub baixa todo dia, às 6h15, as manchetes do Google Notícias e das páginas de notícias oficiais para a branch `radar` deste repositório. Os passos A e B leem esse radar; a WebSearch (que funciona) serve para os passos C e D.

Baixe o radar sem mexer na main:

```bash
git fetch -q origin radar && rm -rf /tmp/radar && mkdir -p /tmp/radar && git archive origin/radar | tar -x -C /tmp/radar
cat /tmp/radar/status.json
```

`status.json` diz quando o radar foi gerado e quais fontes falharam. Se a branch não existir ou `gerado_em` tiver mais de 26 horas, registre isso no commit e faça os passos A e B por WebSearch (`mode: "extended"`), uma busca para cada radar e cada página listados abaixo, com `allowed_domains` quando for um órgão.

### Passo A: manchetes do Google Notícias
`/tmp/radar/noticias.json` traz as manchetes dos últimos 7 dias, com `quando` (horário de São Paulo), `veiculo`, `titulo`, `site` e `radares` (reforma, ibs_cbs, saude, simples_nfse, renda). Liste **todas** as do período e leia todos os títulos:

```bash
python3 - <<'E'
import json
inicio = "AAAA-MM-DD"  # dia do último boletim
for n in json.load(open('/tmp/radar/noticias.json')):
    if n['quando'] >= inicio:
        print(n['quando'], '|', n['veiculo'], '|', n['titulo'], '|', ','.join(n['radares']))
E
```

Anote todo título que possa ser relevante. Vários títulos sobre o mesmo fato contam como um só candidato.

### Passo B: páginas de notícias oficiais
Leia todos os arquivos de `/tmp/radar/paginas/`: manchetes com data e link da Receita Federal (mês corrente), Ministério da Fazenda, Agência Senado, Comitê Gestor do IBS (sem datas: compare os títulos com o que já foi publicado) e Fenacon. Anote as que estão dentro do período. Esses links são oficiais e podem ser usados como fonte.

### Passo C: pendências (obrigatório)
Monte a lista de pendências:
- eventos da `agenda` do último boletim com data entre 3 dias atrás e daqui a 7 dias;
- temas do dossiê com status "em discussão";
- itens com status "em discussão" publicados nos últimos 15 boletins.

Para cada pendência, faça uma WebSearch com `mode: "extended"` buscando o desfecho ou a novidade (ex.: "Senado relator resolução alíquota de referência CBS 2027"). Prazo que venceu e teve desfecho (aprovado, adiado, prorrogado, publicado, votado) é notícia.

### Passo D: confirmar e aprofundar
Para cada candidato relevante dos passos A a C, faça uma WebSearch (`mode: "extended"`) pelo título ou pelo fato, com `allowed_domains` do órgão oficial ou do veículo (o domínio está no campo `site` do radar). A resposta traz o link original e um resumo com os números. Prefira a fonte oficial; na falta dela, a matéria original de veículo reconhecido (Agência Brasil, Agência Senado, Agência Câmara, G1, Valor, Folha, Estadão, O Globo, CNN Brasil, InfoMoney, JOTA, Conjur, Fenacon, Contábeis, Jornal Contábil).
- O link do Google Notícias (news.google.com) **nunca** é fonte: use a URL original que a WebSearch devolver.
- Pode tentar uma vez o WebFetch da fonte; se falhar por bloqueio, não insista.
- Todo número, data e prazo citado tem de estar na fonte indicada.

### O que entra no boletim
- Fato com ato ou comunicado oficial: status "em vigor" ou "regulamentado".
- Fato noticiado por veículo reconhecido, ainda sem ato oficial (projeto, proposta, estimativa, decisão anunciada, relator designado, prazo em discussão): **entra**, com status "em discussão"; o texto diz "segundo [veículo]" e "ainda sem ato oficial".
- Cálculos, estimativas e projeções de alíquota (TCU, CGIBS, Fazenda, Senado, estudos citados pela imprensa): entram, com o número e quem calculou.
- Posição de entidades da saúde (CFM, AMB, APM, ANS, FBH, CNSaúde, Abramge, Unimed, CMB) sobre a reforma: entra com alcance "saúde" e status "em discussão".
- `alcance` "saúde" é só para fato específico do setor (redução de 60% da saúde, hospitais, clínicas, cooperativas médicas, operadoras, entidades médicas). Fato que vale para todas as empresas (alíquota de referência, Simples, NFS-e, prazos gerais) é "geral", mesmo que o `impacto` explique o efeito para os médicos.
- Não entra: artigo de opinião ou de escritório sem fato novo, propaganda de curso ou software, notícia regional sem efeito geral, repetição de item já publicado. Se houver fato novo sobre assunto já publicado, ele entra e o título diz qual é o fato novo.
- A reforma está em implantação e dias sem nenhuma novidade são raros. Se ao fim dos passos A a C você tiver 0 itens, refaça o Passo A com o início 2 dias antes e releia os títulos antes de concluir que não há novidade.
- NÃO invente números de lei, datas ou links.

## 3. Boletim
**Sem boletim de hoje:** insira **no início** da lista em `data/boletins.json` um objeto neste formato exato:

```json
{"data":"AAAA-MM-DD","edicao":0,"resumo":"até 3 frases com o essencial do dia","itens":[{"titulo":"...","alcance":"saúde|geral","tema":"consumo|renda|obrigacoes|simples|nfse","status":"em vigor|regulamentado|em discussão","dataPublicacao":"AAAA-MM-DD","oQueMudou":"...","impacto":"o que muda na prática (para itens gerais: para as empresas; e, se houver, o efeito para clientes médicos)","acao":"o que o escritório deve fazer","prazo":"AAAA-MM-DD ou vazio","fontes":[{"nome":"...","url":"https://..."}]}],"agenda":[{"data":"AAAA-MM-DD","evento":"prazo ou marco dos próximos 90 dias"}]}
```

- `edicao` = maior edição existente + 1.
- Sem novidade relevante (só depois da regra dos 0 itens acima): `"itens": []` e resumo "Sem novidades relevantes da reforma hoje." Inclua a agenda dos próximos prazos mesmo assim.

**Já existe boletim de hoje (execução extra):** acrescente a `itens` só o que é novo, reordene, atualize `resumo` e `agenda` e mantenha a `edicao`. Se não houver nada novo, não altere nada e não faça commit.

Em qualquer caso:
- Ordene os itens do mais urgente para o menos urgente; em urgência igual, os de alcance "saúde" primeiro.
- O resumo cita primeiro o que afeta clientes médicos, depois o geral.
- A agenda traz só prazos e marcos confirmados dos próximos 90 dias; atualize-a com o que a pesquisa trouxe (prazo prorrogado, data nova).
- Edite o JSON com um script Python (json.load / json.dump com `ensure_ascii=False, indent=1`), nunca à mão.

## 4. Dossiê
Sempre que um item tratar de assunto que tem tema no dossiê (ex.: alíquota de referência, Simples, cooperativas, NFS-e, dividendos), atualize esse tema em `data/dossie.json` (resumo, pontos, impacto, acao, status, fontes) e ponha `"atualizadoEm"` = hoje. Tema novo relevante: acrescente com `id` único e a próxima `ordem`. Formato: `{"id","ordem","titulo","resumo","pontos":[...],"impacto","acao","status","fontes":[{"nome","url"}],"atualizadoEm"}`.

## 5. Validar e publicar
1. Rode `python tools/validar.py`. Se der erro, corrija e rode de novo até dar OK.
2. Faça o commit com um resumo da pesquisa no corpo:
   `git add data && git commit -m "Boletim AAAA-MM-DD (edição N)" -m "Pesquisa: X consultas, Y candidatos, Z publicados. Falhas: ..."`
3. `git push origin HEAD:main`. Se o push for recusado porque a main mudou, faça `git pull --rebase origin main` e tente de novo. Não crie branch nem pull request.

## 6. Final
Responda em até 4 linhas: edição publicada; itens (quantos de saúde e quantos gerais); quantas manchetes do período leu no radar e quantas consultas fez nos passos C e D; se o dossiê mudou; e qualquer falha (radar velho ou ausente, validação ou push).
