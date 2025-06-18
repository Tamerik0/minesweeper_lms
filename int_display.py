from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QWidget


class IntDisplay(QWidget):
    digits = [QImage(f'res/IntDisplay/{i}.png') for i in range(10)]
    digit_width = 26
    digit_height = 46

    def __init__(self, *args):
        super().__init__(*args)
        self._value = 0

    def set_value(self, value):
        self._value = value
        self.update()

    def value(self):
        return self._value

    def paintEvent(self, event):
        s = f'{max(0, self._value):03}'
        painter = QPainter(self)
        for i in range(3):
            painter.drawImage(IntDisplay.digit_width * i, 0, IntDisplay.digits[int(s[i])])
