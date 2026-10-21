import random

N = 12                                            # bản đồ N x N ô
RESOURCE_NAMES = ('Gỗ', 'Đá', 'Phép thuật', 'Công nghệ')
ZERO = (0, 0, 0, 0)                               # 4 số luôn theo thứ tự (gỗ, đá, phép thuật, công nghệ)
DARK_SECONDS = 6.25                               # bóng tối chiếm 1 ô mất bấy nhiêu giây (khi chưa có tháp)



class Kind:
    """Thông tin của một loại ô. Class này chỉ để chứa dữ liệu, không có logic."""

    def __init__(self, name, level, art, cost=ZERO, production=ZERO, boost=ZERO, tags=None, description=''):
        self.name = name             
        self.level = level          
        self.art = art                # tên kiểu hình ảnh, dùng cho tile_art() trong assets.py
        self.cost = cost             
        self.production = production  # tài nguyên tự sản xuất mỗi phút
        self.boost = boost            # cộng hưởng cho 4 ô kề bên (0.25 = +25% sản lượng của ô kề)
        if tags is None:
            tags = {}
        self.tags = tags              
        self.description = description


# NHÃN (tags): mỗi ô mang vài nhãn kèm một con số (thường là cấp độ).
# Điều kiện nâng cấp chỉ cần hỏi "kề mấy ô có nhãn X cấp >= Y" mà không cần biết tên từng loại ô.
#   forest        rừng: rừng non = 0, rừng cấp 1..4 = 1..4
#   rock          mỏ đá cấp 1..4
#   mushroom      rừng nấm cấp 1..2
#   village       MỌI loại làng và thành phố: làng = 1, làng cấp 2 = 2, thành phố = 3, thành phố cấp 2 = 4
#   magicvillage  làng phép thuật: 1, 2, thành phố phép thuật = 3
#   light         tháp ánh sáng cấp 1..2
#   slow          mức làm chậm bóng tối của tháp (cộng dồn lại)
#   finished      có nhãn này (= 1) nghĩa là ô đã nâng cấp tối đa
#   magicEnough   có làng phép thuật cấp 2 trở lên (điều kiện mở Vòng đá ánh sáng)
#   magiccity     thành phố phép thuật (mỗi bản đồ chỉ được 1)
#   win           ô chiến thắng
KINDS = {
    'grass': Kind('Đồng cỏ', 1, 'grass', description='Đất trống. Ô kề bên quyết định công trình có thể xây.'),
    'water': Kind('Mặt hồ', 1, 'water', tags={'finished': 1}, description='Mặt hồ. Ô kề hồ được tính là ô đã nâng cấp tối đa.'),

    'sapling': Kind('Rừng non', 0, 'forest', cost=(1, 0, 0, 0), tags={'forest': 0}),
    'forest1': Kind('Rừng', 1, 'forest', cost=(2, 0, 0, 0), boost=(.25, 0, 0, 0), tags={'forest': 1},
                    description='Cung cấp gỗ cho các công trình ở gần.'),
    'forest2': Kind('Rừng', 2, 'forest', cost=(2, 0, 0, 0), production=(3, 0, 0, 0), boost=(.25, 0, 0, 0), tags={'forest': 2}),
    'forest3': Kind('Rừng', 3, 'forest', cost=(5, 0, 0, 0), production=(5, 0, 0, 0), boost=(.25, 0, 0, 0), tags={'forest': 3}),
    'forest4': Kind('Rừng', 4, 'forest', cost=(8, 5, 0, 0), production=(10, 0, 0, 0), boost=(.5, 0, 0, 0),
                    tags={'forest': 4, 'finished': 1}),

    'mushroom1': Kind('Rừng nấm', 1, 'mushroom', tags={'mushroom': 1},
                      description='Nguồn phép thuật đầu tiên. Nền tảng của đường phép thuật.'),
    'mushroom2': Kind('Rừng nấm', 2, 'mushroom', cost=(6, 0, 0, 0), production=(1, 0, 2, 0),
                      tags={'mushroom': 2, 'finished': 1}),
    'rock1': Kind('Mỏ đá', 1, 'rock', tags={'rock': 1}, description='Mỏ đá nhỏ. Nâng cấp để bắt đầu khai thác đá.'),
    'rock2': Kind('Mỏ đá', 2, 'rock', cost=(8, 0, 0, 0), production=(0, 3, 0, 0), tags={'rock': 2}),
    'rock3': Kind('Mỏ đá', 3, 'rock', cost=(10, 3, 0, 0), production=(0, 7, 0, 0), tags={'rock': 3, 'finished': 1}),
    'rock4': Kind('Mỏ đá', 4, 'rock', cost=(12, 10, 0, 2), production=(0, 10, 0, 0), boost=(0, .25, 0, 0),
                  tags={'rock': 4, 'finished': 1}),

    'village1': Kind('Làng', 1, 'village', cost=(5, 0, 0, 0), boost=(.25, .25, 0, 0), tags={'village': 1}),
    'village2': Kind('Làng', 2, 'village', cost=(10, 4, 0, 0), boost=(.5, .5, 0, 0), tags={'village': 2, 'finished': 1}),
    'city1': Kind('Thành phố', 1, 'city', cost=(5, 30, 0, 0), production=(0, 0, 0, 2), boost=(.5, .5, 0, 0),
                  tags={'village': 3, 'finished': 1}),
    'city2': Kind('Thành phố', 2, 'city', cost=(10, 100, 0, 10), production=(0, 0, 0, 5), boost=(.5, .5, 0, .25),
                  tags={'village': 4, 'finished': 1}),

    'mining1': Kind('Làng khai mỏ', 1, 'mining', cost=(5, 2, 0, 0), production=(0, 2, 0, 0), boost=(0, .5, 0, 0),
                    tags={'village': 1}),
    'mining2': Kind('Làng khai mỏ', 2, 'mining', cost=(10, 5, 0, 0), production=(0, 5, 0, 0), boost=(0, 1, 0, 0),
                    tags={'village': 2, 'finished': 1}),
    'mining3': Kind('Thành phố nghiên cứu mỏ', 1, 'research', cost=(5, 35, 0, 0), production=(0, 5, 0, 2),
                    boost=(0, 2, 0, .25), tags={'village': 3, 'finished': 1}),
    'research': Kind('Thành phố nghiên cứu ánh sáng', 1, 'research', cost=(20, 150, 0, 35), production=(0, 5, 0, 4),
                     boost=(0, 2, 0, .5), tags={'village': 4, 'finished': 1, 'win': 1},
                     description='Chiến thắng bằng công nghệ: chặn bóng tối vĩnh viễn.'),

    'magic1': Kind('Làng phép thuật', 1, 'magicvillage', cost=(5, 0, 1, 0), production=(0, 0, 2, 0),
                   boost=(.25, 0, .25, 0), tags={'village': 1, 'magicvillage': 1}),
    'magic2': Kind('Làng phép thuật', 2, 'magicvillage', cost=(14, 2, 5, 0), production=(0, 0, 5, 0),
                   boost=(.5, 0, .5, 0), tags={'village': 2, 'magicvillage': 2, 'magicEnough': 1, 'finished': 1}),
    'magiccity': Kind('Thành phố phép thuật', 1, 'magiccity', cost=(35, 10, 10, 0), production=(0, 0, 10, 0),
                      boost=(1, 0, 1, 0),
                      tags={'village': 3, 'magicvillage': 3, 'magicEnough': 1, 'magiccity': 1, 'finished': 1}),
    'light1': Kind('Tháp ánh sáng', 1, 'light', cost=(25, 0, 15, 0), production=(0, 0, 1, 0),
                   tags={'light': 1, 'slow': .5},
                   description='Làm chậm bóng tối. Chỉ có một Tháp ánh sáng trên bản đồ.'),
    'light2': Kind('Tháp ánh sáng', 2, 'light', cost=(50, 0, 25, 0), production=(0, 0, 2, 0), boost=(0, 0, .25, 0),
                   tags={'light': 2, 'slow': 1, 'finished': 1},
                   description='Thời gian bóng tối chiếm một ô tăng gấp đôi.'),
    'circle1': Kind('Vòng đá', 1, 'circle', tags={'finished': 1},
                    description='Nâng làng phép thuật lên cấp 2 để mở nghi lễ chiến thắng.'),
    'circle2': Kind('Vòng đá ánh sáng', 2, 'circle', cost=(0, 100, 100, 0), tags={'finished': 1, 'win': 1},
                    description='Chiến thắng bằng phép thuật: chặn bóng tối vĩnh viễn.'),
}



class Upgrade:
    """Một cách nâng cấp: ô hiện tại -> `target`, nếu thoả hết điều kiện."""

    def __init__(self, target, needs=None, unique='', exists='', hint=''):
        self.target = target          
        if needs is None:
            needs = []
        self.needs = needs            # danh sách (nhãn, cấp tối thiểu, số ô kề). Phải thoả TẤT CẢ.
                                      # Ví dụ ('forest', 1, 3) = kề ít nhất 3 ô rừng từ cấp 1 trở lên
        self.unique = unique          # nếu trên bản đồ đã có ô mang nhãn này thì KHÔNG được nâng
        self.exists = exists          # trên bản đồ phải đã có ô mang nhãn này thì mới được nâng
        self.hint = hint              # câu giải thích điều kiện, hiện cho người chơi khi chưa đủ điều kiện


UPGRADES = {
    'grass': [
        Upgrade('light1', needs=[('magicvillage', 0, 1)], unique='light',
                hint='Tháp ánh sáng: kề 1 làng phép thuật, mỗi bản đồ chỉ 1 tháp.'),
        Upgrade('mining1', needs=[('rock', 0, 2)], hint='Làng khai mỏ: kề ít nhất 2 mỏ đá.'),
        Upgrade('magic1', needs=[('mushroom', 0, 1)], hint='Làng phép thuật: kề rừng nấm.'),
        Upgrade('sapling', needs=[('forest', 0, 3), ('village', 0, 1)], hint='Rừng non: kề 3 rừng và 1 làng.'),
        Upgrade('village1'),                      
    ],
    'sapling': [Upgrade('forest1')],
    'forest1': [Upgrade('forest2')],
    'forest2': [Upgrade('forest3')],
    'forest3': [Upgrade('forest4')],
    'rock1': [Upgrade('rock2')],
    'rock2': [Upgrade('rock3')],
    'rock3': [Upgrade('rock4')],
    'mushroom1': [Upgrade('mushroom2')],
    'village1': [Upgrade('village2')],
    'village2': [
        Upgrade('city1', needs=[('village', 2, 2)], hint='Thành phố: kề 2 làng cấp 2, hoặc 4 ô đã nâng cấp tối đa.'),
        Upgrade('city1', needs=[('finished', 1, 4)]),
    ],
    'city1': [Upgrade('city2')],
    'mining1': [Upgrade('mining2')],
    'mining2': [
        Upgrade('mining3', needs=[('finished', 1, 3)], hint='Thành phố nghiên cứu mỏ: kề 3 ô tối đa, hoặc 1 làng cấp 2.'),
        Upgrade('mining3', needs=[('village', 2, 1)]),
    ],
    'mining3': [Upgrade('research', unique='win', hint='Đủ chi phí là chiến thắng bằng công nghệ.')],
    'magic1': [Upgrade('magic2')],
    'magic2': [Upgrade('magiccity', needs=[('light', 2, 1)], unique='magiccity',
                       hint='Thành phố phép thuật: kề Tháp ánh sáng cấp 2.')],
    'light1': [Upgrade('light2', needs=[('magicvillage', 2, 1)], hint='Tháp cấp 2: kề làng phép thuật cấp 2.')],
    'circle1': [Upgrade('circle2', unique='win', exists='magicEnough',
                        hint='Cần có ít nhất 1 làng phép thuật cấp 2 trên bản đồ.')],
}


START_ZONES = [
    (3, 3, 'mushroom1'), (4, 3, 'grass'), (5, 3, 'grass'), (4, 2, 'grass'), (3, 4, 'grass'),
    (3, 2, 'grass'), (4, 4, 'grass'), (3, 5, 'forest1'), (2, 5, 'forest1'), (4, 5, 'forest1'),
    (3, 6, 'forest1'), (3, 7, 'forest1'),
    (8, 3, 'grass'), (7, 3, 'rock1'), (9, 3, 'rock1'), (8, 2, 'grass'), (8, 4, 'grass'),
    (7, 2, 'forest1'), (9, 2, 'forest1'), (8, 1, 'grass'), (7, 4, 'grass'), (9, 4, 'grass'),
    (6, 4, 'grass'), (10, 4, 'grass'), (7, 5, 'grass'), (7, 6, 'grass'), (8, 5, 'grass'),
    (6, 5, 'grass'),
]



def make_spiral():
    """Trả về danh sách chỉ số ô theo thứ tự bóng tối chiếm: xoắn ốc từ góc dưới trái vào tâm.

    Cách đi: bắt đầu ở góc dưới trái, đi sang PHẢI. Gặp mép bản đồ hoặc ô đã đi qua thì rẽ TRÁI.
    Thứ tự hướng: phải -> lên -> trái -> xuống -> phải ... cho tới khi đi hết N x N ô."""
    path = []
    visited = set()
    x, y = 0, N - 1                    
    dx, dy = 1, 0                      
    for step in range(N * N):
        i = y * N + x
        path.append(i)
        visited.add(i)

        # nhìn thử ô phía trước: nếu ra ngoài bản đồ hoặc đã đi qua thì rẽ trái
        next_x = x + dx
        next_y = y + dy
        out_of_map = next_x < 0 or next_x >= N or next_y < 0 or next_y >= N
        if out_of_map or (next_y * N + next_x) in visited:
            old_dx = dx                
            dx = dy
            dy = -old_dx
        x = x + dx
        y = y + dy
    return path


SPIRAL = make_spiral()                 

class World:
    def __init__(self, seed=None):
        if seed is None:
            seed = random.randrange(100000, 999999)
        self.seed = seed
        self.tiles = ['grass'] * (N * N)      
        self.resources = [12., 0., 0., 0.]   
        self.built = {}                       # đã xây bao nhiêu ô mỗi loại: {'village1': 2, ...} (để tính giá)
        self.dark = set()                     # chỉ số các ô đã bị bóng tối chiếm
        self.next_dark = SPIRAL[0]            # ô bóng tối sẽ chiếm tiếp theo
        self.dark_timer = .5                  # còn bao nhiêu giây nữa bóng tối chiếm ô kế tiếp
        self.won = ''                        
        self.lost = False                    
        self.generate()

    @staticmethod
    def neighbours(i):
        """Chỉ số các ô kề bên (phải, dưới, trái, trên), không tính đường chéo."""
        x, y = i % N, i // N
        result = []
        if x < N - 1: result.append(i + 1)
        if y < N - 1: result.append(i + N)
        if x > 0: result.append(i - 1)
        if y > 0: result.append(i - N)
        return result

    def generate(self):
        """Sinh bản đồ ngẫu nhiên theo seed."""
        rng = random.Random(self.seed)

        # 1. Rải ngẫu nhiên: rừng, đá, nấm, hồ. Ô còn lại là đồng cỏ.
        bag = (['forest1'] * rng.randint(35, 39) + ['rock1'] * rng.randint(12, 13)
               + ['mushroom1'] * 4 + ['water'] * 29)
        spots = list(range(N * N))
        rng.shuffle(spots)                   
        for n in range(len(bag)):            
            self.tiles[spots[n]] = bag[n]

        # 2. Vòng đá nằm ngay giữa bản đồ.
        circle = rng.choice((5, 6)) * N + rng.choice((5, 6))
        self.tiles[circle] = 'circle1'

        # 3. Đè 2 vùng khởi đầu lên (trừ ô vòng đá) để người chơi luôn có chỗ xây.
        for x, y, kind in START_ZONES:
            if y * N + x != circle:
                self.tiles[y * N + x] = kind

    # các hfm hỏi thông tin về bản đồ 
    def tag(self, i, name):
        """Giá trị nhãn `name` của ô i, hoặc -1 nếu ô không có nhãn đó.
        Ô đã bị bóng tối chiếm coi như không có nhãn nào."""
        if i in self.dark:
            return -1
        kind = KINDS[self.tiles[i]]
        if name in kind.tags:
            return kind.tags[name]
        return -1

    def count(self, i, name, level):
        """Đếm số ô KỀ ô i có nhãn `name` với giá trị >= level."""
        total = 0
        for j in self.neighbours(i):
            if self.tag(j, name) >= level:
                total += 1
        return total

    def exists(self, name):
        """Trên cả bản đồ có ô nào mang nhãn `name` không?"""
        for i in range(N * N):
            if self.tag(i, name) >= 0:
                return True
        return False

    def satisfies(self, i, u):
        """Ô i có thoả điều kiện của cách nâng cấp `u` không?"""
        if i in self.dark:
            return False
        for name, level, amount in u.needs:               
            if self.count(i, name, level) < amount:
                return False
        if u.unique != '' and self.exists(u.unique):      
            return False
        if u.exists != '' and not self.exists(u.exists):  
            return False
        return True

    def upgrade_for(self, i):
        """Cách nâng cấp đang khả dụng của ô i (thoả điều kiện, chưa tính tiền). Không có thì trả về None."""
        if self.tiles[i] not in UPGRADES:                 
            return None
        for u in UPGRADES[self.tiles[i]]:
            if self.satisfies(i, u):
                return u
        return None

    def cost(self, kind):
        """Chi phí thực tế để xây `kind`: mỗi lần đã xây loại này, giá tăng thêm 50% giá gốc."""
        times = 0
        if kind in self.built:
            times = self.built[kind]
        factor = 1 + 0.5 * times
        result = []
        for base in KINDS[kind].cost:
            result.append(int(base * factor))            
        return result

    def can_afford(self, kind):
        """Đủ tài nguyên để xây `kind` chưa?"""
        cost = self.cost(kind)
        for r in range(4):
            if self.resources[r] < cost[r]:
                return False
        return True

    def upgrade(self, i):
        """Nâng cấp ô i. Trả về câu thông báo để hiện cho người chơi."""
        if self.lost:
            return 'Ván chơi đã kết thúc.'
        u = self.upgrade_for(i)
        if u is None:
            return 'Ô này chưa có nâng cấp phù hợp.'
        if not self.can_afford(u.target):
            return 'Chưa đủ tài nguyên.'

        cost = self.cost(u.target)                        # phải tính giá TRƯỚC khi tăng số lần đã xây
        for r in range(4):
            self.resources[r] -= cost[r]
        self.tiles[i] = u.target
        if u.target in self.built:
            self.built[u.target] += 1
        else:
            self.built[u.target] = 1

        if 'win' in KINDS[u.target].tags:                
            if u.target == 'circle2':
                self.won = 'Phép thuật'
            else:
                self.won = 'Công nghệ'
        return KINDS[u.target].name + ' đã sẵn sàng.'

    # sản xuất
    def tile_production(self, i):
        """Sản lượng mỗi phút của ô i = sản xuất gốc x (1 + tổng cộng hưởng từ các ô kề bên)."""
        result = [0, 0, 0, 0]
        if i in self.dark:                              
            return result
        kind = KINDS[self.tiles[i]]
        for r in range(4):                                
            boost = 0
            for j in self.neighbours(i):
                if j not in self.dark:                   
                    boost += KINDS[self.tiles[j]].boost[r]
            result[r] = kind.production[r] * (1 + boost)
        return result

    def rates(self):
        """Tổng sản lượng mỗi phút của cả bản đồ."""
        total = [0, 0, 0, 0]
        for i in range(N * N):
            production = self.tile_production(i)
            for r in range(4):
                total[r] += production[r]
        return total

    #bóng tối 
    def dark_interval(self):
        """Số giây để bóng tối chiếm 1 ô. Mỗi tháp ánh sáng làm khoảng thời gian này dài ra."""
        slow = 0
        for i in range(N * N):
            if self.tag(i, 'slow') > 0:
                slow += self.tag(i, 'slow')
        return DARK_SECONDS * (1 + slow)

    def spread(self):
        """Bóng tối chiếm ô next_dark rồi chuyển sang ô kế tiếp trên đường xoắn ốc."""
        self.dark.add(self.next_dark)
        if len(self.dark) == N * N:                     
            self.lost = True
        else:
            self.next_dark = SPIRAL[len(self.dark)]
            self.dark_timer += self.dark_interval()

    def update(self, dt):
        """Gọi mỗi khung hình, dt = số giây từ khung hình trước: cộng tài nguyên và cho bóng tối lan."""
        if self.lost:
            return
        rates = self.rates()
        for r in range(4):
            self.resources[r] += rates[r] * dt / 60       # rates tính theo phút nên chia 60
        if self.won == '':                               
            self.dark_timer -= dt
            if self.dark_timer <= 0:
                self.spread()
