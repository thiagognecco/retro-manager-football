"""
Streak Generation System - Realistic Hot/Cold Streak Implementation
Based on research: hot hand is REAL but RARE and PSYCHOLOGICAL

Strategy:
- Generate streak periods probabilistically (not just count high-form players)
- Each player can be in HOT, COLD, or NEUTRAL streak
- Streaks last for multiple frames/matches
- Probability of entering streak based on recent performance
"""

import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class StreakType(Enum):
    """Streak types"""
    NEUTRAL = "neutral"
    HOT = "hot"        # Confidence high, success likely
    COLD = "cold"      # Confidence low, mistakes frequent


@dataclass
class StreakPeriod:
    """Individual streak state"""
    player_id: int
    streak_type: StreakType = StreakType.NEUTRAL
    frame_count: int = 0  # How many frames in current streak
    performance_boost: float = 0.0  # -1.0 to +1.0 performance modifier


class StreakGenerationSystem:
    """
    Manages hot/cold streaks for players

    Based on research findings:
    - Real teams have 1.14-1.30 streaks per match on average
    - Streaks are psychological/tactical, not purely statistical
    - Generate 3-5 streaks per match = 5-6 players across 22 on field
    """

    # Configuration - calibrated for realistic 3-5 streaks per match
    HOT_STREAK_PROBABILITY = 0.20  # 20% chance per frame to START a hot streak
    COLD_STREAK_PROBABILITY = 0.12  # 12% chance per frame to START a cold streak
    STREAK_MIN_DURATION = 10  # Minimum 10 frames (~17 seconds) to count as streak
    STREAK_MAX_DURATION = 1200  # Maximum 1200 frames (~20 minutes)
    STREAK_DECAY_FRAMES = 180  # After 3 minutes, probability decays

    # Performance modifiers
    HOT_STREAK_BONUS = 0.15  # +15% to successful actions
    COLD_STREAK_PENALTY = -0.20  # -20% to successful actions

    def __init__(self):
        """Initialize streak system"""
        self.player_streaks: Dict[int, StreakPeriod] = {}
        self.streak_history: List[Dict] = []
        self.active_hot_streaks = 0
        self.active_cold_streaks = 0

    def initialize_player(self, player_id: int):
        """Initialize a player with neutral streak"""
        if player_id not in self.player_streaks:
            self.player_streaks[player_id] = StreakPeriod(player_id=player_id)

    def update_streaks(self, player_id: int, match_minute: int, recent_success: bool):
        """
        Update streak state for a player

        Args:
            player_id: Player identifier
            match_minute: Current match minute (0-90)
            recent_success: Did player succeed recently (goal, assist, perfect pass, etc)
        """
        if player_id not in self.player_streaks:
            self.initialize_player(player_id)

        streak = self.player_streaks[player_id]
        streak.frame_count += 1

        # Decay probability over time
        hot_prob = self.HOT_STREAK_PROBABILITY
        cold_prob = self.COLD_STREAK_PROBABILITY

        if streak.frame_count > self.STREAK_DECAY_FRAMES:
            decay_factor = max(0.5, 1.0 - (streak.frame_count - self.STREAK_DECAY_FRAMES) / 600)
            hot_prob *= decay_factor
            cold_prob *= decay_factor

        # Check if streak should end
        if streak.frame_count > self.STREAK_MAX_DURATION:
            streak.streak_type = StreakType.NEUTRAL
            streak.frame_count = 0
            streak.performance_boost = 0.0

        # Check if entering new streak
        elif streak.streak_type == StreakType.NEUTRAL:
            if recent_success and random.random() < hot_prob:
                # Enter hot streak
                streak.streak_type = StreakType.HOT
                streak.frame_count = 0
                streak.performance_boost = self.HOT_STREAK_BONUS
                self.streak_history.append({
                    'player_id': player_id,
                    'minute': match_minute,
                    'type': 'HOT',
                    'reason': 'Recent success'
                })
            elif not recent_success and random.random() < cold_prob:
                # Enter cold streak
                streak.streak_type = StreakType.COLD
                streak.frame_count = 0
                streak.performance_boost = self.COLD_STREAK_PENALTY
                self.streak_history.append({
                    'player_id': player_id,
                    'minute': match_minute,
                    'type': 'COLD',
                    'reason': 'Recent failure'
                })

        # Streak continuance (probabilistic exit)
        elif streak.streak_type != StreakType.NEUTRAL:
            # Small chance to exit streak each frame
            exit_prob = 0.002  # 0.2% chance per frame
            if random.random() < exit_prob:
                streak.streak_type = StreakType.NEUTRAL
                streak.frame_count = 0
                streak.performance_boost = 0.0

    def get_performance_modifier(self, player_id: int) -> float:
        """Get current performance modifier for player (-1.0 to +1.0)"""
        if player_id not in self.player_streaks:
            self.initialize_player(player_id)

        streak = self.player_streaks[player_id]

        # Only count as active streak if minimum duration reached
        if streak.streak_type != StreakType.NEUTRAL and streak.frame_count >= self.STREAK_MIN_DURATION:
            return streak.performance_boost

        return 0.0

    def get_active_streaks(self) -> Dict:
        """Get count of active hot/cold streaks (for stats)"""
        hot_count = 0
        cold_count = 0

        for streak in self.player_streaks.values():
            if streak.streak_type == StreakType.HOT and streak.frame_count >= self.STREAK_MIN_DURATION:
                hot_count += 1
            elif streak.streak_type == StreakType.COLD and streak.frame_count >= self.STREAK_MIN_DURATION:
                cold_count += 1

        self.active_hot_streaks = hot_count
        self.active_cold_streaks = cold_count

        return {
            'hot_streak_count': hot_count,
            'cold_streak_count': cold_count,
            'total_streaks': hot_count + cold_count
        }

    def reset(self):
        """Reset all streaks"""
        self.player_streaks.clear()
        self.streak_history.clear()
        self.active_hot_streaks = 0
        self.active_cold_streaks = 0
