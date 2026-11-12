import argparse
import json
import yaml
from crewai import Agent, BaseLLM, Crew, Process, Task
from comum import ROOT, Model, Trace, read_input

class InstrumentedLLM(BaseLLM):
    def __init__(self, adapter):
        super().__init__(model=adapter.trace.data['modelo'] or 'nao-configurado', temperature=0)
        self.adapter = adapter
    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None):
        return self.adapter.call(messages)
    def supports_function_calling(self):
        return False  # CrewAI uses its textual ReAct delegation tools.
    def get_context_window_size(self):
        return 16000  # Conservative budget, not a claim about the provider.

def build(entrada, adapter, process):
    configs = yaml.safe_load((ROOT/'crew/config/agents.yaml').read_text())
    tasks_config = yaml.safe_load((ROOT/'crew/config/tasks.yaml').read_text())
    llm = InstrumentedLLM(adapter)
    agents = {key: Agent(**cfg, llm=llm, allow_delegation=False, max_iter=8,
                         max_retry_limit=0, verbose=False) for key, cfg in configs.items()}
    tasks = []
    for key, cfg in tasks_config.items():
        args = dict(description=cfg['description'].replace('{entrada}', entrada),
                    expected_output=cfg['expected_output'], context=list(tasks))
        if process == 'sequencial':
            args['agent'] = agents[key]
        tasks.append(Task(**args))
    kwargs = {}
    if process == 'hierarquica':
        kwargs['manager_agent'] = Agent(
            role='Coordenador da equipe noturna',
            goal='Delegar análise ao analista, proposta ao engenheiro e conferência ao revisor, nessa ordem; nunca fazer merge.',
            backstory='Coordena os três especialistas e pede evidência; deixa integração para Marina.',
            llm=llm, allow_delegation=True, max_iter=12, max_retry_limit=0)
    def completed(output):
        adapter.trace.event('tarefa', agente=output.agent, saida=output.raw)
    return Crew(agents=list(agents.values()), tasks=tasks,
                process=Process.sequential if process=='sequencial' else Process.hierarchical,
                task_callback=completed, memory=False, cache=False, tracing=False,
                verbose=False, **kwargs)

def run(process, path, directory=None):
    entrada = read_input(path)
    trace = Trace('crew_'+process, entrada, directory)
    adapter = Model(trace)
    try:
        # Preflight avoids repeatedly attempting retries on missing credentials.
        import os
        if not os.getenv('OPENAI_API_KEY') or not os.getenv('MODEL'):
            adapter.call([])
        result = build(entrada, adapter, process).kickoff()
        output = dict(final=result.raw,
                      tarefas=[dict(agente=o.agent, saida=o.raw) for o in result.tasks_output],
                      portao='Aguardando revisão humana; nenhuma alteração aplicada')
        trace.save('aguardando_humano', output)
    except Exception as exc:
        trace.fail('ExecucaoInterrompida:' + type(exc).__name__)
        trace.save('bloqueado')
    return trace

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('processo', choices=['sequencial','hierarquica'])
    parser.add_argument('--entrada', required=True)
    a = parser.parse_args()
    trace = run(a.processo, a.entrada)
    print(trace.path)
    raise SystemExit(0 if trace.data['status']=='aguardando_humano' else 1)
