import tkinter as tk
import random
from tkinter import messagebox

from gamelib import Sprite, GameApp, Text

from dir_consts import *
from maze import Maze

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

UPDATE_DELAY = 33

PACMAN_SPEED = 5

class Pacman(Sprite):
    def __init__(self, app, maze, r, c, photo_image=None):
        self.is_ghost = False
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


class Ghost(Sprite):
    def __init__(self, app, maze, r, c, photo_image=None):
        self.is_ghost = True
        self.r = r
        self.c = c
        self.maze = maze

        self.dot_eaten_observers = []

        self.direction = DIR_STILL
        self.next_direction = DIR_STILL

        self.state = NormalPacmanState(self)

        x, y = maze.piece_center(r,c)
        super().__init__(app, 'images/pacman.png', x, y, photo_image)
    
    def update(self):
        if self.maze.is_at_center(self.x, self.y):
            r, c = self.maze.xy_to_rc(self.x, self.y)
        
            if self.maze.is_movable_direction(r, c, self.next_direction):
                self.direction = self.next_direction
            else:
                self.direction = DIR_STILL
        
        self.state.move_pacman()
    
    def movable_ways(self):
        turn = []
        if not self.maze.has_wall_at(self.r+1, self.c):
            turn.append(DIR_DOWN)
        if not self.maze.has_wall_at(self.r-1, self.c):
            turn.append(DIR_UP)
        if not self.maze.has_wall_at(self.r, self.c+1):
            turn.append(DIR_RIGHT)
        if not self.maze.has_wall_at(self.r, self.c-1):
            turn.append(DIR_LEFT)
        if len(turn) > 0:
            return turn
        else:
            return False
    
    def set_next_direction(self, direction):
        self.next_direction = direction


class PacmanGame(GameApp):
    def init_game(self):
        self.game_started = False
        self.maze = Maze(self, CANVAS_WIDTH, CANVAS_HEIGHT)

        self.pacman1_image = tk.PhotoImage(file='images/pacman1.png')
        self.pacman2_image = tk.PhotoImage(file='images/pacman2.png')

        self.ghost1_image = tk.PhotoImage(file='images/ghost1.png')
        self.ghost2_image = tk.PhotoImage(file='images/ghost2.png')
        self.ghost3_image = tk.PhotoImage(file='images/ghost3.png')
        self.ghost4_image = tk.PhotoImage(file='images/ghost4.png')

        self.pacman1 = Pacman(self, self.maze, 1, 1, self.pacman1_image)
        self.pacman2 = Pacman(self, self.maze, self.maze.get_height() - 2, self.maze.get_width() - 2, self.pacman2_image)

        self.ghost1 = Ghost(self, self.maze, (self.maze.get_height() - 2)//2, (self.maze.get_width() - 2)//2, self.ghost1_image)
        self.ghost2 = Ghost(self, self.maze, (self.maze.get_height() - 2)//2, self.maze.get_width() - 10, self.ghost2_image)
        self.ghost3 = Ghost(self, self.maze, (self.maze.get_height() - 2)//2 + 1, (self.maze.get_width() - 2)//2, self.ghost3_image)
        self.ghost4 = Ghost(self, self.maze, (self.maze.get_height() - 2)//2 + 1, self.maze.get_width() - 10, self.ghost4_image)

        self.pacman1_score_text = Text(self, 'P1: 0', 100, 20)
        self.pacman2_score_text = Text(self, 'P2: 0', 600, 20)

        self.elements.append(self.pacman1)
        # self.elements.append(self.pacman2)

        self.elements.append(self.ghost1)
        self.elements.append(self.ghost2)
        self.elements.append(self.ghost3)
        self.elements.append(self.ghost4)

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
        if self.any_collision():
            messagebox.showinfo("Alert", "Game Over!")
            self.new_game()
            
        for ghost in self.elements:
            if not ghost.is_ghost:
                continue
            if not self.game_started:
                continue
            self.move_ghost(ghost, ghost.movable_ways())
        
        if True not in self.maze.has_active_dots.values():
            messagebox.showinfo("Alert", "Game Cleared!")
            self.new_game()

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
            self.game_started = True
            self.command_map[ch]()

    def move_ghost(self, ghost, ways):
        move = random.choice(ways)
        up_down_DIR = [DIR_UP, DIR_DOWN]
        left_right_DIR = [DIR_LEFT, DIR_RIGHT]
        if ghost.direction == DIR_DOWN and move == DIR_UP and ways == [DIR_DOWN, DIR_UP]:
            move = random.choice(ways+[DIR_DOWN]*20)
        elif ghost.direction == DIR_UP and move == DIR_DOWN and ways == [DIR_DOWN, DIR_UP]:
            move = random.choice(ways+[DIR_UP]*20)
        elif ghost.direction == DIR_LEFT and move == DIR_RIGHT and ways == [DIR_LEFT, DIR_RIGHT]:
            move = random.choice(ways+[DIR_LEFT]*20)
        elif ghost.direction == DIR_RIGHT and move == DIR_LEFT and ways == [DIR_LEFT, DIR_RIGHT]:
            move = random.choice(ways+[DIR_RIGHT]*20)
        if len(ways) == 3:
            up_down_DIR.extend(ways)
            left_right_DIR.extend(ways)
            if set(up_down_DIR) == 3:
                temp = list(up_down_DIR)
                temp.remove(DIR_UP)
                temp.remove(DIR_DOWN)
                last_dir = temp[0]
                move = random.choice(ways+[last_dir]*20)
            elif set(left_right_DIR) == 3:
                temp = list(left_right_DIR)
                temp.remove(DIR_LEFT)
                temp.remove(DIR_RIGHT)
                last_dir = temp[0]
                move = random.choice(ways+[last_dir]*10)
        ghost.set_next_direction(move)
    
    def any_collision(self):
        for player in self.elements:
            if player.is_ghost:
                continue
            for ghost in self.elements:
                if not ghost.is_ghost:
                    continue
                if player.x >= ghost.x-20 and player.x <= ghost.x+20 and player.y >= ghost.y-20 and player.y <= ghost.y+20:
                    return player
        return False
    
    def new_game(self):
        for i in self.elements:
            i.hide()
        for i in self.maze.dots:
            self.maze.dots[i].hide()
        self.maze.dots.clear()
        self.elements.clear()
        self.pacman1_score_text.hide()
        self.pacman2_score_text.hide()
        self.init_game()


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
