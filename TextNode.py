class TextNode:
    def __init__(self, text, next=None, quoted=True, query=None, texttype = "Normal", action=False):
        self.text = text
        self.next = next
        self.query = query
        self.texttype = texttype
        self.quoted = quoted
        self.action = action

