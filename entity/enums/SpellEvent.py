from enum import Enum


class SpellEvent(Enum):
    first_launch = 0,
    unknown_command = 1,
    help = 2
