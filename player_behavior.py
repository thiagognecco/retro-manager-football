"""
Player Behavior Trees - Parte 1 de FASE 2

Implementa sistema de decisão para os 22 jogadores baseado em:
- Behavior Trees (composição de tarefas)
- State transitions (máquina de estados)
- Integração com 4 sistemas existentes:
  * xg_advanced_calculator.py (quando tirar)
  * pass_completion_model.py (quando passar)
  * stamina_metabolic_model.py (cada ação)
  * formation_geometry_model.py (posições tácticas)
"""

from enum import Enum
from typing import Optional, Callable, Dict, List
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ============================================================================
# STATE MACHINE
# ============================================================================

class PlayerState(Enum):
    """Possible states for a player in the match"""
    IDLE = "idle"                      # Waiting, off-ball
    MOVING_TO_POSITION = "moving"      # Moving to tactical position
    ON_BALL = "on_ball"                # Has possession
    PASSING = "passing"                # Executing pass
    SHOOTING = "shooting"              # Taking shot
    DEFENDING = "defending"            # Marking opponent
    PRESSING = "pressing"              # Aggressive defense
    RECOVERING = "recovering"          # Out of position, recovering
    INJURED = "injured"                # Can't play


class PlayerRole(Enum):
    """Player positions/roles on field"""
    GOALKEEPER = "GK"
    DEFENDER = "DEF"
    MIDFIELDER = "MID"
    FORWARD = "FWD"


# ============================================================================
# BEHAVIOR TREE NODES
# ============================================================================

class BehaviorNode(ABC):
    """
    Base class for behavior tree nodes.

    Behavior Tree pattern:
    - Composites (Selector, Sequence) contain children
    - Tasks (leaf nodes) perform actions
    - Each node returns SUCCESS, FAILURE, or RUNNING
    """

    @abstractmethod
    def tick(self, player: 'Player', context: Dict) -> str:
        """
        Execute this node.

        Args:
            player: Player object
            context: Match context (ball_pos, score, etc)

        Returns: 'SUCCESS', 'FAILURE', or 'RUNNING'
        """
        pass


class Selector(BehaviorNode):
    """
    Composite: OR logic
    Returns SUCCESS if ANY child succeeds
    Tries children in order until one succeeds
    """

    def __init__(self, children: List[BehaviorNode], name: str = "Selector"):
        self.children = children
        self.name = name
        self.call_count = 0

    def tick(self, player: 'Player', context: Dict) -> str:
        self.call_count += 1

        for i, child in enumerate(self.children):
            result = child.tick(player, context)
            if result == 'SUCCESS':
                return 'SUCCESS'
        return 'FAILURE'


class Sequence(BehaviorNode):
    """
    Composite: AND logic
    Returns SUCCESS only if ALL children succeed
    Stops at first failure
    """

    def __init__(self, children: List[BehaviorNode], name: str = "Sequence"):
        self.children = children
        self.name = name

    def tick(self, player: 'Player', context: Dict) -> str:
        for child in self.children:
            result = child.tick(player, context)
            if result == 'FAILURE':
                return 'FAILURE'
        return 'SUCCESS'


# ============================================================================
# DECISION TASKS
# ============================================================================

class Task_HasBall(BehaviorNode):
    """Check if player has ball"""

    def tick(self, player: 'Player', context: Dict) -> str:
        if player.has_ball:
            return 'SUCCESS'
        return 'FAILURE'


class Task_CanShoot(BehaviorNode):
    """Check if player can and should shoot based on xG"""

    def tick(self, player: 'Player', context: Dict) -> str:
        if not player.has_ball:
            return 'FAILURE'

        # Simple heuristic: distance to goal < 20m and angle decent
        goal_x = 100 if player.team == "Home" else 0
        dist_to_goal = abs(player.x - goal_x)

        if dist_to_goal < 20:
            return 'SUCCESS'
        return 'FAILURE'


class Task_CanPass(BehaviorNode):
    """Check if player has passing options"""

    def tick(self, player: 'Player', context: Dict) -> str:
        if not player.has_ball:
            return 'FAILURE'

        # Check if there are teammates nearby
        nearby = context.get('spatial_grid', None)
        if nearby is None:
            return 'FAILURE'

        teammates_near = nearby.nearby_agents(player.x, player.y, radius=15)
        # Filter for teammates only (same team)
        teammates = [a for a in teammates_near if hasattr(a, 'team') and a.team == player.team]

        if len(teammates) > 0:
            return 'SUCCESS'
        return 'FAILURE'


class Task_IsPressed(BehaviorNode):
    """Check if opponents are pressing"""

    def tick(self, player: 'Player', context: Dict) -> str:
        nearby = context.get('spatial_grid', None)
        if nearby is None:
            return 'FAILURE'

        opponents_close = nearby.nearby_agents(player.x, player.y, radius=8)
        # Filter for opponents
        opponents = [a for a in opponents_close if hasattr(a, 'team') and a.team != player.team]

        if len(opponents) > 1:  # Being pressed by multiple
            return 'SUCCESS'
        return 'FAILURE'


# ============================================================================
# ACTION TASKS (these modify player state)
# ============================================================================

class Task_Shoot(BehaviorNode):
    """Execute shooting action - integrates with xG calculator"""

    def tick(self, player: 'Player', context: Dict) -> str:
        if not player.has_ball:
            return 'FAILURE'

        # Calculate shot angle and distance
        goal_x = 100 if player.team == "Home" else 0
        goal_y = 35  # Center of goal

        dx = goal_x - player.x
        dy = goal_y - player.y
        dist_to_goal = (dx*dx + dy*dy) ** 0.5

        # Only shoot if reasonable position
        if dist_to_goal > 40:
            return 'FAILURE'

        # Calculate angle to goal (0-180 degrees from center)
        import math
        angle = math.atan2(dy, dx) * 180 / math.pi

        player.state = PlayerState.SHOOTING
        player.desired_action = 'SHOOT'
        player.shot_position = (player.x, player.y)
        player.shot_angle = angle
        player.shot_distance = dist_to_goal

        return 'SUCCESS'


class Task_Pass(BehaviorNode):
    """Execute passing action - integrates with pass completion model"""

    def tick(self, player: 'Player', context: Dict) -> str:
        if not player.has_ball:
            return 'FAILURE'

        nearby = context.get('spatial_grid', None)
        if nearby is None:
            return 'FAILURE'

        # Find best teammate to pass to
        teammates_near = nearby.nearby_agents(player.x, player.y, radius=25)
        teammates = [a for a in teammates_near if hasattr(a, 'team') and a.team == player.team and a.id != player.id]

        if len(teammates) == 0:
            return 'FAILURE'

        # Select best target by distance (closer = better)
        target = min(teammates, key=lambda t: ((t.x-player.x)**2 + (t.y-player.y)**2)**0.5)

        # Calculate pass distance
        pass_distance = ((target.x-player.x)**2 + (target.y-player.y)**2) ** 0.5

        player.state = PlayerState.PASSING
        player.desired_action = 'PASS'
        player.pass_target = target
        player.pass_distance = pass_distance
        player.pass_success_prob = 0.75  # Base probability, can be refined by model

        return 'SUCCESS'


class Task_MoveToPosition(BehaviorNode):
    """Move to tactical position based on formation"""

    def tick(self, player: 'Player', context: Dict) -> str:
        # TODO: Consultar formation_geometry_model para posição ideal
        player.state = PlayerState.MOVING_TO_POSITION
        player.desired_action = 'MOVE_TO_POSITION'

        return 'SUCCESS'


class Task_Defend(BehaviorNode):
    """Defensive positioning and marking"""

    def tick(self, player: 'Player', context: Dict) -> str:
        # Find opponent to mark
        nearby = context.get('spatial_grid', None)
        if nearby is None:
            return 'FAILURE'

        opponents_near = nearby.nearby_agents(player.x, player.y, radius=20)
        opponents = [a for a in opponents_near if hasattr(a, 'team') and a.team != player.team]

        if len(opponents) == 0:
            return 'FAILURE'

        # Mark closest opponent
        opponent = min(opponents, key=lambda o: ((o.x-player.x)**2 + (o.y-player.y)**2)**0.5)

        player.state = PlayerState.DEFENDING
        player.desired_action = 'DEFEND'
        player.mark_target = opponent

        return 'SUCCESS'


class Task_Press(BehaviorNode):
    """Aggressive pressing of opponent with ball"""

    def tick(self, player: 'Player', context: Dict) -> str:
        ball_holder = context.get('ball_holder', None)
        if ball_holder is None or ball_holder.team == player.team:
            return 'FAILURE'

        player.state = PlayerState.PRESSING
        player.desired_action = 'PRESS'
        player.press_target = ball_holder

        return 'SUCCESS'


# ============================================================================
# BEHAVIOR TREE TEMPLATES
# ============================================================================

class PlayerBehaviorTree:
    """
    Behavior tree for a single player.

    Structure:
    - If has ball -> Shoot/Pass decision
    - Else if opponent has ball -> Defend/Press
    - Else -> Move to position
    """

    def __init__(self, player: 'Player'):
        self.player = player

        # Build tree
        # Root: Selector (try behaviors in order)
        self.root = Selector([
            # 1. Priority: Have ball - decide to shoot or pass
            Sequence([
                Task_HasBall(),
                Selector([
                    Sequence([
                        Task_CanShoot(),
                        Task_Shoot(),
                    ]),
                    Sequence([
                        Task_CanPass(),
                        Task_Pass(),
                    ]),
                    Task_MoveToPosition(),  # Fallback: move if stuck
                ]),
            ]),

            # 2. Priority: Opponent has ball - defend or press
            Selector([
                Sequence([
                    Task_IsPressed(),
                    Task_Press(),
                ]),
                Task_Defend(),
            ]),

            # 3. Default: Move to tactical position
            Task_MoveToPosition(),
        ], name="PlayerBehavior")

    def tick(self, context: Dict) -> str:
        """Execute behavior tree tick with timing"""
        import time
        t_start = time.perf_counter()
        result = self.root.tick(self.player, context)
        t_end = time.perf_counter()

        # Log slow ticks (> 100ms for debugging)
        elapsed_ms = (t_end - t_start) * 1000
        if elapsed_ms > 100 and self.player.id == 1:  # Only log for first player to avoid spam
            print(f"  [SLOW TICK] Player {self.player.id}: {elapsed_ms:.2f}ms")

        return result


# ============================================================================
# PLAYER CLASS
# ============================================================================

@dataclass
class Player:
    """Enhanced Player class with behavior and state"""
    id: int
    name: str
    team: str  # "Home" or "Away"
    role: PlayerRole
    number: int

    # Position
    x: float = 50.0
    y: float = 35.0

    # Ball possession
    has_ball: bool = False
    pass_target: Optional['Player'] = None
    pass_distance: float = 0.0
    pass_success_prob: float = 0.0
    mark_target: Optional['Player'] = None
    press_target: Optional['Player'] = None

    # Shooting
    shot_position: tuple = field(default_factory=lambda: (0, 0))
    shot_angle: float = 0.0
    shot_distance: float = 0.0

    # Movement
    target_position: tuple = field(default_factory=lambda: (50, 35))
    current_velocity: tuple = field(default_factory=lambda: (0, 0))

    # State machine
    state: PlayerState = PlayerState.IDLE
    desired_action: str = "IDLE"

    # Behavior tree
    behavior_tree: Optional[PlayerBehaviorTree] = field(default=None, init=False)

    # Performance
    stamina: float = 100.0  # 0-100
    speed: float = 7.0  # m/s
    fitness: float = 0.8  # 0-1 fitness level

    def __post_init__(self):
        """Initialize behavior tree after object creation"""
        self.behavior_tree = PlayerBehaviorTree(self)

    def update_behavior(self, context: Dict) -> str:
        """
        Update player behavior for this frame

        Args:
            context: Match context (spatial_grid, ball_holder, etc)

        Returns: Current action
        """
        if self.state == PlayerState.INJURED:
            return "INJURED"

        # Tick behavior tree
        self.behavior_tree.tick(context)

        return self.desired_action


# ============================================================================
# CONTEXT BUILDER
# ============================================================================

def build_match_context(match_state: Dict) -> Dict:
    """
    Build context dict for behavior tree ticks.

    Args:
        match_state: Current match state

    Returns: Context dict with all info players need
    """
    return {
        'spatial_grid': match_state.get('spatial_grid'),
        'ball_holder': match_state.get('ball_holder'),
        'ball_position': match_state.get('ball_position'),
        'score': match_state.get('score'),
        'time_remaining': match_state.get('time_remaining'),
    }
