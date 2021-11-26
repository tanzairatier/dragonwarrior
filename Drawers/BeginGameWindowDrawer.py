def draw(self):
    self.begin_game_box.increment_ticks(self.delta_ticks)
    size_y = (1 if self.available_adventure_logs else 0) + (1 if self.new_game_logs else 0)
    if (size_y + 1.5) != self.begin_game_box.num_cells_high:
        self.begin_game_box.redefine_surface(self.begin_game_box.num_cells_wide, size_y + 1.5)
    self.begin_game_box.draw(self.screen)
    self.begin_game_box.fill(self.black)
    self.begin_game_box.draw_border(self.menu_color)

    if self.new_game_logs:
        self.begin_game_box.draw_string("BEGIN A NEW QUEST", self.gamefont, self.menu_color, 1, 1)
    if self.new_game_logs and self.available_adventure_logs:
        self.begin_game_box.draw_string("CONTINUE A QUEST", self.gamefont, self.menu_color, 1, 2)
    elif self.available_adventure_logs:
        self.begin_game_box.draw_string("CONTINUE A QUEST", self.gamefont, self.menu_color, 1, 1)
    self.begin_game_box.draw_selector(self.command_selector)
