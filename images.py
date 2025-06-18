from PyQt5.QtGui import QImage

digits = [QImage('res/cell2.png')]
for i in range(1, 9):
    digits.append(QImage(f'res/{i}.png'))
cell1_img = QImage('res/cell1.png')
cell2_img = QImage('res/cell2.png')
bomb = QImage('res/bomb.png')
bomb_crossed = QImage('res/bomb_crossed.png')
red_bomb = QImage('res/red_bomb.png')
flag = QImage('res/flag.png')
star = QImage('res/star.png')
dark_star = QImage('res/dark_star.png')