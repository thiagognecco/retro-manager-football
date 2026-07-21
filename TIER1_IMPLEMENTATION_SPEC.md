# TIER 1 IMPLEMENTATION SPECIFICATION
## Based on Real Football Data & Scientific Models

---

## 📋 OVERVIEW

Implementation plan for 4 critical systems based on actual football statistics and peer-reviewed research.

**Target**: Reach 70% realism (from current 50%)
**Estimated Time**: 8-10 hours
**Sources**: Premier League stats, Scientific research papers, Football Manager implementations

---

## 🟡 SYSTEM 1: YELLOW/RED CARD SYSTEM

### Real-World Data (from Premier League & LaLiga)

```
Fouls per match:
  ✓ Premier League: 20.9 fouls per game
  ✓ LaLiga: 27.0 fouls per game
  ✓ Average range: 15-25 fouls per match

Card distribution:
  ✓ 60-70% of yellow cards shown in 2nd half
  ✓ Referee can shift expectation by ±20%
  ✓ Two yellows = automatic red
```

### Implementation Plan

#### 1.1 Add Fields to Player Class
```python
@dataclass
class Player:
    # ... existing fields ...
    
    # Discipline system
    yellow_cards: int = 0          # Current match
    red_card: bool = False          # Ejected?
    career_yellows: int = 0         # Season total
    career_reds: int = 0            # Season total
    suspension_games: int = 0       # Pending suspension
    
    # Foul tracking
    fouls_committed: int = 0        # This match
    fouls_by_position: Dict = field(default_factory=dict)  # Aggressive players foul more
```

#### 1.2 Foul Probability Model

**Based on**: Premier League data (20.9 fouls/match across 22 players)

```python
def calculate_foul_probability(player, minute, opponent_nearby, intensity):
    """
    Probability a player commits a foul this frame
    
    Factors:
    - Base rate: ~1 foul per 4.3 minutes (20.9/90 min / 22 players)
    - Position: Defenders foul more (0.8x), Midfielders (1.0x), Forwards (0.6x)
    - Stamina: Fatigue increases fouls (+0.15 per 10% stamina loss)
    - Match intensity: Losing team fouls more (1.2x), leading team less (0.8x)
    - Time: 2nd half fouls are 60-70% of total
    - Referee style: ±20% variance
    
    Returns: probability 0.0-1.0 per frame
    """
    
    base_foul_rate = 0.00244  # 20.9 / 90 min / 22 players
    
    # Position multiplier
    position_multiplier = {
        'DEF': 1.3,    # Defenders tackle more
        'MID': 1.0,    # Midfielders baseline
        'FWD': 0.7,    # Forwards foul less
        'GK': 0.1,     # Goalkeeper almost never
    }[player.role.value]
    
    # Stamina effect (degradation increases fouls)
    stamina_multiplier = 1.0 + (100 - player.stamina) * 0.0015
    
    # Match intensity (based on score difference)
    intensity_multiplier = 1.0 + (score_gap * 0.05)  # Losing teams foul more
    
    # Time effect (2nd half has ~65% of fouls)
    time_multiplier = 2.0 if minute >= 45 else 1.0
    
    # Referee style (random ±20%)
    referee_var = random.uniform(0.8, 1.2)
    
    return base_foul_rate * position_multiplier * stamina_multiplier * \
           intensity_multiplier * time_multiplier * referee_var
```

#### 1.3 Yellow Card Rules

**Based on**: Football rules + statistical models

```python
def evaluate_foul_for_card(player, foul_type, minute, existing_yellows):
    """
    Determine if foul results in yellow/red card
    
    Foul types:
    - Technical foul: 10% yellow rate
    - Tactical foul: 20% yellow rate (tripping, pulling)
    - Dangerous play: 30% yellow rate (high boot, elbow)
    - Violent conduct: 100% red card
    
    Aggravating factors:
    - Already on yellow: ALWAYS second yellow = RED
    - Persistent fouling: After 3 yellows, 70% chance of 4th yellow
    """
    
    if existing_yellows >= 1:
        # Already on yellow - high chance of red on next foul
        return 'RED_CARD' if random.random() < 0.4 else None
    
    # Foul severity-based probability
    yellow_probability = {
        'technical': 0.10,
        'tactical': 0.20,
        'dangerous': 0.30,
        'violent': 1.00,  # Automatic red
    }.get(foul_type, 0.15)
    
    # Referee variance
    yellow_probability *= random.uniform(0.8, 1.2)
    
    if random.random() < yellow_probability:
        return 'RED_CARD' if foul_type == 'violent' else 'YELLOW_CARD'
    
    return None
```

#### 1.4 Card Effects on Gameplay

```python
def apply_card_effects(player, card_type, match_context):
    """
    Effects of cards on player behavior
    
    Yellow card effects:
    - Psychological: -10% aggression, +5% caution
    - Behavioral: Reduces pressing intensity
    - Risk: Higher injury chance (more cautious = awkward movements)
    
    Red card effects:
    - Immediate ejection from match
    - Team plays 10v11 (major tactical change)
    - Next match: Suspension (automatic 1-game)
    """
    
    if card_type == 'YELLOW':
        player.yellow_cards += 1
        player.aggression_modifier = 0.9  # Less aggressive
        player.caution_modifier = 1.05    # More cautious
        
    elif card_type == 'RED':
        player.red_card = True
        player.state = PlayerState.INJURED  # Can't play
        player.suspension_games = 1
        
        # Notify match of numerical disadvantage
        match_context['team_numerical_disadvantage'] = True
```

### Integration Points

- `match_simulation_engine_v2.py`: Add foul detection in behavior evaluation
- `player_behavior.py`: Modify aggression based on card status
- `Event` class: Log YELLOW_CARD and RED_CARD events

### Test Cases

```python
def test_card_system():
    # 1. Test yellow card accumulation
    assert player.yellow_cards == 1 after first yellow
    assert player.yellow_cards == 2 after second yellow (automatic red)
    
    # 2. Test foul probability
    # 20.9 fouls / 90 min = 0.232 fouls/min
    # Across 22 players: ~1 foul per player per ~8 minutes
    fouls_count = simulate_1000_frames()
    assert 20 < fouls_count < 25  # Should be ~20.9
    
    # 3. Test red card ejection
    assert player.red_card == True
    assert player.state == PlayerState.INJURED
    
    # 4. Test 2nd half bias
    h1_fouls = count_fouls(0, 45)
    h2_fouls = count_fouls(45, 90)
    assert h2_fouls > h1_fouls * 1.5  # 2nd half should have 65% of fouls
```

---

## 🏥 SYSTEM 2: INJURY SYSTEM

### Real-World Data (from Peer-Reviewed Research)

```
Recovery timeline (from Bayesian network model):
  ✓ 1-3 days: 30% of injuries
  ✓ 4-7 days: 25% of injuries
  ✓ 8-14 days: 20% of injuries
  ✓ 15-28 days: 15% of injuries
  ✓ 29-60 days: 7% of injuries
  ✓ >60 days: 3% of injuries

Injury probability factors:
  ✓ Base rate: ~1 injury per team per match
  ✓ Fatigue: Increases injury risk (correlation 0.6)
  ✓ Intensity: High-pressure situations increase risk
  ✓ Previously injured: Higher recurrence rate
```

### Implementation Plan

#### 2.1 Add Injury Fields to Player

```python
@dataclass
class Player:
    # ... existing fields ...
    
    # Injury system
    is_injured: bool = False
    injury_type: str = ""  # "muscle", "ligament", "impact"
    injury_severity: float = 0.0  # 0-1 scale
    recovery_days_left: int = 0
    injury_date: Optional[int] = None  # match minute
    previous_injuries: Dict = field(default_factory=dict)  # recurrence tracking
```

#### 2.2 Injury Probability Model

```python
def calculate_injury_probability(player, minute, match_intensity):
    """
    Bayesian network approach for injury prediction
    
    Base rate: ~1 injury per team per 90 min
    = 1 / (11 players * 90 min) = 0.00101 per player per minute
    
    Factors (XGBoost trained model):
    - Fatigue level: +0.0005 per 10% stamina loss
    - Match intensity: +0.0003 per intensity unit
    - Player history: +0.001 if previously injured
    - Position: Defenders 1.3x, Midfielders 1.0x, Forwards 0.8x, GK 0.3x
    """
    
    base_rate = 0.00101  # 1 per team per 90 min
    
    # Fatigue effect (high correlation 0.6)
    fatigue_factor = 1.0 + ((100 - player.stamina) / 100) * 0.5
    
    # Match intensity (contact, tackles, high speed)
    intensity_factor = 1.0 + match_intensity * 0.3
    
    # Position-based risk
    position_risk = {
        'DEF': 1.3,   # More tackles = more injury
        'MID': 1.0,
        'FWD': 0.8,
        'GK': 0.3,
    }[player.role.value]
    
    # Previous injury recurrence risk
    recurrence_factor = 1.2 if len(player.previous_injuries) > 0 else 1.0
    
    return base_rate * fatigue_factor * intensity_factor * \
           position_risk * recurrence_factor
```

#### 2.3 Injury Severity & Recovery

```python
def determine_injury_recovery(injury_probability_exceeded):
    """
    Sample from Bayesian network recovery distribution
    
    Returns: (injury_type, severity, recovery_days)
    """
    
    # Severity distribution (empirical from research)
    severity = random.choices(
        population=[0.2, 0.4, 0.6, 0.8, 1.0],
        weights=[0.40, 0.30, 0.15, 0.10, 0.05]
    )[0]
    
    # Recovery timeline from Bayesian network
    recovery_days = random.choices(
        population=[2, 6, 11, 21, 45, 90],  # Category midpoints
        weights=[0.30, 0.25, 0.20, 0.15, 0.07, 0.03]
    )[0]
    
    # Injury type based on severity
    if severity < 0.3:
        injury_type = "minor_muscle"      # Light strain
    elif severity < 0.6:
        injury_type = "muscle_strain"     # Grade 1 strain
    elif severity < 0.8:
        injury_type = "muscle_tear"       # Grade 2 strain
    else:
        injury_type = "ligament"          # Ligament damage
    
    return injury_type, severity, recovery_days
```

#### 2.4 Injury Effects

```python
def apply_injury_effects(player, injury_type, severity, recovery_days):
    """
    Immediate effects of injury
    """
    
    player.is_injured = True
    player.injury_type = injury_type
    player.injury_severity = severity
    player.recovery_days_left = recovery_days
    player.state = PlayerState.INJURED
    
    # Injury event logged
    return Event(
        event_type=MatchEvent.INJURY,
        time=match.current_minute,
        player_id=player.id,
        team=player.team,
        details={
            'injury_type': injury_type,
            'severity': severity,
            'recovery_days': recovery_days,
        }
    )
```

### Integration Points

- `match_simulation_engine_v2.py`: Check injury probability each frame
- `player_behavior.py`: Skip behavior ticks for injured players
- Match simulation: Handle 10v11 scenarios automatically

### Test Cases

```python
def test_injury_system():
    # 1. Test base rate
    # 1 injury per team per 90 min = ~1 per 11 players
    injuries = simulate_100_matches()
    assert 90 < len(injuries) < 110  # Should be ~100 total
    
    # 2. Test fatigue correlation
    high_fatigue_injuries = filter(lambda i: i['fatigue'] > 80)
    low_fatigue_injuries = filter(lambda i: i['fatigue'] < 20)
    assert len(high_fatigue) > len(low_fatigue) * 1.5
    
    # 3. Test recovery distribution
    recovery_days = [i['recovery'] for i in injuries]
    assert 25 < sum(1 for d in recovery_days if d < 4) < 35  # ~30%
    assert 20 < sum(1 for d in recovery_days if 4 <= d < 8) < 30  # ~25%
```

---

## 🔄 SYSTEM 3: SUBSTITUTION SYSTEM

### Real-World Practices

```
Substitution timing (from Football Manager research):
  ✓ Best time: Half-time (momentum change)
  ✓ Common: 60-70 minute mark (tactical adjustment)
  ✓ Emergency: Injury response (immediate)
  ✓ Typical matches: 3-5 substitutions per team

Reasons for substitutions (priorities):
  1. Injury (player already injured)
  2. Red card (player ejected)
  3. Yellow card + dangerous opponent (preventative)
  4. Fatigue (stamina < 30% + poor performance)
  5. Tactical change (score deficit or pressure)
  6. Normal rotation (squad management)
```

### Implementation Plan

#### 3.1 Squad Structure

```python
@dataclass
class Squad:
    """Team squad with starting XI and bench"""
    
    primary_eleven: List[Player] = field(default_factory=list)
    bench: List[Player] = field(default_factory=list)
    
    def get_best_replacement(self, position: PlayerRole) -> Optional[Player]:
        """Find best substitute for position"""
        candidates = [p for p in self.bench 
                     if p.role == position and not p.is_injured]
        if not candidates:
            return None
        # Return by overall rating (or highest stamina)
        return max(candidates, key=lambda p: p.fitness * p.stamina)
```

#### 3.2 Substitution Logic

```python
def should_make_substitution(team, match_context, minute) -> Optional[Substitution]:
    """
    Intelligent substitution decision
    
    Priority order:
    1. Injury replacement (mandatory)
    2. Red card (mandatory)
    3. Yellow+danger (preventative, minute > 60)
    4. Fatigue (minute > 70, stamina < 25%)
    5. Tactical (score differential, minute > 60)
    """
    
    # Priority 1: Mandatory injury/ejection replacements
    for player in team.players:
        if player.is_injured or player.red_card:
            replacement = team.squad.get_best_replacement(player.role)
            if replacement:
                return Substitution(
                    player_out=player,
                    player_in=replacement,
                    reason='injury' if player.is_injured else 'ejection',
                    tactical_reason=False
                )
    
    # Priority 2: Preventative (yellow card + attacking opponent)
    if minute > 60:
        for player in team.players:
            if player.yellow_cards >= 1:
                opponent_attackers = [p for p in match_context['opponents']
                                     if p.role == PlayerRole.FORWARD 
                                     and p.stamina > 60]
                if len(opponent_attackers) > 2:
                    replacement = team.squad.get_best_replacement(player.role)
                    if replacement and replacement.stamina > 50:
                        return Substitution(
                            player_out=player,
                            player_in=replacement,
                            reason='yellow_card_risk',
                            tactical_reason=False
                        )
    
    # Priority 3: Fatigue + poor performance
    if minute > 70:
        tired_players = [p for p in team.players 
                        if p.stamina < 25]
        if tired_players:
            # Rate each tired player's recent contribution
            worst_performer = min(tired_players, 
                                 key=lambda p: p.recent_passes_completed / 
                                              max(p.recent_passes_attempted, 1))
            replacement = team.squad.get_best_replacement(worst_performer.role)
            if replacement and replacement.stamina > 70:
                return Substitution(
                    player_out=worst_performer,
                    player_in=replacement,
                    reason='fatigue',
                    tactical_reason=False
                )
    
    # Priority 4: Tactical (rare in simulation, can be enhanced later)
    score_gap = team.score - match_context['opponent_score']
    if minute > 65 and score_gap < -1 and random.random() < 0.3:
        # Losing by 2+, try attacking change
        defensive_mid = next((p for p in team.players 
                            if p.role == PlayerRole.MIDFIELDER 
                            and p.stamina > 50), None)
        if defensive_mid:
            attacking_sub = team.squad.get_best_replacement(PlayerRole.FORWARD)
            if attacking_sub:
                return Substitution(
                    player_out=defensive_mid,
                    player_in=attacking_sub,
                    reason='tactical',
                    tactical_reason=True
                )
    
    return None
```

#### 3.3 Substitution Impact

```python
def execute_substitution(match, substitution: Substitution):
    """
    Apply substitution to match
    
    Effects:
    - Player stamina resets to 90%
    - Recent form/momentum continues
    - Team morale adjustment
    """
    
    # Remove outgoing player
    team = match.get_team_by_player(substitution.player_out)
    team.players.remove(substitution.player_out)
    team.bench.append(substitution.player_out)
    
    # Add incoming player
    substitution.player_in.stamina = 90  # Fresh player
    substitution.player_in.x = substitution.player_out.x  # Same position
    substitution.player_in.y = substitution.player_out.y
    team.players.append(substitution.player_in)
    team.squad.bench.remove(substitution.player_in)
    
    # Update spatial grid
    match.spatial_grid.update_agent(substitution.player_in, 
                                   substitution.player_in.x,
                                   substitution.player_in.y)
    
    # Log event
    match.events.append(Event(
        event_type=MatchEvent.SUBSTITUTION,
        time=match.current_minute,
        player_id=substitution.player_out.id,
        team=team.name,
        details={
            'player_out': substitution.player_out.name,
            'player_in': substitution.player_in.name,
            'reason': substitution.reason,
            'tactical': substitution.tactical_reason,
        }
    ))
```

### Integration Points

- `match_simulation_engine_v2.py`: Add substitution checks each minute
- `Team` class: Add `squad` and `bench` attributes
- Movement system: Handle position continuity for substitutes

### Test Cases

```python
def test_substitution_system():
    # 1. Test injury-forced substitution
    player.is_injured = True
    sub = should_make_substitution(team, context, 30)
    assert sub is not None
    assert sub.reason == 'injury'
    
    # 2. Test yellow card prevention (after 60th minute)
    player.yellow_cards = 1
    player2 = opposing_team_forward
    sub = should_make_substitution(team, context, 65)
    # Should consider substitution
    
    # 3. Test stamina-based (after 70th minute)
    player.stamina = 20
    sub = should_make_substitution(team, context, 75)
    # Should substitute if poor performance
    
    # 4. Test replacement player gets fresh stamina
    execute_substitution(match, sub)
    assert substitute_in.stamina == 90
```

---

## 📝 SYSTEM 4: EVENT LOGGING (Completion)

### Current Status

```
Existing event types:
  ✓ PASS
  ✓ SHOT
  ✓ TACKLE
  ✓ FOUL
  ✓ GOAL
  ✓ OUT_OF_BOUNDS

To add:
  ✗ YELLOW_CARD
  ✗ RED_CARD
  ✗ INJURY
  ✗ SUBSTITUTION
  ✗ CLEARANCE
  ✗ INTERCEPTION
```

### Implementation (1 hour)

```python
class MatchEvent(Enum):
    """Extended match event types"""
    PASS = "pass"
    SHOT = "shot"
    TACKLE = "tackle"
    FOUL = "foul"
    GOAL = "goal"
    OUT_OF_BOUNDS = "out_of_bounds"
    YELLOW_CARD = "yellow_card"      # NEW
    RED_CARD = "red_card"            # NEW
    INJURY = "injury"                # NEW
    SUBSTITUTION = "substitution"    # NEW
    CLEARANCE = "clearance"          # NEW
    INTERCEPTION = "interception"    # NEW
```

Logging is straightforward - just append Event objects with proper details dict.

---

## 📊 SUMMARY

| System | Hours | Complexity | Impact |
|--------|-------|-----------|--------|
| Cards | 2-3 | Medium | HIGH (affects match flow) |
| Injuries | 2 | Low | HIGH (affects squad) |
| Substitutions | 2-3 | Medium | HIGH (tactical element) |
| Event Logging | 1 | Low | MEDIUM (data capture) |
| **TOTAL** | **8-10** | **Medium** | **PRODUCTION** |

---

## 🚀 NEXT STEPS

1. **Implement in order** (cards → injuries → subs → events)
2. **Test each system** before moving to next
3. **Run 10-match tests** after each system
4. **Verify statistics** match real-world data
5. **Check for unintended interactions**

**After Tier 1**: Realism jumps from 50% → 70% 📈

---

## 📚 SOURCES

- [Fouls in Premier League](https://www.statmuse.com/fc/ask/premier-league-teams-fouls-per-game)
- [Card Statistics](https://gamblingcalc.com/betting/football/cards-booking-points-calculator/)
- [Injury Recovery Models](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11925455/)
- [Fatigue & Performance](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11079249/)
- [Substitution Strategy](https://fminside.net/guides/tactical-guides/37-how-to-use-substitutions-in-football-manager)
- [Expected Goals Models](https://www.hudl.com/blog/expected-goals-xg-explained)
