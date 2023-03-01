from copy import deepcopy
from time import time
from random import choice, randint, shuffle

import numpy as np

from board import Board
import util
import sys 
sys.setrecursionlimit(1000000)

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
    def __init__(self, parent, player, move=None,pos=None):
        # 总共赢了多少次
        self.succ = 0
        # 节点总的访问次数
        self.total = 0
        self.child = []
        # 存储还没有扩展的节点,非空表示还有没有扩展的节点
        self.unexpanded = set([])
        self.parent = parent
        # 当前游戏玩家
        self.player = player
        
        
        # 父节点的行动
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
        self.time_limit = time_limit
        self.tick = 0
        # 执棋方 一开始是-1
        self.player = player                                            
        # 记录模拟游戏的次数
        self.cnt = 0                                                    
        # 步骤的分数
        self.score = []


    def limit_branch(self, node, board):
        # 合法的下一步,没有被-1或者1霸占的点
        legal_moves = board.get_legal_actions()
#         print(legal_moves)
        # 寻找没有被扩展的节点limit_moves
        limit_moves = []
        queue = util.PriorityQueue()
        for move in legal_moves:
#             print(move,":",-self.score[move[0], move[1]])
            # 把节点和分数一起添加
            queue.push(move, -self.score[move[0], move[1]])
#         print(queue) # 添加输出格式函数
        while True:
            if len(limit_moves)==0:
                limit_moves.append(queue.pop())
                # print(limit_moves)
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
#         print(board)# 添加输出格式函数
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
            node = self.expansion(node, sim_board)                                 
            
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
    # board棋局状态
    def selection(self, node, board):
        """
        步骤1，节点选择
        :return: 搜索树向下递归选择子节点
        """
        
        ''' 从搜索树的根节点开始，向下递归选择子节点，直至到达叶子节点或者到达具有还未被扩展过子节点 '''
        # YOUR CODE HERE
        terminate,_=board.is_terminated()
        if terminate!=0:# 不是叶子节点，没有结束
            return node

        if node.total==0:# 没有扩展的节点
            return node

        maxUcb=node.succ/node.total+2 * \
            np.sqrt(np.log(self.cnt)/node.total)  # 最大的ucb，一开始是当前node
        maxNode=node
        # 计算子节点的ucb，取最大的一个
        for child in node.child:
            tempNode=self.selection(child,board)
            tempUcb=tempNode.succ/tempNode.total+2 * \
                np.sqrt(np.log(self.cnt)/tempNode.total)
            if tempUcb>maxUcb:
                maxUcb=tempUcb
                maxNode=tempNode
        return maxNode
    

    def expansion(self, node, board):
        """
        步骤2，节点扩展
        """
        
        # YOUR CODE HERE 
        # 取点
        newPos=node.unexpanded.pop()
        # 模拟下到棋盘
        board.move(newPos,self.player)
        newNode=Node(parent=node,player=self.player,move=newPos)
        # 在棋盘中没有被-1或者1标记的节点中选择合理的节点
        self.limit_branch(newNode, board)
        node.child.append(newNode)
        
        return newNode

    def simulation(self, node, board):    # roll out
        """
        步骤3，模拟扩展搜索树
        """
        
        # YOUR CODE HERE

        while True:
            terminate,win=board.is_terminated()
            if terminate!=0: # 说明有人赢了
                return win# 返回作为分数
            player=node.player*(-1)
            # 随机下棋
            move=util.random_move(player,board)
            board.move(move,player)


    def backpropagation(self, node, score):
        """
        步骤4，反向传播，回溯更新模拟路径中的节点奖励
        """
        # YOUR CODE HERE
        self.cnt+=1
        while node!=None:
            node.succ+=score
            node.total+=1
            node=node.parent
            
            
            
            