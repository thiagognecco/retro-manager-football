import json
import os
from typing import List, Dict, Any


def salvar_carregar_historico(history: List[Dict[str, Any]] = None, filepath: str = 'match_history.json') -> List[Dict[str, Any]]:
    """Se history for None -> carrega o histórico de filepath (se existir) e retorna a lista.
    Se history for fornecido -> salva no arquivo e retorna a lista salva.

    Retorna sempre a lista de registros (pode ser vazia).
    """
    if history is None:
        # carregar
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return []
        except Exception:
            # em caso de erro, retorna lista vazia para não quebrar callers
            return []

    # salvar
    try:
        # garante diretório
        dirname = os.path.dirname(os.path.abspath(filepath))
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except Exception:
        # não propaga erro para não quebrar jogo — callers podem tratar
        pass
    return history


def gols_por_jogador(history: List[Dict[str, Any]]) -> Dict[str, int]:
    """Retorna dicionário {nome_jogador: gols} calculado a partir do histórico.
    Espera que cada partida tenha key 'events' que contém eventos com 'scorer'.
    """
    counts: Dict[str, int] = {}
    for match in (history or []):
        events = match.get('events', []) if isinstance(match, dict) else []
        for e in events:
            scorer = e.get('scorer')
            if scorer:
                counts[scorer] = counts.get(scorer, 0) + 1
    return counts


def gols_por_time(history: List[Dict[str, Any]]) -> Dict[str, int]:
    """Retorna dicionário {nome_time: gols} calculado a partir do histórico.
    Conta os gols pelos eventos listados em cada partida.
    """
    counts: Dict[str, int] = {}
    for match in (history or []):
        events = match.get('events', []) if isinstance(match, dict) else []
        for e in events:
            team = e.get('team')
            if team:
                counts[team] = counts.get(team, 0) + 1
    return counts
