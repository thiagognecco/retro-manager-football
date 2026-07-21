"""
Card & Discipline System - Yellow/Red Cards
Based on Premier League statistics and football rules

Fouls per match:
  - Premier League: 20.9 fouls/match
  - LaLiga: 27.0 fouls/match
  - 60-70% of cards in 2nd half

Yellow card rules:
  - Two yellows = automatic red
  - Referee variance: ±20%
"""

import random
from enum import Enum
from typing import Optional, Tuple, Dict
from dataclasses import dataclass


class CardType(Enum):
    """Types of disciplinary cards"""
    YELLOW = "yellow"
    RED = "red"
    SECOND_YELLOW = "second_yellow"  # Two yellows in same match


class FoulType(Enum):
    """Types of fouls with different card probabilities"""
    TECHNICAL = "technical"          # Handball, off side - 10% yellow
    TACTICAL = "tactical"            # Tripping, pulling - 20% yellow
    DANGEROUS = "dangerous"           # High boot, elbow - 30% yellow
    VIOLENT = "violent"              # Violent conduct - 100% red
    RECKLESS = "reckless"            # Reckless play - 50% yellow


@dataclass
class DisciplinaryAction:
    """Result of a foul evaluation"""
    foul_type: FoulType
    card_awarded: Optional[CardType] = None
    player_id: int = 0
    match_minute: int = 0
    description: str = ""


class CardDisciplineSystem:
    """
    Manages yellow/red cards and fouls during match

    Based on:
    - Premier League statistics (20.9 fouls/match)
    - Card probability models
    - Football rules (2 yellows = red)
    """

    # Base foul rate: 20.9 fouls / 90 min / 22 players = 0.00244 per player per min
    # Multiplied by 3.5 to account for frame-level checking
    BASE_FOUL_RATE = 0.00244 * 3.5  # = 0.00854 (calibrated to ~20.9 fouls/match)

    # Position-based foul multipliers (Defenders foul more)
    POSITION_MULTIPLIERS = {
        'GK': 0.1,
        'DEF': 1.3,
        'MID': 1.0,
        'FWD': 0.7,
    }

    # Foul type yellow card probabilities
    FOUL_YELLOW_PROBABILITIES = {
        FoulType.TECHNICAL: 0.10,
        FoulType.TACTICAL: 0.20,
        FoulType.DANGEROUS: 0.30,
        FoulType.RECKLESS: 0.50,
        FoulType.VIOLENT: 0.00,  # Violent is automatic red
    }

    # Card distribution: 60-70% in 2nd half
    HALF_TIME = 45  # Minutes

    @staticmethod
    def calculate_foul_probability(
        player_stamina: float,
        player_position: str,
        match_minute: int,
        score_gap: int,
        referee_strictness: float = 1.0
    ) -> float:
        """
        Calculate probability of player committing a foul this frame

        Args:
            player_stamina: Player stamina 0-100
            player_position: Player role (GK, DEF, MID, FWD)
            match_minute: Current minute (0-90)
            score_gap: Score difference (negative = losing)
            referee_strictness: Referee variance (0.8-1.2)

        Returns:
            Probability of foul this frame (0.0-1.0)
        """

        base_rate = CardDisciplineSystem.BASE_FOUL_RATE

        # Position multiplier
        position_mult = CardDisciplineSystem.POSITION_MULTIPLIERS.get(
            player_position, 1.0
        )

        # Stamina effect: Fatigue increases fouls
        # Every 10% stamina loss adds ~15% to foul rate
        stamina_loss = max(0, 100 - player_stamina)
        stamina_mult = 1.0 + (stamina_loss / 100) * 0.15

        # Match intensity: Losing teams foul more
        # Each goal deficit increases foul rate by 5%
        intensity_mult = 1.0 + max(0, -score_gap) * 0.05

        # Time effect: 2nd half has ~65% of fouls
        # Use Poisson: foul rate increases as match progresses
        if match_minute >= CardDisciplineSystem.HALF_TIME:
            time_mult = 1.8  # ~65% of fouls in 2nd half
        else:
            time_mult = 1.0

        # Referee variance: ±20%
        referee_variance = random.uniform(0.8, 1.2) * referee_strictness

        probability = (
            base_rate * position_mult * stamina_mult *
            intensity_mult * time_mult * referee_variance
        )

        return min(probability, 1.0)  # Cap at 1.0

    @staticmethod
    def evaluate_foul_for_card(
        foul_type: FoulType,
        player_yellow_cards: int,
        referee_strictness: float = 1.0
    ) -> Optional[CardType]:
        """
        Determine if foul results in card

        Args:
            foul_type: Type of foul committed
            player_yellow_cards: Current yellow cards (0, 1, or 2)
            referee_strictness: Strictness variance

        Returns:
            Card type (YELLOW, RED, SECOND_YELLOW) or None
        """

        # Already on yellow - high risk of red on next foul
        if player_yellow_cards >= 1:
            # 40% chance of second yellow = red
            if random.random() < 0.40:
                return CardType.SECOND_YELLOW
            else:
                return None

        # Violent conduct = automatic red
        if foul_type == FoulType.VIOLENT:
            return CardType.RED

        # Get base probability for this foul type
        base_probability = CardDisciplineSystem.FOUL_YELLOW_PROBABILITIES.get(
            foul_type, 0.15
        )

        # Apply referee variance
        probability = base_probability * random.uniform(0.8, 1.2) * referee_strictness

        if random.random() < probability:
            return CardType.YELLOW

        return None

    @staticmethod
    def get_random_foul_type() -> FoulType:
        """
        Sample a random foul type with realistic distribution

        Most fouls are technical/tactical, fewer are dangerous/violent
        Adjusted to reduce yellow cards: target 2-3 per match (was 4.7)
        """
        return random.choices(
            population=[
                FoulType.TECHNICAL,
                FoulType.TACTICAL,
                FoulType.DANGEROUS,
                FoulType.RECKLESS,
                FoulType.VIOLENT,
            ],
            weights=[0.72, 0.25, 0.02, 0.005, 0.005]  # Heavy TECH, reduced others to target 2-3 cards
        )[0]

    @staticmethod
    def apply_card_effects(player, card_type: CardType) -> Dict:
        """
        Apply effects of card on player behavior

        Returns:
            Dictionary with effects applied
        """

        effects = {
            'player_id': player.id,
            'card_type': card_type.value,
            'stamina_modifier': 1.0,
            'aggression_modifier': 1.0,
            'caution_modifier': 1.0,
            'ejected': False,
        }

        if card_type == CardType.YELLOW:
            # Yellow card effects
            player.yellow_cards += 1
            effects['stamina_modifier'] = 1.0  # No stamina effect
            effects['aggression_modifier'] = 0.90  # 10% less aggressive
            effects['caution_modifier'] = 1.05  # 5% more cautious

        elif card_type in [CardType.RED, CardType.SECOND_YELLOW]:
            # Red card: player ejected
            player.red_card = True
            player.yellow_cards = 2  # Mark as having two yellows
            effects['ejected'] = True
            effects['stamina_modifier'] = 0.0  # Can't play
            effects['aggression_modifier'] = 0.0

        return effects


# ============================================================================
# INTEGRATION WITH MATCH SIMULATION
# ============================================================================

def should_award_foul(
    player,
    match_minute: int,
    score_gap: int,
    referee_strictness: float = 1.0
) -> Tuple[bool, Optional[DisciplinaryAction]]:
    """
    Check if player commits a foul this frame

    Returns:
        (foul_committed, disciplinary_action)
    """

    foul_probability = CardDisciplineSystem.calculate_foul_probability(
        player_stamina=player.stamina,
        player_position=player.role.value,
        match_minute=match_minute,
        score_gap=score_gap,
        referee_strictness=referee_strictness
    )

    if random.random() < foul_probability:
        # Foul committed - determine if card
        player.fouls_committed += 1
        foul_type = CardDisciplineSystem.get_random_foul_type()

        card_awarded = CardDisciplineSystem.evaluate_foul_for_card(
            foul_type=foul_type,
            player_yellow_cards=player.yellow_cards,
            referee_strictness=referee_strictness
        )

        action = DisciplinaryAction(
            foul_type=foul_type,
            card_awarded=card_awarded,
            player_id=player.id,
            match_minute=match_minute,
            description=f"{player.name} commits {foul_type.value} foul"
        )

        if card_awarded:
            CardDisciplineSystem.apply_card_effects(player, card_awarded)
            action.description += f" -> {card_awarded.value} card"

        return True, action

    return False, None
