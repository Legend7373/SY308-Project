import config
import socket
import select
import sys
import pickle
from atm import *

class bank:
  def __init__(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.bind((config.local_ip, config.port_bank))
    #====================================================================
    # TO DO: Add any class variables your ATM needs in the __init__
    # function below this.  For example, user balances, PIN numbers
    # etc.
    #====================================================================
    '''
        need to create a local storage mechansim to recive encrypted messages from the atm, such as key,pin,user,amount info

    '''
    self.users = {"Alice": 10000, "Bob": 10001, "Carol": 10002 }
    self.atmUser = ""
    balanceStorage = open("BalanceFile.bin","r")
    balanceStorage.readline()
    self.userBalances = {}
    for userBalance in balanceStorage.readlines():
      line = userBalance.split(":")
      self.userBalances[line[0]] = int(line[1].strip())
    balanceStorage.close()
    pinStorage = open("PinFile.bin","r")
    self.userPins = {}
    for userPin in pinStorage.readlines():
      line = userPin.split(":")
      self.userPins[line[0]] = int(line[1].strip())
    pinStorage.close()

  def encrypt(self, data):
    '''
    Here we will implement our encryption scheme to send messages to the atm
    returns encrypted messsage
    '''
  def decrypt(self, data):
    '''
    Here we will decrypt the incoming message from the atm and update our local storage as necessary
    returns decrypted messsage
    '''


  #====================================================================
  # TO DO: Modify the following function to handle the console input
  # Every time a user enters a command at the bank terminal, it comes
  # to this function as the variable "inString"
  # The current implementation simply sends this string to the ATM
  # as a demonstration.  You will want to remove this and instead process
  # this string to deposit money, check balance, etc.
  #====================================================================
  def handleLocal(self,inString):
    #self.send(inString)
    '''
    get message
    determine its contents 
        if (len(message) >= 2): 
            command  =  1st arg
            name = 2nd arg 
            if (command == 'balance'):
                get balance of name (we need security here somehow)
            if (command == 'deposit'):
                update balance and display new balance (we need security here somehow)
        else: 
          Invalid request
        self.prompt() 
      *This function is a handler the return depends verifying and the command*
    '''
    userMessage = inString.split(" ")
    messageLen = len(userMessage)
    if (userMessage[0] == 'balance') and messageLen == 2:
      try:
        userID = userMessage[1] 
        print("$" + str(self.userBalances[userID]) + "\n") 
      except: 
        print("Invalid user") 
    elif (userMessage[0] == 'deposit') and messageLen == 3:
      try: 
        userID = userMessage[1] 
        amountDeposited = userMessage[2]
        if int(amountDeposited) > 0:
          self.userBalances[userID] += int(amountDeposited) 
          print("$" + str(amountDeposited) + " deposited into " + userID + "'s account\n")
      except:
        print("Invalid Request. Deposit requires a valid user and an ammount") 
      #else: 
        #print("Invalid request") 
    else: 
      print("\nInvalid Request. Commands: deposit user amt, balance user\n")

        
       


  #====================================================================
  # TO DO: Modify the following function to handle the atm request 
  # Every time a message is received from the ATM, it comes to this
  # function as "inObject".  You will want to process this message
  # and potentially allow a user to login, dispense money, etc.
  # You will then have to respond to the ATM by calling the send() 
  # function to notify the ATM of any action you approve or disapprove.
  # Right now it just prints any message sent from the ATM to the screen
  # and sends the same message back to the ATM.
  #====================================================================
  def handleRemote(self, inObject):
    #print("\nFrom ATM: ", inObject )
    #self.send(inObject)
    '''
    get user message
    determine its contents 

        if (command == 'balance'):
            get balance
            send balance (encrypted)
        
        if (command == 'withdraw'):
            get balance
            if (balance >= amount requested): 
                update and send info 
            else: 
                any other case is a no go, just tell em they dont have enough
        
        if (command == 'verify'): 
            here is where we will verify the user's identity
        else:
          self.prompt()
      *This function is a handler the return depends verifying and the command*
    '''
    #Here we would need to decrypt it first
    
    atmMessage = inObject.decode("utf-8") 
    atmMessage = atmMessage.split(" ") 
    messageLen = len(atmMessage)
    atmCommand = atmMessage[0]
    if (atmCommand == "verifyUser") and messageLen == 3:
      responseToATM = "invalid" #FAIL SAFE
      self.atmUser = atmMessage[1].strip()
      atmUserID = atmMessage[2].strip()
      if(self.atmUser in self.users):
          if self.users[self.atmUser] == int(atmUserID): 
            responseToATM = "validuser"
      else:
        responseToATM = "invalidur" #FAIL SAFE 
      responseToATM = responseToATM.encode("utf-8")
      #Here we would need to encrypt first
      self.send(responseToATM)
    if (atmCommand == "verifyPin") and messageLen == 2:
      responseToATM = "invalidp" #FAIL SAFE
      cardPin = atmMessage[1].rstrip()
      if(self.atmUser in self.userPins): 
        if(int(self.userPins[self.atmUser]) == int(cardPin)):
          responseToATM = "validpin" 
      else:
        responseToATM = "invalidp" #FAIL SAFE 
      responseToATM = responseToATM.encode("utf-8")
      #Here we would need to encrypt first
      self.send(responseToATM)
    elif (atmCommand == "balance") and messageLen == 2:
      self.atmUser = atmMessage[1].strip()
      if(self.atmUser in self.userBalances): 
        userBalance = self.userBalances[self.atmUser]   
        responseToATM = "$" + str(userBalance) + "\n" 
      else:
        responseToATM = "\nInvalid User\n" #FAIL SAFE 
      responseToATM = responseToATM.encode("utf-8")
      #Here we would need to encrypt first
      self.send(responseToATM)
    elif (atmCommand == "withdraw") and messageLen == 3:
      self.atmUser = atmMessage[1].strip()
      if(self.atmUser in self.userBalances): 
        userBalance = self.userBalances[self.atmUser]
        amountRequested = int(atmMessage[2])
        if (userBalance >= amountRequested): 
          self.userBalances[self.atmUser] -= amountRequested 
          responseToATM = "$" + str(amountRequested) + " withdrawn\n" 
        else: 
          responseToATM = "\nInsufficient Funds\n" 
      else:
        responseToATM = "\nInvalid User\n" #FAIL SAFE 
      responseToATM = responseToATM.encode("utf-8")
      #Here we would need to encrypt first
      self.send(responseToATM)
   

  #====================================================================
  # DO NOT MODIFY ANYTHING BELOW THIS UNLESS YOU ARE REALLY SURE YOU
  # NEED TO FOR YOUR APPROACH TO WORK. This is all the network IO code
  # that makes it possible for the ATM and bank to communicate.
  #====================================================================
  def prompt(self):
    sys.stdout.write("BANK:")
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
            self.handleRemote(pickle.loads(data)) # call handleRemote
            self.prompt() 
                                 
        # User entered a message
        elif s == sys.stdin:
          m = sys.stdin.readline().rstrip("\n")
          if m == "quit": 
            return
          self.handleLocal(m) # call handleLocal
          self.prompt() 
        

if __name__ == "__main__":
  b = bank()
  b.mainLoop()

