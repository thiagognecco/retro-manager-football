"""
Extended Match Engine - Integrates all TIER 1 + TIER 2 systems
- TIER 1: Card, Injury, Substitution systems
- TIER 2: Set Pieces, Player Form systems
"""

import random
from card_discipline_system import CardDisciplineSystem, CardType, should_award_foul
from injury_system import InjurySystem, should_injure_player
from substitution_system import SubstitutionSystem, Squad
from set_pieces_system import SetPiecesSystem, SetPieceType
from player_form_system import PlayerFormSystem
from player_behavior import PlayerState
from match_simulation_engine_v2 import MatchEvent, Event


class ExtendedMatch:
    """
    Extends base Match with discipline, injury, and substitution systems
    Mixin pattern - to be used alongside Match class
    """

    def add_extended_systems(self):
        """Initialize extended systems (TIER 1 + TIER 2)"""
        # TIER 1: Discipline
        self.substitutions_made = {
            'home': 0,
            'away': 0,
        }
        self.injuries_log = []
        self.cards_log = []

        # Create squads (in real impl, would come from database)
        self.home_team.squad = Squad("Home", self.home_team.players)
        self.away_team.squad = Squad("Away", self.away_team.players)

        # TIER 2: Set Pieces
        self.set_pieces_system = SetPiecesSystem()
        self.set_pieces_log = []

        # TIER 2: Player Form
        self.form_system = PlayerFormSystem()
        # Initialize form for all players
        for player in self.home_team.players + self.away_team.players:
            self.form_system.initialize_player(player.id, player.name)

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

    def check_set_pieces(self):
        """Check for set piece opportunities each frame (TIER 2)"""
        # This would be called when ball goes out of play
        # Detection happens in main simulate_frame() when ball_out_of_bounds
        # For now, this is a hook for future integration
        pass

    def update_player_form_event(self, player_id: int, event_type: str):
        """Update player form based on match event (TIER 2)"""
        if event_type == "goal":
            self.form_system.update_form_goal(player_id, self.current_minute)
        elif event_type == "assist":
            self.form_system.update_form_assist(player_id, self.current_minute)
        elif event_type == "shot_on_target":
            self.form_system.update_form_shot_on_target(player_id, self.current_minute)
        elif event_type == "missed_chance":
            self.form_system.update_form_missed_chance(player_id, self.current_minute)
        elif event_type == "defensive_action":
            self.form_system.update_form_defensive_action(player_id, self.current_minute)
        elif event_type == "poor_pass":
            self.form_system.update_form_poor_pass(player_id, self.current_minute)
        elif event_type == "yellow_card":
            self.form_system.update_form_yellow_card(player_id, self.current_minute)

    def apply_end_of_match_form_decay(self):
        """Apply form decay at end of match (TIER 2)"""
        all_players = self.home_team.players + self.away_team.players
        for player in all_players:
            self.form_system.apply_form_decay(player.id)

    def process_extended_events(self):
        """
        Process all extended systems each frame (TIER 1 + TIER 2)
        Call from simulate_frame()
        """
        # TIER 1: Discipline, injuries, substitutions
        self.check_discipline()
        self.check_injuries()
        self.check_substitutions()

        # TIER 2: Set pieces, form updates
        self.check_set_pieces()

    def get_extended_stats(self) -> dict:
        """Get statistics for extended systems (TIER 1 + TIER 2)"""
        # TIER 1 stats
        tier1_stats = {
            'total_fouls': sum(1 for c in self.cards_log),
            'total_yellows': sum(1 for c in self.cards_log if c.card_awarded and 'YELLOW' in str(c.card_awarded)),
            'total_reds': sum(1 for c in self.cards_log if c.card_awarded and 'RED' in str(c.card_awarded)),
            'total_injuries': len(self.injuries_log),
            'substitutions': self.substitutions_made,
        }

        # TIER 2 Set Pieces stats
        set_pieces_stats = self.set_pieces_system.get_stats()
        tier2_set_pieces = {
            'set_pieces': {
                'corners_total': set_pieces_stats.total_corners,
                'corners_scored': set_pieces_stats.corners_scored,
                'corners_from_play': set_pieces_stats.corners_from_play,
                'free_kicks_total': set_pieces_stats.total_free_kicks,
                'free_kicks_scored': set_pieces_stats.free_kicks_scored,
                'throw_ins': set_pieces_stats.throw_ins,
                'set_piece_goals': set_pieces_stats.set_piece_goals,
                'set_piece_xg': set_pieces_stats.set_piece_xg,
            }
        }

        # TIER 2 Form stats
        form_stats = self.form_system.get_system_stats()
        tier2_form = {
            'player_form': {
                'avg_form': form_stats['avg_form'],
                'hot_streak_count': form_stats['hot_streak_count'],
                'cold_streak_count': form_stats['cold_streak_count'],
            }
        }

        return {**tier1_stats, **tier2_set_pieces, **tier2_form}


# ============================================================================
# INTEGRATION HELPER - to patch existing Match class
# ============================================================================

def integrate_extended_systems(match_instance):
    """
    Monkey-patch extended systems (TIER 1 + TIER 2) onto a Match instance

    Usage:
        match = Match(home_team, away_team)
        integrate_extended_systems(match)
    """

    # TIER 1: Add extended attributes
    match_instance.substitutions_made = {'home': 0, 'away': 0}
    match_instance.injuries_log = []
    match_instance.cards_log = []

    # Create squads
    from substitution_system import Squad
    match_instance.home_team.squad = Squad("Home", match_instance.home_team.players)
    match_instance.away_team.squad = Squad("Away", match_instance.away_team.players)

    # TIER 2: Add set pieces system
    match_instance.set_pieces_system = SetPiecesSystem()
    match_instance.set_pieces_log = []

    # TIER 2: Add form system
    match_instance.form_system = PlayerFormSystem()
    for player in match_instance.home_team.players + match_instance.away_team.players:
        match_instance.form_system.initialize_player(player.id, player.name)

    # TIER 1: Add methods
    match_instance.check_discipline = lambda: ExtendedMatch.check_discipline(match_instance)
    match_instance.check_injuries = lambda: ExtendedMatch.check_injuries(match_instance)
    match_instance.check_substitutions = lambda: ExtendedMatch.check_substitutions(match_instance)

    # TIER 2: Add methods
    match_instance.check_set_pieces = lambda: ExtendedMatch.check_set_pieces(match_instance)
    match_instance.update_player_form_event = lambda event_type, player_id: ExtendedMatch.update_player_form_event(match_instance, player_id, event_type)
    match_instance.apply_end_of_match_form_decay = lambda: ExtendedMatch.apply_end_of_match_form_decay(match_instance)

    # Combined methods
    match_instance.process_extended_events = lambda: ExtendedMatch.process_extended_events(match_instance)
    match_instance.get_extended_stats = lambda: ExtendedMatch.get_extended_stats(match_instance)
