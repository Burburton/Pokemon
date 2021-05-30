import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog, dialog
import traceback
import random
import json

import os

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
DIRECTIONS = (UP, DOWN, LEFT, RIGHT,
              f"{UP}-{LEFT}", f"{UP}-{RIGHT}",
              f"{DOWN}-{LEFT}", f"{DOWN}-{RIGHT}")
WALL_VERTICAL = "|"
WALL_HORIZONTAL = "-"
POKEMON = "☺"
FLAG = "♥"
UNEXPOSED = "~"
EXPOSED = "0"
INVALID = "That ain't a valid action buddy."
HELP_TEXT = """h - Help.
<Uppercase Letter><number> - Selecting a cell (e.g. 'A1')
f <Uppercase Letter><number> - Placing flag at cell (e.g. 'f A1')
:) - Restart game.
q - Quit.
"""

TASK_ONE = 1
TASK_TWO = 2

IMAGE_MATCH = ['zero_adjacent', 'one_adjacent', 'two_adjacent', 'three_adjacent',
             'four_adjacent', 'five_adjacent', 'six_adjacent', 'seven_adjacent',
             'eight_adjacent']

IMAGE_POKEMON = ['charizard', 'cyndaquil', 'pikachu', 'psyduck', 'togepi', 'umbreon']


class BoardModel(object):
    '''
    To stimulate the internal process of the pokemon game
    '''

    def __init__(self, grid_size, num_pokemon):
        '''
        To construct a BoardModel class to complete the internal process of the pokemon game

        :param grid_size: the size of the game. it is related to the number of tile
        :param num_pokemon: refer to the number of pokemon hidden in the game board

        Attribution:
            displayBoard: the board would be showed in the window. it is a two-dimensional list
            num_pokemon: record the number of pokemon hidden in the board
            left_pokemon: record the number of rest pokemon hidden in the board
            state: determine if the game stop
            loss: determine if the player loss in the game
            isWorking:  determine if the game board can be changed
            grid_size: the size the game board
            pokemon: a list of pokemon's positions
            hidden_pokemon: a list of pokemon that still hide
        '''
        self.displayBoard = [[UNEXPOSED for col in range(grid_size)] for row in range(grid_size)]
        self.num_pokemon = self.left_pokemon = num_pokemon
        self.state = True
        self.loss = False
        self.isWorking = True
        self.grid_size = grid_size
        self.pokemon = self.generate_pokemon(grid_size, num_pokemon)
        self.hidden_pokemon = self.pokemon.copy()

    def get_board(self):
        '''
        :return: the attribution: displayBoard
        '''
        return self.displayBoard

    def get_left_pokemon(self):
        '''
        :return: the attribution: left_pokemon
        '''
        return self.left_pokemon

    def get_num_pokemon(self):
        '''
        :return: the attribution: num_pokemon
        '''
        return self.num_pokemon

    def get_game(self):
        '''
        :return: the attribution: state
        '''
        return self.state

    def get_pokemon_location(self):
        '''
        :return: the attribution: pokemon
        '''
        return self.pokemon

    def get_num_attempted_catches(self):
        '''

        :return: the number of catches were used on the board
        '''
        return self.num_pokemon - self.left_pokemon

    def get_item(self, position: tuple):
        '''
        :param position: a tuple that like (x, y)
        :return: the content of the position on the board
        '''
        return self.displayBoard[position[0]][position[1]]

    def generate_pokemon(self, grid_size, num_pokemon):
        '''
        The method is used to randomly generate the list of pokemon hidden in the game board
        the list records the index

        :param grid_size: the size of the board
        :param num_pokemon:  the number of pokemon generate on the board
        :return: randomly generate a list that records the index of every pokemon
        '''
        assert num_pokemon <= grid_size ** 2
        pokemon = random.sample(range(0, grid_size ** 2), num_pokemon)
        return pokemon

    def set_state(self, Boolean):
        '''
        Set the state of the game

        :param Boolean: True or False
        '''
        self.state = Boolean

    def triggle_isworking(self, Bool):
        '''
        Set the attribution isWorking of the game

        :param Bool: True or False
        '''
        self.isWorking = Bool

    def is_on_board(self, position):
        '''
        To ensure the input position is within the board

        :param position: a tuple like (x, y)
        :return: if the positon is within the board return True else return False
        '''

        x, y = position
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return True
        else:
            return False

    def reset_game(self):
        '''
        To re-generate a new game. It will generate the important parameter of BoardModel
        '''
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.displayBoard[i][j] = '~'
        self.state = True
        self.left_pokemon = self.num_pokemon
        self.loss = False
        self.triggle_isworking(True)
        self.hidden_pokemon = self.pokemon.copy()

    def calculate_count(self, position: tuple):
        '''
        calculate how many pokemon surrounding the item in the position
        :param position: a tuple like (x, y)
        :return: the number of pokemon surrounding the position
        '''

        count = 0
        index = self.position_to_index(position)
        x, y = position

        assert index not in self.pokemon

        def is_poke(position):
            if self.is_on_board(position):
                if self.position_to_index(position) in self.pokemon:
                    return True
            return False

        if is_poke((x-1, y-1)):
            count += 1
        if is_poke((x, y -1)):
            count += 1
        if is_poke((x+1, y-1)):
            count += 1
        if is_poke((x + 1, y)):
            count += 1
        if is_poke((x-1, y)):
            count += 1
        if is_poke((x, y+1)):
            count += 1
        if is_poke((x-1, y+1)):
            count += 1
        if is_poke((x+1, y+1)):
            count += 1
        return count

    def left_click(self, position: tuple):
        '''
        To complete the operation in the game. left click would expose the number of pokemon surrounding the position
        However, if a pokemon hide in the position, player would lose the game

        :param position: a tuple like (x, y)
        '''

        assert self.is_on_board(position)
        if self.isWorking:
            if self.position_to_index(position) not in self.pokemon:
                if self.get_item(position) == '~':
                    statistic = self.calculate_count(position)
                    self.set_item(position, str(statistic))
                    if statistic == 0:
                        self.extend_zero(position, position)
            else:
                self.loss = True
                self.show_all_pokemon()

    def right_click(self, position: tuple):
        '''
        To complete the operation in the game. right click would use a catch to cover the grass. if player cover
        all the pokemon accurately, they would win the game
        :param position: a tuple like (x, y)
        '''
        assert position[0] < self.grid_size
        assert position[1] < self.grid_size
        if self.isWorking:
            index = self.position_to_index(position)
            if self.get_item(position) == '~':
                self.set_item(position, FLAG)
                self.left_pokemon -= 1

                if index in self.pokemon:
                    self.hidden_pokemon.remove(index)
                self.check_win()
            elif self.get_item(position) == FLAG:
                self.set_item(position, '~')
                self.left_pokemon += 1
                if index in self.pokemon:
                    self.hidden_pokemon.append(index)

    def extend_zero(self, current_position, pre_position):
        '''
        if players left click a tile which is zero, the method would extend other zero tiles connecting to that zero
        title until not zero title

        :param current_position: the current zero tile position
        :param pre_position: the last zero tile position
        :return:
        '''

        x, y = current_position
        if not self.is_on_board(current_position):
            return
        if self.calculate_count(current_position) != 0:
            self.left_click(current_position)
            return
        else:
            self.set_item(current_position, EXPOSED)
            UP, DOWN, LEFT, RIGHT = (x-1, y), (x + 1, y), (x, y-1), (x, y+1)
            if self.is_on_board(UP) and self.get_item(UP) == '~':
                self.extend_zero(UP, current_position)
            if self.is_on_board(DOWN) and self.get_item(DOWN) == '~':
                self.extend_zero(DOWN, current_position)
            if self.is_on_board(LEFT) and self.get_item(LEFT) == '~':
                self.extend_zero(LEFT, current_position)
            if self.is_on_board(RIGHT) and self.get_item(RIGHT) == '~':
                self.extend_zero(RIGHT, current_position)

    def position_to_index(self, position):
        '''
        covert two-dimensional list to one-dimensional list

        :param position: a tuple like (x, y)
        :return: the corresponding index in one-dimensional list
        '''
        x, y = position
        index = x * self.grid_size + y
        return index

    def index_to_position(self, index):
        '''
        covert one-dimensional list to two-dimensional list
        :param index: a number in one-dimensional list
        :return: the corresponding position in two-dimensional list
        '''
        x = index // self.grid_size
        y = index % self.grid_size
        return (x, y)

    def set_item(self, position: tuple, symbol):
        '''
        to change the symbol on the corresponding position
        :param position: a tuple like (x, y)
        :param symbol: a global variable
        '''
        x, y = position
        self.displayBoard[x][y] = symbol

    # the method is only used when game over
    def show_all_pokemon(self):
        '''
        when game over, the method would show all the position of pokemon
        '''
        for i in self.pokemon:
            self.set_item(self.index_to_position(i), POKEMON)

    def check_win(self):
        '''
        to check if the players win the game
        :return: if it is win would return True, if not, it return False
        '''
        if len(self.hidden_pokemon) == 0 and self.left_pokemon == 0 and self.state:
            self.show_all_pokemon()
            self.isWorking = False
            return True
        else:
            return False

    def check_lose(self):
        '''
        to check if the players lose the game
        :return: if it is loss would return True, if not, it return False
        '''
        if self.loss and self.state:
            self.isWorking = False
            return True
        else:
            return False

    def __str__(self):
        matrix = ''
        for i in self.displayBoard:
            matrix += str(i)
            matrix += '\n'
        return matrix


'''
    The part would complete graphical board of Pokemon Game 
'''


class StatusBar(tk.Frame):
    '''
    The class regards as a frame to show the information of the game in the game window
    the information includes time, number of left pokemon and catches used

    Attribution:
        master: the super component of the class
        time: refer to the timer begin with
        game: a BoardModel class that is running
        state: determine if the StatusBar would continually update
        frames: a collection of all the frames used in the class

    '''

    def __init__(self, master, game: BoardModel, time=0, *args, **kwargs):
        '''
        To construct the StatusBar class

        :param master: the super component
        :param game: the running game
        :param time: the time would begin with
        :param args: other parameters
        :param kwargs: other parameters
        '''

        super().__init__(master, *args, **kwargs)
        self.master = master
        self.time = time
        self.game = game
        self.state = True
        self.frames = []
        self.draw_pokemon_info()
        self.draw_timer()

    def get_state(self):
        '''

        :return: the attribution state
        '''
        return self.state

    def get_time(self):
        '''

        :return: the attribution time
        '''
        return self.time

    def set_state(self, Bool):
        '''
        set the value of state
        :param Bool: True or False
        '''
        self.state = Bool

    def set_time(self, time):
        '''
        set the value of time
        :param time: a positive number
        '''
        self.time = time

    def draw_pokemon_info(self):
        '''
        the method would draw the frame to show the information about pokemon and catches
        :return:
        '''
        image = get_image("images/full_pokeball")

        frame = tk.Frame(self.master)
        frame.pack(side=tk.LEFT)

        pokemon = tk.Label(frame, image=image, anchor=tk.CENTER)
        pokemon.image = image
        pokemon.pack(side=tk.LEFT)

        text_pokemon_left = tk.Label(frame, text=f'Left Pokemon: {self.game.get_left_pokemon()}', anchor='w',
                                     justify='left', wraplength = 200)
        text_catches = tk.Label(frame, text=f'Attempted Catches: {self.game.get_num_attempted_catches()}', anchor='w',
                                justify='left', wraplength = 200)

        text_pokemon_left.pack(side=tk.TOP)
        text_catches.pack(side=tk.BOTTOM)

        self.update_data(text_pokemon_left, text_catches)

        self.frames.append(frame)

    def draw_timer(self):
        '''
        the method  would draw the frame to show the information about timer
        '''
        timerFrame = tk.Frame(self.master)
        timerFrame.pack(side=tk.LEFT)

        image = get_image("images/clock")
        timer = tk.Label(timerFrame, image=image)
        timer.image = image

        timer.pack(side=tk.LEFT)

        text = tk.Label(timerFrame, text='Time elapsed: ')
        text.pack(side=tk.TOP)

        recording = tk.Frame(timerFrame)
        recording.pack(side=tk.BOTTOM)

        numberM = tk.Label(recording, text=self.time//60)
        numberM.pack(side=LEFT)

        minute = tk.Label(recording, text='m ')
        minute.pack(side=LEFT)

        numberS = tk.Label(recording, text=self.time%60)
        numberS.pack(side=tk.LEFT)

        second = tk.Label(recording, text='s ')
        second.pack(side=RIGHT)

        self.frames.append(timerFrame)

        self.timepiece(numberM, numberS, self.time)

    def update_data(self, left_pokemon, attempted_catches):
        '''
        the method to update data about pokemon and catches in real time
        :param left_pokemon: the pokemon component
        :param attempted_catches: the catches component
        :return:
        '''
        left_pokemon.config(text=f'Left Pokemon: {self.game.get_left_pokemon()}')
        attempted_catches.config(text=f'Attempted Catches: {self.game.get_num_attempted_catches()}')
        self.master.after(100, self.update_data, left_pokemon, attempted_catches)

    def timepiece(self, minute, second, time):
        '''
        the mothed was designed to reckon by time
        :param minute: the number of minute
        :param second: the number of second
        :param time: the time in second
        '''
        try:
            if self.state:
                if time < 60:
                    second['text'] = time
                else:
                    minute['text'] = time // 60
                    second['text'] = time % 60
                    # time = 0
                self.master.after(1000, self.timepiece, minute, second, time + 1)
                # self.time = minute['text'] * 60 + time
                self.time = time
            else:
                self.state = False
                # self.redraw()
        except Exception as e:
            traceback.print_exc(e)

    def redraw(self):
        '''
        destroy all the component on the StatusBar to redraw the StatusBar
        '''
        for i in self.frames:
            i.destroy()


class BoardView(tk.Canvas):
    '''
    A class to display the game board on the window

    Attribution:
        game_board: store the currently running game
        board_width: the size of the game board
    '''
    def __init__(self, master, game_board: BoardModel, board_width=600, *args, **kwargs):
        '''
        to construct the class BoardView

        :param master: the super component
        :param game_board: the running game
        :param board_width: the size of the board
        :param args: other parameters
        :param kwargs: other parameters
        '''
        super().__init__(master, width=board_width, *args, **kwargs)
        self.game_board = game_board
        self.board_width = board_width
        self.board = self.load_board()
        self.redraw()

    def get_board(self):
        '''

        :return: the display board of running game
        '''
        return self.game_board.get_board()

    def load_board(self):
        '''
        distribute the game board based on the internal running game
        :return: the 2-dimensional board showing the tile distribution
        '''

        labels = []
        board = self.get_board()

        for y, row in enumerate(board):
            board_row = []
            for x, tile in enumerate(row):
                placement = tk.Label(self.master, text='  ', bg='green')
                placement.grid(column=x, row=y, ipadx=20, ipady=20, padx=0, pady=0)
                self.bind_clicks(placement, (y, x))
                board_row.append(placement)
            labels.append(board_row)

        return labels

    def do_bind(self):
        '''
        to bind the operation of mouse
        '''
        self.bind("<Button-1>", self.do_left)
        self.bind("<Button-2>", self.do_right)
        self.bind("<Button-3>", self.do_right)

    def do_left(self):
        '''
        if it is left click
        :return: True
        '''
        return True

    def do_right(self):
        '''
        if it is right click
        :return: True
        '''
        return True

    def redraw(self):
        '''
        update the display board in the window
        '''
        board = self.get_board()
        for y, row in enumerate(board):
            for x, tile in enumerate(row):
                position = (y, x)
                text, background = self._text_and_background(tile)
                placement = self.board[y][x]
                placement.config(text=text, bg=background, borderwidth=0.5, relief="solid")
                self.detect_mouse(placement, position)
                self.bind_clicks(placement, position)

    def bind_clicks(self, label, position):
        '''
        base on the events to operate
        :param label: the current component that waiting for changing
        :param position: the position of the component. it is (x, y).
        '''
        self.do_bind()

        label.bind("<Button-1>", lambda e, position=position: self._handle_left_click(position))
        label.bind("<Button-2>", lambda e, position=position: self._handle_right_click(position))
        label.bind("<Button-3>", lambda e, position=position: self._handle_right_click(position))

    def detect_mouse(self, label, position):
        '''
        to chase the movement of the mouse and bound the corresponding tile
        to complete the interaction between game and players
        it is the postgraduate parts
        :param label: the component waiting for changing
        :param position: the position of the component. it is (x, y)
        '''
        label.bind("<Enter>", lambda e, position=position: self._handle_move(position))
        label.bind("<Leave>", lambda e, position=position: self._handle_leave(position))

    def _handle_move(self, position):
        '''
        when mouse move on a position of component, it would do some change
        :param position: the position of the component
        '''
        x, y = position
        if self.game_board.get_board()[x][y] == '~':
            placement = self.board[x][y]
            placement.config(borderwidth=1, relief="raise")

    def _handle_leave(self, position):
        '''
        when the mouse leave the component. it would do some change that is losing the highlight
        :param position: the position of the component
        '''
        x, y = position
        if self.game_board.get_board()[x][y] == '~':
            placement = self.board[x][y]
            placement.config(borderwidth=0.5, relief="solid")

    def _handle_left_click(self, position):
        '''
        when detect left click from mouse, it would update the game board
        :param position: a tuple like (x, y)
        '''
        self.game_board.left_click(position)
        if self.game_board.isWorking:
            self.redraw()

    def _handle_right_click(self, position):
        '''
        when detect right click from mouse. it would update the game board
        :param position: a tuple like (x, y)
        '''
        self.game_board.right_click(position)
        self.redraw()

    def _text_and_background(self, tile):
        '''
        different tiles refer to different graphic pattern
        :param tile: a type of tile
        :return: the display text and backgroud color
        '''
        try:
            if tile == '~':
                text = '  '
                background = 'ForestGreen'
            elif tile == FLAG:
                text = '  '
                background = 'Red'
            elif tile == POKEMON:
                text = '  '
                background = 'DarkBlue'
            else:
                text = tile
                background = 'SpringGreen'
        except AttributeError:
            text = ''
            background = 'ForestGreen'

        return text, background


class ImageBoardView(BoardView):
    '''
    a class to display the image tiles
    Attribution:
        game_board: the running internal game
        board: the distribution of the diplayed board
        state: to determine if the tile interact with players
        frequency: the frequency of wave of grass
    '''
    def __init__(self, master, game_board: BoardModel, *args, **kwargs):
        '''
         to construct the class ImageBoardView
        :param master: the super component
        :param game_board: the running internal game
        :param args: other parameters
        :param kwargs: other parameters
        '''
        super().__init__(master, game_board, *args, **kwargs)
        self.game_board = game_board
        self.board = self.load_board()
        self.frequecy = 5
        self.redraw()
        self.state = [[True for i in range(self.game_board.grid_size)] for j in range(self.game_board.grid_size)]

    def redraw(self):
        '''
        to update the displayed board. to cover the tiles by image
        '''
        board = self.get_board()
        for y, row in enumerate(board):
            for x, tile in enumerate(row):
                position = (y, x)
                image = self._load_tile_image(tile)
                placement = self.board[y][x]
                placement.config(image=image)
                placement.image = image
                self.detect_mouse(placement, position)
                self.bind_clicks(placement, position)

    def detect_mouse(self, label, position):
        '''
        to chase the movement of mouse and modify the tiles
        :param label: the component
        :param position: the position of the component
        '''
        label.bind("<Enter>", lambda e, position=position: self._handle_move(position))
        label.bind("<Leave>", lambda e, position=position: self._handle_leave(position))

    def _handle_left_click(self, position):
        '''
        to update the tiles while mouse left click a tile
        :param position: the position of the tile
        '''
        self.game_board.left_click(position)
        self.state[position[0]][position[1]] = False
        if self.game_board.isWorking:
            self.redraw()

    def _handle_right_click(self, position):
        '''
        to update the tiles while mouse right click a tile
        :param position: the position of the tile
        '''
        self.game_board.right_click(position)
        self.state[position[0]][position[1]] = False
        self.master.after(self.frequecy, self.set_state, position, True)
        self.redraw()

    def _trigger_image(self, position, placement, count):
        '''
        trigger the image to complete the wave of grass
        :param position: the position of the compoonent
        :param placement: a component
        :param count: determine which image would be showed
        '''
        x, y = position
        tempTime = 200/self.frequecy
        if count > tempTime and self.state[x][y]:
            image = get_image(f"images/unrevealed")
            placement.config(image=image)
            placement.image = image
            self.master.after(self.frequecy, self._trigger_image, position, placement, (count+1) % (2 * tempTime))
        elif count <= tempTime and self.state[x][y]:
            image = get_image(f"images/unrevealed_moved")
            placement.config(image=image)
            placement.image = image
            self.master.after(self.frequecy, self._trigger_image, position, placement, (count+1) % (2 * tempTime))

    def _handle_move(self, position):
        '''
        to chase the mouse on the position of tile and update the interaction
        :param position: a tuple like (x, y)
        '''
        x, y = position
        if self.game_board.get_board()[x][y] == '~':
            placement = self.board[x][y]
            image = get_image(f"images/unrevealed_moved")
            placement.config(image=image)
            placement.image = image
            self.master.after(self.frequecy, self._trigger_image, position, placement, 1)

    def set_state(self, position, bool):
        '''
        to set the state of position
        :param position: a tuple like (x, y)
        :param bool: True or False
        '''
        x, y = position
        self.state[x][y] = bool

    def _handle_leave(self, position):
        '''
        to chase the mouse leave the positon and update the tile
        :param position: a tuple like (x, y)
        '''

        x, y = position
        self.state[x][y] = False
        if self.game_board.get_board()[x][y] == '~':
            placement = self.board[x][y]
            image = get_image(f"images/unrevealed")
            placement.config(image=image)
            placement.image = image
        self.master.after(self.frequecy*3, self.set_state, position, True)

    def load_board(self):
        '''
        distribute the display board based on the internal game board
        :return: the distribution of game board
        '''
        labels = []
        board = self.get_board()
        for y, row in enumerate(board):
            board_row = []
            for x, tile in enumerate(row):
                placement = tk.Label(self.master)
                placement.grid(column=x, row=y)
                self.bind_clicks(placement, (y, x))
                board_row.append(placement)
            labels.append(board_row)
        return labels

    def _load_tile_image(self, tile):
        '''
        cover images on the corresponding tile based on the game board
        :return: the corrsponding images
        '''
        try:
            if tile == '~':
                image = get_image(f"images/unrevealed")
            elif tile == FLAG:
                image = get_image(f"images/pokeball")
            elif tile == POKEMON:
                image = get_image(f"images/pokemon_sprites/{IMAGE_POKEMON[random.randint(0, len(IMAGE_POKEMON))-1]}")
            else:
                image = get_image(f"images/{IMAGE_MATCH[int(tile)]}")

        except AttributeError:
            print('something wrong')
            image = get_image("images/unrevealed")
        return image


'''
    This part would control the game
'''


class PokemonGame:
    '''
    a class to connect BoradModel and BoardView
    Attribution:
        master: super component
        level: the game level
        task: the different mode to display the game board
        panel_frame: a frame to show the information of the game
        board_frame: a frame to show the display board
        menu_frame: a frame to show the menu
        panel: the panel build on the panel_frame
        board: the board build on the board_frame
        game: the running game
        boardView: the board build on the board_frame
        button_frame: a frame to put buttons
    '''
    def __init__(self, master, grid_size=11, num_pokemon=20, task=TASK_TWO):
        '''
        to construct the PokemonGmae class
        :param master: the super component
        :param grid_size: the size of the game board
        :param num_pokemon: the number of pokemon
        :param task: the mode of display
        '''
        self.master = master
        self.level = 1
        self.task = task
        self.panel_frame, self.board_frame, self.menu_frame, self.title_frame=None, None, None, None
        self.panel, self.board, self.game = None, None, None
        self.boardView = None
        self.button_frame = None
        self.generate_menu()
        self.initial_game(grid_size, num_pokemon)
        self.draw()
        self.check_result()

    def draw(self, time=0):
        '''
        to draw the window of game
        :param time: the beginning time
        '''
        self.title_frame = tk.Frame(self.master)
        self.title_frame.pack(side=tk.TOP)
        title_label = tk.Label(self.title_frame, text='Pokemon: Gotta Find Them All!.', font='Roman -20 bold', bg='red',
                               fg='white', width=100)
        title_label.pack(side=tk.TOP)

        try:
            self.board_frame = tk.Frame(self.master)
            if self.task == TASK_ONE:
                self.board = BoardView(self.board_frame, self.game)
            elif self.task == TASK_TWO:
                self.board = ImageBoardView(self.board_frame, self.game)
            self.board_frame.pack(side=tk.TOP)
        except Exception as e:
            traceback.print_exc(e)
        try:
            self.panel_frame = tk.Frame(self.master)
            self.panel = StatusBar(self.panel_frame, self.game, time)
            self.panel_frame.pack(side=tk.TOP)
            self.panel.pack(side=tk.LEFT)
        except Exception as e:
            traceback.print_exc(e)

        self.button_frame = tk.Frame(self.panel_frame)

        restart_button = tk.Button(self.button_frame, text="Restart Game", command=self.reset_game)
        restart_button.pack(side=tk.BOTTOM)

        newgame_button = tk.Button(self.button_frame, text="New Game", command=self.new_game)
        newgame_button.pack(side=tk.BOTTOM)

        self.button_frame.pack(side=tk.RIGHT)

    def initial_game(self, grid_size=11, num_pokemon=20):
        '''
        to generate the game
        :param grid_size: the size of board
        :param num_pokemon: the number of pokemon
        :return:
        '''
        self.game = BoardModel(grid_size, num_pokemon)

    def check_result(self):
        '''
        to check the game is win or loss
        '''
        if self.game.check_win():
            self.game.set_state(False)
            self.panel.set_state(False)
            messagebox.showinfo('Game Over', f'You Win! You spent {self.panel.get_time()//60}m {self.panel.get_time()%60}s')
            self.record_score()
            self.reading_ranking()
            self.new_game()
        if self.game.check_lose():
            self.game.set_state(False)
            self.panel.set_state(False)
            is_restart_game = messagebox.askokcancel('Game Over', 'You Lost. Would you like to play again?')
            if is_restart_game:
                self.reset_game()
            else:
                self._exit_game()
        self.master.after(100, self.check_result)

    def generate_menu(self):
        '''
        to draw the menu list
        '''
        self.menu_frame = tk.Menu(self.master)

        file_menu = tk.Menu(self.menu_frame, tearoff=0)
        file_menu.add_command(label="Save Game", command=self._save_file)
        file_menu.add_command(label='Load Game', command=self._load_file)
        file_menu.add_command(label="Restart Game", command=self.reset_game)
        file_menu.add_command(label="New Game", command=self.new_game)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._exit_game)

        self.menu_frame.add_cascade(label='Game', menu=file_menu)

        exit_menu = tk.Menu(self.menu_frame, tearoff=0)
        exit_menu.add_command(label='Mode ONE', command=self._task_one)
        exit_menu.add_command(label='Mode TWO', command=self._task_two)
        exit_menu.add_command(label='Help', command=self._help)
        exit_menu.add_command(label='High Scores', command=self.reading_ranking)
        exit_menu.add_separator()
        exit_menu.add_command(label='About', command=self._about)

        self.menu_frame.add_cascade(label='Edit', menu=exit_menu)
        self.master.config(menu=self.menu_frame)

    def reading_ranking(self):
        '''
        to get the ranking list from static file and show on the front
        '''
        ranking_file = os.getcwd()+'\\record.txt'
        if os.path.exists(ranking_file):
            with open(ranking_file, 'r') as file:
                content = json.load(file)
            file.close()
            message_text = ''
            count = 1
            for key, value in content.items():
                value = int(value)
                message_text = f'{message_text} No.{count} {key}: {value//60}m {value%60}s\n'
                count += 1
                if count == 4:
                    break
        else:
            messagebox.showinfo('High Scores', 'There have been no score in the game!')
        messagebox.showinfo('High Scores', message_text)

    def record_score(self):
        '''
        to record the score of players into a static file
        '''
        record_file = os.getcwd()+'\\record.txt'

        content = {}
        ranking = 1
        try:
            if os.path.exists(record_file):
                with open(record_file, 'r') as file:
                    content = json.load(file)
                file.close()

                score_list = list(content.values())
                while self.panel.get_time() > score_list[ranking-1]:
                    ranking += 1
                    if ranking == len(score_list) + 1:
                        break
                score_name = simpledialog.askstring("Input",
                                                    f"You won in {self.panel.get_time() // 60}m "
                                                    f"{self.panel.get_time() % 60}s and No.{ranking}. Enter Your Name:",
                                                    parent=self.master)
                while score_name is None or score_name == '' or score_name in content.keys():
                    score_name = simpledialog.askstring("Input",
                                                        f"Error. The Name is Repeated or None. Input Your Name Again:",
                                                        parent=self.master)
                content[score_name] = self.panel.get_time()
                content = dict(sorted(content.items(), key=lambda item: item[1]))
            else:
                score_name = simpledialog.askstring("Input",
                                                    f"You won in {self.panel.get_time() // 60}m "
                                                    f"{self.panel.get_time() % 60}s and 1st. Enter Your Name:",
                                                    parent=self.master)
                content[score_name] = self.panel.get_time()

            jsonOBJ = json.dumps(content)
            with open(record_file, 'w') as file:
                file.write(jsonOBJ)
            file.close()

        except:
            messagebox.showinfo('Record Score', 'Record failed. It will go to new default game')
            self.new_game()

    def _task_one(self):
        '''
        to change to mode 1
        '''
        self.task = TASK_ONE
        self.redraw(self.panel.get_time())

    def _task_two(self):
        '''
        to change to mode 2
        '''
        self.task = TASK_TWO
        self.redraw(self.panel.get_time())

    def _exit_game(self):
        '''
        to quit the game
        '''
        self.master.quit()

    def _help(self):
        '''
        show some information
        '''
        messagebox.showinfo('Help', 'Pokemon Game Requires Finding All Pokemon')

    def _about(self):
        '''
        show some information
        '''
        messagebox.showinfo('About', 'It was made by myself')

    def _save_file(self):
        '''
        the save the current game that could be restore in the future
        '''
        if self.game.check_win() or self.game.check_lose():
            messagebox.showinfo('Error', 'The Game Was End, You Cannot Save It!')
            return
        file_text = {
            'game': {
                'grid_size': str(self.game.grid_size),
                'pokemon_list': str(self.game.pokemon),
                'hidden_pokemon': str(self.game.hidden_pokemon),
                'board': str(self.game.get_board()),
                'left_pokemon': str(self.game.get_left_pokemon()),
            },
            'panel': {
                'time': str(self.panel.get_time()),
            }
        }
        jsOBJ = json.dumps(file_text)

        file_path = filedialog.asksaveasfilename(title=u'Save File', defaultextension='.txt',
                                                 initialfile='untitled_game',
                                                 filetypes=[('text file', '.txt'), ('all file', '.*')])

        if file_text is not None:
            try:
                with open(file=file_path, mode='w', encoding='utf-8') as file:
                    file.write(jsOBJ)
                file.close()
                messagebox.showinfo('Save Game', 'Done')
            except:
                pass

    def _load_file(self):
        '''
        to restore the saved game based on the saved file
        '''
        try:
            file_path = filedialog.askopenfilename(title=u'Load File',
                                                   filetypes=[('text file', '.txt'), ('all file', '.*')])
            with open(file_path, 'r') as load_file:
                content = json.load(load_file)
            game = content['game']
            grid_size = game['grid_size']
            pokemon_list = game['pokemon_list']
            hidden_pokemon = game['hidden_pokemon']
            board = game['board']
            left_pokemon = game['left_pokemon']
            time = content['panel']['time']

            grid_size = int(grid_size)
            pokemon_list = eval(pokemon_list)
            hidden_pokemon = eval(hidden_pokemon)
            board = eval(board)
            left_pokemon = int(left_pokemon)
            time = int(time)

            self.game = BoardModel(grid_size, len(pokemon_list))
            self.game.pokemon = pokemon_list
            self.game.hidden_pokemon = hidden_pokemon
            self.game.displayBoard = board
            self.game.left_pokemon = left_pokemon
            self.redraw(time)
        except:
            messagebox.showinfo('Load Game', 'Sorry, load Failed. There are some unknown errors')

    def reset_game(self):
        '''
        restart the game without changing the board and pokemon list
        '''
        self.game.reset_game()
        self.redraw()

    def new_game(self):
        '''
        generate a new game. change the board and pokemon list
        '''
        self.level = simpledialog.askstring("Input", "What level would you like to play (range from 1 to 10)",
                                            parent=self.master)
        if self.level in [str(i) for i in list(range(1, 11))]:
            self.level = int(self.level)
        else:
            messagebox.showinfo("New Game", "Sorry, it will go to the default level 9 because of wrong input!")
            self.level = 9
        self.game = BoardModel(1+self.level, 2*self.level)
        self.game.reset_game()
        self.redraw()

    def redraw(self, time=0):
        '''
        redraw the window
        :param time: beginning time
        '''
        self.panel_frame.destroy()
        self.button_frame.destroy()
        self.board_frame.destroy()
        self.title_frame.destroy()
        self.draw(time)


def get_image(image_name):
    """(tk.PhotoImage) Get a image file based on capability.

    If a .png doesn't work, default to the .gif image.
    """
    try:
        image = tk.PhotoImage(file=image_name + ".png")
    except tk.TclError:
        image = tk.PhotoImage(file=image_name + ".gif")
    return image


def main():
    '''
    To run the whole game
    '''
    root = tk.Tk()
    root.title('Pokemon: Got 2 Find Them All!')

    PokemonGame(root)

    root.update()
    root.mainloop()


if __name__ == '__main__':
    main()