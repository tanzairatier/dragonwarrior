import maps
from NPC import NPC
from Condition import Condition,MultiCondition,DataCondition
from TextNode import TextNode
from Query import Query
from Item import Item
from Query import Transaction

class Trigger:
    def __init__(self, x, y, map, nx, ny, music_id):
        self.x = x
        self.y = y
        self.teleport_to = map
        self.teleport_coords = (nx, ny)
        self.music_id = music_id

class SoftTrigger:
    def __init__(self, x, y, map, nx, ny, bg, face, music_id, sound_id):
        self.x = x
        self.y = y
        self.teleport_to = map
        self.teleport_coords = (nx, ny)
        self.bg = bg
        self.face = face
        self.music_id = music_id
        self.sound_id = sound_id


class HiddenItem:
    def __init__(self, name, x, y):
        self.x = x
        self.y = y
        self.name = name

class Chest:
    def __init__(self, x, y, name, contents):
        self.x = x
        self.y = y
        self.name = name
        self.contents = contents

class Door:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name

class MonsterRegion:
    def __init__(self, monster_list, bounding_box, tile_odds = {9:24,18:16,21:16,11:8,15:8,5:16,2:16}):  #these are tile codes, and the values are denominators of 1 (so fractions, 1/d)
        self.monster_list = monster_list
        self.bounding_box = bounding_box
        self.tile_odds = tile_odds
    def contains(self,x,y):
        if x >= self.bounding_box[0] and y >= self.bounding_box[1] and x <= self.bounding_box[0]+self.bounding_box[2] and y <= self.bounding_box[1]+self.bounding_box[3]:
            return True
        else:
            return False

class Map:
    def __init__(self, map_data, name=""):
        self.map_data = [[int(x) for x in m.split("\t")] for m in map_data[1:-1].split("\n")]
        self.mutex_data = {}  #list of x-y coords where mutexes are claimed by some NPC or Hero
        self.name = name
        self.has_bbox = False
        self.triggers = []
        self.soft_triggers = []
        self.hidden_items = []
        self.NPCs = []
        self.secret_stairs = []
        self.chests = []
        self.doors = []
        self.is_dungeon = False
        self.is_dark = False
        self.monster_regions = []
    def setBoundingBoxTrigger(self, box_top, box_left, width, height, dest_map, coord_x, coord_y, music_id=None):
        """stepping onto the border of the bounding box teleports you to dest map and coords there"""
        self.has_bbox = True
        self.bbox_top = box_top
        self.bbox_left = box_left
        self.bbox_width = width
        self.bbox_height = height
        self.bbox_teleport_to = dest_map
        self.bbox_teleport_coords = (coord_x, coord_y)
        self.bbox_music_id = music_id
    def addTrigger(self, x, y, map, nx, ny, music_id=None):
        self.triggers.append(Trigger(x, y, map, nx, ny, music_id))
    def addSoftTrigger(self, x, y, map, nx, ny, bg, face, music_id=None, sound_id=None):
        self.soft_triggers.append(SoftTrigger(x, y, map, nx, ny, bg, face, music_id, sound_id))
    def addNPC(self, npc):
        self.NPCs.append(npc)
    def addChest(self, chest):
        self.chests.append(chest)
    def addDoor(self, door):
        self.doors.append(door)
    def addMonsters(self, monster_list = [], bounding_box = None):
        self.monster_regions.append(MonsterRegion(monster_list=monster_list, bounding_box=bounding_box))
def load_map(map_str, sizex, sizey):
    if map_str == "World":
        return load_World(sizex, sizey)
    elif map_str == "Tantegel":
        return load_Tantegel(sizex, sizey)
    elif map_str == "Brecconary":
        return load_Brecconary(sizex, sizey)
    elif map_str == "Swamp Cave":
        return load_Swamp_Cave(sizex, sizey)
    elif map_str == "Erdricks Cave":
        return load_Erdricks_Cave(sizex, sizey)
    elif map_str == "Grave of Garinham":
        return load_Grave_of_Garinham(sizex, sizey)
    elif map_str == "Garinham":
        return load_Garinham(sizex, sizey)
    elif map_str == "Kol":
        return load_Kol(sizex, sizey)
    elif map_str == "Hauksness":
        return load_Hauksness(sizex, sizey)
    elif map_str == "Rimuldar":
        return load_Rimuldar(sizex, sizey)
    elif map_str == "Cantlin":
        return load_Cantlin(sizex, sizey)
    elif map_str == "Charlock Castle":
        return load_Charlock_Castle(sizex, sizey)
    elif map_str == "Charlock Dungeon":
        return load_Charlock_Dungeon(sizex, sizey)
    elif map_str == "Charlock Cellar":
        return load_Charlock_Cellar(sizex, sizey)
    elif map_str == "Northern Shrine":
        return load_Northern_Shrine(sizex, sizey)
    elif map_str == "Southern Shrine":
        return load_Southern_Shrine(sizex, sizey)
    elif map_str == "Rock Mountain Cave":
        return load_Rock_Mountain_Cave(sizex, sizey)
    elif map_str == "Charlock Bonus":
        return load_Charlock_Bonus(sizex, sizey)

def load_Tantegel(sizex, sizey):
    M = Map(maps.Tantegel, name="Tantegel")
    M.is_dungeon = False
    M.outsidex = 45
    M.outsidey = 45

    M.setBoundingBoxTrigger(1, 1, 31, 31, "World", 45, 45, music_id = 4)
    M.addSoftTrigger(31, 31, "Tantegel", 52, 49, bg=22, face=3, music_id = 2, sound_id = 28)
    M.addSoftTrigger(52, 49, "Tantegel", 31, 31, bg=9, face=2, music_id = 2, sound_id = 28)
    M.addSoftTrigger(9, 9, "Tantegel", 60, 11, bg=40, face=1, music_id = 1, sound_id = 28)
    M.addSoftTrigger(60, 11, "Tantegel", 9, 9, bg=9, face=3, music_id = 2, sound_id = 28)

    #NPCs
    M.addNPC(NPC(M, 10, 8, 0, "Gray Soldier", sizex, sizey, 2, can_move = False, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("King Lorik will record thy deeds in his Imperial Scroll so thou may return to thy quest later.")))
    M.addNPC(NPC(M, 10, 10, 2, "Gray Soldier", sizex, sizey, 2, can_move = False, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("If thou art planning to take a rest, first see King Lorik!")))
    M.addNPC(NPC(M, 10, 8, 0, "Gray Soldier", sizex, sizey, 2, can_move = False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("King Lorik will record thy deeds in his Imperial Scroll so thou may return to thy quest later.")))
    M.addNPC(NPC(M, 10, 10, 2, "Gray Soldier", sizex, sizey, 2, can_move = False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("If thou art planning to take a rest, first see King Lorik!")))
    M.addNPC(NPC(M, 14, 29, 1, "Gray Soldier", sizex, sizey, 2, can_move=False, basetext = TextNode("Welcome to Tantegel Castle.")))
    M.addNPC(NPC(M, 11, 29, 3, "Gray Soldier", sizex, sizey, 2, can_move=False, basetext = TextNode("Welcome to Tantegel Castle.")))
    M.addNPC(NPC(M, 14, 13, 0, "Young Lady", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("RPR_1", False), DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("Where oh where can I find Princess Gwaelin?")))
    M.addNPC(NPC(M, 14, 13, 0, "Young Lady", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("RPR_1", True), DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("Thank you for saving the princess.")))
    M.addNPC(NPC(M, 14, 13, 0, "Young Lady", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("RPR_1", False), DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("Where oh where can I find Princess Gwaelin?")))
    M.addNPC(NPC(M, 14, 13, 0, "Young Lady", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("RPR_1", True), DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("Thank you for saving the princess.")))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("BEGIN", True)], basetext=TextNode("When thou art finished preparing for thy departure, please see me.  I shall wait.")))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("CursedBelt", True)], basetext=TextNode("Thou hast failed and thou art cursed.", next=TextNode("Leave at once!"))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DeathNecklace", True)], basetext=TextNode("Thou hast failed and thou art cursed.", next=TextNode("Leave at once!"))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", False), DataCondition("Princess is Rescued", False), DataCondition("LV30", False), DataCondition("POSTGAME", False)], basetext=TextNode("I am greatly pleased that thou hast returned, $hero_name$.", next=TextNode("Before reaching thy next level of experience, thou must gain $hero_next_level$ Points.", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"], query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", False), DataCondition("Princess is Rescued", False), DataCondition("LV30", True), DataCondition("POSTGAME", False)], basetext=TextNode("I am greatly pleased that thou hast returned, $hero_name$.", next=TextNode("Thou art strong enough! \nWhy can thou not defeat the Dragonlord?", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", True), DataCondition("Princess is Rescued", True), DataCondition("LV30", False), DataCondition("POSTGAME", False)], basetext=TextNode("I am greatly pleased that thou hast returned, $hero_name$.", next=TextNode("Before reaching thy next level of experience, thou must gain $hero_next_level$ Points.", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", True), DataCondition("Princess is Rescued", True), DataCondition("LV30", True), DataCondition("POSTGAME", False)], basetext=TextNode("I am greatly pleased that thou hast returned, $hero_name$.", next=TextNode("Thou art strong enough! \nWhy can thou not defeat the Dragonlord?", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", False), DataCondition("Princess is Rescued", False), DataCondition("LV30", False), DataCondition("POSTGAME", True)], basetext=TextNode("The legends are true.  I shall ever bow unto thee, $hero_name$.", next=TextNode("Before reaching thy next level of experience, thou must gain $hero_next_level$ Points.", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", False), DataCondition("Princess is Rescued", False), DataCondition("LV30", True), DataCondition("POSTGAME", True)], basetext=TextNode("The legends are true.  I shall ever bow unto thee, $hero_name$.", next=TextNode("Thou art already at the max level.  However, there are tales of becoming stronger.", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", True), DataCondition("Princess is Rescued", True), DataCondition("LV30", False), DataCondition("POSTGAME", True)], basetext=TextNode("The legends are true.  I shall ever bow unto thee, $hero_name$.", next=TextNode("Before reaching thy next level of experience, thou must gain $hero_next_level$ Points.", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("RPR_1", True), DataCondition("Princess is Rescued", True), DataCondition("LV30", True), DataCondition("POSTGAME", True)], basetext=TextNode("The legends are true.  I shall ever bow unto thee, $hero_name$.", next=TextNode("Thou art already at the max level.  However, there are tales of becoming stronger.", next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")))))))
    M.addNPC(NPC(M, 55, 4, 0, "King", sizex, sizey, 2, name="Gwaelin's Love", data_conditions=[DataCondition("RPR_1", True), DataCondition("Princess is Rescued", False)], can_move=False, special_action="Gwaelin's Love", basetext=TextNode("Forever shall I be grateful for the gift of my daughter returned to her home, $hero_name$.  Accept my thanks.", next=TextNode("Now, Gwaelin, come to my side.", next=TextNode("Gwaelin then whispers:",quoted=False,next=TextNode("Wait a moment, please.  I would give a present to $hero_name$.", next=TextNode("Please accept my love, $hero_name$.", next=TextNode("Even when we two are parted by great distances, I shall be with thee.", next=TextNode("Farewell, $hero_name$.", action=True, next=TextNode("Will thou tell me now of thy deeds so they won't be forgotten?",
                               query=Query(options=["YES", "NO"],query_type = "Save the Game",
                                           responses=[TextNode("Thy deeds have been recorded on the Imperial Scrolls of Honor.", next=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")),
                                                      TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates.")
                                                      ],
                                           cancel_response=TextNode("Goodbye now, $hero_name$. Take care and tempt not the Fates."))))))))))))
    princesslove = Query(width=4, height=3, options=["Yes", "No"])
    princesslove.responses=[TextNode("I'm so happy!"), TextNode("But thou must.", next=TextNode("Dost thou love me, $hero_name$?", query=princesslove))]
    princesslove.cancel_response=TextNode("But thou must.", next=TextNode("Dost thou love me, $hero_name$?", query=princesslove))
    M.addNPC(NPC(M, 58, 4, 0, "Princess", sizex, sizey, 2, data_conditions=[DataCondition("Princess is Rescued", True), DataCondition("POSTGAME", False)], can_move=False, basetext=TextNode("I love thee, $hero_name$."), randomtexts=[TextNode("Even when we two are parted by great distances, I shall be with thee."),TextNode("Dost thou love me, $hero_name$?", query=princesslove)]))
    M.addNPC(NPC(M, 58, 4, 0, "Princess", sizex, sizey, 2, data_conditions=[DataCondition("Princess is Rescued", True), DataCondition("POSTGAME", True)], can_move=False, basetext=TextNode("I love thee, $hero_name$."), randomtexts=[TextNode("I shall wait here until thou art ready to leave this land."),TextNode("Dost thou love me, $hero_name$?", query=princesslove)]))
    M.addNPC(NPC(M, 55, 9, 3, "Gray Soldier", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("BEGIN", True)], basetext=TextNode("East of this castle is a town where armor, weapons, and many other items may be purchased.", next=TextNode("Return to the Inn for a rest if thou art wounded in battle, $hero_name$.", next=TextNode("Sleep heals all.")))))
    M.addNPC(NPC(M, 57, 9, 1, "Gray Soldier", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("BEGIN", True)], basetext=TextNode("If thou hast collected all the Treasure Chests, a key will be found.", next=TextNode("Once used, the key will disappear, but the door will be open and thou may pass through."))))
    M.addNPC(NPC(M, 55, 9, 3, "Gray Soldier", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("BEGIN", False)], basetext=TextNode("A word of advice.", next=TextNode("Save thy money for more expensive armor."))))
    M.addNPC(NPC(M, 57, 9, 1, "Gray Soldier", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("BEGIN", False)], basetext=TextNode("Listen to what people say. \tIt can be of great help.")))
    M.addNPC(NPC(M, 59, 5, 0, "Gray Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("RPR_1", False)], basetext=TextNode("Dost thou know about Princess Gwaelin?", query=Query(options=["YES", "NO"], responses=[TextNode("$hero_name$, please save the Princess."), TextNode("Half a year now hath passed since the Princess was kidnapped by the enemy.", next=TextNode("Never does the King speak of it, but he must be suffering much.", next=TextNode("$hero_name$, please save the Princess.")))], cancel_response=TextNode("Half a year now hath passed since the Princess was kidnapped by the enemy.", next=TextNode("Never does the King speak of it, but he must be suffering much.", next=TextNode("$hero_name$, please save the Princess.")))))))
    M.addNPC(NPC(M, 59, 5, 0, "Gray Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("RPR_1", True)], basetext=TextNode("Oh, brave $hero_name$.")))
    M.addNPC(NPC(M, 12, 11, 0, "Woman", sizex, sizey, 2, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("There was a time when Brecconary was a paradise. \tThen the Dragonlord's minions came.")))
    M.addNPC(NPC(M, 8, 22, 0, "Merchant", sizex, sizey, 2, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("We are merchants who have traveled much in this land. \tMany of our colleages have been killed by the servants of the Dragonlord.")))
    M.addNPC(NPC(M, 12, 11, 0, "Woman", sizex, sizey, 2, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("There was a time when Brecconary was a paradise. \tThen the Dragonlord's minions came.")))
    M.addNPC(NPC(M, 8, 22, 0, "Merchant", sizex, sizey, 2, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("We are merchants who have traveled much in this land. \tMany of our colleages have been killed by the servants of the Dragonlord.")))
    M.addNPC(NPC(M, 8, 27, 0, "Merchant", sizex, sizey, 2, basetext=TextNode("Rumor has it that entire towns have been destroyed by the Dragonlord's servants.")))
    M.addNPC(NPC(M, 17, 22, 3, "Gray Soldier", sizex, sizey, 2, data_conditions=[DataCondition("RPR_1", False)], can_move=False, basetext=TextNode("Where oh where can I find Princess Gwaelin?")))
    M.addNPC(NPC(M, 17, 22, 3, "Gray Soldier", sizex, sizey, 2, data_conditions=[DataCondition("RPR_1", True)], can_move=False, basetext=TextNode("Oh, my dearest Gwaelin! \nI hate thee, $hero_name$.")))
    M.addNPC(NPC(M, 17, 27, 0, "Gray Soldier", sizex, sizey, 2, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("When entering the cave, take with thee a torch.")))
    M.addNPC(NPC(M, 22, 28, 1, "Old Man", sizex, sizey, 2, can_move=False, special_action="MP Recovery", data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("$hero_name$'s coming was foretold by legend.  May the light shine upon this brave warrior.")))
    M.addNPC(NPC(M, 3, 13, 3, "Gray Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("Never does a brave person steal.")))
    M.addNPC(NPC(M, 4, 10, 0, "Woman", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("To become strong enough to face future trials thou must first battle many foes.")))
    M.addNPC(NPC(M, 22, 5, 0, "Gray Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("Thou must have a key to open a door.")))
    M.addNPC(NPC(M, 29, 7, 0, "Young Lady", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("When the sun and rain meet, a Rainbow Bridge shall appear.", next=TextNode("It's a legend."))))
    M.addNPC(NPC(M, 21, 16, 0, "Old Man", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("Let us wish the warrior well!", next=TextNode("May the light be thy strength!"))))
    M.addNPC(NPC(M, 28, 17, 2, "Gray Soldier", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("If thy Hit Points are high enough, by all means, enter.")))
    M.addNPC(NPC(M, 25, 16, 0, "Red Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("I am looking for the castle cellar. \tI heard it is not easily found.")))
    M.addNPC(NPC(M, 25, 23, 0, "Red Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("In Garinham, look for the grave of Garin.  Thou must push on a wall of darkness there.")))
    M.addNPC(NPC(M, 56, 51, 0, "Old Man", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("I have been waiting long for one such as thee.", next=TextNode("Take the Treasure Chest.")), conditions=[Condition("Stones of Sunlight", required=False)]))
    M.addNPC(NPC(M, 56, 51, 0, "Old Man", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", False), DataCondition("POSTGAME", False)], basetext=TextNode("Thou hast no business here. \tGo away."), conditions=[Condition("Stones of Sunlight", required=True)]))
    M.addNPC(NPC(M, 17, 27, 0, "Gray Soldier", sizex, sizey, 2, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("When entering the cave, take with thee a torch.")))
    M.addNPC(NPC(M, 22, 28, 1, "Old Man", sizex, sizey, 2, can_move=False, special_action="MP Recovery", data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("$hero_name$'s coming was foretold by legend.  May the light shine upon this brave warrior.")))
    M.addNPC(NPC(M, 3, 13, 3, "Gray Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("Never does a brave person steal.")))
    M.addNPC(NPC(M, 4, 10, 0, "Woman", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("To become strong enough to face future trials thou must first battle many foes.")))
    M.addNPC(NPC(M, 22, 5, 0, "Gray Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("Thou must have a key to open a door.")))
    M.addNPC(NPC(M, 29, 7, 0, "Young Lady", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("When the sun and rain meet, a Rainbow Bridge shall appear.", next=TextNode("It's a legend."))))
    M.addNPC(NPC(M, 21, 16, 0, "Old Man", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("Let us wish the warrior well!", next=TextNode("May the light be thy strength!"))))
    M.addNPC(NPC(M, 28, 17, 2, "Gray Soldier", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("If thy Hit Points are high enough, by all means, enter.")))
    M.addNPC(NPC(M, 25, 16, 0, "Red Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("A man in Rimuldar knows more about becoming stronger.")))
    M.addNPC(NPC(M, 25, 23, 0, "Red Soldier", sizex, sizey, 2, can_move=True, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("In Garinham, look for the grave of Garin.  Thou must push on a wall of darkness there.")))
    M.addNPC(NPC(M, 56, 51, 0, "Old Man", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("I have been waiting long for one such as thee.", next=TextNode("Take the Treasure Chest.")), conditions=[Condition("Stones of Sunlight", required=False)]))
    M.addNPC(NPC(M, 56, 51, 0, "Old Man", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", True)], basetext=TextNode("Thou hast no business here. \tGo away."), conditions=[Condition("Stones of Sunlight", required=True)]))

    M.addNPC(NPC(M, 11, 11, 3, "Trumpet Soldier", sizex, sizey, 1, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", False)], basetext=TextNode("code n/a")))
    M.addNPC(NPC(M, 11, 13, 3, "Trumpet Soldier", sizex, sizey, 1, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", False)], basetext=TextNode("code n/a")))
    M.addNPC(NPC(M, 11, 15, 3, "Trumpet Soldier", sizex, sizey, 1, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", False)], basetext=TextNode("code n/a")))
    M.addNPC(NPC(M, 14, 11, 1, "Trumpet Soldier", sizex, sizey, 1, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", False)], basetext=TextNode("code n/a")))
    M.addNPC(NPC(M, 14, 13, 1, "Trumpet Soldier", sizex, sizey, 1, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", False)], basetext=TextNode("code n/a")))
    M.addNPC(NPC(M, 14, 15, 1, "Trumpet Soldier", sizex, sizey, 1, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", False)], basetext=TextNode("code n/a")))
    M.addNPC(NPC(M, 13, 9, 0, "King", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", True), DataCondition("POSTGAME", False)], basetext=TextNode("code n/a")))

    again = Query(width=4, height=3, options=["YES", "NO"], query_type="Mini Shop", transaction=Transaction(Item("Magic Key", 85, "Normal")))
    again.cancel_response=TextNode("I will see thee later.")
    again.responses=[TextNode("Here, take this key.  Dost thou wish to purchase more?", query=again), TextNode("I will see thee later.")]
    M.addNPC(NPC(M, 26, 3, 0, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome. \tMagic Keys!  They can unlock any door.  \tDost thou wish to purchase one for 85 GOLD?",
                                                                                              query=again)))


    M.addChest(Chest(58, 2, "TGC_1", contents=Item("Magic Key")))
    M.addChest(Chest(56, 5, "TGC_2", contents=Item("Gold", cost=[120,120])))
    M.addChest(Chest(57, 5, "TGC_3", contents=Item("Torch")))

    M.addChest(Chest(3, 15, "TGC_4", contents=Item("Gold", cost=[6,13])))
    M.addChest(Chest(4, 16, "TGC_5", contents=Item("Gold", cost=[6,13])))
    M.addChest(Chest(3, 17, "TGC_6", contents=Item("Gold", cost=[6,13])))
    M.addChest(Chest(5, 17, "TGC_7", contents=Item("Gold", cost=[6,13])))

    M.addChest(Chest(56, 50, "TGC_8", contents=Item("Stones of Sunlight")))

    M.addDoor(Door(6, 15, "TGC_9"))
    M.addDoor(Door(20, 8, "TGC_10"))
    M.addDoor(Door(56, 10, "TGC_11"))
    M.background_tile = 9 #Grass
    M.initial_hero_face = 2
    return M


def load_Brecconary(sizex, sizey):
    M = Map(maps.Brecconary)
    M.is_dungeon = False

    M.setBoundingBoxTrigger(1, 1, 31, 31, "World", 50, 43, music_id = 4)

    M.addSoftTrigger(23, 7, "Brecconary", 57, 6, bg=0, face=2)
    M.addSoftTrigger(57, 7, "Brecconary", 23, 8, bg=9, face=0)

    M.addSoftTrigger(24, 26, "Brecconary", 59, 26, bg=0, face=0)
    M.addSoftTrigger(59, 25, "Brecconary", 24, 25, bg=9, face=2)

    M.addDoor(Door(23, 8, "BRC_1"))
    M.addDoor(Door(7, 25, "BRC_2"))

    M.addNPC(NPC(M, 12, 23, 1, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome to the traveler's Inn.  Room and board is 6 GOLD per night.  Dost though want a room?", query=Query(width=4, height=3, options=["Yes", "No"], responses=[TextNode("Good night."), TextNode("Okay.  \tGood-bye, traveler.")], query_type="Inn", query_inn_price=6, cancel_response=TextNode("Okay.  \tGood-bye, traveler.")))))
    M.addNPC(NPC(M, 7, 6, 0, "Merchant", sizex, sizey, 2, can_move=False,
                 basetext=TextNode("We deal in weapons and armor.  Dost thou wish to buy anything today?",
                                   query=Query(options=["Yes", "No"],
                                               responses=[TextNode("What dost thou wish to buy?",
                                                                   query=Query(
                                                                       options=[Item("Bamboo Pole", 10, "Weapon"),
                                                                                Item("Club", 60, "Weapon"),
                                                                                Item("Copper Sword", 180, "Weapon"),
                                                                                Item("Clothes", 20, "Armor"),
                                                                                Item("Leather Armor", 70, "Armor"),
                                                                                Item("Small Shield", 90, "Shield")],
                                                                       responses=[],
                                                                       cancel_response=TextNode("Please, come again."),
                                                                       query_type="Shop",
                                                                       width=9,
                                                                       height=7)),
                                                          TextNode("Please, come again.")],
                                               cancel_response=TextNode("Please, come again.")))))
    M.addNPC(NPC(M, 62, 27, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("CursedBelt", False), DataCondition("DeathNecklace", False)], basetext=TextNode("Welcome. \tWe deal in tools.  What can I do for thee?",
                                                                                              query=Query(options=["BUY", "SELL"],
                                                                                                          responses=[TextNode("What dost thou want?",
                                                                                                                              query=Query(options=[Item("Herb", 24, "Item"),
                                                                                                                                                   Item("Torch", 8, "Item"),
                                                                                                                                                   Item("Dragon's Scale", 20, "Item")],
                                                                                                                                          responses=[],
                                                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                          width=9,
                                                                                                                                          height=4,
                                                                                                                                          query_type="ItemShop")),
                                                                                                                     TextNode("What art thou selling?", query=Query(options=[],
                                                                                                                                                                    responses=[],
                                                                                                                                                                    cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                                                    query_type="Sell",
                                                                                                                                                                    width=9,
                                                                                                                                                                    height=None
                                                                                                                                                                    ))],
                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                          width=4,
                                                                                                          height=3
                                                                                                          ))))
    M.addNPC(NPC(M, 62, 27, 1, "Merchant", sizex, sizey, 2, data_conditions=[DataCondition("CursedBelt", True), DataCondition("DeathNecklace", False)], can_move=False, basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 62, 27, 1, "Merchant", sizex, sizey, 2, data_conditions=[DataCondition("CursedBelt", False), DataCondition("DeathNecklace", True)], can_move=False, basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 62, 27, 1, "Merchant", sizex, sizey, 2, data_conditions=[DataCondition("CursedBelt", True), DataCondition("DeathNecklace", True)], can_move=False, basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    again = Query(width=4, height=3, options=["YES", "NO"], query_type="Mini Shop", transaction=Transaction(Item("Fairy Water", 38, "Normal")))
    again.cancel_response=TextNode("All the best to thee")
    again.responses=[TextNode("I thank thee",next=TextNode("Won't thou buy one more bottle?", query=again)),TextNode("All the best to thee.")]
    M.addNPC(NPC(M, 60, 5, 1, "Young Lady", sizex, sizey, 2, can_move=False, basetext=TextNode("Will thou buy some Fairy Water for 38 GOLD to keep the Dragonlord's minions away?",
                                                                                              query=again)))
    M.addNPC(NPC(M, 3, 15, 0, "Woman", sizex, sizey, 2, can_move=False, basetext=TextNode("Thou art most welcome in Brecconary.")))
    M.addNPC(NPC(M, 6, 9, 0, "Young Lady", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome! \tEnter the shop and speak to its keeper across the desk.")))
    M.addNPC(NPC(M, 11, 5, 0, "Old Man", sizex, sizey, 2, can_move=True, basetext=TextNode("Watch thy Hit Points when in the Poisonous Marsh.")))
    M.addNPC(NPC(M, 15, 15, 0, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Go north to the seashore, then follow the coastline west until thou hath reached Garinham.")))
    M.addNPC(NPC(M, 14, 18, 0, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Many have been the warriors who have perished on this quest.", next=TextNode("But for thee, I wish success, $hero_name$."))))
    M.addNPC(NPC(M, 12, 26, 2, "Gray Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("Tell King Lorik that the search for his daugher hath failed.", next=TextNode("I am almost gone..."))))
    M.addNPC(NPC(M, 6, 28, 0, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Some say that Garin's grave is home to a Silver Harp.")))
    M.addNPC(NPC(M, 16, 12, 0, "Merchant", sizex, sizey, 2, can_move=True, basetext=TextNode("Please, save us from the minions of the Dragonlord.")))
    M.addNPC(NPC(M, 20, 19, 0, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Art thou the descendant of Erdrick? \tHast thou any proof?")))
    M.addNPC(NPC(M, 17, 27, 0, "Young Lady", sizex, sizey, 2, can_move=False, basetext=TextNode("No, I am not Princess Gwaelin.")))
    M.addNPC(NPC(M, 22, 26, 0, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Enter where thou can.")))
    M.addNPC(NPC(M, 25, 23, 0, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Within sight of Tantegel Castle to the south, is Charlock, ", next=TextNode("The fortress of the Dragonlord."))))
    M.addNPC(NPC(M, 28, 17, 0, "Gray Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("See King Lorik when thy experience levels are raised.")))
    M.addNPC(NPC(M, 26, 12, 0, "Old Man", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DeathNecklace", False), DataCondition("CursedBelt", False)], basetext=TextNode("If thou art cursed, come again.")))
    M.addNPC(NPC(M, 26, 12, 0, "Old Man", sizex, sizey, 2, can_move=False, special_action="Remove Curse", data_conditions=[DataCondition("DeathNecklace", True), DataCondition("CursedBelt", False)], basetext=TextNode("I will free thee from thy curse.", next=TextNode("Now, go."))))
    M.addNPC(NPC(M, 26, 12, 0, "Old Man", sizex, sizey, 2, can_move=False, special_action="Remove Curse", data_conditions=[DataCondition("DeathNecklace", False), DataCondition("CursedBelt", True)], basetext=TextNode("I will free thee from thy curse.", next=TextNode("Now, go."))))
    M.addNPC(NPC(M, 26, 12, 0, "Old Man", sizex, sizey, 2, can_move=False, special_action="Remove Curse", data_conditions=[DataCondition("DeathNecklace", True), DataCondition("CursedBelt", True)], basetext=TextNode("I will free thee from thy curse.", next=TextNode("Now, go."))))
    M.addNPC(NPC(M, 22, 12, 0, "Woman", sizex, sizey, 2, can_move=False, basetext=TextNode("There is a town where magic keys can be purchased.")))
    M.addNPC(NPC(M, 30, 3, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("Beware the bridges!", next=TextNode("Danger grows when thou crosses."))))

    M.background_tile = 9 #Grass
    M.initial_hero_face = 3
    return M

def load_Rimuldar(sizex, sizey):
    M = Map(maps.Rimuldar)
    M.is_dungeon = False

    M.setBoundingBoxTrigger(1, 1, 31, 31, "World", 104, 74, music_id = 4)
    M.addSoftTrigger(12, 22, "Rimuldar", 61, 22, bg=0, face=0)
    M.addSoftTrigger(13, 22, "Rimuldar", 62, 22, bg=0, face=0)
    M.addSoftTrigger(61, 21, "Rimuldar", 12, 21, bg=9, face=2)
    M.addSoftTrigger(62, 21, "Rimuldar", 13, 21, bg=9, face=2)

    M.addSoftTrigger(7, 5, "Rimuldar", 57, 5, bg=0, face=3)
    M.addSoftTrigger(6, 6, "Rimuldar", 56, 6, bg=0, face=3)
    M.addSoftTrigger(5, 7, "Rimuldar", 55, 7, bg=0, face=0)
    M.addSoftTrigger(56, 5, "Rimuldar", 6, 5, bg=9, face=1)
    M.addSoftTrigger(55, 6, "Rimuldar", 5, 6, bg=9, face=1)

    M.addNPC(NPC(M, 18, 20, 3, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome to the traveler's Inn.  Room and board is 55 GOLD per night.  Dost though want a room?", query=Query(width=4, height=3, options=["Yes", "No"], responses=[TextNode("Good night."), TextNode("Okay.  \tGood-bye, traveler.")], query_type="Inn", query_inn_price=55, cancel_response=TextNode("Okay.  \tGood-bye, traveler.")))))
    M.addNPC(NPC(M, 22, 25, 0, "Old Man", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("POSTGAME", False)], basetext=TextNode("Good day, I am Howard.  Four steps south of the bath in Kol thou shalt find a magic item.")))
    M.addNPC(NPC(M, 22, 25, 0, "Old Man", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("POSTGAME", True)], basetext=TextNode("Good day, I am Howard.  Becoming stronger?  I have heard tales of ghosts at Hauksness.  Perhaps you can find something there.")))
    M.addNPC(NPC(M, 26, 21, 1, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("You are $hero_name$?  It has been long since last we met.")))
    M.addNPC(NPC(M, 24, 16, 0, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("No, I have no tomatoes. \tI have no tomatoes today.")))
    M.addNPC(NPC(M, 25, 12, 0, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("The scales of the Dragonlord are as hard as steel.")))
    M.addNPC(NPC(M, 25, 9, 0, "Merchant", sizex, sizey, 2, can_move=False,
                 basetext=TextNode("We deal in weapons and armor.  \tDost thou wish to buy anything today?",
                                   query=Query(options=["Yes", "No"],
                                               responses=[TextNode("What dost thou wish to buy?",
                                                                   query=Query(
                                                                       options=[Item("Copper Sword", 180, "Weapon"),
                                                                                Item("Hand Axe", 560, "Weapon"),
                                                                                Item("Broad Sword", 1500, "Weapon"),
                                                                                Item("Half Plate", 1000, "Armor"),
                                                                                Item("Full Plate", 3000, "Armor"),
                                                                                Item("Magic Armor", 7700, "Armor")],
                                                                       responses=[],
                                                                       cancel_response=TextNode("Please, come again."),
                                                                       query_type="Shop",
                                                                       width=9,
                                                                       height=7)),
                                                          TextNode("Please, come again.")],
                                               cancel_response=TextNode("Please, come again.")))))
    M.addNPC(NPC(M, 17, 10, 2, "Young Lady", sizex, sizey, 2, can_move=False, basetext=TextNode("Who art thou? \tLeave at once or I will call my friends.")))
    M.addNPC(NPC(M, 13, 10, 2, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Art thou the descendant of Erdrick? \tHast thou any proof?")))
    M.addNPC(NPC(M, 8, 15, 1, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("Over the western part of this island Erdrick created a rainbow.", next=TextNode("'Tis also said that he entered the darkness from a hidden entrance in the room of the Dragonlord."))))
    M.addNPC(NPC(M, 16, 25, 2, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("All true warriors wear a ring."), conditions=[Condition("Fighter's Ring", required=False)]))
    M.addNPC(NPC(M, 16, 25, 2, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Is that a wedding ring?", next=TextNode("Thou seems too young to be married.")), conditions=[Condition("Fighter's Ring", required=True)]))
    M.addNPC(NPC(M, 12, 20, 3, "Gray Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Thou shalt find the Stones of Sunlight in Tantegel Castle, if thou has not found them yet.")))
    M.addNPC(NPC(M, 62, 25, 2, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("In this world is there any sword that can pierce the scales of the Dragonlord?")))
    M.addNPC(NPC(M, 58, 25, 3, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Heed my warning!  Travel not to the south for there the monsters are fierce and terrible.")))
    M.addNPC(NPC(M, 55, 28, 2, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("Before long the enemy will arrive.")))
    M.addNPC(NPC(M, 54, 25, 3, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("This is a magic place. \tHast thou found a magic temple?", query=Query(options=["YES", "NO"], responses=[TextNode("In this temple do the sun and rain meet."), TextNode("Go to the south.")], cancel_response=TextNode("Go to the south.")))))
    M.addNPC(NPC(M, 29, 2, 0, "Woman", sizex, sizey, 2, can_move=False, basetext=TextNode("I am Orwick, and I am waiting for my girl friend.")))
    M.addNPC(NPC(M, 4, 6, 2, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome!")))
    again = Query(width=4, height=3, options=["YES", "NO"], query_type="Mini Shop", transaction=Transaction(Item("Magic Key", 53, "Normal")))
    again.cancel_response=TextNode("I will see thee later.")
    again.responses=[TextNode("Here, take this key.  Dost thou wish to purchase more?", query=again), TextNode("I will see thee later.")]
    M.addNPC(NPC(M, 56, 9, 2, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("Magic Keys!  \tThey will unlock any door.  \tDost thou wish to purchase one for 53 GOLD?",
                                                                                              query=again)))
    M.addNPC(NPC(M, 2, 28, 3, "Young Lady", sizex, sizey, 2, can_move=False, basetext=TextNode("Orwick is late again.  I'm starving.")))

    M.addChest(Chest(26, 25, "RIM_1", contents=Item("Wings")))
    M.addDoor(Door(23, 23, "RIM_2"))
    M.addDoor(Door(24, 25, "RIM_3"))

    M.background_tile = 9  # Grass
    M.initial_hero_face = 1
    return M

def load_Cantlin(sizex, sizey):
    M = Map(maps.Cantlin)
    M.is_dungeon = False

    M.setBoundingBoxTrigger(1, 1, 29, 29, "World", 75, 104, music_id = 4)

    M.addSoftTrigger(3, 3, "Cantlin", 49, 3, bg=0, face=1)
    M.addSoftTrigger(50, 3, "Cantlin", 4, 3, bg=5, face=3)

    M.addSoftTrigger(28, 3, "Cantlin", 62, 3, bg=0, face=2)
    M.addSoftTrigger(62, 4, "Cantlin", 28, 4, bg=5, face=0)

    M.addSoftTrigger(12, 12, "Cantlin", 53, 12, bg=0, face=3)
    M.addSoftTrigger(12, 15, "Cantlin", 53, 15, bg=0, face=3)
    M.addSoftTrigger(12, 16, "Cantlin", 53, 16, bg=0, face=3)
    M.addSoftTrigger(12, 17, "Cantlin", 53, 17, bg=0, face=3)
    M.addSoftTrigger(12, 18, "Cantlin", 53, 18, bg=0, face=3)
    M.addSoftTrigger(12, 19, "Cantlin", 53, 19, bg=0, face=3)
    M.addSoftTrigger(12, 20, "Cantlin", 53, 21, bg=0, face=3)
    M.addSoftTrigger(12, 21, "Cantlin", 53, 22, bg=0, face=3)
    M.addSoftTrigger(12, 22, "Cantlin", 53, 23, bg=0, face=3)
    M.addSoftTrigger(12, 23, "Cantlin", 53, 24, bg=0, face=3)
    M.addSoftTrigger(12, 24, "Cantlin", 53, 24, bg=0, face=3)
    M.addSoftTrigger(13, 24, "Cantlin", 54, 24, bg=0, face=2)
    M.addSoftTrigger(14, 24, "Cantlin", 55, 24, bg=0, face=2)
    M.addSoftTrigger(17, 24, "Cantlin", 58, 24, bg=0, face=2)
    M.addSoftTrigger(18, 24, "Cantlin", 59, 24, bg=0, face=2)
    M.addSoftTrigger(19, 24, "Cantlin", 60, 24, bg=0, face=2)
    M.addSoftTrigger(19, 23, "Cantlin", 60, 23, bg=0, face=1)
    M.addSoftTrigger(19, 22, "Cantlin", 60, 22, bg=0, face=1)
    M.addSoftTrigger(19, 21, "Cantlin", 60, 21, bg=0, face=1)
    M.addSoftTrigger(19, 18, "Cantlin", 60, 18, bg=0, face=1)
    M.addSoftTrigger(19, 17, "Cantlin", 60, 17, bg=0, face=1)
    M.addSoftTrigger(19, 16, "Cantlin", 60, 16, bg=0, face=1)
    M.addSoftTrigger(19, 15, "Cantlin", 60, 15, bg=0, face=1)
    M.addSoftTrigger(19, 14, "Cantlin", 60, 14, bg=0, face=1)
    M.addSoftTrigger(19, 13, "Cantlin", 60, 13, bg=0, face=1)
    M.addSoftTrigger(19, 12, "Cantlin", 60, 12, bg=0, face=1)
    M.addSoftTrigger(18, 12, "Cantlin", 59, 12, bg=0, face=0)
    M.addSoftTrigger(17, 12, "Cantlin", 58, 12, bg=0, face=0)
    M.addSoftTrigger(16, 12, "Cantlin", 57, 12, bg=0, face=0)

    M.addSoftTrigger(52, 12, "Cantlin", 11, 12, bg=5, face=1)
    M.addSoftTrigger(52, 15, "Cantlin", 11, 15, bg=5, face=1)
    M.addSoftTrigger(52, 16, "Cantlin", 11, 16, bg=5, face=1)
    M.addSoftTrigger(52, 17, "Cantlin", 11, 17, bg=5, face=1)
    M.addSoftTrigger(52, 18, "Cantlin", 11, 18, bg=5, face=1)
    M.addSoftTrigger(52, 19, "Cantlin", 11, 19, bg=5, face=1)
    M.addSoftTrigger(52, 20, "Cantlin", 11, 20, bg=5, face=1)
    M.addSoftTrigger(52, 21, "Cantlin", 11, 21, bg=5, face=1)
    M.addSoftTrigger(52, 22, "Cantlin", 11, 22, bg=5, face=1)
    M.addSoftTrigger(52, 23, "Cantlin", 11, 23, bg=5, face=1)
    M.addSoftTrigger(52, 24, "Cantlin", 11, 24, bg=5, face=1)
    M.addSoftTrigger(53, 25, "Cantlin", 12, 25, bg=5, face=0)
    M.addSoftTrigger(55, 25, "Cantlin", 14, 25, bg=5, face=0)
    M.addSoftTrigger(58, 25, "Cantlin", 17, 25, bg=5, face=0)
    M.addSoftTrigger(60, 25, "Cantlin", 19, 25, bg=5, face=0)
    M.addSoftTrigger(61, 24, "Cantlin", 20, 24, bg=5, face=3)
    M.addSoftTrigger(61, 23, "Cantlin", 20, 23, bg=5, face=3)
    M.addSoftTrigger(61, 22, "Cantlin", 20, 22, bg=5, face=3)
    M.addSoftTrigger(61, 18, "Cantlin", 20, 18, bg=5, face=3)
    M.addSoftTrigger(61, 17, "Cantlin", 20, 17, bg=5, face=3)
    M.addSoftTrigger(61, 16, "Cantlin", 20, 16, bg=5, face=3)
    M.addSoftTrigger(61, 15, "Cantlin", 20, 15, bg=5, face=3)
    M.addSoftTrigger(61, 14, "Cantlin", 20, 14, bg=5, face=3)
    M.addSoftTrigger(61, 13, "Cantlin", 20, 13, bg=5, face=3)
    M.addSoftTrigger(61, 12, "Cantlin", 20, 12, bg=5, face=3)
    M.addSoftTrigger(60, 11, "Cantlin", 19, 11, bg=5, face=2)
    M.addSoftTrigger(59, 11, "Cantlin", 18, 11, bg=5, face=2)
    M.addSoftTrigger(58, 11, "Cantlin", 17, 11, bg=5, face=2)
    M.addSoftTrigger(57, 11, "Cantlin", 16, 11, bg=5, face=2)
    M.addSoftTrigger(53, 11, "Cantlin", 12, 11, bg=5, face=2)

    M.addDoor(Door(27, 10, "CNT_1"))
    M.addDoor(Door(5, 22, "CNT_2"))
    M.addDoor(Door(9, 26, "CNT_3"))
    M.addDoor(Door(15, 26, "CNT_4"))
    M.addDoor(Door(16, 26, "CNT_5"))
    M.addChest(Chest(3, 28, "CNT_6", contents=None)) #impossible to reach chests
    M.addChest(Chest(28, 26, "CNT_7", contents=None))
    M.addChest(Chest(28, 28, "CNT_8", contents=None))

    M.addNPC(NPC(M, 9, 4, 0, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome to the traveler's Inn.  Room and board is 100 GOLD per night.  Dost though want a room?", query=Query(width=4, height=3, options=["Yes", "No"], responses=[TextNode("Good night."), TextNode("Okay.  \tGood-bye, traveler.")], query_type="Inn", query_inn_price=100, cancel_response=TextNode("Okay.  \tGood-bye, traveler.")))))
    M.addNPC(NPC(M, 16, 7, 0, "Gray Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Welcome to Cantlin, the castle town.")))
    M.addNPC(NPC(M, 11, 14, 0, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("I know nothing.")))
    M.addNPC(NPC(M, 24, 10, 0, "Gray Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("It it said that many have held Erdrick's armor.", next=TextNode("The last to have it was a fellow named Wynn."))))
    M.addNPC(NPC(M, 7, 17, 0, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("What shall I get for thy dinner?")))
    M.addNPC(NPC(M, 57, 17, 0, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("To learn how proof may be obtained that thy ancestor was tje great Erdrick, see a man in this very town.")))
    M.addNPC(NPC(M, 15, 29, 0, "Old Man", sizex, sizey, 2, can_move=True, basetext=TextNode("Let us wish the warrior well!", next=TextNode("May the light be thy strength!", next=TextNode("Thou may go search.", next=TextNode("From Tantegel Castle travel 70 leagues to the south and 40 to the east"))))))
    M.addNPC(NPC(M, 26, 18, 0, "Merchant", sizex, sizey, 2, can_move=True, basetext=TextNode("Grandfather used to say that his friend, Wynn, had buried something of great value at the foot of a tree behind his shop.")))
    M.addNPC(NPC(M, 21, 19, 0, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("I'm Nester. \tHey, where am I? No, don't tell me!")))
    M.addNPC(NPC(M, 23, 5, 1, "Merchant", sizex, sizey, 2, can_move=False,
                 basetext=TextNode("We deal in weapons and armor.  \tDost thou wish to buy anything today?",
                                   query=Query(options=["Yes", "No"],
                                               responses=[TextNode("What dost thou wish to buy?",
                                                                   query=Query(
                                                                       options=[Item("Bamboo Pole", 10, "Weapon"),
                                                                                Item("Club", 60, "Weapon"),
                                                                                Item("Copper Sword", 180, "Weapon"),
                                                                                Item("Leather Armor", 70, "Armor"),
                                                                                Item("Chain Mail", 300, "Armor"),
                                                                                Item("Large Shield", 800, "Shield")],
                                                                       responses=[],
                                                                       cancel_response=TextNode("Please, come again."),
                                                                       query_type="Shop",
                                                                       width=9,
                                                                       height=7)),
                                                          TextNode("Please, come again.")],
                                               cancel_response=TextNode("Please, come again.")))))
    M.addNPC(NPC(M, 3, 8, 3, "Woman", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", False)],basetext=TextNode("Welcome. \tWe deal in tools.  What can I do for thee?",
                                                                                              query=Query(options=["BUY", "SELL"],
                                                                                                          responses=[TextNode("What dost thou want?",
                                                                                                                              query=Query(options=[Item("Herb", 24, "Item"),
                                                                                                                                                   Item("Torch", 8, "Item")],
                                                                                                                                          responses=[],
                                                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                          width=9,
                                                                                                                                          height=3,
                                                                                                                                          query_type="ItemShop")),
                                                                                                                     TextNode("What art thou selling?", query=Query(options=[],
                                                                                                                                                                    responses=[],
                                                                                                                                                                    cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                                                    query_type="Sell",
                                                                                                                                                                    width=9,
                                                                                                                                                                    height=None
                                                                                                                                                                    ))],
                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                          width=4,
                                                                                                          height=3
                                                                                                          ))))
    M.addNPC(NPC(M, 3, 8, 3, "Woman", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 3, 8, 3, "Woman", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", False)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 3, 8, 3, "Woman", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))


    M.addNPC(NPC(M, 3, 13, 3, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Come buy my radishes! They are fresh and cheap. \tBuy thy radishes today!")))
    M.addNPC(NPC(M, 3, 8, 3, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", False)], basetext=TextNode("Welcome. \tWe deal in tools.  What can I do for thee?",
                                                                                              query=Query(options=["BUY", "SELL"],
                                                                                                          responses=[TextNode("What dost thou want?",
                                                                                                                              query=Query(options=[Item("Dragon's Scale", 20, "Item"),
                                                                                                                                                   Item("Wings", 70, "Item")],
                                                                                                                                          responses=[],
                                                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                          width=9,
                                                                                                                                          height=3,
                                                                                                                                          query_type="ItemShop")),
                                                                                                                     TextNode("What art thou selling?", query=Query(options=[],
                                                                                                                                                                    responses=[],
                                                                                                                                                                    cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                                                    query_type="Sell",
                                                                                                                                                                    width=9,
                                                                                                                                                                    height=None
                                                                                                                                                                    ))],
                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                          width=4,
                                                                                                          height=3
                                                                                                          ))))
    M.addNPC(NPC(M, 3, 8, 3, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 3, 8, 3, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", False)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 3, 8, 3, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 5, 27, 3, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("My grandfather Wynn once had a shop on the east side of Hauksness.")))
    again = Query(width=4, height=3, options=["YES", "NO"], query_type="Mini Shop", transaction=Transaction(Item("Magic Key", 98, "Normal")))
    again.cancel_response=TextNode("I will see thee later.")
    again.responses=[TextNode("Here, take this key.  Dost thou wish to purchase more?", query=again), TextNode("I will see thee later.")]
    M.addNPC(NPC(M, 28, 7, 0, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("Magic Keys!  \tThey will unlock any door.  \tDost thou wish to purchase one for 98 GOLD?",query=again)))
    M.addNPC(NPC(M, 25, 13, 3, "Gray Soldier", sizex, sizey, 2, can_move=False,
                 basetext=TextNode("We deal in weapons and armor.  \tDost thou wish to buy anything today?",
                                   query=Query(options=["Yes", "No"],
                                               responses=[TextNode("What dost thou wish to buy?",
                                                                   query=Query(
                                                                       options=[Item("Flame Sword", 9800, "Weapon"),
                                                                                Item("Silver Shield", 14800, "Shield")],
                                                                       responses=[],
                                                                       cancel_response=TextNode("Please, come again."),
                                                                       query_type="Shop",
                                                                       width=9,
                                                                       height=3)),
                                                          TextNode("Please, come again.")],
                                               cancel_response=TextNode("Please, come again.")))))
    again2 = Query(width=4, height=3, options=["YES", "NO"], query_type="Mini Shop", transaction=Transaction(Item("Fairy Water", 38, "Normal")))
    again2.cancel_response=TextNode("All the best to thee")
    again2.responses=[TextNode("I thank thee",next=TextNode("Won't thou buy one more bottle?", query=again2)),TextNode("All the best to thee.")]
    M.addNPC(NPC(M, 23, 14, 1, "Young Lady", sizex, sizey, 2, can_move=False, basetext=TextNode("Will thou buy some Fairy Water for 38 GOLD to keep the Dragonlord's minions away?",query=again2)))
    M.addNPC(NPC(M, 28, 27, 1, "Merchant", sizex, sizey, 2, can_move=False,
                 basetext=TextNode("We deal in weapons and armor.  \tDost thou wish to buy anything today?",
                                   query=Query(options=["Yes", "No"],
                                               responses=[TextNode("What dost thou wish to buy?",
                                                                   query=Query(
                                                                       options=[Item("Hand Axe", 560, "Weapon"),
                                                                                Item("Broad Sword", 1500, "Weapon"),
                                                                                Item("Full Plate", 3000, "Armor"),
                                                                                Item("Magic Armor", 7700, "Armor")],
                                                                       responses=[],
                                                                       cancel_response=TextNode("Please, come again."),
                                                                       query_type="Shop",
                                                                       width=9,
                                                                       height=5)),
                                                          TextNode("Please, come again.")],
                                               cancel_response=TextNode("Please, come again.")))))
    M.addNPC(NPC(M, 23, 23, 0, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("'Tis said that Erdrick's sword could cleave steel.")))

    M.background_tile = 5 #Castle Floor
    M.initial_hero_face = 0
    return M


def load_Hauksness(sizex, sizey):
    M = Map(maps.Hauksness, name="Hauksness")
    M.is_dungeon = False

    M.setBoundingBoxTrigger(1, 1, 21, 21, "World", 27, 91, music_id = 4)
    M.addTrigger(43, 11, "World", 27, 91)
    M.addTrigger(43, 12, "World", 27, 91)
    M.addTrigger(59, 1, "World", 27, 91)
    M.addTrigger(60, 1, "World", 27, 91)
    M.secret_stairs.append(Trigger(20, 20, "Hauksness", 44, 11, music_id = 3))
    M.hidden_items.append(HiddenItem("Erdrick's Armor", 20, 14))

    M.addNPC(NPC(M, 45, 3, 0, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("There is a ring in this town that can help thee grow stronger.")))
    M.addNPC(NPC(M, 45, 10, 0, "Woman", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome to Hauksness.  I think.  I'm not sure anymore.")))
    M.addNPC(NPC(M, 48, 8, 0, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("I am worried.  The Dragonlord's minions may strike at any moment.")))
    M.addNPC(NPC(M, 62, 17, 1, "Merchant", sizex, sizey, 2, can_move=False,
                 basetext=TextNode("We deal in weapons and armor.  \tDost thou wish to buy anything today?",
                                   query=Query(options=["Yes", "No"],
                                               responses=[TextNode("What dost thou wish to buy?",
                                                                   query=Query(
                                                                       options=[Item("Rusty Shield", 12500, "Shield"),
                                                                                Item("Shield of Brass", 25000, "Shield"),
                                                                                Item("Circular Defendy Pot", 57200, "Shield"),
                                                                                Item("Erdrick's Shield", 45800, "Shield"),
                                                                                Item("Silver Shield", 12800, "Shield"),
                                                                                Item("Ring of Radiance", 65500, "Weapon")],
                                                                       responses=[],
                                                                       cancel_response=TextNode("Please, come again."),
                                                                       query_type="Shop",
                                                                       width=9,
                                                                       height=7)),
                                                          TextNode("Please, come again.")],
                                               cancel_response=TextNode("Please, come again.")))))

    M.addMonsters(monster_list=["Starwyvern", "Starwyvern", "Werewolf", "Wizard", "Green Dragon"], bounding_box=(1, 1, 21, 21))

    M.background_tile = 15 #Sand
    M.initial_hero_face = 3
    return M

def load_Erdricks_Cave(sizex, sizey):
    M = Map(maps.Erdricks_Cave, name="Erdrick's Cave")
    M.is_dungeon = True
    M.is_dark = True
    M.outsidex = 30
    M.outsidey = 14

    M.addTrigger(2, 2, "World", 30, 14, music_id = 4)
    M.addTrigger(11, 11, "Erdricks Cave", 30, 11, music_id = 6)
    M.addTrigger(30, 11, "Erdricks Cave", 11, 11, music_id = 5)
    M.background_tile = 22 #Wall
    M.addChest(Chest(31, 5, "EDC_1", contents=Item("Tablet")))
    M.initial_hero_face = 0
    return M

def load_Swamp_Cave(sizex, sizey):
    M = Map(maps.Swamp_Cave, name="Swamp Cave")
    M.is_dungeon = True
    M.is_dark = True
    M.outsidex = 106
    M.outsidey = 46
    M.addTrigger(2, 2, "World", 106, 46, music_id = 4)
    M.addTrigger(2, 31, "World", 106, 51, music_id = 4)

    M.addDoor(Door(7, 22, "SWC_1"))

    rescuequery = Query(width=4, height=3, options=["Yes", "No"])
    rescuequery.responses=[TextNode("Princess Gwaelin embraces thee.", quoted=False, next=TextNode("I'm so happy!")), TextNode("But thou must.", next=TextNode("Will thou take me to the castle?", query=rescuequery))]
    rescuequery.cancel_response=TextNode("But thou must.", next=TextNode("Will thou take me to the castle?", query=rescuequery))
    M.addNPC(NPC(M, 7, 20, 0, "Kidnapped Princess", sizex, sizey, 2, can_move=False, name="RPR_1", special_action="Disappear", basetext=TextNode("Thou art brave indeed to rescue me, $hero_name$.", next=TextNode("I am Gwaelin, daughter of Lorik.", next=TextNode("Will thou take me to the castle?", query=rescuequery)))))

    M.addMonsters(monster_list=["Druin", "Druin", "Ghost", "Magician", "Scorpion"], bounding_box=(0, 0, 9, 33))

    M.background_tile = 22 #Wall
    M.initial_hero_face = 0
    return M

def load_Garinham(sizex, sizey):
    M = Map(maps.Garinham)
    M.is_dungeon = False

    M.setBoundingBoxTrigger(1, 1, 21, 21, "World", 4, 4, music_id = 4)

    M.addSoftTrigger(19, 11, "Garinham", 75, 11, bg=0, face=2)
    M.addSoftTrigger(61, 4, "Garinham", 5, 4, bg=9, face=2)

    M.addSoftTrigger(75, 12, "Garinham", 19, 12, bg=9, face=0)
    M.addSoftTrigger(5, 5, "Garinham", 61, 5, bg=0, face=0)

    M.addTrigger(21, 2, "Grave of Garinham", 8, 13)

    M.addChest(Chest(66, 7, "GHM_1", contents=Item("Gold", cost=[10, 17])))
    M.addChest(Chest(67, 7, "GHM_2", contents=Item("Torch")))
    M.addChest(Chest(66, 8, "GHM_3", contents=Item("Herb")))
    M.addDoor(Door(19, 12, "GHM_4"))
    M.addDoor(Door(62, 8, "GHM_5"))

    M.addNPC(NPC(M, 9, 19, 0, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("I have heard one named Nester. \tDost thou know such a one?")))
    M.addNPC(NPC(M, 4, 12, 0, "Old Man", sizex, sizey, 2, can_move=True, basetext=TextNode("Garin, a wandering minstrel of legendary fame, is said to have built this town.")))
    M.addNPC(NPC(M, 4, 19, 3, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("Many believe that Princess Gwaelin is hidden away in a cave.")))
    M.addNPC(NPC(M, 12, 13, 0, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("It is said that the Princess was kidnapped and taken eastward.")))
    M.addNPC(NPC(M, 20, 13, 0, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("Welcome to Garinham.  May thy stay be a peaceful one.")))
    M.addNPC(NPC(M, 76, 9, 3, "Old Man", sizex, sizey, 2, can_move=True, basetext=TextNode("They say that Erdrick's armor was hidden long ago.")))
    M.addNPC(NPC(M, 65, 10, 2, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Once there was a town called Hauksness far to the south, but I do not know if it still exists.")))
    M.addNPC(NPC(M, 60, 9, 0, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("I hate people! \tGo! Leave me!")))
    M.addNPC(NPC(M, 61, 7, 3, "Gray Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("I'm too busy. \tAsk the other guard.")))
    M.addNPC(NPC(M, 63, 7, 1, "Gray Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("I'm too busy. \tAsk the other guard.")))
    M.addNPC(NPC(M, 67, 8, 0, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("I suggest making a map if thy path leads into the darkness.")))
    M.addNPC(NPC(M, 16, 3, 0, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("The harp attracts enemies. \tStay away from the grave in Garinham.")))
    M.addNPC(NPC(M, 19, 17, 1, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome to the traveler's Inn.  Room and board is 25 GOLD per night.  Dost though want a room?", query=Query(width=4, height=3, options=["Yes", "No"], responses=[TextNode("Good night."), TextNode("Okay.  \tGood-bye, traveler.")], query_type="Inn", query_inn_price=25, cancel_response=TextNode("Okay.  \tGood-bye, traveler.")))))
    M.addNPC(NPC(M, 12, 20, 2, "Merchant", sizex, sizey, 2, can_move=False,
                 basetext=TextNode("We deal in weapons and armor.  \tDost thou wish to buy anything today?",
                                   query=Query(options=["Yes", "No"],
                                               responses=[TextNode("What dost thou wish to buy?",
                                                                   query=Query(
                                                                       options=[Item("Club", 60, "Weapon"),
                                                                                Item("Copper Sword", 180, "Weapon"),
                                                                                Item("Hand Axe", 560, "Weapon"),
                                                                                Item("Leather Armor", 70, "Armor"),
                                                                                Item("Chain Mail", 300, "Armor"),
                                                                                Item("Half Plate", 1000, "Armor"),
                                                                                Item("Large Shield", 800, "Shield"),],
                                                                       responses=[],
                                                                       cancel_response=TextNode("Please, come again."),
                                                                       query_type="Shop",
                                                                       width=9,
                                                                       height=8)),
                                                          TextNode("Please, come again.")],
                                               cancel_response=TextNode("Please, come again.")))))
    M.addNPC(NPC(M, 7, 13, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", False)], basetext=TextNode("Welcome. \tWe deal in tools.  What can I do for thee?",
                                                                                              query=Query(options=["BUY", "SELL"],
                                                                                                          responses=[TextNode("What dost thou want?",
                                                                                                                              query=Query(options=[Item("Herb", 24, "Item"),
                                                                                                                                                   Item("Torch", 8, "Item"),
                                                                                                                                                   Item("Dragon's Scale", 20, "Item")],
                                                                                                                                          responses=[],
                                                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                          width=9,
                                                                                                                                          height=4,
                                                                                                                                          query_type="ItemShop")),
                                                                                                                     TextNode("What art thou selling?", query=Query(options=[],
                                                                                                                                                                    responses=[],
                                                                                                                                                                    cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                                                    query_type="Sell",
                                                                                                                                                                    width=9,
                                                                                                                                                                    height=None
                                                                                                                                                                    ))],
                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                          width=4,
                                                                                                          height=3
                                                                                                          ))))
    M.addNPC(NPC(M, 7, 13, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", False)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 7, 13, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 7, 13, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))

    M.background_tile = 9  # Grass
    M.initial_hero_face = 1
    return M

def load_Grave_of_Garinham(sizex, sizey):
    M = Map(maps.Grave_of_Garinham, name="Grave of Garinham")
    M.is_dungeon = True
    M.is_dark = True
    M.outsidex = 4
    M.outsidey = 4

    M.addTrigger(8, 13, "Garinham", 21, 2)

    M.addTrigger(3, 20, "Grave of Garinham", 43, 4)
    M.addTrigger(43, 4, "Grave of Garinham", 3, 20)

    M.addTrigger(44, 3, "Grave of Garinham", 20, 32)
    M.addTrigger(20, 32, "Grave of Garinham", 44, 3)

    M.addTrigger(33, 3, "Grave of Garinham", 16, 32)
    M.addTrigger(16, 32, "Grave of Garinham",33, 3)

    M.addTrigger(33, 12, "Grave of Garinham", 4, 48)
    M.addTrigger(4, 48, "Grave of Garinham", 33, 12)

    M.addTrigger(44, 12, "Grave of Garinham", 20, 44)
    M.addTrigger(20, 44, "Grave of Garinham", 44, 12)

    M.addTrigger(37, 8, "Grave of Garinham", 8, 42)
    M.addTrigger(8, 42, "Grave of Garinham", 37, 8)

    M.addTrigger(11, 36, "Grave of Garinham", 32, 35)
    M.addTrigger(32, 35, "Grave of Garinham", 11, 36)

    M.addTrigger(37, 35, "Grave of Garinham", 12, 40)
    M.addTrigger(12, 40, "Grave of Garinham", 37, 35)

    M.addChest(Chest(13, 2, "GOG_1", contents=Item("Herb")))
    M.addChest(Chest(14, 2, "GOG_2", contents=Item("Gold", cost=[5, 20])))
    M.addChest(Chest(15, 2, "GOG_3", contents=Item("Gold", cost=[6, 13])))
    M.addChest(Chest(3, 32, "GOG_4", contents=Item("Cursed Belt", type="Cursed")))
    M.addChest(Chest(15, 37, "GOG_5", contents=Item("Silver Harp")))

    M.addDoor(Door(19, 19, "GOG_6"))

    M.addMonsters(monster_list=["Warlock", "Drakeema", "Skeleton", "Droll", "Poltergeist"], bounding_box=(2, 2, 20, 20))

    M.addMonsters(monster_list=["Warlock", "Specter", "Wolflord", "Druinlord", "Drollmagi"], bounding_box=(2, 32, 14, 14))

    M.addMonsters(monster_list=["Warlock", "Metal Scorpion", "Skeleton", "Wolf", "Wolf"], bounding_box=(2, 31, 40, 20))

    M.background_tile = 22  # Wall
    M.initial_hero_face = 3

    return M

def load_Kol(sizex, sizey):
    M = Map(maps.Kol)
    M.is_dungeon = False

    M.setBoundingBoxTrigger(1, 1, 25, 25, "World", 106, 12, music_id = 4)

    M.hidden_items.append(HiddenItem("Faerie Flute", 11, 8))

    M.addChest(Chest(17, 22, "KOL_1", contents=None)) #unobtainable chests
    M.addChest(Chest(17, 23, "KOL_2", contents=None))
    M.addChest(Chest(17, 24, "KOL_3", contents=None))
    M.addDoor(Door(9, 14, "KOL_4"))
    M.addDoor(Door(3, 16, "KOL_5"))


    M.addNPC(NPC(M, 22, 22, 0, "Old Man", sizex, sizey, 2, can_move=True, basetext=TextNode("This is the village of Kol.")))
    M.addNPC(NPC(M, 11, 16, 0, "Young Lady", sizex, sizey, 2, can_move=True, basetext=TextNode("Please, save us from the minions of the Dragonlord.")))
    M.addNPC(NPC(M, 18, 16, 1, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Dreadful is the South Island.", next=TextNode("Great strength and skill and wit only will bring thee back from that place."))))
    M.addNPC(NPC(M, 22, 15, 1, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("East of Hauksness there is a town, 'tis said, where one may purchase weapons of extraordinary quality.")))
    M.addNPC(NPC(M, 24, 14, 1, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("We deal in weapons and armor.  Dost thou wish to buy anything today?",
                                                                             query=Query(options=["Yes", "No"],
                                                                                         responses=[TextNode("What dost thou wish to buy?",
                                                                                                             query=Query(options=[Item("Copper Sword", 180, "Weapon"),
                                                                                                                                  Item("Hand Axe", 560, "Weapon"),
                                                                                                                                  Item("Half Plate", 1000, "Armor"),
                                                                                                                                  Item("Full Plate", 3000, "Armor"),
                                                                                                                                  Item("Small Shield", 80, "Shield")],
                                                                                                                         responses=[],
                                                                                                                         cancel_response=TextNode("Please, come again."),
                                                                                                                         query_type = "Shop",
                                                                                                                         width=9,
                                                                                                                         height=6)),
                                                                                                    TextNode("Please, come again.")], cancel_response=TextNode("Please, come again.")))))
    M.addNPC(NPC(M, 11, 11, 1, "Gray Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Golem is afraid of the music of the flute, so 'tis said.")))
    M.addNPC(NPC(M, 9, 8, 1, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Hast thou seen Nester?  \tI think he may need help.")))
    M.addNPC(NPC(M, 23, 11, 2, "Old Man", sizex, sizey, 2, can_move=True, basetext=TextNode("In legends it is said that fairies know how to put Golem to sleep.")))
    M.addNPC(NPC(M, 14, 2, 0, "Young Lady", sizex, sizey, 2, can_move=False, basetext=TextNode("This bath cures rheumatism.")))
    M.addNPC(NPC(M, 21, 6, 2, "Merchant", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome to the traveler's Inn.  Room and board is 20 GOLD per night.  Dost though want a room?", query=Query(width=4, height=3, options=["Yes", "No"], responses=[TextNode("Good night."), TextNode("Okay.  \tGood-bye, traveler.")], query_type="Inn", query_inn_price=20, cancel_response=TextNode("Okay.  \tGood-bye, traveler.")))))
    M.addNPC(NPC(M, 3, 3, 0, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("Finally thou hast obtained it, $hero_name$."), conditions=[Condition("Erdrick's Sword", required=True)]))
    M.addNPC(NPC(M, 3, 3, 0, "Old Man", sizex, sizey, 2, can_move=False, basetext=TextNode("Though thou art as brave as thy ancestor, $hero_name$, thou cannot defeat the great Dragonlord with such weapons. Thou shouldst come here again."), conditions=[Condition("Erdrick's Sword", required=False)]))
    M.addNPC(NPC(M, 4, 19, 3, "Woman", sizex, sizey, 2, can_move=True, basetext=TextNode("Art thou the descendant of Erdrick? \tHast though any proof?")))
    M.addNPC(NPC(M, 5, 22, 2, "Merchant", sizex, sizey, 2, can_move=True, basetext=TextNode("Hast thou been to the southern island?", query=Query(options=["Yes", "No"],responses=[TextNode("Idk."), TextNode("To the south, I believe, there is a town called Rimuldar.")], cancel_response=TextNode("To the south, I believe, there is a town called Rimuldar.")))))
    M.addNPC(NPC(M, 3, 25, 0, "Gray Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("Rimuldar is the place to buy keys.")))
    M.addNPC(NPC(M, 16, 23, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", False)], basetext=TextNode("Welcome. \tWe deal in tools.  What can I do for thee?",
                                                                                              query=Query(options=["BUY", "SELL"],
                                                                                                          responses=[TextNode("What dost thou want?",
                                                                                                                              query=Query(options=[Item("Herb", 24, "Item"),
                                                                                                                                                   Item("Torch", 8, "Item"),
                                                                                                                                                   Item("Dragon's Scale", 20, "Item"),
                                                                                                                                                   Item("Wings", 70, "Item")],
                                                                                                                                          responses=[],
                                                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                          width=9,
                                                                                                                                          height=5,
                                                                                                                                          query_type="ItemShop")),
                                                                                                                     TextNode("What art thou selling?", query=Query(options=[],
                                                                                                                                                                    responses=[],
                                                                                                                                                                    cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                                                                                    query_type="Sell",
                                                                                                                                                                    width=9,
                                                                                                                                                                    height=None
                                                                                                                                                                    ))],
                                                                                                          cancel_response=TextNode("I will be waiting for thy next visit."),
                                                                                                          width=4,
                                                                                                          height=3
                                                                                                          ))))
    M.addNPC(NPC(M, 16, 23, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", False), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 16, 23, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", False)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))
    M.addNPC(NPC(M, 16, 23, 1, "Merchant", sizex, sizey, 2, can_move=False, data_conditions = [DataCondition("CursedBelt", True), DataCondition("DeathNecklace", True)], basetext=TextNode("I am sorry. \nA curse is upon thy body.")))

    M.background_tile = 21  # Trees
    M.initial_hero_face = 2

    return M


def load_Rock_Mountain_Cave(sizex, sizey):
    M = Map(maps.Rock_Mountain_Cave, name="Rock Mountain Cave")
    M.is_dungeon = True
    M.is_dark = True
    M.outsidex = 31
    M.outsidey = 59

    M.addTrigger(2, 9, "World", 31, 59)

    M.addTrigger(2, 2, "Rock Mountain Cave", 29, 2)
    M.addTrigger(29, 2, "Rock Mountain Cave", 2, 2)

    M.addTrigger(8, 7, "Rock Mountain Cave", 35, 7)
    M.addTrigger(35, 7, "Rock Mountain Cave", 8, 7)

    M.addTrigger(14, 14, "Rock Mountain Cave", 41, 14)
    M.addTrigger(41, 14, "Rock Mountain Cave", 14, 14)

    M.addChest(Chest(15, 7, "RMC_1", contents=Item("Herb", cost=24)))
    M.addChest(Chest(31, 4, "RMC_2", contents=Item("Fighter's Ring")))
    M.addChest(Chest(32, 4, "RMC_3", contents=Item("Torch", cost=24)))
    M.addChest(Chest(30, 8, "RMC_4", contents=Item("Gold", cost=[100, 127], option_odds=(1/2.0), option_item = Item("Death Necklace", cost=2400, type="Cursed"))))
    M.addChest(Chest(39, 11, "RMC_5", contents=Item("Gold", cost=[10, 17])))

    M.addMonsters(monster_list=["Druin", "Druin", "Ghost", "Magician", "Scorpion"], bounding_box=(2, 2, 14, 14))

    M.addMonsters(monster_list=["Warlock", "Drakeema", "Skeleton", "Droll", "Poltergeist"], bounding_box=(29, 2, 14, 14))

    M.background_tile = 22  # Wall
    M.initial_hero_face = 3
    return M

def load_Southern_Shrine(sizex, sizey):
    M = Map(maps.Southern_Shrine, name="Southern Shrine")
    M.is_dungeon = True
    M.outsidex = 110
    M.outsidey = 111

    M.addTrigger(2, 6, "World", 110, 111)

    M.addChest(Chest(7, 7, "SRS_1", contents=Item("Rainbow Drop", type="Special")))
    M.addNPC(NPC(M, 6, 7, 1, "Old Man", sizex, sizey, 2, name="SRS_2", can_move=False, special_action="Disappear", conditions=[Condition(item_name="Rainbow Drop", required=False), MultiCondition(item_names=["Erdrick's Token", "Stones of Sunlight", "Staff of Rain"], required=True)], basetext=TextNode("Now the sun and rain shall meet and the Rainbow Drop passes to thy keeping.")))
    M.addNPC(NPC(M, 6, 7, 1, "Old Man", sizex, sizey, 2, name="SRS_2", can_move=False, special_action="Eviction", conditions=[MultiCondition(item_names=["Erdrick's Token", "Stones of Sunlight", "Staff of Rain"], required=False)],basetext=TextNode("In thy task thou hast failed.  Alas, I fear thou art not the one Erdrick predicted would save us.", next=TextNode("Go now!"))))

    M.background_tile = 22  # Wall
    M.initial_hero_face = 3
    return M


def load_Northern_Shrine(sizex, sizey):
    M = Map(maps.Northern_Shrine, name="Northern Shrine")
    M.is_dungeon = True
    M.outsidex = 83
    M.outsidey = 3

    M.addTrigger(6, 11, "World", 83, 3)

    M.addChest(Chest(5, 6, "NRS_1", contents=Item("Staff of Rain", type="Special")))
    M.addNPC(NPC(M, 6, 6, 3, "Old Man", sizex, sizey, 2, name="NRS_2", can_move=False, special_action="Disappear", conditions=[Condition(item_name="Staff of Rain", required=False), Condition(item_name="Silver Harp", required=True)], basetext=TextNode("Thou hast brought the harp.  Good.", next=TextNode("Take the treasure chest."))))
    M.addNPC(NPC(M, 6, 6, 3, "Old Man", sizex, sizey, 2, name="NRS_2", can_move=False, conditions=[Condition(item_name="Staff of Rain", required=False), Condition(item_name="Silver Harp", required=False)], basetext=TextNode("Thy bravery must be proven.", next=TextNode("Thus, I propose a test.", next=TextNode("There is a Silver Harp that beckons to the creatures of the Dragonlord.", next=TextNode("Bring this to me and I will reward thee with a Staff of Rain."))))))


    M.background_tile = 22  # Wall
    M.initial_hero_face = 2
    return M

def load_Charlock_Castle(sizex, sizey):
    M = Map(maps.Charlock_Castle, name="Charlock Castle")
    M.is_dungeon = True
    M.is_dark = False
    M.outsidex = 50
    M.outsidey = 50

    M.addTrigger(11, 22, "World", 50, 50)
    M.addTrigger(12, 22, "World", 50, 50)

    M.secret_stairs.append(Trigger(12, 3, "Charlock Dungeon", 11, 2))

    M.addTrigger(6, 16, "Charlock Dungeon", 10, 15)
    M.addTrigger(17, 16, "Charlock Dungeon", 19, 17)

    M.addDoor(Door(17, 10, "CCC_1"))
    M.addDoor(Door(6, 10, "CCC_2"))

    M.addMonsters(monster_list=["Werewolf", "Green Dragon", "Starwyvern", "Wizard", "Axe Knight"], bounding_box=(2, 2, 20, 20))

    M.background_tile = 18  # Swamp
    M.initial_hero_face = 2
    return M

def load_Charlock_Dungeon(sizex, sizey):
    M = Map(maps.Charlock_Dungeon, name="Charlock")
    M.is_dungeon = True
    M.is_dark = True
    M.outsidex = 50
    M.outsidey = 50

    M.addTrigger(11, 2, "Charlock Castle", 12, 3)

    M.addTrigger(10, 15, "Charlock Castle", 6, 16)
    M.addTrigger(19, 17, "Charlock Castle", 17, 16)

    M.addTrigger(4, 6, "Charlock Dungeon", 32, 2)
    M.addTrigger(32, 2, "Charlock Dungeon", 4, 6)

    M.addTrigger(4, 16, "Charlock Dungeon", 32, 3)
    M.addTrigger(32, 3, "Charlock Dungeon", 4, 16)

    M.addTrigger(16, 11, "Charlock Dungeon", 40, 11)
    M.addTrigger(40, 11, "Charlock Dungeon", 16, 11)

    M.addTrigger(21, 9, "Charlock Dungeon", 41, 10)
    M.addTrigger(41, 10, "Charlock Dungeon", 21, 9)

    M.addTrigger(10, 21, "Charlock Dungeon", 37, 2)
    M.addTrigger(37, 2, "Charlock Dungeon", 10, 21)

    M.addTrigger(35, 2, "Charlock Dungeon", 59, 2)
    M.addTrigger(59, 2, "Charlock Dungeon", 35, 2)

    M.addTrigger(57, 6, "Charlock Dungeon", 32, 10)
    M.addTrigger(32, 10, "Charlock Dungeon", 57, 6)

    M.addTrigger(52, 11, "Charlock Dungeon", 33, 11)
    M.addTrigger(33, 11, "Charlock Dungeon", 52, 11)

    M.addTrigger(53, 8, "Charlock Dungeon", 2, 41)
    M.addTrigger(2, 41, "Charlock Dungeon", 53, 8)

    M.addTrigger(9, 39, "Charlock Dungeon", 59, 9)
    M.addTrigger(59, 9, "Charlock Dungeon", 9, 39)

    M.addTrigger(54, 4, "Charlock Dungeon", 41, 3)
    M.addTrigger(41, 3, "Charlock Dungeon", 54, 4)

    M.addTrigger(40, 2, "Charlock Dungeon", 17, 3)
    M.addTrigger(17, 3, "Charlock Dungeon", 40, 2)

    M.addTrigger(15, 9, "Charlock Dungeon", 36, 6)
    M.addTrigger(36, 6, "Charlock Dungeon", 15, 9)

    M.addTrigger(10, 33, "Charlock Dungeon", 26, 32)
    M.addTrigger(26, 32, "Charlock Dungeon", 10, 33)

    M.addTrigger(42, 32, "Charlock Dungeon", 27, 37)
    M.addTrigger(27, 37, "Charlock Dungeon", 42, 32)

    M.addTrigger(51, 32, "Charlock Dungeon", 42, 32)  #neverending stair repeat

    M.addTrigger(4, 34, "Charlock Dungeon", 31, 32)
    M.addTrigger(31, 32, "Charlock Dungeon", 4, 34)

    M.addTrigger(22, 32, "Charlock Dungeon", 42, 38)
    M.addTrigger(42, 38, "Charlock Dungeon", 22, 32)

    M.addTrigger(51, 38, "Charlock Cellar", 11, 30)

    M.addChest(Chest(37, 7, "CDD_1", contents=Item("Erdrick's Sword", type="Weapon")))

    M.addMonsters(monster_list=["Werewolf", "Green Dragon", "Starwyvern", "Wizard", "Axe Knight"], bounding_box=(2, 2, 20, 20))

    M.addMonsters(monster_list=["Blue Dragon", "Blue Dragon", "Stoneman", "Axe Knight", "Wizard"], bounding_box=(32, 2, 30, 10))
    M.addMonsters(monster_list=["Blue Dragon", "Blue Dragon", "Stoneman", "Axe Knight", "Wizard"], bounding_box=(2, 32, 10, 10))

    M.addMonsters(monster_list=["Wizard", "Stoneman", "Armored Knight", "Armored Knight", "Red Dragon"], bounding_box=(21, 31, 32, 11))

    M.background_tile = 22  # Wall
    M.initial_hero_face = 0
    return M

def load_Charlock_Cellar(sizex, sizey):
    M = Map(maps.Charlock_Cellar, name="Charlock Cellar")
    M.is_dungeon = True
    M.outsidex = 50
    M.outsidey = 50

    M.addTrigger(11, 30, "Charlock Dungeon", 51, 38)

    M.addChest(Chest(12, 12, "CDC_1", contents=Item("Herb", cost=24)))
    M.addChest(Chest(12, 13, "CDC_2", contents=Item("Gold", cost=[500, 755])))
    M.addChest(Chest(12, 14, "CDC_3", contents=Item("Wings", cost=70)))
    M.addChest(Chest(13, 13, "CDC_4", contents=Item("Magic Key", cost=53)))
    M.addChest(Chest(13, 14, "CDC_5", contents=Item("Cursed Belt", cost=360, type="Item")))
    M.addChest(Chest(14, 14, "CDC_6", contents=Item("Herb", cost=24)))
    M.addDoor(Door(18, 13, "CDC_7"))

    M.addNPC(NPC(M, 17, 25, 0, "Dragonlord", sizex, sizey, 2, can_move=False, data_conditions=[DataCondition("DLDEAD", False)], basetext=TextNode("Welcome, $hero_name$. \tI am the Dragonlord--King of Kings.", next=TextNode("I have been waiting long for one such as thee.", next=TextNode("I give thee now a chance to share this world and to rule half of it if thou will now stand beside me.", next=TextNode("What sayest thou? Will the great warrior stand with me?", query=Query(options=["YES", "NO"],query_type="dragonlord1",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           responses=[TextNode("Really?", query=Query(options=["YES", "NO"],query_type="dragonlord2",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          responses=[TextNode("Then half of this world is thine, half of the darkness, and...", next=TextNode("If thou dies I can bring thee back for another attempt without loss of thy deeds to date.", next=TextNode("Thy journey is over.  Take now a long, long rest. \tHahahaha..."))),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 TextNode("Thou art a fool!")],
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      cancel_response=TextNode("Thou art a fool!"))),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      TextNode("Thou art a fool!")],
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           cancel_response=TextNode("Thou art a fool!"))))))))

    M.addMonsters(monster_list=["Wizard", "Stoneman", "Armored Knight", "Armored Knight", "Red Dragon"], bounding_box=(2, 2, 29, 29))

    M.background_tile = 23  # Water
    M.initial_hero_face = 2
    return M


def load_Charlock_Bonus(sizex, sizey):
    M = Map(maps.Charlock_Bonus, name="Charlock")
    M.is_dungeon = True
    M.is_dark = True
    M.outsidex = 50
    M.outsidey = 50

    M.addTrigger(27, 4, "Charlock Bonus", 58, 3)
    M.addTrigger(58, 3, "Charlock Bonus", 27, 4)

    M.addTrigger(58, 29, "Charlock Bonus", 16, 56)
    M.addTrigger(16, 56, "Charlock Bonus", 58, 29)

    M.addTrigger(29, 56, "Charlock Bonus", 69, 56)
    M.addTrigger(69, 56, "Charlock Bonus", 29, 56)

    M.addNPC(NPC(M, 57, 5, 3, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("Welcome to Curealia.")))
    M.addNPC(NPC(M, 59, 5, 1, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("Long live Lord Tanza!")))
    M.addNPC(NPC(M, 53, 26, 0, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("These waters grant life everlasting.")))
    M.addNPC(NPC(M, 63, 25, 0, "Red Soldier", sizex, sizey, 2, can_move=True, basetext=TextNode("Hast thou had any of the water?", query=Query(options=["YES", "NO"], responses=[TextNode("It is very delicious!"), TextNode("The water here is blessed by Lord Tanza.", next=TextNode("It is said that Lord Tanza can grant thee immortality."))], cancel_response=TextNode("The water here is blessed by Lord Tanza.", next=TextNode("It is said that Lord Tanza can grant thee immortality."))))))
    M.addNPC(NPC(M, 46, 20, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("I came from Hauksness after the minions of the Dragonlord destroyed the town...", next=TextNode("As I was about to fall, Lord Tanza brought me to this paradise and saved me.", next=TextNode("Hail Lord Tanza!")))))
    M.addNPC(NPC(M, 70, 20, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("The Dragonlord is powerful indeed to have brought darkness unto the land.", next=TextNode("But Lord Tanza is a God!"))))
    M.addNPC(NPC(M, 11, 54, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("I'm late for a meeting with Lord Tanza.", next=TextNode("But I can never remember which way to go..."))))
    M.addNPC(NPC(M, 56, 53, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("I cannot let thee pass.  I will kill thee if thee try.")))
    M.addNPC(NPC(M, 60, 53, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("I cannot let thee pass.  I will kill thee if thee try.")))
    M.addNPC(NPC(M, 56, 49, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("Halt!  Only thine who hath been summoned may see Lord Tanza.")))
    M.addNPC(NPC(M, 60, 49, 0, "Red Soldier", sizex, sizey, 2, can_move=False, basetext=TextNode("Halt!  Only thine who hath been summoned may see Lord Tanza.")))
    M.addNPC(NPC(M, 58, 46, 0, "Hero", sizex, sizey, 8, can_move=False, basetext=TextNode("You've killed my guards.  Who are you?", next=TextNode("$hero_name$, is it?  Ah, so it was you who defeated the Dragonlord.", next=TextNode("Fate eternal swirls through my veins, boy.  For I am immortal, a God, you cannot hope to destroy me.", next=TextNode("All the cosmos bow before me, the almighty.", next=TextNode("It seems your fate is near at hand.  Prepare yourself, it is time to die!")))))))


    M.background_tile = 15  # Sand
    M.initial_hero_face = 0
    return M

def load_World(sizex, sizey):
    M = Map(maps.World, name="World")
    M.addTrigger(50, 43, "Brecconary", 2, 16, music_id = 3)
    M.addTrigger(45, 45, "Tantegel", 13, 30, music_id = 2)
    M.addTrigger(4, 4, "Garinham", 21, 14, music_id = 3)
    M.addTrigger(106, 12, "Kol", 21, 25, music_id = 3)
    M.addTrigger(104, 74, "Rimuldar", 31, 16, music_id = 3)
    M.addTrigger(75, 104, "Cantlin", 16, 2, music_id = 3)
    M.addTrigger(27, 91, "Hauksness", 2, 11, music_id = 5)
    M.addTrigger(50, 50, "Charlock Castle", 12, 21, music_id = 5)

    M.addTrigger(30, 14, "Erdricks Cave", 2, 2, music_id = 5)
    M.addTrigger(106,46, "Swamp Cave", 2, 2, music_id = 5)
    M.addTrigger(106,51, "Swamp Cave", 2, 31, music_id = 5)
    M.addTrigger(31, 59, "Rock Mountain Cave", 2, 9, music_id = 5)

    M.addTrigger(110, 111, "Southern Shrine", 2, 6, music_id = 3)
    M.addTrigger(83, 3, "Northern Shrine", 6, 11, music_id = 3)

    M.hidden_items.append(HiddenItem("Erdrick's Token", 85, 115))

    #monsters - specify list of monsters and rectangle (inclusive) where they can be found
    M.addMonsters(monster_list=["Slime", "Red Slime", "Slime", "Red Slime", "Slime"], bounding_box=(32,32,30,15))

    M.addMonsters(monster_list=["Slime", "Red Slime", "Drakee", "Red Slime", "Red Slime"], bounding_box=(32, 17, 15, 15))
    M.addMonsters(monster_list=["Slime", "Red Slime", "Drakee", "Red Slime", "Red Slime"], bounding_box=(17, 32, 15, 15))
    M.addMonsters(monster_list=["Slime", "Red Slime", "Drakee", "Red Slime", "Red Slime"], bounding_box=(17, 47, 30, 15))
    M.addMonsters(monster_list=["Slime", "Red Slime", "Drakee", "Red Slime", "Red Slime"], bounding_box=(62, 32, 15, 15))

    M.addMonsters(monster_list=["Slime", "Red Slime", "Drakee", "Ghost", "Ghost"], bounding_box=(32, 2, 30, 15))
    M.addMonsters(monster_list=["Slime", "Red Slime", "Drakee", "Ghost", "Ghost"], bounding_box=(47, 17, 15, 15))
    M.addMonsters(monster_list=["Slime", "Red Slime", "Drakee", "Ghost", "Ghost"], bounding_box=(17, 17, 15, 15))

    M.addMonsters(monster_list=["Red Slime", "Red Slime", "Drakee", "Ghost", "Magician"], bounding_box=(2, 2, 30, 15))
    M.addMonsters(monster_list=["Red Slime", "Red Slime", "Drakee", "Ghost", "Magician"], bounding_box=(2, 17, 15, 15))
    M.addMonsters(monster_list=["Red Slime", "Red Slime", "Drakee", "Ghost", "Magician"], bounding_box=(62, 2, 15, 15))
    M.addMonsters(monster_list=["Red Slime", "Red Slime", "Drakee", "Ghost", "Magician"], bounding_box=(62, 17, 30, 15))
    M.addMonsters(monster_list=["Red Slime", "Red Slime", "Drakee", "Ghost", "Magician"], bounding_box=(77, 32, 15, 15))

    M.addMonsters(monster_list=["Ghost", "Magician", "Magidrakee", "Magidrakee", "Scorpion"], bounding_box=(92, 2, 15, 45))
    M.addMonsters(monster_list=["Ghost", "Magician", "Magidrakee", "Magidrakee", "Scorpion"], bounding_box=(2, 32, 15, 15))
    M.addMonsters(monster_list=["Ghost", "Magician", "Magidrakee", "Magidrakee", "Scorpion"], bounding_box=(32, 62, 15, 15))

    M.addMonsters(monster_list=["Ghost", "Magician", "Magidrakee", "Scorpion", "Skeleton"], bounding_box=(2, 47, 15, 15))
    M.addMonsters(monster_list=["Ghost", "Magician", "Magidrakee", "Scorpion", "Skeleton"], bounding_box=(2, 62, 30, 15))
    M.addMonsters(monster_list=["Ghost", "Magician", "Magidrakee", "Scorpion", "Skeleton"], bounding_box=(77, 2, 15, 15))
    M.addMonsters(monster_list=["Ghost", "Magician", "Magidrakee", "Scorpion", "Skeleton"], bounding_box=(107, 2, 45, 15))

    M.addMonsters(monster_list=["Magidrakee", "Scorpion", "Skeleton", "Warlock", "Wolf"], bounding_box=(62, 47, 60, 15))

    M.addMonsters(monster_list=["Skeleton", "Warlock", "Wolf", "Metal Scorpion", "Wolf"], bounding_box=(77, 62, 45, 15))
    M.addMonsters(monster_list=["Skeleton", "Warlock", "Wolf", "Metal Scorpion", "Wolf"], bounding_box=(107, 77, 15, 15))

    M.addMonsters(monster_list=["Metal Scorpion", "Wraith", "Goldman", "Wolflord", "Wolflord"], bounding_box=(32, 77, 15, 15))
    M.addMonsters(monster_list=["Metal Scorpion", "Wraith", "Goldman", "Wolflord", "Wolflord"], bounding_box=(92, 77, 15, 15))
    M.addMonsters(monster_list=["Metal Scorpion", "Wraith", "Goldman", "Wolflord", "Wolflord"], bounding_box=(107, 92, 15, 15))

    M.addMonsters(monster_list=["Wraith", "Wolflord", "Goldman", "Wyvern", "Wyvern"], bounding_box=(17, 77, 15, 15))
    M.addMonsters(monster_list=["Wraith", "Wolflord", "Goldman", "Wyvern", "Wyvern"], bounding_box=(92, 92, 15, 15))
    M.addMonsters(monster_list=["Wraith", "Wolflord", "Goldman", "Wyvern", "Wyvern"], bounding_box=(92, 107, 30, 15))

    M.addMonsters(monster_list=["Wyvern", "Rogue Scorpion", "Wraith Knight", "Knight", "Demon Knight"], bounding_box=(2, 77, 15, 15))
    M.addMonsters(monster_list=["Wyvern", "Rogue Scorpion", "Wraith Knight", "Knight", "Demon Knight"], bounding_box=(2, 92, 30, 15))

    M.addMonsters(monster_list=["Wraith Knight", "Knight", "Demon Knight", "Magiwyvern", "Metal Slime"], bounding_box=(32, 92, 15, 15))
    M.addMonsters(monster_list=["Wraith Knight", "Knight", "Demon Knight", "Magiwyvern", "Metal Slime"], bounding_box=(2, 107, 30, 15))

    M.addMonsters(monster_list=["Knight", "Demon Knight", "Magiwyvern", "Starwyvern", "Werewolf"], bounding_box=(47, 47, 15, 60))
    M.addMonsters(monster_list=["Knight", "Demon Knight", "Magiwyvern", "Starwyvern", "Werewolf"], bounding_box=(32, 107, 15, 15))
    M.addMonsters(monster_list=["Knight", "Demon Knight", "Magiwyvern", "Starwyvern", "Werewolf"], bounding_box=(77, 107, 15, 15))
    M.addMonsters(monster_list=["Knight", "Demon Knight", "Magiwyvern", "Starwyvern", "Werewolf"], bounding_box=(62, 77, 30, 15))

    M.addMonsters(monster_list=["Starwyvern", "Starwyvern", "Werewolf", "Wizard", "Green Dragon"], bounding_box=(62, 92, 30, 15))
    M.addMonsters(monster_list=["Starwyvern", "Starwyvern", "Werewolf", "Wizard", "Green Dragon"], bounding_box=(47, 107, 30, 15))

    M.background_tile = 23 #Water
    M.initial_hero_face = 0
    return M