import pygame
import sys
import random

pygame.init()

BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
SCREEN_WIDTH = BLOCK_SIZE * COLUMNS
SCREEN_HEIGHT = BLOCK_SIZE * ROWS

BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
COLORS = {
    'I': (0, 255, 255),    # Cyan
    'O': (255, 255, 0),    # Yellow
    'T': (128, 0, 128),    # Purple
    'L': (255, 165, 0),    # Orange
    'J': (0, 0, 255),      # Blue
    'S': (0, 255, 0),      # Green
    'Z': (255, 0, 0),      # Red
}


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
score = 0

SHAPES = {
    'I': [(0, 0), (0, -1), (0, 1), (0, 2)],
    'O': [(0, 0), (0, 1), (1, 0), (1, 1)],
    'T': [(0, 0), (-1, 0), (1, 0), (0, 1)],
    'L': [(0, 0), (-1, 0), (1, 0), (1, 1)],
    'J': [(0, 0), (-1, 0), (1, 0), (-1, 1)],
    'S': [(0, 0), (1, 0), (0, 1), (-1, 1)],
    'Z': [(0, 0), (-1, 0), (0, 1), (1, 1)],
}


board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]

class Block:
    def __init__(self, shape):
        self.shape = shape
        self.color = COLORS[shape]
        self.positions = SHAPES[shape]
        self.x = COLUMNS // 2
        self.y = 0
    
    def rotate(self):
        if self.shape == 'O':
            return 

        new_positions = [(-py, px) for px, py in self.positions]

        for px, py in new_positions:
            nx, ny = self.x + px, self.y + py
            if nx < 0 or nx >= COLUMNS or ny < 0 or ny >= ROWS:
                return  
            if ny >= 0 and board[ny][nx]:
                return 

   
        self.positions = new_positions


    def get_cells(self):
        return [(self.x + px, self.y + py) for px, py in self.positions]

    def move(self, dx, dy):
        if self.valid_move(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def valid_move(self, dx, dy):
        for px, py in self.get_cells():
            nx, ny = px + dx, py + dy
            if nx < 0 or nx >= COLUMNS or ny < 0 or ny >= ROWS:
                return False
            if ny >= 0 and board[ny][nx]:
                return False
        return True

    def place(self):
        for px, py in self.get_cells():
            if 0 <= px < COLUMNS and 0 <= py < ROWS:
                board[py][px] = self.color

    

def draw_grid():
    for y in range(ROWS):
        for x in range(COLUMNS):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_board():
    for y in range(ROWS):
        for x in range(COLUMNS):
            if board[y][x]:
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, board[y][x], rect)
                pygame.draw.rect(screen, BLACK, rect, 2) 


def draw_block(block):
    for x, y in block.get_cells():
        if y >= 0:
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, block.color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2) 



def get_full_rows():
    return [y for y in range(ROWS) if all(board[y][x] is not None for x in range(COLUMNS))]

def animate_line_clear(full_rows):
    for _ in range(3):  # Flash 3 times
        for y in full_rows:
            for x in range(COLUMNS):
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, (255, 255, 255), rect)  # Flash white
        pygame.display.update()
        pygame.time.wait(60)

        draw_board()
        draw_grid()
        pygame.display.update()
        pygame.time.wait(60)

def clear_full_rows():
    global board, score

    full_rows = get_full_rows()
    if full_rows:
        animate_line_clear(full_rows)

    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared_lines = ROWS - len(new_board)

    for _ in range(cleared_lines):
        new_board.insert(0, [None for _ in range(COLUMNS)])

    board = new_board

    if cleared_lines == 1:
        score += 100
    elif cleared_lines == 2:
        score += 235
    elif cleared_lines == 3:
        score += 370
    elif cleared_lines == 4:
        score += 550

def draw_score():
    font = pygame.font.SysFont('Arial', 24)
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (10, 10))  

def draw_speed():
    font = pygame.font.SysFont('Arial', 24)
    speed_level = max(1, 30 - fall_delay + 1) 
    speed_text = font.render(f"Speed: {speed_level}", True, (255, 255, 255))
    screen.blit(speed_text, (10, 30))

def adjust_speed():
    global fall_delay
    fall_delay = max(10, 30 - (score // 350))  

def check_game_over(block):
    for x, y in block.get_cells():
        if y >= 0 and board[y][x] is not None:
            return True
    return False

def get_ghost_position(block):
    ghost = Block(block.shape)
    ghost.positions = block.positions.copy()
    ghost.x = block.x
    ghost.y = block.y

    while ghost.valid_move(0, 1):
        ghost.y += 1

    ghost.color = (200, 200, 200)  
    return ghost

# Function to draw the ghost piece
def draw_ghost(block):
    ghost = get_ghost_position(block)

    for x, y in ghost.get_cells():
        if y >= 0:
            ghost_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            ghost_surface.fill((*block.color, 100)) 
            screen.blit(ghost_surface, (x * BLOCK_SIZE, y * BLOCK_SIZE))
            pygame.draw.rect(screen, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

# Create initial block
current_block = Block(random.choice(list(SHAPES.keys())))

running = True
fall_timer = 0
fall_delay = 30
move_timer = 0 
move_delay = 8.5

while running:
    screen.fill(BLACK)
    draw_grid()
    draw_board()
    draw_block(current_block)
    adjust_speed()
    draw_score()
    draw_ghost(current_block)
    draw_speed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_block.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                current_block.move(1, 0)
            elif event.key == pygame.K_UP:
                current_block.rotate()
            elif event.key == pygame.K_SPACE:
                # Hard drop
                while current_block.move(0, 1):
                    pass
                current_block.place()
                clear_full_rows()
                current_block = Block(random.choice(list(SHAPES.keys())))
                if check_game_over(current_block):
                    font = pygame.font.SysFont(None, 48)
                    text = font.render("Game Over", True, (255, 0, 0))
                    screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 24))
                    pygame.display.update()
                    pygame.time.wait(2000)
                    running = False

    # Handle soft drop
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:  
        soft_drop = True
    else:
        soft_drop = False
    
    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        move_timer += 0.9
        if move_timer >= move_delay:
            if keys[pygame.K_LEFT]:  
                current_block.move(-1, 0)
            if keys[pygame.K_RIGHT]:  
                current_block.move(1, 0)
            move_timer = 0  

    if soft_drop:
        fall_delay = 7 
    else:
        fall_delay = 30 

    # Timer logic for block falling
    fall_timer += 1
    if fall_timer >= fall_delay:
        if not current_block.move(0, 1):
            current_block.place()
            clear_full_rows()
            current_block = Block(random.choice(list(SHAPES.keys())))
            if check_game_over(current_block):
                font = pygame.font.SysFont(None, 48)
                text = font.render("Game Over", True, (255, 0, 0))
                screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 24))
                pygame.display.update()
                pygame.time.wait(2000)
                running = False
        fall_timer = 0

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()

"""
Hold Piece System let the player store one block and swap it

Pause Menu / Restart Game

Sound Effects and Background Music

Bag System (true 7-bag randomizer for fairness)

High Score Tracking

Level Display and Animation Effects

Line Clear Animation

Improve Piece Rotation (Wall Kicks)
    """