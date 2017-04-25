from Player import *
from Ant import *
from Building import *
from AIPlayerUtils import *
import math
import pickle
import os.path


##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        self.stateList = {}
        self.encountered = 0
        self.alpha = .99
        self.alphaDelta = 3
        self.alphaChange = .1
        self.discountFactor = .9
        self.filePath = "roddend17_estesm17_utilFile.txt"
        try:
            self.loadFile()
        except IOError:
            print "Util file nonexistant"
        super(AIPlayer, self).__init__(inputPlayerId, "Testing")

    def consolidate(self, state):

        turn = state.whoseTurn
        myId = PLAYER_ONE if turn == PLAYER_ONE else PLAYER_TWO
        enemId = PLAYER_TWO if turn == PLAYER_TWO else PLAYER_ONE
        myInv = state.inventories[myId]
        enemInv = state.inventories[enemId]
        myQueen = myInv.getQueen()
        enemQueen = enemInv.getQueen()
        myGrapes = []
        for invItem in state.inventories[NEUTRAL].constrs:
            if invItem.type == FOOD:
                myGrapes.append(invItem.coords)
        myStructs = []
        myStructs.append(myInv.getTunnels()[0].coords)
        myStructs.append(myInv.getAnthill().coords)

        # Check for whether we have won or lost
        consolidated = []
        if myInv.foodCount == FOOD_GOAL or len(enemInv.ants) <= 1 or enemQueen is None:
            consolidated.append(["S"])
        elif enemInv.foodCount == FOOD_GOAL or len(myInv.ants) <= 1 or myQueen is None:
            consolidated.append(["F"])
        else:
            consolidated.append(["M", myQueen.health, "E", enemQueen.health])
            ants = 0
            for currentAnt in myInv.ants:
                if ants == 2:
                    break
                if currentAnt.type is not WORKER:
                    continue
                if currentAnt.carrying:
                    for struct in myStructs:
                        consolidated.append(["CARRY", approxDist(self, struct)])
                else:
                    for grape in myGrapes:
                        consolidated.append([approxDist(self, grape)])
        return consolidated

    def addStateList(self, state, next):
        actualStates = ""
        for lines in self.consolidate(state):
            for line in lines:
                actualStates += str(line)
        if next is None and actualStates not in self.stateList:
            self.stateList[actualStates] = 0
            self.encountered += 1
            return self.stateList[actualStates]
        nextStates = ""
        for lines in self.consolidate(next):
            for line in lines:
                nextStates += str(line)
        if nextStates not in self.stateList:
            self.stateList[nextStates] = 0
            self.encountered += 1
            return self.stateList[nextStates]
        self.stateList[actualStates] += (self.reward(actualStates) - self.stateList[actualStates] + self.stateList[
            nextStates] * .92) * self.alpha
        return self.stateList[actualStates]

    def reward(self, consolidated):
        return 1.0 if "S" in consolidated else -1.0 if "F" in consolidated else -.01

    def loadFile(self):
        with open(self.filePath, "rb") as file:
            self.stateList = pickle.load(file)

    def saveFile(self):
        with open("AI/" + self.filePath, "wb") as file:
            pickle.dump(self.stateList, file, 0)