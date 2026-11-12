"""Coleta real; jamais substitui inferência por saídas simuladas."""
import json, os, random, subprocess, sys
from pathlib import Path
R=Path(__file__).resolve().parent

def main():
    from dotenv import load_dotenv
    load_dotenv(R/'.env')
    if not os.getenv('OPENAI_API_KEY') or not os.getenv('MODEL'):
        raise SystemExit('Coleta não iniciada: configure OPENAI_API_KEY e MODEL localmente.')
    if os.getenv('SEED','42')!='42': raise SystemExit('O protocolo fixa SEED=42.')
    subprocess.run(['git','ls-files','--error-unmatch','PROTOCOLO.md'],cwd=R,check=True,stdout=subprocess.DEVNULL)
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=R).strip():
        raise SystemExit('Faça commit da preparação antes da coleta.')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    out=R/'dados/brutos'; out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()): raise SystemExit('Preserve a coleta existente; não sobrescrever.')
    sys.path.insert(0,str(R/'artefato'))
    from crew.main import run
    jobs=[(c.stem,p,i) for c in sorted((R/'casos').glob('*.json')) for p in ['sequencial','hierarquica'] for i in range(1,6)]
    random.Random(20261112).shuffle(jobs)
    env=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)
    (out/'ambiente.json').write_text(json.dumps({'python':sys.version,'pacotes':env.splitlines(),'commit_protocolo':commit,'modelo':os.environ['MODEL'],'seed':42},indent=2))
    with (out/'execucoes.jsonl').open('x') as f:
        for n,(case,cond,rep) in enumerate(jobs,1):
            trace=run(cond,R/'casos'/f'{case}.json',out/'rastros')
            row={'ordem':n,'caso':case,'condicao':cond,'repeticao':rep,'rastro':trace.data,'arquivo_rastro':trace.path.name}
            f.write(json.dumps(row,ensure_ascii=False)+'\n'); f.flush(); os.fsync(f.fileno())
if __name__=='__main__': main()
