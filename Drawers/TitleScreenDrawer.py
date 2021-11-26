import pygame


def draw(self):
    # draw the title screen main logo
    what_to_draw = pygame.transform.scale(self.beginning, (self.screen.get_width(), int(6*self.unitsizey)))
    self.screen.blit(what_to_draw, pygame.rect.Rect(self.screen.get_width()/2 - what_to_draw.get_width()/2,
                                                    2*self.unitsizey, what_to_draw.get_width(),
                                                    what_to_draw.get_height()))

    # draw the sparkling effect
    if self.sparkle_pattern[self.sparkle_step] > -1:
        what_to_draw = pygame.transform.scale(self.sparkle.subsurface(
            pygame.rect.Rect(self.sparkle_pattern[self.sparkle_step] * 72 + self.sparkle_pattern[self.sparkle_step] + 1,
                             1, 72, 120)), (2*self.unitsizex, 4*self.unitsizey))
        self.screen.blit(what_to_draw, pygame.rect.Rect(10.75*self.unitsizex, 3.15*self.unitsizey,
                                                        what_to_draw.get_width(), what_to_draw.get_height()))
    self.sparkle_ticks += self.delta_ticks
    if self.sparkle_ticks > 30:
        self.sparkle_ticks = 0
        self.sparkle_step += 1
        if self.sparkle_step >= len(self.sparkle_pattern):
            self.sparkle_step = 0

    if self.screen_mode == "Screen Title With Intro":
        _text_lines = ["   USE YOUR Z AND X KEYS TO PLAY",
                       "   NINTENDO (C) ENIX 1986 & 1989",
                       "           JKGAMES, 2016        ",
                       "    ... Entirely in Python! ... ",
                       "   Programmer:  Dr. Joseph Krall"]
        _h = self.screen.get_height()
        _w = 0.85 * self.unitsizex
        for i, text in enumerate(_text_lines):
            if i == 0:
                self.screen.blit(self.gamefont.render(text, False, (252, 152, 56)), (_w, _h * 0.60))
            else:
                self.screen.blit(self.gamefont.render(text, False, (244, 120, 252)), (_w, _h * (0.65 + 0.05*i)))
