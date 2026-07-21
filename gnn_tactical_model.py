"""
FASE 4: GNN Tactical Model - Intelligent Tactical Positioning

Uses tactical heuristics (Graph-based reasoning) to determine:
- Optimal positioning for players
- Formation adjustments based on game state
- Defensive/offensive transitions
- Support positioning for ball carrier

This simulates GNN behavior with tactical football knowledge
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class FormationType(Enum):
    """Standard football formations"""
    FORMATION_4_3_3 = "4-3-3"
    FORMATION_4_2_3_1 = "4-2-3-1"
    FORMATION_3_5_2 = "3-5-2"
    FORMATION_5_3_2 = "5-3-2"


@dataclass
class FormationConfig:
    """Configuration for a football formation"""
    name: str
    defensive_line: float  # Y coordinate for defense
    midfield_line: float   # Y coordinate for midfield
    attacking_line: float  # Y coordinate for attack
    width_spread: float    # How spread out players are (0-1)
    defensive_focus: float # 0-1, how defensive/cautious


class TacticalPositioning:
    """
    Calculates optimal tactical positions based on:
    - Current formation
    - Ball position
    - Score state
    - Possession
    - Opponent positions
    """

    def __init__(self):
        self.formations = {
            FormationType.FORMATION_4_3_3: FormationConfig(
                name="4-3-3",
                defensive_line=20,
                midfield_line=45,
                attacking_line=70,
                width_spread=0.85,
                defensive_focus=0.4
            ),
            FormationType.FORMATION_4_2_3_1: FormationConfig(
                name="4-2-3-1",
                defensive_line=20,
                midfield_line=40,
                attacking_line=65,
                width_spread=0.7,
                defensive_focus=0.6
            ),
            FormationType.FORMATION_3_5_2: FormationConfig(
                name="3-5-2",
                defensive_line=22,
                midfield_line=45,
                attacking_line=68,
                width_spread=0.9,
                defensive_focus=0.3
            ),
        }

    def get_formation(self, formation_type: FormationType) -> FormationConfig:
        """Get formation config"""
        return self.formations.get(formation_type, self.formations[FormationType.FORMATION_4_3_3])

    def calculate_ideal_position(self, player: 'Player', match_state: Dict,
                                formation: FormationType) -> Tuple[float, float]:
        """
        Calculate ideal position for player based on tactical model

        Args:
            player: Player object
            match_state: Current match state (ball_pos, possession, score)
            formation: Formation type

        Returns: (x, y) ideal position
        """
        config = self.get_formation(formation)
        ball_x, ball_y = match_state.get('ball_position', (50, 35))
        possession = match_state.get('possession')  # "Home" or "Away"
        score_diff = match_state.get('score_diff', 0)  # Our score - opponent score

        # Base position based on role
        x, y = self._get_role_position(player, config)

        # Adjust based on ball position
        x, y = self._adjust_for_ball(player, x, y, ball_x, ball_y, possession, config)

        # Adjust based on game state
        x, y = self._adjust_for_game_state(player, x, y, score_diff, config)

        # Clamp to field
        x = max(0, min(100, x))
        y = max(0, min(70, y))

        return (x, y)

    def _get_role_position(self, player: 'Player', config: FormationConfig) -> Tuple[float, float]:
        """Get base position for player role"""
        from player_behavior import PlayerRole

        if player.team == "Away":
            # Mirror positions for away team
            if player.role == PlayerRole.GOALKEEPER:
                return (5, 35)
            elif player.role == PlayerRole.DEFENDER:
                return (100 - config.defensive_line, 35)
            elif player.role == PlayerRole.MIDFIELDER:
                return (100 - config.midfield_line, 35)
            elif player.role == PlayerRole.FORWARD:
                return (100 - config.attacking_line, 35)
        else:
            # Home team
            if player.role == PlayerRole.GOALKEEPER:
                return (5, 35)
            elif player.role == PlayerRole.DEFENDER:
                return (config.defensive_line, 35)
            elif player.role == PlayerRole.MIDFIELDER:
                return (config.midfield_line, 35)
            elif player.role == PlayerRole.FORWARD:
                return (config.attacking_line, 35)

        return (50, 35)

    def _adjust_for_ball(self, player: 'Player', x: float, y: float,
                        ball_x: float, ball_y: float, possession: str,
                        config: FormationConfig) -> Tuple[float, float]:
        """Adjust position based on ball location"""
        from player_behavior import PlayerRole

        # If our team has ball, attack
        if possession == player.team:
            if player.role == PlayerRole.MIDFIELDER or player.role == PlayerRole.FORWARD:
                # Move toward ball for support
                dx = ball_x - x
                dy = ball_y - y
                dist = (dx*dx + dy*dy) ** 0.5
                if dist > 0 and dist < 30:
                    x += dx * 0.3
                    y += dy * 0.3
        else:
            # Opponent has ball - defensive positioning
            if player.role == PlayerRole.DEFENDER or player.role == PlayerRole.MIDFIELDER:
                # Move toward ball to defend
                dx = ball_x - x
                dy = ball_y - y
                dist = (dx*dx + dy*dy) ** 0.5
                if dist > 0:
                    x += dx * 0.4
                    y += dy * 0.4

        # Spread players across field width
        # Push to wings if on wings, center if in center
        center_y = 35
        if y < center_y - 10:
            # On left wing
            y -= 2 * config.width_spread
        elif y > center_y + 10:
            # On right wing
            y += 2 * config.width_spread

        return (x, y)

    def _adjust_for_game_state(self, player: 'Player', x: float, y: float,
                              score_diff: int, config: FormationConfig) -> Tuple[float, float]:
        """Adjust position based on game score"""
        from player_behavior import PlayerRole

        if score_diff < 0:
            # Losing - push forward more
            if player.role == PlayerRole.FORWARD:
                if player.team == "Home":
                    x += 5
                else:
                    x -= 5
            elif player.role == PlayerRole.MIDFIELDER:
                if player.team == "Home":
                    x += 3
                else:
                    x -= 3
        elif score_diff > 0:
            # Winning - drop deeper for defense
            if player.role == PlayerRole.DEFENDER:
                if player.team == "Home":
                    x -= 3
                else:
                    x += 3
            elif player.role == PlayerRole.MIDFIELDER:
                if player.team == "Home":
                    x -= 2
                else:
                    x += 2

        return (x, y)


class TacticalGraph:
    """
    Represents tactical relationships between players
    (Simulates graph neural network reasoning)
    """

    def __init__(self):
        self.positioning = TacticalPositioning()
        self.node_features = {}  # Player features
        self.edge_weights = {}   # Relationship weights

    def build_graph(self, players: List['Player'], match_state: Dict) -> None:
        """Build tactical graph"""
        self.node_features.clear()
        self.edge_weights.clear()

        for player in players:
            # Node features: position, state, role
            self.node_features[player.id] = {
                'pos': (player.x, player.y),
                'state': player.state.value,
                'role': player.role.value,
                'has_ball': player.has_ball,
            }

        # Build edges based on proximity and team
        for i, player1 in enumerate(players):
            for player2 in players[i+1:]:
                if player1.team == player2.team:
                    dist = ((player1.x - player2.x)**2 + (player1.y - player2.y)**2) ** 0.5
                    # Weight based on distance (closer = stronger connection)
                    weight = 1.0 / (1.0 + dist / 10.0)
                    self.edge_weights[(player1.id, player2.id)] = weight

    def predict_positions(self, players: List['Player'], match_state: Dict,
                         formation: FormationType) -> Dict[int, Tuple[float, float]]:
        """
        Predict ideal positions for all players

        Returns: Dict of {player_id: (x, y)}
        """
        predicted = {}
        for player in players:
            ideal_pos = self.positioning.calculate_ideal_position(player, match_state, formation)
            predicted[player.id] = ideal_pos
        return predicted

    def get_influence_map(self, player: 'Player', all_players: List['Player']) -> Dict:
        """
        Calculate influence/pressure map around player

        Returns: Dict with influence radius, direction, magnitude
        """
        teammates = [p for p in all_players if p.team == player.team and p.id != player.id]
        opponents = [p for p in all_players if p.team != player.team]

        # Influence zones
        support_distance = 15  # Teammates within this are supporting
        pressure_distance = 10  # Opponents within this are pressuring

        supporting = []
        for teammate in teammates:
            dist = ((teammate.x - player.x)**2 + (teammate.y - player.y)**2) ** 0.5
            if dist < support_distance:
                supporting.append(teammate)

        pressuring = []
        for opponent in opponents:
            dist = ((opponent.x - player.x)**2 + (opponent.y - player.y)**2) ** 0.5
            if dist < pressure_distance:
                pressuring.append(opponent)

        return {
            'supporting_teammates': len(supporting),
            'pressuring_opponents': len(pressuring),
            'support_distance': support_distance,
            'pressure_distance': pressure_distance,
        }


class MatchTacticalState:
    """Represents current tactical state of match"""

    def __init__(self):
        self.positions = {}  # {player_id: (x, y)}
        self.velocities = {}  # {player_id: (vx, vy)}
        self.possession = None  # "Home" or "Away"
        self.ball_position = (50, 35)
        self.score = {"Home": 0, "Away": 0}
        self.time_elapsed = 0  # seconds

    def update(self, players: List['Player'], ball_pos: Tuple[float, float],
              possession: Optional[str], score: Dict) -> None:
        """Update tactical state from current game state"""
        self.positions.clear()
        self.velocities.clear()

        for player in players:
            self.positions[player.id] = (player.x, player.y)
            self.velocities[player.id] = getattr(player, 'current_velocity', (0, 0))

        self.ball_position = ball_pos
        self.possession = possession
        self.score = score.copy()

    def to_dict(self) -> Dict:
        """Convert to dictionary for model inference"""
        return {
            'positions': self.positions,
            'velocities': self.velocities,
            'possession': self.possession,
            'ball_position': self.ball_position,
            'score': self.score,
            'time_elapsed': self.time_elapsed,
        }
