# -*- coding: utf-8 -*-
'''
Entelect StarterBot for Python3
'''
import time

startTime = time.time()

import numpy as np
#from scipy.special import softmax

import json
import os
from time import sleep
import random
from collections import OrderedDict, Set
import pickle

from TowerDefenseApi import *

resume = True
training = False

# hyperparameters to tune
H = 15 # number of hidden layer neurons

NUM_ACTION_TYPES = 7 # defend, attack, energy, destroy, tesla, iron curtain, do nothing

BUILDING_TO_IDX = {
    'tesla': 4,
    'energy': 3,
    'attack': 1,
    'defense': 2,
}

ACTION_TYPE_COMBOS = [
    [6],
    [2,6],
    [0,1,2,6],
    [0,1,2,4,5,6],
    [0,1,2,4,6],
]

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

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

        # model initialization
        D = 28 # input dimensionality
        if resume:
            self.model = pickle.load(open('model_params.p', 'rb'))
        else:
            self.model = {}
            self.model['W1'] = np.random.randn(H,D) / (100*np.sqrt(D)) # "Xavier" initialization - Shape will be H x D
            self.model['W2'] = np.random.randn(NUM_ACTION_TYPES,H) / (100*np.sqrt(H)) # Shape will be H

    def policy_forward(self, stateFeatures, action_type_combo):
        """This is a manual implementation of a forward prop"""
        x = np.array([float(val) for val in stateFeatures.values()])
        h = np.dot(self.model['W1'], x) # (H x D) . (D x 1) = (H x 1) (200 x 1)
        h[h<0] = 0 # ReLU introduces non-linearity
        logp = np.dot(self.model['W2'], h) # This is a logits function and outputs a decimal.   (1 x H) . (H x 1) = 1 (scalar)
        logp = logp[action_type_combo]
        p = softmax(logp)  # squashes output to  between 0 & 1 range
        return p, h # return probability of taking action, and hidden state
    
    def find_x_y(self, api, rows, col_choice=max):
        # Any openings in rows?
        openings_in_rows = False
        for row in rows:
            if len(api.getUnOccupied(api.getMyBuildings()[row])) > 0:
                openings_in_rows = True
                break
        
        found_x_y = False

        while not found_x_y:
            if openings_in_rows:
                y = random.choice(rows)
            else:
                y = random.randint(0, int(api.getGameHeight()-1))
            
            try:
                x = col_choice(api.getUnOccupied(api.getMyBuildings()[y]))
                found_x_y = True
            except:
                pass

        return x, y
    
    def doDefense(self, stateFeatures, api):
        building = 0

        # put as close to the front as possible (max x)
        rand_num = random.random()
        if rand_num < 0.33:
            # put in front of other buildings if possible
            rows_w_my_other_buildings = self.getLanesWithMyBuilding(api, BUILDING_TO_IDX['attack'])
            rows_w_my_other_buildings.extend(self.getLanesWithMyBuilding(api, BUILDING_TO_IDX['energy']))
            
            x, y = self.find_x_y(api, rows_w_my_other_buildings, max)
        else:
            # block row where under attack
            rows_w_opp_attacking = self.getLanesWithOppBuilding(api, BUILDING_TO_IDX['attack'])
            
            x, y = self.find_x_y(api, rows_w_opp_attacking, max)

        return api.createCommand(x,y,building)

    def doAttack(self, stateFeatures, api):
        building = 1

        # If row has Tesla, attack it
        if stateFeatures['oppNumTesla'] > 0:
            rows_with_tesla = self.getLanesWithOppBuilding(api, BUILDING_TO_IDX['tesla'])
            
            x, y = self.find_x_y(api, rows_with_tesla, min)

        # Randomly pick between these more offensive and defensive attacks
        rand_num = random.random()
        if rand_num < 0.33:
            # If under attack from row, attack it
            rows_under_attack = self.getLanesWithOppBuilding(api, BUILDING_TO_IDX['attack'])
            x, y = self.find_x_y(api, rows_under_attack, min)
        elif rand_num < 0.66:
            # If row undefended by opponent, attack it
            rows_defended = self.getLanesWithOppBuilding(api, BUILDING_TO_IDX['defense'])
            rows_undefended = [row for row in range(int(api.getGameHeight()-1)) if row not in rows_defended]
            x, y = self.find_x_y(api, rows_undefended, min)
        else:
            # If energy in row, attack it
            rows_with_energy = self.getLanesWithOppBuilding(api, BUILDING_TO_IDX['energy'])
            x, y = self.find_x_y(api, rows_with_energy, min)

        return api.createCommand(x,y,building)

    def doEnergy(self, stateFeatures, api):
        building = 2

        # place as far back as possible, and behind defense if possible
        rows_with_defense = self.getLanesWithMyBuilding(api, BUILDING_TO_IDX['defense'])
        x, y = self.find_x_y(api, rows_with_defense, min)

        return api.createCommand(x,y,building)

    def doDestroy(self, stateFeatures, api):
        building = 3

        buildings_row_col_list = [(y_row, x_col) for x_col in range(int(api.getGameWidth()/2)) for y_row in range(int(api.getGameHeight()-1)) if api.getMyBuildings()[y_row][x_col]>0]

        try: 
            y, x = random.choice(buildings_row_col_list)
        except:
            return api.createDoNothingCommand()

        return api.createCommand(x,y,building)

    def max_behind(self, unocc_cols, num_cols=8):
        if len(unocc_cols)==0:
            raise ValueError
        else:
            occ_cols = [col for col in range(num_cols) if col not in unocc_cols]
            col_choice = max([unocc_col for unocc_col in unocc_cols if unocc_col<max(occ_cols)])
            return col_choice
    
    def doTesla(self, stateFeatures, api):
        building = 4
        
        # go as close to the front as possible, while being behind defense
        rows_with_defense = self.getLanesWithMyBuilding(api, BUILDING_TO_IDX['defense'])
        x, y = self.find_x_y(api, rows_with_defense, self.max_behind)

        return api.createCommand(x,y,building)

    def doIronCurtain(self, stateFeatures, api):
        building = 5

        y = random.randint(0, int(api.getGameHeight()-1))
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

    def checkLaneForOppBuilding(self, api, lane_number, building_number):
        '''
        Checks a lane.
        Returns True if lane contains building number
        '''
        
        lane = list(api.opponent_buildings[lane_number])
        if (lane.count(building_number) > 0):
            return True
        else:
            return False

    def checkLaneForMyBuilding(self, api, lane_number, building_number):
        '''
        Checks a lane.
        Returns True if lane contains building number
        '''
        
        lane = list(api.my_buildings[lane_number])
        if (lane.count(building_number) > 0):
            return True
        else:
            return False

    def getLanesWithOppBuilding(self, api, building_number):
        rows = []
        for row in range(int(api.getGameHeight()-1)):
            if self.checkLaneForOppBuilding(api, row, building_number):
                rows.append(row)
        return rows

    def getLanesWithMyBuilding(self, api, building_number):
        rows = []
        for row in range(int(api.getGameHeight()-1)):
            if self.checkLaneForMyBuilding(api, row, building_number):
                rows.append(row)
        return rows

    def computeStateFeatures(self, api):
        stateFeatures = OrderedDict()

        game_state = api.getGameState()

        # 2 features
        stateFeatures['round'] = game_state['gameDetails']['round']
        stateFeatures['roundsRemaining'] = game_state['gameDetails']['maxRounds'] - stateFeatures['round']

        player_A_state = api.getMyself()
        player_B_state = api.getOpponent()

        # 7 features
        stateFeatures['myHealth'] = player_A_state['health']
        stateFeatures['oppHealth'] = player_B_state['health']
        stateFeatures['myMinusOppHealth'] = player_A_state['health'] - player_B_state['health']
        stateFeatures['myEnergy'] = player_A_state['energy']
        stateFeatures['oppEnergy'] = player_B_state['energy']
        stateFeatures['myMinusOppEnergy'] = player_A_state['energy'] - player_B_state['energy']
        stateFeatures['myMinusOppScore'] = player_A_state['score'] - player_B_state['score']

        # 6 features
        stateFeatures['countRowsUnderAttack'] = sum([api.isUnderAttack(i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsUnderAttackUndefended'] = sum([api.isUnderAttack(i) and not api.isDefended(i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsUndefended'] = sum([(not api.isDefended(i)) for i in range(api.getGameHeight())])
        stateFeatures['countRowsAttacking'] = sum([self.isAttacking(api, i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsAttackingUndefended'] = sum([self.isAttacking(api, i) and not api.checkOpponentDefense(i) for i in range(api.getGameHeight())])
        stateFeatures['countRowsUndefended'] = sum([(not api.checkOpponentDefense(i)) for i in range(api.getGameHeight())])

        # 6 features
        stateFeatures['myIronCurtainAvailable'] = player_A_state['ironCurtainAvailable']
        stateFeatures['oppIronCurtainAvailable'] = player_B_state['ironCurtainAvailable']
        stateFeatures['myActiveIronCurtainLifetime'] = player_A_state['activeIronCurtainLifetime']
        stateFeatures['oppActiveIronCurtainLifetime'] = player_B_state['activeIronCurtainLifetime']
        stateFeatures['myIronCurtainActive'] = player_A_state['isIronCurtainActive']
        stateFeatures['oppIronCurtainActive'] = player_B_state['isIronCurtainActive']

        my_buildings = api.getMyBuildings()
        opp_buildings = api.getOpponentBuildings()
        # 8 features
        stateFeatures['myNumTesla'] = sum([row_list.count(4) for row_list in my_buildings])
        stateFeatures['oppNumTesla'] = sum([row_list.count(4) for row_list in opp_buildings])
        stateFeatures['myNumEnergy'] = sum([row_list.count(3) for row_list in my_buildings])
        stateFeatures['oppNumEnergy'] = sum([row_list.count(3) for row_list in opp_buildings])
        stateFeatures['myNumAttack'] = sum([row_list.count(1) for row_list in my_buildings])
        stateFeatures['oppNumAttack'] = sum([row_list.count(1) for row_list in opp_buildings])
        stateFeatures['myNumDefense'] = sum([row_list.count(2) for row_list in my_buildings])
        stateFeatures['oppNumDefense'] = sum([row_list.count(2) for row_list in opp_buildings])

        return stateFeatures

    def computePossibleActiontypes(self, stateFeatures, api):
        possible_action_types = set(range(NUM_ACTION_TYPES))

        # Many buildings to destroy?
        # if (
        #     stateFeatures['myNumTesla'] + stateFeatures['myNumEnergy'] + stateFeatures['myNumAttack'] + stateFeatures['myNumDefense']
        # ) < 20:
        possible_action_types.remove(3)

        # Able to do iron curtain?
        if (~stateFeatures['myIronCurtainAvailable']) | (stateFeatures['myEnergy'] < api.game_state['gameDetails']['ironCurtainStats']['price']):
            possible_action_types.remove(5)

        # Able to do Tesla?
        if (stateFeatures['myNumTesla'] > 2) | (stateFeatures['myEnergy'] < api.buildings_stats['TESLA']['price']):
            possible_action_types.remove(4)

        # Enough energy for attack?
        if (stateFeatures['myEnergy'] < api.buildings_stats['ATTACK']['price']):
            possible_action_types.remove(1)

        # Enough energy for defense?
        if (stateFeatures['myEnergy'] < api.buildings_stats['DEFENSE']['price']):
            possible_action_types.remove(0)

        # Enough energy for energy?
        if (stateFeatures['myEnergy'] < api.buildings_stats['ENERGY']['price']):
            possible_action_types.remove(2)

        return sorted(list(possible_action_types))

    def computeActionTypeProbabilities(self, state_features, api):
        # determine possible actions
        possible_action_types = self.computePossibleActiontypes(state_features, api)
        
        action_type_probabilities, hidden_layer = self.policy_forward(state_features, possible_action_types)
        
        return possible_action_types, action_type_probabilities, hidden_layer
        
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
        possible_action_types, action_type_probabilities, hidden_layer = self.computeActionTypeProbabilities(state_features, api)

        # Randomize to select action type
        action_type_choice = random.choices(
            population=possible_action_types,
            k=1,
            weights=action_type_probabilities,
        )[0]

        print('Selected action type {} from options {} with probabilities {}'.format(action_type_choice, possible_action_types, action_type_probabilities))

        # Record things when training
        if training:
            try:
                max_game = max([int(d.split('_')[1]) for d in os.listdir(os.path.join('.','logs')) if os.path.isdir(os.path.join('.','logs',d))])
            except ValueError:
                max_game = -1

            if state_features['round'] == 0:
                game_num = max_game + 1
                os.makedirs(os.path.join('.','logs','game_{}'.format(game_num)))
            else:
                game_num = max_game
            
            # Store results of this step
            with open(os.path.join('.','logs','game_{}'.format(game_num),'round_{}.pkl'.format(state_features['round'])), 'wb') as f:
                pickle.dump((state_features, possible_action_types, action_type_probabilities, hidden_layer, action_type_choice),f)
        
        # Execute and return action type
        do_action_type_method = self.idx2actionType[action_type_choice]

        command = do_action_type_method(state_features, api)

        return command

if __name__ == '__main__':
    from TowerDefense import *
    #This will load the game state and then call your doTurn function with an 
    #instance of the TowerDefenseApi to use in deciding your strategy for the turn
    TowerDefense.run(ShallowMindBot())