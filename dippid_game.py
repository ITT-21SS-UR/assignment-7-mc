import os
import random
import sched
import sys
import time

from DIPPID import SensorUDP

"""
The workload was distributed evenly and tasks were discussed together.

short explanation:
class Input handler: creates the sensor and registers the callback for button 1, button 2 and the accelerometer
class Game: creates the game field and a loop that updates the rows "moving to" the player character
            and another loop that regularly checks if the player is moving his character (by asking the input handler)

"""


# Author: Martina
# Reviewer: Claudia
class InputHandler():
    def __init__(self, port_number):
        self.__playing = False
        self.__turning = False
        self.__connect_device(port_number)

    def __button_pressed(self, number):
        # so it only works for releasing button and not pressing it
        if number == 0:
            self.__playing = not self.__playing

    def exit_game(self):
        print("Danke fürs Mitspielen!")
        # this already kills our data flow and i do not have to open a new terminal or kill -9 pot to play again
        os._exit(0)

    def __handle_accelerometer(self, numb):
        if (self.__sensor.get_value("accelerometer")['x']) > 0.5:
            self.__turning = "Left"
        elif (self.__sensor.get_value("accelerometer")['x']) < -0.5:
            self.__turning = "Right"
        else:
            self.__turning = False

    def __connect_device(self, port_number):
        self.__sensor = SensorUDP(int(port_number))
        self.__sensor.register_callback("button_1", self.__button_pressed)
        self.__sensor.register_callback("button_2", self.exit_game)
        self.__sensor.register_callback("accelerometer", self.__handle_accelerometer)

    def get_playing(self):
        return self.__playing

    def check_player_movement(self):
        return self.__turning


class Game():
    def __init__(self, input_values):
        self.__create_game_field()
        self.__display_game()
        self.__counter = 0

        self.__setup_scheduler(input_values)

    def __setup_scheduler(self, input_values):
        self.__scheduler = sched.scheduler(time.time, time.sleep)
        self.__scheduler.enter(1, None, self.__update_row, argument=(input_values,))
        self.__scheduler.enter(0.25, None, self.__update_player_pos, argument=(input_values,))
        self.__scheduler.run()

    def __create_game_field(self):
        self.__game_field = [[" ", " ", "x", "x", " "],
                             [" ", " ", " ", " ", " "],
                             [" ", " ", " ", " ", " "],
                             [" ", "x", " ", " ", " "],
                             [" ", " ", "R", " ", " "]]

        for row in self.__game_field:
            for symbol in row:
                print(symbol, end=' ')
            # for the new line use print with regular ending
            print("")

    def __display_game(self):
        # delete old line, idea from:
        # https://stackoverflow.com/questions/18248142/what-can-i-use-to-go-one-line-break-back-in-a-terminal-in-python
        for i in self.__game_field[(len(self.__game_field) - 1)]:
            print("\033[1A", end='\r')  # move cursor up one line
            print("\033[K", end='\r')  # delete line

        for row in self.__game_field:
            for symbol in row:
                print(symbol, end=' ')
            # for the new line use print with regular ending
            print("")

    def __update_row(self, input_values):
        if input_values.get_playing():
            self.__check_for_collision(input_values)
            self.__counter = self.__counter + 1
            self.__move_all_rows(self.__create_new_obstacle_row())

            self.__display_game()

        # create Loop
        self.__scheduler.enter(1, None, self.__update_row, argument=(input_values,))

    def __check_for_collision(self, input_values):
        current_pos = self.current_pos(self.__game_field[len(self.__game_field) - 1])

        if self.__game_field[(len(self.__game_field) - 2)][current_pos] == "x":
            print("Game over, du bist mit einem Hindernis kollidiert. (-_-)")
            print("Du hast erfolgreich ", self.__counter, " Reihen bezwungen! :D")

            input_values.exit_game()

    @staticmethod
    def __create_new_obstacle_row():
        # create new row with one obstacle at random position
        new_obstacle_row = [" ", " ", " ", " ", " "]
        obstacle_pos = random.randint(0, 4)
        new_obstacle_row[obstacle_pos] = "x"

        return new_obstacle_row

    def __move_all_rows(self, new_obstacle_row):
        # move all rows (array counts from 0 so len must be taken -1
        for row in range((len(self.__game_field) - 1), -1, -1):
            for symbol in range(len(self.__game_field)):
                # first row shows new content and therefore takes values from the newly created obstacle row
                if row == 0:
                    self.__game_field[row][symbol] = new_obstacle_row[symbol]
                else:
                    # all other rows "move" towards the player (R)
                    # except from the Player who remains in the same row
                    if self.__game_field[row][symbol] != "R":
                        self.__game_field[row][symbol] = self.__game_field[row - 1][symbol]

    @staticmethod
    def current_pos(array):
        counter = 0
        for element in array:
            if element == "R":
                return counter

            counter = counter + 1

        return False

    def __update_player_pos(self, input_values):
        if input_values.get_playing():
            # player is always in the last row
            current_pos = self.current_pos(self.__game_field[len(self.__game_field) - 1])
            if input_values.check_player_movement() == "Right":
                self.__handle_right_movement(current_pos)

            if input_values.check_player_movement() == "Left":
                self.__handle_left_movement(current_pos)

            self.__display_game()

        # create Loop
        self.__scheduler.enter(0.25, None, self.__update_player_pos, argument=(input_values,))

    def __handle_right_movement(self, current_pos):
        # if pos is not already at the right edge and if there occurred no error
        if current_pos != (len(self.__game_field) - 1) and current_pos != "False":
            counter = len(self.__game_field) - 1
            for symbol in self.__game_field[len(self.__game_field) - 1]:
                if counter == current_pos + 1:
                    self.__game_field[len(self.__game_field) - 1][counter] = "R"
                else:
                    self.__game_field[len(self.__game_field) - 1][counter] = " "

                counter = counter - 1

    def __handle_left_movement(self, current_pos):
        # if pos is not already at the left edge and if there occurred no error
        if current_pos != 0 and current_pos is not False:
            counter = 0
            for symbol in self.__game_field[len(self.__game_field) - 1]:
                if counter == current_pos - 1:
                    self.__game_field[len(self.__game_field) - 1][counter] = "R"
                else:
                    self.__game_field[len(self.__game_field) - 1][counter] = " "

                counter = counter + 1


def write_instruction():
    # if connection is lost last input continues...
    instruction_text = "Um das Spiel zu beginnen drückt man den '1' Button. \n" \
                       "Man spielt als 'R' und versucht den 'x' Symbolen auszuweichen. \n" \
                       "Sich innerhalb des 5 x 5 Feldes nach links oder rechts bewegen," \
                       " kann man mit rotieren des Handys. \n" \
                       "Wenn man an Hindernisse nicht frontal, sondern von rechts oder links kommt," \
                       " werden diese zerstört. \n" \
                       "Außerdem kann mit Pressen des '1' Button das Spiel pausieren oder fortfahren. \n" \
                       "Oder mit drücken des '2' Buttons, das Spiel komplett beenden."
    print(instruction_text)


def main():
    # if setup file was not given
    if len(sys.argv) < 2:
        sys.stderr.write("Missing port number of the device (should be 5700) \n")
        sys.exit()

    port = sys.argv[1]
    input_values = InputHandler(port)

    write_instruction()
    Game(input_values)
    sys.exit()


if __name__ == '__main__':
    main()
