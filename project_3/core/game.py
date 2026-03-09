import pygame
from settings import WIDTH, HEIGHT, FPS
from scenes.scene_manager import SceneManager
from scenes.menu_scene import MenuScene

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tank Raid")
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene_manager = SceneManager(MenuScene(self))

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.scene_manager.handle_events(event)

            self.scene_manager.update()
            self.scene_manager.draw(self.screen)
            pygame.display.flip()
