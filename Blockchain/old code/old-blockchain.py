# Module 2 - Create a Cryptocurrency

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries
import binascii
import collections
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import Crypto.Random.random
from Crypto.Signature import pkcs1_15
import datetime
import datetime
from flask import Flask, jsonify, request
import hashlib
import json
import requests
from typing import Collection
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
    
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    

    def add_transaction(self, sender, receiver, amount):
        if not sender or not receiver or not amount:
            print("transaction error 1");
            return False;

        transaction = Transaction(sender, receiver, amount)
        transaction.sign_transaction()

        if not transaction.isValidTransaction():
            print("transaction error 2");
            return False;
        
        self.transactions.append(transaction);
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

class Client:
   def __init__(self):
      random = Crypto.Random.new().read
      self._id = ""
      self._private_key = RSA.generate(1024, random)
      self._public_key = self._private_key.publickey()
      self._signer = pkcs1_15.new(self._private_key)

   @property
   def identity(self):
      return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

class Transaction (object):
    def __init__(self, sender, receiver, amt):
        self.sender = sender;
        self.receiver = receiver;
        self.amt = amt;
        self.time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"); #change to current date
        self.hash = self.calculateHash();

    def calculateHash(self):
        hashString = str(self.sender) + str(self.receiver) + str(self.amt) + str(self.time);
        hashEncoded = json.dumps(hashString, sort_keys=True).encode();
        return hashlib.sha256(hashEncoded).hexdigest();
    
    def to_dict(self):
        if self.sender._id == "Genesis":
            identity = "Genesis"
        else:
            identity = self.sender.identity
     
        return collections.OrderedDict({
           'sender': identity,
           'receiver': self.receiver,
           'amount': self.amt,
           'time' : self.time})

    def isValidTransaction(self):
        if(self.hash != self.calculateHash()):
            return False;
        if(self.sender == self.receiver):
            return False;
        if(self.sender._id == "Miner Rewards"):
			#security : unfinished
            return True;
        if not self.sign_transaction or len(self.sign_transaction()) == 0:
            print("No Signature!")
            return False;
        return True;
		#needs work!

    def sign_transaction(self):
       private_key = self.sender._private_key
       signer = pkcs1_15.new(private_key)
       h = SHA256.new()
       h.update(str(self.to_dict()).encode('utf8'))
       return binascii.hexlify(signer.sign(h)).decode('ascii')

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    initialSender = Client()
    initialSender._id = node_address
    firstClient = Client()
    blockchain.add_transaction(sender =
                               initialSender,
                               receiver = firstClient,
                               amount = 1)
    # validate transaction here: TBD: Add validation code
    block = blockchain.create_block(proof, previous_hash)
    transactions = []
    for transaction in block['transactions']:
        transactions.append(str(transaction.to_dict()))

    print (json.dumps(transactions))

    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': transactions}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': str(blockchain.chain),
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The UBcoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app
app.run(host = '127.0.0.1', port = 5000)