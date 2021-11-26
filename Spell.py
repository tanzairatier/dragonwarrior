class Spell:
    def __init__(self, name):
        self.name = name
        if name == "HEAL":
            self.mp_cost = 4
        elif name == "HURT":
            self.mp_cost = 2
        elif name == "SLEEP":
            self.mp_cost = 2
        elif name == "RADIANT":
            self.mp_cost = 3
        elif name == "STOPSPELL":
            self.mp_cost = 2
        elif name == "OUTSIDE":
            self.mp_cost = 6
        elif name == "RETURN":
            self.mp_cost = 8
        elif name == "REPEL":
            self.mp_cost = 2
        elif name == "HEALMORE":
            self.mp_cost = 10
        elif name == "HURTMORE":
            self.mp_cost = 5
        elif name == "None":
            self.mp_cost = 0