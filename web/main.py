import asyncio
import pygame
import random

CAR_FILES = [
    "Audi.png", "Black_viper.png", "Mini_truck.png",
    "Mini_van.png", "Police.png", "taxi.png",
]
MAX_CARS = 5


class Game:
    RANDOM_CARS_COUNT = 0

    def __init__(self):
        pygame.init()
        self.score = 0
        self.height = 600
        self.width = 500
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Racing AI")

        self.car_img = pygame.image.load("Car.png").convert_alpha()
        self.background = pygame.image.load("Road.png").convert_alpha()
        self.bg_car_imgs = [
            pygame.transform.scale(
                pygame.image.load("cars/" + f).convert_alpha(), (100, 100)
            )
            for f in CAR_FILES
        ]
        self.clock = pygame.time.Clock()

    def cleanUpCars(self, bg_cars):
        for c in bg_cars:
            if c.y >= self.height:
                bg_cars.remove(c)
                self.RANDOM_CARS_COUNT -= 1
        return bg_cars

    def createNewCars(self, bg_cars):
        extra = len([car for car in bg_cars if not car.onScreen()])
        while self.RANDOM_CARS_COUNT != MAX_CARS + extra:
            new_car = BackgroundCars(self.bg_car_imgs[random.randint(0, 5)], self.window, self.height)
            will_append = True
            for cars in bg_cars:
                if cars.collide(new_car) or self.RANDOM_CARS_COUNT == MAX_CARS + extra:
                    will_append = False
                    break
            if will_append:
                bg_cars.append(new_car)
                self.RANDOM_CARS_COUNT += 1

        return bg_cars

    async def run(self):
        font = pygame.font.SysFont("sans", 32)
        small_font = pygame.font.SysFont("sans", 22)

        while True:
            self.score = 0
            self.RANDOM_CARS_COUNT = 0
            car = Car(250, self.height - 100, self.window, self.car_img)
            track = Track(50, self.window, self.height, self.background)
            bg_cars = []
            self.createNewCars(bg_cars)
            show_help = True
            alive = True

            touch_active = False
            touch_x, touch_y = None, None
            touch_frame_multiplier = 1
            while alive:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN and show_help:
                        show_help = False

                    if event.type == pygame.FINGERDOWN:
                        touch_active = True
                        touch_x = event.x * self.width
                        touch_y = event.y * self.height
                        if show_help:
                            show_help = False
                    elif event.type == pygame.FINGERMOTION:
                        touch_x = event.x * self.width
                        touch_y = event.y * self.height
                    elif event.type == pygame.FINGERUP:
                        touch_active = False
                        touch_x, touch_y = None, None
                        touch_frame_multiplier = 1

                keys = pygame.key.get_pressed()
                self.window.fill((0, 255, 0))

                bg_cars = self.cleanUpCars(bg_cars)
                bg_cars = self.createNewCars(bg_cars)

                track.draw()
                self.score = track.move(self.score, show_help)
                car.draw()

                for i in random.sample(
                    list(range(self.RANDOM_CARS_COUNT)), self.RANDOM_CARS_COUNT
                ):
                    bg_cars[i].draw()
                    bg_cars[i].move()

                if not show_help:
                    if keys[pygame.K_LEFT]:
                        car.x -= car.vel
                    if keys[pygame.K_RIGHT]:
                        car.x += car.vel
                    if keys[pygame.K_UP] and car.y + car.vel >= 250:
                        car.y -= car.vel
                    if keys[pygame.K_DOWN] and car.y + car.vel + car.height <= self.height - 50:
                        car.y += car.vel

                    if touch_active:
                        touch_frame_multiplier += 0.0005

                    if touch_active and touch_x is not None:
                        if touch_x < car.x:
                            car.x -= car.vel * touch_frame_multiplier
                        elif touch_x > car.x + car.width:
                            car.x += car.vel * touch_frame_multiplier
                        if touch_y < car.y:
                            car.y -= car.vel * touch_frame_multiplier
                        elif touch_y > car.y + car.height:
                            car.y += car.vel * touch_frame_multiplier

                    for cars in bg_cars:
                        if cars.collide(car):
                            alive = False

                    if car.x < 50 or car.x + car.width > 450:
                        alive = False

                score_text = font.render(
                    " Score: " + str(self.score) + " ", True, (255, 0, 0), (0, 0, 0)
                )
                score_rect = score_text.get_rect()
                score_rect.center = (400, 50)
                self.window.blit(score_text, score_rect)

                if show_help:
                    overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))
                    self.window.blit(overlay, (0, 0))
                    for i, line in enumerate(["Arrow keys or touch to move", "Press any key or tap to start"]):
                        t = small_font.render(line, True, (255, 255, 255))
                        r = t.get_rect(center=(self.width // 2, self.height // 2 - 20 + i * 40))
                        self.window.blit(t, r)

                self.clock.tick(60)
                pygame.display.update()
                await asyncio.sleep(0)

            # Game over screen — wait for Space to restart
            game_over = True
            while game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        game_over = False
                    if event.type == pygame.FINGERDOWN:
                        game_over = False

                self.window.fill((0, 0, 0))

                gameoverscreen = font.render("GAME OVER", True, (255, 50, 50))
                self.window.blit(gameoverscreen, gameoverscreen.get_rect(center=(self.width // 2, self.height // 2 - 50)))

                scoreboard = font.render(f"Score: {self.score}", True, (255, 255, 255))
                self.window.blit(scoreboard, scoreboard.get_rect(center=(self.width // 2, self.height // 2)))

                hint = small_font.render("Press any key or tap to restart", True, (200, 200, 200))
                self.window.blit(hint, hint.get_rect(center=(self.width // 2, self.height // 2 + 50)))

                self.clock.tick(60)
                pygame.display.update()
                await asyncio.sleep(0)


class BackgroundCars:
    def __init__(self, car, window, height):
        self.x = random.randint(50, 350)
        self.y = random.randint(-400, -100)
        self.vel = 5
        self.width = 100
        self.height = 100
        self.window = window
        self.window_height = height
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
        if self.y <= self.window_height - 250:
            return True
        return False

    def __str__(self):
        return f"y: {self.y} , onScreen: {self.onScreen()}"


class Track:
    def __init__(self, x, window, height, background):
        self.x = x
        self.y1 = 0
        self.height = height
        self.y2 = self.height
        self.vel = 10
        self.window = window
        self.background = background

    def move(self, score, show_help):
        self.y1 += self.vel
        self.y2 += self.vel

        if self.y1 - self.height > 0:
            self.y1 = self.y2 - self.height

        if self.y2 - self.height > 0:
            self.y2 = self.y1 - self.height

        if not show_help:
            return score + 1
        return score

    def draw(self):
        self.window.blit(self.background, (self.x, self.y1))
        self.window.blit(self.background, (self.x, self.y2))


class Car:
    def __init__(self, x, y, window, image):
        self.x = x
        self.y = y
        self.vel = 6
        self.width = 44
        self.height = 100
        self.window = window
        self.car = image

    def move(self):
        self.y += self.vel

    def draw(self):
        self.window.blit(self.car, (self.x, self.y))

    def mask(self):
        return pygame.mask.from_surface(self.car)


async def main():
    game = Game()
    await game.run()

asyncio.run(main())
