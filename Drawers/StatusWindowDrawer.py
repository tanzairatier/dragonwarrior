def draw(self):
    self.status_box.increment_ticks(self.delta_ticks)
    self.status_box.draw(self.screen)
    self.status_box.fill(self.black)
    self.status_box.draw_border(self.menu_color)
    self.status_box.draw_string("NAME:"+self.hero.name, self.gamefont, self.menu_color, 3, 0.5)
    _draw_pairs = (("          STRENGTH:", self.hero.strength),
                   ("           AGILITY:", self.hero.agility),
                   ("        MAXIMUM HP:", self.hero.maxhp),
                   ("        MAXIMUM MP:", self.hero.maxmp),
                   ("      ATTACK POWER:", self.hero.get_attack_power()),
                   ("     DEFENSE POWER:", self.hero.get_defense_power()))
    for i,pair in enumerate(_draw_pairs):
        _label = pair[0]
        _value = pair[1]
        self.status_box.draw_string(_label + (3-len(str(_value)))*" " + str(_value),
                                    self.gamefont, self.menu_color, 0.5, 1.5 + i)
    if self.hero.weapon and len(self.hero.weapon.name) > 10:
        weptexts = self.hero.weapon.name.split(" ")
        self.status_box.draw_string("      WEAPON:" + weptexts[0], self.gamefont, self.menu_color, 0.5, 7.5)
        self.status_box.draw_string("              " + weptexts[1], self.gamefont, self.menu_color, 0.5, 8.0)
    else:
        self.status_box.draw_string("      WEAPON:" + str(self.hero.weapon.name if self.hero.weapon else ""), self.gamefont, self.menu_color, 0.5, 7.5)
    if self.hero.armor and len(self.hero.armor.name) > 10:
        weptexts = self.hero.armor.name.split(" ")
        self.status_box.draw_string("       ARMOR:" + weptexts[0], self.gamefont, self.menu_color, 0.5, 8.5)
        self.status_box.draw_string("              " + weptexts[1], self.gamefont, self.menu_color, 0.5, 9.0)
    else:
        self.status_box.draw_string("       ARMOR:" + str(self.hero.armor.name if self.hero.armor else ""), self.gamefont, self.menu_color, 0.5, 8.5)
    if self.hero.shield and len(self.hero.shield.name) > 10:
        weptexts = self.hero.shield.name.split(" ")
        self.status_box.draw_string("      SHIELD:" + weptexts[0], self.gamefont, self.menu_color, 0.5, 9.5)
        self.status_box.draw_string("              " + weptexts[1], self.gamefont, self.menu_color, 0.5, 10.0)
    else:
        self.status_box.draw_string("      SHIELD:" + str(self.hero.shield.name if self.hero.shield else ""), self.gamefont, self.menu_color, 0.5, 9.5)
