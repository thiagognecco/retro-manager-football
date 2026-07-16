import json
import os
from typing import Dict, Any

TRAINING_FILE = 'training.json'


def salvar_carregar_treinos(entry: Dict[str, Any] = None, filepath: str = TRAINING_FILE):
    """Se entry for None -> carrega a lista de treinos; se entry fornecido -> anexa ao arquivo.
    Retorna a lista atualizada.
    """
    # carregar
    if entry is None:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception:
            return []

    # salvar (anexar)
    try:
        dirname = os.path.dirname(os.path.abspath(filepath))
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        existing = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []
        existing.append(entry)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)
    except Exception:
        # não propaga
        pass
    return entry


# API de conveniência para uso em scripts/tests
def run_training(player, team_name: str, training_type: str = 'fis', intensity: int = 1, cost: int = 1000, rng=None):
    """Executa lógica simples de treino para ser usada independentemente do GameEngine.
    Retorna um registro similar ao usado por GameEngine.run_training_session.
    rng: objeto com métodos randint(a,b) e random() para determinismo em testes (opcional).
    """
    if rng is None:
        import random
        rng = random

    before = getattr(player, training_type, None)
    if before is None:
        raise ValueError('Atributo inválido para treino')

    incr = rng.randint(0, max(0, int(intensity)))
    if getattr(player, 'star', False):
        if rng.random() < 0.5:
            incr += 1

    after = min(5, before + incr)
    setattr(player, training_type, after)

    record = {
        'player': player.name,
        'team': team_name,
        'type': training_type,
        'before': before,
        'after': after,
        'delta': after - before,
        'cost': cost
    }
    salvar_carregar_treinos(record, filepath=filepath if (filepath := TRAINING_FILE) else TRAINING_FILE)
    return record
