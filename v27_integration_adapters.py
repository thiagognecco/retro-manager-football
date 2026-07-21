"""
v2.7 Integration Adapters - Bridge between v2.7 and v2.6 Systems

Integrates:
- xg_advanced_calculator.py
- pass_completion_model.py
- stamina_metabolic_model.py
- formation_geometry_model.py
"""

from typing import Tuple, Dict, Optional


class XGCalculatorAdapter:
    """Adapter for xG calculator integration"""

    @staticmethod
    def calculate_shot_xg(distance: float, angle: float, player_skill: float = 0.8) -> float:
        """
        Calculate expected goals (xG) for a shot

        Args:
            distance: Distance to goal in meters
            angle: Angle to goal (-90 to 90 degrees from center)
            player_skill: Player shooting skill 0-1

        Returns: xG value 0-1
        """
        # Base xG decreases exponentially with distance
        if distance < 0:
            distance = 0
        if distance > 50:
            return 0.001

        # Distance model
        xg_distance = 0.75 * (1 - (distance / 50) ** 1.5)

        # Angle model (better angle = higher xG)
        angle_factor = 1.0 - abs(angle) / 90.0  # 0-1, decreases away from center
        xg_angle = 0.3 + (0.7 * angle_factor)

        # Combine factors
        base_xg = xg_distance * xg_angle

        # Player skill factor
        final_xg = base_xg * (0.5 + (player_skill * 0.5))

        # Clamp to valid range
        return max(0.0, min(1.0, final_xg))


class PassCompletionAdapter:
    """Adapter for pass completion model"""

    @staticmethod
    def calculate_pass_success(distance: float, angle: float,
                              receiver_pressure: int = 0,
                              passer_skill: float = 0.8) -> float:
        """
        Calculate pass completion probability

        Args:
            distance: Pass distance in meters
            angle: Angle to receiver (-90 to 90 from straight ahead)
            receiver_pressure: Number of opponents pressuring receiver
            passer_skill: Passer skill 0-1

        Returns: Success probability 0-1
        """
        # Distance model (longer passes harder)
        if distance > 50:
            pass_distance_factor = 0.3
        elif distance > 30:
            pass_distance_factor = 0.65
        elif distance > 15:
            pass_distance_factor = 0.85
        else:
            pass_distance_factor = 0.95

        # Angle model (forward passes easier)
        angle_factor = 1.0 - abs(angle) / 180.0
        pass_angle_factor = 0.7 + (0.3 * angle_factor)

        # Pressure model
        if receiver_pressure == 0:
            pressure_factor = 1.0
        elif receiver_pressure == 1:
            pressure_factor = 0.85
        elif receiver_pressure == 2:
            pressure_factor = 0.65
        else:
            pressure_factor = 0.4

        # Skill factor
        skill_factor = 0.5 + (passer_skill * 0.5)

        # Combine all factors
        success_prob = (pass_distance_factor * pass_angle_factor *
                       pressure_factor * skill_factor)

        return max(0.0, min(1.0, success_prob))


class StaminaMetabolicAdapter:
    """Adapter for stamina/metabolic system"""

    @staticmethod
    def calculate_stamina_loss(velocity: float, intensity: str = "normal",
                              fitness: float = 0.8) -> float:
        """
        Calculate stamina loss per second

        Args:
            velocity: Current movement speed m/s
            intensity: "idle", "normal", "high", "sprint"
            fitness: Player fitness 0-1

        Returns: Stamina loss per second (0-1 scale per 100 stamina)
        """
        # Base loss on velocity
        velocity_factor = min(velocity / 10.0, 1.0)  # Max at 10 m/s

        # Intensity multiplier
        intensity_map = {
            "idle": 0.05,
            "normal": 0.15,
            "high": 0.25,
            "sprint": 0.35,
        }
        intensity_multiplier = intensity_map.get(intensity, 0.15)

        # Recovery factor (better fitness = slower loss)
        fitness_recovery = 0.5 + (fitness * 0.5)

        # Calculate loss
        loss_per_second = (velocity_factor * intensity_multiplier) / fitness_recovery

        return max(0.0, loss_per_second)

    @staticmethod
    def calculate_recovery(stamina_current: float, rest: bool = False) -> float:
        """
        Calculate stamina recovery per second

        Args:
            stamina_current: Current stamina 0-100
            rest: True if player is resting

        Returns: Stamina recovery per second
        """
        # Recovery is faster when stamina is low (natural recovery)
        if stamina_current < 30:
            base_recovery = 0.5
        elif stamina_current < 60:
            base_recovery = 0.3
        else:
            base_recovery = 0.1

        # Rest multiplier
        if rest:
            return base_recovery * 2.0

        return base_recovery


class FormationGeometryAdapter:
    """Adapter for formation geometry system"""

    FORMATION_POSITIONS = {
        "4-3-3": {
            "GK": [(5, 35)],
            "DEF": [(15, 15), (15, 25), (15, 45), (15, 55)],
            "MID": [(40, 20), (40, 35), (40, 50)],
            "FWD": [(70, 25), (70, 45), (75, 35)],
        },
        "4-2-3-1": {
            "GK": [(5, 35)],
            "DEF": [(15, 15), (15, 25), (15, 45), (15, 55)],
            "MID": [(35, 30), (35, 40), (50, 20), (50, 50)],
            "FWD": [(75, 35)],
        },
        "3-5-2": {
            "GK": [(5, 35)],
            "DEF": [(15, 20), (15, 35), (15, 50)],
            "MID": [(40, 15), (40, 35), (40, 55), (55, 25), (55, 45)],
            "FWD": [(75, 25), (75, 45)],
        },
    }

    @staticmethod
    def get_tactical_zone(position: Tuple[float, float],
                         formation: str = "4-3-3") -> str:
        """
        Determine tactical zone for position

        Args:
            position: (x, y) position
            formation: Formation name

        Returns: Zone name ("defensive", "midfield", "attacking")
        """
        x, y = position

        if x < 25:
            return "defensive"
        elif x < 70:
            return "midfield"
        else:
            return "attacking"

    @staticmethod
    def get_formation_positions(formation: str = "4-3-3",
                               team: str = "Home") -> Dict[str, list]:
        """
        Get baseline positions for formation

        Args:
            formation: Formation type
            team: "Home" or "Away"

        Returns: Dict of positions by role
        """
        base_positions = FormationGeometryAdapter.FORMATION_POSITIONS.get(
            formation,
            FormationGeometryAdapter.FORMATION_POSITIONS["4-3-3"]
        )

        if team == "Away":
            # Mirror for away team
            mirrored = {}
            for role, positions in base_positions.items():
                mirrored[role] = [(100 - x, y) for x, y in positions]
            return mirrored

        return base_positions

    @staticmethod
    def calculate_offside_position(ball_x: float, ball_y: float,
                                  defending_team: str = "Home") -> float:
        """
        Calculate offside line for defending team

        Args:
            ball_x: Ball x position
            defending_team: Team defending

        Returns: X coordinate of offside line
        """
        if defending_team == "Home":
            # Home team defending their goal at x=0
            return ball_x - 1  # Ball minus 1 meter
        else:
            # Away team defending their goal at x=100
            return ball_x + 1  # Ball plus 1 meter


class V27IntegrationBridge:
    """
    Main integration bridge between v2.7 and v2.6 systems

    Provides unified interface for accessing v2.6 models from v2.7 code
    """

    def __init__(self):
        self.xg = XGCalculatorAdapter()
        self.pass_model = PassCompletionAdapter()
        self.stamina = StaminaMetabolicAdapter()
        self.formation = FormationGeometryAdapter()

    def evaluate_shot(self, player: 'Player', ball_pos: Tuple[float, float]) -> float:
        """Evaluate quality of a shot"""
        goal_x = 100 if player.team == "Home" else 0
        goal_y = 35

        distance = ((player.x - goal_x) ** 2 + (player.y - goal_y) ** 2) ** 0.5
        angle = self._calculate_angle(player.x, player.y, goal_x, goal_y)

        return self.xg.calculate_shot_xg(distance, angle, player.fitness)

    def evaluate_pass(self, passer: 'Player', receiver: 'Player',
                     nearby_opponents: int = 0) -> float:
        """Evaluate quality of a pass"""
        distance = ((passer.x - receiver.x) ** 2 + (passer.y - receiver.y) ** 2) ** 0.5
        angle = self._calculate_angle(passer.x, passer.y, receiver.x, receiver.y)

        return self.pass_model.calculate_pass_success(
            distance, angle, nearby_opponents, passer.fitness
        )

    def update_player_stamina(self, player: 'Player', dt: float = 1.0) -> None:
        """Update player stamina"""
        velocity = (player.current_velocity[0] ** 2 + player.current_velocity[1] ** 2) ** 0.5

        # Determine intensity
        if velocity > 8:
            intensity = "sprint"
        elif velocity > 5:
            intensity = "high"
        elif velocity > 2:
            intensity = "normal"
        else:
            intensity = "idle"

        loss = self.stamina.calculate_stamina_loss(velocity, intensity, player.fitness)
        player.stamina = max(0, player.stamina - (loss * dt))

        # Recovery when not moving much
        if velocity < 1:
            recovery = self.stamina.calculate_recovery(player.stamina, rest=True)
            player.stamina = min(100, player.stamina + (recovery * dt))

    @staticmethod
    def _calculate_angle(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate angle between two points"""
        import math
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx) * 180 / math.pi
        # Normalize to -90 to 90
        if angle > 90:
            angle = 180 - angle
        elif angle < -90:
            angle = -180 - angle
        return angle


# Global integration bridge instance
integration_bridge = V27IntegrationBridge()
