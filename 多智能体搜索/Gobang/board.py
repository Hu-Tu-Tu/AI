from copy import deepcopy
from itertools import groupby

import numpy as np

class Pattern:
    def __init__(self, idx0, idx1, mask):
        self.idx0 = idx0
        self.idx1 = idx1
        self.mask = mask

def create_win_patterns():
    patterns = []
    mask = [1 for i in range(5)]
    idx0 = [i for i in range(5)]
    idx1 = [i for i in range(5)]
    patterns.append(Pattern(idx0, idx1, mask))
    idx1 = [4-i for i in range(5)]
    patterns.append(Pattern(idx0, idx1, mask))
    idx0 = [0 for i in range(5)]
    idx1 = [i for i in range(5)]
    patterns.append(Pattern(idx0, idx1, mask))
    idx0 = [i for i in range(5)]
    idx1 = [0 for i in range(5)]
    patterns.append(Pattern(idx0, idx1, mask))    
    return patterns

def is_match(pattern, player, board_slice):
    match = 1
    for i in range(len(pattern.mask)):
        x = pattern.idx0[i]
        y = pattern.idx1[i]
        if board_slice[x,y] != (pattern.mask[i]*player):
            match = 0
            break
   
    return match

def is_winning_move(move, player, chess):
    win = 0
    patterns = create_win_patterns()
    for pattern in patterns:
        length = len(pattern.mask)
        size, _ = chess.shape
        for i in range(length):
            x1 = move[0] + pattern.idx0[0] - pattern.idx0[i]
            y1 = move[1] + pattern.idx1[0] - pattern.idx1[i]
            x2 = move[0] + pattern.idx0[length-1] - pattern.idx0[i]
            y2 = move[1] + pattern.idx1[length-1] - pattern.idx1[i]
            upper_left = (min(x1, x2), min(y1, y2))
            lower_right = (max(x1, x2), max(y1, y2))
            if upper_left[0]>=0 and upper_left[1]>=0 and lower_right[0]<size and lower_right[1]<size:
                board_slice = chess[upper_left[0]:lower_right[0]+1, upper_left[1]:lower_right[1]+1]
                if is_match(pattern, player, board_slice):
                    win = 1
                    break
            if win:
                break
                
    return win

class Board:
    def __init__(self, size=15):
        ''' initialize the board with zeros '''
        self.size = size
        self.chess = np.zeros((size, size), int)
        self.terminated = 0
        self.winner = 0
        print(f'==> Board initializing:\n{self.chess}')
        self.vacuity = list(map(lambda x: tuple(x), np.argwhere(self.chess == 0)))

    def update(self, pos, player):
        ''' find  positions that are available for move adn check whether the game is over'''
        #self.vacuity = list(map(lambda x: tuple(x), np.argwhere(self.chess == 0)))
        self.vacuity.remove(pos)
        if is_winning_move(pos, player, self.chess):
            self.terminated = 1
            self.winner = player
        if not self.terminated:
            if len(self.vacuity)==0:
                self.terminated = 1
                self.winner = 0
        
    def get_legal_actions(self):
        ''' find  positions that are available for move'''
        return self.vacuity        

    def move(self, pos, player):
        ''' move a chess '''
        self.chess[pos[0], pos[1]] = player
        self.update(pos, player)

    def is_terminated(self):
        return self.terminated, self.winner

if __name__ == "__main__":
    Board()
