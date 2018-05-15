#!/usr/bin/python
# -*- coding: utf-8 -*-
# ======================== Class Player =======================================
class Player:
    # student do not allow to change two first functions
    def __init__(self, str_name):
        self.str = str_name
        self.myqueen = []
        self.otherqueen = []

    def __str__(self):
        return self.str

    # Student MUST implement this function
    # The return value should be a move that is denoted by a list of tuples:
    # [(row1, col1), (row2, col2), (row3, col3)] with:
        # (row1, col1): current position of selected amazon
        # (row2, col2): new position of selected amazon
        # (row3, col3): position of the square is shot
    def nextMove(self, state):
        # result = [(0,3),(5,3),(8,6)] # example move in wikipedia
        self.findMyQueen(state)
        self.findOtherQueen(state)
        
        result = self.onResolver(state)

        self.myqueen = []
        self.otherqueen = []
        return result
    
    def findMyQueen(self, state):
        myname = 'w' if self.str=='w' else 'b'
        for i in range(10):
            for j in range(10):
                if state[i][j] == myname:
                    self.myqueen.append((i, j))

    def findOtherQueen(self, state):
        othername = 'w' if self.str=='b' else 'w'
        for i in range(10):
            for j in range(10):
                if state[i][j] == othername:
                    self.otherqueen.append((i, j))
    
    def seleQueen(self, state):
        # chọn queen để đi
        return (0,3)
    
    def moveQueen(self, state, cur_pos):
        # di chuyển queen đến vị trị mới
        return (5,3)
    
    def shot(self, state, new_pos):
        # vị trí bắn
        return (8,6)

    def onResolver(self, state):
        cur_pos = self.seleQueen(state)
        new_pos = self.moveQueen(state, cur_pos)
        shot_pos = self.shot(state, new_pos)
        return [cur_pos, new_pos, shot_pos]
        