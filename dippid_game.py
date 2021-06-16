import os
import sys
import time
import sched
import random
import DIPPID
from DIPPID import SensorUDP

# Author: Martina
# Reviewer: Claudia

# short explanation:
# class Input handler: creates the sensor and registers the callback for button 1, button 2 and the accelerometer
# class Game: creates the gamefield and a loop that updates the rows "moving to" the player character
#             and another loop that regularly checks if the player is moving his character (by asking the input handler)


class InputHandler():
    def __init__(self, portNum):
        self.playing = False
        self.turning = False
        self.connectDevice(portNum)

    def buttonPressed(self, number):
        # so it only works for releasing button and not pressing it
        if number == 0:
            self.playing = not self.playing

    def exitGame(self, number):
        print("Thanks for playing!")
        # this already kills our data flow and i do not have to open a new terminal or kill -9 pot to play again
        os._exit(0)

    def accelometer(self, numb):
        if (self.sensor.get_value('accelerometer')['x']) > 0.5:
            self.turning = "Left"
        elif(self.sensor.get_value('accelerometer')['x']) < -0.5:
            self.turning = "Right"
        else:
            self.turning = False

    def connectDevice(self, portNum):
        self.sensor = SensorUDP(int(portNum))
        self.sensor.register_callback('button_1', self.buttonPressed)
        self.sensor.register_callback('button_2', self.exitGame)
        self.sensor.register_callback('accelerometer', self.accelometer)

    def getPlaying(self):
        return self.playing

    def checkPlayerMovement(self):
        return self.turning


class Game():
    def __init__(self, inputValues):
        self.createGamefield()
        self.displayGame()
        self.counter = 0
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.scheduler.enter(1, None, self.updateRow, argument=(inputValues, ))
        self.scheduler.enter(0.25, None, self.updatePlayerPos, argument=(inputValues, ))
        self.scheduler.run()

    def createGamefield(self):
        self.gameField = [[" ", " ", "x", "x", " "],
                          [" ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " "],
                          [" ", "x", " ", " ", " "],
                          [" ", " ", "R", " ", " "]]
        for row in self.gameField:
            for symbol in row:
                print(symbol, end=' ')
            # for the new line use print with regular ending
            print("")

    def displayGame(self):
        # delete old line, idea from:
        # https://stackoverflow.com/questions/18248142/what-can-i-use-to-go-one-line-break-back-in-a-terminal-in-python
        for i in self.gameField[(len(self.gameField) - 1)]:
            print("\033[1A", end='\r')  # move cursor up one line
            print("\033[K", end='\r')   # delete line
        for row in self.gameField:
            for symbol in row:
                print(symbol, end=' ')
            # for the new line use print with regular ending
            print("")

    def updateRow(self, inputValues):
        if inputValues.getPlaying():
            # check for collision
            currentPos = self.currentPos(self.gameField[len(self.gameField)-1])
            if self.gameField[(len(self.gameField) - 2)][currentPos] == "x":
                print("Game over, you collided with an obstacle.")
                print("You succesfully passed ", self.counter, " rows! :D")
                inputValues.exitGame(0)
            # increase the counter
            self.counter = self.counter + 1
            # create new row with one obstacle at random position
            newArray = [" ", " ", " ", " ", " "]
            obstaclePos = random.randint(0, 4)
            newArray[obstaclePos] = "x"
            # move all rows (array counts from 0 so len must be taken -1
            for row in range((len(self.gameField) - 1), -1, -1):
                for symbol in range(len(self.gameField)):
                    # first row shows new content and therefore takes values from the newly created array
                    if row == 0:
                        self.gameField[row][symbol] = newArray[symbol]
                    else:
                        # all other rows "move" towards the player (R)
                        # except from the Player who remains in the same row
                        if self.gameField[row][symbol] != "R":
                            self.gameField[row][symbol] = self.gameField[row - 1][symbol]
            self.displayGame()
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
                    counter = len(self.gameField)-1
                    for symbol in self.gameField[len(self.gameField)-1]:
                        if counter == currentPos + 1:
                            self.gameField[len(self.gameField)-1][counter] = "R"
                        else:
                            self.gameField[len(self.gameField)-1][counter] = " "
                        counter = counter - 1
            if inputValues.checkPlayerMovement() == "Left":
                # if pos is not already at the left edge and if there occured no error
                if currentPos != 0 and currentPos is not False:
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
    instructionText = "Um das Spiel zu beginnen drückt man den '1' Button. \n"\
                      "Man spielt als 'R' und versucht den 'x' symbolen auszuweichen. \n"\
                      "Sich innerhalb des 5 x 5 Feldes nach links oder rechts bewegen,"\
                      " kann man mit rotieren des Handys. \n"\
                      "Wenn man an Hindernisse nicht frontal sondern von rechts oder links kommt,"\
                      " werden diese zerstört. \n"\
                      "Außerdem kann mit Pressen des '1' Button das Spiel pausieren oder fortfahren. \n"\
                      "Oder mit drücken des '2' Buttons, das Spiel komplett beenden."
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
    sys.exit()


if __name__ == '__main__':
    main()
