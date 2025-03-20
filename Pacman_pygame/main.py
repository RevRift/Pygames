""" 

You are Vax-man

Vax-man is a yellow circle, the ghosts are blue circles
Use arrow keys to move vaxman
At the start, there are 10 ghosts on the board
Ghosts duplicate every 15 seconds
Vax-man can vaccinate (i.e. delete) ghosts                                                            
Vax-man can also collect yellow dots

Goal - collect all the dots before the number of ghosts reaches 40

grid.txt is the map layout, where 0 = wall, 1 = dot, 2 = ghost.
the map shouldn't have any deadends

Things to improve:

Making the movement less choppy
Increasing the dimensions of the board
Changing direction has to be timed perfectly otherwise you miss the turn
Adding sounds
Representing Vax-man and the ghosts with images
Make an assertion that the dimensions of the grid are valid

RevRave comments:
make the chance that a ghost goes back on itself smaller - implemented by RevRift

RevRift comments:
"""


import pygame, sys
from pygame.math import Vector2
from random import randint

pygame.init()
pygame.font.init()

# window
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vaxman")

TEXT_FONT = pygame.font.SysFont('comicsans', 25)
GAME_OVER_FONT = pygame.font.SysFont('comicsans', 50)

# settings
FPS = 60
SQUARE_LENGTH = 40  # 15 x 15 grid (resizing will break the game)
PLAYER_VEL = 5
GHOST_VEL = 3

# colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)
PURPLE = (255,0,255)
YELLOW = (255,255,0)
DIRECTIONS = [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]

MOVE_PLAYER = pygame.USEREVENT
pygame.time.set_timer(MOVE_PLAYER, int(1000/PLAYER_VEL))
MOVE_GHOSTS = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_GHOSTS, int(1000/GHOST_VEL))
DUPLICATE_GHOSTS = pygame.USEREVENT + 2
pygame.time.set_timer(DUPLICATE_GHOSTS, int(15000)) # duplicate ghosts every 15s

class Player:
    def __init__(self, x, y, color):
        self.pos = Vector2(x, y)
        self.color = color
        self.direction = DIRECTIONS[randint(0, len(DIRECTIONS)-1)]
        self.score = 0

class Dot:
    def __init__(self, x, y, color):
        self.pos = Vector2(x, y)
        self.color = color
        self.radius = 5
        self.screen_pos = Vector2(int(x * SQUARE_LENGTH + SQUARE_LENGTH/2), 
            int(y * SQUARE_LENGTH + SQUARE_LENGTH/2))

class Wall: # rectangles neither players nor ghost can cross
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x * SQUARE_LENGTH, y * SQUARE_LENGTH, 
                SQUARE_LENGTH, SQUARE_LENGTH)
        self.color = color

class Game:
    player = Player(0, 0, YELLOW)
    ghosts = []
    dots = []
    WALLS = []
    JUNCTIONS = []

    @staticmethod
    def set_up_grid():
        grid_file = open('grid.txt', 'r')
        grid = grid_file.readlines()
        grid_file.close()

        for y, line in enumerate(grid):
            for x, char in enumerate(line):
                if char == '0':
                    Game.WALLS.append(Wall(x, y, GREEN))
                elif char == '1':
                    Game.dots.append(Dot(x, y, YELLOW))
                elif char == '2':
                    Game.ghosts.append(Player(x, y, BLUE))

        for y in range(len(grid)):
            for x in range(len(grid[0])):
                dummy = Player(x, y, YELLOW)
                count_valid_dirs = sum(not Game.will_collide(dummy, dirn) for dirn in DIRECTIONS)
                if count_valid_dirs > 2:
                    Game.JUNCTIONS.append(Vector2(x, y))

    @staticmethod
    def draw_window():
        WIN.fill(BLACK)

        for wall in Game.WALLS:
            pygame.draw.rect(WIN, wall.color, wall.rect)

        for dot in Game.dots:
            pygame.draw.circle(WIN, dot.color, dot.screen_pos, dot.radius)

        for ghost in Game.ghosts:
            pygame.draw.circle(WIN, ghost.color, 
                            (int(ghost.pos.x * SQUARE_LENGTH + SQUARE_LENGTH/2), 
                            int(ghost.pos.y * SQUARE_LENGTH + SQUARE_LENGTH/2)), 
                            int(SQUARE_LENGTH/2 - SQUARE_LENGTH/10))

        pygame.draw.circle(WIN, Game.player.color, 
                        (int(Game.player.pos.x * SQUARE_LENGTH + SQUARE_LENGTH/2), 
                        int(Game.player.pos.y * SQUARE_LENGTH + SQUARE_LENGTH/2)), 
                        int(SQUARE_LENGTH/2 - SQUARE_LENGTH/10))

        ghost_count_text = TEXT_FONT.render(f"Ghost count: {len(Game.ghosts)}", 1, WHITE)
        WIN.blit(ghost_count_text, (10 * SQUARE_LENGTH - ghost_count_text.get_width() - 10, 
                                6 * SQUARE_LENGTH - ghost_count_text.get_height() - 10))

        score_text = TEXT_FONT.render(f"Score: {Game.player.score}", 1, WHITE)
        WIN.blit(score_text, (10 * SQUARE_LENGTH - score_text.get_width() - 10, 
                            10 * SQUARE_LENGTH - score_text.get_height() - 10))

        pygame.display.update() 

    @staticmethod
    def will_collide(object, direction):
        next_rect = pygame.Rect(((object.pos.x + direction.x) % 15) * SQUARE_LENGTH, 
                                ((object.pos.y + direction.y) % 15) * SQUARE_LENGTH, 
                                SQUARE_LENGTH, SQUARE_LENGTH)
        return any(next_rect.colliderect(wall.rect) for wall in Game.WALLS)

    @staticmethod
    def rand_direction(ghost):
        if (Game.will_collide(ghost, ghost.direction) # if ghost will collide, change it's direction
          or ghost.pos in Game.JUNCTIONS and randint(0, 1)): # ghost will sometimes turn at junctions
            directions = DIRECTIONS[:]
            if randint(0, 2): # the ghost is unlikely to go back on itself
                directions.remove(Vector2(-ghost.direction.x, -ghost.direction.y))
            new_direction = directions[randint(0, len(directions)-1)]
            while Game.will_collide(ghost, new_direction):
                new_direction = directions[randint(0, len(directions)-1)]
            return new_direction
        return ghost.direction

    @staticmethod
    def player_at_ghost():
        for ghost in Game.ghosts:
            if Game.player.pos == ghost.pos:
                Game.ghosts.remove(ghost)
                return True
        return False

    @staticmethod
    def player_at_dot():
        for dot in Game.dots:
            if Game.player.pos == dot.pos:
                Game.dots.remove(dot)
                return True
        return False

    @staticmethod
    def play():
        clock = pygame.time.Clock()
        game_over = False

        while not game_over:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True

                if event.type == MOVE_PLAYER and not Game.will_collide(Game.player, Game.player.direction):
                    x = (Game.player.pos.x + Game.player.direction.x) % 15             
                    y = (Game.player.pos.y + Game.player.direction.y) % 15                 
                    Game.player.pos = Vector2(x, y)
                
                if event.type == MOVE_GHOSTS:
                    for ghost in Game.ghosts:                   
                        ghost.direction = Game.rand_direction(ghost)
                        x = (ghost.pos.x + ghost.direction.x) % 15             
                        y = (ghost.pos.y + ghost.direction.y) % 15                 
                        ghost.pos = Vector2(x, y)
                
                if Game.player_at_ghost():
                    Game.player.score += 10
                
                if Game.player_at_dot():
                    Game.player.score += 1
                
                if event.type == DUPLICATE_GHOSTS:
                    ghost_count = len(Game.ghosts)
                    for i in range(ghost_count):
                        new_ghost = Player(Game.ghosts[i].pos.x, Game.ghosts[i].pos.y, Game.ghosts[i].color)
                        Game.ghosts.append(new_ghost)
                
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_KP4) and not Game.will_collide(Game.player, Vector2(-1, 0)):
                        Game.player.direction = Vector2(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_KP6) and not Game.will_collide(Game.player, Vector2(1, 0)):
                        Game.player.direction = Vector2(1, 0)
                    elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_KP8) and not Game.will_collide(Game.player, Vector2(0, -1)):
                        Game.player.direction = Vector2(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_KP2) and not Game.will_collide(Game.player, Vector2(0, 1)):
                        Game.player.direction = Vector2(0, 1)
                    elif event.key == pygame.K_BACKSPACE:
                        game_over = True
                    
            Game.draw_window()

            if len(Game.dots) == 0:
                win_text = GAME_OVER_FONT.render("YOU WIN", 1, WHITE)
                WIN.blit(win_text, (WIDTH/2 - win_text.get_width()//2, HEIGHT/2 - win_text.get_height()//2))
                pygame.display.update()
                pygame.time.delay(3000)
                game_over = True
            elif len(Game.ghosts) >= 50:
                lose_text = GAME_OVER_FONT.render("YOU LOSE", 1, RED)
                WIN.blit(lose_text, (WIDTH/2 - lose_text.get_width()//2, HEIGHT/2 - lose_text.get_height()//2))
                pygame.display.update()
                pygame.time.delay(3000)
                game_over = True


if __name__ == "__main__":
    Game.set_up_grid()
    Game.play()
    pygame.quit() # this isn't in the same scope as pygame.init(), does that matter?
    sys.exit()