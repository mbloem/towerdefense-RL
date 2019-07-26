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
    
    
class ShallowMindBot:
    
    def __init__(self):
        pass
        
    def doTurn(self, api):
        '''
        Place your bot logic here !
        
        - If there is an opponent attack unit on a row, and you have enough energy for a defense
             Build a defense at a random unoccupied location on that row if it is undefended.
        - Else If you have enough energy for the most expensive building 
             Build a random building type at a random unoccupied location
        - Else: 
             Save energy until you have enough for the most expensive building
             
        Building Types :
            0 : Defense Building
            1 : Attack Building
            2 : Energy Building
            3 : Destroy/Remove Building //not really considered in this sample
            4 : Tesla //not really considered in this sample
            5 : Iron Curtain //not used in this sample
        '''
        #Some things you may want to print just to see the current state for debugging
        #print(api.getGameState())
        #print(api.getBuildingsStats())
        #print(api.getIronCurtainStats())
        #print(api.getMyself()))
        #print(api.getOpponent())
        #print(api.getMyBuildings())
        
        lanes = []
        x, y, building = 0, 0, 0
        # check all lanes for an attack unit
        for i in range(api.getGameHeight()):
            if len(api.getUnOccupied(api.getMyBuildings()[i])) == 0:
                # cannot place anything in a lane with no available cells.
                continue
            elif ((api.isUnderAttack(i) 
                  and (api.isDefended(i)) == False)
                  and (api.getMyself()['energy'] >= api.getBuildingsStats()['DEFENSE']['price'])):
                # place defense unit if there is an attack building and you can afford a defense building
                lanes.append(i)
        # lanes variable will now contain information about all lanes which have attacking units 
        # and no defense
        # A count of 0 would mean all lanes are not under attack
        if (len(lanes) > 0) :
            print("lanes " + str(len(lanes)))
            # Chose a random lane under attack to place a defensive unit
            # Chose a cell that is unoccupied in that lane
            building = 0
            y = random.choice(lanes)
            x = random.choice(api.getUnOccupied(api.getMyBuildings()[i]))
        # otherwise, build a random building type at a random unoccupied location
        # if you can afford the most expensive building between ATTACK, DEFENSE, and ENERGY building. This does not consider
        # The TESLA tower or account for the Iron Curtain
        elif  api.getMyself()['energy'] >= max(api.getBuildingsStats()['ATTACK']['price'], 
                                                                    api.getBuildingsStats()['DEFENSE']['price'], 
                                                                    api.getBuildingsStats()['ENERGY']['price']):
            building = random.choice([0, 1, 2])
            x = random.randint(0, api.getGameHeight() - 1)
            y = random.randint(0, int(api.getGameWidth() / 2) - 1)
        else:
            #towerDefenseHelper.writeDoNothing()
            return api.createDoNothingCommand()
        
       # towerDefenseHelper.writeCommand(x, y, building)
        return api.createCommand(x,y,building)
 

if __name__ == '__main__':
    from TowerDefense import *
    #This will load the game state and then call your doTurn function with an 
    #instance of the TowerDefenseApi to use in deciding your strategy for the turn
    TowerDefense.run(ShallowMindBot())
    
