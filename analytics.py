import json
from typing import List, Dict, Any

import stats


def top_scorers(history: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    """Retorna lista de top scorers ordenada desc por gols: [{'player': name, 'goals': n}, ...]"""
    counts = stats.gols_por_jogador(history)
    sorted_items = sorted(counts.items(), key=lambda x: -x[1])
    return [{'player': name, 'goals': goals} for name, goals in sorted_items[:top_n]]


def team_performance_over_time(history: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Calcula o desempenho acumulado de cada time ao longo do histórico.

    Retorna um dicionário {team_name: [snapshot1, snapshot2, ...]} onde cada snapshot contém:
      match_index, played, wins, draws, losses, goals_for, goals_against, points
    A ordem dos snapshots é a ordem cronológica (ordem de entrada no histórico).
    """
    teams: Dict[str, Dict[str, Any]] = {}
    timeline: Dict[str, List[Dict[str, Any]]] = {}

    def ensure_team(team_name: str):
        if team_name not in teams:
            teams[team_name] = {
                'played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'points': 0,
            }
            timeline[team_name] = []

    for idx, match in enumerate(history):
        t1 = match.get('team1')
        t2 = match.get('team2')
        s1 = match.get('score1', 0) or 0
        s2 = match.get('score2', 0) or 0

        if not t1 or not t2:
            # ignora partidas mal formadas
            continue

        ensure_team(t1)
        ensure_team(t2)

        # atualizar contadores
        teams[t1]['played'] += 1
        teams[t2]['played'] += 1
        teams[t1]['goals_for'] += s1
        teams[t1]['goals_against'] += s2
        teams[t2]['goals_for'] += s2
        teams[t2]['goals_against'] += s1

        if s1 > s2:
            teams[t1]['wins'] += 1
            teams[t1]['points'] += 3
            teams[t2]['losses'] += 1
        elif s2 > s1:
            teams[t2]['wins'] += 1
            teams[t2]['points'] += 3
            teams[t1]['losses'] += 1
        else:
            teams[t1]['draws'] += 1
            teams[t2]['draws'] += 1
            teams[t1]['points'] += 1
            teams[t2]['points'] += 1

        # snapshot após essa partida
        for team in (t1, t2):
            snapshot = {'match_index': idx}
            snapshot.update(teams[team])
            timeline[team].append(snapshot.copy())

    return timeline


def export_csv(data: List[Dict[str, Any]], filepath: str) -> str:
    """Exporta uma lista de dicionários para CSV. Cabeçalhos são as chaves unidas de todos os registros.
    Retorna o caminho do arquivo escrito."""
    import csv

    if not isinstance(data, list):
        data = []

    # Determina cabeçalhos
    headers = []
    for item in data:
        if isinstance(item, dict):
            for k in item.keys():
                if k not in headers:
                    headers.append(k)

    try:
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in data:
                # converte apenas valores simples
                row = {}
                for h in headers:
                    v = item.get(h) if isinstance(item, dict) else ''
                    # serializa listas/dicts como JSON strings
                    if isinstance(v, (list, dict)):
                        v = json.dumps(v, ensure_ascii=False)
                    row[h] = v
                writer.writerow(row)
    except Exception:
        pass
    return filepath