"""
TIER 2: Set Pieces System - Corners, Free Kicks, Throw-ins
Adds realistic set piece mechanics based on Premier League 2025-26 data

Statistics:
- 25% of all goals from set pieces
- 55-60% of set-piece goals from corners
- Corner → goal rate: 5.3% inswinger, 3.6% outswinger
- Free kick → goal rate: 0.1-0.5%
- ~10-12 corners per match
- ~3-4 free kicks per match
- ~25-30 throw-ins per match
"""

from enum import Enum
from typing import Optional, Tuple, List
from dataclasses import dataclass, field
import random
import math


class SetPieceType(Enum):
    """Types of set pieces"""
    CORNER_INSWINGER = "corner_inswinger"
    CORNER_OUTSWINGER = "corner_outswinger"
    FREE_KICK_DIRECT = "free_kick_direct"
    FREE_KICK_INDIRECT = "free_kick_indirect"
    THROW_IN = "throw_in"


@dataclass
class SetPieceOpportunity:
    """Represents a set piece opportunity"""
    piece_type: SetPieceType
    time: int  # Match minute
    team: str  # "Home" or "Away"
    position: Tuple[float, float]  # (x, y) on field
    shooter_id: Optional[int] = None
    aerial_threat_id: Optional[int] = None
    xg: float = 0.0
    resulted_in_goal: bool = False
    goal_scorer_id: Optional[int] = None


@dataclass
class SetPieceStats:
    """Statistics for set pieces"""
    total_corners: int = 0
    corners_from_play: int = 0
    corners_scored: int = 0
    total_free_kicks: int = 0
    free_kicks_scored: int = 0
    throw_ins: int = 0
    set_piece_goals: int = 0
    set_piece_xg: float = 0.0
    set_piece_opportunities: List[SetPieceOpportunity] = field(default_factory=list)


class SetPiecesSystem:
    """
    Manages set piece generation and resolution

    Handles:
    - Corner kick detection and execution
    - Free kick detection and execution
    - Throw-in detection (low impact)
    - XG calculation for each piece
    """

    def __init__(self):
        """Initialize set pieces system"""
        # Constants from Premier League data
        self.CORNERS_PER_MATCH = 11  # Average
        self.FREE_KICKS_PER_MATCH = 3.5
        self.THROW_INS_PER_MATCH = 27

        # Goal conversion rates (real data)
        self.CORNER_INSWINGER_GOAL_RATE = 0.053  # 5.3%
        self.CORNER_OUTSWINGER_GOAL_RATE = 0.036  # 3.6%
        self.FREE_KICK_GOAL_RATE = 0.002  # 0.2% overall
        self.THROW_IN_GOAL_RATE = 0.0005  # Very rare

        # XG values
        self.CORNER_XG = 0.04  # Typical corner = 0.04 xG
        self.FREE_KICK_XG = 0.02  # Typical free kick = 0.02 xG
        self.THROW_IN_XG = 0.001

        self.stats = SetPieceStats()

    def detect_corner_opportunity(
        self,
        ball_position: Tuple[float, float],
        last_touch_by: str,  # "Home" or "Away"
        last_touch_player_id: int,
    ) -> Optional[SetPieceOpportunity]:
        """
        Detect if ball going out creates a corner

        Corner: Ball goes out behind goal line, last touched by defending team
        Returns corner opportunity if detected
        """
        x, y = ball_position

        # Check if out of bounds behind goal
        is_behind_goal_home = x < 0 and (y > 5 and y < 65)  # Home goal
        is_behind_goal_away = x > 100 and (y > 5 and y < 65)  # Away goal

        if not (is_behind_goal_home or is_behind_goal_away):
            return None

        # Determine attacking team
        attacking_team = "Away" if is_behind_goal_home else "Home"

        if attacking_team == last_touch_by:
            # Own player touched last = throw-in, not corner
            return None

        # Corner awarded
        corner_type = self._determine_corner_type()
        xg = self.CORNER_XG * self._corner_quality_modifier(corner_type)

        opportunity = SetPieceOpportunity(
            piece_type=corner_type,
            time=0,  # Will be set by caller
            team=attacking_team,
            position=ball_position,
            xg=xg,
        )

        self.stats.total_corners += 1
        self.stats.set_piece_xg += xg
        return opportunity

    def detect_free_kick_opportunity(
        self,
        foul_position: Tuple[float, float],
        attacking_team: str,  # "Home" or "Away"
        fouling_team: str,
        distance_from_goal: float,  # meters
    ) -> Optional[SetPieceOpportunity]:
        """
        Detect free kick opportunity from foul

        Only dangerous free kicks create xG
        Distance matters: closer = higher xG
        """
        x, y = foul_position

        # Only count free kicks in attacking zone (within 35m of goal)
        if distance_from_goal > 35:
            return None

        # Direct vs indirect
        is_direct = distance_from_goal < 15  # Within penalty area
        piece_type = (
            SetPieceType.FREE_KICK_DIRECT
            if is_direct
            else SetPieceType.FREE_KICK_INDIRECT
        )

        # XG decreases with distance
        # Close: 0.04, Medium: 0.02, Far: 0.01
        base_xg = self.FREE_KICK_XG * self._free_kick_distance_modifier(
            distance_from_goal
        )

        opportunity = SetPieceOpportunity(
            piece_type=piece_type,
            time=0,  # Will be set by caller
            team=attacking_team,
            position=foul_position,
            xg=base_xg,
        )

        self.stats.total_free_kicks += 1
        self.stats.set_piece_xg += base_xg
        return opportunity

    def resolve_corner(
        self,
        opportunity: SetPieceOpportunity,
        attacking_players: List,
        defending_players: List,
        match_intensity: float = 1.0,
    ) -> Tuple[bool, Optional[int]]:
        """
        Resolve a corner kick

        Returns: (goal_scored: bool, goal_scorer_id: Optional[int])
        """
        if opportunity.piece_type == SetPieceType.CORNER_INSWINGER:
            goal_rate = self.CORNER_INSWINGER_GOAL_RATE
        else:
            goal_rate = self.CORNER_OUTSWINGER_GOAL_RATE

        # Apply intensity modifier
        goal_rate *= (0.8 + match_intensity * 0.4)

        # Apply aerial threat modifier
        aerial_bonus = 0.0
        if opportunity.aerial_threat_id and attacking_players:
            # Find aerial threat player
            for p in attacking_players:
                if p.id == opportunity.aerial_threat_id:
                    # Player with high heading ability
                    if hasattr(p, "heading"):
                        aerial_bonus = p.heading * 0.01
                    break

        goal_rate *= (1.0 + aerial_bonus)

        # Check if goal
        if random.random() < goal_rate:
            # Select goal scorer (typically aerial threat or nearest forward)
            goal_scorer = self._select_set_piece_scorer(
                attacking_players, opportunity.aerial_threat_id
            )

            if goal_scorer:
                self.stats.set_piece_goals += 1
                self.stats.corners_scored += 1
                opportunity.resulted_in_goal = True
                opportunity.goal_scorer_id = goal_scorer.id
                return True, goal_scorer.id

        self.stats.corners_from_play += 1
        return False, None

    def resolve_free_kick(
        self,
        opportunity: SetPieceOpportunity,
        shooter: Optional["Player"] = None,
        is_wall_present: bool = True,
    ) -> Tuple[bool, Optional[int]]:
        """
        Resolve a free kick

        Direct free kicks can score directly
        Wall reduces goal probability by ~30%
        """
        if opportunity.piece_type == SetPieceType.FREE_KICK_DIRECT:
            base_rate = self.FREE_KICK_GOAL_RATE * 2  # Direct is more dangerous

            # Wall effect
            if is_wall_present:
                base_rate *= 0.7

            # Shooter quality
            if shooter and hasattr(shooter, "free_kick_ability"):
                base_rate *= (1.0 + shooter.free_kick_ability * 0.05)

            if random.random() < base_rate:
                self.stats.set_piece_goals += 1
                self.stats.free_kicks_scored += 1
                opportunity.resulted_in_goal = True
                if shooter:
                    opportunity.goal_scorer_id = shooter.id
                    return True, shooter.id
                return True, None

        else:
            # Indirect free kick - low probability
            indirect_rate = self.FREE_KICK_GOAL_RATE * 0.5
            if random.random() < indirect_rate:
                self.stats.set_piece_goals += 1
                self.stats.free_kicks_scored += 1
                opportunity.resulted_in_goal = True
                return True, None

        self.stats.total_free_kicks += 1
        return False, None

    def resolve_throw_in(
        self,
        throw_in_team: str,
        throw_in_position: Tuple[float, float],
    ) -> Tuple[bool, Optional[int]]:
        """
        Resolve a throw-in

        Very low goal probability, but can lead to possession retention
        Mostly affects tactical positioning
        """
        self.stats.throw_ins += 1

        # Throw-in almost never results in direct goal
        if random.random() < self.THROW_IN_GOAL_RATE:
            self.stats.set_piece_goals += 1
            return True, None

        return False, None

    def _determine_corner_type(self) -> SetPieceType:
        """Randomly determine inswinger vs outswinger"""
        # Inswingers are more common and dangerous
        if random.random() < 0.65:
            return SetPieceType.CORNER_INSWINGER
        return SetPieceType.CORNER_OUTSWINGER

    def _corner_quality_modifier(self, corner_type: SetPieceType) -> float:
        """Get quality modifier for corner type"""
        if corner_type == SetPieceType.CORNER_INSWINGER:
            return 1.3  # More dangerous
        return 0.9  # Outswingers less dangerous

    def _free_kick_distance_modifier(self, distance_from_goal: float) -> float:
        """XG modifier based on distance from goal"""
        if distance_from_goal < 10:  # Penalty box
            return 2.0
        elif distance_from_goal < 18:  # D-area
            return 1.5
        elif distance_from_goal < 25:
            return 1.0
        else:  # Far free kick
            return 0.5

    def _select_set_piece_scorer(
        self,
        attacking_players: List,
        aerial_threat_id: Optional[int] = None,
    ) -> Optional["Player"]:
        """Select most likely goal scorer from set piece"""
        if not attacking_players:
            return None

        # Prefer aerial threat if available
        if aerial_threat_id:
            for p in attacking_players:
                if p.id == aerial_threat_id:
                    return p

        # Otherwise pick highest-rated forward
        forwards = [p for p in attacking_players if hasattr(p, "role") and "FWD" in str(p.role)]
        if forwards:
            return max(forwards, key=lambda p: getattr(p, "overall_rating", 0))

        # Fallback to any player
        return attacking_players[0]

    def get_stats(self) -> SetPieceStats:
        """Get current set piece statistics"""
        return self.stats

    def reset_stats(self):
        """Reset statistics (for new match)"""
        self.stats = SetPieceStats()


# Helper functions for integration

def should_have_corner(
    ball_position: Tuple[float, float],
    last_touch_by: str,
    last_touch_player_id: int,
) -> Tuple[bool, Optional[SetPieceOpportunity]]:
    """
    Check if current state should result in corner

    Returns: (is_corner: bool, opportunity: SetPieceOpportunity or None)
    """
    system = SetPiecesSystem()
    opportunity = system.detect_corner_opportunity(
        ball_position, last_touch_by, last_touch_player_id
    )
    return opportunity is not None, opportunity


def should_have_free_kick(
    foul_position: Tuple[float, float],
    attacking_team: str,
    fouling_team: str,
    distance_from_goal: float,
) -> Tuple[bool, Optional[SetPieceOpportunity]]:
    """
    Check if current foul results in dangerous free kick

    Returns: (is_dangerous_fk: bool, opportunity: SetPieceOpportunity or None)
    """
    system = SetPiecesSystem()
    opportunity = system.detect_free_kick_opportunity(
        foul_position, attacking_team, fouling_team, distance_from_goal
    )
    return opportunity is not None, opportunity
