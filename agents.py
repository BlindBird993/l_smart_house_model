from mesa import Agent, Model
import random
import getDataFromExcel as data
import numpy as np
import scipy.stats as sts

WIND_DATA = data.getData()

class SolarPanelAgent(Agent):
    def __init__(self,unique_id, model,solarPanel):
        super().__init__(unique_id, model)

        self.solarPanel = solarPanel
        self.energy = 0
        self.readyToSell = True
        self.traided = None
        self.currentDemand = 0

        self.priceHistory = []
        self.quantityHistorySell = []

        self.hour = 0
        self.day = 0
        self.week = 0

    def calculatePrice(self):
        if self.readyToSell:
            self.price = round(random.uniform(1.9,0.3),2)
        else:
            self.price = 0#price for KWh, NOK
        print("Price {}".format(self.price))

    def checkSolarEnergy(self):
        self.energy = self.solarPanel.amountOfEnergyGenerated
        print("Amount of Solar energy {}".format(self.solarPanel.amountOfEnergyGenerated))

    def checkStatus(self):
        if self.energy > 0:
            self.readyToSell = True
        else:
            self.readyToSell = False

    def test_func(self):
        print("Seller agent {0}".format(self.unique_id))

    def step(self):
        self.checkSolarEnergy()
        self.checkStatus()
        self.calculatePrice()
        self.traided = False
        print("Ready to Sell {}".format(self.readyToSell))

        self.hour +=1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class WindEnergyAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)
        self.hour = 0
        self.day = 0
        self.week = 0

        self.energy = 0
        self.readyToSell = True
        self.traided = False
        self.currentDemand = 0

        self.priceHistory = []
        self.quantityHistorySell = []
        self.test_list = []

    def calculatePrice(self):
        if self.readyToSell:
            self.price = round(random.uniform(1.9,0.3),1)
        else:
            self.price = 0.0#price for KWh, NOK
        print("Price {}".format(self.price))

    def checkStatus(self):
        if self.energy > 0:
            self.readyToSell = True
        else:
            self.readyToSell = False
        print("Ready to Sell {}".format(self.readyToSell))

    def getWindData(self):
        windList = WIND_DATA
        self.energy = np.random.choice(windList)

    def step(self):
        self.getWindData()
        print("Wind energy {}".format(self.energy))
        self.checkStatus()
        self.calculatePrice()
        self.traided = False

        self.hour +=1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class HeatedFloorAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)

        self.isInRoom = None
        self.readyToBuy = True
        self.traided = False
        self.energy = 0

        self.hour = 0
        self.day = 0
        self.week = 0
        self.currentDemand = 0 #0.8 Kwh for average bathroom
        self.price = 0
        self.initialDemand = 0

    def calculatePrice(self):
        self.price = round(random.uniform(1.9,0.3),2) #price for KWh, NOK
        print("Price {}".format(self.price))

    def calculateDemand(self):
        if self.isInRoom:
            self.calculatePrice()
            self.currentDemand = 0.8
            self.readyToBuy = True
        else:
            self.currentDemand = 0
            self.readyToBuy = False
        print("Heated floor demand {}".format(self.currentDemand))

    def checkIfisInRoom(self):
        if self.hour >= 0 and self.hour < 7:
            self.isInRoom = np.random.choice(
                [True,False],
                1,
                p=[0.9, 0.1,])[0]
        elif self.hour > 7 and self.hour <= 16:
            if self.day < 5:
                self.isInRoom = np.random.choice(
                    [True, False],
                    1,
                    p=[0.1, 0.9])[0]
            else:
                self.isInRoom = np.random.choice(
                    [True, False],
                    1,
                    p=[0.6, 0.4])[0]
        elif self.hour >= 17 and self.hour <= 21:
            self.isInRoom = np.random.choice(
                [True, False],
                1,
                p=[0.7, 0.3])[0]

        elif self.hour >= 22 and self.hour <= 23:
            self.isInRoom = np.random.choice(
                [True, False],
                1,
                p=[0.9, 0.1])[0]
        print("Person is in home {}".format(self.isInRoom))

    def name_func(self):
        print("Agent {}".format(self.unique_id))

    def step(self):
        self.name_func()
        self.traided = False
        self.checkIfisInRoom()
        self.calculateDemand()
        self.hour +=1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class TradeInterface(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)

        self.buyers = []
        self.sellers = []
        self.demands = []
        self.productions = []
        self.demandPrice = []
        self.supplyPrice = []
        self.clearPrice = 0
        self.surplus = 0

        self.demandHistory = []

        self.distributedDemands = []
        self.boughtFromTheGrid = []

        self.totalSupply = 0
        self.totalDemand = 0

        self.numberOfBuyers = 0
        self.numberOfSellers = 0

        self.satisfiedDemands = []
        self.demandCount = 0
        self.stepCount = 0

    def getSellers(self):
        self.sellers = []
        supplyValue = 0.0
        self.numberOfSellers = 0
        for agent in self.model.schedule.agents:
            if (isinstance(agent, SolarPanelAgent) or isinstance(agent,StorageAgent )or isinstance(agent,WindEnergyAgent)):
                if agent.readyToSell is True:
                    self.numberOfSellers += 1
                    self.sellers.append(agent.unique_id)
                    supplyValue = round(supplyValue + agent.energy, 3)
        self.productions.append(supplyValue)
        print("Sellers {}".format(self.sellers))
        print("Number of sellers {}".format(self.numberOfSellers))

    def getBuyres(self):
        self.buyers = []
        demandValue = 0.0
        self.numberOfBuyers = 0
        for agent in self.model.schedule.agents:
            if (isinstance(agent, HeaterAgent) or isinstance(agent,LightAgent) or isinstance(agent,StorageAgent) or isinstance(agent,HeatedFloorAgent)):
                if agent.readyToBuy is True:
                    self.numberOfBuyers += 1
                    self.buyers.append(agent.unique_id)
                    demandValue = round(demandValue + agent.currentDemand, 3)
        self.demands.append(demandValue)
        print("Buyers {}".format(self.buyers))
        print("Number of buyers {}".format(self.numberOfBuyers))

    def chooseSeller(self,buyer,price,amount):
        seller = np.random.choice(self.sellers) #choose seller randomly
        for agent in self.model.schedule.agents:
            if (isinstance(agent, SolarPanelAgent) or isinstance(agent,StorageAgent) or isinstance(agent,WindEnergyAgent)):
                if agent.readyToSell is True and agent.unique_id == seller and agent.traided is False:
                    print("Seller {}".format(agent.unique_id))
                    print("Seller price {}".format(agent.price))
                    print("Seller energy {}".format(agent.energy))

                    if buyer.price >= agent.price:
                        print("Deal !")
                        amount = min(agent.energy,buyer.currentDemand)
                        print("Demand value {}".format(amount))
                        if buyer.currentDemand > amount:
                            buyer.currentDemand = round(buyer.currentDemand-agent.energy,3)

                            self.demandHistory.append(buyer.currentDemand)

                            self.demandCount += agent.energy
                            self.demandCount = round(self.demandCount,3)

                            buyer.energy += agent.energy
                            agent.energy = 0
                            agent.traided = True
                            agent.readyToSell = False
                            agent.priceHistory.append(agent.price)
                            self.numberOfSellers -= 1
                            self.sellers.remove(agent.unique_id)
                            print("Number of sellers {}".format(self.numberOfSellers))

                        elif buyer.currentDemand <= amount:
                            agent.energy = round(agent.energy-buyer.currentDemand,3)
                            buyer.energy += buyer.currentDemand

                            self.demandCount += buyer.currentDemand
                            self.demandCount = round(self.demandCount,3)

                            buyer.currentDemand = 0.0
                            buyer.traided = True
                            buyer.readyToBuy = False
                            self.numberOfBuyers -= 1
                            self.buyers.remove(buyer.unique_id)

                            if agent.energy > 0:
                                agent.price = round(np.mean([agent.price, buyer.price]), 1)
                            else:
                                agent.traided = True
                                self.numberOfSellers -= 1
                        print("Buyer demand {}".format(buyer.currentDemand))
                        print("Buyer status {}".format(buyer.traided))
                        print("Remaining amount of energy {}".format(agent.energy))

                        print("Number of sellers {}".format(self.numberOfSellers))
                        print("Number of buyers {}".format(self.numberOfBuyers))
                    else:
                        print('No deal')
                        agent.price = round(np.mean([agent.price, buyer.price]),1)
                        buyer.calculatePrice()

    def buyFromGrid(self,buyer):
        gridPrice = 0

        for agent in self.model.schedule.agents:
            if (isinstance(agent, SmartGridAgent)):
                gridPrice = agent.price
        print("Buyer {}".format(buyer.unique_id))
        print("Buyer price {}".format(buyer.price))
        if buyer.price >= gridPrice:
            print("Trade with Grid")
            buyer.energy += buyer.currentDemand
            print("Bought form Grid {}".format(buyer.currentDemand))

            self.demandHistory.append(buyer.currentDemand)
            buyer.currentDemand = 0

        else:
            print("No trade, bought for max price")
            buyer.energy += buyer.currentDemand
            print("Bought form Grid {}".format(buyer.currentDemand))
            buyer.currentDemand = 0

    def distributeEnergy(self):
        self.test_list = []
        self.sellPrice = 0
        self.buyPrice = 0
        self.demandCount = 0.0
        while(not(self.numberOfSellers <= 0 or self.numberOfBuyers <= 0)):
            buyer_id = np.random.choice(self.buyers)#random buyers
            print("Buyer Random ID {}".format(buyer_id))
            for agent in self.model.schedule.agents:
                if (isinstance(agent, HeaterAgent) or isinstance(agent,LightAgent)or isinstance(agent,StorageAgent)or isinstance(agent,HeatedFloorAgent)):
                    if agent.readyToBuy is True and agent.traided is False:
                        if agent.unique_id == buyer_id:
                            self.buyPrice = agent.price
                            print("Buyer {}".format(agent.unique_id))
                            print("Buy price {}".format(agent.price))
                            print("Buyer demand {}".format(agent.currentDemand))
                            self.chooseSeller(agent,self.buyPrice,agent.currentDemand)

        if self.numberOfBuyers > 0 and self.numberOfSellers == 0:
            print("Not enough energy, need to buy from grid")
            #check buyers, buy from grid
            for agent in self.model.schedule.agents:
                if isinstance(agent, HeaterAgent) and agent.stateChoice == 'stay':
                    reward = 2.0#reward agents which choose to stay
                    agent.updateStates(reward)  # updates states propensities
                    agent.updateStateProbabilities()  # updates states probabilities

                    if agent.readyToBuy is True and agent.traided is False:
                        self.buyFromGrid(agent)

                if (isinstance(agent, HeaterAgent)):
                    #evaluate rewards
                    print("Agent {} Demand difference {}".format(agent.unique_id,(agent.desiredTemp - agent.currentTemp)))
                    print("Agent State {}, Agent Choice {}".format(agent.currentState,agent.stateChoice))

                    temperatureRange = agent.tempRange
                    print("Temperature range {}".format(temperatureRange))
                    desiredTemperature = agent.desiredTemp
                    maxTemp = max(agent.tempRange)
                    print("max temp {}".format(maxTemp))
                    print("temp choice {}".format(agent.desiredTemp))
                    minTemp = min(agent.tempRange)

                    normReward = ((maxTemp-desiredTemperature)/maxTemp)*10
                    if normReward < 2 and normReward > 0:
                        normReward = 2-normReward
                        print("Norm reward {}".format(normReward))
                    elif normReward < 0:
                        normReward = 0.0
                    if agent.stateChoice == 'min':
                        normReward += 2.0

                    reward = round(1 * normReward, 3)

                    print("Reward {}".format(reward))
                    print("Agent {}".format(agent.unique_id))
                    print("Agent reward {}".format(reward))
                    print("Agent old states {}".format(agent.states))

                    agent.updateStates(reward) #updates states propensities
                    agent.updateStateProbabilities() #updates states probabilities

        elif self.numberOfBuyers == 0 and self.numberOfSellers > 0:
            print("Energy left")
            for agent in self.model.schedule.agents:
                if (isinstance(agent, HeaterAgent) and agent.traided is True):
                    print("Agent State {}, Agent Choice {}".format(agent.currentState, agent.stateChoice))
                    print("Agent {}".format(agent.unique_id))
                    print("Agent old states {}".format(agent.states))

                    maxTemp = agent.desiredTemp
                    temperatureRange = agent.tempRange
                    print("Temperature range {}".format(temperatureRange))
                    test_Reward = (maxTemp-min(temperatureRange))/max(temperatureRange)*10

                    print("max temp {}".format(maxTemp))
                    minTemp = min(temperatureRange)
                    normReward = ((maxTemp - minTemp) / maxTemp)*10
                    if normReward < 0:
                        normReward = 0.0
                    if agent.stateChoice == 'ideal':
                        normReward += 2.0
                    print("Norm reward {}".format(normReward))

                    reward = round(1*normReward,3)

                    print("Reward {}".format(reward))
                    agent.updateStates(reward) #reward
                    agent.updateStateProbabilities()

            self.surplus = 0
            for agent in self.model.schedule.agents:  # check if renewable energy left
                if (isinstance(agent, SolarPanelAgent) or isinstance(agent, WindEnergyAgent)):
                    print("Renewable energy {}".format(agent.energy))
                    print("Ready to sell {}".format(agent.readyToSell))
                    if agent.energy > 0:
                        self.surplus += agent.energy
                        agent.energy = 0

            if self.surplus > 0:
                print("Surplus {}".format(self.surplus)) #possible sell to grid
                for agent in self.model.schedule.agents:
                    if (isinstance(agent, StorageAgent)):
                        print("Stored energy left {}".format(agent.energy))
                        energySurplus = agent.addEnergy(self.surplus)
                        print("Energy in storage {}".format(agent.energy))
                        print("Surplus which can be sold {}".format(energySurplus))
                        print("Sold to Grid {} NOK".format(self.sellToGrid(energySurplus)))
        else:
            print("No sellers and No buyers")
            for agent in self.model.schedule.agents:
                if (isinstance(agent, HeaterAgent) and agent.traided is True):
                    print("Agent State {}, Agent Choice {}".format(agent.currentState, agent.stateChoice))
                    print("Agent {}".format(agent.unique_id))
                    print("Agent old states {}".format(agent.states))
                    agent.updateStates(8.0)  #max reward
                    agent.updateStateProbabilities()

    def sellToGrid(self,amount):
        gridPrice = 0
        for agent in self.model.schedule.agents:
            if (isinstance(agent, SmartGridAgent)):
                gridPrice = agent.price
        profit = amount*gridPrice
        return profit


    def step(self):
        print("Trade")
        self.getBuyres()
        self.getSellers()
        self.distributeEnergy()
        self.stepCount += 1

class SmartGridAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)

        self.price = 0
        self.tariffCoef = 1

        self.hour = 0
        self.day = 0
        self.week = 0

    def checkTariff(self):
        if self.hour >= 0 and self.hour < 7:
            self.tariffCoef = 0.6

        elif self.hour >= 7 and self.hour <= 10:
            self.tariffCoef = 1.5

        elif self.hour >= 12 and self.hour <= 14:
            self.tariffCoef = 1.9

        elif self.hour >= 18 and self.hour <= 20:
            self.tariffCoef = 1.5

        elif self.hour >= 23:
            self.tariffCoef = 0.5
        else:
            self.tariffCoef = 1
        print("Grid Tariff {}".format(self.tariffCoef))

    def calculatePrice(self):
        self.price = 4*self.tariffCoef
        print("Grid Price {}".format(self.price))

    def test_func(self):
        print("Smart Grid agent {0}".format(self.unique_id))

    def step(self):
        self.checkTariff()
        self.calculatePrice()
        self.hour +=1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class StorageAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)

        self.amperHour = 500
        self.voltage = 24
        self.wCapacity = (self.amperHour*self.voltage)/1000

        self.capacity = self.wCapacity
        self.energy = 12.0
        self.price = 0
        self.initialDemand = 0

        self.readyToSell = True
        self.readyToBuy = False
        self.traided = False

        self.currentDemand = 0
        self.status = None
        self.criticalBuyAmount = 0

        self.hour = 0
        self.day = 0
        self.week = 0

    def calculateDemand(self):
        if self.status == 'max' or self.status == 'stable':
            self.currentDemand = 0
        else:
            self.currentDemand = np.random.choice([(self.capacity / 2) - self.energy, (self.capacity - self.energy)])
            self.currentDemand = round(self.currentDemand, 3)
        print("Energy demand {}".format(self.currentDemand))

    def checkBatteryCondition(self):
        if self.energy >= 12.0:
            self.energy = 12.0
        if 12.0 >= self.energy >= 10.0:
            print("Maximum output, discharge disarable")
            self.status = 'max'
        elif self.energy < 10.0 and self.energy >= 6.0:
            print("Stable with slow discharge")
            self.status = 'stable'
        else:
            self.status = 'unstable'
            print("Unstable state, discharge not desirable, needs charging")

    def calculatePrice(self):
        self.price = round(random.uniform(1.9, 0.3), 1)  # price for KWh, NOK
        print("Price {}".format(self.price))

    def addEnergy(self, energy):
        if (energy + self.energy >= self.capacity):
            print("Possible overcharging")
            surplus = ((self.energy + energy) - self.capacity)
            self.energy += (energy - ((self.energy + energy) - self.capacity))
            self.energy = round(self.energy, 3)
            print("Energy level {}".format(self.energy))
        elif energy + self.energy < self.capacity:
            self.energy += energy
            self.energy = round(self.energy, 3)
            surplus = 0
            print("Energy level {}".format(self.energy))
        surplus = round(surplus, 3)
        return surplus

    def getStatus(self):
        print("Status {}".format(self.status))

    def checkStatus(self):
        if self.status == 'max' or self.status == 'stable':
            self.readyToSell = True
            self.readyToBuy = False
        else:
            self.readyToSell = False
            self.readyToBuy = True
        print("Available energy {}".format(self.energy))

    def name_func(self):
        print("Agent {0}".format(self.unique_id))

    def step(self):
        self.name_func()
        self.checkBatteryCondition()
        self.getStatus()
        self.checkStatus()
        self.calculateDemand()
        self.calculatePrice()
        self.traided = False
        print("Ready to Sell {}".format(self.readyToSell))
        print("Ready to Buy {}".format(self.readyToBuy))

        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class SolarPanel(object): #level of Solar energy
    def __init__(self,peakPower,sunLevel):
        self.peakPower = peakPower
        self.sunLevel = sunLevel
        self.size = 0
        self.amountOfEnergyGenerated = 0

class OutdoorLight(object):
    def __init__(self):
        self.outdoorLight = 0

class InitAgent(Agent): # weather condition, outdoor temperature
    def __init__(self,unique_id, model,solarPanel,outdoorLight = None,days=7):
        super().__init__(unique_id, model)
        self.weatherCondition = 0

        self.days = days
        self.solarPanel = solarPanel
        self.outLight = outdoorLight
        self.hourCount = 0
        self.outdoorL = 0
        self.outdoorTemp = 0
        self.weatherCoeff = 0
        self.amountOfEnergy = 0

        self.hour = 0
        self.day = 0
        self.week = 0

    def getWeatherCondition(self):
        self.weatherCondition = random.choice(['sunny','partly cloudy','cloudy','rainy'])
        print("Weather is {}".format(self.weatherCondition))
        return self.weatherCondition

    def calculateWeatherCoeff(self):
        if self.weatherCondition == 'sunny':
            self.weatherCoeff = 1.3
        elif self.weatherCondition == 'partly cloudy':
            self.weatherCoeff = 0.8
        elif self.weatherCondition == 'cloudy':
            self.weatherCoeff = 0.2
        elif self.weatherCondition == 'rainy':
            self.weatherCoeff = 0


    def getOutdoorTemp(self):
        self.outdoorTemp = round(np.random.choice(sts.norm.rvs(9, 2, size=24)))
        print("Outdoor temperature {}".format(self.outdoorTemp))

    def calculateSolarEnergy(self):
        amountOfEnergy = 0
        if self.hour >= 0 and self.hour <= 4:
            self.solarPanel.amountOfEnergyGenerated = 0
            amountOfEnergy = 0
            print("Amount of Solar energy {}".format(self.solarPanel.amountOfEnergyGenerated))
        elif self.hour > 4 and self.hour <= 21:
            if self.hour >= 6 and self.hour <= 7:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(0.26, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 7 and self.hour <= 9:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(0.56, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 8 and self.hour <= 10:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(0.97, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 10 and self.hour <= 11:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(1.4, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 11 and self.hour <= 12:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(2.5, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 12 and self.hour <= 13:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(3.68, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 13 and self.hour <= 14:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(2.9, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 14 and self.hour <= 15:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(1.9, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 15 and self.hour <= 16:
                amountOfEnergy = abs(round(np.random.choice(sts.norm.rvs(2, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 16 and self.hour <= 17:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(1.8, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 17 and self.hour <= 18:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(0.8, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 18 and self.hour <= 19:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(0.4, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour > 19 and self.hour <= 20:
                amountOfEnergy = abs(
                    round(np.random.choice(sts.norm.rvs(0.1, 1, size=self.days)) * self.weatherCoeff, 2))
            elif self.hour >= 21:
                amountOfEnergy = 0
            print("Amount of energy Kwh {}".format(amountOfEnergy))  # real data multiplied on weather coefficient
            self.solarPanel.amountOfEnergyGenerated = amountOfEnergy
            print("Amount of Solar energy {}".format(self.solarPanel.amountOfEnergyGenerated))
        else:
            self.solarPanel.amountOfEnergyGenerated = 0
            print("Amount of Solar energy {}".format(self.solarPanel.amountOfEnergyGenerated))

    def calculateOutdoorLight(self):
        if self.hour >= 0 and self.hour < 7:
            self.outLight.outdoorLight = 20
        elif self.hour == 7 and self.weatherCondition == 'sunny':
            self.outLight.outdoorLight = 400
        elif self.hour == 7 and self.weatherCondition == 'partly cloudy':
            self.outLight.outdoorLight = 100
        elif self.hour == 7 and self.weatherCondition == 'cloudy':
            self.outLight.outdoorLight = 40
        elif self.hour > 7 and self.hour < 18:
            if self.weatherCondition == 'sunny':
                self.outLight.outdoorLight = 2000
            if self.weatherCondition == 'partly cloudy':
                self.outLight.outdoorLight = 200
            if self.weatherCondition == 'cloudy':
                self.outLight.outdoorLight = 100
        elif self.hour == 18 and self.weatherCondition == 'sunny':
            self.outLight.outdoorLight = 400
        elif self.hour == 18 and self.weatherCondition == 'partly cloudy':
            self.outLight.outdoorLight = 80
        else:
            self.outLight.outdoorLight = 20
        print("Outdoor light {}".format(self.outLight.outdoorLight))


    def step(self):
        print("Hour {}".format(self.hour))
        print("Day {}".format(self.day))
        print("Week {}".format(self.week))

        self.getWeatherCondition()
        self.calculateWeatherCoeff()
        self.calculateSolarEnergy()
        self.calculateOutdoorLight()
        self.getOutdoorTemp()
        self.hourCount += 1
        self.hour +=1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class HeaterAgent(Agent):
    def __init__(self, unique_id, model,temperature = 20,roomSize = None):
        super().__init__(unique_id, model)
        self.energy = 0
        self.minTemp = 20
        self.desiredTemp = 0
        self.readyToBuy = None
        self.price = 0

        self.initialDemand = 0

        self.priceHistory = []
        self.quantityHistoryBuy = []

        self.localDemandHistory = []
        self.minChoiceCount = 0
        self.interChoiceCount = 0
        self.stayChoiceCount = 0
        self.idealChoiceCount = 0

        #formula coefficients
        self.roomSize = roomSize
        self.power = 1
        self.hour = 0
        self.day = 0
        self.week = 0

        self.isInRoom = True
        self.turnedOn = True

        self.price = 0
        self.demandKwh = 0

        self.gamma = 0.5

        self.tempRange = 0

        self.currentTemp = 0
        self.currentDemand = 0
        self.minDemand = 0
        self.maxDemand = 0

        self.states = {
        'Critical': [1, 1, 1], #states propensities
        'Low': [1, 1],
        'Intermediate': [1, 1],
        'Ideal':[1]
        }
        self.currentState = None
        self.memory_param = 0.8
        self.experimental_param = 0.5 #more experimental freedom
        self.statesProb = {
        'Critical': [1 / 3, 1 / 3, 1 / 3],
        'Low': [1 / 2, 1 / 2],
        'Intermediate': [1 / 2, 1 / 2],
        'Ideal':[1]
        }
        self.choicesDict = {
        'Critical': ['min','intermediate','ideal'],
        'Low': ['intermediate','ideal'],
        'Intermediate': ['stay','ideal'],
        'Ideal':['pass'] #if ideal state, no updates of strategies required
        }

        self.choice = 0
        self.stateChoice = None

    def updateValues(self):
        stateElements = ['Critical', 'Low', 'Intermediate']
        for state in stateElements:
            for index, elem in enumerate(self.states[state]):
                self.states[state][index] += 1
                self.states[state][index] = elem * 0.9


    def updateStates(self,reward):
        updated_states = []
        i = 0
        for index, elem in enumerate(self.states[self.currentState]):
            if index == self.choice:
                print("elem {}".format(elem))
                elem = (1 - self.memory_param) * elem + (reward * (1 - self.experimental_param))
            else:
                elem = (1 - self.memory_param) * elem + (elem * (self.experimental_param / (len(self.states[self.currentState])-1)))
            updated_states.insert(i, elem)
            i += 1
        self.states[self.currentState] = updated_states
        print("Updated states {}".format(self.states))

    def updateStateProbabilities(self):
        propensitiesList = self.states[self.currentState]
        probs = []
        propSum = sum(propensitiesList)
        for index, elem in enumerate(propensitiesList):
            elem = elem/propSum
            probs.insert(index,elem)
        self.statesProb[self.currentState] = probs
        print("Probabilities {}".format(self.statesProb))

    def makeChoice(self): #make particular choice from states based on probabilities
        choicesList = self.choicesDict[self.currentState]
        choiceProbList = self.statesProb[self.currentState]
        choiceVar = np.random.choice(choicesList,p=choiceProbList)
        self.stateChoice = choiceVar
        self.choice = choicesList.index(choiceVar)
        print("Choice {}, Index {}".format(choiceVar,choicesList.index(choiceVar)))
        # self.choiceTestList.append(choiceVar)

    def calculatePrice(self):
        self.price = round(random.uniform(1.9,0.3),2) #price for KWh, NOK
        print("Price {}".format(self.price))

    def checkStatus(self):
        if self.currentDemand > 0:
            self.readyToBuy = True
        else:
            self.readyToBuy = False
        print("Ready to Buy {}".format(self.readyToBuy))

    def getTempRange(self):
        if self.turnedOn:
            if self.currentTemp > self.minTemp:
                self.tempRange = list(range(self.currentTemp,self.desiredTemp+1))
            else:
                self.tempRange = list(range(self.minTemp, self.desiredTemp + 1))
            print("Temperature range {}".format(self.tempRange))
        else:
            print("Heater is turned off")

    def getState(self):
        if self.currentTemp < self.minTemp and self.desiredTemp > self.minTemp:
            self.currentState = 'Critical'
        elif self.desiredTemp - self.currentTemp > 1:
            self.currentState = 'Low'
        elif self.desiredTemp - self.currentTemp == 1:
            self.currentState = 'Intermediate'
        else:
            self.currentState = 'Ideal'
        print(self.currentState)

    def checkIfIsIn(self):
        if self.hour >= 0 and self.hour < 7:
            self.isInRoom = np.random.choice([True, False], 1, p=[0.9, 0.1, ])[0]
        elif self.hour > 7 and self.hour <= 16:
            if self.day < 5:
                self.isInRoom = np.random.choice([True, False], 1, p=[0.1, 0.9])[0]
            else:
                self.isInRoom = np.random.choice([True, False], 1, p=[0.6, 0.4])[0]
        elif self.hour >= 17 and self.hour <= 21:
            self.isInRoom = np.random.choice([True, False], 1, p=[0.8, 0.2])[0]
        elif self.hour >= 22 and self.hour <= 23:
            self.isInRoom = np.random.choice([True, False], 1, p=[0.9, 0.1])[0]
        print("Person is in the room {}".format(self.isInRoom))

    def getCurrentTemp(self)->int:
        self.previousTemp = self.currentTemp
        self.currentTemp = random.choice(sts.norm.rvs(20,2,size=24))
        self.currentTemp = int(self.currentTemp)
        print("Current temperature {}".format(self.currentTemp))
        return self.currentTemp

    def getDesiredTemp(self)->int:
        if self.isInRoom:
            self.desiredTemp = random.choice(list(range(20,31)))
        else:
            self.desiredTemp = self.minTemp
        print("initial desired temperature {}".format(self.desiredTemp))
        return self.desiredTemp

    def updateDesiredTemp(self):
        if self.stateChoice == 'min':
            self.desiredTemp = self.minTemp
        elif self.stateChoice == 'intermediate':
            self.desiredTemp = self.desiredTemp - 1
        elif self.stateChoice == 'stay':
            self.desiredTemp = self.currentTemp
        print("New desired temperature {}".format(self.desiredTemp))

    def checkTempDifference(self):
        if self.desiredTemp <= self.currentTemp:
            print("no difference or temperature is lower")
            self.turnedOn = False
        else:
            self.turnedOn = True

    def computeDemand(self):
        self.energyKJ = 0
        self.roomSize = 15
        dryAirHeat = 1
        dryAirDencity = 1275
        roomHeight = 2.5
        massAir = dryAirDencity*self.roomSize*roomHeight
        if self.turnedOn == True:
            self.energyKJ = dryAirHeat*dryAirDencity*self.roomSize*roomHeight*(self.desiredTemp-self.currentTemp)
            self.demandKwh = round((self.energyKJ/1000)*0.00028,3)
            self.currentDemand = round(self.demandKwh*10,3)
            print("Demand KWh {}".format(self.demandKwh))
        else:
            self.currentDemand = 0
        self.localDemandHistory.append(self.currentDemand)

    def test_func(self):
        print("{0}".format(self.unique_id))

    def step(self):
        self.test_func()
        self.traided = False

        self.getCurrentTemp()
        self.checkIfIsIn()
        self.getDesiredTemp()

        print("Status {}".format(self.turnedOn))
        self.checkTempDifference()
        print("check temperature difference...")
        print("Status {}".format(self.turnedOn))

        self.updateValues()

        self.getTempRange()
        self.getState()
        self.makeChoice()
        self.updateDesiredTemp()

        self.calculatePrice()
        self.computeDemand()
        self.checkStatus()

        self.hour +=1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class LightAgent(Agent):
    def __init__(self, unique_id, model, power = 0.075,lumens = 90,area = 15):
        super().__init__(unique_id, model)

        self.energy = 0
        #formula coefficients
        self.power  = power
        self.lumens = lumens #lumens/Watt
        self.area = area
        self.lux = 0
        self.userProfile = 0
        self.readyToBuy = None
        self.traided = None
        self.isInRoom = True

        self.turnedOn = False
        self.price = 0

        self.initialDemand = 0

        self.hour = 0
        self.day = 0
        self.week = 0

        self.desiredLight = None
        self.outdoorLight = 0
        self.currentDemand = 0

    def calculatePrice(self):
        self.price = round(random.uniform(1.9,0.3),1) #price for KWh, NOK
        print("Price {}".format(self.price))

    def checkStatus(self):
        if self.currentDemand > 0:
            self.readyToBuy = True
        else:
            self.readyToBuy = False
        print("Ready to Buy {}".format(self.readyToBuy))

    def setUserProfile(self):
        self.userProfile = random.randrange(1,5)
        if self.userProfile == 4:
            self.desiredLight = 1500

        elif self.userProfile == 3:
            self.desiredLight = 500

        elif self.userProfile == 2:
            self.desiredLight = 100

        elif self.userProfile == 1:
            self.desiredLight = 0
            self.turnedOn = False
        print("User profile {}".format(self.userProfile))
        print("Desired Light level {}".format(self.desiredLight))

    def getOutdoorLight(self): #get info from init agent
        for agent in self.model.schedule.agents:
            if (isinstance(agent, InitAgent)):
                self.outdoorLight = agent.outLight.outdoorLight
        print("Calculated outdoor light {}".format(self.outdoorLight))

    def calculateDemand(self):
        if self.turnedOn:
            if self.outdoorLight >= self.desiredLight: #set desired light level according to the user
                powerDemand = (self.desiredLight*self.area)/self.lumens
                self.currentDemand = round(powerDemand / 1000,2)
                print("Desired light {}".format(self.desiredLight))
                print("Power {}".format(powerDemand))

            elif self.outdoorLight < self.desiredLight: #calculate difference for adjusting
                luxDiff = self.desiredLight - self.outdoorLight
                powerDemand = (luxDiff*self.area)/self.lumens
                self.currentDemand = round(powerDemand / 1000,2)
            else:
                self.currentDemand = 0
                print("Too bright")
        else:
            print("no movement")
            self.currentDemand = 0
        print("Light demand {} kWh".format(self.currentDemand))

    def getStatus(self):
        if self.isInRoom:
            self.turnedOn = True
        else:
            self.turnedOn = False

    def checkMovement(self):
        if self.hour >= 0 and self.hour < 7:
            self.isInRoom = np.random.choice([True, False],1,p=[0.9, 0.1, ])[0]
        elif self.hour > 7 and self.hour <= 16:
            if self.day < 5:
                self.isInRoom = np.random.choice([True, False],1,p=[0.1, 0.9])[0]
            else:
                self.isInRoom = np.random.choice([True, False],1,p=[0.6, 0.4])[0]
        elif self.hour >= 17 and self.hour <= 21:
            self.isInRoom = np.random.choice([True, False],1,p=[0.8, 0.2])[0]
        elif self.hour >= 22 and self.hour <= 23:
            self.isInRoom = np.random.choice([True, False], 1, p=[0.9, 0.1])[0]
        print("Person is in the room {}".format(self.isInRoom))

    def name_func(self):
        print("{0}".format(self.unique_id))

    def step(self):
        self.name_func()
        self.traided = False
        self.getOutdoorLight()
        self.setUserProfile()

        self.checkMovement()
        self.getStatus()

        self.calculatePrice()
        self.calculateDemand()
        self.checkStatus()

        self.hour +=1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0