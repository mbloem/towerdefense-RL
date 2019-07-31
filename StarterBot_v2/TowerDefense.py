# -*- coding: utf-8 -*-
'''
Entelect StarterBot for Python3
'''
import time

startTime = time.time()

import json
import os
from time import sleep
import random

from TowerDefenseApi import *   
    
class TowerDefense:
    
    def __init__(self,state_location):
        '''
        Initialize Bot.
        Load all game state information.
        '''
        try:
            self.game_state = self.loadState(state_location)
        except IOError:
            print("Cannot load Game State")
            
    
    def getGameState(self):
        return self.game_state    
        
    def loadState(self,state_location):
        '''
        Gets the current Game State json file.
        '''
        return json.load(open(state_location,'r'))
    
   
    def writeCommand(self, command):
        outfl = open('command.txt','w')
        outfl.write(command)
        outfl.close()
        return None
    
    #def writeCommand(self,x,y,building):
    #    '''
    #    command in form : x,y,building_type
    #    '''
    #    outfl = open('command.txt','w')
    #    outfl.write(','.join([str(x),str(y),str(building)]))
    #    outfl.close()
    #    return None

    def writeDoNothing(self):
        '''
        command in form : x,y,building_type
        '''
        outfl = open('command.txt','w')
        outfl.write("")
        outfl.close()
        return None

    @staticmethod
    def run(bot):
        #DO NOT CHANGE THESE STEPS
        towerDefense = TowerDefense('state.json')
        towerDefenseApi = TowerDefenseApi(towerDefense.getGameState())
        command = bot.doTurn(towerDefenseApi)
        print("Command returned by player: " + command)
        towerDefense.writeCommand(command)
        
    