import pygame

def check_collision(group1, group2):
    return pygame.sprite.groupcollide(group1, group2, True, True)
