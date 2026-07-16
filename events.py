import json
import os
import database

EVENTS_FILE = 'events.json'


def load_events():
    if not os.path.exists(EVENTS_FILE):
        return []
    try:
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_events(records):
    try:
        with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def record_match_events(engine, match_record):
    """Processa efeitos de um match: ajustes de moral, possibilidade de lesões e registros.
    - Vencedor ganha moral moderada; perdedor perde moral.
    - Há pequena chance de lesão por time.
    - Atualiza jogadores afetados e persiste em events.json.

    Recebe engine (GameEngine) para acessar times/players.
    """
    events = load_events()

    entry = {
        'team1': match_record.get('team1'),
        'team2': match_record.get('team2'),
        'score1': match_record.get('score1'),
        'score2': match_record.get('score2'),
        'winner': match_record.get('winner'),
        'match_events': [],
    }

    # apply morale changes
    winner = match_record.get('winner')

    def find_team_by_name(name):
        for t in engine.teams:
            if getattr(t, 'name', None) == name:
                return t
        return None

    t1 = find_team_by_name(entry['team1'])
    t2 = find_team_by_name(entry['team2'])

    # small morale adjustments
    try:
        if winner:
            wteam = find_team_by_name(winner)
            lteam = t1 if wteam is not t1 else t2
            if wteam:
                for p in wteam.players:
                    p.morale = min(100, getattr(p, 'morale', 50) + 5)
                entry['match_events'].append({'type': 'morale', 'team': winner, 'delta': 5})
            if lteam:
                for p in lteam.players:
                    p.morale = max(0, getattr(p, 'morale', 50) - 3)
                entry['match_events'].append({'type': 'morale', 'team': lteam.name, 'delta': -3})
        else:
            # empate: leve ajuste aleatório
            for p in (t1.players if t1 else []):
                p.morale = max(0, getattr(p, 'morale', 50) + 1)
            for p in (t2.players if t2 else []):
                p.morale = max(0, getattr(p, 'morale', 50) + 1)
            entry['match_events'].append({'type': 'morale', 'team': None, 'delta': 1})
    except Exception:
        pass

    # small chance of injury per team
    try:
        for team in (t1, t2):
            if not team:
                continue
            # 5% chance of one player injury
            if database.random.random() < 0.05:
                candidates = [p for p in team.players if not getattr(p, 'injured', False)]
                if candidates:
                    player = database.random.choice(candidates)
                    player.injured = True
                    player.morale = max(0, getattr(player, 'morale', 50) - 10)
                    entry['match_events'].append({'type': 'injury', 'team': team.name, 'player': player.name})
    except Exception:
        pass

    events.append(entry)
    save_events(events)

    # also persist a lightweight snapshot of current injuries/morale into savegame (best-effort)
    try:
        if hasattr(engine, 'teams'):
            # write a minimal events snapshot to events.json already done; optionally update savegame
            pass
    except Exception:
        pass

    return entry
