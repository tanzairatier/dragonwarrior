import pygame



MSGSPEED_LOW = 50.0
MSGSPEED_HIGH = 15.0
MSGSPEED_NORMAL = 30.0



def handle_input(self, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            if not self.select_available_log and not self.name_input and not self.msg_speed_window and not self.select_continue_log:
                #selecting newgame or continue
                self.begin_game_box.selector_y -= 1
                if self.begin_game_box.selector_y < 0:
                    if self.available_adventure_logs and self.new_game_logs:
                        self.begin_game_box.selector_y = 1
                    else:
                        self.begin_game_box.selector_y = 0
            elif self.select_available_log or self.select_continue_log:
                #selecting one of the adventure logs
                self.adventure_log_box.selector_y -= 1
                if self.select_available_log:
                    if self.adventure_log_box.selector_y < 0:
                        self.adventure_log_box.selector_y = len(self.new_game_logs) - 1
                else:
                    if self.adventure_log_box.selector_y < 0:
                        self.adventure_log_box.selector_y = len(self.available_adventure_logs) - 1
            elif self.name_input:
                #inputting name
                self.select_letters_box.selector_y -= 1
                if self.select_letters_box.selector_y < 0:
                    self.select_letters_box.selector_y = len(self.letters) - 1
                if self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 7:
                    self.select_letters_box.selector_x = 6
                elif self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 8:
                    self.select_letters_box.selector_x = 9
                elif self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 10:
                    self.select_letters_box.selector_x = 9
            elif self.msg_speed_window:
                #selecting a msg speed
                self.message_speed_box.selector_y -= 1
                if self.message_speed_box.selector_y < 0:
                    self.message_speed_box.selector_y = 2
        elif event.key == pygame.K_DOWN:
            if not self.select_available_log and not self.name_input and not self.msg_speed_window and not self.select_continue_log:
                self.begin_game_box.selector_y += 1
                if self.available_adventure_logs and self.new_game_logs:
                    if self.begin_game_box.selector_y > 1:
                        self.begin_game_box.selector_y = 0
                else:
                    self.begin_game_box.selector_y = 0
            elif self.select_available_log or self.select_continue_log:
                self.adventure_log_box.selector_y += 1
                if self.select_available_log:
                    if self.adventure_log_box.selector_y > len(self.new_game_logs) - 1:
                        self.adventure_log_box.selector_y = 0
                else:
                    if self.adventure_log_box.selector_y > len(self.available_adventure_logs) - 1:
                        self.adventure_log_box.selector_y = 0
            elif self.name_input:
                self.select_letters_box.selector_y += 1
                if self.select_letters_box.selector_y > len(self.letters) - 1:
                    self.select_letters_box.selector_y = 0
                if self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 7:
                    self.select_letters_box.selector_x = 6
                elif self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 8:
                    self.select_letters_box.selector_x = 9
                elif self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 10:
                    self.select_letters_box.selector_x = 9
            elif self.msg_speed_window:
                self.message_speed_box.selector_y += 1
                if self.message_speed_box.selector_y > 2:
                    self.message_speed_box.selector_y = 0
        elif event.key == pygame.K_LEFT:
            if self.name_input:
                if self.select_letters_box.selector_x == 9 and self.select_letters_box.selector_y == 5:
                    self.select_letters_box.selector_x = 6
                elif self.select_letters_box.selector_x == 0 and self.select_letters_box.selector_y == 5:
                    self.select_letters_box.selector_x = 9
                else:
                    self.select_letters_box.selector_x -= 1
                    if self.select_letters_box.selector_x < 0:
                        self.select_letters_box.selector_x = len(self.letters[0]) - 1
        elif event.key == pygame.K_RIGHT:
            if self.name_input:
                if self.select_letters_box.selector_x == 6 and self.select_letters_box.selector_y == 5:
                    self.select_letters_box.selector_x = 9
                elif self.select_letters_box.selector_x == 9 and self.select_letters_box.selector_y == 5:
                    self.select_letters_box.selector_x = 0
                else:
                    self.select_letters_box.selector_x += 1
                    if self.select_letters_box.selector_x > len(self.letters[0]) - 1:
                        self.select_letters_box.selector_x = 0
        elif event.key == pygame.K_z:
            #playSound(31)
            if not self.select_available_log and not self.name_input and not self.msg_speed_window and not self.select_continue_log:
                if self.new_game_logs and self.begin_game_box.selector_y == 0:
                    self.select_available_log = True
                    self.begin_game_box.selector_y = 0
                elif self.begin_game_box.selector_y == 1 or self.available_adventure_logs and self.begin_game_box.selector_y == 0:
                    self.select_continue_log = True
                    self.begin_game_box.selector_y = 0
            elif self.select_available_log:
                self.select_available_log = False
                self.name_input = True
                self.name_so_far = ["*", "*", "*", "*", "*", "*", "*", "*"]
                self.name_so_far_index = 0
                self.adventure_log = self.new_game_logs[self.adventure_log_box.selector_y]
            elif self.select_continue_log:
                self.select_continue_log = False
                self.adventure_log = self.available_adventure_logs[self.adventure_log_box.selector_y]
                self.hero.load_game(self.adventure_log)
                self.hero.data["CONTINUE"] = True
                self.screen_mode = "Play"
                self.hero.initialize_transition(55, 5, "Tantegel")
                #self.hero.already_did_intro_chat = False
                #changeBGMusic(1)
                self.hero.music_id = 1
            elif self.name_input:
                if self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 6:
                    self.name_so_far_index -= 1
                    if self.name_so_far_index < 0:
                        self.name_so_far_index = 0
                elif self.select_letters_box.selector_y == 5 and self.select_letters_box.selector_x == 9:
                    self.msg_speed_window = True
                    self.name_input = False
                    self.select_letters_box.selector_y = 0
                    self.hero.name = None
                    for i, letter in enumerate(self.name_so_far):
                        if letter == "*":
                            self.hero.name = "".join(self.name_so_far[:i])
                            break
                    if not self.hero.name:
                        self.hero.name = "".join(self.name_so_far)
                else:
                    self.name_so_far[self.name_so_far_index] = self.letters[self.select_letters_box.selector_y][
                        self.select_letters_box.selector_x]
                    self.name_so_far_index += 1
                    if self.name_so_far_index > 7:
                        self.name_so_far_index = 7
            elif self.msg_speed_window:
                if self.walking_command_selector_y == 0:
                    self.walking_talk_box_msgtickspeed = MSGSPEED_HIGH
                elif self.walking_command_selector_y == 0:
                    self.walking_talk_box_msgtickspeed = MSGSPEED_NORMAL
                else:
                    self.walking_talk_box_msgtickspeed = MSGSPEED_LOW
                score = 0
                for letter in self.hero.name:
                    score += self.letter_dict[letter]
                score = score % 16
                self.hero.base_agility = [3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 4, 4, 6, 6, 4, 4][score]
                self.hero.base_strength = [3, 4, 3, 4, 4, 4, 4, 4, 5, 4, 5, 4, 6, 4, 6, 4][score]
                self.hero.base_maxhp = [15, 15, 13, 13, 15, 15, 14, 14, 15, 15, 15, 15, 15, 15, 16, 16][score]
                self.hero.base_maxmp = [5, 4, 5, 4, 5, 5, 5, 5, 5, 6, 5, 6, 5, 7, 5, 7][score]
                self.hero.growth_str = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2][score]
                self.hero.growth_agi = [2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2][score]
                self.hero.growth_maxhp = [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1][score]
                self.hero.growth_maxmp = [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1][score]
                self.hero.new_game()
                self.hero.initialize_level()
                self.hero.data["BEGIN"] = True
                self.hero.save_game(self.adventure_log)
                self.screen_mode = "Play"
                self.hero.initialize_transition(55, 5, "Tantegel")
                #changeBGMusic(1)
                self.hero.music_id = 1

        elif event.key == pygame.K_x:
            if self.select_available_log:
                self.select_available_log = False
                self.adventure_log_box.reset()
            elif self.select_continue_log:
                self.select_continue_log = False
                self.adventure_log_box.reset()
            elif self.name_input:
                self.name_so_far_index -= 1
                if self.name_so_far_index < 0:
                    self.name_so_far_index = 0
            elif self.msg_speed_window:
                self.msg_speed_window = False
                self.walking_command_selector_y = 0
