import pygame
import os
import random
from g import newCars
from car import Car

TOTAL_CARS = 100

BACKGROUND = pygame.image.load("Road.png")
BG_CARS = [
    pygame.transform.scale(pygame.image.load("cars/" + vehicle), (100, 100))
    for vehicle in os.listdir("cars")
]


class Game:
    RANDOM_CARS_COUNT = 0

    def __init__(self):
        # Initializing Pygame stuff
        pygame.init()
        self.window = pygame.display.set_mode((500, 800))
        pygame.display.set_caption("Racing AI")
        self.clock = pygame.time.Clock()
        self.execute = True

        # Initialize Cars
        self.cars = []
        self.score = 0
        self.max = 0
        self.generations = 0
        self.generation_score = 0
        self.deadcars = []

    def nextGeneration(self):
        print(f"\nGeneration : {self.generations}")
        print(f"Max Score from Generation-{self.generations} : {self.generation_score}")
        print(f"Max Score from all generations: {self.max}\n")
        if len(self.deadcars) > 0:
            self.cars = newCars(self.deadcars, self.option)
        else:
            for _ in range(TOTAL_CARS):
                self.cars.append(Car(250, 650, self.window))
        self.deadcars = []
        self.generations += 1
        self.generation_score = 0

    def run(self, option):
        self.option = option
        track = Track(50, self.window)
        bg_cars = []

        while self.execute:
            keys = pygame.key.get_pressed()
            self.window.fill((0, 255, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT or keys[pygame.K_0]:
                    self.execute = False

            if len(self.cars) == 0 and len(bg_cars) == 0:
                self.nextGeneration()

            while len(bg_cars) < 2 and len(self.cars) > 0:
                randomno = random.randint(1, 50)
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

            for car in self.cars:
                car.score += 1
                if car.score > self.generation_score:
                    self.generation_score = car.score
                if car.score > self.max:
                    self.max = car.score
                if len(bg_cars) > 0:
                    car.think(bg_cars)

            for i in random.sample(
                list(range(self.RANDOM_CARS_COUNT)), self.RANDOM_CARS_COUNT
            ):
                bg_cars[i].move()

            for car in self.cars:
                if car.x < 50 or car.x + car.width > 450:
                    car.score -= 10
                    self.deadcars.append(car)
                    self.cars.remove(car)
                    continue
                for cars in bg_cars:
                    if car.y + 100 < cars.y:
                        car.score += 50
                    if cars.collide(car):
                        car.score -= 10
                        self.deadcars.append(car)
                        self.cars.remove(car)
                        break

            for c in bg_cars:
                if c.y >= 800:
                    bg_cars.remove(c)
                    self.RANDOM_CARS_COUNT -= 1

            track.draw()
            self.score = track.move(self.score)
            for car in self.cars:
                car.draw()

            for i in random.sample(
                list(range(self.RANDOM_CARS_COUNT)), self.RANDOM_CARS_COUNT
            ):
                bg_cars[i].draw()
            # self.clock.tick(60)
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

        return score + 10

    def draw(self):
        self.window.blit(BACKGROUND, (self.x, self.y1))
        self.window.blit(BACKGROUND, (self.x, self.y2))


if __name__ == "__main__":
    print(
        """
        Road Fighter AI using NEAT Algorithm. Choose parent selection function - 
            
            1. Fitness proportionate probability function.
            2. Direct rank base selection.

        """
    )
    option = 0
    while option not in {1,2}:
        option = int(input("Choose an option: "))

    game = Game()
    game.run(option)

