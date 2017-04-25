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


    def loadFile(self):
        with open(self.filePath, "rb") as file:
            self.stateList = pickle.load(file)