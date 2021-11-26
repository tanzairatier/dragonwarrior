import pygame


class Window:
    def __init__(self, num_cells_wide, num_cells_high, cell_width, cell_height, draw_ticks_speed, x, y):
        self.unit_size_x = cell_width
        self.unit_size_y = cell_height
        self.num_cells_wide = num_cells_wide
        self.num_cells_high = num_cells_high
        self.draw_ticks_speed = float(draw_ticks_speed)
        self.draw_ticks = 0.0
        self._total_ticks = 0
        self.selector_y = 0
        self.selector_x = 0
        self.x = x
        self.y = y
        self.surface = pygame.Surface((self.unit_size_x * self.num_cells_wide, self.unit_size_y * self.num_cells_high))

    def redefine_surface(self, num_cells_wide, num_cells_high):
        self.num_cells_wide = num_cells_wide
        self.num_cells_high = num_cells_high
        self.surface = pygame.Surface((self.unit_size_x * self.num_cells_wide, self.unit_size_y * self.num_cells_high))

    def _get_partial_surface(self):
        return self.surface.subsurface(pygame.rect.Rect(0, 0, self.num_cells_wide * self.unit_size_x, int(
            self.surface.get_height() * (self.draw_ticks / self.draw_ticks_speed))))

    def draw(self, screen, bump_x=0, bump_y=0):
        screen.blit(self._get_partial_surface(), ((self.x + (2 * bump_x/32.0)) * self.unit_size_x,
                                                  (self.y + (2 * bump_y/32.0)) * self.unit_size_y))

    def increment_ticks(self, delta_ticks):
        self.draw_ticks += delta_ticks
        self._total_ticks += delta_ticks
        if self.draw_ticks >= self.draw_ticks_speed:
            self.draw_ticks = self.draw_ticks_speed

    def fill(self, color):
        self.surface.fill(color)

    def reset(self):
        self.draw_ticks = 0
        self.selector_y = 0

    def draw_border(self, color):
        pygame.draw.rect(self.surface,
                         color,
                         (self.unit_size_x / 8, self.unit_size_x / 8,
                          self.surface.get_width() - self.unit_size_x / 4,
                          self.surface.get_height() - self.unit_size_y / 4 - self.unit_size_x / 16),
                         self.unit_size_x / 8)

    def draw_label(self, label, font, color):
        # clear space for the label on top of border
        label = " " + label + " "
        width = font.size(label)[0]

        pygame.draw.rect(self.surface, (0, 0, 0),
                         ((self.surface.get_width() - width)/2, 0 * self.unit_size_y,
                          width,
                          1 * self.unit_size_y),
                         0)
        self.surface.blit(font.render(label, False, color),
                          ((self.surface.get_width() - width)/2, 0 * self.unit_size_y))

    def draw_string(self, string, font, color, x, y):
        self.surface.blit(font.render(string, True, color), (x * self.unit_size_x, y * self.unit_size_y))

    def draw_selector(self, selector_image, mod_x=1, mod_y=1, rotate=0, shift_x=0, shift_y=1):
        if self._total_ticks % 500 <= 250:
            self.surface.blit(pygame.transform.rotate(
                pygame.transform.scale(selector_image, (self.unit_size_x, self.unit_size_y)), rotate),
                              pygame.rect.Rect((shift_x + self.selector_x*mod_x) * self.unit_size_x,
                                               (shift_y + self.selector_y*mod_y) * self.unit_size_y,
                                               self.unit_size_x,
                                               self.unit_size_y))
