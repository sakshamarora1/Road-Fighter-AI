import pygame
import os
import random
import numpy as np
from g import Brain

TOTAL_CARS = 5
CAR = pygame.image.load("Car.png")
BACKGROUND = pygame.image.load("Road.png")
BG_CARS = [
    pygame.transform.scale(pygame.image.load("cars/" + vehicle), (100, 100))
    for vehicle in os.listdir("cars")
]


class Game:
    RANDOM_CARS_COUNT = 1

    def __init__(self):
        # Initializing Pygame stuff
        pygame.init()
        self.window = pygame.display.set_mode((500, 800))
        pygame.display.set_caption("Racing AI")
        # self.clock = pygame.time.Clock()
        self.execute = True

        # Initialize Cars
        self.cars = []
        self.score = 0

    def nextGeneration(self):
        for i in range(TOTAL_CARS):
            self.cars.append(Car(250, 650, self.window))

    def run(self):
        # car = Car(250, 650, self.window)
        track = Track(50, self.window)
        bg_cars = [BackgroundCars(BG_CARS[0], self.window)]

        # pygame.time.set_timer(pygame.USEREVENT + 1, 500)

        while self.execute:

            keys = pygame.key.get_pressed()
            self.window.fill((0, 255, 0))
            if len(self.cars) == 0 and len(bg_cars) == 0:
                self.nextGeneration()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or keys[pygame.K_0]:
                    self.execute = False

                # if event.type == pygame.USEREVENT + 1:
            if len(bg_cars) < 5 and len(self.cars) > 0:
                randomno = random.randint(1, 20)
                if randomno == 1:
                    new_car = BackgroundCars(BG_CARS[random.randint(0, 5)], self.window)
                    will_append = True
                    for cars in bg_cars:
                        if cars.collide(new_car):
                            will_append = False
                            break
                    if will_append:
                        bg_cars.append(new_car)
                        self.RANDOM_CARS_COUNT += 1

            for c in bg_cars:
                if c.y >= 800:
                    bg_cars.remove(c)
                    self.RANDOM_CARS_COUNT -= 1

            track.draw()
            self.score = track.move(self.score)

            for car in self.cars:
                car.draw()
                car.think()

            for i in random.sample(
                list(range(self.RANDOM_CARS_COUNT)), self.RANDOM_CARS_COUNT
            ):
                bg_cars[i].draw()
                bg_cars[i].move()

            for car in self.cars:
                for cars in bg_cars:
                    if cars.collide(car):
                        self.execute = False

                if car.x < 50 or car.x + car.width > 450:
                    self.cars.remove(car)

            # self.clock.tick(30)
            # print(self.score)
            pygame.display.update()
        pygame.quit()


class BackgroundCars:
    def __init__(self, car, window):
        self.x = random.randint(50, 350)
        self.y = random.randint(-500, -100)
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


class Track:
    def __init__(self, x, window):
        self.x = x
        self.y1 = 0
        self.y2 = 800
        self.vel = 10
        self.window = window

    def move(self, score):
        self.y1 += self.vel
        self.y2 += self.vel

        if self.y1 - 800 > 0:
            self.y1 = self.y2 - 800

        if self.y2 - 800 > 0:
            self.y2 = self.y1 - 800

        return score + 1

    def draw(self):
        self.window.blit(BACKGROUND, (self.x, self.y1))
        self.window.blit(BACKGROUND, (self.x, self.y2))


class Car:
    def __init__(self, x, y, window):
        self.x = x
        self.y = y
        self.vel = 6
        self.width = 44
        self.height = 100
        self.window = window
        self.car = CAR
        self.brain = Brain()

    def think(self):
        inputs = np.random.rand(1, 4)
        thought = self.brain.brain.predict(inputs)
        if thought[0][0] > 0.5:
            self.left()
        else:
            self.right()

    def move(self):
        self.y += self.vel

    def draw(self):
        self.window.blit(self.car, (self.x, self.y))

    def mask(self):
        return pygame.mask.from_surface(self.car)

    def left(self):
        self.x -= self.vel

    def right(self):
        self.x += self.vel

    def up(self):
        if self.y + self.vel >= 250:
            self.y -= self.vel

    def down(self):
        if self.y + self.vel + self.height <= 600:
            self.y += self.vel


if __name__ == "__main__":
    game = Game()
    game.run()

