import os
import sys
import pickle

flightPlanDict = {}
myPickleFile = "activeFlightDatabase.pkl"

class ActiveFlightDatabase:
    
    def startUp():
        # Program will call this one time at start up.
        # Calls pickle.load to sync existing dictionary.
        if os.path.exists(myPickleFile) and os.path.getsize(myPickleFile) > 0:
            with open(myPickleFile, 'rb') as file:
                flightPlanDict = pickle.load(file)
                print(flightPlanDict)
                print("Dictionary loaded from previous server.")
                file.close()
        else:
            print("No existing dictionary present.")
        
    def createFlightPlan(code, src, dst, lata, lona):
        # Write to flight plan dictionary and call pickle.dump
        flightPlanDict[code] = [src, dst, lata, lona, 0]
        with open(myPickleFile, 'wb') as file:
            pickle.dump(flightPlanDict, file)
            file.close() # Last line!
        
    def positionUpdate(flightCode, coordinateIndex):
        # Lookup flight code in database.
        # Assuming flight code is found, update position
        if flightCode in flightPlanDict:
            latPath = flightPlanDict[flightCode][2]
            latPosition = latPath[coordinateIndex]
            longPath = flightPlanDict[flightCode][3]
            longPosition = longPath[coordinateIndex]
            flightPlanDict[flightCode][4] = coordinateIndex
            with open(myPickleFile, 'wb') as file:
                pickle.dump(flightPlanDict, file)
                file.close()
            if latPosition == latPath[-1] and longPosition == longPath[-1]:
                position = [latPosition, longPosition, "END"]
            else:
                position = [latPosition, longPosition, "CONT"]
            return position
        else:
            position = ['DIE', 'DIE', "DIE"]
            return position
            print("Flight code not found.")
            
        
    def printDict():
        print(flightPlanDict)
    
    def clearDict():
        flightPlanDict.clear()
        with open(myPickleFile, 'wb') as file:
            pickle.dump(flightPlanDict, file) # Last line!

