# Protocolo — custo de coordenação da equipe do Exercício 6
Versão 1, registrada antes da coleta. Estudo piloto, sem dados coletados.

## Pergunta e hipóteses
No artefato do Exercício 6, a coordenação hierárquica demanda mais chamadas ao modelo que a sequencial para produzir propostas sobre os mesmos casos?
H0: a média das diferenças pareadas (hierárquica menos sequencial) no número de chamadas tentadas é menor ou igual a zero.
H1: essa média é maior que zero. Desfecho primário: chamadas tentadas por execução, incluindo gerente e tentativas que falharam. Não é uma hipótese sobre produtividade humana ou correção do código.

## Tratamento, controles e amostra
Tratamento: processo hierárquico; controle: sequencial. Ambos usam o código do Exercício 6 copiado em artefato/, três especialistas, mesmos prompts, entradas, modelo, temperatura 0, seed 42, máximo de 40 chamadas e 2.500 tokens de saída por chamada, timeout de 60 s por chamada e sem retries de transporte. O gerente e suas chamadas integram o tratamento. Sem cache ou memória entre execuções. Cada execução recebe uma instância nova.
Amostra intencional de três tarefas sintéticas pequenas: validação de pagamento, média de notas e divisão por zero. Foram escolhidas para permitir inspeção simples e não conter dados pessoais. São criadas neste trabalho e não representam o colheita-mini nem tarefas reais. Cada um dos três casos passa pelas duas condições cinco vezes: 30 execuções. Repetições não são 30 casos independentes.
Desenho: experimento computacional pareado por caso e repetição, ordem embaralhada com random.Random(20261112). Mesma seed de inferência nas repetições, mas isso não garante determinismo do serviço. Não há participantes humanos.

## Medidas e coleta
Cada linha JSONL contém identificação, caso, condição, repetição e rastro original integral. Os rastros contêm entrada hash, configuração, eventos, mensagens, saídas e chamadas. O coletor escreve sem edição manual. Desfechos secundários: tempo total do harness, chamadas concluídas e proporção de status aguardando_humano. Esse status indica conclusão do fluxo e não resolução correta. Erros do modelo contam como execução; credencial ausente impede iniciar a coleta. Sem exclusão por desempenho. Uma falha do processo de coleta exige preservar arquivos e registrar o desvio antes de outra coleta. Sem timeout externo que elimine seletivamente rastros.

## Plano de análise anterior aos dados
Calcular diferenças hierárquica menos sequencial em cada par. Agregar as cinco diferenças de cada caso e depois obter a média entre os três casos, com pesos iguais. Calcular IC percentil exploratório de 95% por bootstrap de casos (10.000 reamostragens, seed 20261112); não reamostrar execuções como se fossem casos independentes. Reportar também os valores por caso. Com apenas três casos, o intervalo é instável e não fundamenta generalização. Não usar teste de significância confirmatório. H1 recebe somente apoio exploratório se a estimativa e o limite inferior forem positivos; caso contrário declarar inconclusivo. Mostrar falhas e tempo por condição. Não excluir falhas. Não substituir modelo durante a coleta. Modelo retornado, ambiente e versões devem ficar registrados. Scripts de análise leem somente dados/brutos/.

## Ameaças e decisões
Interna: variar somente coordenação; ordem aleatória reduz efeito de carga do provedor, sem eliminá-lo. Registrar versões e congelar prompts. Construção: chamadas não medem qualidade; status técnico não equivale a correção. Externa: três casos artificiais e pequenos, nenhuma conclusão sobre produção. Conclusão: repetições dependentes e amostra pequena; agregar por caso, mostrar incerteza e evitar causalidade fora deste ambiente. Reprodutibilidade: seed não fixa backend remoto; registrar modelo retornado e dependências. Segurança: não aplicar patches nem executar código gerado automaticamente; nenhuma chamada faz merge. Revisar rastros antes da publicação para prevenir vazamento de dados; publicar somente entradas sintéticas e nunca .env. Qualquer remoção necessária deve ser declarada, preservando o dado original localmente.

## Desvios
Nenhum até a preparação. Coleta ainda não iniciada por ausência de credenciais e modelo configurado.
