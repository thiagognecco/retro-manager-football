import pygame
from ui import Button, draw_text, BLACK, WHITE, GRAY, GOLD

class SquadScreen:
    def __init__(self, screen, engine, font):
        self.screen = screen
        self.engine = engine
        self.font = font
        self.btn_back = Button(20, 530, 150, 40, "Voltar", font)
        
    def draw(self):
        self.screen.fill(BLACK)
        draw_text(self.screen, f"ELENCO - {self.engine.player_team.name}", self.font, WHITE, 400, 30, center=True)
        
        # Table Header
        header_y = 80
        draw_text(self.screen, "POS", self.font, GRAY, 50, header_y)
        draw_text(self.screen, "NOME", self.font, GRAY, 120, header_y)
        draw_text(self.screen, "FIS", self.font, GRAY, 450, header_y)
        draw_text(self.screen, "TEC", self.font, GRAY, 520, header_y)
        draw_text(self.screen, "DEC", self.font, GRAY, 590, header_y)
        draw_text(self.screen, "AVG", self.font, GRAY, 680, header_y)
        
        # Players List
        for i, player in enumerate(self.engine.player_team.players):
            y = 120 + (i * 30)
            if y > 500: break # Simple pagination
            
            color = WHITE if not player.star else GOLD
            draw_text(self.screen, player.position, self.font, color, 50, y)
            draw_text(self.screen, player.name, self.font, color, 120, y)
            draw_text(self.screen, str(player.fis), self.font, color, 450, y)
            draw_text(self.screen, str(player.tec), self.font, color, 520, y)
            draw_text(self.screen, str(player.dec), self.font, color, 590, y)
            draw_text(self.screen, str(player.get_average_force()), self.font, color, 680, y)

        self.btn_back.draw(self.screen)

    def handle_event(self, event, mouse_pos):
        if self.btn_back.is_clicked(event, mouse_pos):
            self.engine.current_screen = "HUB"
        self.btn_back.update(mouse_pos)
