from game import GameEngine
import database

if __name__ == "__main__":
    engine = GameEngine()
    engine.new_game()
    print(f"Time do jogador: {engine.player_team.name}")

    opponent = database.random.choice([t for t in engine.teams if t != engine.player_team])
    print(f"Oponente escolhido: {opponent.name}")

    resultado = engine.simulate_match(engine.player_team, opponent)
    print(f"Resultado da simulação: {resultado}")

    # Salvar jogo
    engine.save_game()

    # Carregar e mostrar um resumo
    times_carregados = database.carregar_jogo()
    if times_carregados:
        print('\nResumo dos times carregados:')
        for t in times_carregados:
            print(f"- Time: {t.name} | Goleiro: {t.players[0].name} | Força média do time: {t.get_team_force()}")
    else:
        print('Nenhum save encontrado após salvar (algo deu errado).')
