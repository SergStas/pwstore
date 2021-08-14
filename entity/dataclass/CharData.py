from entity.enums.Race import Race
from entity.enums.Server import Server


class CharData:
    def __init__(
            self,
            server: Server,
            race: Race,
            lvl: int,
            char_class: str,
            description: str,
            heavens: str,
            doll: str,
            char_id: int = None
    ):
        self.server = server
        self.race = race
        self.lvl = lvl
        self.char_class = char_class
        self.description = description
        self.heavens = heavens
        self.doll = doll
        self.char_id = char_id
