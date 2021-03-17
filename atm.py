import config
import socket
import select
import sys
import json
import pickle
from bank import *


class atm:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((config.local_ip, config.port_atm))
        #====================================================================
        # TO DO: Add any class variables your ATM needs in the __init__
        # function below this.  I have started with two variables you might
        # want, the loggedIn flag which indicates if someone is logged in to
        # the ATM or not and the user variable which holds the name of the
        # user currently logged in.
        #====================================================================
        self.user = None
        '''
        need to create a local storage mechansim to recive encrypted messages from the bank, such as key,pin,user,amount info

        '''
        self.loggedIn = False
        self.user = None
    def encrypt(self, data):
        '''
        Here we will implement our encryption scheme to send messages to the bank
        returns encrypted messsage 
        '''
    def decrypt(self, data):
        '''
        Here we will decrypt the incoming message from the bank and update our local storage as necessary
        returns decrypted messsage
        '''

    #====================================================================
    # TO DO: Modify the following function to handle the console input
    # Every time a user enters a command at the ATM terminal, it comes
    # to this function as the variable "inString"
    # The current implementation simply sends this string to the bank
    # as a demonstration.  You will want to remove this and instead process
    # this string and determine what, if any, message you want to send to
    # the bank.
    #====================================================================
    def handleLocal(self, inString):
        #self.send(inString)
        '''
        if command == "begin-session":
            get current card
            get the name of the person's card
            if name in our system:
                ask the user for pin and look up the pin we have on file for the user
                if pin on system == user entered pin:
                    verified 
                else:
                    invalid, exit
        if the user is "in session" (already verifified) :
            if command == "balance":
                get blance from bank and display
            elif command == "withdraw":
                see if user entered a correct amount (valid form) and make sure they have the specified amount
            elif command == "end-session":
                end it
            else:
                try to catch anything fishy 
                #self.prompt()

        else:
        try to catch anything fishy - fail safe default
        #self.prompt()
      *This function is a handler the return depends verifying and the command*
        '''
        inputATM = inString.split(" ")
        command = inputATM[0]  
        #Two inputs, the user would be entering a number they wish to withdraw
        try: 
            amount = str(inputATM[1])
        except IndexError: 
            amount = None
        messageATM = str()
        if (command == "begin-session"):
            if (self.user is None): 
                #Open and read card
                with open("Inserted.card", 'r') as cardFile:
                    userName = cardFile.readline().rstrip() 
                    userID = cardFile.readline().rstrip() 
                    #Validate user is a customer of our bank
                    messageVerify = "verifyUser " + userName + " " + userID
                    #Here we would first send it to our encrypt function, convert to bytes, encrypt, then send it
                    self.send(messageVerify.encode("utf-8"))
                    boolean, bankResponse = self.recvBytes() 
                    bankResponse = bankResponse[13:22]
                    bankResponse = bankResponse.decode("utf-8")
                    #Make sure user is even in the bank first
                    if bankResponse == "validuser":
                        print("Welcome " + userName)
                        pin = input("Enter Pin: ")  
                        #Validate user is a customer of our bank
                        messageVerify = "verifyPin " + pin 
                        #Here we would first send it to our encrypt function, convert to bytes, encrypt, then send it
                        self.send(messageVerify.encode("utf-8"))
                        boolean, bankResponse = self.recvBytes() 
                        bankResponse = bankResponse[13:21]
                        bankResponse = bankResponse.decode("utf-8")
                        #Verify correct pin corresponds to current user
                        if bankResponse == "validpin": 
                            print("Access Granted.\n")
                            self.user = str(userName)
                            self.loggedIn = True
                        else: 
                            print("Access Denied: Invalid PIN\n")
                    else:
                        print(bankResponse + ":\n") 
                        print("Access Denied: Invalid User Card\n")
            else: 
                print("\n User: " + self.user.rstrip() + " -already in session\n") 
        elif (command == 'end-session'):  
            if (self.user is not None and self.loggedIn is True) : 
                print("\nSession ended for user: " + self.user + "\n") 
                self.user = None #Reset
                self.loggedIn = False #Reset
            else: #FAIL SAFE
                print("\nNo session in progress\n")
          

        elif (command == 'withdraw'): 
            if (self.user is not None and self.loggedIn is True):
                #FAIL SAFE DEFAULT FOR AMOUNT INPUT
                if amount is None or not amount.isdigit():
                    print("\n Withdraw requires an amount\n Ex: withdraw 1 \n")
                elif (all(chr.isdigit()is True for chr in amount)) and int(amount) >= 0: 
                    messageATM = command + " " +  self.user.rstrip() + " " + str(abs(int(amount)))                 
                    #Here we would first send it to our encrypt function, convert to bytes, encrypt, then send it
                    self.send(messageATM.encode("utf-8"))
                 #FAIL SAFE DEFAULT FOR COMMAND INPUT
                else: 
                    print("Amount must be a valid positive number, we also only have cash\n")
            else: 
                print("\nNo session in progress, please login\n")
              
        elif (command == 'balance'): 
            if (self.user is not None and self.loggedIn is True): 
                messageATM = command + " " + self.user.rstrip()          
                #Here we would first send it to our encrypt function, convert to bytes, encrypt, then send it
                self.send(messageATM.encode("utf-8"))
            else: 
                print("\n No user currently logged in\n")
        #FAIL SAFE DEFAULT FOR COMMAND INPUT
        else: 
            print("\nInvalid Request. Commands: begin-session, end-session, withdraw (amount), and balance\n")

    #====================================================================
    # TO DO: Modify the following function to handle the bank's messages.
    # Every time a message is received from the bank, it comes to this
    # function as "inObject".  You will want to process this message
    # and potentially allow a user to login, dispense money, etc.
    # Right now it just prints any message sent from the bank to the screen.
    #====================================================================
    def handleRemote(self, inObject):
       # print("From Bank: ", inObject)
        '''
        Have to decode the message because we are encrypting 
        then display prompt again
        #self.prompt()
      *This function is a handler the return depends verifying and the command*
        '''
        bankResponse = inObject.decode("utf-8")
        print("\n", inObject.decode("utf-8") )
        
    #====================================================================
    # DO NOT MODIFY ANYTHING BELOW THIS UNLESS YOU ARE REALLY SURE YOU
    # NEED TO FOR YOUR APPROACH TO WORK. This is all the network IO code
    # that makes it possible for the ATM and bank to communicate.
    #====================================================================
    def prompt(self):
        print("ATM" + (" (" + self.user + ")" if self.user != None else "") +
              ":",
              end="")
        sys.stdout.flush()

    def __del__(self):
        self.s.close()

    def send(self, m):
        self.s.sendto(pickle.dumps(m), (config.local_ip, config.port_router))

    def recvBytes(self):
        data, addr = self.s.recvfrom(config.buf_size)
        if addr[0] == config.local_ip and addr[1] == config.port_router:
            return True, data
        else:
            return False, bytes(0)

    def mainLoop(self):
        self.prompt()

        while True:
            l_socks = [sys.stdin, self.s]

            # Get the list sockets which are readable
            r_socks, w_socks, e_socks = select.select(l_socks, [], [])

            for s in r_socks:
                # Incoming data from the router
                if s == self.s:
                    ret, data = self.recvBytes()
                    if ret == True:
                        self.handleRemote(
                            pickle.loads(data))  # call handleRemote
                        self.prompt()

                # User entered a message
                elif s == sys.stdin:
                    m = sys.stdin.readline().rstrip("\n")
                    if m == "quit":
                        return
                    self.handleLocal(m)  # call handleLocal
                    self.prompt()


if __name__ == "__main__":
    a = atm()
    a.mainLoop()
