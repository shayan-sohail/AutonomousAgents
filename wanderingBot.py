import random
import math
import numpy as np
import environment as env

#the bot template is taken from worksheets
class Brain():

    def __init__(self,botp):
        self.bot = botp
        self.turningCount = 0
        self.movingCount = random.randrange(50,100)
        self.currentlyTurning = False

    # modify this to change the robot's behaviour
    def thinkAndAct(self, chargerL, chargerR, x, y, sl, sr, battery):
        newX = None
        newY = None

        obstacle = self.bot.isObstacleInFront()

        # Check for obstacles and adjust behavior
        if obstacle:
            # If there's an obstacle, decide on a new turning direction
            if self.currentlyTurning:
                speedLeft = -2.0  # Continue turning in the current direction
                speedRight = 2.0
            else:
                # Switch turning direction when a new obstacle is detected
                self.currentlyTurning = True
                self.turningCount = 10  # Turn for 10 cycles
                speedLeft = 2.0
                speedRight = -2.0
        else:
            # Usual behavior when no obstacles are detected
            if self.currentlyTurning:
                speedLeft = -2.0
                speedRight = 2.0
                self.turningCount -= 1
            else:
                speedLeft = 5.0
                speedRight = 5.0
                self.movingCount -= 1
            if self.movingCount == 0 and not self.currentlyTurning:
                self.turningCount = random.randrange(20, 40)
                self.currentlyTurning = True
            if self.turningCount == 0 and self.currentlyTurning:
                self.movingCount = random.randrange(50, 100)
                self.currentlyTurning = False

        # # Continue existing logic for power management
        if battery < 600:
            if chargerR > chargerL:
                speedLeft = 2.0
                speedRight = -2.0
            elif chargerR < chargerL:
                speedLeft = -2.0
                speedRight = 2.0
            if abs(chargerR-chargerL) < chargerL * 0.1:
                speedLeft = 5.0
                speedRight = 5.0

        if chargerL + chargerR > 200 and battery < 1000:
            speedLeft = 0.0
            speedRight = 0.0

        #toroidal geometry
        if x>env.GRID_SIZE:
            newX = 0
        if x<0:
            newX = env.GRID_SIZE
        if y>env.GRID_SIZE:
            newY = 0
        if y<0:
            newY = env.GRID_SIZE

        return speedLeft, speedRight, newX, newY


class Bot():

    def __init__(self,namep):
        self.name = namep
        self.x = random.randint(100,900) #starting location
        self.y = random.randint(100,900)
        self.theta = random.uniform(0.0,2.0*math.pi)
        #self.theta = 0
        self.ll = 60 #axle width
        self.sl = 0.0 #speedleft
        self.sr = 0.0 #speedright
        self.battery = 700
        self.collided = False

    def thinkAndAct(self, agents, passiveObjects):
        chargerL, chargerR = self.senseChargers(passiveObjects)
        # print(f"ChargeL: {chargerL}, ChargeR: {chargerR}")
        self.sl, self.sr, xx, yy = self.brain.thinkAndAct(chargerL, chargerR, self.x, self.y, self.sl, self.sr, self.battery)
        
        if xx != None:
            self.x = xx
        if yy != None:
            self.y = yy
        
    def setBrain(self,brainp):
        self.brain = brainp

    def senseChargers(self, passiveObjects):
        chargerL = 0.0
        chargerR = 0.0
        for pp in passiveObjects:
            if isinstance(pp,env.Charger):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt( (lx-self.sensorPositions[0])*(lx-self.sensorPositions[0]) + \
                                       (ly-self.sensorPositions[1])*(ly-self.sensorPositions[1]) )
                distanceR = math.sqrt( (lx-self.sensorPositions[2])*(lx-self.sensorPositions[2]) + \
                                       (ly-self.sensorPositions[3])*(ly-self.sensorPositions[3]) )
                chargerL += 200000/(distanceL*distanceL)
                chargerR += 200000/(distanceR*distanceR)
        return chargerL, chargerR

    def distanceTo(self,obj):
        xx,yy = obj.getLocation()
        return math.sqrt( math.pow(self.x-xx,2) + math.pow(self.y-yy,2) )

    def isObstacleInFront(self):
        # Simulating a forward sensor by checking the position in front of the bot
        forward_x = self.x + math.cos(self.theta) * 20  # Check 20 units ahead in the direction of theta
        forward_y = self.y + math.sin(self.theta) * 20
        return env.is_wall(forward_x, forward_y)

    def update(self,canvas,passiveObjects,dt):
        self.battery -= 1
        for rr in passiveObjects:
            if isinstance(rr,env.Charger) and self.distanceTo(rr)<80:
                self.battery += 10
        if self.battery<=0:
            self.battery = 0

        self.collided = self.isCollided(canvas)
        self.move(canvas,dt)

    def draw(self,canvas):
        self.points = [ (self.x + 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x + 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta)  \
                ]
        
        canvas.create_polygon(self.points, fill="blue", tags=self.name)

        self.sensorPositions = [ (self.x + 20*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y - 20*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta), \
                                 (self.x - 20*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y + 20*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta)  \
                            ]
    
        centre1PosX = self.x 
        centre1PosY = self.y
        canvas.create_oval(centre1PosX-16,centre1PosY-16,\
                           centre1PosX+16,centre1PosY+16,\
                           fill="gold",tags=self.name)
        canvas.create_text(self.x,self.y,text=str(self.battery),tags=self.name)

        wheel1PosX = self.x - 30*math.sin(self.theta)
        wheel1PosY = self.y + 30*math.cos(self.theta)
        canvas.create_oval(wheel1PosX-3,wheel1PosY-3,\
                                         wheel1PosX+3,wheel1PosY+3,\
                                         fill="red",tags=self.name)

        wheel2PosX = self.x + 30*math.sin(self.theta)
        wheel2PosY = self.y - 30*math.cos(self.theta)
        canvas.create_oval(wheel2PosX-3,wheel2PosY-3,\
                                         wheel2PosX+3,wheel2PosY+3,\
                                         fill="green",tags=self.name)

        sensor1PosX = self.sensorPositions[0]
        sensor1PosY = self.sensorPositions[1]
        sensor2PosX = self.sensorPositions[2]
        sensor2PosY = self.sensorPositions[3]
        canvas.create_oval(sensor1PosX-3,sensor1PosY-3, \
                           sensor1PosX+3,sensor1PosY+3, \
                           fill="yellow",tags=self.name)
        canvas.create_oval(sensor2PosX-3,sensor2PosY-3, \
                           sensor2PosX+3,sensor2PosY+3, \
                           fill="yellow",tags=self.name)

    def isCollided(self, canvas):
        x1,y1,x2,y2,x3,y3,x4,y4 = self.points
        if env.is_wall(x1, y1) or env.is_wall(x2, y2) or env.is_wall(x3, y3) or env.is_wall(x4, y4):
            return True
        return False
    
    # handles the physics of the movement
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self,canvas,dt):
        # print(self.battery)

        if self.battery==0:
            self.sl = 0

        if self.sl==self.sr:
            R = 0
        else:
            R = (self.ll/2.0)*((self.sr+self.sl)/(self.sl-self.sr))

        omega = (self.sl-self.sr)/self.ll
        ICCx = self.x-R*math.sin(self.theta) #instantaneous centre of curvature
        ICCy = self.y+R*math.cos(self.theta)
        m = np.matrix( [ [math.cos(omega*dt), -math.sin(omega*dt), 0], \
                        [math.sin(omega*dt), math.cos(omega*dt), 0],  \
                        [0,0,1] ] )
        v1 = np.matrix([[self.x-ICCx],[self.y-ICCy],[self.theta]])
        v2 = np.matrix([[ICCx],[ICCy],[omega*dt]])
        newv = np.add(np.dot(m,v1),v2)
        newX = newv.item(0)
        newY = newv.item(1)
        newTheta = newv.item(2)
        newTheta = newTheta%(2.0*math.pi) #make sure angle doesn't go outside [0.0,2*pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta        
        if self.sl==self.sr: # straight line movement
            self.x += self.sr*math.cos(self.theta) #sr wlog
            self.y += self.sr*math.sin(self.theta)
        canvas.delete(self.name)
        self.draw(canvas)

    def collectDirt(self, canvas, passiveObjects, count):
        global totalDirtCount
        toDelete = []
        for idx,rr in enumerate(passiveObjects):
            if isinstance(rr,env.Dirt):
                if self.distanceTo(rr)<30:
                    canvas.delete(rr.name)
                    toDelete.append(idx)
                    count.itemCollected(canvas)
                    totalDirtCount = count.dirtCollected

        for ii in sorted(toDelete,reverse=True):
            del passiveObjects[ii]
        return passiveObjects
   
