from copy import deepcopy
from time import time
from random import choice, randint, shuffle
import math 
import numpy as np

from board import Board
import util

class GreedyAgent:
    ''' 贪心智能体 '''
    def __init__(self, player):
        """
        初始化
        :param player: -1表示黑方，1表示白方
        """
        self.player = player     
        
    def act(self, queue):
        """
        input: queue包含棋盘的队列
        return: 选择最佳拓展
        """
        board = queue.get()  # 获取棋盘
        best_move = util.find_best_move(self.player, board)
        queue.put(best_move)                                     # 返回最佳落子点         

class Node:
    ''' node of the search tree '''
    def __init__(self, parent, player, move=None):
        self.succ = 0    # ti
        self.total = 0   # ni 
        self.child = []  # 子节点列表 
        self.unexpanded = set([])
        self.parent = parent
        self.player = player
        self.move = move

    def __repr__(self):
        return f'{self.move}=>{self.succ}/{self.total}={self.ucb}'

    def __hash__(self):
        return id(self)

class Agent:
    ''' 蒙特卡洛树搜索 '''
    
    def __init__(self, player, time_limit=30):
        """
        蒙特卡洛树搜索策略初始化
        :param time_limit: 蒙特卡洛树搜索每步的搜索时间步长
        :param tick:记录开始搜索的时间
        :param player: 1表示白方，-1表示黑方
        """
        self.time_limit = time_limit  # 时间限制 
        self.tick = 0                 # ？？
        self.player = player          # 玩家     # 执棋方
        self.cnt = 0                  # 记录模拟游戏的次数
        self.score = []           

    def limit_branch(self, node, board):
        legal_moves = board.get_legal_actions()
        limit_moves = []
        queue = util.PriorityQueue()
        for move in legal_moves:
            queue.push(move, -self.score[move[0], move[1]])
        while True:
            if len(limit_moves)==0:
                limit_moves.append(queue.pop())
            else:
                move = queue.pop()
                if self.score[move[0], move[1]] < self.score[limit_moves[0][0], limit_moves[0][1]]:
                    break
                else:
                    limit_moves.append(move)
        node.unexpanded = set(limit_moves)

    def mcts(self, queue):
        """
        蒙特卡洛树搜索，在时间限制范围内，拓展节点搜索结果
        input: queue包含棋盘的队列
        return: 选择最佳拓展
        """
        
        self.cnt = 0
        self.tick = time()                                              # 更新开始搜索的时间
        
        board = queue.get()  # 获取棋盘
        
        self.score = util.score_func(self.player, board)

        root = Node(None, self.player)                                  # 以当前棋局状态为根节点
        #root.unexpanded = set(board.get_legal_actions())
        self.limit_branch(root, board)
        
        if len(root.unexpanded)==1:
            queue.put(root.unexpanded.pop())
            return
        
        ''' 蒙特卡洛树搜索算法，在时间限制范围内循环进行步骤1至4 '''
        while time() - self.tick < self.time_limit - 1e-4:                 # 在时长允许范围内蒙特卡洛树搜索算法继续选择和扩展节点 
            sim_board = deepcopy(board)                                    # 深拷贝当前棋局状态，以方便智能体在进行模拟对局的时候
                                                                           # 不改变当前对局状态
            # 步骤1.从蒙特卡洛树的根节点开始，向下递归选择子节点
            node = self.selection(root, sim_board)                          
            
            # 步骤2. 随机扩展一个未被扩展过的后继边缘节点M
            node = self.expansion(node, sim_board)      # 上一步的把node传进去了、                             
            
            # 步骤3. 从节点M出发，模拟对局以此来扩展蒙特卡洛搜索树，并返回模拟结果
            score = self.simulation(node, sim_board)                
            
            # 步骤4. 回溯更新
            self.backpropagation(node, score)                             
            
        ''' 从根节点的子节点中搜索最佳落子点(被扩展最多的子节点) '''           
        best_total = -1                                                  # 子节点中最大的扩展次数
        best_move = []                                                   # 被扩展最多次的子节点
        for child in root.child:                                         # 遍历所有子节点
            if child.total > best_total:                                 # 寻找最大扩展次数
                best_total = child.total
                best_move = []
                best_move.append(child.move)
            elif child.total == best_total:
                best_move.append(child.move)
        
        print("模拟对弈次数：", self.cnt)
        queue.put(choice(best_move))                                     # 返回最佳落子点 

    def selection(self, node, board):
        """
        步骤1，节点选择
        :return: 搜索树向下递归选择子节点
        """
        
        ''' 从搜索树的根节点开始，向下递归选择子节点，直至到达叶子节点或者到达具有还未被扩展过子节点 '''
        # YOUR CODE HERE
        if len(node.child) == 0 or len(node.unexpanded) > 0:   # 到达叶子节点或者到达具有还未被扩展过子节点
            return node  
        max_ucb_child= []
        C = 2  # 定义系数为2 
        max_ucb = float('-inf') 
        for childNode in node.child: 
            # 计算所有子节点的ucb，选择最大的那一个
            if childNode.total == 0 :
                ucb=float('inf')
            else :
                ucb = (float)(childNode.succ)/childNode.total + C* math.sqrt(math.log(node.total)/childNode.total) 
            if ucb > max_ucb:
                max_ucb = ucb 
                max_ucb_child.append(childNode) 
        return choice(max_ucb_child)  # 随机选择一个 

    def expansion(self, node, board):
        """
        步骤2，节点扩展
        """
        # YOUR CODE HERE
        if len(node.unexpanded) ==0:  
            node.unexpanded=set(board.get_legal_actions())  # 获取合法的行动

        # self.vacuity = list(map(lambda x: tuple(x), np.argwhere(self.chess == 0)))
        randomAction= choice(list(node.unexpanded))   # 返回的是一个随机行动 
        # 创建孩子节点
        childNode = Node(node, node.player, randomAction)  # NOTE : 玩家是谁？
        node.child.append(childNode)
        # 在当前节点去掉被拓展了的节点
        node.unexpanded.discard(randomAction) 
        self.cnt += 1   # 模拟次数+1
        return childNode 

    def simulation(self, node, board):    # roll out
        """
        步骤3，模拟扩展搜索树————随机下棋 
        """
        board.move(node.move, node.player)  # 随机下棋 ,棋盘会更新状态，然后判断
        terminated, winner = board.is_terminated()
        if terminated==0: # 没终止
            return 0  
        if node.player==winner :  # 终止 
            return 1 
        else :
            return -1 


    def backpropagation(self, node, score):
        """
        步骤4，反向传播，回溯更新模拟路径中的节点奖励
        """
        # YOUR CODE HERE
        while node is None :
            node.total+=1
            node.succ+=score 
            node=node.parent 

            
            
            
            
