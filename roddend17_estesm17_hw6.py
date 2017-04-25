import math
import pickle

from AIPlayerUtils import *
from Player import *


class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        # learning to be used for reward
        self.alpha = .99
        # above alpha's rate of change
        self.alphaDelta = 5
        # alpha decrement
        self.alphaChange = .1
        # amount of states we've stumbled across
        self.encountered = 0
        # states used to eventually save to file in order to learn
        self.stateList = {}
        # path at which learning is stored
        self.filePath = "roddend17_estesm17_utilFile.txt"
        # Attempt to load file if one exists already, otherwise start from zero
        try:
            self.loadFile()
        except IOError:
            print "File nonexistent, starting from zero"
        # Call upon super to set the AI name
        super(AIPlayer, self).__init__(inputPlayerId, "TD Learner")

    @staticmethod
    def consolidate(state):
        """
        Consolidates the given state info to be used as a condensed version
        :param state:
        :return: list of lists of the game state
        """
        turn = state.whoseTurn
        my_id = PLAYER_ONE if turn is not None and turn == PLAYER_ONE else PLAYER_TWO
        enemy_id = PLAYER_TWO if turn is not None and turn == PLAYER_TWO else PLAYER_ONE
        my_inv = state.inventories[my_id]
        enemy_inv = state.inventories[enemy_id]
        my_queen = my_inv.getQueen()
        enemy_queen = enemy_inv.getQueen()
        my_grapes = []
        for invItem in state.inventories[NEUTRAL].constrs:
            if invItem.type == FOOD:
                my_grapes.append(invItem.coords)
        my_structs = []
        my_tunnels = my_inv.getTunnels()
        if len(my_tunnels) is not 0:
            my_structs.append(my_inv.getTunnels()[0].coords)
        my_structs.append(my_inv.getAnthill().coords)

        # Check for whether we have won or lost
        consolidated = []
        if my_inv.foodCount == FOOD_GOAL or len(enemy_inv.ants) <= 1 or enemy_queen is None:
            consolidated.append(["Success"])
        elif enemy_inv.foodCount == FOOD_GOAL or len(my_inv.ants) <= 1 or my_queen is None:
            consolidated.append(["Failure"])
        else:
            consolidated.append(["Me", my_queen.health, "Enemy", enemy_queen.health])
            ants = 0
            for currentAnt in my_inv.ants:
                if ants == 2:
                    break
                if currentAnt.type is not WORKER:
                    continue
                if currentAnt.carrying:
                    struct = []
                    for my_struct in my_structs:
                        struct.append(approxDist(currentAnt.coords, my_struct))
                    consolidated.append(["Carry", min(struct)])
                else:
                    grapes = []
                    for grape in my_grapes:
                        grapes.append(approxDist(currentAnt.coords, grape))
                    consolidated.append(["Grape", min(grapes)])
        return consolidated

    def getMove(self, currentState):
        """
        Gets the next move from Player
        :param currentState: current state passed used to return the move to take
        :return: move to take
        """
        self.addStateList(currentState)
        return self.greatestState(currentState)

    def addStateList(self, state, following_state=None):
        """
        Adds to stateList with regards to the information provided by state and following_state
        :param state:
        :param following_state:
        :return: the recorded actual_state element within stateList
        """
        actual_states = ""
        for lines in self.consolidate(state):
            for line in lines:
                actual_states += str(line)
        if following_state is None:
            if actual_states not in self.stateList:
                self.stateList[actual_states] = 0
                self.encountered += 1
            return self.stateList[actual_states]
        next_states = ""
        for lines in self.consolidate(following_state):
            for line in lines:
                next_states += str(line)
        if next_states not in self.stateList:
            self.stateList[next_states] = 0
            self.encountered += 1
            return self.stateList[next_states]
        self.stateList[actual_states] += (self.reward(actual_states) - self.stateList[actual_states] + self.stateList[
            next_states] * .92) * self.alpha
        return self.stateList[actual_states]

    def greatestState(self, state):
        """
        To be called after addStateList within getMove to either get the best move or to try a new one
        :param state:
        :return: move to be returned within getMove
        """
        legal_moves = listAllLegalMoves(state)
        greatest = None
        greatest_value = None
        for movement in legal_moves:
            current = self.addStateList(state, self.predict(state, movement))
            if greatest_value is None or current > greatest_value:
                greatest_value = current
                greatest = movement
        return legal_moves[random.randint(0, len(legal_moves) - 1)] if random.random() > .7 else greatest

    @staticmethod
    def predict(current_state, move):
        """
        Invokes fastclone() on current_state to be altered with regards to the type of movement
        :param current_state:
        :param move:
        :return:
        """
        current_state = current_state.fastclone()
        if move.moveType == END:
            return current_state
        if move.moveType == BUILD:
            coord_list = move.coordList[0]
            current_inv = current_state.inventories[current_state.whoseTurn]
            if move.buildType == TUNNEL:
                return current_state
            current_inv.foodCount -= UNIT_STATS[move.buildType][COST]
            ant = Ant(coord_list, move.buildType, current_state.whoseTurn)
            ant.hasMoved = True
            current_state.inventories[current_state.whoseTurn].ants.append(ant)
            return current_state
        source = move.coordList[0]
        dest = move.coordList[-1]
        current = getAntAt(current_state, source)
        current.coords = (dest[0], dest[1])
        current.hasMoved = True
        return current_state

    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    def registerWin(self, hasWon):
        """
        Called at the end of the game and a vital part of the learning process
        Modifies the alpha according to the values set within __init__
        :param hasWon: whether we have won or not
        """
        self.alpha -= self.alphaChange * (1.0 - .99 / math.exp(self.alpha ** self.alphaDelta))
        self.encountered = 0
        self.saveFile()

    @staticmethod
    def reward(consolidated):
        """
        Rewards based on whether "Success" or "Failure" exist in the consolidated state or not
        :param consolidated: consolidated state to be searched in order to reward
        :return: 1 for a win, -1 for a loss, and -.1 for neither
        """
        return 1.0 if "Success" in consolidated else -1.0 if "Failure" in consolidated else -.01

    def loadFile(self):
        """
        Attempts to load the file containing the path set within __init__ to be used in stateList
        """
        with open(self.filePath, "rb") as file:
            self.stateList = pickle.load(file)

    def saveFile(self):
        """
        Saves stateList data to the path set within __init__
        Creates file if does not exist already
        """
        with open("AI/" + self.filePath, "wb") as file:
            pickle.dump(self.stateList, file, 0)
