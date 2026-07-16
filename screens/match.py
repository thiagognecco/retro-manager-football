import pygame
import random
import math
from ui import Button, draw_text, BLACK, WHITE, GREEN, GOLD
import ai

class MatchScreen:
    def __init__(self, screen, engine, font):
        self.screen = screen
        self.engine = engine
        self.font = font
        self.btn_continue = Button(300, 500, 200, 50, "Continuar", font)
        self.width, self.height = self.screen.get_size()
        self.pitch_top = 120
        self.pitch_bottom = self.height - 80
        self.reset()
        self.last_time = pygame.time.get_ticks() if pygame.get_init() else 0

    def reset(self):
        self.timer = 0
        self.minute = 0
        self.score1 = 0
        self.score2 = 0
        self.team1 = None
        self.team2 = None
        self.events = []
        self.finished = False
        self.players = []
        self.ball = None

    def _place_players(self, team1, team2):
        center_x = self.width // 2
        # helper
        def place_team(team, side):
            states = []
            pos_groups = {'GL': [], 'DF': [], 'MC': [], 'AT': []}
            for p in team.players:
                pos_groups.setdefault(p.position, []).append(p)
            if side == 'left':
                xs = {'GL': 80, 'DF': 180, 'MC': 320, 'AT': 460}
            else:
                xs = {'GL': self.width - 80, 'DF': self.width - 180, 'MC': self.width - 320, 'AT': self.width - 460}

            for pos, players in pos_groups.items():
                n = len(players) if players else 1
                spacing = (self.pitch_bottom - self.pitch_top) / (n + 1)
                for i, p in enumerate(players):
                    y = int(self.pitch_top + spacing * (i + 1))
                    x = xs.get(pos, center_x)
                    states.append({
                        'game_player': p,
                        'x': float(x),
                        'y': float(y),
                        'vx': 0.0,
                        'vy': 0.0,
                        'team': 1 if side == 'left' else 2,
                        'has_ball': False
                    })
            return states

        return place_team(team1, 'left') + place_team(team2, 'right')

    def start_match(self, team1, team2):
        # Full reset and initialization
        self.reset()
        self.team1 = team1
        self.team2 = team2
        self.events.append(f"0' - Início de partida: {team1.name} vs {team2.name}")
        self.players = self._place_players(team1, team2)
        center_x = self.width // 2
        center_y = (self.pitch_top + self.pitch_bottom) // 2
        self.ball = {'x': float(center_x), 'y': float(center_y), 'vx': 0.0, 'vy': 0.0, 'possession': None}
        # Give ball to a random player to start
        poss = random.choice(self.players)
        poss['has_ball'] = True
        self.ball['possession'] = poss
        self.ball['x'] = poss['x']
        self.ball['y'] = poss['y']

    def _apply_ball_friction(self, dt, friction=3.0):
        # simple linear decay per second
        if not self.ball:
            return
        vx, vy = self.ball.get('vx', 0.0), self.ball.get('vy', 0.0)
        decay = max(0.0, 1.0 - friction * dt)
        self.ball['vx'] = vx * decay
        self.ball['vy'] = vy * decay
        if math.hypot(self.ball['vx'], self.ball['vy']) < 5.0:
            self.ball['vx'] = 0.0
            self.ball['vy'] = 0.0

    def update(self):
        if not self.finished and self.team1:
            # delta time in seconds
            now = pygame.time.get_ticks()
            dt = (now - getattr(self, 'last_time', now)) / 1000.0 if self.last_time else 1/60.0
            if dt <= 0:
                dt = 1/60.0
            self.last_time = now

            # frame-based minute progression (keeps compatibility with original simple timer)
            self.timer += 1
            if self.timer % 10 == 0:
                self.minute += 1
                if self.minute >= 90:
                    self.finished = True
                    self.events.append(f"90' - Fim de jogo!")

            # If ball is free, check collisions first (pick up)
            if self.ball and self.ball.get('possession') is None:
                for p in self.players:
                    dx = self.ball['x'] - p['x']
                    dy = self.ball['y'] - p['y']
                    if math.hypot(dx, dy) < 18:
                        p['has_ball'] = True
                        self.ball['possession'] = p
                        self.ball['vx'] = 0.0
                        self.ball['vy'] = 0.0
                        break

            # Update player decisions
            team1_players = [p for p in self.players if p['team'] == 1]
            team2_players = [p for p in self.players if p['team'] == 2]

            # Call AI and capture actions for logging
            for p in list(self.players):
                teammates = team1_players if p['team'] == 1 else team2_players
                opponents = team2_players if p['team'] == 1 else team1_players
                had_ball = bool(p.get('has_ball'))
                try:
                    ai.update_player(p, self.ball, teammates, opponents, dt)
                except Exception:
                    # keep simulation robust
                    pass
                # detect kicks (pass/shot)
                if had_ball and not p.get('has_ball') and (self.ball and self.ball.get('possession') is None):
                    speed = math.hypot(self.ball.get('vx', 0.0), self.ball.get('vy', 0.0))
                    # decide if it was a shot based on speed or proximity to goal
                    if p.get('team') == 1:
                        goal_x = 800
                    else:
                        goal_x = 0
                    dist_to_goal = abs(goal_x - p['x'])
                    if speed > 250 or dist_to_goal < 220:
                        self.events.append(f"{self.minute}' - Chute de {p['game_player'].name}")
                    else:
                        self.events.append(f"{self.minute}' - Passe de {p['game_player'].name}")

                # detect steals
                if not had_ball and p.get('has_ball'):
                    self.events.append(f"{self.minute}' - Roubou a bola: {p['game_player'].name}")

            # Integrate player movement and clamp to pitch
            for p in self.players:
                p['x'] += p.get('vx', 0.0) * dt
                p['y'] += p.get('vy', 0.0) * dt
                p['y'] = max(self.pitch_top + 10, min(self.pitch_bottom - 10, p['y']))
                p['x'] = max(20, min(self.width - 20, p['x']))

            # Ball physics when not possessed
            if self.ball.get('possession') is None:
                self.ball['x'] += self.ball['vx'] * dt
                self.ball['y'] += self.ball['vy'] * dt
                # apply friction helper
                self._apply_ball_friction(dt)
                # dynamic pickup after movement
                for p in self.players:
                    if math.hypot(self.ball['x'] - p['x'], self.ball['y'] - p['y']) < 18:
                        p['has_ball'] = True
                        self.ball['possession'] = p
                        self.ball['vx'] = 0.0
                        self.ball['vy'] = 0.0
                        break
            else:
                # attach to possessor
                p = self.ball['possession']
                self.ball['x'] = p['x']
                self.ball['y'] = p['y']
                self.ball['vx'] = 0.0
                self.ball['vy'] = 0.0

            # Goal detection
            goal_top = (self.pitch_top + self.pitch_bottom) / 2 - 60
            goal_bottom = (self.pitch_top + self.pitch_bottom) / 2 + 60
            if self.ball['x'] < 30 and goal_top < self.ball['y'] < goal_bottom:
                # goal for team2 (right side)
                self.score2 += 1
                self.events.append(f"{self.minute}' - GOL de {self.team2.name}!")
                self._after_goal(scoring_team=2)
            elif self.ball['x'] > self.width - 30 and goal_top < self.ball['y'] < goal_bottom:
                self.score1 += 1
                self.events.append(f"{self.minute}' - GOL de {self.team1.name}!")
                self._after_goal(scoring_team=1)

    def _after_goal(self, scoring_team):
        # Re-position players and reset ball to center. Keep events and scoreboard.
        self.players = self._place_players(self.team1, self.team2)
        center_x = self.width // 2
        center_y = (self.pitch_top + self.pitch_bottom) // 2
        self.ball = {'x': float(center_x), 'y': float(center_y), 'vx': 0.0, 'vy': 0.0, 'possession': None}
        # Give ball to a random player from the conceding team
        if scoring_team == 1:
            candidates = [p for p in self.players if p['team'] == 2]
        else:
            candidates = [p for p in self.players if p['team'] == 1]
        if candidates:
            kick = random.choice(candidates)
            kick['has_ball'] = True
            self.ball['possession'] = kick
            self.ball['x'] = kick['x']
            self.ball['y'] = kick['y']

    def draw(self):
        # Background field
        self.screen.fill((20, 80, 20))  # Dark Grass Green

        # Scoreboard
        pygame.draw.rect(self.screen, BLACK, (150, 20, 500, 80))
        draw_text(self.screen, f"{self.team1.name if self.team1 else ''}", self.font, WHITE, 160, 45)
        draw_text(self.screen, f"{self.score1} - {self.score2}", self.font, GOLD, 400, 45, center=True)
        draw_text(self.screen, f"{self.team2.name if self.team2 else ''}", self.font, WHITE, 640, 45)
        draw_text(self.screen, f"{self.minute}'", self.font, WHITE, 400, 110, center=True)

        # Players and ball
        if self.players:
            for p in self.players:
                color = WHITE if not p['game_player'].star else (255, 215, 0)
                px, py = int(p['x']), int(p['y'])
                pygame.draw.circle(self.screen, color, (px, py), 12)
                # draw small name tag
                name = p['game_player'].name.split()[0]
                draw_text(self.screen, name, self.font, BLACK, px, py - 18, center=True)

        if self.ball:
            pygame.draw.circle(self.screen, (255, 255, 255), (int(self.ball['x']), int(self.ball['y'])), 6)

        # Match Log
        log_y = 150
        for ev in self.events[-10:]:  # Last 10 events
            draw_text(self.screen, ev, self.font, WHITE, 50, log_y)
            log_y += 30

        if self.finished:
            self.btn_continue.draw(self.screen)

    def handle_event(self, event, mouse_pos):
        if self.finished:
            if self.btn_continue.is_clicked(event, mouse_pos):
                self.engine.current_screen = "HUB"
            self.btn_continue.update(mouse_pos)
