import json
from typing import List, Tuple, Dict
import events


class SeasonManager:
    """Gera calendário double round-robin e auxilia na execução de rodadas.

    schedule: lista de rodadas, cada rodada é lista de jogos (home_team, away_team)
    """

    def __init__(self, teams: List[object]):
        self.teams = teams[:]
        self.schedule: List[List[Tuple[object, object]]] = []

    def generate_schedule(self, teams: List[object]) -> List[List[Tuple[object, object]]]:
        """Gera calendário double round-robin (turno + returno).

        Retorna uma lista de rodadas; cada rodada é uma lista de tuplas (home, away).
        """
        t = teams[:]
        n = len(t)
        if n % 2 != 0:
            # adiciona um bye (None) se necessário
            t.append(None)
            n += 1

        first_half: List[List[Tuple[object, object]]] = []
        teams_list = t[:]
        for rnd in range(n - 1):
            pairs: List[Tuple[object, object]] = []
            for i in range(n // 2):
                home = teams_list[i]
                away = teams_list[n - 1 - i]
                if home is None or away is None:
                    continue
                pairs.append((home, away))
            first_half.append(pairs)
            # rotaciona mantendo o primeiro elemento fixo
            teams_list = [teams_list[0]] + [teams_list[-1]] + teams_list[1:-1]

        # returno (inverte mando de campo)
        second_half = [[(away, home) for (home, away) in rnd] for rnd in first_half]

        self.schedule = first_half + second_half
        return self.schedule

    def init_standings(self) -> Dict[str, Dict]:
        """Cria representação inicial da tabela (dicionário keyed por nome do time)."""
        table = {}
        for team in self.teams:
            name = team.name if hasattr(team, 'name') else str(team)
            table[name] = {
                "team": name,
                "points": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "gf": 0,
                "ga": 0,
                "gd": 0,
            }
        return table

    def play_round(self, round_matches: List[Tuple[object, object]], engine, mode: str = 'fast') -> List[Dict]:
        """Executa uma rodada usando o GameEngine fornecido.

        Retorna lista de records de partidas no formato {'team1','team2','score1','score2','winner'}.
        """
        results = []
        for home, away in round_matches:
            if mode == 'fast':
                # usa engine.simulate_match que já registra engine.match_history
                _ = engine.simulate_match(home, away)
            else:
                # para "visual" por enquanto usamos a mesma simulação e imprimimos
                print(f"Jogando (visual): {home.name} x {away.name}")
                _ = engine.simulate_match(home, away)

            # último registro do histórico deve ser desta partida
            if engine.match_history:
                record = engine.match_history[-1]
                results.append(record)
                # hook de eventos para cada partida executada na rodada
                try:
                    events.record_match_events(engine, record)
                except Exception:
                    pass
        return results

    @staticmethod
    def apply_match_to_standings(match_record: Dict, standings: Dict[str, Dict]):
        """Aplica resultado de partida à tabela passada por referência."""
        t1 = match_record.get('team1')
        t2 = match_record.get('team2')
        s1 = int(match_record.get('score1', 0))
        s2 = int(match_record.get('score2', 0))

        if t1 not in standings or t2 not in standings:
            # nomes inesperados
            return

        standings[t1]['gf'] += s1
        standings[t1]['ga'] += s2
        standings[t2]['gf'] += s2
        standings[t2]['ga'] += s1

        # vitórias/empates/derrotas e pontos
        if s1 > s2:
            standings[t1]['points'] += 3
            standings[t1]['wins'] += 1
            standings[t2]['losses'] += 1
        elif s2 > s1:
            standings[t2]['points'] += 3
            standings[t2]['wins'] += 1
            standings[t1]['losses'] += 1
        else:
            standings[t1]['points'] += 1
            standings[t2]['points'] += 1
            standings[t1]['draws'] += 1
            standings[t2]['draws'] += 1

        standings[t1]['gd'] = standings[t1]['gf'] - standings[t1]['ga']
        standings[t2]['gd'] = standings[t2]['gf'] - standings[t2]['ga']

    @staticmethod
    def get_sorted_standings(standings: Dict[str, Dict]) -> List[Dict]:
        """Retorna lista ordenada por pontos, vitórias, saldo de gols, gols pró."""
        table = list(standings.values())
        table.sort(key=lambda s: (-s['points'], -s['wins'], -s['gd'], -s['gf'], s['team']))
        return table

    @staticmethod
    def save_standings(sorted_standings: List[Dict], filepath: str = 'season.json'):
        """Salva a classificação final em JSON."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sorted_standings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar tabela em {filepath}: {e}")
