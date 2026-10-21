import math
import pygame as pg

BG = '#0b141c'           
PANEL = '#14232c'         # nền khung
PANEL2 = '#1b3038'        # nền khung phụ / nút thường
LINE = '#29424a'          # đường viền
WHITE = '#e5efe9'
MUTED = '#91a7ad'        
MINT = '#9ee5b0'          
GOLD = '#edc581'
PURPLE = '#c1a1ed'
BLUE = '#82c9e1'
RED = '#ed9c9c'
COLORS = [MINT, GOLD, PURPLE, BLUE]      # màu của 4 tài nguyên: gỗ, đá, phép thuật, công nghệ

BASE = 52                              



def resource_icon(s, kind, x, y, size=22):
    c = COLORS[kind]
    x = int(x)
    y = int(y)
    h = size // 2                       
    if kind == 0:                      
        pg.draw.line(s, c, (x - size // 3, y + size // 4), (x + size // 3, y - size // 4), h)
        pg.draw.circle(s, '#526d56', (x + size // 3, y - size // 4), size // 4)
        pg.draw.circle(s, c, (x + size // 3, y - size // 4), size // 4, 2)
    elif kind == 1:                     
        pg.draw.polygon(s, c, [(x - h, y + size // 3), (x - size // 3, y - size // 3),
                               (x + size // 4, y - h), (x + h, y + size // 4), (x, y + h)])
        pg.draw.line(s, '#a1865d', (x - size // 3, y - size // 3), (x, y), 2)
    elif kind == 2:                      
        pg.draw.polygon(s, c, [(x, y - h), (x + size // 3, y), (x, y + h), (x - size // 3, y)])
        pg.draw.line(s, WHITE, (x, y - size // 3), (x + size // 7, y), 1)
    else:                              
        pg.draw.circle(s, c, (x, y), h, 2)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):                
            pg.draw.line(s, c, (x + dx * size // 3, y + dy * size // 3),
                         (x + dx * (h + 3), y + dy * (h + 3)), 3)
        pg.draw.circle(s, c, (x, y), 3)


def tree(s, x, y, scale=1.0):
    pg.draw.rect(s, '#9a8158', (x - 1, y, 3, 13))
    pg.draw.circle(s, '#193b32', (x + 2, y + 2), round(9 * scale))
    pg.draw.circle(s, '#4c8760', (x, y - 3), round(9 * scale))
    pg.draw.circle(s, '#70a979', (x - 2, y - 5), round(5 * scale))


def house(s, x, y, wall='#d6c9a2', roof='#b88869', h=12):
    pg.draw.rect(s, '#20352e', (x + 2, y + 3, 15, h + 2), border_radius=2)   # bóng đổ
    pg.draw.rect(s, wall, (x, y, 14, h), border_radius=2)                    # tường
    pg.draw.polygon(s, roof, [(x - 2, y), (x + 7, y - 8), (x + 16, y)])      # mái
    pg.draw.rect(s, '#463f38', (x + 6, y + 6, 4, h - 6))                     # cửa
    pg.draw.rect(s, '#f6d994', (x + 2, y + 3, 3, 3))                         # cửa sổ sáng


def draw_water(s, art, level, variant):
    for j in range(4):
        off = (variant + j) % 3 * 3
        pg.draw.lines(s, '#508087', False, [(5 + off, 9 + j * 11), (13 + off, 7 + j * 11), (22 + off, 9 + j * 11)])
        pg.draw.lines(s, '#3c6d78', False, [(28, 14 + j * 10), (33, 12 + j * 10), (44, 14 + j * 10)])


def draw_forest(s, art, level, variant):
    if level == 0:
        tree(s, 24, 30, .5)
        return
    tree(s, 14, 25, .8)
    tree(s, 36, 22, .8)
    tree(s, 26, 33, 1)


def draw_mushroom(s, art, level, variant):
    """Rừng nấm: 3 cây nấm (x, y, bán kính mũ)."""
    for x, y, r in [(14, 31, 7), (35, 26, 8), (26, 41, 6)]:
        pg.draw.rect(s, '#c3c4ae', (x - 2, y - 2, 4, 11), border_radius=2)   # thân
        pg.draw.circle(s, '#9674ac', (x, y - 3), r)                           # mũ
        pg.draw.rect(s, '#c6a5dc', (x - r, y - 3, 2 * r, 3))
        pg.draw.circle(s, '#e5d5ef', (x - 2, y - 6), 2)                       # chấm sáng


def draw_rock(s, art, level, variant):
    for x, y in [(14, 32), (34, 35), (26, 20)]:
        pg.draw.polygon(s, '#a0b1aa', [(x - 9, y + 7), (x - 7, y - 4), (x, y - 9), (x + 9, y), (x + 7, y + 9)])
        pg.draw.polygon(s, '#6f8784', [(x, y - 9), (x + 9, y), (x + 7, y + 9), (x, y + 6)])   # mặt tối
    if art == 'mining':
        house(s, 19, 31, '#c3c9b8', '#a6b198', 12)


def draw_circle(s, art, level, variant):
    glow = MINT if level >= 2 else '#718c87'
    pg.draw.ellipse(s, '#203532', (8, 22, 37, 25))
    if level >= 2:
        pg.draw.ellipse(s, MINT, (9, 17, 34, 25), 2)
    for j in range(6):
        angle = math.tau * j / 6                        # chia đều 6 góc quanh vòng tròn
        x = 26 + 14 * math.cos(angle)
        y = 28 + 9 * math.sin(angle)
        pg.draw.rect(s, '#afbab0', (x - 3, y - 10, 6, 12), border_radius=2)
        pg.draw.line(s, glow, (x, y - 8), (x, y - 3))
    pg.draw.circle(s, MINT if level >= 2 else '#9cc5bd', (26, 28), 3)


def draw_tower(s, art, level, variant):
    pg.draw.circle(s, '#496451', (26, 30), 18)
    pg.draw.polygon(s, '#b6c8bc', [(17, 43), (21, 14), (31, 14), (36, 43)])
    pg.draw.rect(s, '#718e87', (23, 18, 6, 24), border_radius=2)
    pg.draw.rect(s, '#e0dabb', (18, 12, 16, 6), border_radius=2)
    pg.draw.polygon(s, '#d2ae72', [(17, 12), (26, 5), (35, 12)])
    pg.draw.circle(s, MINT, (26, 17), 5)
    pg.draw.circle(s, '#edf8ca', (25, 16), 2)
    if level >= 2:
        pg.draw.circle(s, MINT, (26, 17), 10, 1)


def draw_city(s, art, level, variant):
    if art == 'magiccity':
        roof = '#a690c1'
    else:
        roof = '#73a592'
    for x, y, h in [(9, 25, 17), (24, 19, 25), (36, 28, 14)]:       # (x, y, chiều cao) từng toà nhà
        pg.draw.rect(s, '#d2d5bc', (x, y, 9, h), border_radius=2)
        pg.draw.rect(s, '#718f86', (x + 6, y + 2, 3, h - 2))
        for wy in range(y + 4, y + h - 3, 6):                       # các cửa sổ sáng, cách nhau 6px
            pg.draw.rect(s, GOLD, (x + 2, wy, 3, 3))
        pg.draw.polygon(s, roof, [(x - 1, y), (x + 4, y - 6), (x + 10, y)])
    if art == 'research':
        pg.draw.lines(s, BLUE, False, [(28, 4), (28, 13), (40, 13)], 2)
        pg.draw.circle(s, BLUE, (28, 6), 4, 1)
    elif art == 'magiccity':
        pg.draw.circle(s, PURPLE, (28, 7), 5)


def draw_village(s, art, level, variant):
    magic = (art == 'magicvillage')
    if magic:
        roof = '#ac91c0'
    else:
        roof = '#ba9970'
    house(s, 8, 30, '#d1c8a8', roof, 12)
    house(s, 27, 22, '#ddd4b1', roof, 15)
    if level >= 2:
        house(s, 30, 37, '#c6c6a2', roof, 9)
    if magic:
        pg.draw.circle(s, PURPLE, (16, 13), 3)
        pg.draw.line(s, '#8fa9ab', (16, 16), (16, 21))


# Bảng tra: tên kiểu ảnh (Kind.art trong world.py) -> (màu nền ô, hàm vẽ).  Hàm vẽ = None nghĩa là chỉ có nền.
ART = {
    'grass':        ('#2d4b40', None),
    'water':        ('#20434c', draw_water),
    'forest':       ('#2d4b40', draw_forest),
    'mushroom':     ('#33433e', draw_mushroom),
    'rock':         ('#354449', draw_rock),
    'mining':       ('#2d4b40', draw_rock),
    'circle':       ('#304545', draw_circle),
    'light':        ('#374746', draw_tower),
    'village':      ('#2d4b40', draw_village),
    'magicvillage': ('#344342', draw_village),
    'city':         ('#2d4b40', draw_city),
    'magiccity':    ('#354148', draw_city),
    'research':     ('#2b424b', draw_city),
}


def tile_art(art, level=1, size=48, variant=0, dark=False):
    s = pg.Surface((BASE, BASE), pg.SRCALPHA)         # tấm ảnh trong suốt 52x52 để vẽ lên

    if dark:
        # nền đen tím + 3 đường lượn sóng + 2 chấm sáng mờ
        pg.draw.rect(s, '#11151f', (0, 0, BASE, BASE), border_radius=8)
        pg.draw.rect(s, '#242337', (0, 0, BASE, BASE), 1, border_radius=8)
        for j in range(3):
            y = j * 12
            pg.draw.lines(s, '#373149', False, [(0, 16 + y), (12, 8 + y), (22, 16 + y), (37, 8 + y), (52, 12 + y)], 2)
        pg.draw.circle(s, '#796b98', (24, 24), 2)
        pg.draw.circle(s, '#524767', (31, 28), 2)
    else:
        ground, draw = ART[art]
        shift = (variant % 3 - 1) * 3                 # -3, 0 hoặc +3: làm nền sáng/tối nhẹ theo variant
        base = pg.Color(ground)
        color = (base.r + shift, base.g + shift, base.b + shift)    # màu nền đều đủ lớn nên không bị tràn 0..255
        pg.draw.rect(s, color, (0, 0, BASE, BASE), border_radius=6)
        for x, y in [(7, 8), (39, 41), (11, 43), (44, 7)]:        
            pg.draw.circle(s, '#405e4b', (x, y), 1)
        if draw is not None:
            draw(s, art, level, variant)

    if size == BASE:
        return s
    return pg.transform.smoothscale(s, (size, size))               # co/giãn về cỡ yêu cầu
