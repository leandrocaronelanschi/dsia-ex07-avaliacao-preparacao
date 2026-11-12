import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

def read_input(path):
    data = json.loads(Path(path).read_text())
    for key in ('problema', 'arquivos', 'criterios'):
        if key not in data:
            raise ValueError('Entrada sem campo obrigatório: ' + key)
    if not data['arquivos'] or not data['criterios']:
        raise ValueError('Arquivos e critérios devem ser não vazios')
    text = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if len(text.encode()) > 100_000:
        raise ValueError('Entrada excede 100 KB; selecione um recorte explícito')
    return text

def parse_json(text):
    text = text.strip()
    if text.startswith('```'):
        text = '\n'.join(text.splitlines()[1:-1])
    return json.loads(text)

class Trace:
    def __init__(self, version, entrada, directory=None):
        self.directory = Path(directory or ROOT/'rastros')
        self.directory.mkdir(parents=True, exist_ok=True)
        self.started = perf_counter()
        self.data = dict(versao=version, inicio=datetime.now(timezone.utc).isoformat(),
                         entrada_sha256=hashlib.sha256(entrada.encode()).hexdigest(),
                         modelo=os.getenv('MODEL'), seed=int(os.getenv('SEED') or '42'),
                         chamadas_tentadas=0, chamadas_concluidas=0, primeira_falha=None,
                         eventos=[], saida=None, status='iniciado')
        self.path = self.directory / (version + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '.json')
    def event(self, kind, **payload):
        self.data['eventos'].append(dict(tipo=kind, segundos=perf_counter()-self.started, **payload))
    def fail(self, reason):
        if self.data['primeira_falha'] is None:
            self.data['primeira_falha'] = reason
        self.event('falha', motivo=reason)
    def save(self, status, output=None):
        self.data.update(status=status, saida=output, tempo_total_s=perf_counter()-self.started)
        # Only this explicit allowlist is serialized; environment and headers never enter the trace.
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2))
        return self.path

class Model:
    def __init__(self, trace, limit=40):
        self.trace, self.limit = trace, limit
        self.client = None
    def call(self, messages):
        if not os.getenv('OPENAI_API_KEY') or not os.getenv('MODEL'):
            self.trace.fail('ConfiguracaoAusente: definir OPENAI_API_KEY e MODEL localmente')
            raise RuntimeError('Defina OPENAI_API_KEY e MODEL no .env local; não envie a chave pelo chat.')
        if self.trace.data['chamadas_tentadas'] >= self.limit:
            self.trace.fail('OrcamentoExcedido: limite de chamadas atingido')
            raise RuntimeError('Orçamento de chamadas excedido')
        if self.client is None:
            self.client = ChatOpenAI(model=os.environ['MODEL'], temperature=0,
                                     seed=self.trace.data['seed'], max_retries=0,
                                     timeout=60, max_tokens=2500)
        self.trace.data['chamadas_tentadas'] += 1
        t = perf_counter()
        self.trace.event('modelo_inicio', mensagens=messages)
        try:
            response = self.client.invoke(messages)
        except Exception as exc:
            # No raw SDK error: it can contain request URLs or headers.
            self.trace.fail('ErroModelo:' + type(exc).__name__)
            raise RuntimeError('Falha de chamada ao modelo: ' + type(exc).__name__) from None
        text = response.content
        if not isinstance(text, str):
            self.trace.fail('RespostaNaoTextual')
            raise ValueError('Resposta não textual')
        self.trace.data['chamadas_concluidas'] += 1
        self.trace.event('modelo_fim', tempo_s=perf_counter()-t, saida=text,
                         uso=response.usage_metadata,
                         modelo_retornado=response.response_metadata.get('model_name'))
        return text
