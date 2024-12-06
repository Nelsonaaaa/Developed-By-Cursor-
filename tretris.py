# -*- coding: utf-8 -*-
import pygame
import random
import sys
import math

# 初始化 Pygame
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 240, 240),  # 青色 - I
    (0, 0, 240),    # 蓝色 - J
    (240, 160, 0),  # 橙色 - L
    (240, 240, 0),  # 黄色 - O
    (0, 240, 0),    # 绿色 - S
    (160, 0, 240),  # 紫色 - T
    (240, 0, 0)     # 红色 - Z
]

# 游戏设置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]  # Z
]

print("ur being changed.")
class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('俄罗斯方块')
        
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        
        # 设置自动下落
        pygame.time.set_timer(pygame.USEREVENT+1, 1000)
        
        # 使用系统默认中文字体
        try:
            self.font = pygame.font.SysFont('SimHei', 28)  # 使用黑体
        except:
            self.font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 28)  # 备选微软雅黑
        
        # 输入法提示相关变量
        self.input_warning = True
        self.warning_blink_time = 0
        self.warning_visible = True
        self.game_started = False  # 添加游戏开始标志
        
        self.game_start_time = pygame.time.get_ticks()  # 添加游戏开始时间
        self.total_pause_time = 0
        self.pause_start_time = 0
        
        # 烟花特效相关
        self.firework_particles = []
        self.firework_duration = 0
        self.firework_chars = ['★', '☆', '✦', '✧', '✺', '✹']  # 烟花字符
        self.firework_colors = [
            (255, 255, 0),   # 黄色
            (255, 165, 0),   # 橙色
            (255, 99, 71),   # 红色
            (255, 192, 203), # 粉色
            (147, 112, 219)  # 紫色
        ]

    def new_piece(self):
        # 随机选择一个方块形状
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        # 方块出现在屏幕顶部中间
        return {
            'shape': shape,
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0,
            'color': color
        }

    def valid_move(self, piece, x, y):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + j + x
                    new_y = piece['y'] + i + y
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True

    def merge_piece(self):
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']

    def rotate_piece(self):
        print("Rotating piece...")  # 添加调试信息
        # 获取当前形状的行数和列数
        rows = len(self.current_piece['shape'])
        cols = len(self.current_piece['shape'][0])
        
        # 创建新的旋转后的形状
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for i in range(rows):
            for j in range(cols):
                rotated[j][rows-1-i] = self.current_piece['shape'][i][j]
        
        # 打印旋转前后的形状（调试用）
        print("Original shape:", self.current_piece['shape'])
        print("Rotated shape:", rotated)
        
        # 保存原来的形状
        old_shape = self.current_piece['shape'].copy()  # 使用copy()确保深度复制
        self.current_piece['shape'] = rotated
        
        # 如果旋转后的位置无效，则恢复原来的形状
        if not self.valid_move(self.current_piece, 0, 0):
            print("Invalid rotation, reverting...")  # 添加调试信息
            self.current_piece['shape'] = old_shape

    def clear_lines(self):
        lines_cleared = 0
        i = GRID_HEIGHT - 1
        while i >= 0:
            if all(cell for cell in self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                i -= 1
        return lines_cleared

    def create_firework(self):
        """创建一个新的烟花效果"""
        center_x = BLOCK_SIZE * (GRID_WIDTH + 3)
        center_y = SCREEN_HEIGHT - BLOCK_SIZE * 8
        
        num_particles = random.randint(8, 12)
        color = random.choice(self.firework_colors)
        
        for _ in range(num_particles):
            char = random.choice(self.firework_chars)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 3.5)
            
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            
            self.firework_particles.append({
                'x': center_x,
                'y': center_y,
                'dx': dx,
                'dy': dy,
                'char': char,
                'color': color,
                'life': random.randint(25, 35),  # 增加生命周期
                'size': random.randint(25, 35),
                'alpha': 255
            })
            
        self.firework_duration = 30  # 增加总持续时间

    def update_firework(self):
        """更新烟花动画"""
        if self.firework_duration > 0:
            self.firework_duration -= 1
            
            # 更新每个粒子
            for particle in self.firework_particles[:]:  # 使用切片创建副本进行迭代
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
                particle['dy'] += 0.1  # 减小重力效果
                particle['life'] -= 1
                
                # 更快地减少透明度
                particle['alpha'] = int((particle['life'] / 20.0) * 255)
                
                # 如果生命值耗尽或透明度为0，移除粒子
                if particle['life'] <= 0 or particle['alpha'] <= 0:
                    if particle in self.firework_particles:
                        self.firework_particles.remove(particle)
        else:
            # 强制清除所有剩余粒子
            self.firework_particles.clear()

    def draw(self):
        self.screen.fill(BLACK)
        
        # 绘制当前方块
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_piece['color'],
                                   (BLOCK_SIZE * (self.current_piece['x'] + j),
                                    BLOCK_SIZE * (self.current_piece['y'] + i),
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        
        # 绘制已固定的方块
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.grid[i][j]:
                    pygame.draw.rect(self.screen, self.grid[i][j],
                                   (BLOCK_SIZE * j, BLOCK_SIZE * i,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        
        # 绘制网格线
        for i in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, WHITE, 
                           (0, BLOCK_SIZE * i), 
                           (BLOCK_SIZE * GRID_WIDTH, BLOCK_SIZE * i))
        for j in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, WHITE,
                           (BLOCK_SIZE * j, 0),
                           (BLOCK_SIZE * j, SCREEN_HEIGHT))
        
        # 显示分数、时间和暂停状态
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (BLOCK_SIZE * (GRID_WIDTH + 1), 20))
        
        # 显示游戏时间
        game_time = pygame.time.get_ticks() - self.total_pause_time
        time_text = self.font.render(f'Time: {game_time//1000}s', True, WHITE)
        self.screen.blit(time_text, (BLOCK_SIZE * (GRID_WIDTH + 1), 60))
        
        # 显示暂停提示
        pause_text = self.font.render(f'Pause: S', True, WHITE)
        self.screen.blit(pause_text, (BLOCK_SIZE * (GRID_WIDTH + 1), 100))
        
        # 显示输入法提示
        if self.input_warning and self.warning_visible:
            warning_text = self.font.render('请切换至英文输入法!', True, (255, 200, 0))
            self.screen.blit(warning_text, (BLOCK_SIZE * (GRID_WIDTH + 0.5), 140))
        
        # 在暂停状态下显示PAUSED文字
        if self.paused:
            # 创建半透明的黑色遮罩
            pause_surface = pygame.Surface((BLOCK_SIZE * GRID_WIDTH, SCREEN_HEIGHT))
            pause_surface.set_alpha(128)  # 设置透明度
            pause_surface.fill(BLACK)
            self.screen.blit(pause_surface, (0, 0))
            
            # 显示PAUSED文字
            paused_font = pygame.font.Font(None, 74)  # 使用更大的字号
            paused_text = paused_font.render('PAUSED', True, WHITE)
            paused_rect = paused_text.get_rect(center=(BLOCK_SIZE * GRID_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(paused_text, paused_rect)
        
        # 绘制烟花粒子
        for particle in self.firework_particles:
            if particle['life'] > 0:
                particle_font = pygame.font.SysFont('simhei', particle['size'])
                particle_text = particle_font.render(particle['char'], True, particle['color'])
                particle_text.set_alpha(particle['alpha'])  # 设置透明度
                self.screen.blit(particle_text, (particle['x'], particle['y']))
        
        pygame.display.flip()

    def update_warning_blink(self):
        """更新警告文本的闪烁状态"""
        current_time = pygame.time.get_ticks()
        if current_time - self.warning_blink_time > 500:  # 每500毫秒闪烁一次
            self.warning_visible = not self.warning_visible
            self.warning_blink_time = current_time

    def run(self):
        # 游戏暂停相关变量
        self.paused = False
        self.game_start_time = pygame.time.get_ticks()  # 设置游戏开始时间
        self.total_pause_time = 0
        self.pause_start_time = 0
        self.down_key_pressed = False
        self.down_key_start_time = 0
        
        while not self.game_over:
            self.update_warning_blink()
            
            # 更新烟花粒子
            if self.firework_particles:
                self.update_firework()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    # 任意键按下时，如果游戏未开始，则标记游戏开始并隐藏提示
                    if not self.game_started:
                        self.game_started = True
                        self.input_warning = False
                    
                    # S键暂停处理
                    if event.key == pygame.K_s:
                        self.paused = not self.paused
                        current_time = pygame.time.get_ticks()
                        if self.paused:
                            self.pause_start_time = current_time
                        else:
                            self.total_pause_time += current_time - self.pause_start_time
                    
                    # 其他按键只在非暂停状态下处理
                    elif not self.paused:
                        if event.key == pygame.K_LEFT:
                            if self.valid_move(self.current_piece, -1, 0):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_RIGHT:
                            if self.valid_move(self.current_piece, 1, 0):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_DOWN:
                            self.down_key_pressed = True
                            self.down_key_start_time = pygame.time.get_ticks()
                        elif event.key == pygame.K_r:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            while self.valid_move(self.current_piece, 0, 1):
                                self.current_piece['y'] += 1
                
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.down_key_pressed = False
                
                # 处理方块自下落
                elif not self.paused and event.type == pygame.USEREVENT+1:
                    if self.valid_move(self.current_piece, 0, 1):
                        self.current_piece['y'] += 1
                    else:
                        self.merge_piece()
                        lines_cleared = self.clear_lines()
                        if lines_cleared:
                            self.score += lines_cleared * 100
                            self.create_firework()  # 触发烟花效果
                        self.current_piece = self.next_piece
                        self.next_piece = self.new_piece()
                        if not self.valid_move(self.current_piece, 0, 0):
                            self.game_over = True
            
            # 处理长按向下键
            if not self.paused and self.down_key_pressed:
                current_time = pygame.time.get_ticks()
                if current_time - self.down_key_start_time >= 100:  # 调整下落速度
                    if self.valid_move(self.current_piece, 0, 1):
                        self.current_piece['y'] += 1
            
            # 更新显示
            self.draw()
            self.clock.tick(60)

# 创建游戏实并运行
if __name__ == '__main__':
    game = Tetris()
    game.run()
