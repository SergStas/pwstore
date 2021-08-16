from enum import Enum


class Event(Enum):
    first_launch = 0,
    unknown_command = 1,
    help = 2,
    search_select_server = 3,
    search_select_race = 4,
    db_error = 5,
    no_lots_found = 6,
    filtered_lots_found = 7,
    sell_menu = 8,
    sell_input_server = 9,
    sell_input_race = 10
