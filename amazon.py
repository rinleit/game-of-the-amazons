import copy
import re
import sys
import time
import os
import random
import numpy as np
import pickle
from math import log, sqrt

WHITE = 'w'
BLACK = 'b'
XXXXX = 'X'
TRAINTIME = 1.0

class Player:
    
    def __init__(self, str_name):
        self.str = str_name

    def __str__(self):
        return self.str

    def find(self, state):
        tuplesB = []
        tuplesW = []
        tuplesX = []
        for i in range(10):
            for j in range(10):
                if state[i][j] == BLACK:
                    tuplesB.append((i, j))
                if state[i][j] == WHITE:
                    tuplesW.append((i, j))
                if state[i][j] == XXXXX:
                    tuplesX.append((i, j))
        return tuplesB, tuplesW, tuplesX
    
    def nextMove(self, state):
        try:
            starttime = time.time()
            bqs, wqs, xqs = self.find(state)
            CopyBoard = Board(10, wqs, bqs, xqs, self.str)
            trainer = Boss(self.str, board=CopyBoard, starttime=starttime)
            result = self.play_bot(CopyBoard, trainer)
            del CopyBoard, trainer
            return result
        except:
            return None

        
    def play_bot(self, board, trainer):
        is_white = board.bWhite

        boardx = aiboard_Board(np.array(board.config))
        player = Boss.Player(is_white)

        
        boards, moves = boardx.moves(player)

        max_move = random.choice(moves)
        max_score = 0.0
        max_index = 0

        while True:
            for index, cboard in enumerate(boards):
                move = moves[index]
                
                if cboard in trainer.explored:
                    win_count, play_count = trainer.explored[cboard]
                    score = float(win_count) / float(play_count)

                    if score > max_score:
                        max_score = score
                        max_move = move
                        max_index = index

            src, dst, _ = max_move
            if not self.valid_path(src, dst, copy.deepcopy(board.config)):
                moves.remove(max_move)
                boards.remove(boards.index(max_index))
                continue
            break

        return max_move
    
    def valid_path(self, src, dst, config):
        (srcr, srcc) = src
        (dstr, dstc) = dst

        symbol = config[srcr][srcc]
        if self.str != symbol:
            return False

        h = dstr - srcr
        w = dstc - srcc
        if h and w and abs(h / w) != 1:
            return False
        if not h and not w:
            return False

        if not h:
            op = (0, int(w / abs(w)))
        elif not w:
            op = (int(h / abs(h)), 0)
        else:
            op = (int(h / abs(h)), int(w / abs(w)))

        (r, c) = (srcr, srcc)
        while (r, c) != (dstr, dstc):
            (r, c) = (r + op[0], c + op[1])
            if (config[r][c] != '.'):
                return False
        return True


class Board:
    def __init__(self, size, wqs, bqs, xqs, myqueen):
        self.bWhite = True if myqueen == WHITE else False
        self.time_limit = None
        self.config = [['.' for c in range(size)] for r in range(size)]
        for (r, c) in wqs:
            self.config[r][c] = WHITE
        for (r, c) in bqs:
            self.config[r][c] = BLACK
        for (r, c) in xqs:
            self.config[r][c] = XXXXX

    def move_queen(self, src, dst):
        self.config[dst[0]][dst[1]] = self.config[src[0]][src[1]]
        self.config[src[0]][src[1]] = '.'

    def shoot_arrow(self, dst):
        self.config[dst[0]][dst[1]] = XXXXX

class aiboard_Board:
    def __init__(self, board):
        self.board = np.array(board)
        self.player_symbols = {True: WHITE, False: BLACK}

    def moves(self, player):
        boards = []
        moves = []

        queen_moves = self.queen_moves(player.white)

        for queen_move in queen_moves:
            source, destination = queen_move
            moved_board = self.move_queen(self.board, source, destination)

            arrows = self.arrow_moves(moved_board, destination)

            for arrow in arrows:
                moves.append((source, destination, arrow))
                boards.append(self.shoot_arrow(moved_board.board, arrow))

        return boards, moves

    def get_spot(self, start_position, direction):
        height, width = self.board.shape
        r, c = start_position

        r -= direction.count('n')
        r += direction.count('s')
        c += direction.count('e')
        c -= direction.count('w')

        if 0 <= r < height and 0 <= c < width:
            return self.board[r, c], (r, c)
        else:
            return XXXXX, (r, c)

    def position_moves(self, spot):
        directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
        moves = []

        for direction in directions:
            location = spot
            dir = direction

            obstruction = False

            while not obstruction:
                piece, new_spot = self.get_spot(location, dir)

                if piece == '.':
                    moves.append((spot, new_spot))
                    dir += direction
                else:
                    obstruction = True

        return moves

    def queen_moves(self, is_white):
        moves = []
        height, width = self.board.shape

        for r in range(height):
            for c in range(width):

                if self.board[r, c] == self.player_symbols[is_white]:
                    moves += self.position_moves((r, c))

        return moves

    def arrow_moves(self, board, queen_end):
        return [move[1] for move in board.position_moves(queen_end)]

    @staticmethod
    def move_queen(board, src, dst):
        copy = np.copy(board)
        copy[dst] = copy[src]
        copy[src] = '.'
        return aiboard_Board(copy)

    @staticmethod
    def shoot_arrow(board, dst):
        copy = np.copy(board)
        copy[dst] = XXXXX
        return aiboard_Board(copy)

    def __hash__(self):
        return hash(str(self.board))


class Boss:
    class Player:
        def __init__(self, white):
            self.path = []
            self.white = white
            self.other_player = None
            

        def update(self, state):
            self.path.append(state)

        def clear(self):
            self.path = []

        def other(self):
            return self.other_player

    def __init__(self, iswhite=WHITE, board=None, starttime=0):

        self.start = aiboard_Board(board.config)
        self.starttime = starttime
        self.white_player = Boss.Player(True if iswhite==WHITE else False)
        self.black_player = Boss.Player(True if not iswhite==WHITE else False)
        self.white_player.other_player = self.black_player
        self.black_player.other_player = self.white_player

        self.explored = dict()
        self.train()

    def train(self):
        times = 0
        while time.time() - self.starttime < TRAINTIME:
            self.simulate()
            times += 1
        # print("Times %d" % times)
                
    def select(self, current_state, player):

        max_state = None
        max_score = 0

        child_boards, _ = current_state.moves(player)

        for child in child_boards:
            if child not in self.explored:
                player.update(current_state)
                return current_state, player

            wins, plays = self.explored[child]
            if max_score == None or wins / plays > max_score:
                max_score = (wins / plays) + (1.4 * sqrt(log(plays) / plays))
                max_state = child

        player.update(max_state)

        return self.select(max_state, player.other())

    def expand(self, current_state, player):
        shuffled, _ = current_state.moves(player)
        random.shuffle(shuffled)
        for child in shuffled:
            if child not in self.explored:
                player.update(child)
                return child, player.other()

    def simulate(self):
        selected, player = self.select(self.start, self.white_player)
        expand, player = self.expand(selected, player)

        current = expand
        game_end = False

        loser = None
        winner = None

        while not game_end:
            boards, _ = current.moves(player)

            if not boards:
                loser = player
                winner = player.other()
                break

            current = random.choice(boards)
            player.update(current)

            player = player.other()

        for state in loser.path:
            if state in self.explored:
                wins, plays = self.explored[state]
            else:
                wins = plays = 0

            plays += 1

            self.explored[state] = (wins, plays)

        for state in winner.path:
            if state in self.explored:
                wins, plays = self.explored[state]
            else:
                wins = plays = 0

            wins += 1
            plays += 1
            self.explored[state] = (wins, plays)