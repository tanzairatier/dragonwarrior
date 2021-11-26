import pygame

def handle_input(self, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_x or event.key == pygame.K_z:
            self.screen_mode = "Screen Title With Intro"