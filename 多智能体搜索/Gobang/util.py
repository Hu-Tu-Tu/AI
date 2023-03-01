# -*- coding: utf-8 -*-
"""
Play strategies of gobang game

@author: yhzhang@dgut.edu.cn
"""

import random
import numpy as np
from board import Board
from copy import deepcopy

import heapq

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def __repr__(self):
        return f'{self.heap}/{self.count}'
    
    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

class Pattern:
    def __init__(self, idx0, idx1, mask):
        self.idx0 = idx0
        self.idx1 = idx1
        self.mask = mask

def create_masks():
    masks = []
    for x in range(1, 64):
        mask = [0 for i in range(5)]
        y = x
        for i in range(5):
            mask[i] = y % 2
            y = y // 2
        masks.append(mask)
    return masks

def create_patterns():
    patterns = []
    idx0 = [i for i in range(5)]
    idx1 = [i for i in range(5)]
    masks = create_masks()
    for mask in masks:
        patterns.append(Pattern(idx0, idx1, mask))
    idx1 = [4-i for i in range(5)]
    for mask in masks:
        patterns.append(Pattern(idx0, idx1, mask))
    idx0 = [0 for i in range(5)]
    idx1 = [i for i in range(5)]
    for mask in masks:
        patterns.append(Pattern(idx0, idx1, mask))
    idx0 = [i for i in range(5)]
    idx1 = [0 for i in range(5)]
    for mask in masks:
        patterns.append(Pattern(idx0, idx1, mask))
    
    return patterns

def show_patterns(patterns):
    cnt = 0
    for pattern in patterns:
        print('pattern', cnt)
        cnt = cnt +1
        for i in range(len(pattern.mask)):
            print(pattern.idx0[i], pattern.idx1[i])
            
def is_match(pattern, player, board_slice):
    match = 1
    for i in range(len(pattern.mask)):
        x = pattern.idx0[i]
        y = pattern.idx1[i]
        if board_slice[x,y] != (pattern.mask[i]*player):
            match = 0
            break
   
    return match

def evaluate_move(move, player, board):
    score = 0
    if board.chess[move[0], move[1]] != 0:
        return score
    
    adversary = -player
    patterns = create_patterns()
    
    before = 0
    for pattern in patterns:    
        weight = pow(11, sum(pattern.mask))
        length = len(pattern.mask)
        for i in range(length):
            x1 = move[0] + pattern.idx0[0] - pattern.idx0[i]
            y1 = move[1] + pattern.idx1[0] - pattern.idx1[i]
            x2 = move[0] + pattern.idx0[length-1] - pattern.idx0[i]
            y2 = move[1] + pattern.idx1[length-1] - pattern.idx1[i]
            upper_left = (min(x1, x2), min(y1, y2))
            lower_right = (max(x1, x2), max(y1, y2))
            if upper_left[0]>=0 and upper_left[1]>=0 and lower_right[0]<board.size and lower_right[1]<board.size:
                board_slice = board.chess[upper_left[0]:lower_right[0]+1, upper_left[1]:lower_right[1]+1]
                before = before + is_match(pattern, player, board_slice)*weight
                
    for pattern in patterns:    
        weight = pow(10, sum(pattern.mask))
        length = len(pattern.mask)
        for i in range(length):
            x1 = move[0] + pattern.idx0[0] - pattern.idx0[i]
            y1 = move[1] + pattern.idx1[0] - pattern.idx1[i]
            x2 = move[0] + pattern.idx0[length-1] - pattern.idx0[i]
            y2 = move[1] + pattern.idx1[length-1] - pattern.idx1[i]
            upper_left = (min(x1, x2), min(y1, y2))
            lower_right = (max(x1, x2), max(y1, y2))
            if upper_left[0]>=0 and upper_left[1]>=0 and lower_right[0]<board.size and lower_right[1]<board.size:
                board_slice = board.chess[upper_left[0]:lower_right[0]+1, upper_left[1]:lower_right[1]+1]
                before = before + is_match(pattern, adversary, board_slice)*weight                  
                
    after = 0
    sim_board = deepcopy(board)
    sim_board.move(move, player)
    for pattern in patterns:    
        weight = pow(10, sum(pattern.mask))
        length = len(pattern.mask)
        for i in range(length):
            x1 = move[0] + pattern.idx0[0] - pattern.idx0[i]
            y1 = move[1] + pattern.idx1[0] - pattern.idx1[i]
            x2 = move[0] + pattern.idx0[length-1] - pattern.idx0[i]
            y2 = move[1] + pattern.idx1[length-1] - pattern.idx1[i]
            upper_left = (min(x1, x2), min(y1, y2))
            lower_right = (max(x1, x2), max(y1, y2))
            if upper_left[0]>=0 and upper_left[1]>=0 and lower_right[0]<board.size and lower_right[1]<board.size:
                board_slice = sim_board.chess[upper_left[0]:lower_right[0]+1, upper_left[1]:lower_right[1]+1]
                after = after + is_match(pattern, player, board_slice)*weight

    sim_board = deepcopy(board)
    sim_board.move(move, adversary)
    for pattern in patterns:    
        weight = pow(9, sum(pattern.mask))
        length = len(pattern.mask)
        for i in range(length):
            x1 = move[0] + pattern.idx0[0] - pattern.idx0[i]
            y1 = move[1] + pattern.idx1[0] - pattern.idx1[i]
            x2 = move[0] + pattern.idx0[length-1] - pattern.idx0[i]
            y2 = move[1] + pattern.idx1[length-1] - pattern.idx1[i]
            upper_left = (min(x1, x2), min(y1, y2))
            lower_right = (max(x1, x2), max(y1, y2))
            if upper_left[0]>=0 and upper_left[1]>=0 and lower_right[0]<board.size and lower_right[1]<board.size:
                board_slice = sim_board.chess[upper_left[0]:lower_right[0]+1, upper_left[1]:lower_right[1]+1]
                after = after + is_match(pattern, adversary, board_slice)*weight
    
    score = after - before
    
    return score

def score_func(player, board):
    score = np.zeros(board.chess.shape)
    legal_moves = board.get_legal_actions()
    for move in legal_moves:
        score[move[0], move[1]] = evaluate_move(move, player, board)
    return score

def find_best_move(player, board):
    legal_moves = board.get_legal_actions()
    best_move = None
    best_score = -999999
    for move in legal_moves:
        score = evaluate_move(move, player, board)
        if score > best_score:
            best_score = score
            best_move = []
            best_move.append(move)
        elif score == best_score:
            best_move.append(move)

    return random.choice(best_move)

def random_move(player, board):
    legal_moves = board.get_legal_actions()
    move = random.choice(legal_moves)
    return move

def test():
    b = Board()
    move = (2, 3)
    player = 1
    evaluate_move(move, player, b)