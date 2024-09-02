import os
import sys
import pickle

flightPlanDict = {}
myPickleFile = "activeFlightDatabase.pkl"

def startUp():
    # Program will call this one time at start up.
    # Calls pickle.load to sync existing dictionary.
    if os.path.exists(myPickleFile) and os.path.getsize(myPickleFile) > 0:
        with open(myPickleFile, 'rb') as file:
            flightPlanDict = pickle.load(file)
            print(flightPlanDict)
            print("Dictionary loaded from previous server.")
    else:
        print("No existing dictionary present.")
    
def createFlightPlan(code, src, dst, lata, lona):
    # Write to flight plan dictionary and call pickle.dump
    flightPlanDict[code] = [src, dst, lata, lona]
    with open(myPickleFile, 'wb') as file:
        pickle.dump(flightPlanDict, file) # Last line!
    
def positionUpdate(flightCode, coordinateIndex):
    # Lookup flight code in database.
    # Assuming flight code is found, update position
    print("hi")
    
def printDict():
    print(flightPlanDict)

def clearDict():
    flightPlanDict.clear()
    with open(myPickleFile, 'wb') as file:
        pickle.dump(flightPlanDict, file) # Last line!

"""
Dictionary Overview

activeFlights = { 1:"one", 2:"two", 17:"seventeen"}

print(activeFlights[17]) - keys are the 'index', output is seventeen

activeFlights = { 1:("LAX", "MCI", latArr, lonArr), 2:(), 17:()}

code
src
dst
lata
lona
pos

activeFlights[code] = (src, dst, lata, lona, pos)
print( activeFlights[28375] ) - prints  (src, dst, lata, lona, pos)

pickle.dump(dict_a, open('test.pkl', 'wb'))
"""