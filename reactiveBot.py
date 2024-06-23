import random
import math
import numpy as np
import environment as env

#the bot template is taken from worksheets
sensor_range = 100
class Brain():

    def __init__(self,botp):
        self.bot = botp
        self.turningCount = 0
        self.movingCount = random.randrange(50,100)
        self.currentlyTurning = False
        self.time = 0
        self.trainingSet = []
        self.dangerThreshold = 0

    def thinkAndAct(self, chargerL, chargerR, x, y, sl, sr,\
                    battery, camera, collision):
        dangerDetected = False

        trainingTime = 100
        if self.time<trainingTime:
            self.trainingSet.append((camera,collision))
        elif self.time==trainingTime:
            warningValues = []
            for i,tt in enumerate(self.trainingSet):
                if i>=5 and tt[1]==True:
                    warningValues.append(self.trainingSet[i-5][0])
            countWV = 0
            sumWV = 0
            for wv in warningValues:
                if not wv==[0]*9:
                    sumWV += max(wv)
                    countWV += 1
            if countWV != 0:
                self.dangerThreshold = sumWV/countWV

            print("Bot Danger Threshold: ", end="")
            print(self.dangerThreshold)
        elif self.time>trainingTime:
            if any(c>self.dangerThreshold for c in camera):
                dangerDetected = True
            
        self.time += 1
        
        newX = None
        newY = None
        
        if self.currentlyTurning==True:
            speedLeft = -2.0
            speedRight = 2.0
            self.turningCount -= 1
        else:
            speedLeft = 5.0
            speedRight = 5.0
            self.movingCount -= 1
        if self.movingCount==0 and not self.currentlyTurning:
            self.turningCount = random.randrange(20,40)
            self.currentlyTurning = True
        if self.turningCount==0 and self.currentlyTurning:
            self.movingCount = random.randrange(50,100)
            self.currentlyTurning = False

        #battery - these are later so they have priority
        if battery<600:
            if chargerR>chargerL:
                speedLeft = 2.0
                speedRight = -2.0
            elif chargerR<chargerL:
                speedLeft = -2.0
                speedRight = 2.0
            if abs(chargerR-chargerL)<chargerL*0.1: #approximately the same
                speedLeft = 5.0
                speedRight = 5.0
        if chargerL+chargerR>200 and battery<1000:
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

        

        return speedLeft, speedRight, newX, newY, dangerDetected

class Bot():

    def __init__(self,namep,canvasp):
        self.name = namep
        self.canvas = canvasp
        self.x = random.randint(100,900)
        self.y = random.randint(100,900)
        self.theta = random.uniform(0.0,2.0*math.pi)
        #self.theta = 0
        self.ll = 60 #axle width
        self.sl = 0.0
        self.sr = 0.0
        self.battery = 1000
 

    def thinkAndAct(self, agents, passiveObjects):
        chargerL, chargerR = self.senseChargers(passiveObjects)
        collision = self.collision(agents)

        view = self.look(agents)
        self.sl, self.sr, xx, yy, dangerDetected = self.brain.thinkAndAct\
            (chargerL, chargerR, self.x, self.y, \
             self.sl, self.sr, self.battery, view, collision)
        if (dangerDetected):
            self.reactToDanger()
        if xx != None:
            self.x = xx
        if yy != None:
            self.y = yy
        
    def setBrain(self,brainp):
        self.brain = brainp

    def reactToDanger(self):
        print("dangerous situation - analyzing escape route")
        # Analyze sensor data to find the direction with the least obstacles
        min_sensor_value = min(self.view)  # Find the minimum value from sensor data
        min_sensor_index = self.view.index(min_sensor_value)  # Get the index of the minimum sensor value
        
        # Calculate the angle to turn towards based on the sensor index
        # Assuming sensors are evenly spaced and cover a range in front of the robot
        num_sensors = len(self.view)
        sensor_span = 120  # Degrees that the sensors cover in front of the robot
        angle_per_sensor = sensor_span / (num_sensors - 1)
        
        # Calculate the angle to turn to point towards the direction with minimal obstacles
        angle_to_min_sensor = (min_sensor_index * angle_per_sensor) - (sensor_span / 2)
        
        # Adjust robot's orientation based on the calculated angle
        self.theta += math.radians(angle_to_min_sensor)
        
        # Normalize the angle of theta
        self.theta = self.theta % (2 * math.pi)
        
        # Set speeds to move forward in the new direction
        self.sl = 2.0
        self.sr = 2.0

        # Reset the movement and turning count to allow for new movement pattern
        self.turningCount = 0
        self.movingCount = random.randrange(50, 100)
        self.currentlyTurning = False

        print(f"Turning to angle: {math.degrees(self.theta)} degrees due to minimal sensor input at index {min_sensor_index}")



    def look(self,agents):
        self.view = [0]*9
        for idx,pos in enumerate(self.cameraPositions):
            for cc in agents:
                if isinstance(cc,env.Wall):
                    dd = self.distanceTo(cc)
                    scaledDistance = max(sensor_range-dd,0)/sensor_range
                    ncx = cc.x-pos[0] #cat if robot were at 0,0
                    ncy = cc.y-pos[1]
                    #print(abs(angle-self.theta)%2.0*math.pi)
                    m = math.tan(self.theta)
                    A = m*m+1
                    B = 2*(-m*ncy-ncx)
                    r = 15 #radius
                    C = ncy*ncy - r*r + ncx*ncx 
                    if B*B-4*A*C>=0 and scaledDistance>self.view[idx]:
                        self.view[idx] = scaledDistance
        self.canvas.delete("view")
        for vv in range(9):
            if self.view[vv]==0:
                self.canvas.create_rectangle(850+vv*15,50,850+vv*15+15,65,fill="white",tags="view")
            if self.view[vv]>0:
                colour = hex(15-math.floor(self.view[vv]*16.0)) #scale to 0-15 -> hex
                fillHex = "#"+colour[2]+colour[2]+colour[2]
                self.canvas.create_rectangle(850+vv*15,50,850+vv*15+15,65,fill=fillHex,tags="view")
        return self.view

    #returns sensors values that detect chargers
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

    # what happens at each timestep
    def update(self,canvas,passiveObjects,dt):
        # for now, the only thing that changes is that the robot moves
        #   (using the current settings of self.sl and self.sr)
        self.battery -= 1
        for rr in passiveObjects:
            if isinstance(rr,env.Charger) and self.distanceTo(rr)<80:
                self.battery += 10
        if self.battery<=0:
            self.battery = 0
        self.move(canvas,dt)

    # draws the robot at its current position
    def draw(self,canvas):

        self.cameraPositions = []
        for pos in range(20,-21,-5):
            self.cameraPositions.append( ( (self.x + pos*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y - pos*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta) ) )
        for xy in self.cameraPositions:
            canvas.create_oval(xy[0]-2,xy[1]-2,xy[0]+2,xy[1]+2,fill="purple1",tags=self.name)
        for xy in self.cameraPositions:
            canvas.create_line(xy[0],xy[1],xy[0]+sensor_range*math.cos(self.theta),xy[1]+sensor_range*math.sin(self.theta),fill="light grey",tags=self.name)
            

        points = [ (self.x + 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x + 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta)  \
                ]
        canvas.create_polygon(points, fill="green", tags=self.name)

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

    # handles the physics of the movement
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self,canvas,dt):
        if self.battery==0:
            self.sl = 0
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
        toDelete = []
        for idx,rr in enumerate(passiveObjects):
            if isinstance(rr,env.Dirt):
                if self.distanceTo(rr)<30:
                    canvas.delete(rr.name)
                    toDelete.append(idx)
                    count.itemCollected(canvas)
        for ii in sorted(toDelete,reverse=True):
            del passiveObjects[ii]
        return passiveObjects

    def collision(self,agents):
        collision = False
        for rr in agents:
            if isinstance(rr,env.Wall):
                if self.distanceTo(rr)<50.0:
                    collision = True
        return collision