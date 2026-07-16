from game import GameEngine

if __name__ == "__main__":
    engine = GameEngine()
    engine.new_game()

    # inicia temporada
    engine.start_season()

    total = len(engine.schedule)
    print(f"Total de rodadas: {total}")

    while engine.current_round_index < total:
        engine.advance_round(mode='fast')

    # mostra classificação final
    final_table = engine.season_manager.get_sorted_standings(engine.standings)
    print('\nClassificação final:')
    for pos, row in enumerate(final_table, start=1):
        print(f"{pos}. {row['team']} — Pts: {row['points']} | PJ: {row.get('played', 0)} | V: {row['wins']} | E: {row['draws']} | D: {row['losses']} | GF: {row['gf']} | GA: {row['ga']} | GD: {row['gd']}")
    
    # confirma arquivo salvo
    try:
        with open('season.json', 'r', encoding='utf-8') as f:
            print('\nArquivo season.json gerado com sucesso.')
    except Exception:
        print('\nFalha ao localizar season.json')
