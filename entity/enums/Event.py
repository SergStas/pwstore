from enum import Enum


class Event(Enum):
    first_launch = 0,
    unknown_command = 1,
    help = 2,
    select_server = 3,
    select_race = 4,
    db_error = 5,
    no_lots_found = 6,
    filtered_lots_found = 7
