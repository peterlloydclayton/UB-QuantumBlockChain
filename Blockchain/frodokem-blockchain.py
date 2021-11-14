"""

Blockchain Testing:
    
    Implemented with FrodoKEM 
    
    3 components:
        - Client
        - Miner
        - Blockchain

@author: sereysathialuy, peterclayton, arzususoglu
"""
# import libraries
import sys
import hashlib
import binascii
import datetime
import collections
from frodokem import frodokem


# 1. Client class
class Client:
    def __init__(self, matrix_variant='AES'):
        self._matrix_variant = 'FrodoKEM-640-'+matrix_variant
        self.kem = frodokem.FrodoKEM(self._matrix_variant)
        (self._private_key, self._public_key) = self.kem.kem_keygen()
        
    @property
    def identity(self):
        return binascii.hexlify(self._public_key).decode('ascii')
    
# 2. Transaction class
class Transaction:
    def __init__(self, sender, recipient, value):
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.time = datetime.datetime.now()
        self.cypher_text = ""
        self.hashed_message = ""
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
        (ct, ss_e) = frodokem.FrodoKEM(self.sender._matrix_variant).kem_encaps(private_key)
        self.cypher_text = ct
        self.hashed_message = sha256_1(str(ss_e)+str(self.to_dict()))
        self.sign_time_end = datetime.datetime.now().timestamp()*1000
        self.sign_time_duration = self.sign_time_end - self.sign_time_start

    def verify_transaction(self, public_key,cypher_text,transaction_info):
        self.verify_time_start = datetime.datetime.now().timestamp()*1000
        ss_d = frodokem.FrodoKEM(self.sender._matrix_variant).kem_decaps(public_key,cypher_text)
        hashed_transaction_info = sha256_1(str(ss_d)+transaction_info)
        self.verify_time_end = datetime.datetime.now().timestamp()*1000
        self.verify_time_duration = self.verify_time_end - self.verify_time_start
        return (hashed_transaction_info==self.hashed_message)

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
def dump_blockchain(UBCoins, matrix_variant):
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
    print ('FRODOKEM STATS')
    print ('=====================================')
    print ("Matrix Variant: ",matrix_variant)
    print ("Average Sign Time: ",(total_sign_time/counter))
    print ("Average Verify Time: ",(total_verify_time/counter))

def sha256_1(message):
    return hashlib.sha256(message.encode('ascii')).hexdigest()

# function to mine the block
def mine(message, difficulty = 1):
    assert difficulty >= 1
    prefix = '1' * difficulty
    for i in range(10000000):
        digest = sha256_1(str(hash(message)) + str(i))
        if digest.startswith(prefix):
            print("after " + str(i) + " iterations found nonce: " + digest)
        return digest

def main():
    sender_list = []
    transactions = []
    UBCoins = []
    matrix_variant = input("Enter Matrix Variant 'AES' or 'SHAKE': ").upper()
    
    # Clients
    Genesis = Client(matrix_variant)
    Peter = Client(matrix_variant)
    Arzu = Client(matrix_variant)
    Sathia = Client(matrix_variant)
    Professor = Client(matrix_variant)
    sender_list = [Peter,Arzu,Sathia,Professor]
    
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
    for i in range(4):
        current_transaction = transactions[last_transaction_index]
        public_key = current_transaction.sender._public_key
        cypher_text = current_transaction.cypher_text
        transaction_info = str(current_transaction.to_dict())

        #verify_transaction(self, public_key,cypher_text,transaction_info,hashed_message):
        if (current_transaction.verify_transaction(public_key,cypher_text,transaction_info)):
            temp_transaction = current_transaction
            # validate transaction, if valid
            block1.verified_transactions.append(temp_transaction)
            last_transaction_index += 1
        else:
            print("Signature Error: Sender or Transaction Not Valid")

    block1.previous_block_hash = last_block_hash
    block1.Nonce = mine(block1, 2)
    digest = hash(block1)
    
    UBCoins.append(block1)
    last_block_hash = digest
        
    # dump the blocks into the chain
    dump_blockchain(UBCoins, matrix_variant)

if __name__ == '__main__':
    sys.exit(int(main() or 0))