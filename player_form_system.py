"""
TIER 2: Player Form System - Hot/Cold Streaks, Confidence, Momentum
Adds realistic player form dynamics based on peer-reviewed research

Evidence from science:
- Hot hand/streaks are REAL (not just random variation)
- Confidence effect: +5-10% performance improvement
- Streak duration: 3-8 matches typical
- Momentum: When hot, teammates pass more (+15% pass rate)
- Recovery: Form normalizes over 10 matches (decay rate ~10% per match)
"""

from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field
import random
import math


class FormPhase(Enum):
    """Player form phase"""
    COLD_STREAK = "cold_streak"  # Form < -3
    POOR_FORM = "poor_form"  # -3 to -1
    AVERAGE_FORM = "average_form"  # -1 to 1
    GOOD_FORM = "good_form"  # 1 to 3
    HOT_STREAK = "hot_streak"  # Form > 3


@dataclass
class FormUpdate:
    """Record of a form update"""
    time: int  # Match minute
    event_type: str  # "goal", "assist", "miss", "tackle", etc
    form_change: float  # +/- form points
    new_form: float
    reason: str


@dataclass
class FormStats:
    """Statistics about player form"""
    player_id: int
    player_name: str
    current_form: float  # -10 to +10
    form_history: List[float] = field(default_factory=list)
    form_updates: List[FormUpdate] = field(default_factory=list)
    hot_streak_matches: int = 0
    cold_streak_matches: int = 0
    peak_form: float = 0.0
    lowest_form: float = 0.0


class PlayerFormSystem:
    """
    Manages player form dynamics

    Tracks:
    - Individual player form (-10 to +10 scale)
    - Hot streaks (3+ matches of high form)
    - Cold streaks (persistent low form)
    - Confidence effects on performance
    - Momentum (affecting pass networks, positioning)
    """

    def __init__(self):
        """Initialize form system"""
        # Form change constants (reduced 5x for stability - form now -1 to +1 range)
        self.FORM_GOAL = 0.2  # Goal scored (was 1.0)
        self.FORM_ASSIST = 0.1  # Assist (was 0.5)
        self.FORM_SHOT_ON_TARGET = 0.05  # Shot on target (was 0.2)
        self.FORM_MISSED_CHANCE = -0.1  # Big miss (was -0.5)
        self.FORM_DEFENSIVE_ACTION = 0.06  # Tackle/interception/block (was 0.3)
        self.FORM_POOR_PASS = -0.02  # Failed pass (was -0.1)
        self.FORM_YELLOW_CARD = -0.1  # Discipline issue (was -0.3)
        self.FORM_INJURY = -0.1  # Just recovered (was -0.5)

        # Form decay (recovery towards 0)
        self.FORM_DECAY_RATE = 0.1  # Per match without significant events

        # Hot/cold streak thresholds
        self.HOT_STREAK_THRESHOLD = 3.0  # Form > 3 = hot
        self.COLD_STREAK_THRESHOLD = -3.0  # Form < -3 = cold
        self.STREAK_MIN_MATCHES = 3  # Minimum matches to count as streak

        # Maximum form bounds
        self.MAX_FORM = 10.0
        self.MIN_FORM = -10.0

        # Performance modifiers
        self.SHOOTING_MODIFIER_PER_FORM = 0.02  # +2% accuracy per form point
        self.PASSING_MODIFIER_PER_FORM = 0.01  # +1% completion per form point
        self.AERIAL_MODIFIER_PER_FORM = 0.015  # +1.5% aerial success per form point
        self.DECISION_MODIFIER_PER_FORM = 0.01  # Better choices when hot

        # Teammate effects (when player is hot)
        self.HOT_TEAMMATE_PASS_BONUS = 0.15  # +15% pass frequency to hot player
        self.COLD_TEAMMATE_PASS_PENALTY = -0.05  # -5% pass frequency to cold player

        # Storage
        self.player_forms: Dict[int, FormStats] = {}

    def initialize_player(self, player_id: int, player_name: str):
        """Initialize form tracking for a player"""
        self.player_forms[player_id] = FormStats(
            player_id=player_id,
            player_name=player_name,
            current_form=0.0,
        )

    def get_player_form(self, player_id: int) -> float:
        """Get current form for a player (-10 to +10)"""
        if player_id not in self.player_forms:
            return 0.0
        return self.player_forms[player_id].current_form

    def update_form_goal(self, player_id: int, time: int):
        """Player scored a goal"""
        self._update_form_value(
            player_id,
            time,
            self.FORM_GOAL,
            "goal",
            "Scored goal",
        )

    def update_form_assist(self, player_id: int, time: int):
        """Player provided an assist"""
        self._update_form_value(
            player_id,
            time,
            self.FORM_ASSIST,
            "assist",
            "Provided assist",
        )

    def update_form_shot_on_target(self, player_id: int, time: int):
        """Player took a shot on target"""
        self._update_form_value(
            player_id,
            time,
            self.FORM_SHOT_ON_TARGET,
            "shot_on_target",
            "Shot on target",
        )

    def update_form_missed_chance(self, player_id: int, time: int):
        """Player missed a clear chance"""
        self._update_form_value(
            player_id,
            time,
            self.FORM_MISSED_CHANCE,
            "missed_chance",
            "Missed clear chance",
        )

    def update_form_defensive_action(self, player_id: int, time: int):
        """Player made defensive action (tackle, interception, block)"""
        self._update_form_value(
            player_id,
            time,
            self.FORM_DEFENSIVE_ACTION,
            "defensive_action",
            "Defensive action",
        )

    def update_form_poor_pass(self, player_id: int, time: int):
        """Player made a poor pass"""
        self._update_form_value(
            player_id,
            time,
            self.FORM_POOR_PASS,
            "poor_pass",
            "Poor pass",
        )

    def update_form_yellow_card(self, player_id: int, time: int):
        """Player received yellow card"""
        self._update_form_value(
            player_id,
            time,
            self.FORM_YELLOW_CARD,
            "yellow_card",
            "Yellow card received",
        )

    def apply_form_decay(self, player_id: int):
        """Apply end-of-match form decay (recovery towards 0)"""
        if player_id not in self.player_forms:
            return

        stats = self.player_forms[player_id]
        current = stats.current_form

        # Decay towards 0
        if current > 0:
            new_form = current * (1.0 - self.FORM_DECAY_RATE)
        elif current < 0:
            new_form = current * (1.0 - self.FORM_DECAY_RATE)
        else:
            new_form = 0.0

        stats.current_form = self._clamp_form(new_form)
        stats.form_history.append(stats.current_form)

    def get_shooting_modifier(self, player_id: int) -> float:
        """
        Get shooting accuracy modifier based on form

        Returns: Multiplier for shot accuracy/power
        E.g., form=5 → 1.10 (10% better), form=-3 → 0.94 (6% worse)
        """
        form = self.get_player_form(player_id)
        return 1.0 + (form * self.SHOOTING_MODIFIER_PER_FORM)

    def get_passing_modifier(self, player_id: int) -> float:
        """
        Get pass completion modifier based on form

        Returns: Multiplier for pass accuracy
        """
        form = self.get_player_form(player_id)
        return 1.0 + (form * self.PASSING_MODIFIER_PER_FORM)

    def get_aerial_modifier(self, player_id: int) -> float:
        """
        Get aerial duel success modifier based on form

        Returns: Multiplier for aerial success rate
        """
        form = self.get_player_form(player_id)
        return 1.0 + (form * self.AERIAL_MODIFIER_PER_FORM)

    def get_decision_quality_modifier(self, player_id: int) -> float:
        """
        Get decision-making quality modifier

        When hot (form > 0):
        - Better positioning
        - Smarter passes
        - More aggressive when appropriate

        When cold (form < 0):
        - Hesitant decisions
        - Poor positioning
        - Plays it safe too much
        """
        form = self.get_player_form(player_id)
        return 1.0 + (form * self.DECISION_MODIFIER_PER_FORM)

    def get_pass_frequency_modifier_to_player(self, player_id: int) -> float:
        """
        Get modifier for pass frequency TO this player

        Hot players get passed to more by teammates
        Cold players receive fewer passes
        """
        form = self.get_player_form(player_id)

        if form > self.HOT_STREAK_THRESHOLD:
            return 1.0 + self.HOT_TEAMMATE_PASS_BONUS
        elif form < self.COLD_STREAK_THRESHOLD:
            return 1.0 + self.COLD_TEAMMATE_PASS_PENALTY
        else:
            # Linear interpolation between thresholds
            if form > 0:
                return 1.0 + (form / self.HOT_STREAK_THRESHOLD) * self.HOT_TEAMMATE_PASS_BONUS
            else:
                return 1.0 + (form / self.COLD_STREAK_THRESHOLD) * self.COLD_TEAMMATE_PASS_PENALTY

    def get_form_phase(self, player_id: int) -> FormPhase:
        """Get current form phase (cold streak, poor, average, good, hot streak)"""
        form = self.get_player_form(player_id)

        if form > self.HOT_STREAK_THRESHOLD:
            return FormPhase.HOT_STREAK
        elif form > 1.0:
            return FormPhase.GOOD_FORM
        elif form > -1.0:
            return FormPhase.AVERAGE_FORM
        elif form > self.COLD_STREAK_THRESHOLD:
            return FormPhase.POOR_FORM
        else:
            return FormPhase.COLD_STREAK

    def get_player_stats(self, player_id: int) -> Optional[FormStats]:
        """Get form statistics for a player"""
        return self.player_forms.get(player_id)

    def get_all_player_stats(self) -> Dict[int, FormStats]:
        """Get form statistics for all players"""
        return self.player_forms

    def reset_for_new_match(self):
        """Apply decay at end of match (prepare for next match)"""
        for player_id in self.player_forms:
            self.apply_form_decay(player_id)

    def _update_form_value(
        self,
        player_id: int,
        time: int,
        form_change: float,
        event_type: str,
        reason: str,
    ):
        """Internal: update form for a player"""
        if player_id not in self.player_forms:
            self.initialize_player(player_id, f"Player {player_id}")

        stats = self.player_forms[player_id]
        new_form = stats.current_form + form_change
        new_form = self._clamp_form(new_form)

        update = FormUpdate(
            time=time,
            event_type=event_type,
            form_change=form_change,
            new_form=new_form,
            reason=reason,
        )

        stats.form_updates.append(update)
        stats.current_form = new_form

        # Track peaks
        if new_form > stats.peak_form:
            stats.peak_form = new_form
        if new_form < stats.lowest_form:
            stats.lowest_form = new_form

    def _clamp_form(self, form: float) -> float:
        """Clamp form between min and max bounds"""
        return max(self.MIN_FORM, min(self.MAX_FORM, form))

    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        hot_streak_count = 0
        cold_streak_count = 0
        avg_form = 0.0

        for stats in self.player_forms.values():
            if stats.current_form > self.HOT_STREAK_THRESHOLD:
                hot_streak_count += 1
            elif stats.current_form < self.COLD_STREAK_THRESHOLD:
                cold_streak_count += 1

            avg_form += stats.current_form

        if self.player_forms:
            avg_form /= len(self.player_forms)

        return {
            "avg_form": avg_form,
            "hot_streak_count": hot_streak_count,
            "cold_streak_count": cold_streak_count,
            "total_players_tracked": len(self.player_forms),
        }


# Helper functions for integration


def create_player_form_system() -> PlayerFormSystem:
    """Factory function to create a form system"""
    return PlayerFormSystem()


def apply_form_modifiers_to_player(
    player: "Player",
    form_system: PlayerFormSystem,
) -> Dict[str, float]:
    """
    Apply form modifiers to a player

    Returns dict of modifiers:
    - shooting_mod: multiplier for shot accuracy
    - passing_mod: multiplier for pass accuracy
    - aerial_mod: multiplier for aerial success
    - decision_mod: multiplier for decision quality
    """
    return {
        "shooting_mod": form_system.get_shooting_modifier(player.id),
        "passing_mod": form_system.get_passing_modifier(player.id),
        "aerial_mod": form_system.get_aerial_modifier(player.id),
        "decision_mod": form_system.get_decision_quality_modifier(player.id),
    }
