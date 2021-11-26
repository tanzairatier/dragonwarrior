def draw(self):
    self.command_box.increment_ticks(self.delta_ticks)
    self.command_box.draw(self.screen)
    self.command_box.fill(self.black)
    self.command_box.draw_border(self.menu_color)
    self.command_box.draw_label("COMMAND", self.gamefont, self.menu_color)
    for i, row in enumerate([["TALK", "SPELL"], ["STATUS", "ITEM"], ["STAIRS", "DOOR"], ["SEARCH", "TAKE"]]):
        for j, label in enumerate(row):
            self.command_box.draw_string(label, self.gamefont, self.menu_color, 1 + j * 4, 1 + i)
    self.command_box.draw_selector(self.command_selector, mod_x=4)
