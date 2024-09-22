import sys
import socket
import pickle
import numpy as np
import time
from GlobalAirportDatabase import *
from AirportRecord import *

newFlightPlan = 1 
newPositionUpdate = 2

gdb = GlobalAirportDatabase()
gdb.load("GlobalAirportDatabase.txt")

if len(sys.argv) == 4:
    sourceAirport = sys.argv[1]
    endAirport = sys.argv[2]
    numberPoints = int(sys.argv[3]) # Chnage to number of points. create a cap
else:
    sourceAirport = input("Enter source airport code: ")
    endAirport = input("Enter arrival airport code: ")
    numberPoints = int(input("Enter number of points (position update every 10 seconds): ")) # change to above

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
    
msgType = newFlightPlan

    # Receives flight code from server
try:
    clientSocket.sendall(str(msgType).encode('ascii'))
    rawCode = clientSocket.recv(4096)
    flightCode = int(rawCode.decode('ascii'))
    print("Received flight code - %s" % flightCode )
except OSError as ConnectionReset:
    print("Connection closed before receiving response") 

# Obtains necessary data for departure airport
depAirport = gdb.lookup(sourceAirport)
while depAirport is None or depAirport == '':
    print("Departure airport not found.")
    sourceAirport = input("Please enter valid departure airport code: ")
    depAirport = gdb.lookup(sourceAirport)
startLat = depAirport.lat 
startLong = depAirport.lon

# Obtains necessary data for arrival airport
arrAirport = gdb.lookup(endAirport)
while arrAirport is None or arrAirport == '':
    print("Arrival airport not found.")
    endAirport = input("Please enter valid arrival airport code: ")
    arrAirport = gdb.lookup(endAirport)
endLat = arrAirport.lat
endLong = arrAirport.lon

# Creates numpy arrays depicting flight path with lat and long point pairs
latPath = np.linspace(startLat, endLat, numberPoints)
longPath = np.linspace(startLong, endLong, numberPoints)

# Creates flight plan as a list and sends to server
try:
    flightPlan = [flightCode, sourceAirport, endAirport, latPath, longPath]
    packet = pickle.dumps(flightPlan)
    clientSocket.sendall(packet)
except NameError as err:
    print("Element of flight plan is not defined.")
    sys.exit(0)
print("Flight plan sent.")





# Position update sequence

i = 0

latPosition = None
lonPosition = None

for i in range(len(latPath)):

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
    
    msgType = newPositionUpdate
    clientSocket.sendall(str(msgType).encode('ascii'))
    try:
        ready = clientSocket.recv(4096)
    except ConnectionResetError as err:
        print("Lost connection to server. Closing client.")
        sys.exit(0)
    print("Sending position update...")
        
    clientSocket.sendall(str(i).encode('ascii'))
    clientSocket.recv(4096).decode('ascii')
    
    clientSocket.sendall(str(flightCode).encode('ascii'))
    clientSocket.recv(4096).decode('ascii')
        
    print("Sent updated data.")      
    
    latPosition = latPath[i]
    lonPosition = longPath[i]

    time.sleep(10)

if latPosition == latPath[-1] and lonPosition == longPath[-1]:
    finalMsg = "Flight complete. Closing client socket."
    print(finalMsg)

            


