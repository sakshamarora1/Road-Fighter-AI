import pygame
import os
import random

from agent import DQNAgent
from cars import Car, BackgroundCars

BACKGROUND = pygame.image.load(os.path.abspath("..") + "/Road.png")
BG_CARS = [
    pygame.transform.scale(
        pygame.image.load(os.path.abspath("..") + "/cars/" + vehicle), (100, 100)
    )
    for vehicle in os.listdir(os.path.abspath("..") + "/cars")
]
MAX_CARS = 2


class Game:
    RANDOM_CARS_COUNT = 0

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((500, 800))
        pygame.display.set_caption("Racing AI")

        self.clock = pygame.time.Clock()
        self.execute = True

        self.car = Car(250, 650, self.window)
        self.agent = DQNAgent(inputs=4, n_actions=2)
        self.episode_durations = []

        self.update_agent = pygame.USEREVENT + 1
        update_timer = 100
        pygame.time.set_timer(self.update_agent, update_timer)

    def cleanUpCars(self, bg_cars):
        for c in bg_cars:
            if c.y >= 800:
                bg_cars.remove(c)
                self.RANDOM_CARS_COUNT -= 1
        return bg_cars

    def createNewCars(self, bg_cars):
        extra = len([car for car in bg_cars if not car.onScreen()])
        while self.RANDOM_CARS_COUNT != MAX_CARS + extra:
            new_car = BackgroundCars(BG_CARS[random.randint(0, 5)], self.window)
            will_append = True
            for cars in bg_cars:
                if cars.collide(new_car) or self.RANDOM_CARS_COUNT == MAX_CARS + extra:
                    will_append = False
                    break
            if will_append:
                bg_cars.append(new_car)
                self.RANDOM_CARS_COUNT += 1

        return bg_cars

    def get_state(self, bg_cars):
        state = []
        for car in bg_cars:
            state.append(car.x / 500)
        state.append(self.car.x / 500)
        state.append((bg_cars[0].y - bg_cars[1].y) / 800)
        return state

    def run_episodes(self, num_episodes=20):
        track = Track(50, self.window)
        bg_cars = []
        avg = 0

        for i_episode in range(num_episodes):
            self.createNewCars(bg_cars)
            self.car = Car(250, 650, self.window)
            self.execute = True

            while self.execute:
                keys = pygame.key.get_pressed()
                self.window.fill((0, 255, 0))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or keys[pygame.K_0]:
                        pygame.quit()

                if not self.car.ok and len(bg_cars) == 0:
                    self.execute = False

                bg_cars = self.cleanUpCars(bg_cars)

                while len(bg_cars) < 2 and self.car.ok:
                    randomno = random.randint(1, 50)
                    if randomno == 1:
                        new_car = BackgroundCars(
                            BG_CARS[random.randint(0, 5)], self.window
                        )
                        will_append = True
                        for cars in bg_cars:
                            if cars.collide(new_car):
                                will_append = False
                                break
                        if will_append:
                            bg_cars.append(new_car)
                            self.RANDOM_CARS_COUNT += 1

                track.draw()
                track.move()

                for i in random.sample(
                    list(range(self.RANDOM_CARS_COUNT)), self.RANDOM_CARS_COUNT
                ):
                    bg_cars[i].draw()
                    bg_cars[i].move()

                if self.car.ok:
                    state = self.get_state(bg_cars)
                    self.car.score += (
                        self.car.x if self.car.x < 250 else 500 - self.car.x
                    ) // 50
                    self.car.score += 2
                    self.car.draw()

                    for cars in bg_cars:
                        if self.car.y + 100 < cars.y:
                            self.car.score += 50
                        if cars.collide(self.car):
                            self.car.ok = False
                            self.car.score //= 2

                    if self.car.x < 50 or self.car.x + self.car.width > 450:
                        self.car.score //= 2
                        self.car.ok = False

                    action = self.agent.select_action(state)
                    if action == 0:
                        self.car.left()
                    elif action == 1:
                        self.car.right()
                    else:
                        pass

                    reward = self.car.score
                    next_state = self.get_state(bg_cars) if self.car.ok else None
                    self.agent.memory.push(state, action, reward, next_state)

                    self.agent.learn()

                self.display_text()
                # self.clock.tick(60)
                pygame.display.update()

            while bg_cars:
                for i in range(len(bg_cars)):
                    bg_cars[i].move()
                    bg_cars[i].draw()

                bg_cars = self.cleanUpCars(bg_cars)

            if i_episode % 10 == 0:
                self.agent.target_brain.load_state_dict(self.agent.brain.state_dict())
                print("\n\nAverage of last 10 episodes: ", avg / 10, "\n")
                avg = 0

            print("\nScore for episode", i_episode + 1, " ----- ", self.car.score)
            avg += self.car.score

        pygame.time.wait(100)
        pygame.quit()

    def display_text(self):
        font = pygame.font.SysFont("freesansbold", 32)
        text = font.render(
            " Score: " + str(self.car.score) + " ", True, (255, 0, 0), (0, 0, 0)
        )
        textRect = text.get_rect()
        textRect.center = (400, 30)
        self.window.blit(text, textRect)


class Track:
    def __init__(self, x, window):
        self.x = x
        self.y1 = 0
        self.y2 = 800
        self.vel = 10
        self.window = window

    def move(self):
        self.y1 += self.vel
        self.y2 += self.vel

        if self.y1 - 800 > 0:
            self.y1 = self.y2 - 800

        if self.y2 - 800 > 0:
            self.y2 = self.y1 - 800

    def draw(self):
        self.window.blit(BACKGROUND, (self.x, self.y1))
        self.window.blit(BACKGROUND, (self.x, self.y2))


if __name__ == "__main__":
    game = Game()
    game.run_episodes(500)
