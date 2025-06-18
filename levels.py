from game_manager import Game, Field

levels = []


def level(width, height, data):
    field = Field.load_field_from_str(data, width, height)
    lvl = Game(field.count_mines(), width, height)
    lvl.state = Game.State.IN_GAME
    lvl.field = field
    return lvl


levels.append(level(8, 8, "             "))
levels.append(level(10, 10, "                                       "
                            "               "))
levels.append(level(11, 11, "                                    "
                            "                                      "))
levels.append(level(12, 12, "                                               "
                            "                                     "))
levels.append(level(13, 13, "                               "
                            "                         "
                            "              "))
levels.append(level(13, 13, "                                            "
                            "                                                 "
                            "                                         "))
levels.append(level(14, 14, "                                                                  "
                            "                                        "
                            "                       "))
levels.append(level(3, 3, " "))
levels.append(level(1, 1, " "))
