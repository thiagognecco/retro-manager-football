import pygame

# Colors (tuned for contrast)
WHITE = (250, 250, 250)
BLACK = (18, 18, 18)
GRAY = (80, 80, 80)
GREEN = (34, 139, 34)
GOLD = (255, 200, 50)

def _luminance(color):
    r, g, b = color
    return 0.299 * r + 0.587 * g + 0.114 * b

class Button:
    def __init__(self, x, y, width, height, text, font, color=GRAY, hover_color=GOLD):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        draw_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, draw_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        # Choose text color based on background luminance for readability
        text_color = BLACK if _luminance(draw_color) > 150 else WHITE

        # Render text and ensure it fits inside the button by truncating if needed
        text_surf = self.font.render(self.text, True, text_color)
        max_width = max(10, self.rect.width - 12)
        if text_surf.get_width() > max_width:
            # Simple ellipsize
            txt = self.text
            while txt and self.font.size(txt + '...')[0] > max_width:
                txt = txt[:-1]
            text_surf = self.font.render((txt + '...') if txt else '...', True, text_color)

        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event, mouse_pos):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(mouse_pos)


def draw_text(surface, text, font, color, x, y, center=False, max_width=None):
    # Make sure surface is valid
    sw = surface.get_width()
    sh = surface.get_height()

    # Compute available width to avoid text going off-screen
    if max_width is None:
        if center:
            max_width = sw - 20
        else:
            max_width = max(20, sw - x - 10)

    # Ellipsize if text too wide
    rendered = font.render(text, True, color)
    if rendered.get_width() > max_width:
        txt = text
        while txt and font.size(txt + '...')[0] > max_width:
            txt = txt[:-1]
        text = (txt + '...') if txt else '...'
        rendered = font.render(text, True, color)

    text_rect = rendered.get_rect()
    if center:
        # center at (x,y) but ensure it stays on screen
        text_rect.center = (x, y)
        if text_rect.left < 5:
            text_rect.left = 5
        if text_rect.right > sw - 5:
            text_rect.right = sw - 5
    else:
        text_rect.topleft = (x, y)
        # clamp to screen
        if text_rect.right > sw - 5:
            text_rect.right = sw - 5
        if text_rect.bottom > sh - 5:
            text_rect.bottom = sh - 5

    surface.blit(rendered, text_rect)
