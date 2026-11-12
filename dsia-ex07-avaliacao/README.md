# Exercício 7 — Avaliação empírica
**Preparação pronta; experimento e publicação pendentes. Não enviar esta preparação como trabalho concluído.**
Avalia o custo de coordenação da equipe do Exercício 6 em três casos sintéticos. O material anterior também não continha execuções reais. Não há dados brutos ou resultados de inferência neste pacote.

## Reproduzir
Python 3.12; versões completas em artefato/requirements.lock.txt. Modelo real: nenhum usado até o momento. Seed do modelo 42; ordem e bootstrap 20261112. Cada condição roda cinco vezes em cada caso.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r artefato/requirements.lock.txt
cp .env.example .env
# Preencher localmente; nunca enviar chave pelo chat ou ao GitHub.
# Antes da coleta, confirmar modelo com suporte aos parâmetros do adaptador.
# Se alterar protocolo/modelo/parâmetros, registrar novo commit antes dos dados.
python coletar.py
python analise/analisar.py
```
A primeira etapa deve existir no histórico antes dos dados: `git log --reverse --oneline` permite conferir. O bundle incluído no pacote preserva o commit de preparação e pode ser clonado com `git clone historico.bundle dsia-ex07-avaliacao`. Alternativamente iniciar git e fazer commit de todo o protocolo e código antes de executar coletar.py. O coletor recusa dados existentes e protocolo sem commit. O coletor não publica nada.

Após coleta, interpretar resumo.json em RESULTADOS.md, preencher versão do modelo e atualizar declaração de IA. Fazer commit de dados e resultados somente depois. Revisar segredos. Criar repositório público dsia-ex07-avaliacao na própria conta, branch main, enviar histórico completo e conferir sem autenticação antes de colar a URL na atividade. O envio é único segundo o enunciado.

## Arquivos
PROTOCOLO.md contém plano anterior aos dados; artefato/ contém o código reaproveitado; casos/ contém entradas sintéticas; coletar.py registra rastros sem edição; analise/analisar.py lê apenas dados/brutos. RESULTADOS.md registra a ausência de coleta. USO-DE-IA.md separa objeto e apoio.
