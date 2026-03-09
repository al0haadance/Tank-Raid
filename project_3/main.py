import pygame
from core.game import Game

if __name__ == "__main__":
    pygame.init()
    try:
        pygame.mixer.init()
    except:
        print("No sound")

    game = Game()
    game.run()
    pygame.quit()
