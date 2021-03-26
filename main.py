import tkinter as tk
import random

from gamelib import Sprite, GameApp, Text

from dir_consts import *
from maze import Maze

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

UPDATE_DELAY = 33

PACMAN_SPEED = 5

class Pacman(Sprite):
    def __init__(self, app, maze, r, c, photo_image=None):
        self.r = r
        self.c = c
        self.maze = maze

        self.dot_eaten_observers = []

        self.direction = DIR_STILL
        self.next_direction = DIR_STILL

        # self.is_super_speed = False
        # self.super_speed_counter = 0
        self.state = NormalPacmanState(self)

        x, y = maze.piece_center(r,c)
        super().__init__(app, 'images/pacman.png', x, y, photo_image)

    def update(self):
        if self.maze.is_at_center(self.x, self.y):
            r, c = self.maze.xy_to_rc(self.x, self.y)

            if self.maze.has_dot_at(r, c):
                self.maze.eat_dot_at(r, c)

                self.state.random_upgrade()

                for i in self.dot_eaten_observers:
                    i()

                # if random.random() < 0.1:
                #     if not self.is_super_speed:
                #         self.is_super_speed = True
                #         self.super_speed_counter = 0
            
            if self.maze.is_movable_direction(r, c, self.next_direction):
                self.direction = self.next_direction
            else:
                self.direction = DIR_STILL
        
        self.state.move_pacman()

        # if self.is_super_speed:
        #     speed = 2 * PACMAN_SPEED
        #     self.super_speed_counter += 1
        #     if self.super_speed_counter > 50:
        #         self.is_super_speed = False
        # else:
        #     speed = PACMAN_SPEED

        # self.x += speed * DIR_OFFSET[self.direction][0]
        # self.y += speed * DIR_OFFSET[self.direction][1]

    def set_next_direction(self, direction):
        self.next_direction = direction


class PacmanGame(GameApp):
    def init_game(self):
        self.maze = Maze(self, CANVAS_WIDTH, CANVAS_HEIGHT)

        self.pacman1_image = tk.PhotoImage(file='images/pacman1.png')
        self.pacman2_image = tk.PhotoImage(file='images/pacman2.png')

        self.pacman1 = Pacman(self, self.maze, 1, 1, self.pacman1_image)
        self.pacman2 = Pacman(self, self.maze, self.maze.get_height() - 2, self.maze.get_width() - 2, self.pacman2_image)

        self.pacman1_score_text = Text(self, 'P1: 0', 100, 20)
        self.pacman2_score_text = Text(self, 'P2: 0', 600, 20)

        self.elements.append(self.pacman1)
        self.elements.append(self.pacman2)

        self.pacman1_score = 0
        self.pacman2_score = 0

        self.pacman1.dot_eaten_observers.append(self.dot_eaten_by_pacman1)
        self.pacman2.dot_eaten_observers.append(self.dot_eaten_by_pacman2)

        self.command_map = {
            'W': self.get_pacman_next_direction_function(self.pacman1, DIR_UP),
            'A': self.get_pacman_next_direction_function(self.pacman1, DIR_LEFT),
            'S': self.get_pacman_next_direction_function(self.pacman1, DIR_DOWN),
            'D': self.get_pacman_next_direction_function(self.pacman1, DIR_RIGHT),
            'I': self.get_pacman_next_direction_function(self.pacman2, DIR_UP),
            'J': self.get_pacman_next_direction_function(self.pacman2, DIR_LEFT),
            'K': self.get_pacman_next_direction_function(self.pacman2, DIR_DOWN),
            'L': self.get_pacman_next_direction_function(self.pacman2, DIR_RIGHT),
        }
    
    def get_pacman_next_direction_function(self, pacman, next_direction):

        def f():
            pacman.set_next_direction(next_direction)

        return f

    def pre_update(self):
        pass

    def post_update(self):
        pass

    def update_scores(self):
        self.pacman1_score_text.set_text(f'P1: {self.pacman1_score}')
        self.pacman2_score_text.set_text(f'P2: {self.pacman2_score}')
    
    def dot_eaten_by_pacman1(self):
        self.pacman1_score += 1
        self.update_scores()

    def dot_eaten_by_pacman2(self):
        self.pacman2_score += 1
        self.update_scores()

    def on_key_pressed(self, event):
        ch = event.char.upper()
        if ch in self.command_map.keys():
            self.command_map[ch]()


class NormalPacmanState:
    def __init__(self, pacman):
        self.pacman = pacman
   
    def random_upgrade(self):
        if random.random() < 0.1:
            self.pacman.state = SuperPacmanState(self.pacman)

    def move_pacman(self):
        self.pacman.x += PACMAN_SPEED * DIR_OFFSET[self.pacman.direction][0]
        self.pacman.y += PACMAN_SPEED * DIR_OFFSET[self.pacman.direction][1]


class SuperPacmanState:
    def __init__(self, pacman):
        self.pacman = pacman
        self.super_speed_counter = 0
        self.speed = PACMAN_SPEED
   
    def random_upgrade(self):
        self.speed = 2 * PACMAN_SPEED

    def move_pacman(self):
        # TODO:
        #   - update the pacman's location with super speed
        #   - update the counter, if the counter >= 50, set state back to NormalPacmanState
        self.super_speed_counter += 1
        if self.super_speed_counter > 50:
            self.pacman.state = NormalPacmanState(self.pacman)
        self.pacman.x += self.speed * DIR_OFFSET[self.pacman.direction][0]
        self.pacman.y += self.speed * DIR_OFFSET[self.pacman.direction][1]


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pacman Game")
 
    # do not allow window resizing
    root.resizable(False, False)
    app = PacmanGame(root, CANVAS_WIDTH, CANVAS_HEIGHT, UPDATE_DELAY)
    app.start()
    root.mainloop()
