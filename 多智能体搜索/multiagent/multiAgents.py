# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        
        score=successorGameState.getScore()
        
#         disGhost=util.manhattanDistance(newPos,newGhostStates[0].getPosition())
#         if disGhost>0:
#             score-=1.0/disGhost
#         disFood=[util.manhattanDistance(newPos,x) for x in newFood.asList()]
#         if len(disFood):
#             score+=1.0/min(disFood)
#         return score
            
        
        disGhost=[util.manhattanDistance(newPos,x.getPosition()) for x in newGhostStates]
        if len(disGhost):
            if max(disGhost)!=0:
                score-=5.0/max(disGhost)
        disFood=[util.manhattanDistance(newPos,x) for x in newFood.asList()]
        if len(disFood):
            score+=1.0/min(disFood)
        return score
        
#         return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        
        numAgent=gameState.getNumAgents()
        
        def value(state,agentIndex,depth):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state),None
            if depth>=self.depth:
                return self.evaluationFunction(state),None
            if agentIndex==0:
                return max_value(state,agentIndex,depth)
            if agentIndex>0:
                return min_value(state,agentIndex,depth)
            
            
        def max_value(state,agentIndex,depth):
            maxValue=-99999999
            maxAction=None
            for action in state.getLegalActions(agentIndex):
                successor=state.generateSuccessor(agentIndex,action)
                nextAgent=agentIndex+1
                if nextAgent>=numAgent :
                    nextAgent=0
                    nextDepth=depth+1
                else:
                    nextDepth=depth
                v,_ =value(successor,nextAgent,nextDepth)
                if v>=maxValue:
                    maxValue=v
                    maxAction=action

            return maxValue,maxAction

                
        def min_value(state,agentIndex,depth):
            minValue=9999999
            minAction=None
            for action in state.getLegalActions(agentIndex):
                successor=state.generateSuccessor(agentIndex,action)
                nextAgent=agentIndex+1
                if nextAgent>=numAgent :
                    nextAgent=0
                    nextDepth=depth+1
                else:
                    nextDepth=depth
                v,_ =value(successor,nextAgent,nextDepth)
                if v<=minValue:
                    minValue=v
                    minAction=action
            return minValue,minAction
        
        v,action=value(gameState,0,0)
        return action

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        
        numAgent=gameState.getNumAgents()
        
        def value(state,agentIndex,depth,a=-99999999,b=99999999):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state),None
            if depth>=self.depth:
                return self.evaluationFunction(state),None
            if agentIndex==0:
                return max_value(state,agentIndex,depth,a,b)
            if agentIndex>0:
                return min_value(state,agentIndex,depth,a,b)
            
            
        def max_value(state,agentIndex,depth,a,b):
            maxValue=-99999999
            maxAction=None
            for action in state.getLegalActions(agentIndex):
                successor=state.generateSuccessor(agentIndex,action)
                nextAgent=agentIndex+1
                if nextAgent>=numAgent :
                    nextAgent=0
                    nextDepth=depth+1
                else:
                    nextDepth=depth
                v,_ =value(successor,nextAgent,nextDepth,a,b)
                if v>=maxValue:
                    maxValue=v
                    maxAction=action
                if v>b:
                    return v,action
                a=max(a,v)

            return maxValue,maxAction

                
        def min_value(state,agentIndex,depth,a,b):
            minValue=9999999
            minAction=None
            for action in state.getLegalActions(agentIndex):
                successor=state.generateSuccessor(agentIndex,action)
                nextAgent=agentIndex+1
                if nextAgent>=numAgent :
                    nextAgent=0
                    nextDepth=depth+1
                else:
                    nextDepth=depth
                v,_ =value(successor,nextAgent,nextDepth,a,b)
                if v<=minValue:
                    minValue=v
                    minAction=action
                if v<a:
                    return v,action
                b=min(b,v)
            return minValue,minAction
        
        v,action=value(gameState,0,0)
        return action

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        
        numAgent=gameState.getNumAgents()
        
        def value(state,agentIndex,depth):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state),None
            if depth>=self.depth:
                return self.evaluationFunction(state),None
            if agentIndex==0:
                return max_value(state,agentIndex,depth)
            if agentIndex>0:
                return exp_value(state,agentIndex,depth)
            
            
        def max_value(state,agentIndex,depth):
            maxValue=-99999999
            maxAction=None
            for action in state.getLegalActions(agentIndex):
                successor=state.generateSuccessor(agentIndex,action)
                nextAgent=agentIndex+1
                if nextAgent>=numAgent :
                    nextAgent=0
                    nextDepth=depth+1
                else:
                    nextDepth=depth
                v,_ =value(successor,nextAgent,nextDepth)
                if v>=maxValue:
                    maxValue=v
                    maxAction=action

            return maxValue,maxAction

                
        def exp_value(state,agentIndex,depth):
            legalActions=state.getLegalActions(agentIndex)
            successor_prob=1.0/len(legalActions)
            expValue=0
            expAction=None
            for action in state.getLegalActions(agentIndex):
                successor=state.generateSuccessor(agentIndex,action)
                nextAgent=agentIndex+1
                if nextAgent>=numAgent:
                    nextAgent=0
                    nextDepth=depth+1
                else:
                    nextDepth=depth
                v,_ =value(successor,nextAgent,nextDepth)
                expValue+=successor_prob*v
                expAction=action

            return expValue,expAction
        
        v,action=value(gameState,0,0)
        return action

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    pos=currentGameState.getPacmanPosition()
    food=currentGameState.getFood()
    ghostStates=currentGameState.getGhostStates()
#     ghostPositions=currentGameState.getGhostPositions()
    scaredTimes=[ghostState.scaredTimer for ghostState in ghostStates]


    score=currentGameState.getScore()
    disGhost=[util.manhattanDistance(pos,x.getPosition()) for x in ghostStates]
    
    if max(disGhost)!=0:
        if max(scaredTimes)<max(disGhost):
            score-=2.0/min(disGhost)
        else:
            score+=2.0/min(disGhost)
            
    if max(scaredTimes)!=0:
        score+=2.0/max(scaredTimes)
    disFood=[util.manhattanDistance(pos,x) for x in food.asList()]
    if len(disFood):
        score+=1.0/min(disFood)
    return score
        
# Abbreviation
better = betterEvaluationFunction
