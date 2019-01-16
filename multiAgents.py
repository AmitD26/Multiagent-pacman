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
import random, util, math

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
		some Directions.X for some X in the set {North, South, West, East, Stop}
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

		"*** YOUR CODE HERE ***"

		score = 0
		newFood = newFood.asList()
		num_food = len(newFood)	#Number of food pellets left

		#If num_food == 0, it means that all food has been consumed by the Pacman, which is ideal
		if num_food == 0:
			return 99999
		
		gh_x, gh_y = currentGameState.getGhostPosition(1)
		gh_dist = manhattanDistance(newPos, (gh_x, gh_y))

		#If the new position has food, 20 is added to the score. Also, ten times the reciprocal of the distance to the nearest food pellet is added to the score. It is multiplied by 10 in order to give it more weight.
		min_dist_to_food = 99999
		for food in newFood:
			if newPos == food:
				score += 20
			else:
				min_dist_to_food = min(min_dist_to_food, manhattanDistance(food, newPos))

		score += 10.0 * (1.0/min_dist_to_food)
		
		#If pacman gets too close to a ghost, 50 is subtracted from the score.
		dist_to_ghost = manhattanDistance(newPos, (gh_x, gh_y))
		if dist_to_ghost <= 2:
			score -= 50

		#If pacman lands on a power pellet, 100 is added to the score.
		if newPos in currentGameState.getCapsules():
			score += 100


		#If the ghost is scared (i.e after pacman has eaten a power pellet), the timer multiplied by the distance between pacman and the ghost is added to the score.
		if newScaredTimes is not None:
			score += newScaredTimes[0] * manhattanDistance(currentGameState.getPacmanPosition(), currentGameState.getGhostPosition(1))

		score += successorGameState.getScore()
		return score

		
		

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


#This variable is used to keep track of the number of nodes expanded.
number_of_nodes = 0
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
		"""
		"*** YOUR CODE HERE ***"
		
		'''
		Reference has been taken from http://www.giocc.com/concise-implementation-of-minimax-through-higher-order-functions.html for writing this code.
		
		The max player (pacman) and the min player (ghosts) are defined as two separate functions. 
		Since the number of ghosts is more than 1, the min player function calls itself recursively for each ghost. 
		It keeps track of the ghosts using the agentIndex variable.
		'''

		#This is the starting point. Pacman is the max player and it makes the first move.
		action = self.max_player(gameState, gameState.getNumAgents(), self.depth)
		legal_actions = gameState.getLegalActions()
		print "Number of nodes expanded: " + str(number_of_nodes)
		if action[1] in legal_actions:
			return legal_actions[legal_actions.index(action[1])]


	def min_player(self,state, agentIndex, num_agents, depth):
		min_score = 999999
		#The agentIndex keeps track of the number of times the min player has called itself. If agentIndex > num_agents, it means that all the ghosts have played their turn and it is now pacman's turn.
		if(agentIndex >= num_agents):
			if(depth == 1):
				return self.evaluationFunction(state)
			else:
				#We decrement the depth while passing it to the max player since one ply has been completed.
				return self.max_player(state, num_agents, depth - 1)
		else:
			legal_actions = state.getLegalActions(agentIndex)

			for action in legal_actions:
				successorGameState = state.generateSuccessor(agentIndex, action)
				#We increment the number_of_nodes variable since we generated a successor.
				global number_of_nodes
				number_of_nodes += 1
				#Checking whether we have reached the leaf node.
				if(successorGameState.isWin() or successorGameState.isLose()):
					min_score = min(min_score, self.evaluationFunction(successorGameState))
				else:
					#We increment the agent index while calling min player since it is now time for the next ghost's turn.
					min_score = min(min_score, self.min_player(successorGameState, agentIndex + 1, num_agents, depth))
		return min_score


	def max_player(self, state, num_agents, depth):
		#pacman_choice variable keeps track of the action corresponding to the best score.
		pacman_choice = None
		max_score = -999999
		legal_actions = state.getLegalActions(0)

		for action in legal_actions:
			successorGameState = state.generateSuccessor(0, action)
			global number_of_nodes
			number_of_nodes += 1

			if(successorGameState.isWin() or successorGameState.isLose()):
				successor_score = self.evaluationFunction(successorGameState)
				if successor_score > max_score:
					max_score = successor_score
					pacman_choice = action
			else:
				successor_score = self.min_player(successorGameState, 1, num_agents, depth)
				if successor_score > max_score:
					max_score = successor_score
					pacman_choice = action

		#depth == self.depth means that we are at the top level of recursion, the level at which pacman wants to make a choice. Hence, we also return the best action along with the max score.
		if(depth == self.depth):
			return max_score,pacman_choice
		else:
			return max_score

		util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
	"""
	  Your minimax agent with alpha-beta pruning (question 3)
	"""
	def getAction(self, gameState):
		"""
		  Returns the minimax action using self.depth and self.evaluationFunction
		"""
		"*** YOUR CODE HERE ***"
		'''
		This code has been implemented according to the pseudocode given by the instructors on the project webpage http://www3.cs.stonybrook.edu/~cse537/project02.html.
		'''
		action = self.max_player(gameState, gameState.getNumAgents(), self.depth, -999999, 999999)
		legal_actions = gameState.getLegalActions()
		print "Number of nodes expanded: " + str(number_of_nodes)
		if action[1] in legal_actions:
			return legal_actions[legal_actions.index(action[1])]


	def min_player(self,state, agentIndex, num_agents, depth, alpha, beta):
		min_score = 999999
		V = 999999
		if(agentIndex >= num_agents):
			if(depth == 1):
				return self.evaluationFunction(state)
			else:
				if alpha > beta:
					return V
				return self.max_player(state, num_agents, depth - 1, alpha, beta)
		else:
			legal_actions = state.getLegalActions(agentIndex)

			for action in legal_actions:
				if alpha > beta:
					return V
				successorGameState = state.generateSuccessor(agentIndex, action)
				global number_of_nodes
				number_of_nodes += 1
				if(successorGameState.isWin() or successorGameState.isLose()):
					V = min(V, self.evaluationFunction(successorGameState))
					if V < alpha:
						return V
					beta = min(beta, V)
				else:
					V = min(V, self.min_player(successorGameState, agentIndex + 1, num_agents, depth, alpha, beta))
					if V < alpha:
						return V
					beta = min(beta, V)
		return V


	def max_player(self, state, num_agents, depth, alpha, beta):
		pacman_choice = None
		max_score = -999999
		V = -999999
		legal_actions = state.getLegalActions(0)

		for action in legal_actions:
			if alpha > beta:
				break
			successorGameState = state.generateSuccessor(0, action)
			global number_of_nodes
			number_of_nodes += 1
			
			if(successorGameState.isWin() or successorGameState.isLose()):
				successor_score = self.evaluationFunction(successorGameState)
				if successor_score > V:
					V = successor_score
					pacman_choice = action
				if V > beta:
					return V
				alpha = max(alpha, V)
			else:
				successor_score = self.min_player(successorGameState, 1, num_agents, depth, alpha, beta)
				if successor_score > V:
					V = successor_score
					pacman_choice = action
				if V > beta:
					return V
				alpha = max(alpha, V)
		if(depth == self.depth):
			return V,pacman_choice
		else:
			return V

		util.raiseNotDefined()


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
		"*** YOUR CODE HERE ***"

		action = self.max_player(gameState, gameState.getNumAgents(), self.depth)
		legal_actions = gameState.getLegalActions()
		print "Number of nodes expanded: " + str(number_of_nodes)
		if action[1] in legal_actions:
			return legal_actions[legal_actions.index(action[1])]


	'''
	It is assumed that we are running against an adversary which chooses amongst their getLegalActions uniformly at random.
	We calculate the average score by adding up the scores for each action and dividing by the total number of actions.
	'''
	def exp_player(self,state, agentIndex, num_agents, depth):
		min_score = 999999
		expected_value = 0.0
		if(agentIndex >= num_agents):
			if(depth == 1):
				return self.evaluationFunction(state)
			else:
				return self.max_player(state, num_agents, depth - 1)
		else:
			legal_actions = state.getLegalActions(agentIndex)

			for action in legal_actions:
				successorGameState = state.generateSuccessor(agentIndex, action)
				global number_of_nodes
				number_of_nodes += 1
				if(successorGameState.isWin() or successorGameState.isLose()):
					expected_value += self.evaluationFunction(successorGameState)
				else:
					expected_value += self.exp_player(successorGameState, agentIndex + 1, num_agents, depth)
		num_of_actions = len(legal_actions)
		expected_value = expected_value/float(num_of_actions)
		return expected_value


	def max_player(self, state, num_agents, depth):
		pacman_choice = None
		max_score = -999999
		legal_actions = state.getLegalActions(0)

		for action in legal_actions:
			successorGameState = state.generateSuccessor(0, action)
			global number_of_nodes
			number_of_nodes += 1

			if(successorGameState.isWin() or successorGameState.isLose()):
				successor_score = self.evaluationFunction(successorGameState)
				if successor_score > max_score:
					max_score = successor_score
					pacman_choice = action
			else:
				successor_score = self.exp_player(successorGameState, 1, num_agents, depth)
				if successor_score > max_score:
					max_score = successor_score
					pacman_choice = action
		if(depth == self.depth):
			return max_score,pacman_choice
		else:
			return max_score




		util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
	"""
	  Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
	  evaluation function (question 5).

	  DESCRIPTION: <write something here so we know what you did>
	"""
	"*** YOUR CODE HERE ***"
	util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
