import pygame
import sys
import database
from game import GameEngine
from ui import Button, draw_text, BLACK, GREEN, WHITE
from screens.squad import SquadScreen
from screens.match import MatchScreen

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 60

class ScreenManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Retro Manager Football")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 32)
        self.engine = GameEngine()
        
        # Menu Buttons
        self.btn_new_game = Button(WIDTH//2 - 100, 250, 200, 50, "Novo Jogo", self.font_menu)
        self.btn_load_game = Button(WIDTH//2 - 100, 320, 200, 50, "Carregar Jogo", self.font_menu)
        self.btn_exit = Button(WIDTH//2 - 100, 390, 200, 50, "Sair", self.font_menu)
        
        # Hub Buttons
        self.btn_match = Button(WIDTH - 220, 20, 200, 50, "Jogar Partida", self.font_menu, color=GREEN)
        self.btn_save = Button(WIDTH - 220, 80, 200, 50, "Salvar Jogo", self.font_menu)
        self.btn_squad = Button(20, 530, 200, 50, "Ver Elenco", self.font_menu)
        
        self.match_result = ""
        self.squad_screen = None # Initialized after engine has teams
        self.match_screen = None  # Visual match screen (initialized when needed)

    def run(self):
        while self.engine.running:
            if self.engine.current_screen == "MENU":
                self.menu_loop()
            elif self.engine.current_screen == "HUB":
                if not self.squad_screen:
                    self.squad_screen = SquadScreen(self.screen, self.engine, self.font_menu)
                self.hub_loop()
            elif self.engine.current_screen == "MATCH":
                self.match_loop()
            elif self.engine.current_screen == "SQUAD":
                self.squad_loop()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

    def menu_loop(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            
            if self.btn_new_game.is_clicked(event, mouse_pos):
                self.engine.new_game()
            if self.btn_load_game.is_clicked(event, mouse_pos):
                if self.engine.load_game():
                    print("Jogo carregado!")
                else:
                    print("Nenhum save encontrado.")
            if self.btn_exit.is_clicked(event, mouse_pos):
                self.engine.running = False

        self.btn_new_game.update(mouse_pos)
        self.btn_load_game.update(mouse_pos)
        self.btn_exit.update(mouse_pos)

        self.screen.fill(GREEN)
        draw_text(self.screen, "RETRO MANAGER", self.font_title, WHITE, WIDTH//2, 100, center=True)
        draw_text(self.screen, "FOOTBALL", self.font_title, WHITE, WIDTH//2, 170, center=True)
        
        self.btn_new_game.draw(self.screen)
        self.btn_load_game.draw(self.screen)
        self.btn_exit.draw(self.screen)

    def hub_loop(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.engine.current_screen = "MENU"
            
            if self.btn_match.is_clicked(event, mouse_pos):
                opponent = database.random.choice([t for t in self.engine.teams if t != self.engine.player_team])
                # Initialize and start visual match screen
                if not self.match_screen:
                    self.match_screen = MatchScreen(self.screen, self.engine, self.font_menu)
                self.match_screen.start_match(self.engine.player_team, opponent)
                self.engine.current_screen = "MATCH"
            
            if self.btn_save.is_clicked(event, mouse_pos):
                self.engine.save_game()
            
            if self.btn_squad.is_clicked(event, mouse_pos):
                self.engine.current_screen = "SQUAD"

        self.btn_match.update(mouse_pos)
        self.btn_save.update(mouse_pos)
        self.btn_squad.update(mouse_pos)

        self.screen.fill(BLACK)
        draw_text(self.screen, f"Time: {self.engine.player_team.name}", self.font_menu, WHITE, 20, 20)
        draw_text(self.screen, f"Fundos: ${self.engine.funds}", self.font_menu, WHITE, 20, 60)
        draw_text(self.screen, "Pressione ESC para voltar ao menu", self.font_menu, WHITE, WIDTH//2, HEIGHT - 50, center=True)
        
        # Display squad summary
        draw_text(self.screen, "ELENCO:", self.font_menu, WHITE, 20, 120)
        for i, player in enumerate(self.engine.player_team.players[:10]): # Show first 10
            color = WHITE if not player.star else (255, 215, 0) # Gold for stars
            text = f"{player.position} - {player.name} (Avg: {player.get_average_force()})"
            draw_text(self.screen, text, self.font_menu, color, 40, 160 + (i * 35))

        # Draw match result if exists
        if self.match_result:
            pygame.draw.rect(self.screen, (50, 50, 50), (WIDTH//2 - 250, HEIGHT - 150, 500, 100))
            draw_text(self.screen, self.match_result, self.font_menu, (255, 255, 0), WIDTH//2, HEIGHT - 100, center=True)

        self.btn_match.draw(self.screen)
        self.btn_save.draw(self.screen)
        self.btn_squad.draw(self.screen)

    def match_loop(self):
        # Handle events and update visual match screen
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.engine.current_screen = "HUB"
            if self.match_screen:
                self.match_screen.handle_event(event, mouse_pos)

        if self.match_screen:
            self.match_screen.update()
            self.match_screen.draw()

    def squad_loop(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            self.squad_screen.handle_event(event, mouse_pos)
        
        self.squad_screen.draw()

if __name__ == "__main__":
    manager = ScreenManager()
    manager.run()
