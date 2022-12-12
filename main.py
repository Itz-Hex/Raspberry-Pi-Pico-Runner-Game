# Imports
from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
import time
import math
import _thread

# Set up the button
button_l = Pin(8, Pin.IN, Pin.PULL_DOWN)
button_r = Pin(16, Pin.IN, Pin.PULL_DOWN)

# Set up I2C and the pins we're using for it
i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

# Set up the buzzer
buzzer = PWM(Pin(13))

# define music variables
volume = 10000
B6 = 1979
E7 = 2637
B3 = 246
E4 = 329
playJump = False
playDeath = False
playInteract = False
playBootup = False
playBootdown = False

# Short delay to stop I2C falling over
time.sleep(1) 

# Define the display and size (128x32)
display = SSD1306_I2C(128, 32, i2c)

# Define functions & classes

def triangle(x,y,h,c):
    w = int(math.ceil(h/(0.5*math.sqrt(3))))
    display.line(x,y+h,math.ceil(x+w/2),y,c)
    display.line(x+w,y+h,math.ceil(x+w/2),y,c)
    display.line(x,y+h,x+w,y+h,c)

class Player:
    x = 20
    y = 20
    speed = 10
    jumpPower = 12
    def move(self, t_x,t_y):
        triangle(t_x,t_y,10,1)
        self.x = t_x
        self.y = t_y
    def speedUp(self):
        self.speed -= 0.01
    def getSpeed(self):
        return self.speed
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def jump(self):
        self.y -= self.jumpPower
    def fall(self):
        self.y += self.jumpPower
    def draw(self):
        t_x = self.getX()
        t_y = self.getY()
        display.fill_rect(t_x, t_y, 10, 10, 1)
        
class Obstacle:
    x = 5
    y = 5
    def __init__(self, t_x=5, t_y=5):
        self.x = t_x
        self.y = t_y
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def move(self):
        self.x -= 5
    def resetX(self):
        self.x = 160
    def draw(self):
        triangle(self.getX(), self.getY(), 8, 1)
        
def drawLevel():
    display.hline(0, 30, 200, 1)
    drawObstacles()
    player.draw()
    
def drawObstacles():
    for obstacle in obstacles:
        obstacle.draw()

def moveObstacles():
    for obstacle in obstacles:
        if obstacle.getX() <= 0:
            obstacle.resetX()
        else:
            obstacle.move()
            
def gameOver():
    onScreen = True
    selected = 0
    display.invert(0)
    display.fill(0)
    display.text("GAME OVER!", 0, 0, 1)
    display.text("Score: "+str(score), 0, 12, 1)
    display.text(">Restart  Home", 0,24)
    display.show()
    while onScreen:
        time.sleep(0.2)
        if button_l():
            if selected == 0:
                selected = 1
                display.fill(0)
                display.text("GAME OVER!", 0, 0, 1)
                display.text("Score: "+str(score), 0, 12, 1)
                display.text(" Restart >Home", 0,24)
                display.show()
            else:
                selected = 0
                display.fill(0)
                display.text("GAME OVER!", 0, 0, 1)
                display.text("Score: "+str(score), 0, 12, 1)
                display.text(">Restart  Home", 0,24)
                display.show()
        if button_r():
            if selected == 0:
                onScreen = False
                startGame()
            else:
                onScreen = False
                home()

def startGame():
    global game
    global player
    global obstacles
    global playerIsInAir
    global timeInAir
    global score
    global fallTime
    game = True
    player = Player()
    obstacles = [Obstacle(60,21), Obstacle(110,21), Obstacle(160,21)]
    playerIsInAir = False
    timeInAir = 0
    score = 0
    fallTime = 1.15
    display.fill(0)
    display.show()
    
def home():
    global playInteract
    global playBootup
    global playBootdown
    onScreen = True
    selection = 0
    isOff = False
    display.fill(0)
    display.text("Cube Dash", 0, 0)
    display.text(">Start  Quit", 0, 24)
    display.show()
    while onScreen:
        time.sleep(0.2)
        if not isOff:
            if button_l():
                playInteract = True
                if selection == 0:
                    selection = 1
                    display.fill(0)
                    display.text("Cube Dash", 0, 0)
                    display.text(" Start >Quit", 0, 24)
                    display.show()
                elif selection == 1:
                    selection = 0
                    display.fill(0)
                    display.text("Cube Dash", 0, 0)
                    display.text(">Start  Quit", 0, 24)
                    display.show()
            elif button_r():
                playInteract = True
                if selection == 0:
                    onScreen = False
                    startGame()
                elif selection == 1:
                    playBootdown = True
                    isOff = True
                    display.poweroff()
        else:
            if button_l() or button_r():
                playBootup = True
                isOff = False
                display.poweron()

def secondThread():
    global playJump
    global playDeath
    global playInteract
    global playBootup
    global playBootdown
    while True:
        time.sleep(0.05)
        if playJump:
            jumpSFX()
            playJump = False
        elif playDeath:
            deathSFX()
            playDeath = False
        elif playInteract:
            interactSFX()
            playInteract = False
        elif playBootup:
            bootupSFX()
            playBootup = False
        elif playBootdown:
            bootdownSFX()
            playBootdown = False
        

def jumpSFX():
    buzzer.duty_u16(volume)
    buzzer.freq(B6)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(volume)
    buzzer.freq(E7)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)

def deathSFX():
    buzzer.duty_u16(volume)
    buzzer.freq(E4)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(volume)
    buzzer.freq(B3)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    
def interactSFX():
    buzzer.duty_u16(volume)
    buzzer.freq(B6)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)

def bootupSFX():
    buzzer.duty_u16(volume)
    buzzer.freq(B3)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(volume)
    buzzer.freq(B6)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(volume)
    buzzer.freq(E7)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(volume)
    buzzer.freq(E7)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)

def bootdownSFX():
    buzzer.duty_u16(volume)
    buzzer.freq(E7)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(volume)
    buzzer.freq(E7)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    time.sleep(0.1)
    buzzer.duty_u16(volume)
    buzzer.freq(B6)
    time.sleep(0.05)
    buzzer.duty_u16(0)
    buzzer.duty_u16(volume)
    buzzer.freq(B3)
    time.sleep(0.05)
    buzzer.duty_u16(0)

# Create variables
game = False
player = Player()
obstacles = [Obstacle(60,21), Obstacle(110,21), Obstacle(160,21)]
playerIsInAir = False
timeInAir = 0
score = 0
fallTime = 1.15

def mainThread():
    global game
    global player
    global obstacles
    global playerIsInAir
    global timeInAir
    global score
    global fallTime
    global playJump
    global playDeath
    
    home()

    while game:
        display.fill(0)
        drawLevel()
        
        speed = player.getSpeed()
        fallTime = 1.15/10*speed
        time.sleep(speed/60)
        moveObstacles()
        
        if button_l() == 1 and not playerIsInAir:
            player.jump()
            playJump = True
        
        if player.getY() < 20:
            playerIsInAir = True
        
        if playerIsInAir:
            timeInAir += speed/60
        
        if playerIsInAir and timeInAir > fallTime:
            player.fall()
            playerIsInAir = False
            timeInAir = 0
            
        score += 1
        display.text("Score: "+str(score),0,0)
        
        if not int(math.floor(score/100.0))%2 == 0:
            display.invert(1)
        else:
            display.invert(0)
            
        if not int(math.floor(score/10.0))%15 == 0 and score > 200:
            player.speedUp()
        elif not int(math.floor(score/10.0))%10 == 0 and score > 600:
            player.speedUp()
        elif not int(math.floor(score/10.0))%5 == 0 and score > 1000:
            player.speedUp()
        elif not int(math.floor(score/10.0))%3 == 0 and score > 2000:
            player.speedUp()
            
        display.show()
        
        for obstacle in obstacles:
            if player.getX() == obstacle.getX() and not playerIsInAir:
                game = False
                playDeath = True
                gameOver()

second_thread = _thread.start_new_thread(secondThread, ())
mainThread()
