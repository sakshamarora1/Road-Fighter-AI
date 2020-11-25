import os
import pygame
from nn import NeuralNetwork
import random


CAR = pygame.image.load(os.path.abspath("..") + "/Car.png")


def mutate(x):
    if random.random() < 0.1:
        return random.gauss(0, 1) * 0.5 + x
    return x


class Car:
    def __init__(self, x, y, window, brain=None):
        self.x = x
        self.y = y
        self.vel = 6
        self.width = 44
        self.height = 100
        self.window = window
        self.car = CAR
        self.fitness = 0
        self.score = 0
        if brain:
            self.brain = brain.copy()
            self.brain.mutate(mutate)
        else:
            self.brain = NeuralNetwork(4, 8, 2)

    def think(self, bg_cars):
        inputs = []
        for car in bg_cars:
            inputs.append(car.x / 500)
        inputs.append(self.x / 500)
        inputs.append((bg_cars[0].y - bg_cars[1].y) / 800)

        thought = self.brain.predict(inputs)
        i = thought.index(max(thought))

        if i == 0:
            self.left()
        elif i == 1:
            self.right()
        # elif i == 2:
        #     self.down()
        # elif i == 4:
        #     self.up()
        else:
            # self.up()
            pass

    def move(self):
        self.y += self.vel
        self.score += 0.1

    def draw(self):
        self.window.blit(self.car, (self.x, self.y))

    def mask(self):
        return pygame.mask.from_surface(self.car)

    def left(self):
        self.x -= self.vel - 2

    def right(self):
        self.x += self.vel - 2

    def up(self):
        if self.y + self.vel >= 250:
            self.y -= self.vel

    def down(self):
        if self.y + self.vel + self.height <= 600:
            self.y += self.vel
