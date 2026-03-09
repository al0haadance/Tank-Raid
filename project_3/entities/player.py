import pygame
from settings import PLAYER_SPEED, WIDTH, PLAYER_LIVES
from entities.base_entity import BaseEntity
from entities.bullet import Bullet

class Player(BaseEntity):
    def __init__(self):
        super().__init__((0, 255, 0), WIDTH//2, 500)
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0
        self.lives = PLAYER_LIVES

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        if keys[pygame.K_SPACE] and self.shoot_cooldown == 0:
            self.shoot()
            self.shoot_cooldown = 15

    def shoot(self):
        self.bullets.add(Bullet(self.rect.centerx, self.rect.top))

    def update(self):
        self.handle_input()
        self.bullets.update()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

