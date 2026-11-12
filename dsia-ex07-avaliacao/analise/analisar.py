import json, random, statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def analisar(rows):
    keys=[(x['caso'],x['condicao'],x['repeticao']) for x in rows]
    cases=sorted({x['caso'] for x in rows})
    if len(cases)!=3 or len(rows)!=30 or len(set(keys))!=30: raise ValueError('Coleta incompleta ou duplicada')
    for c in cases:
        for p in ['sequencial','hierarquica']:
            if {x['repeticao'] for x in rows if x['caso']==c and x['condicao']==p}!=set(range(1,6)):raise ValueError('Repetições incompletas')
    indexed=dict(zip(keys,rows)); diffs={}
    for c in cases:
        diffs[c]=statistics.mean(indexed[c,'hierarquica',i]['rastro']['chamadas_tentadas']-indexed[c,'sequencial',i]['rastro']['chamadas_tentadas'] for i in range(1,6))
    values=list(diffs.values()); rng=random.Random(20261112)
    boots=sorted(statistics.mean(rng.choices(values,k=3)) for _ in range(10000))
    lo,hi=boots[249],boots[9749]; estimate=statistics.mean(values)
    return {'n_execucoes':len(rows),'n_casos':3,'diferenca_por_caso':diffs,'diferenca_media_chamadas':estimate,'ic95_bootstrap_exploratorio':[lo,hi],'interpretacao':'apoio exploratório a H1' if estimate>0 and lo>0 else 'inconclusivo','por_condicao':{p:{'chamadas_media':statistics.mean(x['rastro']['chamadas_tentadas'] for x in rows if x['condicao']==p),'tempo_medio_s':statistics.mean(x['rastro']['tempo_total_s'] for x in rows if x['condicao']==p),'fluxos_concluidos':sum(x['rastro']['status']=='aguardando_humano' for x in rows if x['condicao']==p),'n':15} for p in ['sequencial','hierarquica']}}
def main():
    source=R/'dados/brutos/execucoes.jsonl'
    if not source.exists():raise SystemExit('Sem dados reais: análise não executada.')
    result=analisar([json.loads(l) for l in source.read_text().splitlines()])
    (R/'analise/resumo.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
