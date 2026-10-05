import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import random
import pygame as pg

WIDTH, HEIGHT = 1280, 880
BG = '#0b141c'
PANEL = '#14232c'
PANEL2 = '#1b3038'
LINE = '#29424a'
WHITE = '#e5efe9'
MUTED = '#91a7ad'
MINT = '#9ee5b0'
GOLD = '#edc581'
PURPLE = '#c1a1ed'
BLUE = '#82c9e1'
RED = '#ed9c9c'
COLORS = [MINT, GOLD, PURPLE, BLUE]

FONTS = {}

def font(size, bold=False):
    if (size, bold) not in FONTS:
        FONTS[(size, bold)] = pg.font.SysFont('avenirnext,helveticaneue,trebuchetms,tahoma,segoeui,arial', size, bold)
    return FONTS[(size, bold)]


def txt(surface, value, x, y, size=18, color=WHITE, bold=False, align='left'):
    image = font(size, bold).render(str(value), True, color)
    r = image.get_rect(topleft=(x, y))
    if align == 'center':
        r.centerx = x
    elif align == 'right':
        r.right = x
    surface.blit(image, r)


def paragraph(s, value, x, y, width, size=17, color=MUTED, spacing=5):
    row = ''
    for word in value.split():
        if row and font(size).size(row + ' ' + word)[0] > width:
            txt(s, row, x, y, size, color)
            y += size + spacing
            row = word
        else:
            row = (row + ' ' + word).strip()
    txt(s, row, x, y, size, color)
    return y + size + spacing


def box(s, r, color=PANEL, border=None, radius=16):
    pg.draw.rect(s, color, r, border_radius=radius)
    if border:
        pg.draw.rect(s, border, r, 1, border_radius=radius)

class Game:
    def __init__(self):
        pg.init()
        self.s = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption('Stop the Darkness · Ánh sáng cuối cùng')
        self.clock = pg.time.Clock()
        self.running = True
        self.scene = 'menu'
        self.mouse = (0, 0)
        self.click = False
        self.seed = random.randrange(100000, 999999)

    def button(self, label, r, primary=False):
        r = pg.Rect(r)
        hot = r.collidepoint(self.mouse)
        if primary:
            color = '#b0edbf' if hot else MINT
            text_color = BG
        else:
            color = '#29434a' if hot else PANEL2
            text_color = WHITE
        box(self.s, r, color, None if primary else LINE, 12)
        txt(self.s, label, r.centerx, r.y + (r.height - 22) // 2, 17, text_color, True, 'center')
        return hot and self.click

    def menu(self):
        txt(self.s, 'STOP THE DARKNESS', 40, 23, 24, WHITE, True)
        txt(self.s, 'ÁNH SÁNG CUỐI CÙNG', 40, 54, 11, MINT, True)

        box(self.s, (28, 192, 648, 648), '#152b2d', LINE, 22)

        for x, y in [(718, 127), (1183, 151), (1234, 773), (1150, 824), (695, 842)]:
            pg.draw.circle(self.s, '#627f71', (x, y), 2)

        box(self.s, (708, 185, 532, 656), PANEL, LINE, 24)
        txt(self.s, 'MỘT THẾ GIỚI NHỎ. MỘT CƠ HỘI CUỐI.', 744, 220, 12, MINT, True)
        txt(self.s, 'GIỮ LẠI ÁNH SÁNG', 740, 255, 50, WHITE, True)
        paragraph(self.s, 'Xây làng. Kết nối tài nguyên. Đánh thức phép thuật trước khi bóng tối nuốt chửng vùng đất của bạn.',
                  744, 395, 444, 20, WHITE, 7)

        for y, title, desc in [(511, 'Phát triển từng ô', 'Các ô kề nhau tăng sức mạnh cho nhau.'),
                               (571, 'Chạy đua với bóng tối', 'Hai con đường: phép thuật hoặc công nghệ.')]:
            box(self.s, (744, y, 44, 44), PANEL2, LINE, 8)
            txt(self.s, title, 804, y + 2, 18, WHITE, True)
            txt(self.s, desc, 804, y + 26, 15, MUTED)

        if self.button('Bắt đầu ván mới', (744, 640, 460, 52), True):
            self.scene = 'game'
        if self.button('Đổi bản đồ', (744, 704, 460, 46)):
            self.seed = random.randrange(100000, 999999)

        txt(self.s, f'BẢN ĐỒ #{self.seed}  ·  STANDARD  ·  12 × 12', 744, 773, 12, MUTED, True)
        txt(self.s, 'Cơ chế tham khảo: Stop the Darkness / Florian van Strien', 40, 853, 13, MUTED)

    def game(self):
        txt(self.s, 'Màn chơi sẽ làm ở các bước sau', 640, 420, 24, WHITE, True, 'center')
        if self.button('Về menu', (560, 480, 160, 46)):
            self.scene = 'menu'

    def run(self):
        while self.running:
            dt = min(.1, self.clock.tick(120) / 1000)
            self.mouse = pg.mouse.get_pos()
            self.click = False
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.running = False
                elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    self.click = True
            self.s.fill(BG)
            if self.scene == 'menu':
                self.menu()
            else:
                self.game()
            pg.display.flip()
        pg.quit()

if __name__ == '__main__':
    Game().run()