"""
Extended Match Engine - Integrates Card, Injury, and Substitution systems
Adds to match_simulation_engine_v2.Match class
"""

import random
from card_discipline_system import CardDisciplineSystem, CardType, should_award_foul
from injury_system import InjurySystem, should_injure_player
from substitution_system import SubstitutionSystem, Squad
from player_behavior import PlayerState
from match_simulation_engine_v2 import MatchEvent, Event


class ExtendedMatch:
    """
    Extends base Match with discipline, injury, and substitution systems
    Mixin pattern - to be used alongside Match class
    """

    def add_extended_systems(self):
        """Initialize extended systems"""
        self.substitutions_made = {
            'home': 0,
            'away': 0,
        }
        self.injuries_log = []
        self.cards_log = []

        # Create squads (in real impl, would come from database)
        self.home_team.squad = Squad("Home", self.home_team.players)
        self.away_team.squad = Squad("Away", self.away_team.players)

    def check_discipline(self):
        """Check for fouls and cards each frame"""
        all_players = self.home_team.players + self.away_team.players

        for player in all_players:
            # Skip injured/ejected players
            if player.is_injured or player.red_card:
                continue

            # Calculate foul probability
            score_gap = (
                self.home_team.score - self.away_team.score
                if player.team == "Home"
                else self.away_team.score - self.home_team.score
            )

            foul_committed, action = should_award_foul(
                player=player,
                match_minute=self.current_minute,
                score_gap=score_gap,
                referee_strictness=1.0
            )

            if foul_committed and action:
                self.cards_log.append(action)

                # Log event
                if action.card_awarded:
                    event_type = (
                        MatchEvent.RED_CARD if action.card_awarded in [CardType.RED, CardType.SECOND_YELLOW]
                        else MatchEvent.YELLOW_CARD
                    )

                    self.events.append(Event(
                        event_type=event_type,
                        time=self.current_minute,
                        player_id=player.id,
                        team=player.team,
                        details={
                            'card_type': action.card_awarded.value,
                            'yellow_count': player.yellow_cards,
                        }
                    ))

    def check_injuries(self):
        """Check for injuries each frame"""
        all_players = self.home_team.players + self.away_team.players

        for player in all_players:
            # Skip already injured players
            if player.is_injured or player.red_card:
                continue

            # Match intensity based on current action
            match_intensity = 1.0 if self.current_minute > 45 else 0.8

            injured, injury = should_injure_player(
                player=player,
                match_minute=self.current_minute,
                match_intensity=match_intensity
            )

            if injured and injury:
                self.injuries_log.append(injury)

                # Log event
                self.events.append(Event(
                    event_type=MatchEvent.INJURY,
                    time=self.current_minute,
                    player_id=player.id,
                    team=player.team,
                    details={
                        'injury_type': injury.injury_type.value,
                        'severity': injury.severity,
                        'recovery_days': injury.recovery_days_total,
                    }
                ))

    def check_substitutions(self):
        """Check if substitutions should be made"""
        # Check both teams
        for team, opposing_team in [
            (self.home_team, self.away_team),
            (self.away_team, self.home_team),
        ]:
            score_gap = team.score - opposing_team.score

            # Only make substitution if under limit (3-5 per team)
            team_key = 'home' if team.name == 'Home' else 'away'
            if self.substitutions_made[team_key] >= 5:
                continue

            substitution = SubstitutionSystem.should_make_substitution(
                team=team,
                opposing_team=opposing_team,
                match_minute=self.current_minute,
                score_gap=score_gap,
                match_intensity=1.0
            )

            if substitution:
                if SubstitutionSystem.execute_substitution(self, team, substitution):
                    self.substitutions_made[team_key] += 1

    def process_extended_events(self):
        """
        Process all extended systems each frame
        Call from simulate_frame()
        """
        # These are called after main behavior/movement updates
        self.check_discipline()
        self.check_injuries()
        self.check_substitutions()

    def get_extended_stats(self) -> dict:
        """Get statistics for extended systems"""
        return {
            'total_fouls': sum(1 for c in self.cards_log),
            'total_yellows': sum(1 for c in self.cards_log if c.card_awarded and 'YELLOW' in str(c.card_awarded)),
            'total_reds': sum(1 for c in self.cards_log if c.card_awarded and 'RED' in str(c.card_awarded)),
            'total_injuries': len(self.injuries_log),
            'substitutions': self.substitutions_made,
        }


# ============================================================================
# INTEGRATION HELPER - to patch existing Match class
# ============================================================================

def integrate_extended_systems(match_instance):
    """
    Monkey-patch extended systems onto a Match instance

    Usage:
        match = Match(home_team, away_team)
        integrate_extended_systems(match)
    """

    # Add extended attributes
    match_instance.substitutions_made = {'home': 0, 'away': 0}
    match_instance.injuries_log = []
    match_instance.cards_log = []

    # Create squads
    from substitution_system import Squad
    match_instance.home_team.squad = Squad("Home", match_instance.home_team.players)
    match_instance.away_team.squad = Squad("Away", match_instance.away_team.players)

    # Add methods
    match_instance.check_discipline = lambda: ExtendedMatch.check_discipline(match_instance)
    match_instance.check_injuries = lambda: ExtendedMatch.check_injuries(match_instance)
    match_instance.check_substitutions = lambda: ExtendedMatch.check_substitutions(match_instance)
    match_instance.process_extended_events = lambda: ExtendedMatch.process_extended_events(match_instance)
    match_instance.get_extended_stats = lambda: ExtendedMatch.get_extended_stats(match_instance)
