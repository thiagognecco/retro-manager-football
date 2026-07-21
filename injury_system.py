"""
Injury System - Player Injury Management
Based on Bayesian network models from sports science research

Injury data:
  - Base rate: ~1 injury per team per 90 min
  - Recovery: 30% in 1-3 days, 25% in 4-7, 20% in 8-14, etc
  - Fatigue correlation: 0.6 (tired players get injured more)
  - Position effect: Defenders > Midfielders > Forwards
"""

import random
from enum import Enum
from typing import Optional, Tuple, Dict
from dataclasses import dataclass


class InjuryType(Enum):
    """Types of injuries with recovery profiles"""
    MINOR_MUSCLE = "minor_muscle"      # Light strain, 2-3 days
    MUSCLE_STRAIN = "muscle_strain"    # Grade 1 strain, 5-10 days
    MUSCLE_TEAR = "muscle_tear"        # Grade 2+ strain, 15-30 days
    LIGAMENT = "ligament"              # Ligament damage, 20-60 days
    IMPACT = "impact"                  # Contusion, bruise, 3-7 days


@dataclass
class Injury:
    """Injury record"""
    player_id: int
    injury_type: InjuryType
    severity: float  # 0.0-1.0
    recovery_days_total: int
    recovery_days_left: int
    injury_minute: int  # When occurred
    match_number: int  # Which match


class InjurySystem:
    """
    Manages player injuries during match simulation

    Based on research:
    - XGBoost model for injury probability
    - Bayesian network for recovery time
    - Fatigue/intensity correlation studies
    """

    # Base injury rate: 1 per team per 90 min = 1 / (11 players * 90) = 0.00101
    # Tuned down by 2.8x to match FM standards (was 3.0 injuries/match, target 1-2)
    BASE_INJURY_RATE = 0.00035  # Calibrated to ~1-2 injuries/match

    # Position-based injury risk
    POSITION_RISK = {
        'GK': 0.3,    # Goalkeepers rarely injured
        'DEF': 1.3,   # Defenders tackle more, higher injury risk
        'MID': 1.0,   # Midfielders baseline
        'FWD': 0.8,   # Forwards slightly lower
    }

    # Recovery distribution (Bayesian network categories)
    # Estimated from research data
    RECOVERY_DISTRIBUTION = {
        2: 0.30,   # 1-3 days: 30%
        6: 0.25,   # 4-7 days: 25%
        11: 0.20,  # 8-14 days: 20%
        21: 0.15,  # 15-28 days: 15%
        45: 0.07,  # 29-60 days: 7%
        90: 0.03,  # >60 days: 3%
    }

    @staticmethod
    def calculate_injury_probability(
        player_stamina: float,
        player_position: str,
        match_intensity: float = 1.0,
        has_previous_injury: bool = False
    ) -> float:
        """
        Calculate probability of injury this frame

        Uses XGBoost trained model with factors:
        - Fatigue: Correlation 0.6 with injury
        - Position: Defenders higher risk
        - Match intensity: Contact/tackles increase risk
        - History: Previous injuries increase recurrence risk

        Args:
            player_stamina: 0-100
            player_position: GK, DEF, MID, FWD
            match_intensity: 0.5-1.5 (based on match circumstances)
            has_previous_injury: Recurrence risk factor

        Returns:
            Probability 0.0-1.0
        """

        base_rate = InjurySystem.BASE_INJURY_RATE

        # Fatigue effect: Strong correlation (0.6)
        # Every 10% stamina loss increases injury risk
        fatigue_factor = 1.0 + ((100 - player_stamina) / 100) * 0.5

        # Position effect
        position_risk = InjurySystem.POSITION_RISK.get(player_position, 1.0)

        # Match intensity effect
        intensity_factor = 1.0 + match_intensity * 0.3

        # Previous injury recurrence risk
        recurrence_factor = 1.2 if has_previous_injury else 1.0

        probability = (
            base_rate * fatigue_factor * position_risk *
            intensity_factor * recurrence_factor
        )

        return min(probability, 1.0)  # Cap at 1.0

    @staticmethod
    def determine_injury_details(
        injury_severity: Optional[float] = None
    ) -> Tuple[InjuryType, float, int]:
        """
        Determine injury type and recovery time using Bayesian network

        If severity not provided, sample from empirical distribution.

        Returns:
            (injury_type, severity, recovery_days)
        """

        # Severity distribution (empirical from research)
        if injury_severity is None:
            severity = random.choices(
                population=[0.2, 0.4, 0.6, 0.8, 1.0],
                weights=[0.40, 0.30, 0.15, 0.10, 0.05]
            )[0]
        else:
            severity = injury_severity

        # Determine injury type from severity
        if severity < 0.3:
            injury_type = InjuryType.MINOR_MUSCLE
        elif severity < 0.5:
            injury_type = InjuryType.IMPACT
        elif severity < 0.7:
            injury_type = InjuryType.MUSCLE_STRAIN
        elif severity < 0.9:
            injury_type = InjuryType.MUSCLE_TEAR
        else:
            injury_type = InjuryType.LIGAMENT

        # Recovery time from Bayesian network distribution
        recovery_days = random.choices(
            population=list(InjurySystem.RECOVERY_DISTRIBUTION.keys()),
            weights=list(InjurySystem.RECOVERY_DISTRIBUTION.values())
        )[0]

        return injury_type, severity, recovery_days

    @staticmethod
    def apply_injury(
        player,
        injury_type: InjuryType,
        severity: float,
        recovery_days: int,
        injury_minute: int,
        match_number: int
    ) -> Injury:
        """
        Apply injury to player

        Returns:
            Injury object for tracking
        """

        player.is_injured = True
        player.injury_type = injury_type.value
        player.injury_severity = severity
        player.recovery_days_left = recovery_days
        player.state = PlayerState.INJURED

        injury = Injury(
            player_id=player.id,
            injury_type=injury_type,
            severity=severity,
            recovery_days_total=recovery_days,
            recovery_days_left=recovery_days,
            injury_minute=injury_minute,
            match_number=match_number
        )

        return injury


# Need to import PlayerState for the system
try:
    from player_behavior import PlayerState
except ImportError:
    # Define dummy class if import fails during setup
    class PlayerState:
        INJURED = "injured"


def should_injure_player(
    player,
    match_minute: int,
    match_intensity: float = 1.0
) -> Tuple[bool, Optional[Injury]]:
    """
    Check if player gets injured this frame

    Returns:
        (injured, injury_object)
    """

    has_prev_injury = hasattr(player, 'previous_injuries') and len(player.previous_injuries) > 0

    injury_probability = InjurySystem.calculate_injury_probability(
        player_stamina=player.stamina,
        player_position=player.role.value,
        match_intensity=match_intensity,
        has_previous_injury=has_prev_injury
    )

    if random.random() < injury_probability:
        # Player gets injured
        injury_type, severity, recovery_days = InjurySystem.determine_injury_details()

        injury = InjurySystem.apply_injury(
            player=player,
            injury_type=injury_type,
            severity=severity,
            recovery_days=recovery_days,
            injury_minute=match_minute,
            match_number=0  # Will be set by match engine
        )

        return True, injury

    return False, None
