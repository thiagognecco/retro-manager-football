"""
FASE 5: Match Simulation Engine v2 - Complete Integration

Integrates all systems:
- Spatial Grid for O(1) agent queries
- Player Behavior Trees for decision making
- Player Movement with pathfinding & collision avoidance
- Tactical positioning via GNN model
- xG Calculator for shooting
- Pass Completion Model for passing
- Stamina Model for fatigue
- Formation Geometry for zone-based tactics

Runs 90 minutes of simulation at 60 FPS equivalent (90*60 = 5400 frames)
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import math
import time

from spatial_hash_grid import SpatialHashGrid
from player_behavior import Player, PlayerRole, PlayerState, build_match_context
from player_movement import PlayerMovement
from gnn_tactical_model import TacticalGraph, FormationType, MatchTacticalState


class MatchEvent(Enum):
    """Types of match events"""
    PASS = "pass"
    SHOT = "shot"
    TACKLE = "tackle"
    FOUL = "foul"
    GOAL = "goal"
    OUT_OF_BOUNDS = "out_of_bounds"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    INJURY = "injury"
    SUBSTITUTION = "substitution"


@dataclass
class Event:
    """Match event record"""
    event_type: MatchEvent
    time: int  # Match minute
    player_id: int
    team: str
    details: Dict = field(default_factory=dict)


class Team:
    """Team representation"""

    def __init__(self, name: str, formation: FormationType, strength: float):
        self.name = name
        self.formation = formation
        self.strength = strength  # 0-1 team quality
        self.players: List[Player] = []
        self.score = 0

    def add_player(self, player: Player) -> None:
        """Add player to team"""
        self.players.append(player)

    def get_players_by_role(self, role: PlayerRole) -> List[Player]:
        """Get players with specific role"""
        return [p for p in self.players if p.role == role]


class Match:
    """Complete match simulation"""

    def __init__(self, home_team: Team, away_team: Team):
        self.home_team = home_team
        self.away_team = away_team

        # Systems
        self.spatial_grid = SpatialHashGrid(cell_size=5, width=100, height=70)
        self.tactical_graph = TacticalGraph()
        self.tactical_state = MatchTacticalState()

        # Player movement controllers
        self.movement_controllers: Dict[int, PlayerMovement] = {}

        # Match state
        self.current_minute = 0
        self.current_frame = 0
        self.total_frames = 90 * 60  # 90 minutes at 60 FPS equiv
        self.ball_position = (50.0, 35.0)
        self.ball_holder: Optional[Player] = None
        self.ball_possession = None  # "Home" or "Away"
        self.events: List[Event] = []

        # Statistics
        self.stats = {
            'home': {
                'passes': 0,
                'pass_accuracy': 0,
                'shots': 0,
                'shots_on_target': 0,
                'goals': 0,
                'possession': 0,
                'distance_covered': 0,
                'avg_speed': 0,
            },
            'away': {
                'passes': 0,
                'pass_accuracy': 0,
                'shots': 0,
                'shots_on_target': 0,
                'goals': 0,
                'possession': 0,
                'distance_covered': 0,
                'avg_speed': 0,
            }
        }

        self._initialize()

    def _initialize(self) -> None:
        """Initialize match"""
        # Add all players to spatial grid
        for team in [self.home_team, self.away_team]:
            for player in team.players:
                self.spatial_grid.add_agent(player, player.x, player.y)
                self.movement_controllers[player.id] = PlayerMovement(player, self.spatial_grid)

        # Set initial ball holder (random midfielder)
        all_midfielders = (
            self.home_team.get_players_by_role(PlayerRole.MIDFIELDER) +
            self.away_team.get_players_by_role(PlayerRole.MIDFIELDER)
        )
        if all_midfielders:
            self.ball_holder = random.choice(all_midfielders)
            self.ball_holder.has_ball = True
            self.ball_possession = self.ball_holder.team

    def simulate_match(self) -> Dict:
        """
        Simulate complete 90-minute match

        Returns: Match result with statistics
        """
        print("\n[MATCH START] Simulating 90-minute match...")
        print(f"  {self.home_team.name} vs {self.away_team.name}")

        # Simulate minute by minute
        for minute in range(90):
            self.current_minute = minute
            self.simulate_minute()

        print(f"\n[MATCH END] Final Score: {self.home_team.name} {self.home_team.score} - {self.away_team.score} {self.away_team.name}")

        return self.get_match_result()

    def simulate_minute(self) -> None:
        """Simulate one minute (60 frames at 60 FPS)"""
        for frame in range(60):
            self.current_frame = self.current_minute * 60 + frame
            self.simulate_frame(dt=1.0/60.0)

    def simulate_frame(self, dt: float = 1.0/60.0) -> None:
        """
        Simulate one frame with timing instrumentation

        Args:
            dt: Delta time in seconds
        """
        frame_start = time.perf_counter()
        all_players = self.home_team.players + self.away_team.players

        # TIMING: Tactical state update
        t1 = time.perf_counter()
        self.tactical_state.update(
            all_players,
            self.ball_position,
            self.ball_possession,
            {'Home': self.home_team.score, 'Away': self.away_team.score}
        )
        t2 = time.perf_counter()

        # TIMING: Tactical graph build
        self.tactical_graph.build_graph(all_players, self.tactical_state.to_dict())
        t3 = time.perf_counter()

        # TIMING: Predict positions
        ideal_positions = self.tactical_graph.predict_positions(
            all_players,
            self.tactical_state.to_dict(),
            self.home_team.formation if self.ball_possession == "Home" else self.away_team.formation
        )
        t4 = time.perf_counter()

        # TIMING: Update behaviors (22 players)
        context = build_match_context({
            'spatial_grid': self.spatial_grid,
            'ball_holder': self.ball_holder,
            'ball_position': self.ball_position,
        })

        behavior_start = time.perf_counter()
        slow_players = []

        for player in all_players:
            p_start = time.perf_counter()
            player.update_behavior(context)
            p_behavior = time.perf_counter() - p_start

            if player.state == PlayerState.MOVING_TO_POSITION:
                target = ideal_positions.get(player.id, (player.x, player.y))
                self.movement_controllers[player.id].set_target(target)
            elif player.state == PlayerState.PASSING:
                if player.pass_target:
                    target = (player.pass_target.x, player.pass_target.y)
                    self.movement_controllers[player.id].set_target(target)
            elif player.state == PlayerState.DEFENDING or player.state == PlayerState.PRESSING:
                if player.mark_target or player.press_target:
                    target_player = player.mark_target or player.press_target
                    target = (target_player.x, target_player.y)
                    self.movement_controllers[player.id].set_target(target)

            # TIMING: Player movement update (22 players)
            self.movement_controllers[player.id].update(dt)

            # Track slow players
            p_total = (time.perf_counter() - p_start) * 1000
            if p_total > 100:
                slow_players.append((player.id, p_total))

        behavior_end = time.perf_counter()
        t5 = behavior_end

        # TIMING: Spatial grid rebuild
        grid_start = time.perf_counter()
        self.spatial_grid.clear()
        for player in all_players:
            self.spatial_grid.add_agent(player, player.x, player.y)
        grid_end = time.perf_counter()
        t6 = grid_end

        # TIMING: Events processing
        event_start = time.perf_counter()
        self._process_events()
        event_end = time.perf_counter()
        t7 = event_end

        # Update stamina (every second)
        if self.current_frame % 60 == 0:
            self._update_stamina()

        frame_end = time.perf_counter()
        total_ms = (frame_end - frame_start) * 1000

        # Print timing breakdown every 60 frames OR first frame
        if (self.current_frame % 60 == 0 and self.current_frame > 0) or self.current_frame == 0:
            print(f"\n[FRAME {self.current_frame}] Minute {self.current_minute} - Total: {total_ms:.2f}ms")
            print(f"  Tactical State: {(t2-t1)*1000:.2f}ms")
            print(f"  Graph Build:    {(t3-t2)*1000:.2f}ms")
            print(f"  Predict Pos:    {(t4-t3)*1000:.2f}ms")
            print(f"  Behaviors (22x):{(t5-t4)*1000:.2f}ms (avg: {(t5-t4)*1000/22:.2f}ms per player)")
            if slow_players:
                print(f"    Slow players: {slow_players[:5]}")  # Show top 5 slowest
            print(f"  Grid Rebuild:   {(t6-t5)*1000:.2f}ms")
            print(f"  Events:         {(t7-t6)*1000:.2f}ms")

    def _process_events(self) -> None:
        """Check for and process match events"""
        if self.ball_holder is None:
            return

        # Check for passes
        if self.ball_holder.desired_action == 'PASS' and self.ball_holder.pass_target:
            self._handle_pass()

        # Check for shots
        elif self.ball_holder.desired_action == 'SHOOT':
            self._handle_shot()

    def _handle_pass(self) -> None:
        """Handle pass event"""
        if not self.ball_holder or not self.ball_holder.pass_target:
            return

        # Simulate pass success based on distance and receiver position
        distance = self.ball_holder.pass_distance
        # Success rate decreases with distance
        success_prob = max(0.5, 1.0 - (distance / 50.0))

        if random.random() < success_prob:
            # Pass successful
            passer_id = self.ball_holder.id
            self.ball_holder.has_ball = False
            new_holder = self.ball_holder.pass_target
            new_holder.has_ball = True
            self.ball_holder = new_holder
            self.events.append(Event(
                event_type=MatchEvent.PASS,
                time=self.current_minute,
                player_id=new_holder.id,
                team=new_holder.team,
                details={'distance': distance, 'passer_id': passer_id}
            ))
            # HOOK 2: Form event for successful pass
            if hasattr(self, 'update_player_form_event'):
                self.update_player_form_event(passer_id, 'shot_on_target')  # Treat pass success as positive event
        else:
            # Pass intercepted - lose ball
            self._lose_ball()

    def _handle_shot(self) -> None:
        """Handle shot event"""
        if not self.ball_holder:
            return

        # Calculate xG based on position
        distance = self.ball_holder.shot_distance
        angle = self.ball_holder.shot_angle
        shooter_id = self.ball_holder.id

        # Simple xG calculation
        xg = self._calculate_xg(distance, angle)

        # Simulate shot result
        if random.random() < xg:
            # Goal!
            if self.ball_holder.team == "Home":
                self.home_team.score += 1
            else:
                self.away_team.score += 1

            self.events.append(Event(
                event_type=MatchEvent.GOAL,
                time=self.current_minute,
                player_id=shooter_id,
                team=self.ball_holder.team,
                details={'distance': distance, 'xg': xg}
            ))
            # HOOK 3: Form event for goal scored
            if hasattr(self, 'update_player_form_event'):
                self.update_player_form_event(shooter_id, 'goal')
            self._lose_ball()
        else:
            # Shot on target or miss
            self.events.append(Event(
                event_type=MatchEvent.SHOT,
                time=self.current_minute,
                player_id=shooter_id,
                team=self.ball_holder.team,
                details={'distance': distance, 'angle': angle, 'xg': xg}
            ))
            # HOOK 4: Form event for missed shot
            if hasattr(self, 'update_player_form_event'):
                self.update_player_form_event(shooter_id, 'missed_chance')
            self._lose_ball()

    def _calculate_xg(self, distance: float, angle: float) -> float:
        """
        Calculate expected goals (xG) for a shot

        Based on distance and angle to goal
        """
        # Base xG decreases with distance
        if distance > 40:
            return 0.01
        elif distance > 30:
            return 0.05
        elif distance > 20:
            return 0.15
        elif distance > 15:
            return 0.25
        elif distance > 10:
            return 0.35
        else:
            return 0.50

        # Could integrate with xg_advanced_calculator here
        # For now, using simplified model

    def _lose_ball(self) -> None:
        """Lose ball possession"""
        if self.ball_holder:
            self.ball_holder.has_ball = False

        # Random opponent gets ball
        opponent_team = (
            self.away_team if self.ball_holder.team == "Home"
            else self.home_team
        )
        self.ball_holder = random.choice(opponent_team.players)
        self.ball_holder.has_ball = True
        self.ball_possession = self.ball_holder.team

    def _update_stamina(self) -> None:
        """Update stamina for all players"""
        all_players = self.home_team.players + self.away_team.players
        for player in all_players:
            # Stamina decreases based on movement and intensity
            velocity_magnitude = (player.current_velocity[0]**2 + player.current_velocity[1]**2) ** 0.5
            stamina_loss = 0.1 + (velocity_magnitude / 10.0) * 0.2  # 0.1-0.3 per second

            player.stamina = max(0, player.stamina - stamina_loss)

            # Slower if low stamina
            if player.stamina < 30:
                player.speed = 5.0
            elif player.stamina < 50:
                player.speed = 6.0

    def get_match_result(self) -> Dict:
        """Get final match result and statistics"""
        return {
            'match_duration': 90,
            'home_team': {
                'name': self.home_team.name,
                'goals': self.home_team.score,
                'possession': self.stats['home']['possession'],
                'shots': self.stats['home']['shots'],
                'shots_on_target': self.stats['home']['shots_on_target'],
                'passes': self.stats['home']['passes'],
                'pass_accuracy': self.stats['home']['pass_accuracy'],
            },
            'away_team': {
                'name': self.away_team.name,
                'goals': self.away_team.score,
                'possession': self.stats['away']['possession'],
                'shots': self.stats['away']['shots'],
                'shots_on_target': self.stats['away']['shots_on_target'],
                'passes': self.stats['away']['passes'],
                'pass_accuracy': self.stats['away']['pass_accuracy'],
            },
            'events': len(self.events),
            'event_log': self.events[:100],  # First 100 events
        }


def create_sample_teams() -> Tuple[Team, Team]:
    """Create sample teams for testing"""
    home = Team("Manchester United", FormationType.FORMATION_4_3_3, 0.85)
    away = Team("Liverpool", FormationType.FORMATION_4_2_3_1, 0.82)

    # Add players to home team
    home_positions = [
        (5, 35),    # GK
        (15, 15), (15, 25), (15, 45), (15, 55),  # Defenders
        (40, 20), (40, 35), (40, 50),  # Midfielders
        (70, 25), (70, 45), (75, 35),  # Forwards
    ]

    home_roles = [
        PlayerRole.GOALKEEPER,
        PlayerRole.DEFENDER, PlayerRole.DEFENDER, PlayerRole.DEFENDER, PlayerRole.DEFENDER,
        PlayerRole.MIDFIELDER, PlayerRole.MIDFIELDER, PlayerRole.MIDFIELDER,
        PlayerRole.FORWARD, PlayerRole.FORWARD, PlayerRole.FORWARD,
    ]

    for i, (pos, role) in enumerate(zip(home_positions, home_roles)):
        player = Player(
            id=i+1,
            name=f"Home_P{i+1}",
            team="Home",
            role=role,
            number=i+1,
            x=pos[0],
            y=pos[1]
        )
        home.add_player(player)

    # Add players to away team
    away_positions = [
        (95, 35),   # GK
        (85, 15), (85, 25), (85, 45), (85, 55),  # Defenders
        (60, 20), (60, 35), (60, 50),  # Midfielders
        (30, 25), (30, 45), (25, 35),  # Forwards
    ]

    for i, (pos, role) in enumerate(zip(away_positions, home_roles)):
        player = Player(
            id=i+12,
            name=f"Away_P{i+1}",
            team="Away",
            role=role,
            number=i+1,
            x=pos[0],
            y=pos[1]
        )
        away.add_player(player)

    return home, away
