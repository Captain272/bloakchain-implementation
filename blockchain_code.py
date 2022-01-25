from hashlib import sha256
from flask import Flask, request
import requests
import json
import time
from flask import Flask,render_template,redirect,request,url_for
from flask_toastr import Toastr
from flask import flash
import secrets

secret = secrets.token_urlsafe(32)


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain: 
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()
 
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
    @property
    def last_block(self):
        return self.chain[-1]

    difficulty = 2
    def proof_of_work(self, block):
            block.nonce = 0
            computed_hash = block.compute_hash()
            while not computed_hash.startswith('0' * Blockchain.difficulty):
                block.nonce += 1
                computed_hash = block.compute_hash()
            return computed_hash

    def add_block(self, block, proof):
            previous_hash = self.last_block.hash
            if previous_hash != block.previous_hash:
                return False
            if not self.is_valid_proof(block, proof):
                return False
            block.hash = proof
            self.chain.append(block)
            return True
     
    def is_valid_proof(self, block, block_hash):
            return (block_hash.startswith('0' * Blockchain.difficulty) and
                    block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
                self.unconfirmed_transactions.append(transaction)
     
    def mine(self):
            if not self.unconfirmed_transactions:
                return False
     
            last_block = self.last_block
     
            new_block = Block(index=last_block.index + 1,
                              transactions=self.unconfirmed_transactions,
                              timestamp=time.time(),
                              previous_hash=last_block.hash)
     
            proof = self.proof_of_work(new_block)
            self.add_block(new_block, proof)
            self.unconfirmed_transactions = []
            return new_block.index


toastr = Toastr()

# def create_app(config):
app = Flask(__name__)
app.secret_key = secret    
toastr = Toastr(app)
toastr.init_app(app)


# app = create_app(prod_config)
 
blockchain = Blockchain()


# chain_data=[]

@app.route('/chain',methods=['GET','POST'])
def get_chain():

    if request.method == 'GET':
        chain_data=[]
        for block in blockchain.chain:
            chain_data.append(block.__dict__)
        data=json.dumps({"length": len(chain_data),
                           "chain": chain_data})
        return render_template('index.html',chain_data=chain_data)

    elif request.method =='POST':
        data=request.form['transaction_data']
        transaction=[data]
        print(len(transaction))
        print(transaction)

        if(transaction[0]==''):
            flash("Transaction Data Empty")
            print("Transaction Data Empty")
            chain_data = []
            for block in blockchain.chain:
                chain_data.append(block.__dict__)
            data=json.dumps({"length": len(chain_data),
                               "chain": chain_data})
            return render_template('index.html',chain_data=chain_data)
        else:
            blockchain.add_new_transaction(transaction)
            prev=time.time()
            blockchain.mine()
            after=time.time()

            total=str (after-prev) + ' Sec'
            chain_data = []
            for block in blockchain.chain:
                chain_data.append(block.__dict__)
            data=json.dumps({"length": len(chain_data),
                               "chain": chain_data})
            return render_template('index.html',chain_data=chain_data,total=total)

app.run(debug=True, port=5000)

