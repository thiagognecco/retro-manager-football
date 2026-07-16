from game import GameEngine
import stats

if __name__ == "__main__":
    engine = GameEngine()
    engine.new_game()

    # simula alguns jogos para popular o histórico
    t1 = engine.player_team
    opponent = [t for t in engine.teams if t != t1][0]

    for _ in range(3):
        engine.simulate_match(t1, opponent)

    # garante que histórico foi persistido
    saved = stats.salvar_carregar_historico(None)
    print(f"Registros salvos: {len(saved)}")

    # mostra agregados
    gols_jog = stats.gols_por_jogador(saved)
    gols_time = stats.gols_por_time(saved)

    print("Gols por jogador (top):")
    for p, g in sorted(gols_jog.items(), key=lambda x: -x[1])[:5]:
        print(f"- {p}: {g}")

    print("Gols por time:")
    for t, g in gols_time.items():
        print(f"- {t}: {g}")
