# Retro Manager Football

Esse repositório contém o projeto Retro Manager Football (Python + Pygame).

Sumário rápido (fluxo):
1. Leia a documentação (PROJECT.md / README.md)
2. Inicie o jogo (executar `run_game.bat` no Windows ou `python main.py`)
3. No menu do jogo: Novo Jogo / Carregar Jogo
4. Salve o progresso usando o botão "Salvar Jogo" (cria `savegame.json` na raiz do projeto)
5. Para atualizar o projeto: editar arquivos, rodar `git add`/`git commit` conforme protocolo em SESSIONS.md
6. Para ver resultados rápidos: use o console (o jogo imprime mensagens de salvamento/carregamento) e a tela do jogo

Requisitos e dependências:
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
4. Executar o jogo: `run_game.bat` ou `python main.py`

Testes e verificação headless:
- Para validar alterações sem abrir a UI, rode:
  `python test_headless.py`
- O script cria um jogo, simula uma partida, salva e carrega o save. Verifique as mensagens impressas no console.

Nota: As mudanças recentes alteram apenas apresentação (cores, ajuste de texto). A lógica do jogo não foi modificada.
Protocolo de commits e sessões (resumido):
- Antes de começar uma sessão: criar uma nova seção em SESSIONS.md com data, objetivo e tarefas.
- Ao finalizar uma etapa: salvar no repositório com mensagem clara e referência à sessão.
- Mensagem de commit sugerida: `[sessão YYYY-MM-DD] descrição curta — arquivos: X, Y` (inclua Co-authored-by: Copilot na primeira integração feita por este assistente, se desejar).

Se quiser que eu rode os commits agora (inicializar git e criar commit inicial), confirme que posso prosseguir.

---

(Conteúdo gerado automaticamente pelo assistente. Se quiser alterações na linguagem ou formatação, me diga.)