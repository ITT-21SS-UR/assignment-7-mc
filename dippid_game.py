import sys
import time
import sched
import DIPPID
from DIPPID import SensorUDP

# Author: Martina
# Reviewer: Claudia


class InputHandler():       
    def __init__(self, portNum):
        self.playing = False
        self.connectDevice(portNum)
        
    def buttonPressed(self, number):
        # so it only works for releasing button and not pressing it
        # print("modi: ", self.playing)
        if number == 0:
            self.playing = not self.playing
            print("changed modi: ", self.playing)
     
    def connectDevice(self, portNum):
        print("")
        self.sensor = SensorUDP(int(portNum))
        self.sensor.register_callback('button_1', self.buttonPressed)
        self.sensor.register_callback('accelerometer', self.buttonPressed)
        
    def getPlaying(self):
        return self.playing
        
    def checkPlayerMovement(self):
        if (self.sensor.get_value('accelerometer')['x']) > 0.5:
            return "Left"
        elif(self.sensor.get_value('accelerometer')['x']) < -0.5:
            return "Right"
        return False
        

class Game():
    def __init__(self, inputValues):
        self.createGamefield()
        self.displayGame()
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.scheduler.enter(1, None, self.updateRow, argument=(inputValues, ))
        self.scheduler.enter(0.25, None, self.updatePlayerPos, argument=(inputValues, ))
        self.scheduler.run()
        
    def createGamefield(self):
        self.gameField = [[" ", " ", "x", "x", " "],
                          [" ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " "],
                          [" ", " ", "R", " ", " "]]
                          
    def displayGame(self):
        for row in self.gameField:
            for symbol in row:
                print(symbol, end = ' ')
            # for the new line use print with regular ending
            print("")
        
    def updateRow(self, inputValues):
        if inputValues.getPlaying():
            print("movement is: ", inputValues.checkPlayerMovement())
        
        # create Loop
        self.scheduler.enter(1, None, self.updateRow, argument=(inputValues, ))
        
    def currentPos(self, array):
        counter = 0
        for element in array:
            if element == "R":
                return counter
            counter = counter + 1
        return False
        
    def updatePlayerPos(self, inputValues):
        if inputValues.getPlaying():
            # player is always in the last row
            currentPos = self.currentPos(self.gameField[len(self.gameField)-1])
            if inputValues.checkPlayerMovement() == "Right":
                # if pos is not already at the right edge and if there occured no error
                if currentPos != (len(self.gameField)-1) and currentPos != "False":
                    print("rechts gedreht")
                    counter = len(self.gameField)-1
                    for symbol in self.gameField[len(self.gameField)-1]:
                        if counter == currentPos + 1:
                            self.gameField[len(self.gameField)-1][counter] = "R"
                        else:
                            self.gameField[len(self.gameField)-1][counter] = " "
                        counter = counter - 1
            if inputValues.checkPlayerMovement() == "Left":
                print("links gedreht")
                # if pos is not already at the left edge and if there occured no error
                if currentPos != 0 and currentPos != False:
                    counter = 0
                    for symbol in self.gameField[len(self.gameField)-1]:
                        if counter == currentPos - 1:
                            self.gameField[len(self.gameField)-1][counter] = "R"
                        else:
                            self.gameField[len(self.gameField)-1][counter] = " "
                        counter = counter + 1
            
            self.displayGame()
        
        # create Loop
        self.scheduler.enter(0.25, None, self.updatePlayerPos, argument=(inputValues, ))
        


def writeInstruction():
    # if connection is lost last input continues...
    instructionText = "Um das Spiel zu beginnen drückt man den 1 Button. Man macht... \n"\
                      "Man spielt als R und versucht den 'x' symbolen auzuweichen. Dies kann man mit rotation des Handys. \n"\
                      "und man kann mit Pressen des 1 Button das Spiel pausieren oder fortfahren. \n"
    print(instructionText)


def main():
    # if setup file was not given
    if len(sys.argv) < 2:
        sys.stderr.write("Missing portnumber of the device (should be 5700) \n")
        sys.exit()
    else:
        port = sys.argv[1]
        inputValues = InputHandler(port)
    writeInstruction()
    Game(inputValues)
    # end program
    sys.exit()

if __name__ == '__main__':
    main()
