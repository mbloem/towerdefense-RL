# -*- coding: utf-8 -*-
'''
Entelect StarterBot for Python3
'''
import time

startTime = time.time()

import numpy as np

import json
import os
from time import sleep
import random
from collections import OrderedDict, Set

from TowerDefenseApi import *

NUM_ACTION_TYPES = 7 # defend, attack, energy, destroy, tesla, iron curtain, do nothing
    
class ShallowMindBot:
    
    def __init__(self):
        # Put (trained) policy parameters here eventually

        # Also a helpful dict
        self.idx2actionType = {
            0: self.doDefense,
            1: self.doAttack,
            2: self.doEnergy,
            3: self.doDestroy,
            4: self.doTesla,
            5: self.doIronCurtain,
            6: self.doNothing,
        }

    def doDefense(self, stateFeatures, api):
        building = 0

        y = random.randint(0, int(api.getGameHeight()))
        x = random.choice(api.getUnOccupied(api.getMyBuildings()[y]))

        return api.createCommand(x,y,building)

    def doAttack(self, stateFeatures, api):
        building = 1

        y = random.randint(0, int(api.getGameHeight()))
        x = random.choice(api.getUnOccupied(api.getMyBuildings()[y]))

        return api.createCommand(x,y,building)

    def doEnergy(self, stateFeatures, api):
        building = 2

        y = random.randint(0, int(api.getGameHeight()))
        x = random.choice(api.getUnOccupied(api.getMyBuildings()[y]))

        return api.createCommand(x,y,building)

    def doDestroy(self, stateFeatures, api):
        building = 3

        my_buildings_array = np.array(api.getMyBuildings())
        my_building_coords = np.where(my_buildings_array>0)
        num_buildings = len(my_building_coords[0])
        random_building_idx = np.random.choice(range(num_buildings))
        random_building_y = my_building_coords[0][random_building_idx]
        random_building_x = my_building_coords[1][random_building_idx]

        return api.createCommand(random_building_x,random_building_y,building)

    def doTesla(self, stateFeatures, api):
        building = 4

        y = random.randint(0, int(api.getGameHeight()))
        x = random.choice(api.getUnOccupied(api.getMyBuildings()[y]))

        return api.createCommand(x,y,building)

    def doIronCurtain(self, stateFeatures, api):
        building = 5

        y = random.randint(0, int(api.getGameHeight()))
        x = random.choice(api.getUnOccupied(api.getMyBuildings()[y]))

        return api.createCommand(x,y,building)

    def doNothing(self, stateFeatures, api):
        return api.createDoNothingCommand()

    def isAttacking(self, api, lane_number):
        '''
        Checks a lane.
        Returns True if lane contains my attack unit.

        Should be in API but isn't, so I made it
        '''
        
        lane = list(api.my_buildings[lane_number])
        if (lane.count(1) > 0):
            return True
        else:
            return False

    def computeStateFeatures(self, api):
        stateFeatures = OrderedDict()

        game_state = api.getGameState()

        stateFeatures['round'] = game_state['gameDetails']['round']
        stateFeatures['roundsRemaining'] = game_state['gameDetails']['maxRounds'] - stateFeatures['round']

        player_A_state = api.getMyself()
        player_B_state = api.getOpponent()

        stateFeatures['myHealth'] = player_A_state['health']
        stateFeatures['oppHealth'] = player_B_state['health']
        stateFeatures['myMinusOppHealth'] = player_A_state['health'] - player_B_state['health']
        stateFeatures['myEnergy'] = player_A_state['energy']
        stateFeatures['oppEnergy'] = player_B_state['energy']
        stateFeatures['myMinusOppEnergy'] = player_A_state['energy'] - player_B_state['energy']
        stateFeatures['myMinusOppScore'] = player_A_state['score'] - player_B_state['score']

        stateFeatures['countRowsUnderAttack'] = sum([api.isUnderAttack(i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsUnderAttackUndefended'] = sum([api.isUnderAttack(i) and not api.isDefended(i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsUndefended'] = sum([(not api.isDefended(i)) for i in range(api.getGameHeight())])
        stateFeatures['countRowsAttacking'] = sum([self.isAttacking(api, i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsAttackingUndefended'] = sum([self.isAttacking(api, i) and not api.checkOpponentDefense(i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsUndefended'] = sum([(not api.checkOpponentDefense(i)) for i in range(api.getGameHeight())])

        stateFeatures['myIronCurtainAvailable'] = player_A_state['ironCurtainAvailable']
        stateFeatures['oppIronCurtainAvailable'] = player_B_state['ironCurtainAvailable']
        stateFeatures['myActiveIronCurtainLifetime'] = player_A_state['activeIronCurtainLifetime']
        stateFeatures['oppActiveIronCurtainLifetime'] = player_B_state['activeIronCurtainLifetime']
        stateFeatures['myIronCurtainActive'] = player_A_state['isIronCurtainActive']
        stateFeatures['oppIronCurtainActive'] = player_B_state['isIronCurtainActive']

        my_buildings = api.getMyBuildings()
        opp_buildings = api.getOpponentBuildings()
        stateFeatures['myNumTelsa'] = sum([row_list.count(4) for row_list in my_buildings])
        stateFeatures['oppNumTelsa'] = sum([row_list.count(4) for row_list in opp_buildings])
        stateFeatures['myNumEnergy'] = sum([row_list.count(3) for row_list in my_buildings])
        stateFeatures['oppNumEnergy'] = sum([row_list.count(3) for row_list in opp_buildings])
        stateFeatures['myNumAttack'] = sum([row_list.count(1) for row_list in my_buildings])
        stateFeatures['oppNumAttack'] = sum([row_list.count(1) for row_list in opp_buildings])
        stateFeatures['myNumDefense'] = sum([row_list.count(2) for row_list in my_buildings])
        stateFeatures['oppNumDefense'] = sum([row_list.count(2) for row_list in opp_buildings])

        return stateFeatures

    def computePossibleActiontypes(self, stateFeatures, api):
        possible_action_types = set(range(NUM_ACTION_TYPES))

        # Any buildings to destroy?
        if (
            stateFeatures['myNumTelsa'] + stateFeatures['myNumEnergy'] + stateFeatures['myNumAttack'] + stateFeatures['myNumDefense']
        ) == 0:
            possible_action_types.remove(3)

        # Able to do iron curtain?
        if (~stateFeatures['myIronCurtainAvailable']) | (stateFeatures['myEnergy'] < api.game_state['gameDetails']['ironCurtainStats']['price']):
            possible_action_types.remove(5)

        # Able to do telsa?
        if (stateFeatures['myNumTelsa'] > 2) | (stateFeatures['myEnergy'] < api.buildings_stats['TESLA']['price']):
            possible_action_types.remove(4)

        # Enough energy for attack?
        if (stateFeatures['myEnergy'] < api.buildings_stats['ATTACK']['price']):
            possible_action_types.remove(1)

        # Enough energy for defense?
        if (stateFeatures['myEnergy'] < api.buildings_stats['DEFENSE']['price']):
            possible_action_types.remove(0)

        # Enough energy for defense?
        if (stateFeatures['myEnergy'] < api.buildings_stats['ENERGY']['price']):
            possible_action_types.remove(2)

        return sorted(list(possible_action_types))

    def computeActionTypeProbabilities(self, state_features, api):
        # determine possible actions
        possible_action_types = self.computePossibleActiontypes(state_features, api)
        
        # here is where the network(s) will go
        action_type_probabilities = np.ones(len(possible_action_types))/len(possible_action_types)

        return possible_action_types, action_type_probabilities
        
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
        
        # Compute state features
        state_features = self.computeStateFeatures(api)

        # Convert state features to probability of each action type
        possible_action_types, action_type_probabilities = self.computeActionTypeProbabilities(state_features, api)

        # Randomize to select action type
        action_type_choice = np.random.choice(
            possible_action_types,
            size=1,
            p=action_type_probabilities,
        )[0]

        # Execute and return action type
        do_action_type_method = self.idx2actionType[action_type_choice]

        return do_action_type_method(state_features, api)

if __name__ == '__main__':
    from TowerDefense import *
    #This will load the game state and then call your doTurn function with an 
    #instance of the TowerDefenseApi to use in deciding your strategy for the turn
    TowerDefense.run(ShallowMindBot())
    
