from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QDialog, QSpinBox, QRadioButton

import game_manager
import images
import res


class MainMenu(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        uic.loadUi('ui/main_menu.ui', self)

        def normal_mode_button_clicked():
            if game_manager.saved_game_exist():
                ContinueGameDialog(self.parent()).exec()
            else:
                NewGameDialog(self.parent()).exec()

        def campaign_button_clicked():
            self.parent().show_campaign_menu()

        self.normal_mode_button.clicked.connect(normal_mode_button_clicked)
        self.campaign_button.clicked.connect(campaign_button_clicked)
        self.exit_button.clicked.connect(lambda: self.parent().close())


class ContinueGameDialog(QDialog):
    def __init__(self, *args):
        super().__init__(*args)
        uic.loadUi('ui/continue_game.ui', self)

        def continue_button_handler():
            self.accept()
            game_manager.load_game()
            self.parent().show_normal_game()

        self.continue_button.clicked.connect(continue_button_handler)

        def new_game_button_handler():
            self.accept()
            NewGameDialog(self.parent()).exec()

        self.new_game_button.clicked.connect(new_game_button_handler)


class WinLoseDialog(QDialog):
    def __init__(self, win: bool, *args):
        super().__init__(*args)
        uic.loadUi('ui/win_lose.ui', self)
        if win:
            self.lose_text.hide()
        else:
            self.win_text.hide()

        def new_game_button_handler():
            self.accept()
            NewGameDialog(self.parent()).exec()

        self.new_game_button.clicked.connect(new_game_button_handler)


class LevelLoseDialog(QDialog):
    def __init__(self, *args):
        super().__init__(*args)
        uic.loadUi('ui/level_lose.ui', self)

        def replay_button_handler():
            self.accept()
            game_manager.load_level(game_manager.current_level)
            self.parent().show_level()

        def main_menu_handler():
            self.accept()
            self.parent().show_main_menu()

        self.replay.clicked.connect(replay_button_handler)
        self.main_menu.clicked.connect(main_menu_handler)


class LevelCompletedDialog(QDialog):
    def __init__(self, *args):
        super().__init__(*args)
        uic.loadUi('ui/level_completed.ui', self)
        stars = game_manager.get_level_stars(game_manager.current_level)
        for j in range(3):
            if j < stars:
                getattr(self, f'star_{j + 1}').setPixmap(QPixmap.fromImage(images.star))
            else:
                getattr(self, f'star_{j + 1}').setPixmap(QPixmap.fromImage(images.dark_star))

        def next_button_handler():
            self.accept()
            game_manager.load_level(game_manager.current_level + 1)
            self.parent().show_level()

        def replay_button_handler():
            self.accept()
            game_manager.load_level(game_manager.current_level)
            self.parent().show_level()

        def main_menu_handler():
            self.accept()
            self.parent().show_main_menu()

        self.replay.clicked.connect(replay_button_handler)
        self.main_menu.clicked.connect(main_menu_handler)
        self.next.clicked.connect(next_button_handler)


class NewGameDialog(QDialog):
    def __init__(self, *args):
        super().__init__(*args)
        self.mines_count: QSpinBox
        self.field_width: QSpinBox
        self.field_height: QSpinBox
        uic.loadUi('ui/new_game.ui', self)

        def difficulty_selected(difficulty):
            def handler():
                self.mines_count.setValue(game_manager.difficulties[difficulty][0])
                self.mines_count.setEnabled(False)
                self.field_width.setValue(game_manager.difficulties[difficulty][1])
                self.field_width.setEnabled(False)
                self.field_height.setValue(game_manager.difficulties[difficulty][2])
                self.field_height.setEnabled(False)

            return handler

        for i in range(3):
            button: QRadioButton = getattr(self, f'difficulty_{i}')
            button.clicked.connect(difficulty_selected(i))

        def custom_difficulty_handler():
            self.mines_count.setEnabled(True)
            self.field_width.setEnabled(True)
            self.field_height.setEnabled(True)

        def play_handler():
            game_manager.new_normal_game(self.field_width.value(), self.field_height.value(), self.mines_count.value())
            self.parent().show_normal_game()

        self.play_button.clicked.connect(play_handler)
        self.custom_difficulty.clicked.connect(custom_difficulty_handler)
        self.difficulty_1.clicked.emit()
        self.difficulty_1.setChecked(True)


class Campaign(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        uic.loadUi('ui/campaign.ui', self)
        levels_completed = game_manager.get_levels_completed()
        for i in range(9):
            lvl = getattr(self, f'level_{i + 1}')
            uic.loadUi('ui/level.ui', lvl)
            stars = game_manager.get_level_stars(i)

            def level_button_handler(level):
                def handler():
                    if game_manager.saved_game_exist(game_manager.GameType.Level, level):
                        game_manager.load_saved_level(level)
                    else:
                        game_manager.load_level(level)
                    self.parent().show_level()

                return handler

            getattr(lvl, f'button').clicked.connect(level_button_handler(i))
            getattr(lvl, f'level_name').setText(f'Уровень {i + 1}')
            for j in range(3):
                if j < stars:
                    getattr(lvl, f'star_{j + 1}').setPixmap(QPixmap.fromImage(images.star))
                else:
                    getattr(lvl, f'star_{j + 1}').setPixmap(QPixmap.fromImage(images.dark_star))
            if i > levels_completed:
                lvl.setEnabled(False)
            lvl.show()
