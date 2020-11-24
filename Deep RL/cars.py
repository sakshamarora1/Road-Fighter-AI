import random
import pygame
import os


class BackgroundCars:
    def __init__(self, car, window):
        self.x = random.randint(50, 350)
        self.y = random.randint(-400, -100)
        self.vel = 5
        self.width = 100
        self.height = 100
        self.window = window
        self.car = car

    def move(self):
        self.y += self.vel

    def draw(self):
        self.window.blit(self.car, (self.x, self.y))

    def collide(self, gaddi):
        playerMask = gaddi.mask()
        carMask = self.mask()

        collision = playerMask.overlap(carMask, (self.x - gaddi.x, self.y - gaddi.y))
        return bool(collision)

    def mask(self):
        return pygame.mask.from_surface(self.car)

    def onScreen(self):
        if self.y <= 650:
            return True
        return False

    def __str__(self):
        return f"y: {self.y} , onScreen: {self.onScreen()}"


CAR = pygame.image.load(os.path.abspath("..") + "/Car.png")


class Car:
    def __init__(self, x, y, window):
        self.x = x
        self.y = y
        self.vel = 6
        self.width = 44
        self.height = 100
        self.window = window
        self.car = CAR
        self.ok = True
        self.score = 0

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
