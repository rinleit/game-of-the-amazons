#!/usr/bin/python
# -*- coding: utf-8 -*-
# ======================== Class Player =======================================
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


class Player:
    # student do not allow to change two first functions
    def __init__(self, str_name):
        self.str = str_name
        self.ejw45_mc = ejw45_MonteCarlo(10, self.str)

    def __str__(self):
        return self.str

    # Student MUST implement this function
    # The return value should be a move that is denoted by a list of tuples:
    # [(row1, col1), (row2, col2), (row3, col3)] with:
        # (row1, col1): current position of selected amazon
        # (row2, col2): new position of selected amazon
        # (row3, col3): position of the square is shot

    def findW(self, state):
        tuples = []
        for i in range(10):
            for j in range(10):
                if state[i][j] == WHITE:
                    tuples.append((i, j))
        return tuples

    def findB(self, state):
        tuples = []
        for i in range(10):
            for j in range(10):
                if state[i][j] == BLACK:
                    tuples.append((i, j))
        return tuples

    def nextMove(self, state):
        wqs = self.findW(copy.deepcopy(state))
        bqs = self.findB(copy.deepcopy(state))
        newBoard = Board(10, wqs, bqs, self.str)
        result = self.ejw45_bot(newBoard, self.ejw45_mc)
        del newBoard
        return result


    def ejw45_bot(self, board, ejw45_mc):
        is_white = board.bWhite

        board = ejw45_Board(np.array(board.config))
        player = ejw45_MonteCarlo.Player(is_white)

        # Set a random move to be chosen if none of children boards are known
        boards, moves = board.moves(player)

        max_move = random.choice(moves)
        max_score = 0.0

        for index, board in enumerate(boards):
            move = moves[index]

            if board in ejw45_mc.explored:
                win_count, play_count = ejw45_mc.explored[board]
                score = float(win_count) / float(play_count)

                if score > max_score:
                    max_score = score
                    max_move = move

        return max_move


class Board:
    def __init__(self, size, wqs, bqs, myqueen):
        self.bWhite = True if myqueen == WHITE else False
        self.time_limit = None
        self.config = [['.' for c in range(size)] for r in range(size)]
        for (r, c) in wqs:
            self.config[r][c] = WHITE
        for (r, c) in bqs:
            self.config[r][c] = BLACK

    def valid_path(self, src, dst):
        (srcr, srcc) = src
        (dstr, dstc) = dst

        srcstr = rc2ld(src)
        dststr = rc2ld(dst)

        symbol = self.config[srcr][srcc]
        if (self.bWhite and symbol != WHITE) or (not self.bWhite and symbol != BLACK):
            print("invalid move: cannot find queen at src:", srcstr)
            return False

        h = dstr - srcr
        w = dstc - srcc
        if h and w and abs(h / w) != 1:
            print("invalid move: not a straight line")
            return False
        if not h and not w:
            print("invalid move: same star-end")
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
            if (self.config[r][c] != '.'):
                print("invalid move: the path is not cleared between", srcstr, dststr)
                return False
        return True

    def move_queen(self, src, dst):
        self.config[dst[0]][dst[1]] = self.config[src[0]][src[1]]
        self.config[src[0]][src[1]] = '.'

    def shoot_arrow(self, dst):
        self.config[dst[0]][dst[1]] = 'X'

    def end_turn(self):
        # count up each side's territories
        (w, b) = self.count_areas()
        # if none of the queens of either side can move, the player who just
        # played wins, since that player claimed the last free space.
        if b == w and b == 0:
            if self.bWhite:
                w = 1
            else:
                b = 1
        # switch player
        self.bWhite = not self.bWhite
        return (w, b)

    # adapted from standard floodfill method to count each player's territories
    # - if a walled-off area with queens from one side belongs to that side
    # - a walled-off area with queens from both side is neutral
    # - a walled-off area w/ no queens is deadspace
    def count_areas(self):
        # replace all blanks with Q/q/n/-
        def fill_area(replace):
            count = 0
            for r in range(size):
                for c in range(size):
                    if status[r][c] == '.':
                        count += 1
                        status[r][c] = replace
            return count

        # find all blank cells connected to the seed blank at (seedr, seedc)
        def proc_area(seedr, seedc):
            symbols = {}  # keeps track of types of symbols encountered in this region
            connected = [(seedr, seedc)]  # a stack for df traversal on the grid
            while connected:
                (r, c) = connected.pop()
                status[r][c] = '.'
                for ops in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    (nr, nc) = (r + ops[0], c + ops[1])
                    if nr < 0 or nr >= size or nc < 0 or nc >= size:
                        continue
                    # if it's a new blank, need to process it; also add to seen
                    if self.config[nr][nc] == '.' and status[nr][nc] == '?':
                        status[nr][nc] = '.'
                        connected.append((nr, nc))
                    # if it's a queen or an arrow; just mark as seen
                    elif self.config[nr][nc] != '.':
                        status[nr][nc] = 'X'
                        symbols[self.config[nr][nc]] = 1

            if WHITE in symbols and not BLACK in symbols:  # area belongs to white
                return (fill_area(WHITE), 0, 0)
            elif BLACK in symbols and not WHITE in symbols:  # area belongs to black
                return (0, fill_area(BLACK), 0)
            elif BLACK in symbols and WHITE in symbols:  # area is neutral
                return (0, 0, fill_area('n'))
            else:  # deadspace -- still have to fill but don't return its area value
                fill_area('-')
                return (0, 0, 0)

        size = len(self.config)
        # data structure for keeping track of seen locations
        status = [['?' for i in range(size)] for j in range(size)]
        wtot = btot = ntot = 0
        for r in range(size):
            for c in range(size):
                # if it's an empty space and we haven't seen it before, process it
                if self.config[r][c] == '.' and status[r][c] == '?':
                    (w, b, n) = proc_area(r, c)
                    wtot += w
                    btot += b
                    ntot += n
                # if it's anything else, but we haven't seen it before, just mark it as seen and move on
                elif status[r][c] == '?':
                    status[r][c] = 'X'

        if ntot == 0:  # no neutral space left -- should end game
            if wtot > btot:
                return (wtot - btot, 0)
            else:
                return (0, btot - wtot)
        else:
            return (wtot + ntot, btot + ntot)


class ejw45_Board:
    def __init__(self, board):
        self.board = np.array(board)
        self.player_symbols = {True: WHITE, False: BLACK}

    def moves(self, player):
        """
        :param is_white: if the player in question is white or black
        :return: a set of all possible moves in the form of (queen_start, queen_end, arrow)
        """
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
            return 'X', (r, c)

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
        return ejw45_Board(copy)

    @staticmethod
    def shoot_arrow(board, dst):
        copy = np.copy(board)
        copy[dst] = 'X'
        return ejw45_Board(copy)

    def __eq__(x, y):
        return np.array_equal(x.board, y.board)

    def __hash__(self):
        return hash(str(self.board))


class ejw45_MonteCarlo:
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

    def __init__(self, training_iterations=0, iswhite='WHITE'):

        self.start = ejw45_Board(np.array([['.', '.', '.', WHITE, '.', '.', WHITE, '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           [WHITE, '.', '.', '.', '.', '.', '.', '.', '.', WHITE],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           [BLACK, '.', '.', '.', '.', '.', '.', '.', '.', BLACK],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', BLACK, '.', '.', BLACK, '.', '.', '.']]))

        self.white_player = ejw45_MonteCarlo.Player(True if iswhite==WHITE else False)
        self.black_player = ejw45_MonteCarlo.Player(True if not iswhite==WHITE else False)
        self.white_player.other_player = self.black_player
        self.black_player.other_player = self.white_player

        self.explored = dict()

        if os.path.isfile('ai.pickle'):
            with open('ai.pickle', 'rb') as handle:
                self.explored = pickle.load(handle)

        if training_iterations > 0:
            self.train(training_iterations)

    def train(self, iterations):
        while iterations > 0:
            self.simulate()
            iterations -= 1

            if iterations % 10 == 0:
                self.write_to_file('ai.pickle')

    def write_to_file(self, path):
        with open(path, 'wb') as handle:
            pickle.dump(self.explored, handle)

    def select(self, current_state, player):

        max_state = None
        max_score = None

        child_boards, _ = current_state.moves(player)

        # Return the next unexplored node. If none exist, recurse on the best scoring child
        for child in child_boards:

            # If you've found an unexplored node
            if child not in self.explored:
                player.update(current_state)
                return current_state, player

            wins, plays = self.explored[child]
            if max_score is None or wins / plays > max_score:
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




