import pygame
import random
import os

ICON_COLORS = {0: 'w', 1: 'b'}
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
MENU_COLOR = pygame.Color((72, 61, 139))
win.fill(MENU_COLOR)
LOGO_COLOR = ICON_COLORS[random.randint(0, 1)]
MAIN_MENU_LOGO = pygame.transform.scale(
    pygame.image.load(os.path.join("../images", LOGO_COLOR + "_game_name.png")), (400, 400))
LOGO_POSITION = (pygame.display.Info().current_w // 2 - 200, pygame.display.Info().current_h // 2 - 300)
win.blit(MAIN_MENU_LOGO, LOGO_POSITION)
pygame.display.update()
