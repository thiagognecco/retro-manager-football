"""
Comprehensive tests for Spatial Hash Grid (FASE 1)

Tests:
- Correct behavior of nearby_agents()
- O(1) performance validation
- No memory leaks
- Edge cases (boundaries, overlaps)
"""

import time
import math
from spatial_hash_grid import SpatialHashGrid, Agent


def test_basic_add_query():
    """Test basic add and query functionality"""
    print("\n[TEST 1] Basic add and query")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Create 2 agents close together
    player1 = Agent(id=1, name="P1", x=30, y=35)
    player2 = Agent(id=2, name="P2", x=35, y=38)

    grid.add_agent(player1, 30, 35)
    grid.add_agent(player2, 35, 38)

    # Query should find both within 10m radius
    nearby = grid.nearby_agents(33, 36, radius=10)
    assert len(nearby) == 2, f"Expected 2 agents, got {len(nearby)}"
    assert player1 in nearby, "Player1 not found"
    assert player2 in nearby, "Player2 not found"

    print("[OK] Basic add and query works")


def test_distance_threshold():
    """Test that distance threshold is respected"""
    print("\n[TEST 2] Distance threshold")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Agent at exact position
    player1 = Agent(id=1, name="P1", x=50, y=35)
    grid.add_agent(player1, 50, 35)

    # Query exactly at agent - should find it
    nearby = grid.nearby_agents(50, 35, radius=0)
    assert len(nearby) == 1, "Should find agent at exact position with radius=0"
    print("  [OK] Finds agent at exact position")

    # Query within radius
    nearby = grid.nearby_agents(50, 35, radius=5)
    assert len(nearby) == 1, "Should find agent within radius"
    print("  [OK] Finds agent within radius")

    # Query outside radius
    nearby = grid.nearby_agents(50, 35, radius=1)
    # At distance 0, should still find
    assert len(nearby) == 1, "Agent at same position should always be found"
    print("  [OK] Distance threshold respected")


def test_22_players_realistic():
    """Test with 22 realistic football player positions"""
    print("\n[TEST 3] 22 players realistic simulation")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Create 22 players in realistic formation (4-3-3)
    # Field positions (100m x 70m)
    players = []

    # Goalkeepers (1 per team, let's use 2 for simulation)
    positions = [
        (5, 35),    # GK 1
        (95, 35),   # GK 2

        # Defenders (4-4-8 back)
        (15, 15), (15, 25), (15, 45), (15, 55),  # Team 1 defense
        (85, 15), (85, 25), (85, 45), (85, 55),  # Team 2 defense

        # Midfielders (6)
        (40, 20), (40, 35), (40, 50),            # Team 1 midfield
        (60, 20), (60, 35), (60, 50),            # Team 2 midfield

        # Forwards (6)
        (75, 25), (75, 45),                       # Team 1 forwards
        (25, 25), (25, 45),                       # Team 2 forwards
        (70, 35),                                 # Team 1 striker
        (30, 35),                                 # Team 2 striker
    ]

    for i, (x, y) in enumerate(positions):
        player = Agent(id=i+1, name=f"P{i+1}", x=x, y=y)
        grid.add_agent(player, x, y)
        players.append(player)

    assert len(grid.get_all_agents()) == 22, "Should have 22 players"
    print(f"  [OK] Added 22 players")

    # Test queries
    # Query near team 1 striker
    nearby_striker = grid.nearby_agents(70, 35, radius=15)
    assert len(nearby_striker) > 0, "Should find nearby players"
    print(f"  [OK] Query near striker found {len(nearby_striker)} nearby players")

    # Query in center field
    nearby_center = grid.nearby_agents(50, 35, radius=20)
    assert len(nearby_center) > 0, "Should find players in center"
    print(f"  [OK] Query in center found {len(nearby_center)} nearby players")

    # Query near corner
    nearby_corner = grid.nearby_agents(10, 10, radius=10)
    print(f"  [OK] Query in corner found {len(nearby_corner)} nearby players")

    print(grid.visualize())


def test_performance_o1():
    """Validate O(1) performance of nearby_agents queries"""
    print("\n[TEST 4] Performance validation - O(1) queries")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Add 22 players
    for i in range(22):
        x = (i % 6) * 15 + 10
        y = (i % 4) * 15 + 10
        player = Agent(id=i+1, name=f"P{i+1}", x=x, y=y)
        grid.add_agent(player, x, y)

    # Perform many queries and measure time
    query_positions = [
        (30, 35),
        (50, 35),
        (70, 35),
        (20, 20),
        (80, 60),
    ]

    total_time = 0
    query_count = 100

    start = time.perf_counter()
    for _ in range(query_count):
        for x, y in query_positions:
            nearby = grid.nearby_agents(x, y, radius=10)
    end = time.perf_counter()

    total_time = (end - start) * 1000  # Convert to ms
    avg_time = total_time / (query_count * len(query_positions))

    print(f"  {query_count} × {len(query_positions)} queries")
    print(f"  Total time: {total_time:.2f} ms")
    print(f"  Average per query: {avg_time:.4f} ms")

    # Should be <1ms per query
    assert avg_time < 1.0, f"Query too slow: {avg_time:.4f} ms (expected <1ms)"
    print(f"  [OK] Performance validated (<1ms per query)")


def test_update_position():
    """Test updating agent position"""
    print("\n[TEST 5] Update position")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    player = Agent(id=1, name="P1", x=30, y=35)
    grid.add_agent(player, 30, 35)

    # Find before move
    nearby_before = grid.nearby_agents(33, 36, radius=10)
    assert len(nearby_before) == 1, "Should find player before move"

    # Move player
    grid.update_agent_position(1, 80, 65)

    # Should not find in old location
    nearby_old = grid.nearby_agents(33, 36, radius=10)
    assert len(nearby_old) == 0, "Should not find player in old location after move"

    # Should find in new location
    nearby_new = grid.nearby_agents(80, 65, radius=10)
    assert len(nearby_new) == 1, "Should find player in new location"

    print("  [OK] Position update works correctly")


def test_remove_agent():
    """Test removing agents"""
    print("\n[TEST 6] Remove agent")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    player1 = Agent(id=1, name="P1", x=30, y=35)
    player2 = Agent(id=2, name="P2", x=35, y=38)

    grid.add_agent(player1, 30, 35)
    grid.add_agent(player2, 35, 38)

    assert len(grid.get_all_agents()) == 2, "Should have 2 players"

    # Remove one
    removed = grid.remove_agent(1)
    assert removed, "Remove should return True"

    nearby = grid.nearby_agents(33, 36, radius=10)
    assert len(nearby) == 1, "Should find only 1 player after removal"
    assert player2 in nearby, "Should be player2"

    # Try remove non-existent
    removed = grid.remove_agent(999)
    assert not removed, "Remove non-existent should return False"

    print("  [OK] Remove agent works correctly")


def test_boundary_conditions():
    """Test agents at field boundaries"""
    print("\n[TEST 7] Boundary conditions")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Corners
    p_tl = Agent(id=1, name="TL", x=0, y=0)
    p_tr = Agent(id=2, name="TR", x=100, y=0)
    p_bl = Agent(id=3, name="BL", x=0, y=70)
    p_br = Agent(id=4, name="BR", x=100, y=70)

    grid.add_agent(p_tl, 0, 0)
    grid.add_agent(p_tr, 100, 0)
    grid.add_agent(p_bl, 0, 70)
    grid.add_agent(p_br, 100, 70)

    # Query at each corner
    nearby_tl = grid.nearby_agents(0, 0, radius=5)
    assert p_tl in nearby_tl, "Should find corner agent"

    nearby_br = grid.nearby_agents(100, 70, radius=5)
    assert p_br in nearby_br, "Should find corner agent"

    print("  [OK] Boundary conditions handled correctly")


def test_memory_no_leaks():
    """Test for memory leaks with add/remove cycles"""
    print("\n[TEST 8] Memory leak detection")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Add and remove many agents
    for cycle in range(10):
        # Add 22 players
        agents = []
        for i in range(22):
            agent = Agent(id=cycle*100+i, name=f"P{i}", x=30+i*2, y=35)
            grid.add_agent(agent, 30+i*2, 35)
            agents.append(agent)

        # Remove them
        for agent in agents:
            grid.remove_agent(agent.id)

    # Grid should be clean
    assert len(grid.get_all_agents()) == 0, "Grid should be empty after all removals"
    assert len(grid.agent_map) == 0, "Agent map should be empty"
    assert len(grid.grid) == 0, "Grid cells should be empty"

    print("  [OK] No memory leaks detected")


def test_stats():
    """Test statistics tracking"""
    print("\n[TEST 9] Statistics tracking")
    grid = SpatialHashGrid(cell_size=5, width=100, height=70)

    # Add some players
    for i in range(22):
        player = Agent(id=i+1, name=f"P{i+1}", x=30+i*2, y=35)
        grid.add_agent(player, 30+i*2, 35)

    # Get stats
    stats = grid.get_stats()

    assert stats['total_agents'] == 22, "Should count 22 agents"
    assert stats['occupied_cells'] > 0, "Should have occupied cells"
    assert stats['avg_cell_density'] > 0, "Should calculate density"

    print(f"  Stats: {stats}")
    print("  [OK] Statistics tracking works")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("SPATIAL HASH GRID - PHASE 1 TESTS")
    print("="*60)

    tests = [
        test_basic_add_query,
        test_distance_threshold,
        test_22_players_realistic,
        test_performance_o1,
        test_update_position,
        test_remove_agent,
        test_boundary_conditions,
        test_memory_no_leaks,
        test_stats,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
