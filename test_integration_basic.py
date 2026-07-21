"""
Basic Integration Test - Spatial Grid + Behavior Trees

Valida que os dois sistemas funcionam juntos corretamente
"""

from spatial_hash_grid import SpatialHashGrid, Agent
from player_behavior import Player, PlayerRole, build_match_context


def test_spatial_grid_with_behavior_trees():
    """Test spatial grid providing data to behavior trees"""
    print("\n[INTEGRATION TEST] Spatial Grid + Behavior Trees")

    # Create grid
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Create players
    passer = Player(
        id=1,
        name="Passer",
        team="Home",
        role=PlayerRole.MIDFIELDER,
        number=8,
        x=50,
        y=35
    )
    passer.has_ball = True

    teammate = Player(
        id=2,
        name="Teammate",
        team="Home",
        role=PlayerRole.FORWARD,
        number=9,
        x=55,
        y=40
    )

    opponent = Player(
        id=3,
        name="Opponent",
        team="Away",
        role=PlayerRole.DEFENDER,
        number=4,
        x=60,
        y=35
    )

    # Add to grid
    grid.add_agent(passer, 50, 35)
    grid.add_agent(teammate, 55, 40)
    grid.add_agent(opponent, 60, 35)

    print(f"  [OK] Added 3 players to grid")

    # Create context
    context = build_match_context({
        'spatial_grid': grid,
        'ball_holder': passer,
        'ball_position': (50, 35),
    })

    # Tick passer's behavior (should pass)
    passer.update_behavior(context)
    print(f"  [OK] Passer action: {passer.desired_action}")
    assert passer.desired_action in ['PASS', 'MOVE_TO_POSITION', 'SHOOT'], \
        f"Expected valid action, got {passer.desired_action}"

    # Tick teammate's behavior (should move to position)
    teammate.update_behavior(context)
    print(f"  [OK] Teammate action: {teammate.desired_action}")

    # Tick opponent's behavior (should defend)
    opponent.update_behavior(context)
    print(f"  [OK] Opponent action: {opponent.desired_action}")
    assert opponent.desired_action == 'DEFEND', \
        f"Expected DEFEND, got {opponent.desired_action}"

    print("\n[SUCCESS] Spatial grid and behavior trees integrate correctly!")


def test_match_simulation_context():
    """Test building match context for all 22 players"""
    print("\n[INTEGRATION TEST] Match Context for 22 Players")

    # Create grid
    grid = SpatialHashGrid()

    # Create 22 players
    players = []
    positions = [
        (5, 35),    # GK 1
        (95, 35),   # GK 2

        (15, 15), (15, 25), (15, 45), (15, 55),  # Defenders 1
        (85, 15), (85, 25), (85, 45), (85, 55),  # Defenders 2

        (40, 20), (40, 35), (40, 50),  # Midfielders 1
        (60, 20), (60, 35), (60, 50),  # Midfielders 2

        (75, 25), (75, 45), (25, 25), (25, 45),  # Forwards
        (70, 35), (30, 35),  # Strikers
    ]

    teams = ["Home"] * 11 + ["Away"] * 11
    roles = [PlayerRole.GOALKEEPER, PlayerRole.GOALKEEPER] + \
            [PlayerRole.DEFENDER] * 8 + \
            [PlayerRole.MIDFIELDER] * 6 + \
            [PlayerRole.FORWARD] * 6

    for i, ((x, y), team, role) in enumerate(zip(positions, teams, roles)):
        player = Player(
            id=i+1,
            name=f"P{i+1}",
            team=team,
            role=role,
            number=i+1,
            x=x,
            y=y
        )
        grid.add_agent(player, x, y)
        players.append(player)

    print(f"  [OK] Created 22 players")

    # Set ball to midfielder
    ball_holder = players[10]  # Midfielder
    ball_holder.has_ball = True

    # Build match context
    context = build_match_context({
        'spatial_grid': grid,
        'ball_holder': ball_holder,
        'ball_position': (40, 35),
        'score': {'Home': 0, 'Away': 0},
        'time_remaining': 5400,  # 90 minutes
    })

    print(f"  [OK] Built match context")

    # Update all players
    home_actions = {}
    away_actions = {}

    for player in players:
        action = player.update_behavior(context)
        if player.team == "Home":
            home_actions[player.name] = action
        else:
            away_actions[player.name] = action

    print(f"  [OK] Updated all 22 players")
    print(f"\n  Home team actions: {list(set(home_actions.values()))}")
    print(f"  Away team actions: {list(set(away_actions.values()))}")

    # Validate
    assert len(home_actions) == 11, "Should have 11 home players"
    assert len(away_actions) == 11, "Should have 11 away players"

    print("\n[SUCCESS] Match context works with 22 players!")


def test_player_movement_simulation():
    """Test a simple movement scenario"""
    print("\n[INTEGRATION TEST] Player Movement Scenario")

    grid = SpatialHashGrid()

    # Player starts at center
    player = Player(
        id=1,
        name="Test",
        team="Home",
        role=PlayerRole.MIDFIELDER,
        number=8,
        x=50,
        y=35
    )
    grid.add_agent(player, 50, 35)

    context = build_match_context({
        'spatial_grid': grid,
        'ball_holder': None,
        'ball_position': (50, 35),
    })

    # Initial update
    action1 = player.update_behavior(context)
    pos1 = (player.x, player.y)

    print(f"  Step 1: Position {pos1}, Action: {action1}")

    # Simulate position update (would happen in movement phase)
    grid.update_agent_position(player.id, 52, 37)

    # Second update
    action2 = player.update_behavior(context)
    pos2 = (player.x, player.y)

    print(f"  Step 2: Position {pos2}, Action: {action2}")

    print("\n[SUCCESS] Player movement scenario works!")


def run_all_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("SPATIAL GRID + BEHAVIOR TREES - INTEGRATION TESTS")
    print("="*60)

    tests = [
        test_spatial_grid_with_behavior_trees,
        test_match_simulation_context,
        test_player_movement_simulation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n  [FAIL] {e}")
            failed += 1
        except Exception as e:
            print(f"\n  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_integration_tests()
    exit(0 if success else 1)
