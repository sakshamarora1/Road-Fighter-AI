import random
from car import Car


def normalizeFitness(cars):
    total = 0
    for car in cars:
        total += car.score ** 2

    for car in cars:
        car.fitness = car.score ** 2 / total

    return cars


def newCars(cars, option):
    cars = normalizeFitness(cars)
    top_brain = selection(cars, option)
    new_cars = []
    for _ in range(len(cars)):
        new_cars.append(Car(250, 650, cars[0].window, brain=top_brain))
    
    return new_cars


def selection(cars, option):
    i = 0
    r = random.random()

    if option == 1:
        while r > 0:
            r -= cars[i].fitness
            i += 1
        i -= 1
        return cars[i].brain

    elif option == 2:
        maxx = 0
        for i in range(len(cars)):
            if cars[i].fitness > cars[maxx].fitness:
                maxx = i
        return cars[maxx].brain

