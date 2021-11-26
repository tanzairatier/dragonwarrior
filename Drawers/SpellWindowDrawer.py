def draw(self):
    self.spell_box.increment_ticks(self.delta_ticks)
    self.spell_box.draw(self.screen)
    self.spell_box.fill(self.black)
    self.spell_box.draw_border(self.menu_color)
    self.spell_box.draw_label("SPELL", self.gamefont, self.menu_color)
    for i, spell in enumerate(self.hero.spells):
        self.spell_box.draw_string(spell.name, self.gamefont, self.menu_color, 1, 1+i)
    self.spell_box.draw_selector(self.command_selector)
