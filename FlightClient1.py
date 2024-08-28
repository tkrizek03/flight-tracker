import sys
import socket
import pickle
import numpy as np
from GlobalAirportDatabase import *
from AirportRecord import *

gdb = GlobalAirportDatabase()
gdb.load("GlobalAirportDatabase.txt")

serverHost = "127.0.0.1"
serverPort = 9000

# Makes initial connection to server
try:   
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Trying to connect...")
    clientSocket.connect((serverHost, serverPort))
    print( 'Connection succeeded')
except ConnectionRefusedError as Err:
    print("Connection refused by server.")
    sys.exit(0)
except TimeoutError as Err:
    print("Timeout... Cannot find host server.")
    sys.exit(0)
    
# Receives flight code from server
try:
    rawCode = clientSocket.recv(4096)
    flightCode = int(rawCode.decode('ascii'))
    print("Received flight code - %s" % flightCode )
except OSError as ConnectionReset:
    print("Connection closed before receiving response") 

# Obtains necessary data for departure airport
depAirport = gdb.lookup('LAX')
if depAirport is None:
    print("Departure airport not found.")
startLat = depAirport.lat 
startLong = depAirport.lon

# Obtains necessary data for arrival airport
arrAirport = gdb.lookup('MCI')
if arrAirport is None:
    print("Arrival airport not found.")
endLat = arrAirport.lat
endLong = arrAirport.lon

# Calculates points necessary based on contact with server every 30 seconds
flightTime = 702000 # Seconds
numberPoints = flightTime // 30

# Creates numpy arrays depicting flight path with lat and long point pairs
latPath = np.linspace(startLat, endLat, numberPoints)
longPath = np.linspace(startLong, endLong, numberPoints)

# Creates flight plan as a list and sends to server
flightPlan = ['LAX', 'MCI', latPath, longPath]
packet = pickle.dumps(flightPlan)
clientSocket.sendall(packet)

print("Flight plan sent.")
clientSocket.close()