import json
import os.path
import random
import shutil
import sys
from enum import Enum

sys.setrecursionlimit(10000000)


class GameType(Enum):
    Normal = 0
    Level = 1
    Endless = 2


def saved_game_exist(game_type=GameType.Normal, level_id=None):
    if game_type == GameType.Normal:
        game_path = f'{save_path}/normal'
    elif game_type == GameType.Endless:
        game_path = f'{save_path}/endless_game'
    else:
        game_path = f'{save_path}/campaign/{level_id}'
    if os.path.exists(game_path):
        if get_game_info(game_path) is not None:
            return True
    return False


def get_game_info(game_path):
    info_path = f'{game_path}/info.json'
    if os.path.exists(info_path):
        return json.load(open(info_path))


def get_levels_completed():
    return json.load(open(f'{save_path}/campaign/progress.json')).get('levels_completed', 0)


def set_levels_completed(number):
    data = json.load(open(f'{save_path}/campaign/progress.json', 'r+'))
    data['levels_completed'] = number
    json.dump(data, open(f'{save_path}/campaign/progress.json', 'w'))


def get_level_stars(index):
    stars = json.load(open(f'{save_path}/campaign/progress.json'))['stars']
    return stars[index]


def set_level_stars(index, stars):
    data = json.load(open(f'{save_path}/campaign/progress.json'))
    data['stars'][index] = stars
    json.dump(data, open(f'{save_path}/campaign/progress.json', 'w'))


def load_game(type=GameType.Normal):
    global game_type
    game_type = type
    if game_type == GameType.Normal:
        load_game_from_path(f'{save_path}/normal')
        game_type = GameType.Normal
    elif game_type == GameType.Endless:
        pass


def load_saved_level(number):
    global game_type, current_level
    load_game_from_path(f'{save_path}/campaign/{number}')
    game_type = GameType.Level
    current_level = number


def save_current_game():
    global game_type, current_level, current_game
    if current_game is not None:
        if game_type == GameType.Normal:
            current_game.save_normal_game()
        elif game_type == GameType.Level:
            current_game.save_level(current_level)


def load_level(number):
    global current_game, current_level, game_type
    current_game = Game.load_level(number)
    game_type = GameType.Level
    current_level = number


def load_game_from_path(game_path):
    global current_game
    current_game = Game.load_game(game_path)


def new_normal_game(width, height, mines):
    global current_game, game_type
    current_game = Game(mines, width, height)
    game_type = GameType.Normal


def set_game_callback(win, lose):
    current_game.win_handler = win
    current_game.lose_handler = lose


class Cell:
    class State(Enum):
        NOT_OPENED = 0
        FLAG = 1
        OPENED = 2

    def __init__(self, contains_mine=False):
        self.state = Cell.State.NOT_OPENED
        self.contains_mine = contains_mine
        self.mines_around = None

    def copy(self):
        cell = Cell(self.contains_mine)
        cell.state = self.state
        cell.mines_around = self.mines_around
        return cell


class Game:
    class State(Enum):
        NOT_STARTED = 0
        IN_GAME = 1
        VICTORY = 2
        LOSS = 3

    def __init__(self, mines, width, height, win_callback=None, lose_callback=None):
        self.win_handler = win_callback
        self.lose_handler = lose_callback
        self.time = 0
        self.field = Field(width, height)
        self.mines = mines
        self.width = width
        self.height = height
        self.state = Game.State.NOT_STARTED

    def open(self, x, y):
        if self.state == Game.State.NOT_STARTED:
            self.field.gen_field(self.mines, [(x, y)])
            self.state = Game.State.IN_GAME
        if self.state == Game.State.IN_GAME:
            res = self.field.open(x, y)
            if res == Field.OpenResult.WIN:
                self.state = Game.State.VICTORY
                if self.win_handler is not None:
                    self.win_handler()
            elif res == Field.OpenResult.LOSE:
                self.state = Game.State.LOSS
                self.fail_pos = (x, y)
                if self.lose_handler is not None:
                    self.lose_handler()

    def flag(self, x, y):
        if self.state == Game.State.IN_GAME:
            if self.field.get_cell(x, y).state == Cell.State.FLAG:
                self.field.get_cell(x, y).state = Cell.State.NOT_OPENED
                self.mines += 1
            elif self.field.get_cell(x, y).state == Cell.State.NOT_OPENED:
                self.field.get_cell(x, y).state = Cell.State.FLAG
                self.mines -= 1

    @staticmethod
    def load_game(path):
        info = get_game_info(path)
        time = info.get('time', 0)
        width = info.get('width', 0)
        height = info.get('height', 0)
        field = Field.load_field(f'{path}/field', width, height)
        game = Game(field.count_mines() - field.count_flags(), width, height)
        game.field = field
        game.time = time
        game.state = Game.State.IN_GAME
        return game

    @staticmethod
    def load_level(index):
        from levels import levels
        return levels[index].copy()

    def save(self, path):
        if self.state == Game.State.IN_GAME:
            info = {'time': self.time, 'width': self.field.width, 'height': self.field.height}
            if not os.path.exists(path):
                os.makedirs(path)
            json.dump(info, open(f'{path}/info.json', 'w'))
            self.field.save(f'{path}/field')
        else:
            if os.path.exists(path):
                shutil.rmtree(path)
                os.mkdir(path)

    def save_normal_game(self):
        self.save(f'{save_path}/normal')

    def save_level(self, level_id):
        self.save(f'{save_path}/campaign/{level_id}')

    def copy(self):
        game = Game(self.mines, self.width, self.height)
        game.state = self.state
        game.time = self.time
        game.field = self.field.copy()
        return game


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.min_x = 0
        self.min_y = 0
        self.max_x = width - 1
        self.max_y = height - 1
        self.field = [[Cell() for i in range(height)] for j in range(width)]

    def gen_field(self, mines, excluded_positions: list[tuple[int, int]]):
        available_cells = set()
        for i in range(self.width):
            for j in range(self.height):
                available_cells.add(self.field[i][j])
        available_cells.difference_update(map(lambda x: self.field[x[0]][x[1]], excluded_positions))
        available_cells = list(available_cells)
        for i in range(mines):
            m = random.randrange(0, len(available_cells))
            cell = available_cells[m]
            cell.contains_mine = True
            available_cells.remove(cell)
        self._count_mines_for_all_cells()

    def count_mines(self):
        ans = 0
        for i in range(self.min_x, self.max_x + 1):
            for j in range(self.min_y, self.max_y + 1):
                ans += int(self.get_cell(i, j).contains_mine)
        return ans

    def count_flags(self):
        ans = 0
        for i in range(self.min_x, self.max_x + 1):
            for j in range(self.min_y, self.max_y + 1):
                ans += int(self.get_cell(i, j).state == Cell.State.FLAG)
        return ans

    def count_mines_around(self, x, y):
        mines_around = 0
        for i in range(max(0, x - 1), min(x + 2, self.width)):
            for j in range(max(0, y - 1), min(y + 2, self.height)):
                mines_around += int(self.field[i][j].contains_mine)
        return mines_around

    def _count_mines_for_all_cells(self):
        for i in range(self.width):
            for j in range(self.height):
                self.field[i][j].mines_around = self.count_mines_around(i, j)

    @staticmethod
    def load_field(path, width, height):
        return Field.load_field_from_str(open(path).read(), width, height)

    @staticmethod
    def load_field_from_str(data, width, height):
        field = Field(width, height)
        data = bytearray(data, 'utf-8')
        for i in range(width):
            for j in range(height):
                cell_data = data[i * height + j]
                contains_mine = cell_data & 1
                state = (cell_data & 0b1100) >> 2
                field.field[i][j].contains_mine = contains_mine
                field.field[i][j].state = Cell.State(state)
        field._count_mines_for_all_cells()
        return field

    def save(self, path):
        file = open(path, 'wb')
        data = [0] * (self.width * self.height)
        for i in range(self.width):
            for j in range(self.height):
                contains_mine = self.field[i][j].contains_mine
                state = self.field[i][j].state
                data[i * self.height + j] = (state.value << 2) | contains_mine
        file.write(bytearray(data))

    class OpenResult(Enum):
        WIN = 0
        LOSE = 1
        OK = 2

    def get_cell(self, x, y):
        return self.field[x][y]

    def check_for_win(self):
        for i in range(self.width):
            for j in range(self.height):
                if not self.field[i][j].contains_mine and self.field[i][j].state == Cell.State.NOT_OPENED:
                    return False
        return True

    def open(self, x, y):
        if self.field[x][y].contains_mine:
            return Field.OpenResult.LOSE
        else:
            self.get_cell(x, y).state = Cell.State.OPENED
            self.get_cell(x, y).mines_around = 0
            for i in range(max(self.min_x, x - 1), min(x + 1, self.max_x) + 1):
                for j in range(max(self.min_y, y - 1), min(y + 1, self.max_y) + 1):
                    self.get_cell(x, y).mines_around += int(self.get_cell(i, j).contains_mine)
            if self.get_cell(x, y).mines_around == 0:
                for i in range(max(self.min_x, x - 1), min(x + 1, self.max_x) + 1):
                    for j in range(max(self.min_y, y - 1), min(y + 1, self.max_y) + 1):
                        if self.get_cell(i, j).state == Cell.State.NOT_OPENED:
                            self.open(i, j)
            if self.check_for_win():
                return Field.OpenResult.WIN
            return Field.OpenResult.OK

    def copy(self):
        field = Field(self.width, self.height)
        for i in range(self.width):
            for j in range(self.height):
                field.field[i][j] = self.field[i][j].copy()
        return field


save_path = "save"
level_count = 9
difficulties = [(10, 8, 8), (40, 16, 16), (99, 30, 16)]
current_game: Game = None
game_type = None
current_level = None
if not os.path.exists(f'{save_path}/campaign'):
    os.makedirs(f'{save_path}/campaign')
if not os.path.exists(f'{save_path}/campaign/progress.json'):
    open(f'{save_path}/campaign/progress.json', 'w').write('{"levels_completed": 0, "stars": [0,0,0,0,0,0,0,0,0]}')
