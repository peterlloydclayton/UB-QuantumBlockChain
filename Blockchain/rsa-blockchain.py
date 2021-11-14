"""

Blockchain Testing:
    
    Implemented with RSA 
    
    3 components:
        - Client
        - Miner
        - Blockchain

@author: sereysathialuy
"""
# import libraries
import sys
import hashlib
import binascii
import datetime
import collections
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# 1. Client class
class Client:
    def __init__(self, key_length=1024):
        random = Crypto.Random.new().read
        self._private_key = RSA.generate(key_length, random)
        self._public_key = self._private_key.publickey()
        self.signer = PKCS1_v1_5.new(self._private_key)
        
    @property
    def identity(self):
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')
    
# 2. Transaction class
class Transaction:
    def __init__(self, sender, recipient, value):
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.signature = None
        self.time = datetime.datetime.now()
        self.sign_time_start = 0
        self.sign_time_end = 0
        self.sign_time_duration = 0
        self.verify_time_start = 0
        self.verify_time_end = 0
        self.verify_time_duration = 0
        
    def to_dict(self):
        if self.sender == "Genesis":
            identity = "Genesis"
        else:
            identity = self.sender.identity
            
        return collections.OrderedDict({
            'sender':identity,
            'recipient':self.recipient,
            'value':self.value,
            'time':self.time})
    
    def sign_transaction(self):
        self.sign_time_start = datetime.datetime.now().timestamp()*1000
        private_key = self.sender._private_key
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')
        self.sign_time_end = datetime.datetime.now().timestamp()*1000
        self.sign_time_duration = self.sign_time_end - self.sign_time_start

    def verify_transaction(self, public_key,signature,transaction_info):
        self.verify_time_start = datetime.datetime.now().timestamp()*1000
        h = SHA.new(str(transaction_info).encode('utf8'))
        isValid = False
        try:
            PKCS1_v1_5.new(public_key).verify(h, signature)
            print ("The signature is valid")
            isValid = True
        except (ValueError, TypeError):
            print ("The signature is not valid")
        self.verify_time_end = datetime.datetime.now().timestamp()*1000
        self.verify_time_duration = self.verify_time_end - self.verify_time_start
        return (isValid)

# 3. Block class
class Block:
    def __init__(self):
        self.verified_transactions = []
        self.previous_block_hash = ""
        self.Nonce = ""


# function to display transactions    
def display_transaction(transaction):
    # for transaction in transactions:
    dict = transaction.to_dict()
    print("sender: " + str(dict['sender'])[-25:])
    print("recipient: " + str(dict['recipient'])[-25:])
    print("value: " + str(dict['value'])[-25:])
    print("time: " + str(dict['time']))


# function to dump the transaction onto Blockchain    
def dump_blockchain(UBCoins, key_length):
    counter = 0
    total_sign_time = 0
    total_verify_time = 0

    print ("Number of blocks in the chain: " + str(len (UBCoins)))
    for x in range (len(UBCoins)):
        block_temp = UBCoins[x]
        print ("block # " + str(x))
        for transaction in block_temp.verified_transactions:
            counter = counter + 1
            total_sign_time = total_sign_time + transaction.sign_time_duration
            total_verify_time = total_verify_time + transaction.verify_time_duration
            display_transaction (transaction)
            print ('--------------')
    print ('=====================================')
    print ('RSA STATS')
    print ('=====================================')
    print ("RSA Key Length: ",key_length)
    print ("Average Sign Time: ",(total_sign_time/counter))
    print ("Average Verify Time: ",(total_verify_time/counter))


def sha256(message):
    return hashlib.sha256(message.encode('ascii')).hexdigest()

# function to mine the block
def mine(message, difficulty = 1):
    assert difficulty >= 1
    prefix = '1' * difficulty
    for i in range(10000000):
        digest = sha256(str(hash(message)) + str(i))
        if digest.startswith(prefix):
            print("after " + str(i) + " iterations found nonce: " + digest)
        return digest


def main():
    transactions = []
    UBCoins = []
    key_length = input("Enter RSA Key Length: ")
    key_length = int(key_length)

    
    # Clients
    Genesis = Client(key_length)
    Peter = Client(key_length)
    Arzu = Client(key_length)
    Sathia = Client(key_length)
    Professor = Client(key_length)
    
    # transactions
    t0 = Transaction(Genesis, Peter.identity, 5000)
    t0.sign_transaction()
    transactions.append(t0)
    t1 = Transaction(Peter, Arzu.identity, 100)
    t1.sign_transaction()
    transactions.append(t1)
    t2 = Transaction(Peter, Sathia.identity, 150)
    t2.sign_transaction()
    transactions.append(t2)
    t3 = Transaction(Arzu, Sathia.identity, 75)
    t3.sign_transaction()
    transactions.append(t3)
    t4 = Transaction(Sathia, Professor.identity, 120)
    t4.sign_transaction()
    transactions.append(t4)
    
    # adding the genesis block
    block0 = Block()
    block0.previous_block_hash = None
    Nonce = None
    
    block0.verified_transactions.append(t0)
    digest = hash(block0)
    last_block_hash = digest
    
    UBCoins.append(block0)
    
    # mining the next block (Block 1)
    block1 = Block()
    last_transaction_index = 1
    
    # mining the next 2 transactions in block 1
    for i in range(2):
        current_transaction = transactions[last_transaction_index]
        public_key = current_transaction.sender._public_key
        transaction_info = str(current_transaction.to_dict())
        signature = current_transaction.signature

        if (current_transaction.verify_transaction(public_key,signature,transaction_info)):
            temp_transaction = current_transaction
            # validate transaction, if valid
            block1.verified_transactions.append(temp_transaction)
            last_transaction_index += 1
            temp_transaction = transactions[last_transaction_index]
            # validate transaction, if valid
            block1.verified_transactions.append(temp_transaction)
            last_transaction_index += 1

    block1.previous_block_hash = last_block_hash
    block1.Nonce = mine(block1, 2)
    digest = hash(block1)
    
    UBCoins.append(block1)
    last_block_hash = digest
    
    # dump the blocks into the chain
    dump_blockchain(UBCoins,key_length)

if __name__ == '__main__':
    sys.exit(int(main() or 0))