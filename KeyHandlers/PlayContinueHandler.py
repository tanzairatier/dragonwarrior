import pygame

def handle_input(self, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_x or event.key == pygame.K_z or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
            if self.hero.data.get("CONTINUE", False) and not self.hero.already_did_intro_chat \
                                                     and self.hero.map.name == "Tantegel" \
                                                     and self.hero.x == 55 \
                                                     and self.hero.y == 5 \
                                                     and self.hero.face == 2:
                self.hero.perform_action("TALK")
                if self.hero.data.get("CONTINUE", False):
                    self.hero.data["CONTINUE"] = False
                self.hero.already_did_intro_chat = True

