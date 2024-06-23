import sys
import tkinter as tk
import random
import csv
import math
import numpy as np

GRID_SIZE = 1000
DIRT_COUNT = 1000
CELL_SIZE = 20  # Assuming cell size remains the same as previously defined
WALL_FILE = "walls_1000_20_0.csv"
GRID = []
PASSIVE_OBJECTS = []
DANGER_OBJECTS = []

class Counter:
    def __init__(self):
        self.dirtCollected = 0
        self.seconds_elapsed = 0
 
    def itemCollected(self, canvas):
        self.dirtCollected += 1
        canvas.delete("dirtCount")

        canvas.create_text(10, 20, anchor="nw", font="Arial 14", 
                        text=f"Dirt Collected: {self.dirtCollected}", tags="dirtCount")
        
    def updateTime(self, canvas, time):
        canvas.delete("timeElapsed")

        canvas.create_text(GRID_SIZE - 10, 20, anchor="ne", font="Arial 14", 
                       text=f"Time Elapsed: {time} s", tags="timeElapsed")
        

class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, 
                                self.x + CELL_SIZE, self.y + CELL_SIZE, fill="black", outline="grey")
        
    def getLocation(self):
        return self.x, self.y

class Charger:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, 
                                self.x + CELL_SIZE, self.y + CELL_SIZE, fill="red", outline="grey")
    def getLocation(self):
        return self.x, self.y
        
class Dirt:
    def __init__(self, namep, x, y):
        self.centreX = x
        self.centreY = y
        self.name = namep

    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-2,self.centreY-2, \
                                  self.centreX+2,self.centreY+2, \
                                  fill="lime",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


def is_wall(x, y):
    ix = (int)(x/CELL_SIZE)
    iy = (int)(y/CELL_SIZE)
    if (iy < 0 or iy >= GRID_SIZE/CELL_SIZE):
        return False
    if (ix < 0 or ix >= GRID_SIZE/CELL_SIZE):
        return False
    return GRID[iy][ix] > 0

def create_dirt(canvas, amount_of_dirt=DIRT_COUNT):
    for i in range(amount_of_dirt):
        x = random.randint(20, GRID_SIZE - 20)
        y = random.randint(100, GRID_SIZE - 20)

        while is_wall(x, y):
            x = random.randint(20, GRID_SIZE - 20)
            y = random.randint(100, GRID_SIZE - 20)

        dirt = Dirt(f"Dirt{i}", x, y)
        PASSIVE_OBJECTS.append(dirt)
        dirt.draw(canvas)


def create_passive_objects(canvas, filename):
    global GRID
    try:
        with open(filename, newline='') as file:
            grid = list(csv.reader(file))
            GRID = [[int(char) for char in row] for row in grid]
            if len(grid) != (GRID_SIZE) // CELL_SIZE or len(grid[0]) != GRID_SIZE // CELL_SIZE:
                raise ValueError("CSV grid size does not match expected GRID_SIZE.")
            for y in range(len(grid)):
                for x in range(len(grid[y])):
                    if grid[y][x] == '1':
                        wall = Wall(x * CELL_SIZE, y * CELL_SIZE)
                        PASSIVE_OBJECTS.append(wall)
                        DANGER_OBJECTS.append(wall)
                        wall.draw(canvas)
                    elif grid[y][x] == '2':
                        charger = Charger(x * CELL_SIZE, y * CELL_SIZE)
                        PASSIVE_OBJECTS.append(charger)
                        charger.draw(canvas)
    except FileNotFoundError:
        print("CSV file not found.")
        sys.exit()
    except ValueError as e:
        print(e)


    # hub1 = WiFiHub("Hub1",950,50)
    # PASSIVE_OBJECTS.append(hub1)
    # hub1.draw(canvas)
    # hub2 = WiFiHub("Hub2",50,500)
    # PASSIVE_OBJECTS.append(hub2)
    # hub2.draw(canvas)

    create_dirt(canvas)

    

def display_status(canvas, dirt_count, seconds_elapsed):
    canvas.create_text(10, 20, anchor="nw", font="Arial 14", 
                       text=f"Dirt Collected: {dirt_count}", tags="dirt_collected")
    canvas.create_text(GRID_SIZE - 10, 20, anchor="ne", font="Arial 14", 
                       text=f"Time Elapsed: {seconds_elapsed} s", tags="time_elapsed")
