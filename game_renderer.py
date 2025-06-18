from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QImage, QMouseEvent, QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.uic.properties import QtGui

import game_manager
import images
from int_display import IntDisplay


class GameRenderer(QWidget):
    def __init__(self, *args):
        super().__init__(*args)

        uic.loadUi('ui/game.ui', self)
        g = self.field_renderer.geometry()
        self.field_renderer = GameRenderer.FieldRenderer(self)
        self.field_renderer.setGeometry(g)

        g = self.mines_count.geometry()
        self.mines_count = IntDisplay(self)
        self.mines_count.setGeometry(g)

        g = self.time.geometry()
        self.time = IntDisplay(self)
        self.time.setGeometry(g)

        self.timer = QTimer(self)
        self.time.set_value(game_manager.current_game.time)
        self.mines_count.set_value(game_manager.current_game.mines)
        field = game_manager.current_game.field
        self.parent().setMinimumSize(field.width * 32 + 200, field.height * 32 + 200)
        self.setFixedSize(field.width * 32 + 200, field.height * 32 + 200)

        def update():
            if game_manager.current_game.state == game_manager.Game.State.IN_GAME:
                game_manager.current_game.time += 1
                self.time.set_value(game_manager.current_game.time)

        self.timer.timeout.connect(update)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.start(1000)

    def close(self):
        super().close()
        self.timer.stop()

    def update(self):
        super().update()
        self.mines_count.set_value(game_manager.current_game.mines)

    class FieldRenderer(QWidget):
        def __init__(self, *args):
            super().__init__(*args)
            self.click_pos = (None, None)

        def paintEvent(self, a0):
            if game_manager.current_game is not None:
                field = game_manager.current_game.field
                self.setFixedSize(field.width * 32, field.height * 32)
                painter = QPainter(self)
                if game_manager.current_game.state == game_manager.Game.State.LOSS:
                    for i in range(field.width):
                        for j in range(field.height):
                            cell: game_manager.Cell = field.get_cell(i, j)
                            if cell.contains_mine:
                                if (i, j) == game_manager.current_game.fail_pos:
                                    painter.drawImage(i * 32, j * 32, images.red_bomb)
                                elif cell.state == game_manager.Cell.State.FLAG:
                                    painter.drawImage(i * 32, j * 32, images.flag)
                                else:
                                    painter.drawImage(i * 32, j * 32, images.bomb)
                            else:
                                if cell.state == game_manager.Cell.State.FLAG:
                                    painter.drawImage(i * 32, j * 32, images.bomb_crossed)
                                else:
                                    painter.drawImage(i * 32, j * 32, images.digits[cell.mines_around])
                else:
                    for i in range(field.width):
                        for j in range(field.height):
                            cell: game_manager.Cell = field.get_cell(i, j)
                            if cell.state == game_manager.Cell.State.NOT_OPENED:
                                if (i, j) == self.click_pos:
                                    painter.drawImage(i * 32, j * 32, images.cell2_img)
                                else:
                                    painter.drawImage(i * 32, j * 32, images.cell1_img)
                            elif cell.state == game_manager.Cell.State.OPENED:
                                painter.drawImage(i * 32, j * 32, images.digits[cell.mines_around])
                            else:
                                painter.drawImage(i * 32, j * 32, images.flag)

        def mousePressEvent(self, event: QMouseEvent):
            if event.button() == Qt.MouseButton.LeftButton:
                self.click_pos = (event.x() // 32, event.y() // 32)
            self.update()

        def mouseReleaseEvent(self, event: QMouseEvent):
            if 0 <= event.x() < game_manager.current_game.width * 32 and 0 <= event.y() < game_manager.current_game.height * 32:
                if event.button() == Qt.MouseButton.LeftButton:
                    if (event.x() // 32, event.y() // 32) == self.click_pos:
                        game_manager.current_game.open(*self.click_pos)
                    self.click_pos = None
                elif event.button() == Qt.MouseButton.RightButton:
                    game_manager.current_game.flag(event.x() // 32, event.y() // 32)
            self.update()
            self.parent().update()
