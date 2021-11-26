class Condition:
    def __init__(self, item_name=None, required=True):
        self.item_name = item_name
        self.required = required

    def isSatisfied(self, items):
        if not self.item_name:
            return True
        else:
            for item in items:
                if item == self.item_name:
                    return self.required

            return not self.required


class DataCondition:
    def __init__(self, data, required=True):
        self.data = data
        self.required = required
    def isSatisfied(self, data):
        res = data.get(self.data, False)
        return res if self.required else not res


class MultiCondition:
    def __init__(self, item_names = [], required=True):
        self.item_names = item_names
        self.required = required

    def isSatisfied(self, items):
        if not self.item_names:
            return True
        else:
            have_all = True
            for item in self.item_names:
                if item not in items:
                    have_all = False
                    break
            return have_all if self.required else not have_all


class SituationCondition:
    def __init__(self, situation_name=None, required=True):
        self.situation_name = situation_name
        self.required = required

    def isSatisfied(self, situations):
        if self.situation_name:
            for sit in situations:
                if sit.name == self.situation_name:
                    return self.required

        return True