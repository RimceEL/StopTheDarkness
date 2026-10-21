
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'         
import pygame as pg
from world import World, KINDS, UPGRADES, N, RESOURCE_NAMES
from assets import (BG, PANEL, PANEL2, LINE, WHITE, MUTED, MINT, RED, COLORS,
                    tile_art, resource_icon)

WIDTH, HEIGHT = 1280, 880                               
BOARD_X, BOARD_Y, CELL = 40, 204, 52                    
FONTS = {}                                            


def font(size, bold=False):
    """Lấy font theo cỡ chữ. Mỗi font chỉ tạo 1 lần rồi cất vào FONTS (tạo font mỗi khung hình sẽ rất chậm)."""
    if (size, bold) not in FONTS:
        FONTS[(size, bold)] = pg.font.SysFont('avenirnext,helveticaneue,trebuchetms,tahoma,segoeui,arial', size, bold)
    return FONTS[(size, bold)]


def txt(surface, value, x, y, size=18, color=WHITE, bold=False, align='left'):
    """Viết 1 dòng chữ. align='left': x là mép trái; 'center': x là giữa; 'right': x là mép phải."""
    image = font(size, bold).render(str(value), True, color)
    r = image.get_rect(topleft=(x, y))
    if align == 'center':
        r.centerx = x
    elif align == 'right':
        r.right = x
    surface.blit(image, r)


def paragraph(s, value, x, y, width, size=17, color=MUTED, spacing=5):
    """Viết đoạn văn, tự xuống dòng khi vượt quá `width` pixel. Trả về y của dòng kế tiếp."""
    row = ''                                            
    for word in value.split():
        if row != '' and font(size).size(row + ' ' + word)[0] > width:
            txt(s, row, x, y, size, color)              
            y += size + spacing
            row = word                                
        else:
            row = (row + ' ' + word).strip()
    txt(s, row, x, y, size, color)                     
    return y + size + spacing


def box(s, r, color=PANEL, border=None, radius=16):
    """Vẽ hình chữ nhật bo góc r = (x, y, rộng, cao), có thể kèm viền."""
    pg.draw.rect(s, color, r, border_radius=radius)
    if border is not None:
        pg.draw.rect(s, border, r, 1, border_radius=radius)


def fmt(n):
    """Số đẹp để hiện: 12 -> '12', 2.5 -> '2.5', 12000 -> '12.0k'."""
    if n >= 10000:
        return f'{n / 1000:.1f}k'
    if abs(n - round(n)) < .05:                        
        return str(int(n))
    return f'{n:.1f}'



class Game:
    def __init__(self):
        pg.init()
        self.s = pg.display.set_mode((WIDTH, HEIGHT))   
        pg.display.set_caption('Stop the Darkness · Ánh sáng cuối cùng')
        pg.display.set_icon(tile_art('light', 2, 64))
        self.clock = pg.time.Clock()
        self.running = True
        self.scene = 'menu'           
        self.mouse = (0, 0)           # vị trí chuột khung hình này
        self.click = False            # khung hình này có bấm chuột trái không
        self.world = World()          # bản đồ hiện tại
        self.selected = 0             # chỉ số ô đang chọn
        self.hover = None             # chỉ số ô chuột đang trỏ vào (None nếu ngoài bản đồ)
        self.dt = 0                   # số giây của khung hình vừa rồi
        self.message = ''             # thông báo sau khi bấm nâng cấp
        self.win_seen = False        

    # thành phần dùng chung
    def button(self, label, r, primary=False):
        """Vẽ nút r = (x, y, rộng, cao). Trả về True nếu khung hình này nút vừa được bấm.
        primary=True: nút nổi bật (nền xanh)."""
        r = pg.Rect(r)
        hot = r.collidepoint(self.mouse)                
        if primary:
            if hot:
                color = '#b0edbf'
            else:
                color = MINT
            text_color = BG
            border = None
        else:
            if hot:
                color = '#29434a'
            else:
                color = PANEL2
            text_color = WHITE
            border = LINE
        box(self.s, r, color, border, 12)
        txt(self.s, label, r.centerx, r.y + (r.height - 22) // 2, 17, text_color, True, 'center')
        return hot and self.click

    def header(self):
        """Phần đầu trang: tên game; ở màn chơi thì thêm thông tin bóng tối và nút Menu."""
        txt(self.s, 'STOP THE DARKNESS', 40, 23, 24, WHITE, True)
        txt(self.s, 'ÁNH SÁNG CUỐI CÙNG', 40, 54, 11, MINT, True)
        if self.scene == 'game':
            w = self.world
            if w.won:
                txt(self.s, 'Bóng tối đã dừng vĩnh viễn', 1136, 36, 15, MINT, True, 'right')
            else:
                seconds = max(0, w.dark_timer)
                txt(self.s, f'Bóng tối {len(w.dark)}/{N * N} ô  ·  ô kế tiếp sau {seconds:.0f}s',
                    1136, 36, 15, RED, True, 'right')
            if self.button('Menu', (1158, 26, 82, 40)):
                self.scene = 'menu'

    def cell_at(self, pos):
        """Đổi vị trí pixel thành chỉ số ô trên bản đồ. Nằm ngoài bản đồ thì trả về None."""
        cx = (pos[0] - BOARD_X) // CELL                 # cột
        cy = (pos[1] - BOARD_Y) // CELL                 # hàng
        if 0 <= cx < N and 0 <= cy < N:
            return cy * N + cx
        return None

    def board(self, interactive=False):
        """Vẽ bản đồ. interactive=True (màn chơi) thì vẽ thêm các viền chọn/trỏ/cảnh báo."""
        box(self.s, (28, 192, 648, 648), '#152b2d', LINE, 22)
        for i in range(N * N):
            k = KINDS[self.world.tiles[i]]
            x = BOARD_X + i % N * CELL                
            y = BOARD_Y + i // N * CELL                 
            is_dark = i in self.world.dark
            self.s.blit(tile_art(k.art, k.level, CELL - 4, i % 3, is_dark), (x + 2, y + 2))

            if interactive:
                if i == self.world.next_dark and not self.world.won and not self.world.lost:
                    pg.draw.rect(self.s, RED, (x + 1, y + 1, CELL - 2, CELL - 2), 1, border_radius=8)   # ô sắp bị chiếm
                if i == self.selected:
                    pg.draw.rect(self.s, MINT, (x, y, CELL, CELL), 2, border_radius=9)                  # ô đang chọn
                elif i == self.hover:
                    pg.draw.rect(self.s, '#89afa1', (x + 1, y + 1, CELL - 2, CELL - 2), 1, border_radius=8)

    # ---------- màn menu ----------
    def menu(self):
        self.header()
        self.board()

        for x, y in [(718, 127), (1183, 151), (1234, 773), (1150, 824), (695, 842)]:    
            pg.draw.circle(self.s, '#627f71', (x, y), 2)

        box(self.s, (708, 185, 532, 656), PANEL, LINE, 24)
        txt(self.s, 'MỘT THẾ GIỚI NHỎ. MỘT CƠ HỘI CUỐI.', 744, 220, 12, MINT, True)
        txt(self.s, 'GIỮ LẠI ÁNH SÁNG', 740, 255, 50, WHITE, True)
        paragraph(self.s, 'Xây làng. Kết nối tài nguyên. Đánh thức phép thuật trước khi bóng tối nuốt chửng vùng đất của bạn.',
                  744, 395, 444, 20, WHITE, 7)

       
        for y, art, title, desc in [(511, 'village', 'Phát triển từng ô', 'Các ô kề nhau tăng sức mạnh cho nhau.'),
                                    (571, 'light', 'Chạy đua với bóng tối', 'Hai con đường: phép thuật hoặc công nghệ.')]:
            box(self.s, (744, y, 44, 44), PANEL2, LINE, 8)
            self.s.blit(tile_art(art, 1, 36), (748, y + 4))
            txt(self.s, title, 804, y + 2, 18, WHITE, True)
            txt(self.s, desc, 804, y + 26, 15, MUTED)

        if self.button('Bắt đầu ván mới', (744, 640, 460, 52), True):
            self.scene = 'game'
            self.world = World(self.world.seed)                  # ván mới nhưng giữ nguyên bản đồ đang xem
            self.win_seen = False
            self.message = ''
            self.selected = self.world.tiles.index('circle1')    # mở đầu chọn sẵn Vòng đá
        if self.button('Đổi bản đồ', (744, 704, 460, 46)):
            self.world = World()                                 # seed mới -> bản đồ mới

        txt(self.s, f'BẢN ĐỒ #{self.world.seed}  ·  STANDARD  ·  12 × 12', 744, 773, 12, MUTED, True)
        txt(self.s, 'Cơ chế tham khảo: Stop the Darkness / Florian van Strien', 40, 853, 13, MUTED)

    # màn chơi: các khung thông tin
    def resources(self):
        """4 ô tài nguyên ở trên cùng: số lượng hiện có và sản lượng mỗi phút."""
        rates = self.world.rates()
        for j in range(4):
            x = 40 + j * 302
            box(self.s, (x, 90, 294, 82))
            resource_icon(self.s, j, x + 27, 116, 21)
            txt(self.s, RESOURCE_NAMES[j].upper(), x + 47, 102, 12, MUTED, True)
            txt(self.s, fmt(self.world.resources[j]), x + 20, 126, 28, COLORS[j], True)
            txt(self.s, '+' + fmt(rates[j]) + ' / phút', x + 275, 136, 15, MUTED, False, 'right')

    def tile_info(self, i):
        """Nửa trên của khung bên phải: ảnh, tên, sản lượng, cộng hưởng và mô tả của ô i."""
        w = self.world
        k = KINDS[w.tiles[i]]
        is_dark = i in w.dark

        txt(self.s, 'VÙNG ĐẤT ĐANG CHỌN', 728, 211, 12, MUTED, True)
        self.s.blit(tile_art(k.art, k.level, 70, i % 3, is_dark), (728, 243))
        if is_dark:
            txt(self.s, 'Bóng tối', 816, 247, 24, WHITE, True)
        else:
            txt(self.s, k.name, 816, 247, 24, WHITE, True)
        txt(self.s, f'Cột {i % N + 1} · Hàng {i // N + 1} · Cấp {k.level}', 816, 283, 15, MUTED)

        # sản lượng thực tế của ô (đã tính cộng hưởng từ ô kề), chỉ hiện tài nguyên nào > 0
        production = w.tile_production(i)
        x = 728
        shown = False
        for r in range(4):
            if production[r] > 0:
                resource_icon(self.s, r, x + 9, 339, 16)
                txt(self.s, '+' + fmt(production[r]) + '/ph', x + 25, 328, 16, COLORS[r], True)
                x += 112
                shown = True
        if not shown:
            txt(self.s, 'Chưa sản xuất tài nguyên', 728, 328, 16, MUTED)

        # cộng hưởng: ô này làm 4 ô kề bên sản xuất nhiều hơn bao nhiêu %
        if not is_dark:
            boost_text = ''
            for r in range(4):
                if k.boost[r] > 0:
                    if boost_text != '':
                        boost_text += ' · '
                    boost_text += f'{RESOURCE_NAMES[r]} +{int(k.boost[r] * 100)}%'
            if boost_text != '':
                txt(self.s, 'Cộng hưởng ô kề bên: ' + boost_text, 728, 358, 15, MINT)

        # mô tả
        if is_dark:
            description = 'Tài nguyên và hiệu ứng tại đây đã ngừng hoạt động.'
        else:
            description = k.description
        paragraph(self.s, description, 728, 388, 478, 16, MUTED)
        pg.draw.line(self.s, LINE, (728, 470), (1216, 470))

    def upgrade_box(self, i):
        """Khung 'NÂNG CẤP TIẾP THEO' của ô i. Có 4 trường hợp:
        ô bị tối / chưa đủ điều kiện (hiện gợi ý) / đã tối đa / nâng cấp được (hiện chi phí + nút)."""
        w = self.world
        txt(self.s, 'NÂNG CẤP TIẾP THEO', 728, 490, 12, MUTED, True)
        box(self.s, (728, 520, 488, 100), PANEL2, None, 12)

        u = w.upgrade_for(i)
        if i in w.dark:
            txt(self.s, 'Vùng đất đã bị bóng tối chiếm', 972, 560, 16, RED, False, 'center')

        elif u is None:
            # không nâng cấp được: gom các câu gợi ý điều kiện của loại ô này để người chơi biết cần gì
            hints = ''
            if w.tiles[i] in UPGRADES:
                for option in UPGRADES[w.tiles[i]]:
                    if option.hint != '':
                        hints += option.hint + ' '
            if hints != '':
                paragraph(self.s, 'Chưa đủ điều kiện. ' + hints, 744, 532, 456, 15, MUTED, 4)
            else:
                txt(self.s, 'Ô này đã nâng cấp tối đa', 972, 560, 16, MUTED, False, 'center')

        else:
            target = KINDS[u.target]
            txt(self.s, f'{target.name} · cấp {target.level}', 744, 530, 18, WHITE, True)

            # chi phí: mỗi tài nguyên cần > 0 thì vẽ icon + số. Thiếu tài nguyên thì số màu đỏ.
            cost = w.cost(u.target)
            x = 744
            for r in range(4):
                if cost[r] > 0:
                    if w.resources[r] >= cost[r]:
                        color = COLORS[r]
                    else:
                        color = RED
                    resource_icon(self.s, r, x + 9, 580, 16)
                    txt(self.s, fmt(cost[r]), x + 25, 570, 16, color, True)
                    x += 90

            # nút nâng cấp: chỉ nổi bật khi đủ tiền
            affordable = w.can_afford(u.target)
            if affordable:
                label = 'Nâng cấp  [U]'
            else:
                label = 'Chưa đủ tài nguyên'
            if self.button(label, (728, 628, 488, 36), affordable):
                self.do_upgrade()

    def neighbour_row(self, i):
        """Hàng 4 ô kề bên của ô i ở phía dưới khung bên phải."""
        w = self.world
        txt(self.s, '4 Ô KỀ BÊN · KHÔNG TÍNH ĐƯỜNG CHÉO', 728, 675, 12, MUTED, True)
        neighbours = w.neighbours(i)
        for j in range(len(neighbours)):
            other = neighbours[j]
            k = KINDS[w.tiles[other]]
            other_dark = other in w.dark
            x = 728 + j * 123
            self.s.blit(tile_art(k.art, k.level, 43, other % 3, other_dark), (x, 700))
            if other_dark:
                txt(self.s, 'Tối', x, 751, 12, MUTED)
            else:
                txt(self.s, 'Cấp ' + str(k.level), x + 52, 703, 14, MUTED)
                txt(self.s, k.name, x, 751, 12, MUTED)

    def selected_panel(self):
        """Khung thông tin bên phải = thông tin ô + nâng cấp + ô kề + thanh thông báo."""
        box(self.s, (704, 192, 536, 648), PANEL, LINE, 22)
        self.tile_info(self.selected)
        self.upgrade_box(self.selected)
        self.neighbour_row(self.selected)

        box(self.s, (728, 789, 488, 30), '#1e3539', None, 9)
        if self.message != '':
            text = self.message
        else:
            text = 'Nhấn vào một ô trên bản đồ để xem thông tin'
        txt(self.s, text, 972, 795, 12, MINT, False, 'center')

    def do_upgrade(self):
        """Nâng cấp ô đang chọn. World trả về câu thông báo (thành công hoặc lý do thất bại)."""
        self.message = self.world.upgrade(self.selected)

    # bảng thắng / thua 
    def popup(self):
        """Có đang phải hiện bảng thắng/thua không? (thua, hoặc vừa thắng mà chưa bấm đóng)"""
        return self.world.lost or (self.world.won != '' and not self.win_seen)

    def result_popup(self):
        """Vẽ bảng thắng/thua đè lên màn chơi."""
        w = self.world
        shade = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)   
        shade.fill((5, 10, 14, 200))
        self.s.blit(shade, (0, 0))
        box(self.s, (320, 260, 640, 330), PANEL, LINE, 24)

        if w.won != '':
            txt(self.s, 'BÓNG TỐI ĐÃ BỊ CHẶN', 640, 295, 30, MINT, True, 'center')
            saved = N * N - len(w.dark)                      # số ô còn sáng
            paragraph(self.s, f'Bạn chiến thắng bằng {w.won.lower()}. {saved} ô đất đã được cứu.',
                      360, 360, 560, 20, WHITE, 8)
            if self.button('Tiếp tục xây dựng', (360, 500, 270, 48), True):
                self.win_seen = True                         # đóng bảng, chơi tiếp (bóng tối đã dừng)
            if self.button('Về menu', (650, 500, 270, 48)):
                self.scene = 'menu'
        else:
            txt(self.s, 'BÓNG TỐI ĐÃ NUỐT CHỬNG', 640, 295, 30, RED, True, 'center')
            paragraph(self.s, 'Bóng tối đã lan khắp bản đồ. Hãy nâng rừng sớm và xây làng sát nguồn tài nguyên trong ván sau.',
                      360, 360, 560, 20, WHITE, 8)
            if self.button('Về menu', (360, 500, 560, 48), True):
                self.scene = 'menu'

    # màn chơi
    def game(self):
        """Một khung hình của màn chơi: cập nhật thế giới, rồi vẽ."""
        popup = self.popup()                  # chốt trạng thái bảng thắng/thua ngay đầu khung hình
        real_click = self.click
        if popup:
            self.click = False                # đang có bảng: tạm coi như không bấm, để không lọt xuống bản đồ phía sau
        else:
            self.world.update(self.dt)        # cộng tài nguyên + cho bóng tối lan

        self.header()
        self.resources()

        # chuột trỏ vào ô nào? bấm thì chọn ô đó
        self.hover = self.cell_at(self.mouse)
        if self.hover is not None and self.click:
            self.selected = self.hover

        txt(self.s, 'THẾ GIỚI CỦA BẠN', 40, 178, 12, MUTED, True)
        self.board(interactive=True)
        self.selected_panel()
        txt(self.s, f'#{self.world.seed}  ·  {N * N} ô', 40, 853, 13, MUTED)

        if popup:
            self.click = real_click           
            self.result_popup()

    #vòng lặp chính
    def run(self):
        while self.running:
            self.dt = min(self.clock.tick(120) / 1000, .1)
            self.mouse = pg.mouse.get_pos()
            self.click = False

            # đọc các sự kiện (đóng cửa sổ, bấm chuột, bấm phím) đã xảy ra từ khung hình trước
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.running = False
                elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    self.click = True
                elif e.type == pg.KEYDOWN and (e.key == pg.K_u or e.key == pg.K_RETURN):
                    if self.scene == 'game' and not self.popup():
                        self.do_upgrade()                    

            self.s.fill(BG)                                  # xoá màn hình rồi vẽ lại từ đầu
            if self.scene == 'menu':
                self.menu()
            else:
                self.game()
            pg.draw.circle(self.s, '#f5f8f6', self.mouse, 7)  
            pg.display.flip()                                
        pg.quit()


if __name__ == '__main__':
    Game().run()
