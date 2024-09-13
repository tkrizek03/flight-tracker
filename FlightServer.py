import sys
import socket
import random
import pickle
import time
from ActiveFlightDatabase import createFlightPlan
from ActiveFlightDatabase import startUp
from ActiveFlightDatabase import positionUpdate
from ActiveFlightDatabase import printDict
from ActiveFlightDatabase import clearDict
 

class FlightServer():
    
    ######################################
    def __init__( self, ip = '127.0.0.1', port = 9000):
        self.listenFilter = ip
        self.listenPort = port
        self.connections = 0
        self.numberOfFlights = 0
        # startUp()
        
    def stats( self ):
        return( self.connections, self.echoCount)
    
    ######################################
    def run( self ):
          
        listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Listen socket created for flight server.")
        
        try:
            listenSocket.bind( (self.listenFilter, self.listenPort) )
        except OSError as bindException :
            print( "failed to bind to port %d" % self.listenPort )
            print(bindException)
            sys.exit(0)
        print 
        listenSocket.listen(5)
        
        dead = False
        while not dead:
            clientSocket, clientAddress = listenSocket.accept()
            print( "Received connection from ", end='' )
            print( clientAddress )
            clientConnected = True
            while clientConnected == True:
                route = int(clientSocket.recv(4096).decode('ascii'))
                if route == 1:
                    
                    print("Received new connection.")
                    flightCode = int(time.time() * 10000)
                    print("Assigning flight code.")
                    clientSocket.sendall(str(flightCode).encode('ascii'))
                    print("Sent flight code.")
                    
                    chunkData = b''
                    chunk = clientSocket.recv(8192)
                    chunkData += chunk
                    flightData = pickle.loads(chunkData)
                    
                    if flightData[1] == 'DIE':
                        print("Received server kill code from client. Shutting server and client down.")
                        clientConnected = False
                        dead = True
                        break
                    elif flightData[1] == 'EMT':
                        print("Clearing active flight database. Shutting server and client down.")
                        clearDict()
                        clientConnected = False
                        dead = True
                        break
                    else:
                        print("Received flight data for flight #%s" % flightCode)
                        createFlightPlan(flightData[0], flightData[1], flightData[2], flightData[3], flightData[4])
                        print("Flight plan created.")
                        clientConnected = False
                        clientSocket.close()
                        break
                    
                elif route == 2:
                    print("Receiving position update...")
                    clientSocket.sendall(("Ready").encode("ascii"))
                    
                    for i in range(2):
                        if i == 0:
                            
                            coordinateIndex = int(clientSocket.recv(4096).decode("ascii"))
                            clientSocket.sendall(str(coordinateIndex).encode("ascii"))
                            
                        elif i == 1:
                            
                            receivedCode = int(clientSocket.recv(4096).decode("ascii"))
                            clientSocket.sendall(str(coordinateIndex).encode("ascii"))
                    
                    position = positionUpdate(receivedCode, coordinateIndex)
                    
                    if position[0] == "DIE":
                        
                        print("Invalid flight code entered. Closing client.")
                        clientSocket.close()
                        clientConnected = False
                        break
                    
                    elif position[2] == "END":
                        
                        print("Flight #{} is at [lat, lon]: {}, {}.".format(receivedCode, position[0], position[1]))
                        print("Flight #%d has arrived. Closing client." % receivedCode)
                        clientConnected = False
                        break
                    
                    else:
                        
                        print("Flight #{} is at [lat, lon]: {}, {}.".format(receivedCode, position[0], position[1]))
                        clientSocket.close()
                        clientConnected = False
                        break
                else:
                    
                    print("Invalid client connection. Closing client connection")
                    clientConnected = False
                    dead == True
        
        clientSocket.close()
        listenSocket.close()
        print('Shutting echo server down')

if len(sys.argv) == 3:
    serverPort = int(sys.argv[2])
    serverHost = sys.argv[1]
else:
    serverHost = "127.0.0.1"
    serverPort = 9000

server = FlightServer(serverHost, serverPort)
server.run()