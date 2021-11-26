class Item:
    def __init__(self, name, cost=0, type="Normal", option_odds = 0, option_item = None):
        self.name = name
        self.cost = cost
        self.type = type
        self.option_odds = option_odds
        self.option_item = option_item