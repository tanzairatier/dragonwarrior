def draw(self):
    self.side_box.increment_ticks(self.delta_ticks)
    self.side_box.draw(self.screen)
    self.side_box.fill(self.black)
    self.side_box.draw_border(self.menu_color)
    self.side_box.draw_label(self.hero.name[:6], self.gamefont, self.menu_color)
    _draw_pairs = (("LV", self.hero.level),
                   ("HP", self.hero.HP),
                   ("MP", self.hero.MP),
                   ("G ", self.hero.G),
                   ("E ", self.hero.E))
    for i, pair in enumerate(_draw_pairs):
        _label = pair[0]
        _value = pair[1]
        self.side_box.draw_string(_label + (6 - len(str(_value))) * " " + str(_value),
                                  self.gamefont, self.menu_color, 0.5, 1 + i)
