class PrometheusSinkMetricNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class FieldNotFoundError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
