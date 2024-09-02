import sys
import socket
import pickle
import numpy as np
import time
from GlobalAirportDatabase import *
from AirportRecord import *

gdb = GlobalAirportDatabase()
gdb.load("GlobalAirportDatabase.txt")

if len(sys.argv) == 4:
    sourceAirport = sys.argv[1]
    endAirport = sys.argv[2]
    flightTime = int(sys.argv[3])
else:
    sourceAirport = input("Enter source airport code: ")
    endAirport = input("Enter arrival airport code: ")
    flightTime = int(input("Enter flight time in seconds: "))

serverHost = "127.0.0.1"
serverPort = 9000

# Makes initial connection to server
try:   
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Trying to connect...")
    clientSocket.connect((serverHost, serverPort))
    print( 'Connection succeeded')
    route = 1
except ConnectionRefusedError as Err:
    print("Connection refused by server.")
    sys.exit(0)
except TimeoutError as Err:
    print("Timeout... Cannot find host server.")
    sys.exit(0)
    
if route == 1:

# Receives flight code from server
    try:
        clientSocket.sendall(str(route).encode('ascii'))
        rawCode = clientSocket.recv(4096)
        flightCode = int(rawCode.decode('ascii'))
        print("Received flight code - %s" % flightCode )
    except OSError as ConnectionReset:
        print("Connection closed before receiving response") 
    
    # Obtains necessary data for departure airport
    depAirport = gdb.lookup(sourceAirport)
    while depAirport is None:
        print("Departure airport not found.")
        sourceAirport = input("Please enter valid departure airport code: ")
        depAirport = gdb.lookup(endAirport)
    startLat = depAirport.lat 
    startLong = depAirport.lon
    
    # Obtains necessary data for arrival airport
    arrAirport = gdb.lookup(endAirport)
    while arrAirport is None:
        print("Arrival airport not found.")
        endAirport = input("Please enter valid arrival airport code: ")
        arrAirport = gdb.lookup(endAirport)
    endLat = arrAirport.lat
    endLong = arrAirport.lon
    
    # Calculates points necessary based on contact with server every 30 seconds
    numberPoints = flightTime // 30 # Will contain data point every 30 sec
    
    # Creates numpy arrays depicting flight path with lat and long point pairs
    latPath = np.linspace(startLat, endLat, numberPoints)
    longPath = np.linspace(startLong, endLong, numberPoints)
    
    # Creates flight plan as a list and sends to server
    flightPlan = [flightCode, sourceAirport, endAirport, latPath, longPath]
    packet = pickle.dumps(flightPlan)
    clientSocket.sendall(packet)
    
    print("Flight plan sent.")
    clientSocket.close()

else:
    route = 2
    # Input code for updating route here.