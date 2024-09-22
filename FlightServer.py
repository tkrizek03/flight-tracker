import sys
import socket
import pickle
import time
from ActiveFlightDatabase import *

newFlightPlan = 1 
newPositionUpdate = 2

class FlightServer():
    
    ######################################
    def __init__( self, ip = '127.0.0.1', port = 9000):
        self.listenFilter = ip # accepts to an owned network interface OR 127.0.0.1 OR 0.0.0.0
        self.listenPort = port
        self.connections = 0
        self.numberOfFlights = 0
        ActiveFlightDatabase.startUp()
        
    #####################################
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
        listenSocket.listen(5) # Ready for connections
        
        dead = False
        while not dead:
            clientSocket, clientAddress = listenSocket.accept() # Waits for connection. Opens client socket once connection is received.
            print( "Received connection from ", end='' )
            print( clientAddress )
            msgType = int(clientSocket.recv(4096).decode('ascii'))
            if msgType == newFlightPlan:
                
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
                    dead = True
                elif flightData[1] == 'EMT':
                    print("Clearing active flight database. Shutting server and client down.")
                    ActiveFlightDatabase.clearDict()
                    dead = True
                else:
                    print("Received flight data for flight #%s" % flightCode)
                    ActiveFlightDatabase.createFlightPlan(flightData[0], flightData[1], flightData[2], flightData[3], flightData[4])
                    print("Flight plan created.")
                    clientSocket.close()
                    
                
            elif msgType == newPositionUpdate:
                print("Receiving position update...")
                clientSocket.sendall(("Ready").encode("ascii"))
                        
                coordinateIndex = int(clientSocket.recv(4096).decode("ascii"))
                clientSocket.sendall(str(coordinateIndex).encode("ascii"))
                
                receivedCode = int(clientSocket.recv(4096).decode("ascii"))
                clientSocket.sendall(str(coordinateIndex).encode("ascii"))
                
                position = ActiveFlightDatabase.positionUpdate(receivedCode, coordinateIndex)
                
                if position[0] == "DIE":
                    
                    print("Invalid flight code entered. Closing client.")
                    clientSocket.close()
                    dead = True
                
                elif position[2] == "END":
                    
                    print("Flight #{} is at [lat, lon]: {}, {}.".format(receivedCode, position[0], position[1]))
                    print("Flight #%d has arrived. Closing client." % receivedCode)
                    clientSocket.close()
                
                else:

                    print("Flight #{} is at [lat, lon]: {}, {}.".format(receivedCode, position[0], position[1]))
                    clientSocket.close()
                    
            else:
                print("Invalid client connection. Closing client connection")
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