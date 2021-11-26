def draw(self):
    num_items = self.hero.get_item_inv_size()
    if num_items+1 > self.item_box.num_cells_high:
        self.item_box.redefine_surface(5, num_items + 1.5)
    self.item_box.increment_ticks(self.delta_ticks)
    self.item_box.draw(self.screen)
    self.item_box.fill(self.black)
    self.item_box.draw_border(self.menu_color)

    if len(self.hero.draw_items) == 0:
        i = -1

    for i, item in enumerate(self.hero.draw_items):
        if len(item) > 8:
            item_texts = item.split(" ")
            if self.hero.draw_items[item] > 1:
                self.item_box.draw_string(item_texts[0] + (8-len(item_texts[0]))*" " + str(self.hero.draw_items[item]),
                                          self.gamefont, self.menu_color, 1, i+1.0)
            else:
                self.item_box.draw_string(item_texts[0], self.gamefont, self.menu_color, 1, i+1.0)
            self.item_box.draw_string(" " + " ".join(item_texts[1:]), self.gamefont, self.menu_color, 1, i+1.5)
        else:
            if self.hero.draw_items[item] > 1:
                self.item_box.draw_string(item + (8-len(item))*" " + str(self.hero.draw_items[item]),
                                          self.gamefont, self.menu_color, 1, i+1.0)
            else:
                self.item_box.draw_string(item, self.gamefont, self.menu_color, 1, i+1.0)

    for j, item in enumerate(self.hero.undraw_items):
        if len(item) > 8:
            item_texts = item.split(" ")
            if len(item_texts) > 2:
                if len(item_texts[0])+len(item_texts[1]) > 8:
                    self.item_box.draw_string(item_texts[0], self.gamefont, self.menu_color, 1, 1+i+j+1.0)
                    self.item_box.draw_string(" " + " ".join(item_texts[1:]),
                                              self.gamefont, self.menu_color, 1, 1+i+j+1.5)
                else:
                    self.item_box.draw_string(" ".join(item_texts[:2]), self.gamefont, self.menu_color, 1, 1+i+j+1.0)
                    self.item_box.draw_string(" " + " ".join(item_texts[2:]),
                                              self.gamefont, self.menu_color, 1, 1+i+j+1.5)
            else:
                self.item_box.draw_string(item_texts[0], self.gamefont, self.menu_color, 1, 1+i+j+1.0)
                self.item_box.draw_string(" " + " ".join(item_texts[1:]), self.gamefont, self.menu_color, 1, 1+i+j+1.5)
        else:
            self.item_box.draw_string(item, self.gamefont, self.menu_color, 1, 1+i+j+1.0)
    self.item_box.draw_selector(self.command_selector)
