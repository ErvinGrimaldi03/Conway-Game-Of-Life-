import pygame
import random


class GameOfLife:
    BLACK = (0, 0, 0)
    GREY = (128, 128, 128)
    YELLOW = (255, 255, 0)

    def __init__(self, width=720, height=720, title_size=20, fps=120):
        pygame.init()
        pygame.font.init()

        self.width = width
        self.height = height
        self.title_size = title_size
        self.fps = fps
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.grid = Grid(width, height, title_size)
        self.running = True
        self.playing = False
        self.menu = Menu(self.screen, self.width, self.height, self.start_game)

    def run(self):
        count = 0
        freq = 120

        while self.running:
            if self.menu.active:
                self.menu.run()
            else:
                self.clock.tick(self.fps)

                if self.playing:
                    count += 1

                if count >= freq:
                    count = 0
                    self.grid.update_cells()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.grid.toggle_cell(pygame.mouse.get_pos())
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.playing = not self.playing
                        elif event.key == pygame.K_c:
                            self.grid.clear()
                            self.playing = False
                        elif event.key == pygame.K_g:
                            self.grid.generate_random()

                self.screen.fill(GameOfLife.GREY)
                self.grid.draw(self.screen)

                if not self.playing and not self.menu.active:
                    self.draw_text("GAME STOP", 40, self.width // 2, self.height // 2)

                pygame.display.update()

        pygame.quit()

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(pygame.font.get_default_font(), size)
        text_surface = font.render(text, True, GameOfLife.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def start_game(self):
        self.menu.active = False
        self.playing = False
        self.grid.clear()


class Menu:
    def __init__(self, screen, width, height, start_game_callback):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = True
        self.options = ["New Game", "Exit"]
        self.selected = 0
        self.start_game_callback = start_game_callback

    def run(self):
        self.screen.fill(GameOfLife.GREY)
        self.draw_options()
        pygame.display.update()
        self.handle_events()

    def draw_options(self):
        for i, option in enumerate(self.options):
            if i == self.selected:
                color = GameOfLife.YELLOW
            else:
                color = GameOfLife.BLACK
            self.draw_text(option, 40, self.width // 2, self.height // 2 + i * 50, color)

    def draw_text(self, text, size, x, y, color):
        font = pygame.font.Font(pygame.font.get_default_font(), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key is pygame.K_RETURN:
                    self.select_option()

    def select_option(self):
        if self.options[self.selected] == "New Game":
            self.start_game_callback()
        elif self.options[self.selected] == "Exit":
            pygame.quit()
            exit()


class Grid:
    def __init__(self, width, height, title_size):
        self.width = width
        self.height = height
        self.title_size = title_size
        self.grid_width = width // title_size
        self.grid_height = height // title_size
        self.positions = set()

    def draw(self, screen):
        for position in self.positions:
            column, row = position
            top_left = (column * self.title_size, row * self.title_size)
            pygame.draw.rect(screen, GameOfLife.YELLOW, (*top_left, self.title_size, self.title_size))

        for row in range(self.grid_height):
            pygame.draw.line(screen, GameOfLife.BLACK, (0, row * self.title_size), (self.width, row * self.title_size))
            for column in range(self.grid_width):
                pygame.draw.line(screen, GameOfLife.BLACK, (column * self.title_size, 0),
                                 (column * self.title_size, self.height))

    def update_cells(self):
        new_positions = set()
        all_neighbors = set()

        for position in self.positions:
            neighbors = self.get_neighbors(position)
            all_neighbors.update(neighbors)
            neighbors = list(filter(lambda x: x in self.positions, neighbors))

            if len(neighbors) in [2, 3]:
                new_positions.add(position)

        for position in all_neighbors:
            neighbors = self.get_neighbors(position)
            neighbors = list(filter(lambda x: x in self.positions, neighbors))

            if len(neighbors) == 3:
                new_positions.add(position)

        self.positions = new_positions

    def get_neighbors(self, position):
        x, y = position
        neighbors = []
        for dx in [-1, 0, 1]:
            if x + dx < 0 or x + dx >= self.grid_width:
                continue
            for dy in [-1, 0, 1]:
                if y + dy < 0 or y + dy >= self.grid_height:
                    continue
                if dx == 0 and dy == 0:
                    continue
                neighbors.append((x + dx, y + dy))
        return neighbors

    def toggle_cell(self, mouse_pos):
        x, y = mouse_pos
        column = x // self.title_size
        row = y // self.title_size
        pos = (column, row)
        if pos in self.positions:
            self.positions.remove(pos)
        else:
            self.positions.add(pos)

    def clear(self):
        self.positions.clear()

    def generate_random(self):
        num = random.randrange(2, 5) * self.grid_width
        self.positions = set(
            [(random.randrange(0, self.grid_height), random.randrange(0, self.grid_width)) for _ in range(num)])
