import pygame
from ui import Button, draw_text, BLACK, WHITE, GRAY

class SeasonTableScreen:
    def __init__(self, screen, engine, font):
        self.screen = screen
        self.engine = engine
        self.font = font
        self.btn_back = Button(20, 530, 150, 40, "Voltar", font)

    def draw(self):
        self.screen.fill(BLACK)
        draw_text(self.screen, "CLASSIFICAÇÃO", self.font, WHITE, 400, 20, center=True)

        if not hasattr(self.engine, 'season_manager') or not getattr(self.engine, 'standings', None):
            draw_text(self.screen, "Nenhuma temporada ativa. Inicie uma temporada.", self.font, GRAY, 400, 120, center=True)
            self.btn_back.draw(self.screen)
            return

        standings = self.engine.season_manager.get_sorted_standings(self.engine.standings)

        header_y = 60
        x_positions = {'pos': 50, 'team': 100, 'pj': 320, 'pts': 380, 'gf': 450, 'ga': 520, 'gd': 590}

        draw_text(self.screen, "POS", self.font, GRAY, x_positions['pos'], header_y)
        draw_text(self.screen, "TIME", self.font, GRAY, x_positions['team'], header_y)
        draw_text(self.screen, "PJ", self.font, GRAY, x_positions['pj'], header_y)
        draw_text(self.screen, "PTS", self.font, GRAY, x_positions['pts'], header_y)
        draw_text(self.screen, "GF", self.font, GRAY, x_positions['gf'], header_y)
        draw_text(self.screen, "GA", self.font, GRAY, x_positions['ga'], header_y)
        draw_text(self.screen, "GD", self.font, GRAY, x_positions['gd'], header_y)

        for i, row in enumerate(standings):
            y = header_y + 30 + i * 28
            if y > 500:
                break
            color = WHITE
            draw_text(self.screen, str(i + 1), self.font, color, x_positions['pos'], y)
            draw_text(self.screen, row['team'], self.font, color, x_positions['team'], y)
            draw_text(self.screen, str(row.get('played', 0)), self.font, color, x_positions['pj'], y)
            draw_text(self.screen, str(row['points']), self.font, color, x_positions['pts'], y)
            draw_text(self.screen, str(row['gf']), self.font, color, x_positions['gf'], y)
            draw_text(self.screen, str(row['ga']), self.font, color, x_positions['ga'], y)
            draw_text(self.screen, str(row['gd']), self.font, color, x_positions['gd'], y)

        self.btn_back.draw(self.screen)

    def handle_event(self, event, mouse_pos):
        if self.btn_back.is_clicked(event, mouse_pos):
            self.engine.current_screen = "HUB"
        self.btn_back.update(mouse_pos)
