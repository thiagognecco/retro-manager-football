# Retro Manager Football

Esse repositório contém o projeto Retro Manager Football (Python + Pygame).

Sumário rápido (fluxo):
1. Leia a documentação (PROJECT.md / README.md)
2. Inicie o jogo (executar `run_game.bat` no Windows ou `python main.py`)
3. No menu do jogo: Novo Jogo / Carregar Jogo
4. Salve o progresso usando o botão "Salvar Jogo" (cria `savegame.json` na raiz do projeto)
5. Para atualizar o projeto: editar arquivos, rodar `git add`/`git commit` conforme protocolo em SESSIONS.md
6. Para ver resultados rápidos: use o console (o jogo imprime mensagens de salvamento/carregamento) e a tela do jogo

Requisitos:
- Python 3.8+
- pygame (instalar com `pip install pygame`)

Arquivos importantes e caminhos:
- main.py — gerenciador de telas e ponto de entrada
- game.py — lógica principal do jogo
- database.py — classes Player/Team, gerador de times e funções de salvar/carregar (`savegame.json`)
- ui.py / screens/ — UI e telas
- PROJECT.md — documentação do projeto (visão, regras, atributos)
- SESSIONS.md — protocolo para registros de sessões e commits (criado por mim)
- run_game.bat — script para iniciar o jogo no Windows

Como executar (Windows):
1. Abra um terminal na pasta do projeto (ex: `c:\Users\<usuario>\Documents\Footbal manager`)
2. (Opcional) Crie um venv: `python -m venv .venv` e ative-o
3. Instale dependências: `pip install pygame`
4. Execute: `run_game.bat` ou `python main.py`

Protocolo de commits e sessões (resumido):
- Antes de começar uma sessão: criar uma nova seção em SESSIONS.md com data, objetivo e tarefas.
- Ao finalizar uma etapa: salvar no repositório com mensagem clara e referência à sessão.
- Mensagem de commit sugerida: `[sessão YYYY-MM-DD] descrição curta — arquivos: X, Y` (inclua Co-authored-by: Copilot na primeira integração feita por este assistente, se desejar).

Se quiser que eu rode os commits agora (inicializar git e criar commit inicial), confirme que posso prosseguir.

---

(Conteúdo gerado automaticamente pelo assistente. Se quiser alterações na linguagem ou formatação, me diga.)

---

Novos módulos adicionados (branches agent/*):
- ai.py — IA visual básica para jogadores (branch: agent/ai-visual-20260716-0301)
- season.py — SeasonManager e geração de calendário (branch: agent/season-refine-20260716-0301)
- market.py — Mercado de transferências e persistência (branch: agent/market-expand-20260716-0301)
- stats.py — Persistência de histórico de partidas e agregações (branch: agent/core-stats-20260716-0301)

Como rodar a suíte de verificação (headless):
- python test_headless.py
- python test_market.py
- python test_season.py
- python test_stats.py

Todos os testes atuais passaram em ambiente de desenvolvimento local ao executar os agentes automáticos.

Branches locais geradas (exemplos):
- agent/ai-visual-20260716-0301
- agent/season-refine-20260716-0301
- agent/market-expand-20260716-0301
- agent/core-stats-20260716-0301
- agent/ui-polish-20260716-0301

Próximos passos sugeridos:
- Revisar os branches e criar pull requests quando estiver pronto para mesclar.
- Testar visualmente executando `run_game.bat` e entrando em "Jogar Partida" para o modo visual.
- Se desejar, autorizo mescla automática de branches após revisão dos testes (não feita por padrão).
