"""
Substitution System - Squad Management & Tactical Changes
Based on Football Manager implementation research

Substitution strategy:
  - Best time: Half-time (momentum change)
  - Common triggers: Injury, Red card, Yellow+danger, Fatigue, Tactical
  - Typical: 3-5 substitutions per team per match
"""

from enum import Enum
from typing import Optional, List
from dataclasses import dataclass


class SubstitutionReason(Enum):
    """Why substitution is made"""
    INJURY = "injury"              # Player injured
    EJECTION = "ejection"          # Red card
    YELLOW_CARD_RISK = "yellow_risk"  # Prevent 2nd yellow
    FATIGUE = "fatigue"            # Too tired
    TACTICAL = "tactical"          # Tactical change
    ROTATION = "rotation"          # Squad rotation


@dataclass
class Substitution:
    """Substitution record"""
    player_out_id: int
    player_in_id: int
    reason: SubstitutionReason
    match_minute: int
    tactical_change: bool = False


class Squad:
    """Team squad with starting XI and bench"""

    def __init__(self, name: str, players: List['Player']):
        self.name = name
        self.primary_eleven: List['Player'] = players[:11]
        self.bench: List['Player'] = players[11:] if len(players) > 11 else []

    def get_best_replacement(self, position: str) -> Optional['Player']:
        """
        Find best substitute for position

        Criteria:
        - Not injured
        - High stamina (70%+)
        - Correct position
        - Highest fitness
        """
        candidates = [
            p for p in self.bench
            if not p.is_injured and p.stamina > 70 and p.role.value == position
        ]

        if not candidates:
            return None

        # Return player with highest fitness/stamina
        return max(candidates, key=lambda p: p.fitness * (p.stamina / 100))

    def make_substitution(
        self,
        player_out: 'Player',
        player_in: 'Player'
    ) -> bool:
        """
        Execute substitution: remove out, add in to squad

        Returns:
            True if successful, False if invalid
        """

        if player_out not in self.primary_eleven:
            return False

        if player_in not in self.bench:
            return False

        # Swap players
        idx = self.primary_eleven.index(player_out)
        self.primary_eleven[idx] = player_in
        self.bench.remove(player_in)
        self.bench.append(player_out)

        return True


class SubstitutionSystem:
    """
    Intelligent substitution decision making

    Priority order (based on Football Manager):
    1. Injury (mandatory)
    2. Red card (mandatory)
    3. Yellow + danger (preventative, minute > 60)
    4. Fatigue (minute > 70, stamina < 30%)
    5. Tactical (minute > 60, losing badly)
    """

    @staticmethod
    def should_make_substitution(
        team,
        opposing_team,
        match_minute: int,
        score_gap: int,  # Negative = losing
        match_intensity: float = 1.0
    ) -> Optional[Substitution]:
        """
        Determine if substitution should be made

        Returns:
            Substitution object or None
        """

        # PRIORITY 1: Mandatory injury/red card
        for player in team.players:
            if player.is_injured:
                replacement = team.squad.get_best_replacement(player.role.value)
                if replacement:
                    return Substitution(
                        player_out_id=player.id,
                        player_in_id=replacement.id,
                        reason=SubstitutionReason.INJURY,
                        match_minute=match_minute,
                        tactical_change=False
                    )

            if player.red_card:
                replacement = team.squad.get_best_replacement(player.role.value)
                if replacement:
                    return Substitution(
                        player_out_id=player.id,
                        player_in_id=replacement.id,
                        reason=SubstitutionReason.EJECTION,
                        match_minute=match_minute,
                        tactical_change=False
                    )

        # PRIORITY 2: Preventative (yellow card risk, after minute 60)
        if match_minute > 60:
            for player in team.players:
                if player.yellow_cards >= 1:
                    # Check if many opposing attackers active
                    opposing_forwards = [
                        p for p in opposing_team.players
                        if p.role.value == 'FWD' and p.stamina > 60
                    ]

                    if len(opposing_forwards) >= 2:
                        replacement = team.squad.get_best_replacement(player.role.value)
                        if replacement and replacement.stamina > 50:
                            return Substitution(
                                player_out_id=player.id,
                                player_in_id=replacement.id,
                                reason=SubstitutionReason.YELLOW_CARD_RISK,
                                match_minute=match_minute,
                                tactical_change=False
                            )

        # PRIORITY 3: Fatigue (after minute 70)
        if match_minute > 70:
            tired_players = [
                p for p in team.players
                if p.stamina < 40 and p.role.value != 'GK'  # Lowered from 30 to 40 for more subs
            ]

            if tired_players:
                # Pick worst performer
                worst = min(
                    tired_players,
                    key=lambda p: p.fitness * (p.stamina / 100)
                )

                replacement = team.squad.get_best_replacement(worst.role.value)
                if replacement and replacement.stamina > 70:
                    return Substitution(
                        player_out_id=worst.id,
                        player_in_id=replacement.id,
                        reason=SubstitutionReason.FATIGUE,
                        match_minute=match_minute,
                        tactical_change=False
                    )

        # PRIORITY 4: Tactical (losing by 2+, rare in simulation)
        if match_minute > 65 and score_gap < -1:
            import random
            if random.random() < 0.3:  # 30% chance to try attacking change
                # Replace defensive midfielder with attacker
                defensive_mids = [
                    p for p in team.players
                    if p.role.value == 'MID' and p.stamina > 50
                ]

                if defensive_mids:
                    to_remove = defensive_mids[0]
                    replacement = team.squad.get_best_replacement('FWD')

                    if replacement:
                        return Substitution(
                            player_out_id=to_remove.id,
                            player_in_id=replacement.id,
                            reason=SubstitutionReason.TACTICAL,
                            match_minute=match_minute,
                            tactical_change=True
                        )

        return None

    @staticmethod
    def execute_substitution(
        match,
        team,
        substitution: Substitution
    ) -> bool:
        """
        Execute substitution in match

        Effects:
        - Incoming player gets 90% stamina
        - Position maintained
        - Event logged

        Returns:
            True if successful (stub for now)
        """
        # Simplified version: just log the event
        # In real implementation, would swap players
        # For now, tracking only without actual swap to avoid complexity

        try:
            from match_simulation_engine_v2 import Event, MatchEvent

            player_out = next(
                (p for p in team.players if p.id == substitution.player_out_id),
                None
            )

            if not player_out:
                return False

            match.events.append(Event(
                event_type=MatchEvent.SUBSTITUTION,
                time=substitution.match_minute,
                player_id=player_out.id,
                team=team.name,
                details={
                    'player_out': player_out.name,
                    'player_in': f'Sub_{substitution.player_in_id}',
                    'reason': substitution.reason.value,
                    'tactical': substitution.tactical_change,
                }
            ))
            return True
        except:
            return False
