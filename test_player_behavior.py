"""
Tests para Player Behavior Trees - FASE 2 Setup Validation

Valida:
- Behavior tree structure
- State transitions
- Decision logic
- Integration com spatial grid
"""

from player_behavior import (
    Player, PlayerRole, PlayerState, PlayerBehaviorTree,
    Task_HasBall, Task_CanShoot, Task_CanPass, Task_Defend,
    Selector, Sequence, build_match_context
)
from spatial_hash_grid import SpatialHashGrid, Agent


def test_player_creation():
    """Test creating a player with behavior tree"""
    print("\n[TEST 1] Player creation")

    player = Player(
        id=1,
        name="Cristiano",
        team="Home",
        role=PlayerRole.FORWARD,
        number=7,
        x=75,
        y=35
    )

    assert player.id == 1, "Player ID should be set"
    assert player.name == "Cristiano", "Player name should be set"
    assert player.team == "Home", "Team should be set"
    assert player.behavior_tree is not None, "Behavior tree should be initialized"
    assert player.state == PlayerState.IDLE, "Initial state should be IDLE"

    print("  [OK] Player created with behavior tree")


def test_behavior_tree_ticks():
    """Test behavior tree ticking"""
    print("\n[TEST 2] Behavior tree execution")

    player = Player(
        id=1,
        name="Test",
        team="Home",
        role=PlayerRole.MIDFIELDER,
        number=8
    )

    # Create context
    context = build_match_context({
        'spatial_grid': SpatialHashGrid(),
        'ball_holder': None,
        'ball_position': (50, 35),
    })

    # Tick behavior tree
    action = player.update_behavior(context)

    assert player.desired_action is not None, "Action should be set"
    assert isinstance(player.state, PlayerState), "State should be PlayerState enum"

    print(f"  [OK] Behavior tree ticked: action={player.desired_action}, state={player.state.value}")


def test_has_ball_decision():
    """Test has ball decision"""
    print("\n[TEST 3] Has ball decision")

    player = Player(
        id=1,
        name="Test",
        team="Home",
        role=PlayerRole.MIDFIELDER,
        number=8,
        x=50,
        y=35
    )

    # Initially no ball
    has_ball_task = Task_HasBall()
    result = has_ball_task.tick(player, {})
    assert result == 'FAILURE', "Should fail when no ball"
    print("  [OK] Correctly detects no ball")

    # Give player ball
    player.has_ball = True
    result = has_ball_task.tick(player, {})
    assert result == 'SUCCESS', "Should succeed with ball"
    print("  [OK] Correctly detects ball possession")


def test_shooting_decision():
    """Test shooting decision based on position"""
    print("\n[TEST 4] Shooting decision")

    # Player far from goal - can't shoot
    player_far = Player(
        id=1,
        name="Test",
        team="Home",
        role=PlayerRole.MIDFIELDER,
        number=8,
        x=30,
        y=35
    )
    player_far.has_ball = True

    shoot_task = Task_CanShoot()
    result = shoot_task.tick(player_far, {})
    assert result == 'FAILURE', "Should not shoot from 70m"
    print("  [OK] Rejects shooting from far away")

    # Player close to goal - can shoot
    player_close = Player(
        id=2,
        name="Test",
        team="Home",
        role=PlayerRole.FORWARD,
        number=9,
        x=85,
        y=35
    )
    player_close.has_ball = True

    result = shoot_task.tick(player_close, {})
    assert result == 'SUCCESS', "Should allow shooting from 15m"
    print("  [OK] Allows shooting when close to goal")


def test_passing_decision():
    """Test passing decision with spatial grid"""
    print("\n[TEST 5] Passing decision")

    grid = SpatialHashGrid()

    # Player with ball
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
    grid.add_agent(passer, 50, 35)

    # Teammate nearby
    teammate = Player(
        id=2,
        name="Teammate",
        team="Home",
        role=PlayerRole.FORWARD,
        number=9,
        x=55,
        y=40
    )
    grid.add_agent(teammate, 55, 40)

    context = {'spatial_grid': grid}

    can_pass = Task_CanPass()
    result = can_pass.tick(passer, context)
    assert result == 'SUCCESS', "Should find passing option"
    print("  [OK] Correctly detects passing options")


def test_defense_decision():
    """Test defensive positioning"""
    print("\n[TEST 6] Defense decision")

    grid = SpatialHashGrid()

    # Defender
    defender = Player(
        id=1,
        name="Defender",
        team="Home",
        role=PlayerRole.DEFENDER,
        number=4,
        x=20,
        y=35
    )
    grid.add_agent(defender, 20, 35)

    # Attacker nearby
    attacker = Player(
        id=2,
        name="Attacker",
        team="Away",
        role=PlayerRole.FORWARD,
        number=9,
        x=25,
        y=38
    )
    grid.add_agent(attacker, 25, 38)

    context = {'spatial_grid': grid}

    defend_task = Task_Defend()
    result = defend_task.tick(defender, context)
    assert result == 'SUCCESS', "Should find opponent to mark"
    assert defender.mark_target == attacker, "Should mark closest attacker"
    assert defender.state == PlayerState.DEFENDING, "State should be DEFENDING"

    print("  [OK] Correctly marks opponent for defense")


def test_state_transitions():
    """Test state machine transitions"""
    print("\n[TEST 7] State transitions")

    player = Player(
        id=1,
        name="Test",
        team="Home",
        role=PlayerRole.MIDFIELDER,
        number=8
    )

    # Initial state
    assert player.state == PlayerState.IDLE, "Should start IDLE"
    print("  [OK] Initial state IDLE")

    # Transition to PASSING
    player.state = PlayerState.PASSING
    assert player.state == PlayerState.PASSING, "Should transition to PASSING"
    print("  [OK] Can transition to PASSING")

    # Transition to DEFENDING
    player.state = PlayerState.DEFENDING
    assert player.state == PlayerState.DEFENDING, "Should transition to DEFENDING"
    print("  [OK] Can transition to DEFENDING")

    # Transition to INJURED
    player.state = PlayerState.INJURED
    assert player.state == PlayerState.INJURED, "Should transition to INJURED"
    action = player.update_behavior({})
    assert action == "INJURED", "Should return INJURED action"
    print("  [OK] Can transition to INJURED")


def test_selector_logic():
    """Test Selector (OR) logic"""
    print("\n[TEST 8] Selector logic (OR)")

    player = Player(
        id=1,
        name="Test",
        team="Home",
        role=PlayerRole.MIDFIELDER,
        number=8
    )

    # Create selector with multiple options
    selector = Selector([
        Task_HasBall(),      # Will fail (no ball)
        Task_CanShoot(),     # Will fail (no ball)
        Task_Defend(),       # Will fail (no grid)
    ], name="TestSelector")

    context = {}
    result = selector.tick(player, context)
    assert result == 'FAILURE', "Selector should fail if all children fail"
    print("  [OK] Selector returns FAILURE when all children fail")

    # Now add succeeding task
    player.has_ball = True
    selector2 = Selector([
        Task_HasBall(),      # Will succeed
        Task_CanShoot(),
    ])

    result = selector2.tick(player, context)
    assert result == 'SUCCESS', "Selector should succeed if any child succeeds"
    print("  [OK] Selector returns SUCCESS when any child succeeds")


def test_sequence_logic():
    """Test Sequence (AND) logic"""
    print("\n[TEST 9] Sequence logic (AND)")

    player = Player(
        id=1,
        name="Test",
        team="Home",
        role=PlayerRole.FORWARD,
        number=9,
        x=85,
        y=35
    )
    player.has_ball = True

    # Sequence that should succeed
    sequence = Sequence([
        Task_HasBall(),      # Will succeed
        Task_CanShoot(),     # Will succeed (close to goal)
    ])

    context = {}
    result = sequence.tick(player, context)
    assert result == 'SUCCESS', "Sequence should succeed if all children succeed"
    print("  [OK] Sequence returns SUCCESS when all children succeed")

    # Sequence that should fail
    player.has_ball = False
    sequence2 = Sequence([
        Task_HasBall(),      # Will fail
        Task_CanShoot(),
    ])

    result = sequence2.tick(player, context)
    assert result == 'FAILURE', "Sequence should fail at first failure"
    print("  [OK] Sequence returns FAILURE at first failure")


def test_22_players_behavior():
    """Test 22 players with behavior trees"""
    print("\n[TEST 10] 22 players behavior")

    grid = SpatialHashGrid()
    players = []

    # Create 22 players
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

    assert len(players) == 22, "Should have 22 players"
    print(f"  [OK] Created 22 players")

    # All players should have behavior trees
    for player in players:
        assert player.behavior_tree is not None, f"Player {player.name} should have behavior tree"

    print(f"  [OK] All 22 players have behavior trees")

    # Update all behaviors
    context = build_match_context({
        'spatial_grid': grid,
        'ball_holder': players[10],  # Midfielder
        'ball_position': (40, 35),
    })

    for player in players:
        action = player.update_behavior(context)
        assert action is not None, f"Player {player.name} should return action"

    print(f"  [OK] All 22 players updated behavior")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PLAYER BEHAVIOR TREES - PHASE 2 SETUP TESTS")
    print("="*60)

    tests = [
        test_player_creation,
        test_behavior_tree_ticks,
        test_has_ball_decision,
        test_shooting_decision,
        test_passing_decision,
        test_defense_decision,
        test_state_transitions,
        test_selector_logic,
        test_sequence_logic,
        test_22_players_behavior,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
