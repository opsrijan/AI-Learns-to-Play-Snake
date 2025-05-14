import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()

# directions
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
# point
Point = namedtuple('Point', 'x, y')

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# creating window
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
SPEED = 20


class Game:

    def __init__(self):

        # initialize display
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        self.head = Point(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)
                      ]

        self.score = 0

        self.direction = Direction.RIGHT
        self.food = None
        self.placeFood()

    def placeFood(self):
        x = random.randint(2, (SCREEN_WIDTH - 3 * BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(2, (SCREEN_HEIGHT - 3 * BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self.placeFood()
    
    def playStep(self):
        # return gameOver, score
        # take input
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                quit()
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_LEFT):
                    self.direction = Direction.LEFT
                if (event.key == pygame.K_RIGHT):
                    self.direction = Direction.RIGHT
                if (event.key == pygame.K_DOWN):
                    self.direction = Direction.DOWN
                if (event.key == pygame.K_UP):
                    self.direction = Direction.UP
        
        # update head
        self.move(self.direction) 
        self.snake.insert(0, self.head)

        # check collision
        gameOver = False
        if (self.isCollision()):
            gameOver = True
            return gameOver, self.score
        
        # check food
        if (self.head == self.food):
            self.score += 1
            self.placeFood()
        else:
            self.snake.pop()

        # update UI and clock
        self.updateUI()
        self.clock.tick(SPEED)

        # return gameOver, score
        return gameOver, self.score


    def isCollision(self):
        # boundary conditions
        if (self.head.x > SCREEN_WIDTH - BLOCK_SIZE or 
            self.head.x < 0 or
            self.head.y < 0 or
            self.head.y > SCREEN_HEIGHT - BLOCK_SIZE):
            return True
        
        # htis itself
        if (self.head in self.snake[1:]):
            return True
        
        return False

    def updateUI(self):
        self.display.fill(WHITE)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        font = pygame.font.SysFont(None, 55)
        
        text = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def move(self, direction):
        x = self.head.x
        y = self.head.y

        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE

        self.head = Point(x, y)



if __name__ == '__main__':
    snakeGame = Game()

    while True:
        gameOver, score = snakeGame.playStep()

        if gameOver==True:
            break
    
    print("final Score", snakeGame.score)

    pygame.quit()
