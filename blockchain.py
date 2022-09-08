

from hashlib import sha256

import datetime
import hashlib
import json
from typing import Dict
from urllib.parse import urlparse
import requests

# from transactions import Transaction



class Blockchain:

    def __init__(self):
        self.chain = []
        # below is the list that containing the transactions before they are added
        self.transactions = []
        self.walletdetails = []
        self.connected_nodes = set()
        self.nodes = set()
        # self.create_block(previous_hash='0' * 64)

   # def create_block(self, proof,previous_hash):
       # block_content = {'index': len(self.chain) + 1,

      #           'timestamp': str(datetime.datetime.now()),
       #          'proof': proof,
      #           'previous_hash': previous_hash,
     #            'transactions':self.transactions}
        # all the transactions must become empty because we add the
        # the transaction only once we need to empty thr transaction list
      #  block={'block':block_content,
        #       'hash':self.hash(block_content)

        #   }

       # self.transactions=[]
        # self.addBlockToChain(block)

       # return block

    def create_block(self, previous_hash):
        block_content = {'index': len(self.chain) + 1,
                         'timestamp': str(datetime.datetime.now()),
                         'previous_hash': previous_hash,
                         'transactions': self.transactions}
        mined_block, new_hash = self.mine(block_content)
        block = {'block': mined_block,
                 'hash': new_hash
                }

        self.transactions = []
        self.addBlockToChain(block)

        self.propogate_block()

        return block

    def SHA256(text):
        return sha256(text.encode("ascii")).hexdigest()

    def mine(self, raw_block_content):
        # prefix_str = 0*prefix_zeros
        nonce_searching = True
        new_hash = ""
        nonce = 1
        block_content = raw_block_content
        while nonce_searching:
            block_content['nonce'] = nonce
            #text = str(block_content)
            #new_hash =sha256(text.encode("ascii")).hexdigest()
            new_hash = self.hash(block_content)

            if new_hash.startswith("0000"):
                #print(f"Yay! Successfully mined bitcoins with nonce value:{nonce}", new_hash)
                nonce_searching = False
            nonce = nonce+1
        return block_content, new_hash

    def addBlockToChain(self, block):
        self.chain.append(block)

    # def addBlockToChains(self,new_block):
    #     self.chain.append(new_block)

    def get_previous_block(self):
        return self.chain[-1]['block']

    def get_new_block(self):

        return self.chain

 # 1st pillaar added trasaction is donw by below function
    # def add_transaction(self, sender, receiver, amount, transactionId, is_mining_reward=0):
    #     self.transactions.append({'sender': sender,
    #                               'receiver': receiver,
    #                               'amount': amount,
    #                               'transactionId': transactionId,
    #                               'is_mining_reward': is_mining_reward
    #                             })
    #     print("hi")
    #     previous_block = self.get_previous_block()
    #     print("pr", previous_block)
    #     return previous_block['index']+1


    def add_transaction(self, transaction_data_dict: Dict):

        self.transactions.append(transaction_data_dict)
        # print("--->> ", self.transactions)
        next_block_index = 0
        if len(self.chain) != 0:
            previous_block = self.get_previous_block()
            next_block_index = previous_block['index']+1
        # print("pr", previous_block)
        return next_block_index


    def validate_funds(self, senders_address: bytes, amount: int) -> bool:
        sender_balance = 0
        for block_details in self.chain:
            current_block = block_details['block']
            for transaction_details in current_block['transactions']:
                current_transaction = transaction_details['tx']
                if current_transaction['sender'] == senders_address:
                    sender_balance -= current_transaction['amount']
                if current_transaction['receiver'] == senders_address:
                    sender_balance += current_transaction['amount']

        if amount <= sender_balance:
            return True
        else:
            return False


    # def proof_of_work(self, previous_proof):
    #     new_proof = 1
    #     check_proof = False
    #     while check_proof is False:
    #         hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
    #         if hash_operation[:4] == '0000':
    #             check_proof = True
    #         else:
    #             new_proof += 1
    #     return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]['block']
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]['block']
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # previous_proof = previous_block['proof']
            # proof = block['proof']
            # hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            # if hash_operation[:4] != '0000':
            #     return False
            # previous_block = block
            current_block_hash = self.hash(block)
            if not current_block_hash.startswith("0000"):
                return False
            previous_block = block
            block_index += 1
        return True

    def replace_chains(self):
        print("Inside replace chain")
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
            self.transactions.clear()

            return True
        return False

        # create wallet

    def propogate_block(self):
        network = self.nodes
        for node in network:
            try:
                response = requests.get(f'http://{node}/replace_chain')
                if response.status_code == 200:
                    print("Block propogated")
            except Exception as e:
                pass
        print("Done propogating blocks")

    # consesus pillar function secod pillar

    def add_node(self, address):

        # parse the addrress of the node
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        self.connected_nodes.add(address)

    def get_nodes(self):
        return self.nodes