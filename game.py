import pygame,sys,os,math,time,random
import maps
import Map
from Item import Item
from TextNode import TextNode
from Query import Query, Transaction
from Spell import Spell
from Enemy import Enemy
from Window import Window
import shelve


from KeyHandlers import TitleScreenHandler, IntroScreenHandler, BeginScreenHandler, PlayBeginHandler, PlayContinueHandler
from Loaders import LoadTiles
from Drawers import TitleScreenDrawer, BeginGameWindowDrawer, SelectAdventureLogWindowDrawer, NameInputWindowDrawer, \
    MessageSpeedWindowDrawer, StatusWindowDrawer, SpellWindowDrawer, ItemWindowDrawer, SideWindowDrawer, \
    CommandWindowDrawer

NUM_CELLS_WIDE = 15
NUM_CELLS_HIGH = 15
HEROMOVESPEED = 250.0
HEROSTEPSPEED = 250.0
MAPTRANSITIONTIME = 250.0



clock = pygame.time.Clock()


#read in music files
last_music = 4
musics = []
for (dirpath, _, filenames) in os.walk('music/'):
    for filename in filenames:
        musics.append(os.path.join(dirpath, filename))

def changeBGMusic(music_id):
    if music_id is not None:
        print "playing music " + str(music_id)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(musics[music_id])  # play title screen music
        #pygame.mixer.music.play(-1)
        last_music = music_id

def pauseMusic():
    pygame.mixer.music.pause()

def queueSound(sound_id):
    if sound_id:
        s = pygame.mixer.Sound(musics[sound_id])
        pygame.mixer.Channel(3).queue(s)
def playSound(sound_id):
    if sound_id:
        s = pygame.mixer.Sound(musics[sound_id])
        pygame.mixer.Channel(3).play(s)
        print "played sound " + str(sound_id)



class Main:
    def __init__(self):


        pygame.mixer.pre_init(44100, -16, 2, 512)  # setup mixer to avoid sound lag
        pygame.init()



        self.width = 800
        self.height = 640
        self.unitsizex = int(self.width/float(NUM_CELLS_WIDE))
        self.unitsizey = int(self.height/float(NUM_CELLS_HIGH))
        self.width = int(self.unitsizex * (NUM_CELLS_WIDE+0.5))
        self.height = int(self.unitsizey * (NUM_CELLS_HIGH+0.5))
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.alpha = 255
        self.frozen = False




        self.menu_color = (255,255,255)
        self.black = (0,0,0)

        self.white_flash = pygame.Surface((self.width, self.height))
        self.white_flash.fill((180, 180, 180))
        self.white_flash.set_alpha(180)

        self.red_flash = pygame.Surface((self.width, self.height))
        self.red_flash.fill((255, 15, 15))
        self.red_flash.set_alpha(200)

        self.hero = Hero(self.unitsizex, self.unitsizey)
        self.hero.offsetx = - self.hero.x + NUM_CELLS_WIDE/2
        self.hero.offsety = - self.hero.y + NUM_CELLS_HIGH/2
        changeBGMusic(0)
        self.hero.music_id = 0

        self.gamefont = pygame.font.Font("fonts/Dragon Quest.ttf", int((0.80*self.unitsizex)/2))

        self.screen_mode = "Screen Title"
        self.select_available_log = False
        self.name_input = False
        self.name_so_far = ["*", "*", "*", "*", "*", "*", "*", "*"]
        self.name_so_far_index = 0
        self.msg_speed_window = False
        self.select_continue_log = False

        #walking menu
        self.side_box = Window(4, 6, self.unitsizex, self.unitsizey, 125, 0.5, 1.5)


        # walking command
        self.command_box = Window(8, 5, self.unitsizex, self.unitsizey, 125, 5.5, 0.5)
        #self.walking_command_drawspeedticks = 125.0
        #self.walking_command_ticks = 0
        #self.walking_command = pygame.Surface((self.unitsizex * 8, self.unitsizey * 5))
        #self.walking_command.fill((0, 0, 0))

        #self.walking_command_selector_x = 0
        #self.walking_command_selector_y = 0
        #self.walking_command_selector_ticks = 0
        #self.walking_command_selector_blinkspeedticks = 250.0
        #self.walking_command_selector_visible = True
        #self.walking_command_options = [["TALK", "SPELL"], ["STATUS", "ITEM"], ["STAIRS", "DOOR"], ["SEARCH", "TAKE"]]

        # battle command
        self.battle_command_selector_x = 0
        self.battle_command_selector_y = 0
        self.battle_command_ticks = 0
        self.battle_command_tickspeed = 125.0
        self.battle_command_options = [["FIGHT", "SPELL"], ["RUN", "ITEM"]]
        self.battle_command = pygame.Surface((self.unitsizex * 8, self.unitsizey * 3))

        # battle box
        self.battle_box = pygame.Surface((self.unitsizex * 7, self.unitsizey * 7), pygame.SRCALPHA, 32).convert_alpha()
        self.enemy_background = pygame.image.load("images/enemy_background.png").convert()


        self.command_selector_white = pygame.image.load("images/command_selector.png").convert()
        self.command_selector_red = pygame.image.load("images/command_selector_red.png").convert()
        self.command_selector = self.command_selector_white

        self.screen_shake_shift_x = 0
        self.screen_shake_shift_y = 0

        #walking talk box
        self.chat_box = Window(13, 5.5, self.unitsizex, self.unitsizey, 125, 1.5, 8.5)
        #self.walking_talk_box_drawspeedticks = 125.0
        #self.walking_talk_box_ticks = 0
        #self.walking_talk_box = pygame.Surface((self.unitsizex * 12, self.unitsizey * 5.5))
        #self.walking_talk_box_visible = False
        #self.walking_talk_box_msg_ticks = 0
        self.walking_talk_box_msgtickspeed = 20.0   #equiv to number of ms per letter of message


        #query box
        self.query_box_drawspeedticks = 125.0
        self.query_box_ticks = 0
        self.query_box = None
        self.query_selection = 0

        #shop box
        self.shop_selection = 0

        #status box
        self.status_box = Window(10, 11, self.unitsizex, self.unitsizey, 125, 5.5, 3)

        # spell box
        self.spell_box = Window(7, len(self.hero.spells)+1.0, self.unitsizex, self.unitsizey, 125, 8.5, 1.5)

        # item box
        self.item_box = Window(5, self.hero.get_item_inv_size()+1.5, self.unitsizex, self.unitsizey, 125, 9.5, 2.5)

        # begin or continue box
        self.begin_game_box = Window(10, 3, self.unitsizex, self.unitsizey, 125, 3, 4)

        # adventure log select box
        self.adventure_log_box = Window(8, 3, self.unitsizex, self.unitsizey, 125, 6, 7)

        # input name box
        self.input_name_box = Window(6,2, self.unitsizex, self.unitsizey, 125, 5, 2.25)
        self.select_letters_box = Window(12,7, self.unitsizex, self.unitsizey, 125, 2, 4)

        # message speed box
        self.message_speed_box = Window(10,4.5, self.unitsizex, self.unitsizey, 125, 3, 4)

        self.donetalkingitsokaytoacceptinput = True

        self.beginning = pygame.image.load("images/beginning.png").convert()
        self.sparkle = pygame.image.load("images/sparkle_sprite.png").convert()
        self.sparkle_step = 0
        self.sparkle_ticks = 0
        self.sparkle_pattern = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                          -1, -1,  0,  1,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  1,  2,  3, -1, -1, -1,
                          -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                          -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  1,  1,  1,  2,  2,  2,  3,  3,  3]


        self.ending_screen = pygame.image.load("images/ending.png").convert()
        self.ending_credits_ticks = 0

        self.clock = pygame.time.Clock()
        self.tiles = LoadTiles.load_normal_tiles()
        self.red_tiles = LoadTiles.load_red_tiles()

        self.last_ticks = pygame.time.get_ticks()

        self.letters = [["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
                   ["L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V"],
                   ["W", "X", "Y", "Z", "-", "'", "!", "?", "(", ")", " "],
                   ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"],
                   ["l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v"],
                   ["w", "x", "y", "z", ",", "."]]

        self.letter_dict = {" ": 0, " ": 1, " ": 2, " ": 3, " ": 4, " ": 5, " ": 6, " ": 7, " ": 8, " ": 9, "a": 10, "b": 11, "c": 12, "d": 13, "e": 14, "f": 15,
                             "g": 0, "h": 1, "i": 2, "j": 3, "k": 4, "l": 5, "m": 6, "n": 7, "o": 8, "p": 9, "q": 10, "r": 11, "s": 12, "t": 13, "u": 14, "v": 15,
                             "w": 0, "x": 1, "y": 2, "z": 3, "A": 4, "B": 5, "C": 6, "D": 7, "E": 8, "F": 9, "G": 10, "H": 11, "I": 12, "J": 13, "K": 14, "L": 15,
                             "M": 0, "N": 1, "O": 2, "P": 3, "Q": 4, "R": 5, "S": 6, "T": 7, "U": 8, "V": 9, "W": 10, "X": 11, "Y": 12, "Z": 13, " ": 14, " ": 15,
                             "'": 0, " ": 1, " ": 2, " ": 3, " ": 4, " ": 5, " ": 6, ".": 7, ",": 8, "-": 9, " ": 10, "?": 11, "!": 12, " ": 13, ")": 14, "(": 15}

        self.available_adventure_logs = self.hero.read_adventure_logs()
        self.new_game_logs = [i for i in [1,2,3] if not i in self.available_adventure_logs]



    def goforit(self):
        go = False
        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
            go = True
        elif self.hero.walking_talk_box_message == "":
            go = True
        return go



    def loop(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    pass
                if event.type == pygame.QUIT:
                    sys.exit()

                if self.screen_mode == "Screen Title":
                    TitleScreenHandler.handle_input(self,event)
                elif self.screen_mode == "Screen Title With Intro":
                    IntroScreenHandler.handle_input(self,event)
                    changeBGMusic(3)
                elif self.screen_mode == "Begin or Continue":
                    BeginScreenHandler.handle_input(self,event)
                elif self.screen_mode == "Play":
                    PlayBeginHandler.handle_input(self,event)
                    PlayContinueHandler.handle_input(self, event)

                    if self.hero.teleport_via_death:
                        if self.donetalkingitsokaytoacceptinput and self.goforit() and self.hero.teleport_via_death and event.type == pygame.KEYDOWN:
                            self.hero.battle_mode = False
                            self.hero.teleport_via_death = False
                            self.hero.is_dead = True
                            self.hero.mode = "Transitioning"
                            self.hero.mx = 55
                            self.hero.my = 5
                            self.hero.moffsetx = - self.hero.mx + NUM_CELLS_WIDE / 2
                            self.hero.moffsety = - self.hero.my + NUM_CELLS_HIGH / 2
                            self.hero.teleport_pack = ("Tantegel", self.hero.sizex, self.hero.sizey)
                            self.hero.map_transition = True
                            self.hero.flag_moving = False
                            self.hero.flag_left = False
                            self.hero.flag_right = False
                            self.hero.flag_up = False
                            self.hero.flag_down = False
                            self.hero.screenfade = "out"
                            self.hero.screenfadeticks = 0
                            self.hero.mode = "Walking"
                            self.hero.walking_talk_box_visible = False
                            self.hero.walking_talk_box_message = ""
                            self.walking_talk_box_ticks = 0
                            self.side_box.reset()
                            self.command_box.reset()
                            self.walking_talk_box_msg_ticks = 0
                    elif self.hero.battle_running and not self.hero.enemy_spiral_flag and self.donetalkingitsokaytoacceptinput and self.goforit() and event.type == pygame.KEYDOWN:
                        self.hero.battle_running = False
                        self.hero.mode = "Walking"
                        self.hero.walking_talk_box_visible = False
                        self.hero.walking_talk_box_message = ""
                        self.walking_talk_box_ticks = 0
                        self.side_box.reset()
                        self.command_box.reset()
                        self.walking_talk_box_msg_ticks = 0
                        self.hero.battle_mode = False
                        self.hero.battle_report_mode = False
                        changeBGMusic(last_music)
                        if self.hero.enemy.name == "Golem": #back up one space -- cant avoid Golem by running
                            self.hero.face = 2
                            self.hero.targety = self.hero.y - 1
                            self.hero.targetx = self.hero.x
                            if self.hero.valid_cell(self.hero.x, self.hero.y - 1) and not self.hero.map.mutex_data.get(
                                    (self.hero.targetx, self.hero.targety), False):
                                self.hero.map.mutex_data[(self.hero.x, self.hero.y)] = False
                                self.hero.map.mutex_data[(self.hero.targetx, self.hero.targety)] = True
                                self.hero.vely = -(self.delta_ticks / HEROMOVESPEED)
                                self.hero.velx = 0
                                self.hero.motion_in_progress = True
                            else:
                                self.lag_motion = True
                        elif self.hero.enemy.name == "Green Dragon" and self.hero.map.name == "Swamp Cave":
                            self.hero.face = 2
                            self.hero.targety = self.hero.y - 1
                            self.hero.targetx = self.hero.x
                            if self.hero.valid_cell(self.hero.x, self.hero.y - 1) and not self.hero.map.mutex_data.get(
                                    (self.hero.targetx, self.hero.targety), False):
                                self.hero.map.mutex_data[(self.hero.x, self.hero.y)] = False
                                self.hero.map.mutex_data[(self.hero.targetx, self.hero.targety)] = True
                                self.hero.vely = -(self.delta_ticks / HEROMOVESPEED)
                                self.hero.velx = 0
                                self.hero.motion_in_progress = True
                            else:
                                self.lag_motion = True
                        elif self.hero.enemy.name == "Axe Knight" and self.hero.map.name == "Hauksness":
                            self.hero.face = 1
                            self.hero.targety = self.hero.y
                            self.hero.targetx = self.hero.x - 1
                            if self.hero.valid_cell(self.hero.x - 1, self.hero.y) and not self.hero.map.mutex_data.get(
                                    (self.hero.targetx, self.hero.targety), False):
                                self.hero.map.mutex_data[(self.hero.x, self.hero.y)] = False
                                self.hero.map.mutex_data[(self.hero.targetx, self.hero.targety)] = True
                                self.hero.vely = 0
                                self.hero.velx = -(self.delta_ticks / HEROMOVESPEED)
                                self.hero.motion_in_progress = True
                            else:
                                self.lag_motion = True
                        self.hero.enemy = Enemy("Red Slime")
                    elif not self.hero.battle_running and not self.hero.is_dead and not self.hero.enemyspell and not self.hero.youdied and not self.hero.spell_lag and not self.hero.heroattack and not self.hero.enemyattack and not self.hero.chose_a_turn and not self.hero.enemy_turn and not self.hero.enemy_red_shadow and not self.hero.screen_shake_flag and event.type == pygame.KEYDOWN:
                        if self.hero.walking_talk_box_msg_tick_next:
                            self.hero.walking_talk_box_msg_tick_next = False
                            if self.hero.walking_talk_box_message.next:
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.next
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                        elif self.hero.mode == "Status":
                            if event.key == pygame.K_z or event.key == pygame.K_x:
                                self.hero.mode = "Walking"
                        elif self.hero.mode == "Walking":
                            if self.hero.oktolorikafterdying and not self.hero.youdied and self.donetalkingitsokaytoacceptinput:
                                self.hero.teleport_via_death = False
                                self.hero.justdied = True
                                self.hero.perform_action("TALK")
                            elif not self.hero.ready_for_ending_credits and not self.hero.do_ending_credits and not self.hero.eviction and not self.hero.teleport_via_death and not self.hero.youdied and not self.hero.fight_the_true_dragonlord and not self.hero.fight_the_dragonlord and not self.hero.dragonlord_is_dead and not self.hero.do_rainbow_bridge and not self.hero.rainbow_blink_on:
                                if event.key == pygame.K_LEFT:
                                    if not self.hero.flag_moving:
                                        self.hero.flag_moving = True
                                        self.hero.flag_left = True
                                elif event.key == pygame.K_DOWN:
                                    if not self.hero.flag_moving:
                                        self.hero.flag_moving = True
                                        self.hero.flag_down = True
                                elif event.key == pygame.K_UP:
                                    if not self.hero.flag_moving:
                                        self.hero.flag_moving = True
                                        self.hero.flag_up = True
                                elif event.key == pygame.K_RIGHT:
                                    if not self.hero.flag_moving:
                                        self.hero.flag_moving = True
                                        self.hero.flag_right = True
                                if event.key == pygame.K_z and not self.hero.motion_in_progress:
                                    playSound(31)
                                    self.hero.mode = "Menu"
                                    self.hero.flag_moving = False
                                    self.hero.flag_left = False
                                    self.hero.flag_right = False
                                    self.hero.flag_up = False
                                    self.command_box.reset()
                                    self.shop_selection = 0
                        elif self.hero.mode == "Menu":
                            if event.key == pygame.K_x:
                                if not self.hero.battle_mode:
                                    self.hero.mode = "Walking"
                                    self.side_box.reset()
                                    self.command_box.reset()
                                else:
                                    if not self.hero.ready_to_end_battle and not self.hero.enemy_spiral_flag:
                                        self.hero.add_to_message_render(TextNode("Command?", quoted=False), replace=False)
                                        self.battle_command_selector_x = 0
                                        self.battle_command_selector_y = 0
                            elif event.key == pygame.K_z:
                                playSound(31)
                                if not self.hero.battle_mode:
                                    self.hero.perform_action(self.walking_command_options[self.walking_command_selector_y][self.walking_command_selector_x])
                                else:
                                    if not self.hero.ready_to_end_battle and not self.hero.enemy_spiral_flag:
                                        self.hero.perform_battle_action(self.battle_command_options[self.battle_command_selector_y][self.battle_command_selector_x])
                                        self.battle_command_selector_x = 0
                                        self.battle_command_selector_y = 0
                            if event.key == pygame.K_RIGHT:
                                if not self.hero.battle_mode:
                                    self.command_box.selector_x += 1
                                    if self.command_box.selector_x > 1:
                                        self.command_box.selector_x = 0
                                else:
                                    if not self.hero.ready_to_end_battle and not self.hero.enemy_spiral_flag:
                                        self.battle_command_selector_x += 1
                                        if self.battle_command_selector_x > 1:
                                            self.battle_command_selector_x = 0
                            if event.key == pygame.K_LEFT:
                                if not self.hero.battle_mode:
                                    self.command_box.selector_x -= 1
                                    if self.command_box.selector_x < 0:
                                        self.command_box.selector_x = 1
                                else:
                                    if not self.hero.ready_to_end_battle and not self.hero.enemy_spiral_flag:
                                        self.battle_command_selector_x -= 1
                                        if self.battle_command_selector_x < 0:
                                            self.battle_command_selector_x = 1
                            if event.key == pygame.K_UP:
                                if not self.hero.battle_mode:
                                    self.command_box.selector_y -= 1
                                    if self.command_box.selector_y < 0:
                                        self.command_box.selector_y = 3
                                else:
                                    if not self.hero.ready_to_end_battle and not self.hero.enemy_spiral_flag:
                                        self.battle_command_selector_y -= 1
                                        if self.battle_command_selector_y < 0:
                                            self.battle_command_selector_y = 1
                            if event.key == pygame.K_DOWN:
                                if not self.hero.battle_mode:
                                    self.command_box.selector_y += 1
                                    if self.command_box.selector_y > 3:
                                        self.command_box.selector_y = 0
                                else:
                                    if not self.hero.ready_to_end_battle and not self.hero.enemy_spiral_flag:
                                        self.battle_command_selector_y += 1
                                        if self.battle_command_selector_y > 1:
                                            self.battle_command_selector_y = 0
                        elif self.hero.mode == "Item":
                            if event.key == pygame.K_x:
                                self.hero.mode = "Walking"
                                self.hero.display_item_window = False
                                self.item_box.draw_ticks = 0
                                self.item_box.selector_y = 0
                                if self.hero.battle_mode:
                                    self.hero.mode = "Menu"
                            elif event.key == pygame.K_z:
                                self.hero.use_item(self.item_box.selector_y)
                            if event.key == pygame.K_UP:
                                self.item_box.selector_y -= 1
                                if self.item_box.selector_y < 0:
                                    self.item_box.selector_y = self.hero.get_item_inv_size()-1
                            if event.key == pygame.K_DOWN:
                                self.item_box.selector_y += 1
                                if self.item_box.selector_y > self.hero.get_item_inv_size()-1:
                                    self.item_box.selector_y = 0
                        elif self.hero.mode == "Spell":
                            if event.key == pygame.K_x:
                                self.hero.mode = "Walking"
                                if self.hero.battle_mode:
                                    self.hero.mode = "Menu"
                                self.spell_box.draw_ticks = 0
                                self.spell_box.selector_y = 0
                            elif event.key == pygame.K_z:
                                self.hero.cast_spell(self.hero.spells[self.spell_box.selector_y])
                            if event.key == pygame.K_UP:
                                self.spell_box.selector_y -= 1
                                if self.spell_box.selector_y < 0:
                                    self.spell_box.selector_y = len(self.hero.spells)-1
                            if event.key == pygame.K_DOWN:
                                self.spell_box.selector_y += 1
                                if self.spell_box.selector_y > len(self.hero.spells)-1:
                                    self.spell_box.selector_y = 0
                        elif self.hero.mode == "Talking":
                            if not self.frozen:
                                if self.donetalkingitsokaytoacceptinput and not self.hero.faerie_flute_blown and not self.hero.silver_harp_playing and not self.hero.spell_lag and not self.hero.heroattack and not self.hero.enemyattack and not self.hero.chose_a_turn and not self.hero.enemy_turn and not self.hero.enemy_red_shadow and not self.hero.screen_shake_flag:
                                    if not self.hero.walking_talk_box_message.next:
                                        if event.key == pygame.K_x or event.key == pygame.K_z:
                                            self.hero.mode = "Walking"
                                            self.hero.walking_talk_box_visible = False
                                            self.hero.walking_talk_box_message = ""
                                            self.walking_talk_box_ticks = 0
                                            self.side_box.reset()
                                            self.command_box.reset()
                                            self.walking_talk_box_msg_ticks = 0
                                            self.hero.battle_report_mode = False
                        elif self.hero.mode == "Query":
                            if event.key == pygame.K_UP:
                                self.query_selection -= 1
                                if self.query_selection < 0:
                                    self.query_selection = len(self.hero.walking_talk_box_message.query.options)-1
                            elif event.key == pygame.K_DOWN:
                                self.query_selection += 1
                                if self.query_selection > len(self.hero.walking_talk_box_message.query.options)-1:
                                    self.query_selection = 0
                            elif event.key == pygame.K_x:
                                #invoke cancel option of query
                                if self.hero.walking_talk_box_message.query.query_type == "dragonlord1":
                                        self.hero.fight_the_dragonlord = True
                                        self.hero.delayticks = 0
                                elif self.hero.walking_talk_box_message.query.query_type == "dragonlord2":
                                        self.hero.fight_the_dragonlord = True
                                        self.hero.delayticks = 0
                                elif self.hero.walking_talk_box_message.query.query_type == "Decide to Discard":
                                        self.hero.remove_from_inventory(Item(self.hero.walking_talk_box_message.query.transaction2))
                                        self.hero.data[self.hero.walking_talk_box_message.query.transaction] = False
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                            elif event.key == pygame.K_z:
                                #invoke option
                                if self.hero.walking_talk_box_message.query.options[self.query_selection] == "SELL" and len(self.hero.items) == 0:
                                        self.hero.walking_talk_box_message = TextNode("Thou have no items to sell.")
                                        self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                        self.hero.mode = "Talking"
                                else:
                                    if self.hero.walking_talk_box_message.query.query_type == "Purchase" and self.hero.walking_talk_box_message.query.options[self.query_selection] == "Yes":
                                        self.hero.G -= self.hero.walking_talk_box_message.query.transaction.item.cost
                                        self.hero.add_to_inventory(self.hero.walking_talk_box_message.query.transaction.item)
                                        self.hero.update_sprite()
                                    elif self.hero.walking_talk_box_message.query.query_type == "Save the Game" and self.hero.walking_talk_box_message.query.options[self.query_selection] == "YES":
                                        self.hero.save_game(self.adventure_log)
                                    elif self.hero.walking_talk_box_message.query.query_type == "Sell an Item" and self.hero.walking_talk_box_message.query.options[self.query_selection] == "YES":
                                        self.hero.G += self.hero.walking_talk_box_message.query.transaction.item.cost
                                        self.hero.remove_from_inventory(self.hero.walking_talk_box_message.query.transaction.item)
                                        if self.hero.walking_talk_box_message.query.transaction.item.name == "Fighter's Ring":
                                            self.hero.fighters_ring = False
                                        elif self.hero.walking_talk_box_message.query.transaction.item.name == "Dragon's Scale":
                                            self.hero.dragons_scale = False
                                    elif self.hero.walking_talk_box_message.query.query_type == "Decide to Discard" and self.hero.walking_talk_box_message.query.options[self.query_selection] == "NO":
                                        self.hero.data[self.hero.walking_talk_box_message.query.transaction] = False
                                    elif self.hero.walking_talk_box_message.query.query_type == "Purchase and Sell" and self.hero.walking_talk_box_message.query.options[self.query_selection] == "Yes":
                                        if self.hero.walking_talk_box_message.query.transaction.item.type == "Weapon":
                                            self.hero.G += self.hero.weapon.cost/2
                                        elif self.hero.walking_talk_box_message.query.transaction.item.type == "Armor":
                                            self.hero.G += self.hero.armor.cost/2
                                        elif self.hero.walking_talk_box_message.query.transaction.item.type == "Shield":
                                            self.hero.G += self.hero.shield.cost / 2
                                        else:
                                            self.hero.G += self.hero.walking_talk_box_message.query.transaction.cost/2
                                        self.hero.remove_from_inventory(self.hero.walking_talk_box_message.query.transaction.item)
                                        self.hero.G -= self.hero.walking_talk_box_message.query.transaction2.item.cost
                                        self.hero.add_to_inventory(self.hero.walking_talk_box_message.query.transaction2.item)
                                        self.hero.update_sprite()

                                    if self.hero.walking_talk_box_message.query.query_type == "dragonlord1":
                                        if self.hero.walking_talk_box_message.query.options[self.query_selection] == "NO":
                                            self.hero.fight_the_dragonlord = True
                                            self.hero.delayticks = 0
                                    elif self.hero.walking_talk_box_message.query.query_type == "dragonlord2":
                                        if self.hero.walking_talk_box_message.query.options[self.query_selection] == "NO":
                                            self.hero.fight_the_dragonlord = True
                                            self.hero.delayticks = 0
                                        elif self.hero.walking_talk_box_message.query.options[self.query_selection] == "YES":
                                            self.hero.join_the_dragonlord = True
                                            self.frozen = True
                                            self.hero.delayticks = 0
                                    self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.responses[self.query_selection]
                                    self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                    self.hero.mode = "Talking"

                        elif self.hero.mode == "Mini Shop":
                            if event.key == pygame.K_UP:
                                self.query_selection -= 1
                                if self.query_selection < 0:
                                    self.query_selection = len(self.hero.walking_talk_box_message.query.options)-1
                            elif event.key == pygame.K_DOWN:
                                self.query_selection += 1
                                if self.query_selection > len(self.hero.walking_talk_box_message.query.options)-1:
                                    self.query_selection = 0
                            elif event.key == pygame.K_x:
                                #invoke cancel option of query
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                            elif event.key == pygame.K_z:
                                #invoke option
                                if self.hero.walking_talk_box_message.query.options[self.query_selection] == "YES":
                                    if self.hero.G < self.hero.walking_talk_box_message.query.transaction.item.cost:
                                        self.hero.walking_talk_box_message = TextNode("Thou hast not enough money.")
                                    elif self.hero.get_item_inv_size() > 8 and self.hero.number_owned(self.hero.walking_talk_box_message.query.transaction.item.name) == 0:
                                        self.hero.walking_talk_box_message = TextNode("Thou cannot carry anymore.")
                                    elif self.hero.number_owned(self.hero.walking_talk_box_message.query.transaction.item.name) > 5:
                                        self.hero.walking_talk_box_message = TextNode("I am sorry, but I cannot sell you any more.", next=self.hero.walking_talk_box_message.query.cancel_response)
                                    else:
                                        self.hero.G -= self.hero.walking_talk_box_message.query.transaction.item.cost
                                        self.hero.add_to_inventory(self.hero.walking_talk_box_message.query.transaction.item)
                                        self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.responses[self.query_selection]
                                else:
                                    self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.responses[self.query_selection]
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                        elif self.hero.mode == "ItemShop":
                            if event.key == pygame.K_UP:
                                self.shop_selection -= 1
                                if self.shop_selection < 0:
                                    self.shop_selection = len(self.hero.walking_talk_box_message.query.options)-1
                            elif event.key == pygame.K_DOWN:
                                self.shop_selection += 1
                                if self.shop_selection > len(self.hero.walking_talk_box_message.query.options)-1:
                                    self.shop_selection = 0
                            elif event.key == pygame.K_x:
                                #invoke cancel option of query
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                            elif event.key == pygame.K_z:
                                #invoke option
                                if self.hero.G < self.hero.walking_talk_box_message.query.options[self.shop_selection].cost:
                                    self.hero.walking_talk_box_message = TextNode("Thou hast not enough money.", next=TextNode("Dost thou want anything else?", query=Query(options=["YES", "NO"], responses=[TextNode("What dost thou want?", query=self.shop_base_query), self.hero.walking_talk_box_message.query.cancel_response], cancel_response=self.hero.walking_talk_box_message.query.cancel_response,height=3,width=4)))
                                elif self.hero.get_item_inv_size() > 8:
                                    self.hero.walking_talk_box_message = TextNode("Thou cannot carry anymore.", next=TextNode("Dost thou want anything else?", query=Query(options=["YES", "NO"], responses=[TextNode("What dost thou want?", query=self.shop_base_query), self.hero.walking_talk_box_message.query.cancel_response], cancel_response=self.hero.walking_talk_box_message.query.cancel_response,height=3,width=4)))
                                elif self.hero.number_owned(self.hero.walking_talk_box_message.query.options[self.shop_selection].name) >= 6:
                                    self.hero.walking_talk_box_message = TextNode("Thou cannot carry anymore " + self.hero.walking_talk_box_message.query.options[self.shop_selection].name + "s.", next=TextNode("Dost thou want anything else?", query=Query(options=["YES", "NO"], responses=[TextNode("What dost thou want?", query=self.shop_base_query), self.hero.walking_talk_box_message.query.cancel_response], cancel_response=self.hero.walking_talk_box_message.query.cancel_response,height=3,width=4)))
                                else:
                                    self.hero.G -= self.hero.walking_talk_box_message.query.options[self.shop_selection].cost
                                    self.hero.add_to_inventory(self.hero.walking_talk_box_message.query.options[self.shop_selection])
                                    self.hero.walking_talk_box_message = TextNode("The " + str(self.hero.walking_talk_box_message.query.options[self.shop_selection].name) + "? \tThank you very much.", next=TextNode("Dost thou want anything else?", query=Query(options=["YES", "NO"], responses=[TextNode("What dost thou want?", query=self.shop_base_query), self.hero.walking_talk_box_message.query.cancel_response], cancel_response=self.hero.walking_talk_box_message.query.cancel_response,height=3,width=4)))
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                        elif self.hero.mode == "Discard an Item":
                            if event.key == pygame.K_UP:
                                self.shop_selection -= 1
                                if self.shop_selection < 0:
                                    self.shop_selection = self.hero.get_item_inv_size()-1
                            elif event.key == pygame.K_DOWN:
                                self.shop_selection += 1
                                if self.shop_selection > self.hero.get_item_inv_size()-1:
                                    self.shop_selection = 0
                            elif event.key == pygame.K_x:
                                #invoke cancel option of query
                                self.hero.data[self.hero.walking_talk_box_message.query.transaction] = False
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                            elif event.key == pygame.K_z:
                                #invoke option
                                if self.shop_selection < len(self.hero.draw_items):
                                    for i,item in enumerate(self.hero.draw_items):
                                        if i == self.shop_selection:
                                            break
                                else:
                                    for j,item in enumerate(self.hero.undraw_items):
                                        if j+len(self.hero.draw_items) == self.shop_selection:
                                            break
                                whatitem = Item(item, cost=self.hero.lookup_cost(item), type=self.hero.lookup_type(item))
                                if whatitem.type == "Special":
                                    self.hero.walking_talk_box_message = TextNode("That is much too important to throw away.", quoted=False, next=TextNode("What shall thou drop?", quoted=False, query=Query(options=[],
                                                                                  responses=[],
                                                                                  cancel_response=TextNode(
                                                                                      "Thou hast given up thy " + hidden_item.contents.name + ".", quoted=False),
                                                                                  query_type="Discard Item",
                                                                                  transaction=self.hero.walking_talk_box_message.query.transaction,
                                                                                  transaction2=self.hero.walking_talk_box_message.query.transaction2)))
                                else:
                                    for i in range(6):
                                        self.hero.remove_from_inventory(Item(whatitem.name))
                                    self.hero.add_to_inventory(Item(self.hero.walking_talk_box_message.query.transaction2))
                                    self.hero.walking_talk_box_message = TextNode("Thou hast dropped thy " + whatitem.name + ". \nAnd obtained the " + self.hero.walking_talk_box_message.query.transaction2 + ".", quoted=False)

                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                        elif self.hero.mode == "Sell":
                            if event.key == pygame.K_UP:
                                self.shop_selection -= 1
                                if self.shop_selection < 0:
                                    self.shop_selection = self.hero.get_item_inv_size()-1
                            elif event.key == pygame.K_DOWN:
                                self.shop_selection += 1
                                if self.shop_selection > self.hero.get_item_inv_size()-1:
                                    self.shop_selection = 0
                            elif event.key == pygame.K_x:
                                #invoke cancel option of query
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                            elif event.key == pygame.K_z:
                                #invoke option
                                if self.shop_selection < len(self.hero.draw_items):
                                    for i,item in enumerate(self.hero.draw_items):
                                        if i == self.shop_selection:
                                            break
                                else:
                                    for j,item in enumerate(self.hero.undraw_items):
                                        if j+len(self.hero.draw_items) == self.shop_selection:
                                            break
                                whatitem = Item(item, cost=self.hero.lookup_cost(item), type=self.hero.lookup_type(item))
                                if whatitem.type == "Special":
                                    self.hero.walking_talk_box_message = TextNode("I cannot buy it.", next=TextNode("Wilt thou sell anything else?",
                                                                                           query=Query(
                                                                                           options=["YES", "NO"],
                                                                                           responses=[TextNode("What art thou selling?",
                                                                                                               query=Query(options=[],
                                                                                                                           responses=[],
                                                                                                                           cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                           query_type="Sell",
                                                                                                                           width=9,
                                                                                                                           height=None)),
                                                                                                     TextNode("I will be waiting for thy next visit.")
                                                                                                      ],
                                                                                           cancel_response=TextNode("I will be waiting for thy next visit."))
                                                                                           ))
                                else:
                                    self.hero.walking_talk_box_message = TextNode("Thou said the " + whatitem.name + ".  I will buy thy " + whatitem.name + " for " + str(whatitem.cost) + " GOLD. \tIs that all right?",
                                        query=Query(options=["YES", "NO"],
                                                    responses=[TextNode("Wilt thou sell anything else?",
                                                                                           query=Query(
                                                                                           options=["YES", "NO"],
                                                                                           responses=[TextNode("What art thou selling?",
                                                                                                               query=Query(options=[],
                                                                                                                           responses=[],
                                                                                                                           cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                           query_type="Sell",
                                                                                                                           width=9,
                                                                                                                           height=None)),
                                                                                                     TextNode("I will be waiting for thy next visit.")
                                                                                                      ],
                                                                                           cancel_response=TextNode("I will be waiting for thy next visit."))
                                                                                           ),
                                                              TextNode("Wilt thou sell anything else?",
                                                                       query=Query(
                                                                       options=["YES", "NO"],
                                                                       responses=[TextNode("What art thou selling?",
                                                                                           query=Query(options=[],
                                                                                                       responses=[],
                                                                                                       cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                       query_type="Sell",
                                                                                                       width=9,
                                                                                                       height=None)),
                                                                                 TextNode("I will be waiting for thy next visit.")
                                                                                  ],
                                                                       cancel_response=TextNode("I will be waiting for thy next visit."))
                                                                       )
                                                               ],
                                                    cancel_response=TextNode("Wilt thou sell anything else?",
                                                                       query=Query(
                                                                       options=["YES", "NO"],
                                                                       responses=[TextNode("What art thou selling?",
                                                                                           query=Query(options=[],
                                                                                                       responses=[],
                                                                                                       cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                       query_type="Sell",
                                                                                                       width=9,
                                                                                                       height=None)),
                                                                                 TextNode("I will be waiting for thy next visit.")
                                                                                  ],
                                                                       cancel_response=TextNode("I will be waiting for thy next visit."))
                                                                       ),
                                                    width=4, height=3, query_type="Sell an Item",
                                                    transaction=Transaction(whatitem)))

                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                        elif self.hero.mode == "Shop":
                            if event.key == pygame.K_UP:
                                self.shop_selection -= 1
                                if self.shop_selection < 0:
                                    self.shop_selection = len(self.hero.walking_talk_box_message.query.options)-1
                            elif event.key == pygame.K_DOWN:
                                self.shop_selection += 1
                                if self.shop_selection > len(self.hero.walking_talk_box_message.query.options)-1:
                                    self.shop_selection = 0
                            elif event.key == pygame.K_x:
                                #invoke cancel option of query
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                            elif event.key == pygame.K_z:
                                #invoke option
                                if self.hero.G < self.hero.walking_talk_box_message.query.options[self.shop_selection].cost:
                                    whatnext = TextNode("Sorry. \tThou hast not enough money.", next=TextNode("Dost thou wish to buy anything more?", query=self.shop_base_query))
                                elif self.hero.walking_talk_box_message.query.options[self.shop_selection].type == "Weapon" and self.hero.weapon:
                                        whatnext = TextNode("Then I will buy thy "+self.hero.weapon.name+" for "+str(self.hero.weapon.cost/2)+" GOLD.", next=TextNode("Is that okay?", query=Query(options=["Yes", "No"],
                                                                                         transaction=Transaction(
                                                                                             self.hero.weapon),
                                                                                         transaction2=Transaction(
                                                                                             self.hero.walking_talk_box_message.query.options[
                                                                                                 self.shop_selection]),
                                                                                         query_type="Purchase and Sell",
                                                                                         cancel_response=TextNode(
                                                                                             "Oh, yes? That's too bad.",
                                                                                             next=TextNode(
                                                                                                 "Dost thou wish to buy anything more?",
                                                                                                 query=self.shop_base_query)),
                                                                                         responses=[
                                                                                             TextNode("I thank thee.",
                                                                                                      next=TextNode(
                                                                                                          "Dost thou wish to buy anything more?",
                                                                                                          query=self.shop_base_query)),
                                                                                             TextNode(
                                                                                                 "Oh, yes? That's too bad.",
                                                                                                 next=TextNode(
                                                                                                     "Dost thou wish to buy anything more?",
                                                                                                     query=self.shop_base_query))])))
                                elif self.hero.walking_talk_box_message.query.options[self.shop_selection].type == "Armor" and self.hero.armor:
                                    whatnext = TextNode("Then I will buy thy " + self.hero.armor.name + " for " + str(
                                        self.hero.armor.cost / 2) + " GOLD.",
                                                        next=TextNode("Is that okay?", query=Query(options=["Yes", "No"],
                                                                                                   transaction=Transaction(
                                                                                                       self.hero.armor),
                                                                                                   transaction2=Transaction(
                                                                                                       self.hero.walking_talk_box_message.query.options[
                                                                                                           self.shop_selection]),
                                                                                                   query_type="Purchase and Sell",
                                                                                                   cancel_response=TextNode(
                                                                                                       "Oh, yes? That's too bad.",
                                                                                                       next=TextNode(
                                                                                                           "Dost thou wish to buy anything more?",
                                                                                                           query=self.shop_base_query)),
                                                                                                   responses=[
                                                                                                       TextNode(
                                                                                                           "I thank thee.",
                                                                                                           next=TextNode(
                                                                                                               "Dost thou wish to buy anything more?",
                                                                                                               query=self.shop_base_query)),
                                                                                                       TextNode(
                                                                                                           "Oh, yes? That's too bad.",
                                                                                                           next=TextNode(
                                                                                                               "Dost thou wish to buy anything more?",
                                                                                                               query=self.shop_base_query))])))
                                elif self.hero.walking_talk_box_message.query.options[self.shop_selection].type == "Shield" and self.hero.shield:
                                    whatnext = TextNode("Then I will buy thy " + self.hero.shield.name + " for " + str(
                                        self.hero.shield.cost / 2) + " GOLD.",
                                                        next=TextNode("Is that okay?", query=Query(options=["Yes", "No"],
                                                                                                   transaction=Transaction(
                                                                                                       self.hero.shield),
                                                                                                   transaction2=Transaction(
                                                                                                       self.hero.walking_talk_box_message.query.options[
                                                                                                           self.shop_selection]),
                                                                                                   query_type="Purchase and Sell",
                                                                                                   cancel_response=TextNode(
                                                                                                       "Oh, yes? That's too bad.",
                                                                                                       next=TextNode(
                                                                                                           "Dost thou wish to buy anything more?",
                                                                                                           query=self.shop_base_query)),
                                                                                                   responses=[
                                                                                                       TextNode(
                                                                                                           "I thank thee.",
                                                                                                           next=TextNode(
                                                                                                               "Dost thou wish to buy anything more?",
                                                                                                               query=self.shop_base_query)),
                                                                                                       TextNode(
                                                                                                           "Oh, yes? That's too bad.",
                                                                                                           next=TextNode(
                                                                                                               "Dost thou wish to buy anything more?",
                                                                                                               query=self.shop_base_query))])))
                                else:
                                    whatnext = TextNode("Is that okay?", query=Query(options=["Yes", "No"],
                                                                                     transaction=Transaction(
                                                                                         self.hero.walking_talk_box_message.query.options[
                                                                                             self.shop_selection]),
                                                                                     query_type="Purchase",
                                                                                     cancel_response=TextNode(
                                                                                         "Oh, yes? That's too bad.",
                                                                                         next=TextNode(
                                                                                             "Dost thou wish to buy anything more?",
                                                                                             query=self.shop_base_query)),
                                                                                     responses=[TextNode("I thank thee.",
                                                                                                         next=TextNode(
                                                                                                             "Dost thou wish to buy anything more?",
                                                                                                             query=self.shop_base_query)),
                                                                                                TextNode(
                                                                                                    "Oh, yes? That's too bad.",
                                                                                                    next=TextNode(
                                                                                                        "Dost thou wish to buy anything more?",
                                                                                                        query=self.shop_base_query))]))
                                self.hero.walking_talk_box_message = TextNode("The " + str(self.hero.walking_talk_box_message.query.options[self.shop_selection].name) + "?", next=whatnext)
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"

                        elif self.hero.mode == "Inn":
                            if event.key == pygame.K_UP:
                                self.shop_selection -= 1
                                if self.shop_selection < 0:
                                    self.shop_selection = len(self.hero.walking_talk_box_message.query.options)-1
                            elif event.key == pygame.K_DOWN:
                                self.shop_selection += 1
                                if self.shop_selection > len(self.hero.walking_talk_box_message.query.options)-1:
                                    self.shop_selection = 0
                            elif event.key == pygame.K_x:
                                #invoke cancel option of query
                                self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                self.hero.mode = "Talking"
                            elif event.key == pygame.K_z:
                                #invoke option
                                if self.hero.walking_talk_box_message.query.options[self.shop_selection] == "Yes" and self.hero.G >= self.shop_base_query.query_inn_price:
                                    self.hero.G -= self.shop_base_query.query_inn_price
                                    self.hero.walking_talk_box_message = TextNode("Good night.")
                                    self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                    self.hero.mode = "Talking then Sleeping"
                                    self.morning_after_message = TextNode("Good morning. \tThou seems to have spent a good night.", next=TextNode("I shall see thee again."))
                                elif self.hero.walking_talk_box_message.query.options[self.shop_selection] == "Yes" and self.hero.G < self.shop_base_query.query_inn_price:
                                    self.hero.walking_talk_box_message = TextNode("Thou hast not enough money.")
                                    self.hero.mode = "Talking"
                                    self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                else:
                                    self.hero.walking_talk_box_message = self.hero.walking_talk_box_message.query.cancel_response
                                    self.hero.mode = "Talking"
                                    self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)


                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            self.hero.flag_left = False
                            self.hero.flag_moving = False
                        elif event.key == pygame.K_DOWN:
                            self.hero.flag_down = False
                            self.hero.flag_moving = False
                        elif event.key == pygame.K_UP:
                            self.hero.flag_up = False
                            self.hero.flag_moving = False
                        elif event.key == pygame.K_RIGHT:
                            self.hero.flag_right = False
                            self.hero.flag_moving = False
            else:

                self.delta_ticks = clock.tick(60)#pygame.time.get_ticks() - self.last_ticks
                self.last_ticks = pygame.time.get_ticks()
                self.screen.fill(pygame.Color(0, 0, 0))


                if self.screen_mode == "Screen Title" or self.screen_mode == "Screen Title With Intro":
                    TitleScreenDrawer.draw(self)

                if self.screen_mode == "Begin or Continue":
                    BeginGameWindowDrawer.draw(self)

                    if self.select_available_log or self.select_continue_log:
                        SelectAdventureLogWindowDrawer.draw(self)

                    if self.name_input:
                        NameInputWindowDrawer.draw(self)

                    if self.msg_speed_window:
                        MessageSpeedWindowDrawer.draw(self)


                if self.screen_mode == "Play":
                    if self.hero.map_transition:
                        self.hero.screenfadeticks += self.delta_ticks
                        if self.hero.screenfadeticks >= self.hero.screenfadetickspeed:
                            self.hero.screenfadeticks = self.hero.screenfadetickspeed
                            if self.hero.screenfade == "out":
                                self.hero.screenfade = "between"
                                self.hero.screenfadeticks = 0
                                self.hero.betweenfadeticks = 0
                                self.alpha = 0
                                if not self.hero.map_transition_with_sleep:
                                    self.hero.execute_map_change()
                                    changeBGMusic(self.hero.music_id)
                            elif self.hero.screenfade == "in":
                                self.hero.screenfade = None
                                self.hero.screenfadeticks = 0
                                self.hero.map_transition = False

                                if self.hero.map_transition_with_sleep:
                                    self.hero.map_transition_with_sleep = False
                                    self.hero.walking_talk_box_message = self.morning_after_message
                                    self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=False)
                                    self.hero.MP = self.hero.maxmp
                                    self.hero.HP = self.hero.maxhp
                                    self.hero.mode = "Talking"
                                else:
                                    self.alpha = 255
                                    self.walking_talk_box_ticks = 0
                                    self.side_box.reset()
                                    self.walking_command_ticks = 0
                                    self.walking_talk_box_msg_ticks = 0
                                    self.hero.mode = "Walking"
                                    if self.hero.is_dead:
                                        self.hero.is_dead = False
                                        self.hero.oktolorikafterdying = True
                                        self.hero.enemy = Enemy("Red Slime")
                                        self.hero.battle_mode = False
                                        self.hero.battle_report_mode = False
                                        self.hero.HP = self.hero.maxhp
                                        self.hero.G = self.hero.G / 2
                                        self.hero.MP = self.hero.maxmp
                            else:
                                self.hero.betweenfadeticks += self.delta_ticks
                                if self.hero.betweenfadeticks >= self.hero.betweenfadetickspeed:
                                    self.hero.betweenfadeticks = 0
                                    self.hero.screenfade = "in"
                                    self.hero.screenfadeticks = 0



                    if self.hero.screenfade == "in":
                        self.alpha = 255 * (self.hero.screenfadeticks/float(self.hero.screenfadetickspeed))
                    elif self.hero.screenfade == "out":
                        self.alpha = 255 * (1 - self.hero.screenfadeticks/float(self.hero.screenfadetickspeed))



                    if self.hero.do_ending_credits:

                        self.ending_credits_ticks += self.delta_ticks
                        if self.ending_credits_ticks >= 500 and self.ending_credits_ticks < 7500:
                            whatdraw = pygame.transform.scale(self.ending_screen, (int(NUM_CELLS_WIDE*0.80)*self.unitsizex, int(NUM_CELLS_HIGH*0.70)*self.unitsizey))
                            self.screen.blit(whatdraw, pygame.rect.Rect(self.screen.get_width()/2 - whatdraw.get_width()/2, self.screen.get_height()/2 - whatdraw.get_height()/2, whatdraw.get_width(), whatdraw.get_height()))
                        elif self.ending_credits_ticks >= 7500 and self.ending_credits_ticks < 12500:
                            self.screen.blit(self.gamefont.render("Thank you for playing.", False, (255,255,255)),(int(NUM_CELLS_WIDE*0.29) * self.unitsizex, int(NUM_CELLS_HIGH*0.5) * self.unitsizey))
                        elif self.ending_credits_ticks >= 12500 and self.ending_credits_ticks < 17500:
                            self.screen.blit(self.gamefont.render("And then the next day...", False, (255,255,255)),(int(NUM_CELLS_WIDE*0.28) * self.unitsizex, int(NUM_CELLS_HIGH*0.5) * self.unitsizey))
                        elif self.ending_credits_ticks >= 17500:
                            self.hero.do_ending_credits = False
                            self.hero.data["POSTGAME"] = True
                            self.hero.mode = "Transitioning"
                            self.hero.mx = 45
                            self.hero.my = 45
                            self.hero.moffsetx = - self.hero.mx + NUM_CELLS_WIDE / 2
                            self.hero.moffsety = - self.hero.my + NUM_CELLS_HIGH / 2
                            self.hero.teleport_pack = ("World", self.hero.sizex, self.hero.sizey)
                            self.hero.map_transition = True
                            self.hero.flag_moving = False
                            self.hero.flag_left = False
                            self.hero.flag_right = False
                            self.hero.flag_up = False
                            self.hero.flag_down = False
                            self.hero.screenfade = "out"
                            self.hero.screenfadeticks = 0
                            self.hero.display_item_window = False
                            self.hero.walking_talk_box_visible = False
                            self.hero.walking_talk_box_message = TextNode("")
                            self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=True)
                    else:

                        #resizing spell box
                        if self.hero.learned_new_spell:
                            self.spell_box.redefine_surface(self.spell_box.num_cells_wide, len(self.hero.spells)+1.0)
                            self.hero.learned_new_spell = False

                        #hp low = red menu
                        if not self.frozen:
                            if self.hero.HP/float(self.hero.maxhp) < 0.35:
                                self.menu_color = (255, 128, 128)
                                self.command_selector = self.command_selector_red
                            else:
                                self.menu_color = (255, 255, 255)
                                self.command_selector = self.command_selector_white

                        #draw the map
                        dl = self.hero.enemy.name == "Dragonlord" and self.hero.enemy._dl == 2
                        if not dl:
                            for y in range(int(self.hero.y-NUM_CELLS_HIGH/2-2), int(self.hero.y+NUM_CELLS_HIGH/2+2)):
                                for x in range(int(self.hero.x-NUM_CELLS_WIDE/2-2), int(self.hero.x+NUM_CELLS_WIDE/2+3)):
                                    drawx = x + self.hero.offsetx
                                    drawy = y + self.hero.offsety
                                    if self.hero.map.name == "Charlock Castle" and x == self.hero.map.secret_stairs[0].x and y == self.hero.map.secret_stairs[0].y and self.hero.data.get("Charlock Castle Stairs"):
                                        tile = self.tiles[16]
                                    elif self.hero.map.name == "Hauksness" and x == self.hero.map.secret_stairs[0].x and y == self.hero.map.secret_stairs[0].y and self.hero.data.get("Hauksness Stairs"):
                                        tile = self.tiles[16]
                                    elif self.hero.map.name == "World" and self.hero.data.get("Rainbow Bridge", False) and x == 66 and y == 51:
                                        tile = self.tiles[3]
                                    else:
                                        if x >= 0 and x < len(self.hero.map.map_data[0]) and y >= 0 and y < len(self.hero.map.map_data):
                                            if self.hero.HP / float(self.hero.maxhp) < 0.35 and self.hero.map.map_data[y][x] >= 23 and self.hero.map.map_data[y][x] <= 38:  #water tiles -> red
                                                tile = self.red_tiles[self.hero.map.map_data[y][x]]
                                            else:
                                                tile = self.tiles[self.hero.map.map_data[y][x]]

                                            if self.hero.map.map_data[y][x] == 14 and self.hero.data.get("RPR_1", False):
                                                tile = self.tiles[5]  # castle floor after Gwaelin is picked up
                                        else:
                                            if self.hero.HP / float(self.hero.maxhp) < 0.35 and self.hero.map.background_tile >= 23 and self.hero.map.background_tile <= 38:
                                                tile = self.red_tiles[self.hero.map.background_tile]
                                            else:
                                                tile = self.tiles[self.hero.map.background_tile]
                                    for door in self.hero.map.doors:
                                        if door.x == x and door.y == y and self.hero.data.get(door.name, False):
                                            tile = self.tiles[5] #castle floor after a door is cleared
                                    for hidden_item in self.hero.map.chests:
                                        if hidden_item.x == x and hidden_item.y == y and not self.hero.data.get(hidden_item.name, False):
                                            tile = self.tiles[7] #chest
                                            break

                                    if x >= 0 and x < len(self.hero.map.map_data[0]) and y >= 0 and y < len(self.hero.map.map_data) and self.hero.map.map_data[y][x] >= 23 and self.hero.map.map_data[y][x] <= 35 and not self.hero.map.map_data[y][x] == 33:
                                        whatdraw = pygame.transform.scale(tile.subsurface(pygame.rect.Rect(0,0 + self.hero.rainbowcolorindex*16 + self.hero.rainbowcolorindex,16,16)), (self.unitsizex, self.unitsizey))
                                    else:
                                        whatdraw = pygame.transform.scale(tile.subsurface(pygame.rect.Rect(0,0,16,16)), (self.unitsizex, self.unitsizey))
                                    whatdraw.set_alpha(self.alpha)
                                    self.screen.blit(whatdraw, pygame.rect.Rect((drawx+0.5) * self.unitsizex + (2*self.screen_shake_shift_x/32.0)*self.unitsizex, (drawy+0.5) * self.unitsizey + (2*self.screen_shake_shift_y/32.0)*self.unitsizey, self.unitsizex, self.unitsizey))

                        #obscure map if dungeon
                        if self.hero.map.is_dark or dl:
                            pygame.draw.rect(self.screen, (0,0,0), (0, 0, self.unitsizex*((NUM_CELLS_WIDE/2+0.5)-self.hero.radiance_level), self.unitsizey*(NUM_CELLS_HIGH+0.5)), 0)
                            pygame.draw.rect(self.screen, (0,0,0), (0, 0, self.unitsizex*(NUM_CELLS_WIDE+0.5), self.unitsizey*((NUM_CELLS_HIGH/2+0.5)-self.hero.radiance_level)), 0)
                            pygame.draw.rect(self.screen, (0,0,0), (self.unitsizex*((NUM_CELLS_WIDE/2+0.5)+self.hero.radiance_level+1), 0, self.unitsizex*(NUM_CELLS_WIDE-(NUM_CELLS_WIDE/2)+self.hero.radiance_level+0.5), self.unitsizey*(NUM_CELLS_HIGH+0.5)), 0)
                            pygame.draw.rect(self.screen, (0,0,0), (0, self.unitsizey*((NUM_CELLS_HIGH/2+0.5)+self.hero.radiance_level+1), self.unitsizex*(NUM_CELLS_WIDE+0.5), self.unitsizey*(NUM_CELLS_HIGH-(NUM_CELLS_HIGH/2)+self.hero.radiance_level+0.5)), 0)


                        if not dl:
                            # draw npcs
                            for npc in self.hero.map.NPCs:
                                if npc.all_conditions_satisfied(self.hero.items, self.hero.data) and not self.hero.data.get(npc.name, False):
                                    if self.hero.mode == "Walking":
                                        npc.update(self.delta_ticks, self.hero.data, self.hero.motion_in_progress)

                                    if npc.type != "Kidnapped Princess":
                                        whatdraw = npc.getSurface()
                                        whatdraw.set_alpha(self.alpha)
                                        self.screen.blit(whatdraw, pygame.rect.Rect((npc.x - self.hero.x + (NUM_CELLS_WIDE/2)+0.5) * self.unitsizex,
                                                                                            (npc.y - self.hero.y + (NUM_CELLS_HIGH/2)+0.5) * self.unitsizey,
                                                                                                  self.unitsizex, self.unitsizey))

                            #update hero
                            self.hero.update(self.delta_ticks)
                            #draw hero
                            if not self.hero.mode == "Transitioning Softly":
                                whatdraw = self.hero.getSurface()
                                whatdraw.set_alpha(self.alpha)
                                self.screen.blit(whatdraw, pygame.rect.Rect((NUM_CELLS_WIDE/2+0.5)*self.unitsizex, (NUM_CELLS_HIGH/2+0.5)*self.unitsizey, self.unitsizex, self.unitsizey))


                        #draw walking menu
                        if self.hero.mode == "Menu" or self.hero.mode == "Talking" or self.hero.mode == "Spell" or self.hero.mode == "Item" or self.hero.mode == "Talking then Sleeping" or self.hero.mode == "Query" or self.hero.mode == "Shop" or self.hero.mode == "Mini Shop" or self.hero.mode == "ItemShop" or self.hero.mode == "Discard an Item" or self.hero.mode == "Sell" or self.hero.mode == "Status" or self.hero.mode == "Inn":
                            SideWindowDrawer.draw(self)

                            if not self.hero.battle_mode and not self.hero.battle_report_mode and not self.hero.teleport_via_death:
                                CommandWindowDrawer.draw(self)
                            else:
                                #draw battle command instead
                                if not self.hero.youdied and not self.hero.teleport_via_death and not self.hero.enemy_is_dead and not self.hero.chose_a_turn and not self.hero.enemy_turn and not self.hero.heroattack and not self.hero.enemyattack and not self.hero.enemy_red_shadow and not self.hero.enemy_spiral_flag and not self.hero.spell_cast and not self.hero.battle_running:


                                    self.walking_command_ticks += self.delta_ticks
                                    if self.walking_command_ticks > self.walking_command_drawspeedticks:
                                        self.walking_command_ticks = self.walking_command_drawspeedticks
                                    self.screen.blit(self.battle_command.subsurface(pygame.rect.Rect(0,0,8*self.unitsizex, int(3*self.unitsizey*(self.walking_command_ticks/self.walking_command_drawspeedticks)))), ((5+0.5) * self.unitsizex, 0.5 * self.unitsizey))
                                    self.battle_command.fill(pygame.Color(0, 0, 0))
                                    pygame.draw.rect(self.battle_command, self.menu_color, (self.unitsizex/8, self.unitsizex/8, self.battle_command.get_width()-self.unitsizex/4, self.battle_command.get_height()-self.unitsizey/4-self.unitsizex/16), self.unitsizex/8)
                                    pygame.draw.rect(self.battle_command, (0, 0, 0), (1.75 * self.unitsizex, 0 * self.unitsizey, 3.25 * self.unitsizex, 1 * self.unitsizey), 0)
                                    self.battle_command.blit(self.gamefont.render("COMMAND", False, self.menu_color),(2 * self.unitsizex, 0 * self.unitsizey))
                                    self.battle_command.blit(self.gamefont.render("FIGHT", True, self.menu_color), (1 * self.unitsizex, 1 * self.unitsizey))
                                    self.battle_command.blit(self.gamefont.render("SPELL", True, self.menu_color), (5 * self.unitsizex, 1 * self.unitsizey))
                                    self.battle_command.blit(self.gamefont.render("RUN", True, self.menu_color),  (1 * self.unitsizex, 2 * self.unitsizey))
                                    self.battle_command.blit(self.gamefont.render("ITEM", True, self.menu_color),  (5 * self.unitsizex, 2 * self.unitsizey))
                                    if self.walking_command_selector_visible and not self.hero.mode == "Item" and not self.hero.mode == "Spell":
                                        self.battle_command.blit(pygame.transform.scale(self.command_selector, (self.unitsizex, self.unitsizey)),pygame.rect.Rect((4*self.battle_command_selector_x) * self.unitsizex, (1+self.battle_command_selector_y) * self.unitsizey, self.unitsizex, self.unitsizey))
                                if self.hero.battle_mode or self.hero.battle_report_mode:
                                    self.screen.blit(self.battle_box.subsurface(pygame.rect.Rect(0, 0, 7 * self.unitsizex, self.unitsizey * 7)), (4.5 * self.unitsizex, 3.5 * self.unitsizey))
                                    self.battle_box = pygame.Surface((self.unitsizex * 7, self.unitsizey * 7), pygame.SRCALPHA, 32).convert_alpha()
                                    if self.hero.map.is_dungeon:
                                        if self.hero.enemy_spiral_flag:
                                            for spiral in self.hero.enemy_spiral[:self.hero.enemy_spiral_index]:
                                                pygame.draw.rect(self.battle_box, (0,0,0), (spiral[0]*self.unitsizex, spiral[1]*self.unitsizey, self.unitsizex, self.unitsizey))
                                        else:
                                            self.battle_box.fill(pygame.Color(0, 0, 0))
                                    else:
                                        if self.hero.enemy_spiral_flag:
                                            for spiral in self.hero.enemy_spiral[:self.hero.enemy_spiral_index]:
                                                whatdraw = pygame.transform.scale(self.enemy_background.subsurface(  pygame.rect.Rect(spiral[0]*16, spiral[1]*16, 16, 16) ), (1*self.unitsizex, 1*self.unitsizey))
                                                whatdraw.set_alpha(self.alpha)
                                                self.battle_box.blit(whatdraw, pygame.rect.Rect(spiral[0]*self.unitsizex, spiral[1]*self.unitsizey, self.unitsizex, self.unitsizey))
                                        else:
                                            whatdraw = pygame.transform.scale(self.enemy_background, (7*self.unitsizex, 7*self.unitsizey))
                                            whatdraw.set_alpha(self.alpha)
                                            self.battle_box.blit(whatdraw, pygame.rect.Rect(0, 0, 7*self.unitsizex, 7*self.unitsizey))
                                    if not self.hero.enemy_is_dead and not self.hero.enemy_spiral_flag and not self.hero.battle_running:
                                        if not dl:
                                            whatenemydraw = pygame.transform.scale(self.hero.enemy.image, (int((self.unitsizex/16.0)*self.hero.enemy.image.get_width()), int((self.unitsizey/16.0)*self.hero.enemy.image.get_height())))
                                            self.battle_box.blit(whatenemydraw, (int((self.battle_box.get_width()-whatenemydraw.get_width())/2), int((self.battle_box.get_height()-whatenemydraw.get_height())/2)))
                                        else:
                                            whatenemydraw = pygame.transform.scale(self.hero.enemy.image, (int((self.unitsizex/16.0)*self.hero.enemy.image.get_width()), int((self.unitsizey/16.0)*self.hero.enemy.image.get_height())))
                                            self.battle_box.blit(whatenemydraw, (int((self.battle_box.get_width()-whatenemydraw.get_width())/2), int(0.05*(self.battle_box.get_height()-whatenemydraw.get_height()))))

                            #self.walking_command_selector_ticks += self.delta_ticks
                            #if self.walking_command_selector_ticks > self.walking_command_selector_blinkspeedticks:
                            #    self.walking_command_selector_ticks = 0
                            #    self.walking_command_selector_visible = not self.walking_command_selector_visible
                            #if self.walking_command_selector_visible or self.hero.mode == "Talking":
                            #    if not self.hero.mode == "Item" and not self.hero.mode == "Spell" and not self.hero.mode == "Status":
                            #        self.walking_command.blit(pygame.transform.scale(self.command_selector, (self.unitsizex, self.unitsizey)), pygame.rect.Rect((4*self.walking_command_selector_x) * self.unitsizex, (1+self.walking_command_selector_y) * self.unitsizey, self.unitsizex, self.unitsizey))

                            if self.hero.walking_talk_box_visible:
                                #self.walking_talk_box_ticks += self.delta_ticks
                                #if self.walking_talk_box_ticks > self.walking_talk_box_drawspeedticks:
                                #    self.walking_talk_box_ticks = self.walking_talk_box_drawspeedticks

                                self.chat_box.increment_ticks(self.delta_ticks)
                                self.chat_box.draw(self.screen,
                                                   bump_x=self.screen_shake_shift_x,
                                                   bump_y=self.screen_shake_shift_y)
                                #if not dl:
                                #    self.screen.blit(self.walking_talk_box.subsurface(pygame.rect.Rect(0,0, self.unitsizex*12, int(5.5*self.unitsizey*(self.walking_talk_box_ticks/self.walking_talk_box_drawspeedticks)))), (1.5 * self.unitsizex + (2*self.screen_shake_shift_x/32.0)*self.unitsizex, 8.5 * self.unitsizey + (2*self.screen_shake_shift_y/32.0)*self.unitsizey))
                                #else:
                                #    self.screen.blit(self.walking_talk_box.subsurface(pygame.rect.Rect(0,0, self.unitsizex*12, int(5.5*self.unitsizey*(self.walking_talk_box_ticks/self.walking_talk_box_drawspeedticks)))), (1.5 * self.unitsizex + (2*self.screen_shake_shift_x/32.0)*self.unitsizex, 9.5 * self.unitsizey + (2*self.screen_shake_shift_y/32.0)*self.unitsizey))
                                #self.walking_talk_box.fill(pygame.Color(0, 0, 0))
                                self.chat_box.fill(self.black)
                                self.chat_box.draw_border(self.menu_color)
                                #pygame.draw.rect(self.walking_talk_box, self.menu_color, (self.unitsizex/8, self.unitsizex/8, self.walking_talk_box.get_width()-self.unitsizex/4, self.walking_talk_box.get_height()-self.unitsizey/4-self.unitsizex/16), self.unitsizex/8)
                                words = self.hero.walking_talk_box_message_to_render.split(" ")
                                lines = []
                                line = ""
                                words = [word for word in words if len(word) > 0]
                                #print words
                                quoted = False
                                for word in words:
                                    if not word[0] == "\n" and not word[0] == "\t":
                                        if word[0] == "`":
                                            quoted = True
                                    elif len(word) > 1:
                                        if word[1] == "`":
                                            quoted = True

                                    if word[0] == "\n":
                                        lines.append(line+"")
                                        lines.append("")
                                        if quoted:
                                            if word[1] == "`":
                                                line = word[1:] + " "
                                            else:
                                                line = " " + word[1:] + " "
                                        else:
                                            line = word[1:] + " "
                                    elif word[0] == "\t":
                                        lines.append(line)
                                        if quoted:
                                            if word[1] == "`":
                                                line = word[1:] + " "
                                            else:
                                                line = " " + word[1:] + " "
                                        else:
                                            line = word[1:] + " "
                                    else:
                                        if not len(line+" "+word) > 25:
                                            line += word + " "
                                        else:
                                            lines.append(line)
                                            if quoted:
                                                line = " " + word + " "
                                            else:
                                                line = word + " "
                                    if word[-1] == "'":
                                        quoted = False
                                #line = line[:-1]
                                lines.append(line)# + "'")
                                self.walking_talk_box_msg_ticks += self.delta_ticks
                                lenmsg = sum([len(l) for l in lines])
                                if self.walking_talk_box_msg_ticks > (lenmsg*self.walking_talk_box_msgtickspeed):
                                    self.donetalkingitsokaytoacceptinput = True

                                    if self.hero.npc_name == "RPR_1" and not self.hero.walking_talk_box_message.query and not self.hero.walking_talk_box_message.next and not self.hero.data.get(self.hero.npc_name, False):
                                        self.hero.data[self.hero.npc_name] = True
                                        self.hero.sprite_identity = "Princess"
                                        self.hero.map.mutex_data[(self.hero.npc.x, self.hero.npc.y)] = False
                                    elif not self.hero.walking_talk_box_message.next and not self.hero.walking_talk_box_message.query and self.hero.npc_special_action == "Disappear" and not self.hero.data.get(self.hero.npc_name, False):
                                        self.hero.data[self.hero.npc_name] = True
                                        self.hero.map.mutex_data[(self.hero.npc.x,self.hero.npc.y)] = False
                                        if self.hero.npc_name == "NRS_2":
                                            self.hero.remove_from_inventory(Item("Silver Harp"))
                                    elif self.hero.walking_talk_box_message.action and self.hero.npc_special_action == "Gwaelin's Love" and not self.hero.data.get(self.hero.npc_name, False):
                                        self.hero.data[self.hero.npc_name] = True
                                        self.hero.map.mutex_data[(58, 4)] = False
                                        self.hero.items.append(Item("Gwaelin's Love"))
                                        self.hero.data["Princess is Rescued"] = True
                                        self.hero.map = Map.load_map("Tantegel", self.hero.sizex, self.hero.sizey)
                                        self.hero.map.background_tile = 40
                                        self.hero.update_sprite()
                                    elif not self.hero.walking_talk_box_message.next and not self.hero.walking_talk_box_message.query and self.hero.npc_special_action == "Eviction":
                                        self.hero.eviction = True
                                        self.hero.delayticks = 0
                                        self.hero.spell_blinks = 0
                                        self.hero.spell_cast = True
                                        self.hero.spell_blink_ticks = 0
                                        self.hero.spell_chanted = Spell("None")
                                        self.hero.mode = "Walking"
                                        self.hero.npc_special_action = "Nothing"
                                        #self.hero.walking_talk_box_message.next = None
                                    elif not self.hero.walking_talk_box_message.next and not self.hero.walking_talk_box_message.query and self.hero.npc_special_action == "Remove Curse":
                                        if self.hero.death_necklace:
                                            self.hero.death_necklace = False
                                            self.hero.remove_from_inventory(Item("Death Necklace"))
                                            self.hero.data["DeathNecklace"] = False
                                        if self.hero.cursed_belt:
                                            self.hero.cursed_belt = False
                                            self.hero.remove_from_inventory(Item("Cursed Belt"))
                                            self.hero.data["CursedBelt"] = False
                                    elif not self.hero.walking_talk_box_message.next and not self.hero.walking_talk_box_message.query and self.hero.npc_special_action == "MP Recovery":
                                        self.hero.spell_chanted = None
                                        self.hero.npc_special_action = None
                                        self.hero.MP = self.hero.maxmp
                                        self.hero.spell_blinks = 0
                                        self.hero.spell_blink_ticks = 0
                                        self.hero.spell_cast = True
                                        self.spell_lag = True
                                        self.spell_lag_tickspeed = 150.0

                                    self.walking_talk_box_msg_ticks = (lenmsg*self.walking_talk_box_msgtickspeed)
                                    if self.hero.mode == "Talking then Sleeping":
                                        self.hero.mode = "Transitioning"
                                        self.hero.map_transition = True
                                        self.hero.map_transition_with_sleep = True
                                        self.hero.map_transition_ticks = 0
                                        self.hero.screenfade = "out"
                                        self.hero.screenfadeticks = 0
                                    if not self.hero.mode == "Query" and not self.hero.mode == "Shop" and not self.hero.mode == "ItemShop" and not self.hero.mode == "Mini Shop" and not self.hero.mode == "Sell" and not self.hero.mode == "Inn" and not self.hero.mode == "Discard an Item" and self.hero.walking_talk_box_message.query:
                                        if self.hero.walking_talk_box_message.query.query_type == "Shop":
                                            self.hero.mode = "Shop"
                                            self.query_box = pygame.Surface((self.hero.walking_talk_box_message.query.width * self.unitsizex, self.hero.walking_talk_box_message.query.height * self.unitsizey))
                                            self.query_box_ticks = 0
                                            self.query_selection = 0
                                            self.shop_base_query = self.hero.walking_talk_box_message.query
                                        elif self.hero.walking_talk_box_message.query.query_type == "Mini Shop":
                                            self.hero.mode = "Mini Shop"
                                            self.query_box = pygame.Surface((self.hero.walking_talk_box_message.query.width * self.unitsizex, self.hero.walking_talk_box_message.query.height * self.unitsizey))
                                            self.query_box_ticks = 0
                                            self.query_selection = 0
                                            self.shop_base_query = self.hero.walking_talk_box_message.query
                                        elif self.hero.walking_talk_box_message.query.query_type == "ItemShop":
                                            self.hero.mode = "ItemShop"
                                            self.query_box = pygame.Surface((self.hero.walking_talk_box_message.query.width * self.unitsizex, self.hero.walking_talk_box_message.query.height * self.unitsizey))
                                            self.query_box_ticks = 0
                                            self.query_selection = 0
                                            self.shop_base_query = self.hero.walking_talk_box_message.query
                                        elif self.hero.walking_talk_box_message.query.query_type == "Discard Item":
                                            self.hero.mode = "Discard an Item"
                                            self.query_box = pygame.Surface((5 * self.unitsizex, (1.5+self.hero.get_item_inv_size()) * self.unitsizey))
                                            self.query_box_ticks = 0
                                            self.query_selection = 0
                                            self.shop_base_query = self.hero.walking_talk_box_message.query
                                        elif self.hero.walking_talk_box_message.query.query_type == "Sell":
                                            self.hero.mode = "Sell"
                                            self.query_box = pygame.Surface((5 * self.unitsizex, (1.5+self.hero.get_item_inv_size()) * self.unitsizey))
                                            self.query_box_ticks = 0
                                            self.query_selection = 0
                                            self.shop_base_query = self.hero.walking_talk_box_message.query
                                        elif self.hero.walking_talk_box_message.query.query_type == "Inn":
                                            self.hero.mode = "Inn"
                                            self.query_box = pygame.Surface((self.hero.walking_talk_box_message.query.width * self.unitsizex, self.hero.walking_talk_box_message.query.height * self.unitsizey))
                                            self.query_box_ticks = 0
                                            self.query_selection = 0
                                            self.shop_base_query = self.hero.walking_talk_box_message.query
                                        else:
                                            self.hero.mode = "Query"
                                            self.query_box = pygame.Surface((self.hero.walking_talk_box_message.query.width*self.unitsizex, self.hero.walking_talk_box_message.query.height*self.unitsizey))
                                            self.query_box_ticks = 0
                                            self.query_selection = 0
                                    elif self.hero.walking_talk_box_message.next:
                                        self.hero.walking_talk_box_msg_tick_next = True
                                    else:
                                        self.hero.walking_talk_box_msg_tick_next = False
                                else:
                                    self.donetalkingitsokaytoacceptinput = False

                                maxmsgrender = int(lenmsg*(self.walking_talk_box_msg_ticks/float((lenmsg*self.walking_talk_box_msgtickspeed))))
                                currrender = 0
                                linestorender = []
                                for i,line in enumerate(lines):
                                    lline = len(line)
                                    if currrender+lline <= maxmsgrender:
                                        linestorender.append(line)
                                        currrender += lline
                                    else:
                                        if currrender <= maxmsgrender:
                                            allowedtorender = maxmsgrender-currrender
                                            linestorender.append(line[:allowedtorender+1])
                                            currrender += allowedtorender
                                            break
                                for i,line in enumerate(linestorender[-7:]):
                                    self.chat_box.draw_string(line, self.gamefont, self.menu_color, 0.6, (i + 1) * 0.4 + 0.1 * i)
                                if self.hero.walking_talk_box_msg_tick_next:
                                    self.chat_box.draw_selector(self.command_selector, rotate=270, shift_x=6, shift_y=(i + 1) * 0.4 + 0.1 * i)

                            if self.hero.mode == "Query" or self.hero.mode == "Mini Shop":
                                self.query_box_ticks += self.delta_ticks
                                if self.query_box_ticks > self.query_box_drawspeedticks:
                                    self.query_box_ticks = self.query_box_drawspeedticks

                                self.screen.blit(self.query_box.subsurface(pygame.rect.Rect(0, 0, self.hero.walking_talk_box_message.query.width * self.unitsizex,int(self.hero.walking_talk_box_message.query.height * self.unitsizey * (self.query_box_ticks / self.query_box_drawspeedticks)))), (5 * self.unitsizex, 2 * self.unitsizey))
                                self.query_box.fill(pygame.Color(0, 0, 0))
                                pygame.draw.rect(self.query_box, self.menu_color, (self.unitsizex/8, self.unitsizex/8, self.query_box.get_width()-self.unitsizex/4, self.query_box.get_height()-self.unitsizey/4-self.unitsizex/16), self.unitsizex/8)
                                for i,option in enumerate(self.hero.walking_talk_box_message.query.options):
                                    self.query_box.blit(self.gamefont.render(option, True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                if self.walking_command_selector_visible:
                                    self.query_box.blit(
                                        pygame.transform.scale(self.command_selector, (self.unitsizex, self.unitsizey)),
                                        pygame.rect.Rect(0 * self.unitsizex,
                                                         (1+self.query_selection) * self.unitsizey,
                                                         self.unitsizex, self.unitsizey))


                            if self.hero.mode == "Shop" or self.hero.mode == "ItemShop":
                                self.query_box_ticks += self.delta_ticks
                                if self.query_box_ticks > self.query_box_drawspeedticks:
                                    self.query_box_ticks = self.query_box_drawspeedticks
                                self.screen.blit(self.query_box.subsurface(pygame.rect.Rect(0, 0, self.hero.walking_talk_box_message.query.width * self.unitsizex,int(self.hero.walking_talk_box_message.query.height * self.unitsizey * (self.query_box_ticks / self.query_box_drawspeedticks)))), (5 * self.unitsizex, 2 * self.unitsizey))
                                self.query_box.fill(pygame.Color(0, 0, 0))
                                pygame.draw.rect(self.query_box, self.menu_color, (self.unitsizex/8, self.unitsizex/8, self.query_box.get_width()-self.unitsizex/4, self.query_box.get_height()-self.unitsizey/4-self.unitsizex/16), self.unitsizex/8)
                                for i,option in enumerate(self.hero.walking_talk_box_message.query.options):
                                    option_words = option.name.split(" ")
                                    if len(option_words) > 2:
                                        if len(option_words[0]) + len(option_words[1]) > 8: #line 1 has only first word, line 2 has both words.  price goes on line 1
                                            self.query_box.blit(self.gamefont.render(option_words[0] + (18-len(option_words[0]+str(option.cost)))*" " + str(option.cost), True, self.menu_color), (1 * self.unitsizex, (0.5+i) * self.unitsizey))
                                            self.query_box.blit(self.gamefont.render(" " + " ".join(option_words[1:]), True, self.menu_color), (1 * self.unitsizex, (1.0+i) * self.unitsizey))
                                        else:
                                            self.query_box.blit(self.gamefont.render(" ".join(option_words[:2]) + (18-len(" ".join(option_words[:2])+str(option.cost)))*" " + str(option.cost), True, self.menu_color), (1 * self.unitsizex, (0.5+i) * self.unitsizey))
                                            self.query_box.blit(self.gamefont.render(" " + " ".join(option_words[2:]), True, self.menu_color), (1 * self.unitsizex, (1.0+i) * self.unitsizey))
                                    elif len(option_words) == 2:
                                        if len(option_words[0]) + len(option_words[1]) > 8: #line 1 has only first word, line 2 has second word.  price goes on line 1
                                            self.query_box.blit(self.gamefont.render(option_words[0] + (18-len(option_words[0]+str(option.cost)))*" " + str(option.cost), True, self.menu_color), (1 * self.unitsizex, (0.5+i) * self.unitsizey))
                                            self.query_box.blit(self.gamefont.render(" " + " ".join(option_words[1:]), True, self.menu_color), (1 * self.unitsizex, (1.0+i) * self.unitsizey))
                                        else:
                                            self.query_box.blit(self.gamefont.render(" ".join(option_words[:]) + (18-len(" ".join(option_words[:])+str(option.cost)))*" " + str(option.cost), True, self.menu_color), (1 * self.unitsizex, (0.5+i) * self.unitsizey))
                                    else:
                                        self.query_box.blit(self.gamefont.render(" ".join(option_words[:]) + (18-len(" ".join(option_words[:])+str(option.cost)))*" " + str(option.cost), True, self.menu_color), (1 * self.unitsizex, (0.5+i) * self.unitsizey))

                                if self.walking_command_selector_visible:
                                    self.query_box.blit(
                                        pygame.transform.scale(self.command_selector, (self.unitsizex, self.unitsizey)),
                                        pygame.rect.Rect(0 * self.unitsizex,
                                                         (0.5+self.shop_selection) * self.unitsizey,
                                                         self.unitsizex, self.unitsizey))

                            if self.hero.mode == "Sell" or self.hero.mode == "Discard an Item":
                                self.query_box_ticks += self.delta_ticks
                                if self.query_box_ticks > self.query_box_drawspeedticks:
                                    self.query_box_ticks = self.query_box_drawspeedticks
                                self.screen.blit(self.query_box.subsurface(pygame.rect.Rect(0, 0, 5 * self.unitsizex, int(((1.5+self.hero.get_item_inv_size()) * self.unitsizey) * (self.query_box_ticks / self.query_box_drawspeedticks)))), (5 * self.unitsizex, 2 * self.unitsizey))
                                self.query_box.fill(pygame.Color(0, 0, 0))
                                pygame.draw.rect(self.query_box, self.menu_color, (self.unitsizex/8, self.unitsizey/8, self.query_box.get_width()-self.unitsizex/4, self.query_box.get_height()-self.unitsizey/4-self.unitsizex/16), self.unitsizex/8)
                                for i,item in enumerate(self.hero.draw_items):
                                    if len(item) > 8:
                                        itemtexts = item.split(" ")
                                        if self.hero.draw_items[item] > 1:
                                            self.query_box.blit(self.gamefont.render(itemtexts[0] + (8-len(itemtexts[0]))*" " + str(self.hero.draw_items[item]), True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                            self.query_box.blit(self.gamefont.render(" " + itemtexts[1], True, self.menu_color), (1 * self.unitsizex, (1.5+i) * self.unitsizey))
                                        else:
                                            if len(itemtexts) > 2:
                                                if len(itemtexts[0]) + len(itemtexts[1]) > 8:
                                                    self.query_box.blit(self.gamefont.render(itemtexts[0], True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                                    self.query_box.blit(self.gamefont.render(" " + " ".join(itemtexts[1:]), True, self.menu_color), (1 * self.unitsizex, (1.5+i) * self.unitsizey))
                                                else:
                                                    self.query_box.blit(self.gamefont.render(" ".join(itemtexts[:2]), True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                                    self.query_box.blit(self.gamefont.render(" " + " ".join(itemtexts[2:]), True, self.menu_color), (1 * self.unitsizex, (1.5+i) * self.unitsizey))
                                            else:
                                                self.query_box.blit(self.gamefont.render(itemtexts[0], True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                                self.query_box.blit(self.gamefont.render(" " + " ".join(itemtexts[1:]), True, self.menu_color), (1 * self.unitsizex, (1.5+i) * self.unitsizey))
                                    else:
                                        if self.hero.draw_items[item] > 1:
                                            self.query_box.blit(self.gamefont.render(item + (8-len(item))*" " + str(self.hero.draw_items[item]), True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                        else:
                                            self.query_box.blit(self.gamefont.render(item, True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                if len(self.hero.draw_items) > 0:
                                    adder = 1
                                else:
                                    adder = 0
                                for j,item in enumerate(self.hero.undraw_items):
                                    if len(item) > 8:
                                        itemtexts = item.split(" ")
                                        if len(itemtexts) > 2:
                                            if len(itemtexts[0]) + len(itemtexts[1]) > 8:
                                                self.query_box.blit(self.gamefont.render(itemtexts[0], True, self.menu_color), (1 * self.unitsizex, (1+i+j+adder) * self.unitsizey))
                                                self.query_box.blit(self.gamefont.render(" " + " ".join(itemtexts[1:]), True, self.menu_color), (1 * self.unitsizex, (1.5+i+j+adder) * self.unitsizey))
                                            else:
                                                self.query_box.blit(self.gamefont.render(" ".join(itemtexts[:2]), True, self.menu_color), (1 * self.unitsizex, (1+i+j+adder) * self.unitsizey))
                                                self.query_box.blit(self.gamefont.render(" " + " ".join(itemtexts[2:]), True, self.menu_color), (1 * self.unitsizex, (1.5+i+j+adder) * self.unitsizey))
                                        else:
                                            self.query_box.blit(self.gamefont.render(itemtexts[0], True, self.menu_color), (1 * self.unitsizex, (1+i+j+adder) * self.unitsizey))
                                            self.query_box.blit(self.gamefont.render(" " + " ".join(itemtexts[1:]), True, self.menu_color), (1 * self.unitsizex, (1.5+i+j+adder) * self.unitsizey))
                                    else:
                                        self.query_box.blit(self.gamefont.render(item, True, self.menu_color), (1 * self.unitsizex, (1+i+j+adder) * self.unitsizey))

                                if self.walking_command_selector_visible:
                                    self.query_box.blit(
                                        pygame.transform.scale(self.command_selector, (self.unitsizex, self.unitsizey)),
                                        pygame.rect.Rect(0 * self.unitsizex,
                                                         (1+self.shop_selection) * self.unitsizey,
                                                         self.unitsizex, self.unitsizey))

                            if self.hero.mode == "Inn":
                                self.query_box_ticks += self.delta_ticks
                                if self.query_box_ticks > self.query_box_drawspeedticks:
                                    self.query_box_ticks = self.query_box_drawspeedticks

                                self.screen.blit(self.query_box.subsurface(pygame.rect.Rect(0, 0, self.hero.walking_talk_box_message.query.width * self.unitsizex,int(self.hero.walking_talk_box_message.query.height * self.unitsizey * (self.query_box_ticks / self.query_box_drawspeedticks)))), (5 * self.unitsizex, 2 * self.unitsizey))
                                self.query_box.fill(pygame.Color(0, 0, 0))
                                pygame.draw.rect(self.query_box, self.menu_color, (self.unitsizex/8, self.unitsizey/8, self.query_box.get_width()-self.unitsizex/4, self.query_box.get_height()-self.unitsizey/4-self.unitsizex/16), self.unitsizex/8)
                                for i,option in enumerate(self.hero.walking_talk_box_message.query.options):
                                    self.query_box.blit(self.gamefont.render(option, True, self.menu_color), (1 * self.unitsizex, (1+i) * self.unitsizey))
                                if self.walking_command_selector_visible:
                                    self.query_box.blit(
                                        pygame.transform.scale(self.command_selector, (self.unitsizex, self.unitsizey)),
                                        pygame.rect.Rect(0 * self.unitsizex,
                                                         (1+self.shop_selection) * self.unitsizey,
                                                         self.unitsizex, self.unitsizey))

                        # draw spell box
                        if self.hero.mode == "Spell":
                            SpellWindowDrawer.draw(self)

                        # draw status box
                        if self.hero.mode == "Status":
                            StatusWindowDrawer.draw(self)

                        # draw item box
                        if self.hero.display_item_window:
                            ItemWindowDrawer.draw(self)

                    if self.hero.eviction and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 650.0:
                                self.hero.eviction = False
                                self.hero.mode = "Transitioning"
                                self.hero.mx = self.hero.map.outsidex
                                self.hero.my = self.hero.map.outsidey
                                self.hero.moffsetx = - self.hero.mx + NUM_CELLS_WIDE / 2
                                self.hero.moffsety = - self.hero.my + NUM_CELLS_HIGH / 2
                                self.hero.teleport_pack = ("World", self.hero.sizex, self.hero.sizey)
                                self.hero.map_transition = True
                                self.hero.flag_moving = False
                                self.hero.flag_left = False
                                self.hero.flag_right = False
                                self.hero.flag_up = False
                                self.hero.flag_down = False
                                self.hero.screenfade = "out"
                                self.hero.screenfadeticks = 0
                                self.hero.display_item_window = False
                                self.hero.walking_talk_box_visible = False
                                self.hero.walking_talk_box_message = TextNode("")
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=True)
                                self.item_box.reset()

                    if self.hero.do_rainbow_bridge and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 350.0:
                                self.hero.mode = "Walking"
                                self.hero.walking_talk_box_visible = False
                                self.hero.walking_talk_box_message = ""
                                self.walking_talk_box_ticks = 0
                                self.side_box.reset()
                                self.command_box.reset()
                                self.walking_talk_box_msg_ticks = 0
                                self.hero.do_rainbow_bridge = False
                                self.hero.rainbow_blinks = 0
                                self.hero.rainbow_blink_on = True

                    if self.hero.rainbow_blink_on and self.hero.rainbow_blinks < 52:
                        self.hero.delayticks += self.delta_ticks
                        if self.hero.delayticks > 75.0:
                            self.hero.delayticks = 0
                            self.hero.rainbowcolorindex += 1
                            self.hero.rainbow_blinks += 1
                            if self.hero.rainbowcolorindex > 12:
                                self.hero.rainbowcolorindex = 0
                    elif self.hero.rainbow_blink_on and self.hero.rainbow_blinks >= 52:
                        self.hero.rainbow_blink_on = False
                        self.hero.data["Rainbow Bridge"] = True

                    if self.hero.time_to_lure_enemies and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 350.0:
                                enemies = ["Red Slime", "Red Slime", "Drakee", "Ghost", "Magician", "Scorpion"]
                                self.hero.time_to_lure_enemies = False
                                self.hero.walking_talk_box_visible = True
                                enemy = random.choice(enemies)
                                self.hero.walking_talk_box_message = TextNode("A " + enemy + " draws near! \nCommand?", quoted=False)
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=True)
                                self.hero.flag_moving = False
                                self.hero.flag_left = False
                                self.hero.flag_right = False
                                self.hero.flag_up = False
                                self.hero.flag_down = False
                                self.hero.battle_mode = True
                                self.hero.ready_to_end_battle = False
                                self.hero.enemy_is_dead = False
                                self.hero.enemy = Enemy(enemy)
                                self.hero.enemy_spiral_flag = True
                                self.hero.enemy_spiral_index = 0
                                self.hero.enemy_spiral_ticks = 0
                                self.hero.mode = "Menu"

                    if self.hero.time_to_warp_home and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 350.0:
                                self.hero.time_to_warp_home = False
                                playSound(27)
                                self.hero.mode = "Transitioning"
                                self.hero.mx = 44
                                self.hero.my = 45
                                self.hero.moffsetx = - self.hero.mx + NUM_CELLS_WIDE / 2
                                self.hero.moffsety = - self.hero.my + NUM_CELLS_HIGH / 2
                                self.hero.teleport_pack = ("World", self.hero.sizex, self.hero.sizey)
                                self.hero.map_transition = True
                                self.hero.flag_moving = False
                                self.hero.flag_left = False
                                self.hero.flag_right = False
                                self.hero.flag_up = False
                                self.hero.flag_down = False
                                self.hero.screenfade = "out"
                                self.hero.screenfadeticks = 0
                                #self.hero.items.remove(item)
                                self.hero.display_item_window = False
                                self.hero.walking_talk_box_visible = False
                                self.hero.walking_talk_box_message = TextNode("")
                                self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=True)
                                self.item_box.reset()

                    if self.hero.heroattack and self.donetalkingitsokaytoacceptinput and self.goforit():
                        self.hero.delayticks += self.delta_ticks
                        if self.hero.delayticks > self.hero.delaytickspeed:
                            self.hero.delayticks = 0
                            self.hero.heroattack = False
                            #formula of damage the hero does on the enemy
                            if int((self.hero.get_attack_power() - self.hero.enemy.agility/2)/4) < 0:
                                a = 0
                            else:
                                a = int((self.hero.get_attack_power() - self.hero.enemy.agility/2)/4)
                            if int((self.hero.get_attack_power() - self.hero.enemy.agility/2)/2) < 0:
                                b = 0
                            else:
                                b = int((self.hero.get_attack_power() - self.hero.enemy.agility / 2) / 2)
                            dmg = random.randint(a, b)
                            if dmg < 1:
                                if random.random() < 0.50:
                                    dmg = 1
                                else:
                                    dmg = 0

                            #chance for excellent move
                            luckyhit = False
                            if random.random() < (1/32.0):
                                luckyhit = True
                                dmg = random.randint(int(self.hero.get_attack_power()/2),int(self.hero.get_attack_power()))

                            if luckyhit:
                                luckyhitbit = "Excellent move! \n"
                            else:
                                luckyhitbit = ""

                            dodging = False
                            if random.random() < self.hero.enemy.dodge:
                                dodging = True

                            miss = True if dmg == 0 else False
                            if miss:
                                missbit = "A miss! No damage hath been scored!"

                            if dodging:
                                self.hero.add_to_message_render(TextNode(luckyhitbit + "It is dodging!", quoted=False), replace=False)
                                self.hero.miss_enemy_sound = True
                                self.hero.chose_a_turn = True
                            else:
                                if miss:
                                    self.hero.enemy_zero_dmg_sound = True
                                    self.hero.add_to_message_render(TextNode(luckyhitbit + missbit, quoted=False), replace=False)
                                    self.hero.chose_a_turn = True
                                else:
                                    self.hero.enemy.HP -= dmg
                                    if luckyhit:
                                        self.hero.excellent_hit_sound = True
                                    else:
                                        self.hero.attack_enemy_sound = True
                                    self.hero.add_to_message_render(TextNode(luckyhitbit + "The " + self.hero.enemy.name + "'s Hit Points have been reduced by " + str(dmg) + ".", quoted=False), replace=False)
                                    self.hero.enemy_red_shadow = True
                                    self.hero.enemy_red_shadow_blinks = 0
                                    self.hero.enemy_red_shadow_ticks = 0



                    elif self.hero.chose_a_turn and self.donetalkingitsokaytoacceptinput and self.goforit():
                        self.hero.delayticks += self.delta_ticks
                        if self.hero.delayticks > self.hero.delaytickspeed:
                            self.hero.delayticks = 0
                            self.hero.chose_a_turn = False
                            if self.hero.enemy.HP <= 0:
                                self.hero.kill_enemy()
                                self.hero.heroattack = False
                                self.hero.enemyattack = False
                                self.hero.chose_a_turn = False
                                self.hero.lost_initiative = False
                                self.hero.enemy_turn = False
                                self.hero.convert_initiative = False
                                self.hero.enemy_red_shadow = False
                                self.hero.screen_shake_flag = False
                            else:
                                if self.hero.convert_initiative:
                                    self.hero.enemyattack = False
                                    self.hero.convert_initiative = False
                                    self.hero.enemy_turn = True
                                    self.hero.chose_a_turn = False
                                else:
                                    if self.hero.enemy.asleep:
                                        self.hero.enemy.turns_asleep += 1
                                        if self.hero.enemy.turns_asleep > 1:
                                            if random.random() < (1/3.0):
                                                self.hero.enemy.asleep = False
                                                self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " hath woken up.", quoted=False))
                                                self.hero.enemy.turns_asleep = 0
                                            else:
                                                self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " is asleep.", quoted=False))
                                        else:
                                            self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " is asleep.", quoted=False))
                                    if not self.hero.enemy.asleep:
                                        if self.hero.strength >= self.hero.enemy.strength*2 and random.random() < 0.25:
                                            #enemy runs away
                                            self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " is running away.", quoted=False))
                                            self.hero.battle_running = True
                                        else:
                                            for action in self.hero.enemy.pattern:
                                                validaction = True
                                                if len(action) > 2:
                                                    if action[2] == "HP<25%" and self.hero.enemy.HP/float(self.hero.enemy.maxhp) >= 0.25:
                                                        validaction = False
                                                    elif action[2] == "RequireAwake" and self.hero.asleep:
                                                        validaction = False
                                                    elif action[2] == "RequireSpell" and self.hero.spell_stopped:
                                                        validaction = False
                                                if validaction and random.random() < action[1]:
                                                    self.hero.enemy.action = action[0]
                                                    break

                                            if self.hero.enemy.action == "Attack":
                                                self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " attacks!", quoted=False))
                                                self.hero.prepare_hit_me_sound = True
                                                self.hero.enemyattack = True
                                            elif self.hero.enemy.action == "HURT" or self.hero.enemy.action == "HEAL" or self.hero.enemy.action == "HURTMORE" or self.hero.enemy.action == "HEALMORE" or self.hero.enemy.action == "STOPSPELL" or self.hero.enemy.action == "SLEEP":
                                                self.hero.walking_talk_box_message = TextNode(self.hero.enemy.name + " chants the spell of " + self.hero.enemy.action + ".", quoted=False)
                                                self.hero.add_to_message_render(self.hero.walking_talk_box_message)
                                                self.hero.enemyspell = True
                                                self.hero.spell_lag = True
                                                self.hero.spell_lag_tickspeed = 150.0
                                                self.hero.spell_blinks = 0
                                                self.hero.spell_cast = True
                                                self.hero.spell_blink_ticks = 0
                                                self.donetalkingitsokaytoacceptinput = False #this prevents the immediate spell blink cuz of the code-order
                                            elif self.hero.enemy.action == "FireBreath" or self.hero.enemy.action == "StrongFireBreath":
                                                self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " is breathing fire.", quoted=False))
                                                self.hero.enemyattack = True
                                    else:
                                        self.hero.enemyattack = True



                    elif self.hero.enemyattack and self.donetalkingitsokaytoacceptinput and self.goforit():
                        self.hero.delayticks += self.delta_ticks
                        if self.hero.delayticks > 3*self.hero.delaytickspeed:
                            self.hero.delayticks = 0
                            self.hero.enemyattack = False

                            if not self.hero.enemy.asleep:
                                dmg = None #init

                                if self.hero.enemy.action == "Attack":
                                    if self.hero.get_defense_power() >= self.hero.enemy.strength:
                                        dmg = random.randint(0, int((self.hero.enemy.strength+4)/6))
                                    else:
                                        dmg = random.randint(int((self.hero.enemy.strength - self.hero.get_defense_power()/2)/4), int((self.hero.enemy.strength - self.hero.get_defense_power()/2)/2))

                                elif self.hero.enemy.action == "HURT":
                                    if not self.hero.enemy.spell_stopped:
                                        if self.hero.armor and self.hero.armor.name == "Magic Armor" or self.hero.armor and self.hero.armor.name == "Erdrick's Armor":
                                            dmg = random.randint(2, 6)
                                        else:
                                            dmg = random.randint(3, 10)
                                    else:
                                        self.hero.add_to_message_render(TextNode("But that spell hath been blocked.", quoted=False))
                                        self.hero.enemy_turn = True

                                elif self.hero.enemy.action == "HURTMORE":
                                    if not self.hero.enemy.spell_stopped:
                                        if self.hero.armor and self.hero.armor.name == "Magic Armor" or self.hero.armor and self.hero.armor.name == "Erdrick's Armor":
                                            dmg = random.randint(20, 30)
                                        else:
                                            dmg = random.randint(30, 45)
                                    else:
                                        self.hero.add_to_message_render(TextNode("But that spell hath been blocked.", quoted=False))
                                        self.hero.enemy_turn = True

                                elif self.hero.enemy.action == "SLEEP":
                                    if not self.hero.enemy.spell_stopped:
                                        self.hero.asleep = True
                                        self.hero.turns_asleep = 0
                                        self.hero.add_to_message_render(TextNode("Thou art asleep.", quoted=False))
                                        self.hero.enemy_turn = True
                                    else:
                                        self.hero.add_to_message_render(TextNode("But that spell hath been blocked.", quoted=False))
                                        self.hero.enemy_turn = True

                                elif self.hero.enemy.action == "STOPSPELL":
                                    if not self.hero.enemy.spell_stopped:
                                        didntwork = True
                                        if self.hero.armor and self.hero.armor.name == "Erdrick's Armor":
                                            didntwork = True
                                        elif random.random() < 0.50:
                                            didntwork = False
                                        if not didntwork:
                                            self.hero.spell_stopped = True
                                            self.hero.add_to_message_render(TextNode("$hero_name$'s spell is blocked.", quoted=False))
                                        else:
                                            self.hero.add_to_message_render(TextNode("The spell will not work.", quoted=False))
                                        self.hero.enemy_turn = True
                                    else:
                                        self.hero.add_to_message_render(TextNode("But that spell hath been blocked.", quoted=False))
                                        self.hero.enemy_turn = True

                                elif self.hero.enemy.action == "HEAL":
                                    if not self.hero.enemy.spell_stopped:
                                        self.hero.enemy.HP += random.randint(20, 27)
                                        if self.hero.enemy.HP > self.hero.enemy.maxhp:
                                            self.hero.enemy.HP = self.hero.enemy.maxhp
                                        self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " hath recovered.", quoted=False))
                                        self.hero.enemy_turn = True
                                    else:
                                        self.hero.add_to_message_render(TextNode("But that spell hath been blocked.", quoted=False))
                                        self.hero.enemy_turn = True


                                elif self.hero.enemy.action == "HEALMORE":
                                    if not self.hero.enemy.spell_stopped:
                                        self.hero.enemy.HP += random.randint(85, 100)
                                        if self.hero.enemy.HP > self.hero.enemy.maxhp:
                                            self.hero.enemy.HP = self.hero.enemy.maxhp
                                        self.hero.add_to_message_render(TextNode("The " + self.hero.enemy.name + " hath recovered.", quoted=False))
                                        self.hero.enemy_turn = True
                                    else:
                                        self.hero.add_to_message_render(TextNode("But that spell hath been blocked.", quoted=False))
                                        self.hero.enemy_turn = True

                                elif self.hero.enemy.action == "FireBreath":
                                    if self.hero.armor and self.hero.armor.name == "Erdrick's Armor":
                                        dmg = random.randint(10, 14)
                                    else:
                                        dmg = random.randint(16, 23)

                                elif self.hero.enemy.action == "StrongFireBreath":
                                    if self.hero.armor and self.hero.armor.name == "Erdrick's Armor":
                                        dmg = random.randint(42, 48)
                                    else:
                                        dmg = random.randint(65, 72)


                                if dmg == 0:
                                    self.hero.add_to_message_render(TextNode("A miss! No damage hath been scored!", quoted=False))
                                    self.hero.enemy_turn = True
                                elif dmg > 0:
                                    self.hero.HP -= dmg
                                    self.hero.enemy_hit_me_sound = True
                                    self.hero.add_to_message_render(TextNode("Thy Hit Points decreased by " + str(dmg) + ".", quoted=False))
                                    self.hero.screen_shake_flag = True
                                    self.hero.screen_shake_index = 0
                                    self.hero.scren_shake_ticks = 0
                                    if self.hero.HP <= 0:
                                        self.hero.lost_initiative = False
                                        self.hero.convert_initiative = False
                                        self.hero.delayticks = 0
                                        self.hero.HP = 0
                                        self.hero.enemy_turn = False
                                        self.hero.youdied = True
                                        self.hero.mode = "Talking"
                                        self.hero.barrier_blinks = 0  # hijack barrier variables to implement the death blink effect
                                        self.hero.barrier_flash = True
                                        self.hero.barrier_flash_ticks = 0
                                    else:
                                        self.hero.enemy_turn = True
                            else:
                                self.hero.enemy_turn = True

                            if self.hero.lost_initiative:
                                if not self.hero.asleep:
                                    self.hero.lost_initiative = False
                                    self.hero.convert_initiative = True
                                    self.hero.enemy_turn = False
                                    if self.hero.action == "FIGHT":
                                        self.hero.action = None
                                        self.hero.heroattack = True
                                        self.hero.update_sleep()
                                        self.hero.add_to_message_render(TextNode("$hero_name$ attacks!", quoted=False))
                                        self.hero.prepare_attack_enemy_sound = True
                                        self.hero.chose_a_turn = True
                                    elif self.hero.action == "SPELL":
                                        self.hero.cast_spell(self.hero.spell_chanted)
                                    elif self.hero.action == "ITEM":
                                        self.hero.update_draw_items()
                                        self.hero.use_item(self.hero.item_used)
                                        self.hero.chose_a_turn = True


                    elif self.hero.enemy_turn and self.donetalkingitsokaytoacceptinput and self.goforit() and not self.hero.spell_cast:
                        self.hero.delayticks += self.delta_ticks
                        if self.hero.delayticks > 4*self.hero.delaytickspeed:
                                self.hero.delayticks = 0
                                self.hero.enemy_turn = False
                                self.hero.update_sleep()
                                if not self.hero.asleep:
                                    self.hero.add_to_message_render(TextNode("Command?", quoted=False))
                                    self.battle_command_selector_x = 0
                                    self.battle_command_selector_y = 0
                                    self.hero.mode = "Menu"
                                else:
                                    self.hero.chose_a_turn = True

                    # spell blinkies
                    if self.hero.spell_cast and self.donetalkingitsokaytoacceptinput and self.goforit():
                        if self.hero.spell_sound:
                            self.hero.spell_sound = False
                            playSound(42)
                        if self.hero.blink_on:
                            if self.hero.spell_blinks < 8:
                                # draw white flash
                                self.screen.blit(self.white_flash, (0, 0))
                                self.hero.spell_blink_ticks += self.delta_ticks
                                if self.hero.spell_blink_ticks >= self.hero.spell_blink_tickspeed:
                                    self.hero.spell_blink_ticks = 0
                                    self.hero.blink_on = False
                                    self.hero.spell_blinks += 1
                            else:
                                self.hero.spell_lag_ticks += self.delta_ticks
                                if self.hero.spell_lag_ticks > self.hero.spell_lag_tickspeed:
                                    self.hero.spell_lag = False
                                    self.hero.spell_lag_ticks = 0
                                    self.hero.spell_cast = False
                                    if self.hero.enemyspell:
                                        self.hero.enemyspell = False
                                        self.hero.enemyattack = True
                                    elif self.hero.spell_chanted:
                                        self.hero.execute_spell_effect()
                                    self.hero.npc_special_action = None
                                    self.hero.blink_on = False
                                    self.hero.spell_blink_ticks = 0
                        else:
                            self.hero.spell_blink_ticks += self.delta_ticks
                            if self.hero.spell_blink_ticks >= self.hero.spell_blink_tickoffspeed:
                                self.hero.blink_on = True
                                self.hero.spell_blink_ticks = 0

                    #swamp blinkies
                    if self.hero.swamp_flash and not self.hero.motion_in_progress:
                        if self.hero.blink_on:
                            if self.hero.swamp_blinks < 1:
                                # draw red flash
                                self.screen.blit(self.red_flash, (0, 0))
                                self.hero.swamp_flash_ticks += self.delta_ticks
                                if self.hero.swamp_flash_ticks >= self.hero.swamp_flash_tickspeed:
                                    self.hero.swamp_flash_ticks = 0
                                    self.hero.blink_on = False
                                    self.hero.swamp_blinks += 1
                            else:
                                self.hero.swamp_flash = False

                        else:
                            self.hero.swamp_flash_ticks += self.delta_ticks
                            if self.hero.swamp_flash_ticks >= self.hero.swamp_flash_tickoffspeed:
                                self.hero.blink_on = True
                                self.hero.swamp_flash_ticks = 0

                    # barrier blinkies
                    if self.hero.barrier_flash and not self.hero.motion_in_progress:
                        if self.hero.blink_on:
                            if self.hero.barrier_blinks < 3:
                                # draw red flash
                                self.screen.blit(self.red_flash, (0, 0))
                                self.hero.barrier_flash_ticks += self.delta_ticks
                                if self.hero.barrier_flash_ticks >= self.hero.barrier_flash_tickspeed:
                                    self.hero.barrier_flash_ticks = 0
                                    self.hero.blink_on = False
                                    self.hero.barrier_blinks += 1
                            else:
                                self.hero.barrier_flash = False

                        else:
                            self.hero.barrier_flash_ticks += self.delta_ticks
                            if self.hero.barrier_flash_ticks >= self.hero.barrier_flash_tickoffspeed:
                                self.hero.blink_on = True
                                self.hero.barrier_flash_ticks = 0

                    # youdied blinkies
                    if self.hero.youdied:
                        if self.hero.blink_on:
                            if self.hero.barrier_blinks < 12:
                                # draw red flash
                                self.screen.blit(self.red_flash, (0, 0))
                                self.hero.barrier_flash_ticks += self.delta_ticks
                                if self.hero.barrier_flash_ticks >= self.hero.barrier_flash_tickspeed:
                                    self.hero.barrier_flash_ticks = 0
                                    self.hero.blink_on = False
                                    self.hero.barrier_blinks += 1
                            else:
                                self.hero.delayticks += self.delta_ticks
                                if self.hero.delayticks >= self.hero.delaytickspeed*12:
                                    self.hero.delayticks = 0
                                    self.hero.mode = "Talking"
                                    if self.hero.battle_mode:
                                        self.hero.add_to_message_render(TextNode("Thou art dead.", quoted=False))
                                    else:
                                        self.hero.walking_talk_box_visible = True
                                        self.hero.walking_talk_box_message = TextNode("Thou art dead.", quoted=False)
                                        self.hero.add_to_message_render(self.hero.walking_talk_box_message, replace=True)
                                    #teleport to king lorik on button press
                                    self.hero.youdied = False
                                    self.hero.teleport_via_death = True
                        else:
                            self.hero.barrier_flash_ticks += self.delta_ticks
                            if self.hero.barrier_flash_ticks >= self.hero.barrier_flash_tickoffspeed:
                                self.hero.blink_on = True
                                self.hero.barrier_flash_ticks = 0

                    if self.hero.lag_motion and not self.hero.swamp_flash and not self.hero.barrier_flash:
                        self.hero.lag_motion_ticks += self.delta_ticks
                        if self.hero.lag_motion_ticks > self.hero.lag_motion_tickspeed:
                            self.hero.lag_motion = False
                            self.hero.lag_motion_ticks = 0


                    #enemy red shadow on taking damage
                    if self.hero.enemy_red_shadow:
                        if self.hero.enemy_red_shadow_blink_on:
                            if self.hero.enemy_red_shadow_blinks < 8:
                                #draw red shadow
                                whatenemydraw = pygame.transform.scale(self.hero.enemy.red_shadow, (int((self.unitsizex/16.0)*self.hero.enemy.image.get_width()), int((self.unitsizey/16.0)*self.hero.enemy.image.get_height())))
                                if dl:
                                    self.battle_box.blit(whatenemydraw, (int((self.battle_box.get_width()-whatenemydraw.get_width())/2), int(0.05*(self.battle_box.get_height()-whatenemydraw.get_height()))))
                                else:
                                    self.battle_box.blit(whatenemydraw, (int((self.battle_box.get_width()-whatenemydraw.get_width())/2), int((self.battle_box.get_height()-whatenemydraw.get_height())/2)))
                                self.hero.enemy_red_shadow_ticks += self.delta_ticks
                                if self.hero.enemy_red_shadow_ticks >= self.hero.enemy_red_shadow_tickspeed:
                                    self.hero.enemy_red_shadow_ticks = 0
                                    self.hero.enemy_red_shadow_blink_on = False
                            else:
                                self.hero.enemy_red_shadow = False
                                self.hero.chose_a_turn = True

                        else:
                            self.hero.enemy_red_shadow_ticks += self.delta_ticks
                            if self.hero.enemy_red_shadow_ticks >= self.hero.enemy_red_shadow_tickspeed:
                                self.hero.enemy_red_shadow_ticks = 0
                                self.hero.enemy_red_shadow_blink_on = True
                                self.hero.enemy_red_shadow_blinks += 1

                    if self.hero.screen_shake_flag:
                        if self.hero.screen_shake_on:
                            if self.hero.screen_shake_index < len(self.hero.screen_shake):
                                #set screen shake shift
                                self.screen_shake_shift_x = self.hero.screen_shake[self.hero.screen_shake_index][0]
                                self.screen_shake_shift_y = self.hero.screen_shake[self.hero.screen_shake_index][1]
                                self.hero.screen_shake_ticks += self.delta_ticks
                                if self.hero.screen_shake_ticks >= self.hero.screen_shake_tickspeed:
                                    self.hero.screen_shake_ticks = 0
                                    self.hero.screen_shake_on = False
                            else:
                                self.hero.screen_shake_flag = False

                        else:
                            self.hero.screen_shake_ticks += self.delta_ticks
                            if self.hero.screen_shake_ticks >= self.hero.screen_shake_tickspeed:
                                self.hero.screen_shake_ticks = 0
                                self.hero.screen_shake_on = True
                                self.hero.screen_shake_index += 1

                    if self.hero.enemy_spiral_flag:
                        self.hero.enemy_spiral_ticks += self.delta_ticks
                        if self.hero.enemy_spiral_ticks >= self.hero.enemy_spiral_tickspeed:
                            self.hero.enemy_spiral_ticks = 0
                            self.hero.enemy_spiral_index += 1
                        if self.hero.enemy_spiral_index > 47:
                            self.hero.enemy_spiral_flag = False
                            self.hero.enemy_is_dead = False #toggles appearance of enemy

                    if self.hero.fight_the_dragonlord and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 550.0:
                                self.hero.mode = "Walking"
                                self.hero.walking_talk_box_visible = False
                                self.hero.walking_talk_box_message = ""
                                self.walking_talk_box_ticks = 0
                                self.side_box.reset()
                                self.command_box.reset()
                                self.walking_talk_box_msg_ticks = 0
                                self.hero.delayticks = 0
                                self.hero.fight_dragonlord()
                    elif self.hero.fight_the_true_dragonlord and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 550.0:
                                self.hero.mode = "Walking"
                                self.hero.walking_talk_box_visible = False
                                self.hero.walking_talk_box_message = ""
                                self.walking_talk_box_ticks = 0
                                self.side_box.reset()
                                self.command_box.reset()
                                self.walking_talk_box_msg_ticks = 0
                                self.hero.delayticks = 0
                                self.hero.fight_true_dragonlord()
                    elif self.hero.join_the_dragonlord and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 550.0:
                                self.menu_color = (255,0,0)
                                self.hero.face = 0
                                self.hero.map.NPCs[0].face = 0
                    elif self.hero.dragonlord_is_dead and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:
                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 550.0:
                                self.hero.dragonlord_is_dead = False
                                self.hero.ready_to_win_game = True
                                self.hero.mode = "Transitioning"
                                self.hero.mx = 50
                                self.hero.my = 50
                                self.hero.moffsetx = - self.hero.mx + NUM_CELLS_WIDE / 2
                                self.hero.moffsety = - self.hero.my + NUM_CELLS_HIGH / 2
                                self.hero.teleport_pack = ("World", self.hero.sizex, self.hero.sizey)
                                self.hero.map_transition = True
                                self.hero.flag_moving = False
                                self.hero.flag_left = False
                                self.hero.flag_right = False
                                self.hero.flag_up = False
                                self.hero.flag_down = False
                                self.hero.screenfade = "out"
                                self.hero.screenfadeticks = 0
                                self.hero.enemy = Enemy("Red Slime") #default to satisfy some checks
                                self.hero.battle_mode = False
                                self.hero.walking_talk_box_message = ""

                    if self.hero.ready_for_ending_credits and self.donetalkingitsokaytoacceptinput:
                        goforit = False
                        if self.hero.walking_talk_box_message and not self.hero.walking_talk_box_message.next:
                            goforit = True
                        elif self.hero.walking_talk_box_message == "":
                            goforit = True
                        if goforit:

                            self.hero.delayticks += self.delta_ticks
                            if self.hero.delayticks > 5250.0:
                                self.hero.ready_for_ending_credits = False
                                self.hero.do_ending_credits = True

                    if self.hero.faerie_flute_blown and self.donetalkingitsokaytoacceptinput and self.goforit():
                        if self.hero.faerie_flute_sound:
                            self.hero.faerie_flute_sound = False
                            pauseMusic()
                            playSound(17)
                        self.hero.faerie_flute_ticks += self.delta_ticks
                        if self.hero.faerie_flute_ticks > 6000:
                            self.hero.faerie_flute_blown = False
                            changeBGMusic(self.hero.music_id)
                            if self.hero.battle_mode:
                                self.hero.chose_a_turn = True
                            self.hero.add_to_message_render(self.hero.next_msg, replace=False)

                    if self.hero.kill_enemy_sound and self.donetalkingitsokaytoacceptinput:
                        self.hero.kill_enemy_ticks += self.delta_ticks
                        if self.hero.kill_enemy_ticks > 2000:
                            self.hero.kill_enemy_ticks = 0
                            self.hero.kill_enemy_sound = False
                            changeBGMusic(self.hero.music_id)

                    if self.hero.attack_enemy_sound and self.donetalkingitsokaytoacceptinput:
                        self.hero.attack_enemy_sound = False
                        playSound(33)
                    if self.hero.miss_enemy_sound and self.donetalkingitsokaytoacceptinput:
                        self.hero.miss_enemy_sound = False
                        playSound(39)
                    if self.hero.enemy_zero_dmg_sound and self.donetalkingitsokaytoacceptinput:
                        self.hero.enemy_zero_dmg_sound = False
                        playSound(40)
                    if self.hero.excellent_hit_sound and self.donetalkingitsokaytoacceptinput:
                        self.hero.excellent_hit_sound = False
                        playSound(34)
                    if self.hero.enemy_hit_me_sound and self.donetalkingitsokaytoacceptinput:
                        self.hero.enemy_hit_me_sound = False
                        playSound(36)
                    if self.hero.prepare_hit_me_sound:
                        self.hero.prepare_hit_me_sound = False
                        playSound(35)
                    if self.hero.prepare_attack_enemy_sound:
                        self.hero.prepare_attack_enemy_sound = False
                        playSound(38)
                    if self.hero.level_up_sound and self.donetalkingitsokaytoacceptinput:
                        self.hero.level_up_sound = False
                        playSound(25)

                pygame.display.flip()

                continue


class Hero(pygame.sprite.Sprite):
    def __init__(self, sizex, sizey):

        self.spell_sound = False
        self.faerie_flute_blown = False
        self.faerie_flute_ticks = 0
        self.faerie_flute_sound = False
        self.silver_harp_playing = False
        self.silver_harp_ticks = 0
        self.silver_harp_sound = False
        self.kill_enemy_sound = False
        self.kill_enemy_ticks = 0
        self.attack_enemy_sound = False
        self.miss_enemy_sound = False
        self.enemy_zero_dmg_sound = False
        self.excellent_hit_sound = False
        self.enemy_hit_me_sound = False
        self.prepare_attack_enemy_sound = False
        self.prepare_hit_me_sound = False
        self.level_up_sound = False
        self.next_msg = None

        self.is_dead = False
        self.lost_initiative = False
        self.convert_initiative = False
        self.action = None
        self.music_id = 0
        self.steps = 2
        self.mode = "Walking"
        self.sprite_identity = "Plain"
        self.spritesheets = [
            pygame.image.load("spritesheets/hero.png").convert(),
            pygame.image.load("spritesheets/hero_shield.png").convert(),
            pygame.image.load("spritesheets/hero_sword.png").convert(),
            pygame.image.load("spritesheets/hero_swordshield.png").convert(),
            pygame.image.load("spritesheets/hero_princess.png").convert()
        ]
        self.spritesheet = pygame.image.load("spritesheets/hero.png").convert()
        self.step = 0
        self.face = 2  #0=down 1=left 2=up 3=right
        self.x = 55
        self.y = 5
        self.items = []
        self.data = {}  # track data such as chests which have been looted
        self.spells = []

        self.targetx = None
        self.targety = None
        self.sizex = sizex
        self.sizey = sizey
        self.map = Map.load_map("Tantegel", sizex, sizey)
        self.flag_moving = False
        self.motion_in_progress = False
        self.flag_left = False
        self.flag_right = False
        self.flag_up = False
        self.flag_down = False
        self.step_ticks = 0
        self.map_transition = False
        self.map_transition_with_sleep = False
        self.map_transition_ticks = 0
        self.idlemapticks = 300.0
        self.walking_talk_box_visible = False
        self.screenfade = None # or "in"  # or "out"
        self.screenfadeticks = 0
        self.screenfadetickspeed = 250.0
        self.betweenfadeticks = 0
        self.betweenfadetickspeed = 700.0
        self.npc_special_action = None
        self.npc_name = "DNI"
        self.texttype = "Normal"


        self.walking_talk_box_message = None

        self.display_item_window = False
        self.new_bg_tile = None

        self.time_to_warp_home = False
        self.time_to_lure_enemies = False

        self.spell_cast = False
        self.spell_blink_ticks = 0
        self.spell_blink_tickspeed = 25.0
        self.spell_blink_tickoffspeed = 25.0
        self.spell_blinks = 0
        self.blink_on = True
        self.eviction = False

        self.swamp_flash = False
        self.swamp_flash_ticks = 0
        self.swamp_flash_tickspeed = 25.0
        self.swamp_flash_tickoffspeed = 25.0
        self.swamp_blinks = 0
        self.lag_motion = False
        self.lag_motion_ticks = 0
        self.lag_motion_tickspeed = 85.0
        self.spell_lag = False
        self.spell_lag_ticks = 0
        self.spell_lag_tickspeed = 650.0

        self.barrier_flash = False
        self.barrier_flash_ticks = 0
        self.barrier_flash_tickspeed = 25.0
        self.barrier_flash_tickoffspeed = 25.0
        self.barrier_blinks = 0

        #magic armor increases HP every 4th step
        self.magicarmorsteps = 0

        self.radiance_level = 0
        self.radiance_steps = 0
        self.torch = False
        self.repel_steps = 0
        self.repel = None

        self.walking_talk_box_msg_tick_next = False

        self.experience_table = [0, 7, 23, 47, 110, 220, 450, 800, 1300, 2000, 2900, 4000, 5500, 7500, 10000, 13000,
                                 16000, 19000, 22000, 26000, 30000, 34000, 38000, 42000, 46000, 50000, 54000, 58000,
                                 62000, 65535, 80000]


        str1 = [None, 1,    3,    3,  8,  12, 14, 18, 26, 31 ,36 ,44, 48, 56, 64 ,68 ,68 ,81 , 83 , 88 , 91 , 93 , 95 , 99 , 109 ,113 ,121 ,126 ,131 ,136]
        agi1 = [None, 0,    2,    4,  6,  6,  13, 16, 18, 27, 31 ,36 ,44 ,51 ,60 ,66 ,74 ,80 , 82 , 84 , 86 , 86 , 90 , 94 , 96  ,101 ,103 ,111 ,116 ,126]
        hp1  = [None, 7,    9 ,   16 ,20 ,23 ,25 ,31 ,35 ,39 ,47 ,48 ,55 ,61 ,71 ,77 ,85 ,100 ,115 ,123 ,134 ,143 ,150 ,155 ,159 ,165 ,174 ,180 ,185 ,195]
        mp1  = [None, None, None, 11, 15, 19, 21, 24 ,31 ,25 ,45, 53 ,59 ,65 ,67 ,90 ,65 ,103 ,110 ,123 ,130 ,141 ,148 ,156 ,156 ,163 ,170 ,175 ,185 ,195]
        str2 = [None, 1,    3,    3,  7,  11, 13, 16, 24, 28, 33, 40 ,43, 51 ,58, 61 ,61, 73,  75,  79,  82,  84,  86,  89,  98,  102, 109, 114, 118, 123]
        agi2 = [None, 0,    2,    4,  6,  6,  12, 15, 16, 24, 28, 33, 40, 46, 52, 60, 67, 70,  74,  76,  78,  78,  81,  85,  87,  91,  93,  100, 105, 114]
        hp2  = [None, 6,    8,    14, 18, 21, 23, 28, 32, 35, 42, 43, 50, 57, 64, 69, 77, 90,  104, 111, 121, 129, 135, 140, 143, 149, 157, 162, 167, 176]
        mp2  = [None, None, None, 10, 14, 17, 19, 22, 28, 32, 41, 48, 53, 59, 60, 81, 86, 93,  99,  111, 117, 127, 133, 140, 140, 148, 153, 158, 167, 176]
        self.strength_progression = [str1, str2]
        self.agility_progression = [agi1, agi2]
        self.maxhp_progression = [hp1, hp2]
        self.maxmp_progression = [mp1, mp2]

        self.spell_progression =    [None, None, "HEAL", "HURT", None, None, "SLEEP", None, "RADIANT", "STOPSPELL", None, "OUTSIDE", "RETURN", None, "REPEL", None, "HEALMORE", None, "HURTMORE", None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None]
        self.learned_new_spell = False

        self.enemy_spiral_flag = False
        self.enemy_spiral_index = 0
        self.enemy_spiral_ticks = 0
        self.enemy_spiral_tickspeed = 5.0
        self.enemy_spiral = [(3, 3),  # 1
                             (3, 4),  # 2
                             (2, 4),  # 3
                             (2, 3),  # 4
                             (2, 2),  # 5
                             (3, 2),  # 6
                             (4, 2),  # 7
                             (4, 3),  # 8
                             (4, 4),  # 9
                             (4, 4),  # 10
                             (3, 5),  # 11
                             (2, 5),  # 12
                             (1, 5),  # 13
                             (1, 4),  # 14
                             (1, 3),  # 15
                             (1, 2),  # 16
                             (1, 1),  # 17
                             (2, 1),  # 18
                             (3, 1),  # 19
                             (4, 1),  # 10
                             (5, 1),  # 21
                             (5, 2),  # 22
                             (5, 3),  # 23
                             (5, 4),  # 24
                             (5, 5),  # 25
                             (5, 6),  # 26
                             (4, 6),  # 27
                             (3, 6),  # 28
                             (2, 6),  # 29
                             (1, 6),  # 30
                             (0, 6),  # 31
                             (0, 5),  # 32
                             (0, 4),  # 33
                             (0, 3),  # 34
                             (0, 2),  # 35
                             (0, 1),  # 36
                             (0, 0),  # 37
                             (1, 0),  # 38
                             (2, 0),  # 39
                             (3, 0),  # 40
                             (4, 0),  # 41
                             (5, 0),  # 42
                             (6, 0),  # 43
                             (6, 1),  # 44
                             (6, 2),  # 45
                             (6, 3),  # 46
                             (6, 4),  # 47
                             (6, 5),  # 48
                             (6, 6),  # 49
                             ]

        self.npc = None
        self.ready_to_end_battle = False
        self.enemy_is_dead = True
        self.chose_a_turn = False
        self.enemy_turn = False
        self.battle_mode = False
        self.battle_report_mode = False
        self.battle_running = False
        self.enemyattack = False
        self.enemyspell = False
        self.heroattack = False
        self.enemy_red_shadow = False
        self.enemy_red_shadow_blink_on = False
        self.enemy_red_shadow_blinks = 0
        self.enemy_red_shadow_ticks = 0
        self.enemy_red_shadow_tickspeed = 50.0

        self.enemy = Enemy("Red Slime") #default to satisfy some constant checks

        self.delayticks = 0
        self.delaytickspeed = 125.0

        self.screen_shake = [(-2,0), (0,0), (0, 2), (0,0), (-2,0), (0,0), (0, 2), (0,0), (-2,0), (0,0), (0, 2), (0,0), (-2,0), (0,0), (0, 2), (0,0), ]
        self.screen_shake_index = 0
        self.screen_shake_flag = False
        self.screen_shake_on = False
        self.screen_shake_ticks = 0
        self.screen_shake_tickspeed = 5.0

        self.spell_stopped = False
        self.asleep = False

        self.youdied = False
        self.teleport_via_death = False
        self.justdied = False
        self.oktolorikafterdying = False

        self.fight_the_dragonlord = False
        self.fight_the_true_dragonlord = False
        self.join_the_dragonlord = False
        self.dragonlord_is_dead = False
        self.ready_to_win_game = False

        self.fighters_ring = False
        self.dragons_scale = False
        self.cursed_belt = False
        self.death_necklace = False

        self.do_rainbow_bridge = False
        self.rainbowcolorindex = 0
        self.rainbow_blink_on = False
        self.rainbow_blinks = 0

        self.spell_chanted = None

        self.ready_for_ending_credits = False
        self.do_ending_credits = False

        self.already_did_intro_chat = False

        #init map landing
        for npc in self.map.NPCs:
            self.map.mutex_data[(npc.x, npc.y)] = True
        self.map.mutex_data[(self.x, self.y)] = True


        """
        #init level - stats
        self.initialize_level()
        if self.level == 30:
            self.data["LV30"] = True

        self.update_sprite()
        """

        #testing
        #self.data["DLDEAD"] = True

        #self.data["BEGIN"] = True


        #self.load_game()

    def new_game(self):

        self.items = []  # [Item("Herb", 15, "Normal"), Item("Herb", 15, "Normal"), Item("Magic Key", 15, "Normal"), Item("Cursed Belt"), Item("Fighter's Ring"), Item("Erdrick's Token"), Item("Stones of Sunlight")]
        self.data = {}  # track data such as chests which have been looted
        self.spells = []  # Spell("HEAL", 4), Spell("HURT", 2), Spell("SLEEP", 2), Spell("RADIANT", 3), Spell("STOPSPELL", 2), Spell("OUTSIDE", 6), Spell("RETURN", 8), Spell("REPEL", 2), Spell("HEALMORE", 10), Spell("HURTMORE", 5)]
        self.level = 1
        self.monster_dictionary = {"Slime": (0, 0, 0, 0, 0,
                                             0)}  # enemy name: (num killed, total gold, total exp, num ran from, num died from, num the enemy ran from you
        self.G = 0
        self.E = 0
        self.weapon = None  # Item("Bamboo Pole", 10, "Weapon")
        self.armor = None  # Item("Clothes", 90, "Armor")
        self.shield = None  # Item("Silver Shield", 8400, "Shield")
        self.update_sprite()

    def initialize_level(self):
        self.strength = self.base_strength
        self.agility = self.base_agility
        self.maxhp = self.base_maxhp
        self.maxmp = self.base_maxmp
        self.HP = self.maxhp
        self.MP = self.maxmp
        newlv = self.level
        while (self.E >= self.experience_table[newlv]):
            newlv += 1
        newlv -= 1
        oldlv = 1
        if newlv > 1:
            if self.strength_progression[self.growth_str-1][newlv]:
                self.strength = self.base_strength + self.strength_progression[self.growth_str-1][newlv]
            if self.agility_progression[self.growth_agi-1][newlv]:
                self.agility = self.base_agility + self.agility_progression[self.growth_agi-1][newlv]
            if self.maxhp_progression[self.growth_maxhp-1][newlv]:
                self.maxhp = self.base_maxhp + self.maxhp_progression[self.growth_maxhp-1][newlv]
            if self.maxmp_progression[self.growth_maxmp-1][newlv]:
                if newlv >= 3:
                    self.maxmp = self.base_maxmp + self.maxmp_progression[self.growth_maxmp-1][newlv]
                else:
                    self.maxmp = 0
            for lv in range(oldlv + 1, newlv + 1):
                if self.spell_progression[lv]:
                    self.spells.append(Spell(self.spell_progression[lv]))
            self.level = newlv + 1
            if len(self.spells) > 0: self.learned_new_spell = True

        self.HP = self.maxhp
        if self.level >= 3:
            self.MP = self.maxmp
        else:
            self.MP = 0
            self.maxmp = 0

    def parse_message(self, message):
        return message.replace("$hero_name$", self.name).replace("$hero_next_level$", str(self.to_next_level()))

    def add_to_message_render(self, message, replace=False):
        if replace:
            if message.quoted:
                self.walking_talk_box_message_to_render = "`" + self.parse_message(message.text) + "'"
            else:
                self.walking_talk_box_message_to_render = self.parse_message(message.text)
        else:
            if message.quoted:
                self.walking_talk_box_message_to_render += " \n" + "`" + self.parse_message(message.text) + "'"
            else:
                self.walking_talk_box_message_to_render += " \n" + self.parse_message(message.text)

    def number_owned(self, item_name):
        return sum([1 for item in self.items if item.name == item_name])
    def update_draw_items(self):
        self.draw_items = {}
        self.undraw_items = []
        for i, item in enumerate(self.items):
            if item.name == 'Herb' or item.name == "Torch" or item.name == "Magic Key" or item.name == "Wings" or item.name == "Fairy Water":
                self.draw_items[item.name] = self.draw_items.get(item.name, 0) + 1
            else:
                self.undraw_items.append(item.name)
    def get_item_inv_size(self):
        self.update_draw_items()
        return len(self.draw_items) + len(self.undraw_items)
    def get_attack_power(self):
        return self.lookup_weapon_power() + self.lookup_item_power() + self.strength
    def get_defense_power(self):
        return self.lookup_armor_defense() + self.lookup_shield_defense() + self.lookup_item_defense() + self.agility/2

    def lookup_cost(self, item):
        if item == "Wings":
            return 35
        elif item == "Torch":
            return 4
        elif item == "Magic Key":
            return 26
        elif item == "Herb":
            return 12
        elif item == "Cursed Belt":
            return 180
        elif item == "Death Necklace":
            return 1200
        elif item == "Fairy Water":
            return 19
        elif item == "Fighter's Ring":
            return 15
        elif item == "Dragon's Scale":
            return 10

    def lookup_type(self, item):
        if item == "Staff of Rain" or item == "Stones of Sunlight" or item == "Rainbow Drop" or item == "Erdrick's Token" or item == "Faerie Flute" or item == "Silver Harp" or item == "Gwaelin's Love":
            return "Special"
        else:
            return "Normal"

    def lookup_weapon_power(self):
        if self.weapon:
            if self.weapon.name == "Bamboo Pole": return 2
            elif self.weapon.name == "Club": return 4
            elif self.weapon.name == "Copper Sword": return 10
            elif self.weapon.name == "Hand Axe": return 15
            elif self.weapon.name == "Broad Sword": return 20
            elif self.weapon.name == "Flame Sword": return 28
            elif self.weapon.name == "Erdrick's Sword": return 40
        else:
            return 0
    def lookup_armor_defense(self):
        if self.armor:
            if self.armor.name == "Clothes": return 2
            elif self.armor.name == "Leather Armor": return 4
            elif self.armor.name == "Chain Mail": return 10
            elif self.armor.name == "Half Plate": return 16
            elif self.armor.name == "Full Plate": return 24
            elif self.armor.name == "Magic Armor": return 24
            elif self.armor.name == "Erdrick's Armor": return 28
        else:
            return 0
    def lookup_shield_defense(self):
        if self.shield:
            if self.shield.name == "Small Shield": return 4
            elif self.shield.name == "Large Shield": return 10
            elif self.shield.name == "Silver Shield": return 25
            elif self.shield.name == "Circular Defendy Pot": return 12
            elif self.shield.name == "Rusty Shield": return 2
            elif self.shield.name == "Shield of Brass": return 28
            elif self.shield.name == "Erdrick's Shield": return 45

        else:
            return 0
    def lookup_item_power(self):
        return 2 if self.fighters_ring else 0

    def lookup_item_defense(self):
        return 2 if self.dragons_scale else 0

    def increment(self):
        self.step += 1
        if self.step >= self.steps:
            self.step = 0
    def getSurface(self):
        if self.sprite_identity == "Plain":
            return pygame.transform.scale(self.spritesheets[0].subsurface(pygame.rect.Rect(self.step*16+self.step+1+self.face*2*16+self.face*2,1,16,16)), (self.sizex, self.sizey))
        elif self.sprite_identity == "Shield":
            return pygame.transform.scale(self.spritesheets[1].subsurface(pygame.rect.Rect(self.step*16+self.step+1+self.face*2*16+self.face*2,1,16,16)), (self.sizex, self.sizey))
        elif self.sprite_identity == "Sword":
            return pygame.transform.scale(self.spritesheets[2].subsurface(pygame.rect.Rect(self.step*16+self.step+1+self.face*2*16+self.face*2,1,16,16)), (self.sizex, self.sizey))
        elif self.sprite_identity == "Swordshield":
            return pygame.transform.scale(self.spritesheets[3].subsurface(pygame.rect.Rect(self.step*16+self.step+1+self.face*2*16+self.face*2,1,16,16)), (self.sizex, self.sizey))
        elif self.sprite_identity == "Princess":
            return pygame.transform.scale(self.spritesheets[4].subsurface(pygame.rect.Rect(self.step*16+self.step+1+self.face*2*16+self.face*2,1,16,16)), (self.sizex, self.sizey))


    def valid_cell(self, y, x):

        if self.map.name == "Southern Shrine" and y == 6 and x == 7 and self.data.get("SRS_2", False):
            return True

        if self.map.map_data[x][y] == 14 and not self.data.get("RPR_1", False):
            playSound(41)
            return False

        if self.map.name == "World" and self.data.get("Rainbow Bridge", False) and y == 66 and x == 51:
            return True

        if self.map.map_data[x][y] == 1 or \
                self.map.map_data[x][y] == 10 or \
                self.map.map_data[x][y] == 12 or \
                self.map.map_data[x][y] == 19 or \
                self.map.map_data[x][y] == 22 or \
                                self.map.map_data[x][y] >= 23 and self.map.map_data[x][y] <= 41:
            playSound(41)
            return False

        for door in self.map.doors:
            if door.x == y and door.y == x and not self.data.get(door.name, False):
                return False

        for npc in self.map.NPCs:
            if npc.all_conditions_satisfied(self.items, self.data) and y == npc.x and x == npc.y and not self.data.get(npc.name, False):
                playSound(41)
                return False

        return True

    def initialize_transition(self, destx, desty, destmap):
        self.mode = "Transitioning"
        self.map_transition = True
        self.screenfade = "in"
        self.screenfadeticks = 0
        self.mx = destx
        self.my = desty
        self.teleport_pack = (destmap, self.sizex, self.sizey)
        self.execute_map_change()

    def execute_map_change(self):
        self.x = self.mx
        self.y = self.my
        self.offsetx = - self.mx + NUM_CELLS_WIDE / 2#self.moffsetx
        self.offsety = - self.my + NUM_CELLS_HIGH / 2#self.moffsety
        oldmapname = self.map.name
        self.map = Map.load_map(self.teleport_pack[0], self.teleport_pack[1], self.teleport_pack[2])
        for npc in self.map.NPCs:
            if npc.all_conditions_satisfied(self.items, self.data):
                if not self.data.get(npc.name, False):
                    self.map.mutex_data[(npc.x, npc.y)] = True
        self.map.mutex_data[(self.x, self.y)] = True
        self.face = self.map.initial_hero_face
        if self.new_bg_tile is not None:
            self.map.background_tile = self.new_bg_tile
            self.new_bg_tile = None
            self.face = self.new_face

        if self.oktolorikafterdying or self.youdied or self.is_dead or self.data.get("BEGIN", False) or self.data.get("CONTINUE", False):
            self.map.background_tile = 40

        if oldmapname != self.map.name:
            self.radiance_level = 0
            self.radiance_steps = 0
            self.torch = False

    def update(self, delta_ticks):
        #animate foot step
        self.step_ticks += delta_ticks
        if self.step_ticks > HEROSTEPSPEED:
            self.step_ticks = 0
            self.increment()
        if not self.motion_in_progress and not self.lag_motion:
            if self.flag_right:
                self.face = 3
                self.targetx = self.x + 1
                self.targety = self.y
                if self.valid_cell(self.x + 1, self.y) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx, self.targety)] = True
                    self.velx = (delta_ticks/HEROMOVESPEED)
                    self.vely = 0
                    self.motion_in_progress = True
                else:
                    self.lag_motion = True
                    self.lag_motion_tickspeed = 300
            elif self.flag_left:
                self.face = 1
                self.targetx = self.x - 1
                self.targety = self.y
                if self.valid_cell(self.x - 1, self.y) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx, self.targety)] = True
                    self.velx = -(delta_ticks / HEROMOVESPEED)
                    self.vely = 0
                    self.motion_in_progress = True
                else:
                    self.lag_motion = True
                    self.lag_motion_tickspeed = 300
            elif self.flag_up:
                self.face = 2
                self.targety = self.y - 1
                self.targetx = self.x
                if self.valid_cell(self.x, self.y - 1) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx, self.targety)] = True
                    self.vely = -(delta_ticks / HEROMOVESPEED)
                    self.velx = 0
                    self.motion_in_progress = True
                else:
                    self.lag_motion = True
                    self.lag_motion_tickspeed = 300
            elif self.flag_down:
                self.face = 0
                self.targety = self.y + 1
                self.targetx = self.x
                if self.valid_cell(self.x, self.y + 1) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx, self.targety)] = True
                    self.vely = (delta_ticks / HEROMOVESPEED)
                    self.velx = 0
                    self.motion_in_progress = True
                else:
                    self.lag_motion = True
                    self.lag_motion_tickspeed = 300
        if self.motion_in_progress:
            if self.velx > 0:
                self.x = min(self.targetx, self.x + self.velx)
            else:
                self.x = max(self.targetx, self.x + self.velx)
            self.offsetx = -self.x + NUM_CELLS_HIGH/2
            if self.vely > 0:
                self.y = min(self.targety, self.y + self.vely)
            else:
                self.y = max(self.targety, self.y + self.vely)
            self.offsety = -self.y + NUM_CELLS_WIDE/2
            if self.x == self.targetx and self.y == self.targety:
                self.motion_in_progress = False

                if self.map.name == "Tantegel" and self.data.get("DLDEAD", False) and not self.data.get("POSTGAME", False) and self.x >= 12 and self.x <= 13 and self.y == 10:
                    endbit = TextNode("\n\n\nAnd thus thy adventure comes to and end.... unless the dragons return again. \n\n\n")
                    princessjourney = Query(width=4, height=3, options=["Yes", "No"])
                    princessjourney.responses=[TextNode("I'm so happy!",next=endbit), TextNode("But thou must.", next=TextNode("May I travel as thy companion?", query=princessjourney))]
                    princessjourney.cancel_response=TextNode("But thou must.", next=TextNode("Dost thou love me, $hero_name$?", query=princessjourney))
                    self.walking_talk_box_message = TextNode("The legends have proven true.", next=TextNode("Thou art indeed of the line of Erdrick.", next=TextNode("It is thy right to rule over this land.", next=TextNode("Will thou take my place?", next=TextNode("$hero_name$ thought carefully before answering.", quoted=False, next=TextNode("I cannot, ", next=TextNode("said $hero_name$.", quoted=False, next=TextNode("If ever I am to rule a country, it must be a land that I myself find.", next=TextNode("Gwaelin said: ", quoted=False, next=TextNode("Please wait!", next=TextNode("I wish to go with thee on thy journey.", next=TextNode("May I travel as thy companion?", query=princessjourney))))))))))))
                    self.ready_for_ending_credits = True
                    self.delay_ticks = 0
                    self.walking_talk_box_visible = True
                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                    self.mode = "Talking"

                #erdrick's armor HP step boost
                if self.armor and self.armor.name == "Erdrick's Armor":
                    self.HP = min(self.maxhp, self.HP + 1)

                #magic armor HP step boost every 4th step
                if self.armor and self.armor.name == "Magic Armor":
                    self.magicarmorsteps += 1
                    if self.magicarmorsteps >= 4:
                        self.magicarmorsteps = 0
                        self.HP = min(self.maxhp, self.HP + 1)

                #repel and radiance steps
                if self.repel_steps > 0:
                    self.repel_steps -= 1
                    if self.repel_steps == 0:
                        if self.repel == "Fairy Water":
                            self.walking_talk_box_message = TextNode("The Fairy Water has lost its effect.", quoted=False)
                        else:
                            self.walking_talk_box_message = TextNode("REPEL has lost its effect.", quoted=False)
                        self.flag_down = False
                        self.flag_up = False
                        self.flag_right = False
                        self.flag_left = False
                        self.walking_talk_box_visible = True
                        self.add_to_message_render(self.walking_talk_box_message, replace=True)
                        self.mode = "Talking"
                self.repel_steps = max(0, self.repel_steps - 1)
                self.radiance_steps = max(0, self.radiance_steps - 1)

                #radiance level
                if self.torch:
                    self.radiance_level = 1
                elif self.radiance_steps >= 120:
                    self.radiance_level = 3
                elif self.radiance_steps >= 60:
                    self.radiance_level = 2
                elif self.radiance_steps > 0:
                    self.radiance_level = 1
                else:
                    self.radiance_level = 0

                encounter = False
                if self.map.name == "World" and self.x == 75 and self.y == 102 and not self.data.get("Golem", False): #Golem encounter
                    encounter = True
                    self.walking_talk_box_visible = True
                    self.walking_talk_box_message = TextNode("Golem draws near! \nCommand?", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.battle_mode = True
                    self.ready_to_end_battle = False
                    self.enemy_is_dead = False
                    self.enemy = Enemy("Golem")
                    changeBGMusic(13)
                    self.enemy_spiral_flag = True
                    self.enemy_spiral_index = 0
                    self.enemy_spiral_ticks = 0
                    self.mode = "Menu"
                elif self.map.name == "Swamp Cave" and self.x == 6 and self.y == 16 and not self.data.get("Green Dragon", False): #Green Dragon encounter
                    encounter = True
                    self.walking_talk_box_visible = True
                    self.walking_talk_box_message = TextNode("A Green Dragon draws near! \nCommand?", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.battle_mode = True
                    self.ready_to_end_battle = False
                    self.enemy_is_dead = False
                    self.enemy = Enemy("Green Dragon")
                    changeBGMusic(13)
                    self.enemy_spiral_flag = True
                    self.enemy_spiral_index = 0
                    self.enemy_spiral_ticks = 0
                    self.mode = "Menu"
                elif self.map.name == "Hauksness" and self.x == 19 and self.y == 14: #data intentionally avoids storing axe knight fight (copy of the classic)
                    encounter = True
                    self.walking_talk_box_visible = True
                    self.walking_talk_box_message = TextNode("An Axe Knight draws near! \nCommand?", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.battle_mode = True
                    self.ready_to_end_battle = False
                    self.enemy_is_dead = False
                    self.enemy = Enemy("Axe Knight")
                    changeBGMusic(13)
                    self.enemy_spiral_flag = True
                    self.enemy_spiral_index = 0
                    self.enemy_spiral_ticks = 0
                    self.mode = "Menu"



                #checking bbox triggers
                if self.map.has_bbox:
                    if self.x == self.map.bbox_left or self.y == self.map.bbox_top or self.x == self.map.bbox_left+self.map.bbox_width or self.y == self.map.bbox_top + self.map.bbox_height:
                        self.mode = "Transitioning"
                        self.mx = self.map.bbox_teleport_coords[0]
                        self.my = self.map.bbox_teleport_coords[1]
                        self.music_id = self.map.bbox_music_id
                        self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                        self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                        self.teleport_pack = (self.map.bbox_teleport_to, self.sizex, self.sizey)
                        self.map_transition = True
                        self.flag_moving = False
                        self.flag_left = False
                        self.flag_right = False
                        self.flag_up = False
                        self.flag_down = False
                        self.screenfade = "out"
                        self.screenfadeticks = 0
                        playSound(29)
                        return

                for trigger in self.map.triggers:
                    if self.x == trigger.x and self.y == trigger.y:
                        self.mode = "Transitioning"
                        self.mx = trigger.teleport_coords[0]
                        self.my = trigger.teleport_coords[1]
                        self.music_id = trigger.music_id
                        self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                        self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                        self.teleport_pack = (trigger.teleport_to, self.sizex, self.sizey)
                        self.map_transition = True
                        self.flag_moving = False
                        self.flag_left = False
                        self.flag_right = False
                        self.flag_up = False
                        self.flag_down = False
                        self.screenfade = "out"
                        self.screenfadeticks = 0
                        playSound(29)
                        return

                for trigger in self.map.soft_triggers:
                    if self.x == trigger.x and self.y == trigger.y:
                        self.mode = "Transitioning Softly"
                        self.mx = trigger.teleport_coords[0]
                        self.my = trigger.teleport_coords[1]
                        self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                        self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                        self.music_id = trigger.music_id
                        self.teleport_pack = (trigger.teleport_to, self.sizex, self.sizey)
                        self.new_bg_tile = trigger.bg
                        self.new_face = trigger.face
                        self.map_transition = True
                        self.flag_moving = False
                        self.flag_left = False
                        self.flag_right = False
                        self.flag_up = False
                        self.flag_down = False
                        self.screenfade = "out"
                        self.screenfadeticks = 0
                        playSound(trigger.sound_id)
                        return

                foundtrigger = False
                for trigger in self.map.secret_stairs:
                    if self.x == trigger.x and self.y == trigger.y and self.map.name == "Charlock Castle" and self.data.get("Charlock Castle Stairs", False):
                        foundtrigger = True
                        break
                    elif self.x == trigger.x and self.y == trigger.y and self.map.name == "Hauksness" and self.data.get("Hauksness Stairs", False):
                        foundtrigger = True
                        break
                if foundtrigger:
                    self.mode = "Transitioning"
                    self.mx = trigger.teleport_coords[0]
                    self.my = trigger.teleport_coords[1]
                    self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                    self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                    self.teleport_pack = (trigger.teleport_to, self.sizex, self.sizey)
                    self.map_transition = True
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.screenfade = "out"
                    self.screenfadeticks = 0
                    return

                #swamp step without erdrick's armor
                if self.map.map_data[self.y][self.x] == 18 and self.armor and not self.armor.name == "Erdrick's Armor" and not self.data.get("DLDEAD", False):
                    self.swamp_blinks = 0
                    self.swamp_flash = True
                    self.swamp_flash_ticks = 0
                    self.lag_motion = True
                    self.lag_motion_tickspeed = 85
                    self.HP = max(0, self.HP - 2)
                    if self.HP <= 0:
                        self.youdied = True
                        self.delayticks = 0
                        self.flag_moving = False
                        self.flag_left = False
                        self.flag_right = False
                        self.flag_up = False
                        self.flag_down = False
                        self.barrier_blinks = 0  # hijack barrier variables to implement the death blink effect
                        self.barrier_flash = True
                        self.barrier_flash_ticks = 0

                # barrier step without erdrick's armor
                if self.map.map_data[self.y][self.x] == 2 and self.armor and not self.armor.name == "Erdrick's Armor" and not self.data.get("DLDEAD", False):
                    self.barrier_blinks = 0
                    self.barrier_flash = True
                    self.barrier_flash_ticks = 0
                    self.lag_motion = True
                    self.lag_motion_tickspeed = 85
                    self.HP = max(0, self.HP - 15)
                    if self.HP <= 0:
                        self.delayticks = 0
                        self.youdied = True
                        self.flag_moving = False
                        self.flag_left = False
                        self.flag_right = False
                        self.flag_up = False
                        self.flag_down = False
                        self.barrier_blinks = 0  # hijack barrier variables to implement the death blink effect
                        self.barrier_flash = True
                        self.barrier_flash_ticks = 0

                if self.cursed_belt or self.death_necklace:
                    if self.map.name == "Tantegel" and self.x >= 12 and self.x <= 13 and self.y == 29 and self.face == 2: #only if you walk up not down (and out)
                        self.walking_talk_box_message = TextNode("Cursed one, be gone!")
                        self.walking_talk_box_visible = True
                        self.add_to_message_render(self.walking_talk_box_message, replace=True)
                        self.delayticks = 0
                        self.mode = "Talking"
                        self.eviction = True
                        self.delayticks = 0
                        self.spell_blinks = 0
                        self.spell_cast = True
                        self.spell_blink_ticks = 0
                        self.spell_chanted = Spell("None")
                        self.npc_special_action = "Nothing"



                if not encounter and not self.ready_to_win_game:
                    for region in self.map.monster_regions:
                        if region.contains(self.x, self.y):
                            tile = self.map.map_data[self.y][self.x]
                            odds_denominator = region.tile_odds.get(tile, 16)
                            if random.random() < 1.0/odds_denominator:
                                enemy = random.choice(region.monster_list)
                                self.enemy = Enemy(enemy)
                                if self.repel_steps > 0 and self.strength > self.enemy.strength:
                                    pass #repelled
                                else:
                                    self.walking_talk_box_visible = True
                                    changeBGMusic(13)
                                    self.walking_talk_box_message = TextNode("A " + enemy + " draws near! \nCommand?", quoted=False)
                                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                                    self.flag_moving = False
                                    self.flag_left = False
                                    self.flag_right = False
                                    self.flag_up = False
                                    self.flag_down = False
                                    self.battle_mode = True
                                    self.ready_to_end_battle = False
                                    self.enemy_is_dead = False
                                    self.enemy_spiral_flag = True
                                    self.enemy_spiral_index = 0
                                    self.enemy_spiral_ticks = 0
                                    self.mode = "Menu"
                                    if self.strength >= self.enemy.strength * 2 and random.random() < 0.25:
                                        # enemy runs away
                                        self.add_to_message_render(TextNode("The " + self.enemy.name + " is running away.", quoted=False))
                                        self.battle_running = True
                                        self.mode = "Talking"


    def fight_dragonlord(self):
        self.fight_the_dragonlord = False
        self.walking_talk_box_visible = True
        self.walking_talk_box_message = TextNode("The Dragonlord draws near! \nCommand?", quoted=False)
        self.add_to_message_render(self.walking_talk_box_message, replace=True)
        self.battle_mode = True
        self.ready_to_end_battle = False
        self.enemy_is_dead = False
        self.enemy = Enemy("Dragonlord first form")
        self.enemy_spiral_flag = True
        self.enemy_spiral_index = 0
        self.enemy_spiral_ticks = 0
        self.mode = "Menu"

    def fight_true_dragonlord(self):
        self.fight_the_true_dragonlord = False
        self.walking_talk_box_visible = True
        self.walking_talk_box_message = TextNode("The Dragonlord draws near! \nCommand?", quoted=False)
        self.add_to_message_render(self.walking_talk_box_message, replace=True)
        self.battle_mode = True
        self.ready_to_end_battle = False
        self.enemy_is_dead = False
        self.enemy = Enemy("Dragonlord second form")
        self.enemy_spiral_flag = True
        self.enemy_spiral_index = 0
        self.enemy_spiral_ticks = 0
        self.mode = "Menu"

    def kill_enemy(self):

        playSound(24)
        pauseMusic()
        self.kill_enemy_sound = True

        if self.enemy.name == "Golem":
            self.data["Golem"] = True
        if self.map.name == "Swamp Cave" and self.enemy.name == "Green Dragon":
            self.data["Green Dragon"] = True

        self.battle_report_mode = True
        self.battle_mode = False
        self.E = min(65535, 100*self.enemy.E+self.E)
        G_up = random.randint(self.enemy.G[0], self.enemy.G[1])
        self.G = min(65535, self.G+100*G_up)

        startbit = TextNode("Thou hast done well in defeating the " + self.enemy.name + ".", quoted=False)
        infobit = TextNode("Thy Experience increases by " + str(self.enemy.E) + ". \tThy GOLD increases by " + str(G_up) + ".", quoted=False)

        if self.enemy.name == "Dragonlord" and self.enemy._dl == 1:
            self.walking_talk_box_message = startbit
            startbit.next = TextNode("The dragonlord reveals its true form!", quoted=False)
            self.add_to_message_render(startbit, replace=False)
            self.ready_to_end_battle = True
            self.enemy_is_dead = True
            self.fight_the_true_dragonlord = True
        elif self.enemy.name == "Dragonlord" and self.enemy._dl == 2:
            self.walking_talk_box_message = startbit
            startbit.next = TextNode("Thou hast found the Ball of Light.", quoted=False, next=TextNode("Radiance streams forth as thy hands touch the object and hold it aloft.", quoted=False, next=TextNode("Across the land spreads the brilliance until all shadows are banished and peace is restored.", quoted=False)))
            self.dragonlord_is_dead = True
            self.data["DLDEAD"] = True
            self.cursed_belt = False
            self.death_necklace = False
            self.data["DeathNecklace"] = False
            self.data["CursedBelt"] = False
            self.add_to_message_render(startbit, replace=False)
            self.ready_to_end_battle = True
            self.enemy_is_dead = True
        else:

            #level up
            if self.E >= self.experience_table[self.level]:
                newlv = self.level
                while (self.E >= self.experience_table[newlv]):
                    newlv += 1
                newlv -= 1
                oldlv = self.level
                old_strength = self.strength
                old_agility = self.agility
                old_maxmp = self.maxmp
                old_maxhp = self.maxhp
                if self.strength_progression[self.growth_str-1][newlv]:
                    self.strength = self.base_strength + self.strength_progression[self.growth_str-1][newlv]
                if self.agility_progression[self.growth_agi-1][newlv]:
                    self.agility = self.base_agility + self.agility_progression[self.growth_agi-1][newlv]
                if self.maxhp_progression[self.growth_maxhp-1][newlv]:
                    self.maxhp = self.base_maxhp + self.maxhp_progression[self.growth_maxhp-1][newlv]
                if self.maxmp_progression[self.growth_maxmp-1][newlv]:
                    if newlv >= 3:
                        self.maxmp = self.base_maxmp + self.maxmp_progression[self.growth_maxmp-1][newlv]
                    else:
                        self.maxmp = 0
                strength_gain = self.strength - old_strength
                agility_gain = self.agility - old_agility
                maxmp_gain = self.maxmp - old_maxmp
                maxhp_gain = self.maxhp - old_maxhp
                ongoing = self.walking_talk_box_message


                spells_learned = []
                for lv in range(oldlv, newlv+1):
                    if self.spell_progression[lv]:
                        spells_learned.append(self.spell_progression[lv])
                        self.spells.append(Spell(self.spell_progression[lv]))

                self.learned_new_spell = True

                spell_seg = ""
                for spell_learned in spells_learned:
                    spell_seg += "Thou hast learned a new spell. \t"
                if len(spells_learned) > 0:
                    spell_seg = TextNode(spell_seg, quoted=False)
                else:
                    spell_seg = None
                if maxmp_gain > 0:
                    mp_seg = TextNode("Thy Maximum Magic Points increase by " + str(maxmp_gain) + ".", next=spell_seg, quoted=False)
                else:
                    mp_seg = spell_seg
                if maxhp_gain > 0:
                    hp_seg = TextNode("Thy Maximum Hit Points increase by " + str(maxhp_gain) + ".", next=mp_seg, quoted=False)
                else:
                    hp_seg = mp_seg
                if agility_gain > 0:
                    agi_seg = "Thy Response Speed increases by " + str(agility_gain) + "."
                else:
                    agi_seg = ""
                if strength_gain > 0:
                    str_seg = TextNode("The power increases by " + str(strength_gain) + "." + " \t" + agi_seg, next=hp_seg, quoted=False)
                else:
                    str_seg = hp_seg
                self.level = newlv+1
                if self.level == 30:
                    self.data["LV30"] = True
                infobit.next = TextNode("Courage and wit have served thee well.  Thou hast been promoted to the next level.", quoted=False, next=str_seg)
            self.walking_talk_box_message = startbit
            startbit.next = infobit
            self.add_to_message_render(self.walking_talk_box_message, replace=False)
            self.level_up_sound = True
            self.ready_to_end_battle = True
            self.enemy_is_dead = True


    def add_to_inventory(self, item):
        if item.type == "Weapon":
            self.weapon = Item(item.name, item.cost, item.type)
        elif item.type == "Armor":
            self.armor = Item(item.name, item.cost, item.type)
        elif item.type == "Shield":
            self.shield = Item(item.name, item.cost, item.type)
        else:
            self.items.append(Item(item.name, item.cost, item.type))

    def remove_from_inventory(self, item):
        if item.type == "Weapon":
            self.weapon = None
        elif item.type == "Armor":
            self.armor = None
        elif item.type == "Shield":
            self.shield = None
        else:
            for _item in self.items:
                if item.name == _item.name:
                    self.items.remove(_item)
                    break

    def use_item(self, item_index):
        for i,item in enumerate(self.draw_items):
            if i == item_index:
                itemname = item
                break
        for j,item in enumerate(self.undraw_items):
            if 1+j+i == item_index:
                itemname = item
        for item in self.items:
            if item.name == itemname:
                break


        if self.battle_mode:
            self.action = "ITEM"
            self.item_used = item_index
            if item.name in ["Faerie Flute", "Herb"]:
                if self.lost_initiative:
                    self.chose_a_turn = True
                    self.mode = "Talking"
                    self.display_item_window = False
                else:
                    if item.name == "Faerie Flute":
                        msg = self.name + " blew the Faerie's Flute."
                        self.add_to_message_render(TextNode(msg, quoted=False))
                        if self.enemy.name == "Golem":
                            self.next_msg = TextNode("Quietly Golem closes his eyes and settles into sleep.", quoted=False)
                            self.enemy.asleep = True
                            self.enemy.turns_asleep = 0
                        else:
                            self.next_msg = TextNode("But nothing happened.", quoted=False)
                        self.mode = "Talking"
                        self.display_item_window = False
                        self.faerie_flute_blown = True
                        self.faerie_flute_ticks = 0
                        self.faerie_flute_sound = True
                        self.display_item_window = False
                        #self.item_box.reset()
                    elif item.name == "Herb":
                        hp_recovery = random.randint(23, 30)
                        if self.HP + hp_recovery > self.maxhp:
                            hp_recovery = self.maxhp - self.HP
                        self.HP += hp_recovery
                        self.add_to_message_render(TextNode(self.name + " used the Herb.", quoted=False))
                        self.display_item_window = False
                        self.mode = "Talking"
                        self.items.remove(item)
                        self.chose_a_turn = True
            else:
                self.add_to_message_render(TextNode("That cannot be used in battle. \nCommand?", quoted=False))
                self.display_item_window = False
                self.mode = "Menu"

        else:
            if item.name == "Faerie Flute":
                self.walking_talk_box_message = TextNode(self.name + " blew the Faerie's Flute.", quoted=False)
                self.faerie_flute_blown = True
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.next_msg = TextNode("But nothing happened.", quoted=False)
                self.mode = "Talking"
                self.faerie_flute_ticks = 0
                self.faerie_flute_sound = True
                self.walking_talk_box_visible = True
                self.display_item_window = False
                #self.item_box.reset()
                return
            elif item.name == "Torch":
                if self.map.is_dark:
                    self.torch = True
                    self.radiance_level = 1
                    self.items.remove(item)
                    self.display_item_window = False
                    # self.item_box.reset()
                    self.mode = "Walking"
                    return
                else:
                    self.walking_talk_box_message = TextNode("A torch can be used only in dark places.", quoted=False)
            elif item.name == "Herb":
                hp_recovery = random.randint(23, 30)
                if self.HP + hp_recovery > self.maxhp:
                    hp_recovery = self.maxhp - self.HP
                self.HP += hp_recovery
                self.walking_talk_box_message = TextNode(self.name + " used the Herb.", quoted=False)
                self.items.remove(item)
            elif item.name == "Wings":
                if not self.map.is_dungeon:
                    self.time_to_warp_home = True
                    self.delayticks = 0
                    self.items.remove(item)
                    self.walking_talk_box_message = TextNode("$hero_name$ threw the Wings of the Wyvern up into the sky.", quoted=False)
                    self.music_id = 4
                else:
                    self.walking_talk_box_message = TextNode("The Wings of the Wyvern cannot be used here.", quoted=False)
            elif item.name == "Fairy Water":
                self.repel_steps = 127
                self.items.remove(item)
                self.walking_talk_box_message = TextNode("$hero_name$ sprinkled the Fairy Water over his body.", quoted=False)
                self.repel = "Fairy Water"
            elif item.name == "Dragon's Scale":
                if not self.dragons_scale:
                    self.dragons_scale = True
                    self.walking_talk_box_message = TextNode("$hero_name$ donned the scale of the dragon.", quoted=False)
                else:
                    self.walking_talk_box_message = TextNode("Thou art already wearing the scale of the dragon.", quoted=False)
            elif item.name == "Fighter's Ring":
                if not self.fighters_ring:
                    self.fighters_ring = True
                    self.walking_talk_box_message = TextNode("$hero_name$ put on the Fighter's Ring.", quoted=False)
                else:
                    self.walking_talk_box_message = TextNode("$hero_name$ adjusted the position of the Fighter's Ring.", quoted=False)
            elif item.name == "Silver Harp":
                self.walking_talk_box_message = TextNode("$hero_name$ played a sweet melody on the harp.", quoted=False)
                self.delayticks = 0
                self.time_to_lure_enemies = True
            elif item.name == "Magic Key":
                self.do_door()
                return
            elif item.name == "Cursed Belt":
                if self.cursed_belt:
                    self.walking_talk_box_message = TextNode("The " + item.name + " is squeezing thy body.", quoted=False)
                else:
                    if self.data.get("DLDEAD",False):
                        self.walking_talk_box_message = TextNode("$hero_name$ put on the " + item.name + ".  \nThe Ball of Light prevents the curse.", quoted=False)
                    else:
                        self.cursed_belt = True
                        self.data["CursedBelt"] = True
                        self.walking_talk_box_message = TextNode("$hero_name$ put on the " + item.name + " and was cursed!", quoted=False)
            elif item.name == "Death Necklace":
                if self.death_necklace:
                    self.walking_talk_box_message = TextNode("The " + item.name + " is squeezing thy body.", quoted=False)
                else:
                    if self.data.get("DLDEAD",False):
                        self.walking_talk_box_message = TextNode("$hero_name$ put on the " + item.name + ".  \nThe Ball of Light prevents the curse.", quoted=False)
                    else:
                        self.death_necklace = True
                        self.data["DeathNecklace"] = True
                        self.walking_talk_box_message = TextNode("$hero_name$ put on the " + item.name + " and was cursed!", quoted=False)
            elif item.name == "Staff of Rain" or item.name == "Stones of Sunlight" or item.name == "Erdrick's Token":
                self.walking_talk_box_message = TextNode("$hero_name$ held the " + item.name + " tightly. \nBut nothing happened.", quoted=False)
            elif item.name == "Rainbow Drop":
                if self.map.name == "World" and self.x == 67 and self.y == 51 and not self.data.get("Rainbow Bridge", False) and self.face == 1:
                    self.walking_talk_box_message = TextNode("$hero_name$ held the " + item.name + " toward the sky.", quoted=False)
                    self.do_rainbow_bridge = True
                else:
                    self.walking_talk_box_message = TextNode("$hero_name$ held the " + item.name + " toward the sky.", quoted=False, next=TextNode("But no rainbow appeared here.", quoted=False))
            elif item.name == "Gwaelin's Love":
                castle_x = 45
                castle_y = 45
                dx = self.x - castle_x
                dy = self.y - castle_y
                if dx < 0:
                    xdir = "east"
                else:
                    xdir = "west"
                ax = abs(dx)
                if dy < 0:
                    ydir = "south"
                else:
                    ydir = "north"
                ay = abs(dy)
                if self.data.get("LV30", False):
                    lvbit = TextNode("$hero_name$? \nThis is Gwaelin. Know that thou hath reached the final level.")
                else:
                    lvbit = TextNode("Heed my voice, " + self.name + ", for this is Gwaelin. \tTo reach the next level thou must raise thy Experience Points by " + str(self.to_next_level()) + ". \tMy hope is with thee.")
                if self.map.name == "World":
                    lvbit.next = TextNode("From where thou art now, my castle lies... " + str(ay) + " to the " + ydir + " and... " + str(ax) + " to the " + xdir + ".", next=TextNode("I love thee, " + self.name + "."))
                else:
                    lvbit.next = TextNode("I love thee, " + self.name + ".")
                self.walking_talk_box_message = lvbit
            else:
                self.walking_talk_box_message = TextNode(self.name + " took out the " + item.name + ".", next=TextNode("Greetings, $hero_name$.  I am the Almighty programmer.  I haven't implemented the use of this item yet, so you'll have to be patient.  Sorry!"), quoted=False)
            self.mode = "Talking"
            self.display_item_window = False
            # self.item_box.reset()
            self.walking_talk_box_visible = True
            self.add_to_message_render(self.walking_talk_box_message, replace=True)
        if self.battle_mode and self.convert_initiative:
            self.enemy_turn = True
            self.chose_a_turn = False
            self.item_used = None

    def update_sprite(self):
        if self.weapon and self.shield:
            self.sprite_identity = "Swordshield"
        elif self.weapon and not self.shield:
            self.sprite_identity = "Sword"
        elif not self.weapon and self.shield:
            self.sprite_identity = "Shield"
        else:
            self.sprite_identity = "Plain"

    def update_sleep(self):
        if self.asleep:
            self.turns_asleep += 1
            if self.turns_asleep > 1:
                if random.random() < 0.50:
                    self.asleep = False
                    self.add_to_message_render(TextNode("$hero_name$ awakes.", quoted=False))
                else:
                    self.add_to_message_render(TextNode("Thou art still asleep.", quoted=False))
    def cast_spell(self, spell):
        if self.battle_mode:
            self.action = "SPELL"
            self.spell_chanted = spell
            if self.lost_initiative:
                self.chose_a_turn = True
                self.mode = "Talking"
            else:
                if spell.name == "OUTSIDE" or spell.name == "RETURN" or spell.name == "REPEL" or spell.name == "RADIANT":
                    self.add_to_message_render(TextNode("That cannot be used in battle. \nCommand?", quoted=False))
                    self.mode = "Menu"
                else:
                    if self.MP >= spell.mp_cost:
                        self.walking_talk_box_visible = True
                        self.walking_talk_box_message = TextNode(self.name + " chanted the spell of " + spell.name + ".", quoted=False)
                        self.add_to_message_render(self.walking_talk_box_message, replace=False)
                        self.spell_chanted = spell
                        self.spell_lag = True
                        self.spell_sound = True
                        self.spell_lag_tickspeed = 150.0
                        self.spell_blinks = 0
                        self.spell_cast = True
                        self.spell_blink_ticks = 0
                        self.mode = "Talking"
                    else:
                        self.walking_talk_box_visible = True
                        self.add_to_message_render(TextNode("Thy MP is too low.", quoted=False), replace=False)
                        self.add_to_message_render(TextNode("Command?", quoted=False), replace=False)
                        self.battle_command_selector_x = 0
                        self.battle_command_selector_y = 0
                        self.mode = "Menu"
        else:
            if self.MP >= spell.mp_cost:
                self.walking_talk_box_visible = True
                self.walking_talk_box_message = TextNode(self.name + " chanted the spell of " + spell.name + ".", quoted=False)
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.spell_chanted = spell
                self.spell_lag = True
                self.spell_sound = True
                self.spell_lag_tickspeed = 650.0
                self.spell_blinks = 0
                self.spell_cast = True
                self.spell_blink_ticks = 0
                self.mode = "Talking"
            else:
                self.walking_talk_box_visible = True
                self.walking_talk_box_message = TextNode("Thy MP is too low.", quoted=False)
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.mode = "Talking"

    def execute_spell_effect(self):
        self.MP -= self.spell_chanted.mp_cost
        if self.spell_chanted.name == "HEAL":
            if self.battle_mode:
                if not self.spell_stopped:
                    self.HP = min(self.HP + random.randint(10, 17), self.maxhp)
                    self.chose_a_turn = True
                    self.mode = "Talking"
                else:
                    self.walking_talk_box_message = TextNode("But that spell hath been blocked.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
            else:
                self.HP = min(self.HP + random.randint(10, 17), self.maxhp)
        elif self.spell_chanted.name == "HURT":
            if self.battle_mode:
                if not self.spell_stopped:
                    dmg = random.randint(5, 12) if random.random() >= self.enemy.hurt_resist else 0
                    if dmg == 0:
                        self.walking_talk_box_message = TextNode("The spell will not work.", quoted=False)
                    else:
                        self.walking_talk_box_message = TextNode("The " + self.enemy.name + "'s Hit Points have been reduced by " + str(dmg) + ".", quoted=False)
                    self.enemy.HP -= dmg
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
                else:
                    self.walking_talk_box_message = TextNode("But that spell hath been blocked.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
            else:
                self.walking_talk_box_message = TextNode("But nothing happened.", quoted=False)
                self.add_to_message_render(self.walking_talk_box_message, replace=False)
                self.mode = "Talking"
        elif self.spell_chanted.name == "SLEEP":
            if self.battle_mode:
                if not self.spell_stopped:
                    success = True if random.random() >= self.enemy.sleep_resist else False
                    if success:
                        self.walking_talk_box_message = TextNode("Thou hast put the " + self.enemy.name + " to sleep.", quoted=False)
                        self.enemy.asleep = True
                        self.enemy.turns_asleep = 0
                    else:
                        self.walking_talk_box_message = TextNode("The spell will not work.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
                else:
                    self.walking_talk_box_message = TextNode("But that spell hath been blocked.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
            else:
                self.walking_talk_box_message = TextNode("But nothing happened.", quoted=False)
                self.add_to_message_render(self.walking_talk_box_message, replace=False)
                self.mode = "Talking"
        elif self.spell_chanted.name == "RADIANT":
            if self.battle_mode:
                pass #cant reach
            else:
                if self.map.is_dark:
                    self.torch = False
                    self.radiance_level = 3
                    self.radiance_steps = 200
                else:
                    self.walking_talk_box_message = TextNode("But nothing happened.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.mode = "Talking"
        elif self.spell_chanted.name == "STOPSPELL":
            if self.battle_mode:
                if not self.spell_stopped:
                    success = True if random.random() >= self.enemy.stopspell_resist else False
                    if success:
                        self.walking_talk_box_message = TextNode("The " + self.enemy.name + "'s spell hath been blocked.", quoted=False)
                        self.enemy.spell_stopped = True
                    else:
                        self.walking_talk_box_message = TextNode("The spell will not work.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
                else:
                    self.walking_talk_box_message = TextNode("But that spell hath been blocked.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
            else:
                self.walking_talk_box_message = TextNode("But nothing happened.", quoted=False)
                self.add_to_message_render(self.walking_talk_box_message, replace=False)
                self.mode = "Talking"
        elif self.spell_chanted.name == "OUTSIDE":
            if self.battle_mode:
                pass  # cant reach
            else:
                if self.map.is_dungeon:
                    self.mode = "Transitioning"
                    self.mx = self.map.outsidex
                    self.my = self.map.outsidey
                    self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                    self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                    self.teleport_pack = ("World", self.sizex, self.sizey)
                    self.map_transition = True
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.screenfade = "out"
                    self.screenfadeticks = 0
                    self.walking_talk_box_visible = False
                    self.walking_talk_box_message = ""
                else:
                    self.walking_talk_box_message = TextNode("But nothing happened.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.mode = "Talking"
        elif self.spell_chanted.name == "RETURN":
            if self.battle_mode:
                pass  #cant reach
            else:
                if not self.map.is_dungeon:
                    self.mode = "Transitioning"
                    playSound(27)
                    self.mx = 44
                    self.my = 45
                    self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                    self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                    self.teleport_pack = ("World", self.sizex, self.sizey)
                    self.music_id = 4
                    self.map_transition = True
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.screenfade = "out"
                    self.screenfadeticks = 0
                    self.walking_talk_box_visible = False
                    self.walking_talk_box_message = ""
                else:
                    self.walking_talk_box_message = TextNode("But nothing happened.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.mode = "Talking"
        elif self.spell_chanted.name == "REPEL":
            if self.battle_mode:
                pass  # cant reach
            else:
                self.repel_steps = 127
                self.repel = "REPEL"
        elif self.spell_chanted.name == "HEALMORE":
            if self.battle_mode:
                if not self.spell_stopped:
                    self.HP = min(self.HP + random.randint(85, 100), self.maxhp)
                    self.chose_a_turn = True
                    self.mode = "Talking"
                else:
                    self.walking_talk_box_message = TextNode("But that spell hath been blocked.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
            else:
                self.HP = min(self.HP + random.randint(85, 100), self.maxhp)
        elif self.spell_chanted.name == "HURTMORE":
            if self.battle_mode:
                if not self.spell_stopped:
                    dmg = random.randint(58, 65) if random.random() >= self.enemy.hurt_resist else 0
                    if dmg == 0:
                        self.walking_talk_box_message = TextNode("The spell will not work.", quoted=False)
                    else:
                        self.walking_talk_box_message = TextNode("The " + self.enemy.name + "'s Hit Points have been reduced by " + str(dmg) + ".", quoted=False)
                    self.enemy.HP -= dmg
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
                else:
                    self.walking_talk_box_message = TextNode("But that spell hath been blocked.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=False)
                    self.chose_a_turn = True
                    self.mode = "Talking"
            else:
                self.walking_talk_box_message = TextNode("But nothing happened.", quoted=False)
                self.add_to_message_render(self.walking_talk_box_message, replace=False)
                self.mode = "Talking"

    def to_next_level(self):
        if self.level >= 30:
            return 0
        else:
            return self.experience_table[self.level+1] - self.E

    def perform_battle_action(self, action_str):
        if action_str == "FIGHT":
            self.action = "FIGHT"
            initiative_success = True if (self.agility * random.randint(0,255) < self.enemy.agility * random.randint(0,255) * 0.25) else False
            if initiative_success:
                self.chose_a_turn = True
                self.lost_initiative = True
                self.mode = "Talking"
            else:
                self.heroattack = True
                self.lost_initiative = False
                self.add_to_message_render(TextNode("$hero_name$ attacks!", quoted=False))
                self.prepare_attack_enemy_sound = True
                self.mode = "Talking"

        elif action_str == "RUN":
            if self.enemy.asleep:
                run_success = True
            else:
                run_success = False if (self.agility * random.randint(0,255) < self.enemy.agility * random.randint(0,255) * self.enemy.run_resist) else True
            if run_success:
                self.battle_mode = False
                self.battle_report_mode = True
                self.enemy_is_dead = True
                self.battle_running = True
                self.mode = "Talking"
                self.add_to_message_render(TextNode("$hero_name$ started to run.", quoted=False), replace=False)
            else:
                self.add_to_message_render(TextNode("$hero_name$ start to run away. \nBut was blocked in front.", quoted=False), replace=False)
                self.chose_a_turn = True
                self.mode = "Talking"

        elif action_str == "SPELL":
            if len(self.spells) > 0:
                initiative_success = True if (self.agility * random.randint(0,255) < self.enemy.agility * random.randint(0,255) * 0.25) else False
                if initiative_success:
                    self.lost_initiative = True
                self.mode = "Spell"
            else:
                self.walking_talk_box_visible = True
                self.add_to_message_render(TextNode("You have no spells. \nCommand?", quoted=False))
                self.mode = "Menu"

        elif action_str == "ITEM":
            if len(self.items) > 0:
                self.update_draw_items()
                self.display_item_window = True
                self.mode = "Item"
                initiative_success = True if (self.agility * random.randint(0,255) < self.enemy.agility * random.randint(0,255) * 0.25) else False
                if initiative_success:
                    self.lost_initiative = True
            else:
                self.walking_talk_box_visible = True
                self.add_to_message_render(TextNode("Nothing of use has yet been given to thee.", quoted=False))
                self.mode = "Menu"

    def read_adventure_logs(self):
        available_adventure_logs = []
        for adventure_log in [1,2,3]:
            try:
                shelf_file = open("gamedata" + str(adventure_log) + ".logsav", "r")
                available_adventure_logs.append(adventure_log)
            except:
                pass
        return available_adventure_logs

    def save_game(self, adventure_log):
        shelf_file = shelve.open("gamedata" + str(adventure_log) + ".logsav")
        shelf_file["data"] = self.data
        shelf_file["name"] = self.name
        shelf_file["level"] = self.level
        shelf_file["weapon"] = self.weapon
        shelf_file["armor"] = self.armor
        shelf_file["shield"] = self.shield
        shelf_file["fighter's ring"] = self.fighters_ring
        shelf_file["dragon's scale"] = self.dragons_scale
        shelf_file["death necklace"] = self.death_necklace
        shelf_file["cursed belt"] = self.cursed_belt
        shelf_file["items"] = self.items
        shelf_file["monster dictionary"] = self.monster_dictionary
        shelf_file["gold"] = self.G
        shelf_file["exp"] = self.E
        shelf_file["base agi"] = self.base_agility
        shelf_file["base str"] = self.base_strength
        shelf_file["base mhp"] = self.base_maxhp
        shelf_file["base mmp"] = self.base_maxmp
        shelf_file["grow str"] = self.growth_str
        shelf_file["grow agi"] = self.growth_agi
        shelf_file["grow mhp"] = self.growth_maxhp
        shelf_file["grow mmp"] = self.growth_maxmp
        shelf_file.close()

    def load_game(self, adventure_log):
        self.new_game()
        try:
            shelf_file = shelve.open("gamedata" + str(adventure_log) + ".logsav")
        except Exception, e:
            print e
        try:
            self.data = shelf_file["data"]
            self.name = shelf_file["name"]
            self.level = shelf_file["level"]
            self.weapon = shelf_file["weapon"]
            self.armor = shelf_file["armor"]
            self.shield = shelf_file["shield"]
            self.fighters_ring = shelf_file["fighter's ring"]
            self.dragons_scale = shelf_file["dragon's scale"]
            self.death_necklace = shelf_file["death necklace"]
            self.cursed_belt = shelf_file["cursed belt"]
            self.items = shelf_file["items"]
            self.monster_dictionary = shelf_file["monster dictionary"]
            self.G = shelf_file["gold"]
            self.E = shelf_file["exp"]
            self.base_agility = shelf_file["base agi"]
            self.base_strength = shelf_file["base str"]
            self.base_maxhp = shelf_file["base mhp"]
            self.base_maxmp = shelf_file["base mmp"]
            self.growth_str = shelf_file["grow str"]
            self.growth_agi = shelf_file["grow agi"]
            self.growth_maxhp = shelf_file["grow mhp"]
            self.growth_maxmp = shelf_file["grow mmp"]
            shelf_file.close()
        except Exception, e:
            print e

        #testing
        #self.items = [Item("Wings")]

        self.initialize_level()
        self.update_sprite()



    def do_door(self):
        if self.face == 0:
            targetx = self.x
            targety = self.y + 1
        elif self.face == 1:
            targetx = self.x - 1
            targety = self.y
        elif self.face == 2:
            targetx = self.x
            targety = self.y - 1
        elif self.face == 3:
            targetx = self.x + 1
            targety = self.y

        for door in self.map.doors:
            if door.x == targetx and door.y == targety and not self.data.get(door.name, False):
                if "Magic Key" in [item.name for item in self.items]:
                    for item in self.items:
                        if item.name == "Magic Key":
                            self.items.remove(item)
                            break
                    self.data[door.name] = True
                    self.mode = "Walking"
                    self.display_item_window = False
                    # self.item_box.reset()
                    return
                else:
                    self.walking_talk_box_message = TextNode("Thou hast not a key to use.", quoted=False)
                    self.walking_talk_box_visible = True
                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                    self.mode = "Talking"
                    return
        else:
            self.walking_talk_box_message = TextNode("There is no door here.", quoted=False)
            self.walking_talk_box_visible = True
            self.add_to_message_render(self.walking_talk_box_message, replace=True)
            self.mode = "Talking"
            self.display_item_window = False
            # self.item_box.reset()

    def perform_action(self, action_str):
        if action_str == "TALK":
            if self.data.get("BEGIN", False) and not self.already_did_intro_chat:
                self.walking_talk_box_visible = True
                self.walking_talk_box_message = TextNode("Descendant of Erdrick, listen now to my words.", next=TextNode("It is told that in ages past Erdrick fought demons with a Ball of Light.", next=TextNode("Then came the Dragonlord who stole the precious globe and hid it in the darkness.", next=TextNode("Now, $hero_name$, thou must help us recover the Ball of Light and restore peace to our land.", next=TextNode("The Dragonlord must be defeated.", next=TextNode("Take now whatever thou may find in these Treasure Chests to aid thee in thy quest.", next=TextNode("Then speak with the guards, for they have much knowledge that may aid thee.", next=TextNode("May the light shine upon thee, $hero_name$."))))))))
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.mode = "Talking"
            elif self.data.get("CONTINUE", False) and not self.already_did_intro_chat:
                self.walking_talk_box_visible = True
                self.walking_talk_box_message = TextNode("I am glad thou hast returned. \nAll our hopes are riding on thee.", next=TextNode("Come see me again when thy level has increased."))
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.mode = "Talking"
            elif self.justdied:
                self.justdied = False
                self.walking_talk_box_visible = True
                self.is_dead = False
                self.walking_talk_box_message = TextNode("Death should not have taken thee, $hero_name$.", next=TextNode("I will give thee another chance.", next=TextNode("Now, go, $hero_name$!", quoted=False), quoted=False), quoted=False)
                self.oktolorikafterdying = False
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.mode = "Talking"
            else:
                if self.face == 0:
                    targetx = self.x
                    targety = self.y+1
                elif self.face == 1:
                    targetx = self.x-1
                    targety = self.y
                elif self.face == 2:
                    targetx = self.x
                    targety = self.y-1
                elif self.face == 3:
                    targetx = self.x+1
                    targety = self.y

                if self.map.map_data[targety][targetx] == 19:  #Table -- communicate across the cell in same direction
                    if self.face == 0:
                        targety += 1
                    elif self.face == 1:
                        targetx -= 1
                    elif self.face == 2:
                        targety -= 1
                    elif self.face == 3:
                        targetx += 1

                for npc in self.map.NPCs:
                    if npc.all_conditions_satisfied(self.items, self.data) and npc.x == targetx and npc.y == targety and not self.data.get(npc.name, False):
                        if not npc.type == "Trumpet Soldier":
                            if self.face == 0:
                                npc.face = 2
                            elif self.face == 1:
                                npc.face = 3
                            elif self.face == 2:
                                npc.face = 0
                            elif self.face == 3:
                                npc.face = 1
                        self.walking_talk_box_visible = True
                        if self.data.get("DLDEAD",False) and not self.map.name == "Tantegel" and not self.data.get("POSTGAME", False):
                            self.walking_talk_box_message = random.choice([TextNode("Hurrah! \nHurrah! \nLong live $hero_name$!"), TextNode("Thou hast brought us peace, again.")])
                        elif self.data.get("DLDEAD",False) and self.map.name == "Tantegel" and not self.data.get("POSTGAME", False):
                            self.walking_talk_box_message = TextNode("Come now, King Lorik awaits.")
                        else:
                            if npc.randomtexts:
                                self.walking_talk_box_message = random.choice([npc.basetext]+npc.randomtexts)
                            else:
                                self.walking_talk_box_message = npc.basetext
                        self.add_to_message_render(self.walking_talk_box_message, replace=True)
                        self.walking_talk_box_msg_tick_next = False
                        self.npc_special_action = npc.special_action
                        self.texttype = self.walking_talk_box_message.texttype
                        self.npc_name = npc.name
                        self.npc = npc
                        self.mode = "Talking"
                        return
                else:
                    self.walking_talk_box_visible = True
                    self.walking_talk_box_message = TextNode("There is no one there.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                    self.mode = "Talking"
                    return
        if action_str == "STAIRS":
            for trigger in self.map.triggers:
                if self.x == trigger.x and self.y == trigger.y and self.map.map_data[self.y][self.x] == 16 or self.map.map_data[self.y][self.x] == 17:
                    self.mode = "Transitioning"
                    self.mx = trigger.teleport_coords[0]
                    self.my = trigger.teleport_coords[1]
                    self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                    self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                    self.teleport_pack = (trigger.teleport_to, self.sizex, self.sizey)
                    self.map_transition = True
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.screenfade = "out"
                    self.screenfadeticks = 0
                    return
            else:
                foundtrigger = False
                for trigger in self.map.secret_stairs:
                    if self.x == trigger.x and self.y == trigger.y and self.map.name == "Charlock Castle" and self.data.get("Charlock Castle Stairs", False):
                        foundtrigger = True
                    elif self.x == trigger.x and self.y == trigger.y and self.map.name == "Hauksness" and self.data.get("Hauksness Stairs", False):
                        foundtrigger = True

                if foundtrigger:
                    self.mode = "Transitioning"
                    self.mx = trigger.teleport_coords[0]
                    self.my = trigger.teleport_coords[1]
                    self.moffsetx = - self.mx + NUM_CELLS_WIDE / 2
                    self.moffsety = - self.my + NUM_CELLS_HIGH / 2
                    self.teleport_pack = (trigger.teleport_to, self.sizex, self.sizey)
                    self.map_transition = True
                    self.flag_moving = False
                    self.flag_left = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_down = False
                    self.screenfade = "out"
                    self.screenfadeticks = 0
                    return
                else:
                    self.walking_talk_box_visible = True
                    self.walking_talk_box_message = TextNode("There are no stairs here.", quoted=False)
                    self.add_to_message_render(self.walking_talk_box_message, replace=True)
                    self.mode = "Talking"

        if action_str == "STATUS":
            self.mode = "Status"

        if action_str == "SPELL":
            if len(self.spells) > 0:
                self.mode = "Spell"
            else:
                self.walking_talk_box_visible = True
                self.walking_talk_box_message = TextNode("You have no spells.", quoted=False)
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.mode = "Talking"

        if action_str == "DOOR":
            self.do_door()

        if action_str == "TAKE":
            self.walking_talk_box_message = TextNode("There is nothing there.", quoted=False)
            for hidden_item in self.map.chests:
                if self.x == hidden_item.x and self.y == hidden_item.y:
                    if not self.data.get(hidden_item.name, False):
                        if hidden_item.name == "EDC_1":
                            self.walking_talk_box_message = TextNode("Fortune smiles upon thee, " + str(self.name) + ".  \tThou hast found the " + hidden_item.contents.name + ".", quoted=False, next=TextNode("The tablet reads as follows: ", quoted=False, next=TextNode("I am Erdrick and thou art my descendant.", next=TextNode("Three items were needed to reach the Isle of Dragons, which is south of Brecconary.", next=TextNode("I gathered these items, reached the island, and there defeated a creature of great evil.", next=TextNode("Now I have entrusted the three items to three worthy keepers.", next=TextNode("Their descendants will protect the items until thy quest leads thee to seek them out.", next=TextNode("When a new evil arises, find the three items, then fight!"))))))))
                        elif hidden_item.contents.option_odds > 0:
                            if random.random() < hidden_item.contents.option_odds:
                                hidden_item.contents = hidden_item.contents.option_item

                        if hidden_item.contents.name == "Gold":
                            gold_value = random.randint(hidden_item.contents.cost[0], hidden_item.contents.cost[1])
                            self.walking_talk_box_message = TextNode("Of GOLD thou hast gained " + str(gold_value) + ".", quoted=False)
                            self.G += gold_value
                        elif hidden_item.contents.type == "Weapon":
                            self.walking_talk_box_message = TextNode("Fortune smiles upon thee, " + str(self.name) + ".  \tThou hast found the " + hidden_item.contents.name + ".", quoted=False)
                            self.weapon = hidden_item.contents
                        else:
                            self.walking_talk_box_message = TextNode("Fortune smiles upon thee, " + str(self.name) + ".  \tThou hast found the " + hidden_item.contents.name + ".", quoted=False)
                            self.update_draw_items()
                            if len(self.undraw_items) + len(self.draw_items) > 9:
                                self.walking_talk_box_message.next = TextNode("If thou would take the " + hidden_item.contents.name + ", thou must discard some other item.", quoted=False, next=TextNode("Dost thou wish to have the " + hidden_item.contents.name + "?",  quoted=False,  query=Query(options=["YES", "NO"],
                                                                                                                                                                                                                                                                        responses=[TextNode("What shall thou drop?",  quoted=False, query=Query(options=[],
                                                                                                                                                                                                                                                                                      responses=[],
                                                                                                                                                                                                                                                                                      cancel_response=TextNode("Thou hast given up thy " + hidden_item.contents.name + ".",  quoted=False, ),
                                                                                                                                                                                                                                                                                      query_type="Discard Item",
                                                                                                                                                                                                                                                                                      transaction=hidden_item.name,
                                                                                                                                                                                                                                                                                      transaction2=hidden_item.contents.name)),
                                                                                                                                                                                                                                                                                   TextNode("Thou hast given up thy " + hidden_item.contents.name + ".",  quoted=False, )],
                                                                                                                                                                                                                                                                        cancel_response=TextNode("Thou hast given up thy " + hidden_item.contents.name + ".",  quoted=False, ),
                                                                                                                                                                                                                                                                                                       query_type="Decide to Discard",
                                                                                                                                                                                                                                                                                                       transaction=hidden_item.name,
                                                                                                                                                                                                                                                                                                       transaction2=hidden_item.contents.name
                                                                                                                                                                                                                                                                                                       )))
                            else:
                                self.items.append(hidden_item.contents)
                        self.data[hidden_item.name] = True
                        break
            self.walking_talk_box_visible = True
            self.add_to_message_render(self.walking_talk_box_message, replace=True)
            self.mode = "Talking"

        if action_str == "SEARCH":
            self.walking_talk_box_message = TextNode(self.name + " searched the ground all about.", next=TextNode("But there found nothing.", quoted=False), quoted=False)
            for hidden_item in self.map.hidden_items:
                if self.x == hidden_item.x and self.y == hidden_item.y:
                    if not self.data.get(hidden_item.name, False):
                        self.walking_talk_box_message = TextNode(self.name + " searched the ground all about.", next=TextNode(self.name + " discovers the " + hidden_item.name + ".", quoted=False), quoted=False)
                        if hidden_item.name == "Erdrick's Armor":
                            self.armor = Item("Erdrick's Armor", type="Armor")
                        else:
                            self.items.append(Item(hidden_item.name))
                        self.data[hidden_item.name] = True
                        break
            for hidden_stairs in self.map.secret_stairs:
                if self.map.name == "Charlock Castle":
                    if hidden_stairs.x == self.x and hidden_stairs.y == self.y:
                        if not self.data.get("Charlock Castle Stairs", False):
                            self.walking_talk_box_message = TextNode(self.name + " searched the ground all about.", quoted=False, next=TextNode(self.name + " discovers the Secret Passage.", quoted=False))
                            self.data["Charlock Castle Stairs"] = True
                elif self.map.name == "Hauksness":
                    if hidden_stairs.x == self.x and hidden_stairs.y == self.y:
                        if not self.data.get("Hauksness Stairs", False):
                            self.walking_talk_box_message = TextNode(self.name + " searched the ground all about.", quoted=False, next=TextNode(self.name + " discovers the Secret Passage.", quoted=False))
                            self.data["Hauksness Stairs"] = True

            for chest in self.map.chests:
                if chest.x == self.x and chest.y == self.y and not self.data.get(chest.name, False):
                    self.walking_talk_box_message = TextNode(self.name + " searched the ground all about.", quoted=False, next=TextNode("There is a treasure box.", quoted=False))

            self.walking_talk_box_visible = True
            self.add_to_message_render(self.walking_talk_box_message, replace=True)
            self.mode = "Talking"

        if action_str == "ITEM":
            if len(self.items) > 0:
                self.update_draw_items()
                self.display_item_window = True
                self.mode = "Item"
            else:
                self.walking_talk_box_message = TextNode("Nothing of use has yet been given to thee.", quoted=False)
                self.walking_talk_box_visible = True
                self.add_to_message_render(self.walking_talk_box_message, replace=True)
                self.mode = "Talking"








if __name__ == "__main__":
    Main().loop()