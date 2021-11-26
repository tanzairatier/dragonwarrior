class Query:
    def __init__(self, options=[], responses=[], width=4, height=3, cancel_response=None, query_type = "Normal", transaction=None, transaction2=None, query_inn_price=None):
        self.options = options
        self.responses = responses
        self.width = width
        self.height = height
        self.cancel_response = cancel_response
        self.query_type = query_type
        self.transaction = transaction
        self.transaction2 = transaction2
        self.query_inn_price = query_inn_price


class Transaction:
    def __init__(self, item):
        self.item = item
