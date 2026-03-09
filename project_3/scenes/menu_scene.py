import random
import pygame

from scenes.game_scene import GameScene
from settings import WIDTH, HEIGHT


class MenuScene:
    def __init__(self, game):
        self.game = game
        self.title_font = pygame.font.SysFont("consolas", 72, bold=True)
        self.menu_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.info_font = pygame.font.SysFont("consolas", 22)

        self.options = ["Start Battle", "Exit"]
        self.selected = 0
        self.timer = 0
        self.stars = []
        for _ in range(55):
            self.stars.append(
                [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)]
            )

    def handle_events(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.selected == 0:
                self.game.scene_manager.change_scene(GameScene(self.game))
            else:
                self.game.running = False
        elif event.key == pygame.K_ESCAPE:
            self.game.running = False

    def update(self):
        self.timer += 1
        for star in self.stars:
            star[1] += star[2] * 0.35
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = -5

    def draw(self, screen):
        self._draw_background(screen)

        title_shadow = self.title_font.render("TANK RAID", True, (20, 20, 20))
        title = self.title_font.render("TANK RAID", True, (230, 235, 250))
        screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 83))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = self.info_font.render("Arcade Campaign", True, (170, 210, 220))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 160))

        panel = pygame.Rect(WIDTH // 2 - 180, 220, 360, 180)
        pygame.draw.rect(screen, (20, 30, 40), panel, border_radius=12)
        pygame.draw.rect(screen, (80, 140, 165), panel, 2, border_radius=12)

        for index, option in enumerate(self.options):
            y = panel.y + 42 + index * 62
            is_selected = index == self.selected
            pulse = 20 if is_selected and (self.timer // 20) % 2 == 0 else 0
            color = (255, 230, 120) if is_selected else (205, 215, 230)
            text = self.menu_font.render(option, True, color)
            marker = self.menu_font.render(">", True, (255, 230 + pulse, 120))
            text_x = WIDTH // 2 - text.get_width() // 2
            screen.blit(text, (text_x, y))
            if is_selected:
                screen.blit(marker, (text_x - 34, y))

        controls = [
            "Move tank: WASD or Arrows",
            "Shoot: Space",
            "Menu navigation: Up / Down + Enter",
            "In game: R - restart level, Esc - back to menu",
        ]
        for idx, line in enumerate(controls):
            hint = self.info_font.render(line, True, (175, 190, 210))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 440 + idx * 30))

    def _draw_background(self, screen):
        top = (18, 28, 45)
        bottom = (10, 14, 22)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            color = (
                int(top[0] * (1 - ratio) + bottom[0] * ratio),
                int(top[1] * (1 - ratio) + bottom[1] * ratio),
                int(top[2] * (1 - ratio) + bottom[2] * ratio),
            )
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        for x in range(0, WIDTH, 40):
            pygame.draw.line(screen, (28, 42, 60), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(screen, (28, 42, 60), (0, y), (WIDTH, y), 1)

        for x, y, size in self.stars:
            pygame.draw.circle(screen, (140, 180, 210), (int(x), int(y)), size)
