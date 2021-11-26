def draw(self):
    self.adventure_log_box.increment_ticks(self.delta_ticks)
    _logs = self.new_game_logs if self.select_available_log else self.available_adventure_logs
    size_y = len(_logs) + 1.5
    if size_y != self.adventure_log_box.num_cells_high:
        self.adventure_log_box.redefine_surface(self.adventure_log_box.num_cells_wide, size_y)
    self.adventure_log_box.draw(self.screen)
    self.adventure_log_box.fill(self.black)
    self.adventure_log_box.draw_border(self.menu_color)
    for i, log in enumerate(_logs):
        self.adventure_log_box.draw_string("ADVENTURE LOG " + str(log), self.gamefont, self.menu_color, 1, 1+i)
    self.adventure_log_box.draw_selector(self.command_selector)
