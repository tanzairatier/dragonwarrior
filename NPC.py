import pygame
import random
from Condition import Condition

class NPC:
    MAX_MOVE_SPEED = 1800
    MIN_MOVE_SPEED = 1250
    def __init__(self, map, initx, inity, initface, type, sizex, sizey, steps, can_move = True, basetext = "I don't have anything to say.", conditions = [], special_action=None, name="", data_conditions = [], randomtexts=None):
        self.move_ticks = random.randint(0,200)
        self.step_ticks = 0
        self.movespeedticks = random.randint(NPC.MIN_MOVE_SPEED,NPC.MAX_MOVE_SPEED)
        self.movespeed = 250.0
        self.stepspeed = 250.0
        self.map = map
        self.motion_in_progress = False
        self.flag_left = False
        self.flag_right = False
        self.flag_up = False
        self.flag_down = False
        self.x = initx
        self.y = inity
        self.face = initface
        self.step = 0
        self.steps = steps
        self.sizex = sizex
        self.sizey = sizey
        self.velx = 0
        self.vely = 0
        self.targetx = None
        self.targety = None
        self.type = type
        self.can_move = can_move
        self.basetext = basetext
        self.conditions = conditions
        self.data_conditions = data_conditions
        self.special_action = special_action
        self.name = name
        self.randomtexts = randomtexts

        if type == "Gray Soldier":
            self.spritesheet = pygame.image.load("spritesheets/npc_soldiergray.png").convert()
        elif type == "Young Lady":
            self.spritesheet = pygame.image.load("spritesheets/npc_girl.png").convert()
        elif type == "Woman":
            self.spritesheet = pygame.image.load("spritesheets/npc_woman.png").convert()
        elif type == "King":
            self.spritesheet = pygame.image.load("spritesheets/npc_king.png").convert()
        elif type == "Princess":
            self.spritesheet = pygame.image.load("spritesheets/npc_princess.png").convert()
        elif type == "Red Soldier":
            self.spritesheet = pygame.image.load("spritesheets/npc_soldierred.png").convert()
        elif type == "Trumpet Soldier":
            self.spritesheet = pygame.image.load("spritesheets/npc_trumpetsoldier.png").convert()
        elif type == "Merchant":
            self.spritesheet = pygame.image.load("spritesheets/npc_merchant.png").convert()
        elif type == "Old Man":
            self.spritesheet = pygame.image.load("spritesheets/npc_oldman.png").convert()
        elif type == "Dragonlord":
            self.spritesheet = pygame.image.load("spritesheets/npc_dragonlord.png").convert()
        elif type == "Hero":
            self.spritesheet = pygame.image.load("spritesheets/hero-demon.png").convert()
    def getSurface(self):
        return pygame.transform.scale(self.spritesheet.subsurface(
            pygame.rect.Rect(self.step * 16 + self.step + 1 + self.face * 2 * 16 + self.face * 2, 1, 16, 16)),
                                      (self.sizex, self.sizey))
    def valid_cell(self, y, x, data):
        if self.map.map_data[x][y] == 1 or \
                        self.map.map_data[x][y] == 0 or \
                        self.map.map_data[x][y] == 41 or \
                        self.map.map_data[x][y] == 10 or \
                self.map.map_data[x][y] == 42 or \
                self.map.map_data[x][y] == 2 or \
                        self.map.map_data[x][y] == 40 or \
                self.map.map_data[x][y] == 12 or \
                        self.map.map_data[x][y] == 19 or \
                        self.map.map_data[x][y] == 22 or \
                                23 <= self.map.map_data[x][y] <= 38:
            return False
        if x == self.map.bbox_left+self.map.bbox_width or x == self.map.bbox_left or y == self.map.bbox_top or y == self.map.bbox_left+self.map.bbox_height: #this technically only works because no components of map intersect with the lines made by these or statements
            return False

        for door in self.map.doors:
            if door.x == y and door.y == x and not data.get(door.name, False):
                return False
        return True

    def increment(self):
        self.step += 1
        if self.step >= self.steps:
            self.step = 0

    def move(self):
        dir = random.randint(0,3)
        if dir == 0:
            self.flag_down = True
            self.flag_right = False
            self.flag_up = False
            self.flag_left = False
        elif dir == 1:
            self.flag_down = False
            self.flag_right = True
            self.flag_up = False
            self.flag_left = False
        elif dir == 2:
            self.flag_down = False
            self.flag_right = False
            self.flag_up = True
            self.flag_left = False
        elif dir == 3:
            self.flag_down = False
            self.flag_right = False
            self.flag_up = False
            self.flag_left = True


    def update(self, delta_ticks, data, heromotion_in_progress):
        #animate foot step
        self.step_ticks += delta_ticks
        if self.step_ticks > self.stepspeed:
            self.step_ticks = 0
            self.increment()
        if self.can_move:
            self.move_ticks += delta_ticks
            if self.move_ticks > self.movespeedticks:
                if not heromotion_in_progress:
                    self.movespeedticks = random.randint(NPC.MIN_MOVE_SPEED,NPC.MAX_MOVE_SPEED)
                    self.move_ticks = 0
                    self.move()
        if not self.motion_in_progress:
            if self.flag_right:
                self.face = 3
                self.targetx = self.x + 1
                self.targety = self.y
                if self.valid_cell(self.x + 1, self.y, data) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx,self.targety)] = True
                    self.velx = (delta_ticks/self.movespeed)
                    self.vely = 0
                    self.motion_in_progress = True
                else:
                    self.flag_down = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_left = False
            elif self.flag_left:
                self.face = 1
                self.targetx = self.x - 1
                self.targety = self.y
                if self.valid_cell(self.x - 1, self.y, data) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx, self.targety)] = True
                    self.velx = -(delta_ticks / self.movespeed)
                    self.vely = 0
                    self.motion_in_progress = True
                else:
                    self.flag_down = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_left = False
            elif self.flag_up:
                self.face = 2
                self.targety = self.y - 1
                self.targetx = self.x
                if self.valid_cell(self.x, self.y - 1, data) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx, self.targety)] = True
                    self.vely = -(delta_ticks / self.movespeed)
                    self.velx = 0
                    self.motion_in_progress = True
                else:
                    self.flag_down = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_left = False
            elif self.flag_down:
                self.face = 0
                self.targety = self.y + 1
                self.targetx = self.x
                if self.valid_cell(self.x, self.y + 1, data) and not self.map.mutex_data.get((self.targetx,self.targety),False):
                    self.map.mutex_data[(self.x, self.y)] = False
                    self.map.mutex_data[(self.targetx, self.targety)] = True
                    self.vely = (delta_ticks / self.movespeed)
                    self.velx = 0
                    self.motion_in_progress = True
                else:
                    self.flag_down = False
                    self.flag_right = False
                    self.flag_up = False
                    self.flag_left = False
        if self.motion_in_progress:
            if self.velx > 0:
                self.x = min(self.targetx, self.x + self.velx)
            else:
                self.x = max(self.targetx, self.x + self.velx)
            if self.vely > 0:
                self.y = min(self.targety, self.y + self.vely)
            else:
                self.y = max(self.targety, self.y + self.vely)
            if self.x == self.targetx and self.y == self.targety:
                self.motion_in_progress = False
                self.flag_down = False
                self.flag_right = False
                self.flag_up = False
                self.flag_left = False

    def all_conditions_satisfied(self, items, data):
        item_names = [item.name for item in items]
        all_satisfied = True
        for condition in self.conditions:
            if not condition.isSatisfied(item_names):
                all_satisfied = False
                break
        for condition in self.data_conditions:
            if not condition.isSatisfied(data):
                all_satisfied = False
                break
        return all_satisfied
