import os
from game import GameEngine
import events


def test_events_file_created_and_has_entries():
    # remove existing events file to start clean
    if os.path.exists('events.json'):
        os.remove('events.json')

    engine = GameEngine()
    engine.new_game()

    # play a few matches to generate events
    for _ in range(3):
        opponent = engine.player_team
        for t in engine.teams:
            if t is not engine.player_team:
                opponent = t
                break
        engine.simulate_match(engine.player_team, opponent)

    assert os.path.exists('events.json'), "events.json must be created"

    data = events.load_events()
    assert isinstance(data, list) and len(data) >= 1, "events.json should contain at least one match record"

    # each record should have basic keys
    for rec in data:
        assert 'team1' in rec and 'team2' in rec and 'score1' in rec and 'score2' in rec


if __name__ == '__main__':
    test_events_file_created_and_has_entries()
    print('test_events: OK')