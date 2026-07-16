import os
from game import GameEngine
import database
import training


def run_test():
    # Garantir ambiente limpo
    if os.path.exists(training.TRAINING_FILE):
        try:
            os.remove(training.TRAINING_FILE)
        except Exception:
            pass

    engine = GameEngine()
    engine.new_game()

    # escolher um jogador (não goleiro) do elenco do jogador
    player = None
    for p in engine.player_team.players:
        if p.position != 'GL':
            player = p
            break

    assert player is not None, 'Nenhum jogador válido encontrado para treino.'

    before = getattr(player, 'tec')
    # semear RNG para determinismo
    database.random.seed(1)

    res = engine.run_training_session(player, training_type='tec', intensity=2, cost=500)
    assert res.get('ok'), f"Treino falhou: {res}"

    after = getattr(player, 'tec')
    assert after >= before, 'Atributo TEC diminuiu após treino (inválido)'
    assert after <= min(5, before + 2), 'Atributo TEC aumentou além do esperado'

    # verificar que arquivo foi criado
    assert os.path.exists(training.TRAINING_FILE), 'Arquivo de treino não criado'

    # carregar e checar registro
    entries = training.salvar_carregar_treinos(None)
    assert isinstance(entries, list) and len(entries) >= 1, 'Registro de treino não encontrado no arquivo'

    print('[TEST PASSED] test_training: sessão de treino aplicada e persistida corretamente.')


if __name__ == '__main__':
    run_test()
