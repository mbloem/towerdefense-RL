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


    
    
class TowerDefenseApi:
    
    def __init__(self, loadedGameState):
        
        self.game_state = loadedGameState
        self.full_map = self.game_state['gameMap']
        self.rows = self.game_state['gameDetails']['mapHeight']
        self.columns = self.game_state['gameDetails']['mapWidth']
        self.command = ''
        
        self.my_buildings = self.getMyBuildings()
        self.opponent_buildings = self.getOpponentBuildings()
        self.missiles = self.getMissiles()
               
        self.myself = self.getPlayerInfo('A')
        self.opponent = self.getPlayerInfo('B')
        
        self.round = self.game_state['gameDetails']['round']
        
        self.iron_curtain_stats = self.game_state['gameDetails']['ironCurtainStats']
        
        self.buildings_stats = {"ATTACK":{"health": self.game_state['gameDetails']['buildingsStats']['ATTACK']['health'],
                                 "constructionTime": self.game_state['gameDetails']['buildingsStats']['ATTACK']['constructionTime'],
                                 "price": self.game_state['gameDetails']['buildingsStats']['ATTACK']['price'],
                                 "weaponDamage": self.game_state['gameDetails']['buildingsStats']['ATTACK']['weaponDamage'],
                                 "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['ATTACK']['weaponSpeed'],
                                 "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['ATTACK']['weaponCooldownPeriod'],
                                 "energyGeneratedPerTurn": self.game_state['gameDetails']['buildingsStats']['ATTACK']['energyGeneratedPerTurn'],
                                 "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['ATTACK']['destroyMultiplier'],
                                 "constructionScore": self.game_state['gameDetails']['buildingsStats']['ATTACK']['constructionScore']},
                       "DEFENSE":{"health": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['health'],
                                 "constructionTime": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['constructionTime'],
                                 "price": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['price'],
                                 "weaponDamage": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['weaponDamage'],
                                 "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['weaponSpeed'],
                                 "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['weaponCooldownPeriod'],
                                 "energyGeneratedPerTurn": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['energyGeneratedPerTurn'],
                                 "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['destroyMultiplier'],
                                 "constructionScore": self.game_state['gameDetails']['buildingsStats']['DEFENSE']['constructionScore']},
                       "ENERGY":{"health": self.game_state['gameDetails']['buildingsStats']['ENERGY']['health'],
                                 "constructionTime": self.game_state['gameDetails']['buildingsStats']['ENERGY']['constructionTime'],
                                 "price": self.game_state['gameDetails']['buildingsStats']['ENERGY']['price'],
                                 "weaponDamage": self.game_state['gameDetails']['buildingsStats']['ENERGY']['weaponDamage'],
                                 "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['ENERGY']['weaponSpeed'],
                                 "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['ENERGY']['weaponCooldownPeriod'],
                                 "energyGeneratedPerTurn": self.game_state['gameDetails']['buildingsStats']['ENERGY']['energyGeneratedPerTurn'],
                                 "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['ENERGY']['destroyMultiplier'],
                                 "constructionScore": self.game_state['gameDetails']['buildingsStats']['ENERGY']['constructionScore']},
                       "TESLA":{"health": self.game_state['gameDetails']['buildingsStats']['TESLA']['health'],
                                 "constructionTime": self.game_state['gameDetails']['buildingsStats']['TESLA']['constructionTime'],
                                 "price": self.game_state['gameDetails']['buildingsStats']['TESLA']['price'],
                                 "weaponDamage": self.game_state['gameDetails']['buildingsStats']['TESLA']['weaponDamage'],
                                 "weaponSpeed": self.game_state['gameDetails']['buildingsStats']['TESLA']['weaponSpeed'],
                                 "weaponCooldownPeriod": self.game_state['gameDetails']['buildingsStats']['TESLA']['weaponCooldownPeriod'],
                                 "energyGeneratedPerTurn": self.game_state['gameDetails']['buildingsStats']['TESLA']['energyGeneratedPerTurn'],
                                 "destroyMultiplier": self.game_state['gameDetails']['buildingsStats']['TESLA']['destroyMultiplier'],
                                 "constructionScore": self.game_state['gameDetails']['buildingsStats']['TESLA']['constructionScore']}}
                        
        return None
        
        
    
    def getGameState(self):
        return self.game_state
    
    def getGameWidth(self):
        return self.columns
    
    def getGameHeight(self):
        return self.rows
    
    def getBuildingsStats(self):
        return self.buildings_stats
        
    def getMyself(self):
        return self.getPlayerInfo('A')
    
    def getOpponent(self):
        return self.getPlayerInfo('B')

    def getPlayerInfo(self,playerType):
        '''
        Gets the player information of specified player type
        '''
        for i in range(len(self.game_state['players'])):
            if self.game_state['players'][i]['playerType'] == playerType:
                return self.game_state['players'][i]
            else:
                continue        
        return None
    
    def getOpponentBuildings(self):
        '''
        Looks for all buildings, regardless if completed or not.
        Note: the 2 dimensional array is [rows][cols] which would by y,x if you are looking for
        something at a specific location.
        
        0 - Nothing
        1 - Attack Unit
        2 - Defense Unit
        3 - Energy Unit
        4 - Tesla tower
        '''
        opponent_buildings = []
        
        for row in range(0,self.rows):
            buildings = []
            for col in range(int(self.columns/2),self.columns):
                if (len(self.full_map[row][col]['buildings']) == 0):
                    buildings.append(0)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'ATTACK'):
                    buildings.append(1)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'DEFENSE'):
                    buildings.append(2)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'ENERGY'):
                    buildings.append(3)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'TESLA'):
                    buildings.append(4)
                else:
                    buildings.append(0)
                
            opponent_buildings.append(buildings)
            
        return opponent_buildings
    
    def getMyBuildings(self):
        '''
        Looks for all buildings, regardless if completed or not. 
        Note: the 2 dimensional array is [rows][cols] which would by y,x if you are looking for
        something at a specific location.
        
        0 - Nothing
        1 - Attack Unit
        2 - Defense Unit
        3 - Energy Unit
        4 - Tesla tower
        '''
        player_buildings = []
        
        for row in range(0,self.rows):
            buildings = []
            for col in range(0,int(self.columns/2)):
                if (len(self.full_map[row][col]['buildings']) == 0):
                    buildings.append(0)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'ATTACK'):
                    buildings.append(1)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'DEFENSE'):
                    buildings.append(2)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'ENERGY'):
                    buildings.append(3)
                elif (self.full_map[row][col]['buildings'][0]['buildingType'] == 'TESLA'):
                    buildings.append(4)
                else:
                    buildings.append(0)
                 
            player_buildings.append(buildings)
            
        return player_buildings
    
    def getMissiles(self):
        '''
        Find all missiles on the map.
        0 - Nothing there
        1 - missiles belongs to player
        2 - missiles belongs to opponent
        '''
        projectiles = []
        
        for row in range(0,self.rows):
            temp = []
            for col in range(0,self.columns):
                if (len(self.full_map[row][col]['missiles']) == 0):
                    temp.append(0)
                elif (self.full_map[row][col]['missiles'][0]['playerType'] == 'A'):
                    temp.append(1)
                elif (self.full_map[row][col]['missiles'][0]['playerType'] == 'B'):
                    temp.append(2)
                
            projectiles.append(temp)
            
        return projectiles
    

    def checkOpponentDefense(self, lane_number):

        '''
        Checks a lane.
        Returns True if lane contains defense unit.
        '''
        
        lane = list(self.opponent_buildings[lane_number])
        if (lane.count(2) > 0):
            return True
        else:
            return False

    def isDefended(self, lane_number):

        '''
        Checks a lane.
        Returns True if lane contains defense unit.
        '''
        
        lane = list(self.my_buildings[lane_number])
        if (lane.count(2) > 0):
            return True
        else:
            return False
    
    def isUnderAttack(self, lane_number):

        '''
        Checks a lane.
        Returns True if lane contains attack unit.
        '''
        
        lane = list(self.opponent_buildings[lane_number])
        if (lane.count(1) > 0):
            return True
        else:
            return False
    
    def getUnOccupied(self,lane):
        '''
        Returns index of all unoccupied cells in a lane
        '''
        indexes = []
        for i in range(len(lane)):
            if lane[i] == 0 :
                indexes.append(i)
        
        return indexes
  
    
    def createCommand(self,col,row,building):
        '''
        Returns a string with the x,y, and building
        '''
        return ','.join([str(col),str(row),str(building)])       
        
    def createDoNothingCommand(self):
        return ""
        
        
    