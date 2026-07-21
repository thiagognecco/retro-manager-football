#!/usr/bin/env python3
"""Test suite for Card System (Yellow/Red cards)"""

import sys
sys.path.insert(0, r"C:\Users\gnecc\Documents\Footbal manager")

import pytest
from player_behavior import Player, PlayerRole

class TestCardSystem:
    """Test yellow/red card mechanics"""

    def test_player_has_card_fields(self):
        """Players should have card tracking fields"""
        player = Player(
            id=1, name="Test Player", team="Home",
            role=PlayerRole.MIDFIELDER, number=7
        )

        assert hasattr(player, 'yellow_cards')
        assert hasattr(player, 'red_card')
        assert hasattr(player, 'fouls_committed')
        assert player.yellow_cards == 0
        assert player.red_card == False
        assert player.fouls_committed == 0

    def test_yellow_card_accumulation(self):
        """Test yellow card accumulation"""
        player = Player(
            id=1, name="Test Player", team="Home",
            role=PlayerRole.DEFENDER, number=4
        )

        player.yellow_cards = 1
        assert player.yellow_cards == 1

        player.yellow_cards = 2
        assert player.yellow_cards == 2
        # Two yellows should trigger red

    def test_red_card_flag(self):
        """Test red card flag"""
        player = Player(
            id=1, name="Test Player", team="Home",
            role=PlayerRole.MIDFIELDER, number=7
        )

        player.red_card = True
        assert player.red_card == True

    def test_foul_tracking(self):
        """Test foul count tracking"""
        player = Player(
            id=1, name="Test Player", team="Home",
            role=PlayerRole.DEFENDER, number=4
        )

        assert player.fouls_committed == 0
        player.fouls_committed += 1
        assert player.fouls_committed == 1

    def test_position_affects_fouls(self):
        """Different positions should have different foul rates"""
        # This will be validated in integration tests
        # Defenders should foul more than forwards
        defender = Player(
            id=1, name="Defender", team="Home",
            role=PlayerRole.DEFENDER, number=4
        )

        forward = Player(
            id=2, name="Forward", team="Home",
            role=PlayerRole.FORWARD, number=9
        )

        assert defender.role == PlayerRole.DEFENDER
        assert forward.role == PlayerRole.FORWARD

    def test_stamina_affects_fouls(self):
        """Tired players should foul more"""
        player = Player(
            id=1, name="Test Player", team="Home",
            role=PlayerRole.MIDFIELDER, number=7
        )

        player.stamina = 100.0
        high_stamina = player.stamina

        player.stamina = 20.0
        low_stamina = player.stamina

        assert low_stamina < high_stamina
        # Integration test will verify foul rate increases with fatigue


class TestCardIntegration:
    """Integration tests for card system with match simulation"""

    def test_cards_in_match(self):
        """Test that cards are properly recorded in matches"""
        # This will be run after implementing card logic in match engine
        pass

    def test_match_with_100_fouls(self):
        """
        Run a match and verify approximately 20.9 fouls
        Based on Premier League average
        """
        # This will run a full match and check foul statistics
        pass

    def test_red_card_effects(self):
        """Test that red card causes ejection"""
        # Player should be removed from play
        pass

    def test_two_yellows_equals_red(self):
        """Verify two yellows automatically produces red"""
        # This should be automatic in card logic
        pass


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
