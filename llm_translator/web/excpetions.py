
class MultipleActiveSpecs(Exception):
    def __init__(self, message):
        super().__init__(message)

class TranslationException(Exception):
    def __init__(self, message):
        super().__init__(message)
