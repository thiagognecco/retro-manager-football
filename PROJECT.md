# 📋 Retro Manager Football - Documentação Oficial

## Visão Geral do Projeto
- **Nome**: Retro Manager Football
- **Estilo**: Football Manager retrô / pixel art simples
- **Tecnologia**: Python 3 + Pygame
- **Objetivo**: Criar um jogo completo, divertido e viciante de gerenciamento de futebol
- **Tom**: Leve, divertido e nostálgico

## Objetivos Principais
1. Mecânicas sólidas e divertidas
2. Progressão clara (subir de divisões)
3. Interface simples e funcional
4. Sistema de salvamento robusto
5. Fácil de expandir

## Estrutura de Pastas Sugerida

Football Manager/
├── main.py                 # Arquivo principal
├── PROJECT.md              # Esta documentação
├── grok_agent.py           # Assistente IA
├── database.py             # Sistema de dados
├── ui.py                   # Interface e telas
├── game.py                 # Lógica principal do jogo
├── screens/                # Pasta com as telas
│   ├── menu.py
│   ├── team_hub.py
│   ├── squad.py
│   └── match.py
├── savegame.json           # Arquivo de save
└── assets/                 # Imagens, sons (futuro)


## Regras para o Grok Agent (Importante!)

**Sempre siga estas regras:**
- Mantenha o código **limpo, comentado e organizado**
- Use Pygame puro (sem libs extras por enquanto)
- Prefira **simplicidade + diversão**
- Entregue código completo quando solicitado
- Mantenha compatibilidade com `database.py` (classes Player e Team)
- Use um **gerenciador de telas** (Screen Manager) para alternar entre menus

## Atributos dos Jogadores
- `fis` → Físico (1-5)
- `tec` → Técnica (1-5)
- `dec` → Decisão (1-5)
- `star` → Estrela (True/False)

## Fluxo Principal do Jogo
1. Menu Principal → Novo Jogo / Carregar
2. Escolha de Time ou Criação
3. Hub do Time (Visão Geral)
4. Gerenciar Elenco
5. Transferências
6. Calendário e Partidas
7. Simulação de Jogos
8. Fim de Temporada / Promoção/Rebaixamento

---

**Próximo passo:**

Depois de criar esse `PROJECT.md`, me fala que eu atualizo o `grok_agent.py` para que ele leia automaticamente essa documentação no início.

Quer adicionar ou mudar alguma coisa nessa documentação antes? (ex: mais detalhes, metas específicas, etc.)
