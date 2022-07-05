#!/usr/bin/env python3

import random
import pygame

COLORS = [
    # WHITE
    (255, 255, 255),
    # BLACK
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (255, 68, 51),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]

class Piece:
    coordinates_under_rotation = [
        # vertical bar
        [
            [(1,0), (1,1), (1,2), (1,3)],
            [(0,1), (1,1), (2,1), (3,1)],
        ],
        # the right facing L
        [
            [(1,0), (1,1), (1,2), (2,2)],
            [(2,0), (0,1), (1,1), (2,1)],
            [(1,0), (2,0), (2,1), (2,2)],
            [(0,1), (1,1), (2,1), (0,2)],
        ],
        # the 2*2 square
        [
            [(1,0), (2,0), (1,1), (2,1)],
        ],
        # the T shape
        [
            [(0,1), (1,1), (2,1), (1,2)],
            [(1,0), (1,1), (1,2), (2,1)],
            [(1,0), (0,1), (1,1), (2,1)],
            [(1,0), (0,1), (1,1), (1,2)],
        ],
    ]

    def __init__(self, x, y, coordinates):
        # x and y are the screen coordinates for the 4*4 box that holds the tetris piece
        self.x, self.y = x, y
        assert coordinates
        self._coord_index = 0
        self._coordinates = coordinates
        # take any of the random colors that isn't WHITE
        self.color = random.choice(COLORS[2:])

    @classmethod
    def random_piece(cls, x, y):
        return Piece(x, y, random.choice(Piece.coordinates_under_rotation))

    def coordinates(self):
        """returns the actual screen coordinates of the piece"""
        return [(coord[0] + self.x, coord[1] + self.y) for coord in self._coordinates[self._coord_index]]
    
    def rotate(self):
        self._coord_index = (self._coord_index + 1) % len(self._coordinates)

        
class Tetris:
    def new_active_piece(self):
        return Piece.random_piece(self.w//2-1, 0)

    def __init__(self, width, height):
        # x and y are screen coordinates for the top left corner of the game field.
        self.x, self.y = 100, 60
        # zoom controls the size of the grid cell.
        self.zoom = 20
        # level controls the speed of the game
        self.level = 2

        self.w = width
        self.h = height
        self.active_piece = self.new_active_piece()
        self.score = 0
        self.state = 'start'

        # this saves all the already settled pieces on the tetris board.
        self.board = []
        # creates a row first representation of the game field. this means that a coordinate of (x, y) relative to
        # the topleft corner of the game should be retrieved using self.board[y][x].
        for _ in range(self.h):
            self.board.append([0]*self.w)

    def rotate(self):
        self.active_piece.rotate()
        
    def _eliminate(self):
        """eliminate all the lines that could be eliminated from the bottom."""
        def elim_one_line():
            index_to_del = None
            for i in range(self.h-1, -1, -1):
                if sum(1 if cell else 0 for cell in self.board[i]) == self.w:
                    index_to_del = i
                    break
      
            if index_to_del:
                del self.board[index_to_del]
                self.board.insert(0, [0]*self.w)
                return True
            return False

        lines_elimed = 0
        while elim_one_line():
            lines_elimed += 1
        self.score += 10*(lines_elimed**2)

    def drop(self):
        """let the active piece drop by 1 unit below if possible. returns whether the drop was successful."""
        self.active_piece.y += 1
        if self._collide():
            self.active_piece.y -= 1
            self._freeze()
            return False
        return True
            
    def move_horizontal(self, right=True):
        """Move the active piece to the left or right if possible."""
        increment = (1 if right else -1)
        self.active_piece.x += increment
        if self._collide():
            self.active_piece.x -= increment

    def _collide(self):
        """checks if the active piece has hit the boundary or the other settled pieces"""
        for c in self.active_piece.coordinates():
            if c[0] < 0 or c[0] >= self.w or c[1] < 0 or c[1] >= self.h:
                return True
            if self.board[c[1]][c[0]] != 0:
                return True
        return False

    def _freeze(self):
        """freeze the currently active piece and allocate a new active piece."""
        for c in self.active_piece.coordinates():
            self.board[c[1]][c[0]] = 1

        self._eliminate()
        # get new active piece
        self.active_piece = self.new_active_piece()
        if self._collide():
            self.state = 'gameover'


if __name__ == '__main__':
    # Initialize the game engine
    pygame.init()

    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)

    size = (400, 500)
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Tetris")

    # Loop until the user clicks the close button.
    done = False
    clock = pygame.time.Clock()
    fps = 500
    game = Tetris(10, 20)
    counter = 0

    pressing_down = False
    should_eliminate = False

    while not done:
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (fps // game.level // 2) == 0 or pressing_down:
            if game.state == 'start' :
                game.drop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_LEFT:
                    game.move_horizontal(right=False)
                if event.key == pygame.K_RIGHT:
                    game.move_horizontal(right=True)
                if event.key == pygame.K_SPACE:
                    #game.go_space()
                    pass
                if event.key == pygame.K_ESCAPE:
                    game = Tetris(game.w, game.h)

        if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        screen.fill(WHITE)

        for i in range(game.h):
            for j in range(game.w):
                pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                if game.board[i][j] > 0:
                    pygame.draw.rect(screen, COLORS[game.board[i][j]],
                                     [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

        for c in game.active_piece.coordinates():
            pygame.draw.rect(screen, game.active_piece.color,
                             [
                                 game.x + game.zoom * c[0] + 1,
                                 game.y + game.zoom * c[1] + 1,
                                 game.zoom - 2, game.zoom - 2,
                             ])

        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text = font.render("Score: " + str(game.score), True, BLACK)
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

        screen.blit(text, [0, 0])
        if game.state == 'gameover':
            screen.blit(text_game_over, [20, 200])
            screen.blit(text_game_over1, [25, 265])

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


