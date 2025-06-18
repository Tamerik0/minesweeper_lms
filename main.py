import os
import sqlite3
import sys

from PyQt5.QtCore import Qt

import game_manager
import game_renderer
import menus
import res
from PyQt5 import uic
from PyQt5.QtWidgets import *


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_menu = None
        self.campaign_menu = None
        self.game_renderer = None
        uic.loadUi('ui/main.ui', self)
        self.show_main_menu()

    def show_game(self):
        if self.main_menu is not None:
            self.main_menu.close()
            self.main_menu = None
        if self.campaign_menu is not None:
            self.campaign_menu.close()
            self.campaign_menu = None
        if self.game_renderer is not None:
            self.game_renderer.close()
            del self.game_renderer
        self.game_renderer = game_renderer.GameRenderer(self)
        self.game_renderer.show()

    def show_normal_game(self):
        self.show_game()
        game_manager.set_game_callback(lambda: menus.WinLoseDialog(True, self).exec(),
                                       lambda: menus.WinLoseDialog(False, self).exec())

    def show_level(self):
        self.show_game()

        def level_completed():
            game_manager.set_levels_completed(max(game_manager.get_levels_completed(), game_manager.current_level + 1))
            if game_manager.current_game.time < 30:
                stars = 3
            elif game_manager.current_game.time < 60:
                stars = 2
            else:
                stars = 1
            game_manager.set_level_stars(game_manager.current_level,
                                         max(game_manager.get_level_stars(game_manager.current_level), stars))
            menus.LevelCompletedDialog(self).exec()

        game_manager.set_game_callback(level_completed, lambda: menus.LevelLoseDialog(self).exec())

    def show_main_menu(self):
        if self.game_renderer is not None:
            self.game_renderer.close()
            del self.game_renderer
            self.game_renderer = None
        if self.campaign_menu is not None:
            self.campaign_menu.close()
            self.campaign_menu = None
        if self.main_menu is None:
            self.main_menu = menus.MainMenu(self)
        self.main_menu.show()

    def show_campaign_menu(self):
        if self.game_renderer is not None:
            self.game_renderer.close()
            del self.game_renderer
            self.game_renderer = None
        if self.game_renderer is not None:
            self.game_renderer.close()
            self.game_renderer = None
        if self.main_menu is not None:
            self.main_menu.close()
            self.main_menu = None
        if self.campaign_menu is None:
            self.campaign_menu = menus.Campaign(self)
        self.campaign_menu.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            game_manager.save_current_game()
            self.show_main_menu()

    def closeEvent(self, event):
        game_manager.save_current_game()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    app.exec()
