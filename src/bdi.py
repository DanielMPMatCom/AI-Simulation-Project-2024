

class Belief:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description

class Desire:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description
        
class Intention:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description