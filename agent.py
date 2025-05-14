import torch
import random
import numpy as np
from collections import deque
from game import Game, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:


    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def getState(self, game):
        head = game.snake[0]
        pointLeft = Point(head.x - 20, head.y)
        pointRight = Point(head.x + 20, head.y)
        pointUp = Point(head.x, head.y - 20)
        pointDown = Point(head.x, head.y + 20)

        state = [
            # Danger straight
            (game.direction == Direction.RIGHT and game.isCollision(pointRight)) or 
            (game.direction == Direction.LEFT and game.isCollision(pointLeft)) or 
            (game.direction == Direction.UP and game.isCollision(pointUp)) or 
            (game.direction == Direction.DOWN and game.isCollision(pointDown)),

            # Danger right
            (game.direction == Direction.UP and game.isCollision(pointRight)) or 
            (game.direction == Direction.DOWN and game.isCollision(pointLeft)) or 
            (game.direction == Direction.LEFT and game.isCollision(pointUp)) or 
            (game.direction == Direction.RIGHT and game.isCollision(pointDown)),

            # Danger left
            (game.direction == Direction.DOWN and game.isCollision(pointRight)) or 
            (game.direction == Direction.UP and game.isCollision(pointLeft)) or 
            (game.direction == Direction.RIGHT and game.isCollision(pointUp)) or 
            (game.direction == Direction.LEFT and game.isCollision(pointDown)),
            
            # Move direction
            game.direction == Direction.LEFT,
            game.direction == Direction.RIGHT,
            game.direction == Direction.UP,
            game.direction == Direction.DOWN,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            miniSample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            miniSample = self.memory

        states, actions, rewards, next_states, dones = zip(*miniSample)
        self.trainer.trainStep(states, actions, rewards, next_states, dones)
        #for state, action, reward, next_state, done in mini sample:
        #    self.trainer.trainStep(state, action, reward, next_state, done)

    def trainShortMemory(self, state, action, reward, next_state, done):
        self.trainer.trainStep(state, action, reward, next_state, done)

    def getAction(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        finalmove = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            finalmove[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            finalmove[move] = 1

        return finalmove


def train():
    plotScores = []
    plotMeanScores = []
    totalScore = 0
    record = 0
    agent = Agent()
    game = Game()
    while True:
        # get old state
        oldState = agent.getState(game)

        # get move
        finalmove = agent.getAction(oldState)

        # perform move and get new state
        reward, done, score = game.playStep(finalmove)
        newState = agent.getState(game)

        # train short memory
        agent.trainShortMemory(oldState, finalmove, reward, newState, done)

        # remember
        agent.remember(oldState, finalmove, reward, newState, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.trainLongMemory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plotScores.append(score)
            totalScore += score
            meanScore = totalScore / agent.n_games
            plotMeanScores.append(meanScore)
            plot(plotScores, plotMeanScores)


if __name__ == '__main__':
    train()