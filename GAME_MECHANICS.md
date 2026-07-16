📋 Copie e cole o texto abaixo para a sua IA:
Nós estamos desenvolvendo o Retro Manager Football em Python. O jogo é um gerenciador de futebol tático e rápido inspirado em Elifoot (menus e decisões rápidas) com simulação visual em Pygame.

Aqui estão as mecânicas detalhadas do jogo que você deve seguir para criar e expandir as próximas funções:

1. Atributos e Elenco (O Banco de Dados)
Atributos de Jogadores (1 a 5):

FIS (Físico): Define a velocidade de corrida no simulador visual e a taxa de perda de fôlego ao longo do tempo.

TEC (Técnica): Determina a precisão do passe, o controle da bola e a chance de driblar com sucesso.

DEC (Decisão): Atributo de ação final. Para atacantes, define a precisão do chute; para defensores, a precisão do desarme; para goleiros, a capacidade de defesa.

Estrela ⭐ (Booleano): Jogadores marcados como "Estrela" recebem um bônus temporário de +1 em todas as ações de decisão (DEC) em momentos críticos da partida.

Posições: GL (Goleiro), DF (Defensor), MC (Meio-campista), AT (Atacante).

Limites de Elenco: Cada time começa com 11 jogadores titulares (1 GL, 4 DF, 4 MC, 2 AT), mas pode comprar e vender atletas para ter reservas.

2. Economia e Finanças (Estilo Elifoot)
Dinheiro Inicial: Todos os times começam com a mesma quantia (ex: $150.000).

Receita por Partida:

O time mandante do jogo recebe receita de bilheteria baseada na capacidade do seu estádio e na importância do jogo.

Vitórias dão um bônus financeiro de patrocínio; empates dão um bônus menor.

Despesas: Manutenção semanal do elenco (salários baseados na média de força dos jogadores).

Mercado de Transferências: Uma lista de jogadores livres para compra e a possibilidade de colocar jogadores do próprio elenco à venda. O valor do passe de um jogador é calculado por: Valor=(Média de Força)^2 × 10.000.

3. Mecânica do Campeonato (Tabela e Turnos)
Estrutura: 4 times jogam entre si em turno e returno (6 rodadas no total).

Pontuação Clássica: Vitória = 3 pts, Empate = 1 pt, Derrota = 0 pts.

Critérios de Desempate: Pontos > Vitórias > Saldo de Gols > Gols Pró.

4. Motor de Simulação de Partida (2 Modos)
Modo Rápido (Texto): Simulação matemática direta baseada na soma da força do Meio-Campo (MC) e Ataque (AT) de um time contra a Defesa (DF) e Goleiro (GL) do adversário. O time com maior força acumulada ganha "chances de gol". Cada chance é testada contra o goleiro adversário usando números aleatórios ponderados.

Modo Visual (Pygame): Campo verde de 800×600 pixels. Os jogadores são representados por círculos coloridos que se movem de forma autônoma (IA simples de perseguição de bola/posicionamento).

A Bola: Tem física básica de movimento e atrito.

Ações: Quando um círculo encosta na bola, ele toma uma decisão baseada em seus stats (dar um passe para o jogador mais próximo se for MC, ou chutar para o gol se for AT na área).