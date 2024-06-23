import tkinter as tk
import numpy as np
import environment as env
import time
import sys
import wanderingBot as wb
import reactiveBot as rb

totalDirtCount = 0 
start_time = 0 
elapsed_time = 0 
prev_time = 0

def initialise(window):
    window.title("Simulation-1")
    window.resizable(False, False)
    canvas = tk.Canvas(window, width=env.GRID_SIZE, height=env.GRID_SIZE)
    canvas.pack()
    return canvas
  
def create_agents(canvas,noOfAgents):
    agents = []

    for i in range(0,3):
        wbot = wb.Bot("WB" + str(i))
        brain = wb.Brain(wbot)
        wbot.setBrain(brain)
        agents.append(wbot)
        wbot.draw(canvas)
    
    for i in range(0,2):
        rbot = rb.Bot("RB" + str(i), canvas)
        brain = rb.Brain(rbot)
        rbot.setBrain(brain)
        agents.append(rbot)
        rbot.draw(canvas)

    count = env.Counter()
    return agents, count

def moveIt(canvas,agents,passiveObjects,count,moves):
    global elapsed_time, prev_time
    elapsed_time = (int)(time.time()) - (int)(start_time)
    if ((time.time() - start_time) - prev_time >1):
        prev_time = elapsed_time
        count.updateTime(canvas, elapsed_time)

    if totalDirtCount == env.DIRT_COUNT:
            print("All Dirt Collected")
            sys.exit()

    for rr in agents:
        rr.thinkAndAct(env.DANGER_OBJECTS,passiveObjects)
        rr.update(canvas,passiveObjects,1.0)
        passiveObjects = rr.collectDirt(canvas,passiveObjects,count)
        moves +=1
    canvas.after(20,moveIt,canvas,agents,passiveObjects,count,moves)

def main():
    global start_time
    window = tk.Tk()
    canvas = initialise(window)
    env.create_passive_objects(canvas, env.WALL_FILE)
    agents, count = create_agents(canvas,1)
    start_time = (int)(time.time())
    moveIt(canvas,agents,env.PASSIVE_OBJECTS,count,0)

    window.mainloop()

if __name__ == "__main__":
    
    main()
