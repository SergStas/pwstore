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
    new_lot_input_server = 9,
    new_lot_input_race = 10,
    new_lot_input_class = 11,
    invalid_value = 12
    new_lot_input_lvl = 13,
    new_lot_input_heaven = 14,
    new_lot_input_doll = 15,
    new_lot_input_description = 16,
    new_lot_input_price = 17,
    new_lot_input_contacts = 18
