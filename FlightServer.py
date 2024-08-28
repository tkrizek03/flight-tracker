import sys
import socket
import random
import pickle

class FlightServer():
    
    ######################################
    def __init__( self, ip = '127.0.0.1', port = 9000):
        self.listenFilter = ip
        self.listenPort = port
        self.connections = 0
        self.numberOfFlights = 0
        
    def stats( self ):
        return( self.connections, self.echoCount)
    
    ######################################
    def run( self ):
        
        flightRecords = dict()
        
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
            self.connections += 1
            clientConnected=True
            while clientConnected and not dead :
                flightCode = random.randint(1000,9999)
                print("Assigning flight code.")
                clientSocket.sendall(str(flightCode).encode('ascii'))
                print("Sent flight code.")
                
                chunkData = b''
                while True:
                    chunk = clientSocket.recv(4096)
                    if not chunk:
                        break
                    chunkData += chunk
                flightData = pickle.loads(chunkData)
                print("Received flight data for flight #%s:" % flightCode)
                print(flightData)
                
                
                self.numberOfFlights += 1
                dead = True
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