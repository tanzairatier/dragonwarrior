def draw(self):
    self.input_name_box.increment_ticks(self.delta_ticks)
    self.input_name_box.draw(self.screen)
    self.input_name_box.fill(self.black)
    self.input_name_box.draw_border(self.menu_color)
    self.input_name_box.draw_label("NAME", self.gamefont, self.menu_color)
    for i, letter in enumerate(self.name_so_far):
        self.input_name_box.draw_string(letter, self.gamefont, self.menu_color, 1 + i * 0.5, 1)
    self.input_name_box.draw_string("_", self.gamefont, self.menu_color, 1 + self.name_so_far_index * 0.5, 1.15)

    self.select_letters_box.increment_ticks(self.delta_ticks)
    self.select_letters_box.draw(self.screen)
    self.select_letters_box.fill(self.black)
    self.select_letters_box.draw_border(self.menu_color)
    for j, row in enumerate(self.letters):
        for i, letter in enumerate(row):
            self.select_letters_box.draw_string(letter, self.gamefont, self.menu_color, 1 + i, 1 + j)
    self.select_letters_box.draw_string("BACK", self.gamefont, self.menu_color, 1 + 6, 1 + 5)
    self.select_letters_box.draw_string("END", self.gamefont, self.menu_color, 1 + 9, 1 + 5)
    self.select_letters_box.draw_selector(self.command_selector)
