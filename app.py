
# Importing the libraries

# import json
from typing import List
from urllib.parse import urlparse
from flask import Flask, jsonify, request
import time
# from uuid import uuid4
import requests
# from eth_account import Account

from blockchain import Blockchain
# python module used for generating random numbers
# import secrets
import random
import os
from transactions import Transaction

from wallet import Account, Wallet

# from wallet111 import generate_new_wallet


# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)



# Creating a Blockchain
blockchain = Blockchain()
mining_reward = 100
wallet = Wallet()
# Mining a new block
current_node_address = ''


def get_random_tx_id() -> int:
    return random.randint(1,999999999)


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
   # previous_proof = previous_block['proof']
   # proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    reward_giver_account = wallet.get_system_account()
    current_node_account = wallet.get_account_for_node_address(current_node_address)
    transaction = Transaction(
        sender= reward_giver_account.public_key, 
        receiver= current_node_account.public_key,
        amount= mining_reward,
        transaction_id=get_random_tx_id(),
        is_mining_reward= 1
    )

    isSigned = transaction.sign(bytes(reward_giver_account.private_key, 'utf-8'))
    if isSigned == False:
        response = {'message': f'Unable to sign mining reward transaction. Please call sync wallet first and re run.'}
        return jsonify(response), 201
    isValidTransaction = transaction.validate_signature()
    if isValidTransaction == False:
        response = {'message': f'Signature validation failed. Please call sync wallet first and re run.'}
        return jsonify(response), 201
    blockchain.add_transaction(transaction.get_transaction_data())
    block_details = blockchain.create_block(previous_hash)
    block = block_details['block']
    new_hash = block_details['hash']
    update_wallet_after_mining(block['transactions'])
    request_to_sync_wallet()
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['nonce'],
                'hash': new_hash,
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
                }
    # transactions is the key of the block dictionary here
    # previous hash -0e301f8b68d80ccc6c510bd9cfa610d294a5dd8772d18ee6ef329d1d0e4b3104
    return jsonify(response), 200



# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Checking if the Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {
            'message': 'Blockchain, have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


# adding new transaction to the blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    print("in add")
    json = request.get_json()
    print(json)
    transaction_keys = ['sender', 'receiver', 'amount', 'sendersPrivateKey']
    if not all(key in json for key in transaction_keys):
        return "Some elements of the transactionare missing", 400
      # status 400 menas bad request

    transaction = Transaction(
        sender= json['sender'], 
        receiver= json['receiver'], 
        amount= json['amount'], 
        transaction_id=get_random_tx_id(),
    )
    
    isSigned = transaction.sign(bytes(json['sendersPrivateKey'], 'utf-8'))
    if isSigned == False:
        response = {'message': f'Unable to sign the transaction. Please check your private key.'}
        return jsonify(response), 201

    isValidTransaction = transaction.validate_signature()
    if isValidTransaction == False:
        response = {'message': f'Signature validation failed. Please check your private key.'}
        return jsonify(response), 201

    isValidFund = blockchain.validate_funds(transaction.sender, transaction.amount)
    if isValidFund == False:
        response = {'message': f'The amount mentioned in the transaction is not valid.'}
        return jsonify(response), 201

    # index = blockchain.add_transaction(
    #     json['sender'], json['receiver'], json['amount'], json['transactionId'])
    index = blockchain.add_transaction(transaction.get_transaction_data())

    

    response = {'message': f'This transaction will be added to Block  {index}'}
    return jsonify(response), 201


# crearte wallet api
# @app.route('/create_wallet', methods=['GET'])
# def create_wallet():

#     priv = secrets.token_hex(32)

# # Attaching 0x prefix to our 64 character hexadecimal string stored in priv and storing the new string in variable private_key
#     private_key = "0x" + priv
#     print("SAVE BUT DO NOT SHARE:", private_key)

# # Creating a new account using the private_key and storing it in variable acct
#     acct = Account.from_key(private_key)
#     print("Address:", acct.address)
#     response = {'message': 'Congratulations, you just mined a block!',
#                 'privateKey': priv,
#                 'publicKey': acct.address,
#                 'amount': 90,
#                 'gaslimit': 2000,
#                 'coinname': "pdCoin",
#                 }

#     # transactions is the key of the block dictionary here
#     # previous hash -0e301f8b68d80ccc6c510bd9cfa610d294a5dd8772d18ee6ef329d1d0e4b3104
#     return jsonify(response), 200


# crearte wallet api
@app.route('/create_wallet/<number>', methods=['GET'])
def create_wallet(number):
    for x in range(int(number)):
        create_account('')
    
    request_to_sync_wallet()
    response = {'accounts': wallet.get_user_accounts_dicts()
                }
    return jsonify(response), 200




# Part 3 decentralising blockchain

# connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The PDCoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201
# replaceing the chain by  the longest chain if needed
# Still need to figure out when i should call replace_chain web service


@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    # print(blockchain.nodes)
    response = {'nodes': list(blockchain.connected_nodes)
                }
    # response = {'nodes': db.get_nodes_dicts()
    #             }
    return jsonify(response), 200



@app.route('/get_all_accounts', methods=['GET'])
def get_accounts():
    response = {'accounts': wallet.get_accounts_dicts()
                }
    return jsonify(response)


@app.route('/get_user_accounts', methods=['GET'])
def get_user_accounts():
    response = {'accounts': wallet.get_user_accounts_dicts()
                }
    return jsonify(response)

@app.route('/get_node_accounts', methods=['GET'])
def get_node_accounts():
    response = {'accounts': wallet.get_node_accounts_dicts()
                }
    return jsonify(response)


@app.route('/sync_wallet', methods=['GET'])
def sync_wallet():
    update_network_wallet()
    response = {'success': True }
    return jsonify(response)


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chains()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


@app.route('/create_genesis_block', methods=['GET'])
def genesis_block():
    create_genesis_block()
    response = {'message': 'Genesis block created'}
    return jsonify(response), 200



@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    blockchain.transactions
    response = {'message': 'All transactions',
                
                'transactions' :blockchain.transactions}
    return jsonify(response), 200


def update_wallet_after_mining(transactions_dicts: List[dict]):
    # update blocks minded property from current node's account 
    current_node_account = wallet.get_account_for_node_address(current_node_address)
    # print("current_node_account ", current_node_account.account_owner)
    current_node_account.blocks_mined += 1
    current_node_account.updated_at = time.time() * 1000
    wallet.upsert_account(current_node_account)

    system_account = wallet.get_system_account()

    # update accounts based on transactions
    for transaction_dict in transactions_dicts:
        transaction = Transaction(
            sender= transaction_dict['tx']['sender'],
            receiver= transaction_dict['tx']['receiver'],
            amount= transaction_dict['tx']['amount'],
            is_mining_reward=transaction_dict['tx']['is_mining_reward'],
            signature=transaction_dict['signature'],
            transaction_id=transaction_dict['tx']['transaction_id'],
        )
        sender_account = wallet.get_account_for_public_key(transaction.sender)
        receiver_account = wallet.get_account_for_public_key(transaction.receiver)
        receiver_account.coins += transaction.amount
        if transaction.is_mining_reward == 1:
            receiver_account.reward_amount += transaction.amount
        receiver_account.updated_at = time.time() * 1000
        wallet.upsert_account(receiver_account)
        if transaction.sender != system_account.public_key:
            sender_account.coins -= transaction.amount
            sender_account.updated_at = time.time() * 1000
            wallet.upsert_account(sender_account)



# decentralising the blockchian# adding trasaction to blopacjchain is 1st pillar
# consuse function is the second pillar
# once some new transactions are integrated to a mew block which is added
# to the blockchain we need to make sure that all the nodes in the networl get also their chain updated
# with last mined block containg the transactions in this particular check is caalled
# consensus
    

def request_to_sync_wallet():
    for node_address in blockchain.get_nodes():
        try:
            requests.get(f'http://{node_address}/sync_wallet')
        except requests.exceptions.ConnectionError as connErr:
            print("Error -> ", connErr)


def create_genesis_block():
    for x in range(4):
        create_account('', 10)
    system_account = wallet.get_system_account()
    for account in wallet.get_user_accounts():
        transacton = Transaction(
            sender= system_account.public_key,
            receiver= account.public_key,
            amount= 100,
            transaction_id=get_random_tx_id(),
        )
        transacton.sign(system_account.private_key)
        transacton.validate_signature()
        blockchain.add_transaction(transacton.get_transaction_data())
    current_node_account = wallet.get_account_for_node_address(current_node_address)
    mining_reward_transacton = Transaction(
        sender= system_account.public_key,
        receiver= current_node_account.public_key,
        amount= mining_reward,
        transaction_id=get_random_tx_id(),
        is_mining_reward= 1
    )
    mining_reward_transacton.sign(system_account.private_key)
    mining_reward_transacton.validate_signature()
    blockchain.add_transaction(mining_reward_transacton.get_transaction_data())
    block_details = blockchain.create_block(previous_hash='0' * 64)
    block = block_details['block']
    update_wallet_after_mining(block['transactions'])
    request_to_sync_wallet()


def update_network_wallet():
    for node_address in blockchain.get_nodes():
        try:
            response = requests.get(f'http://{node_address}/get_all_accounts')
            if response.status_code == 200:
                accounts = response.json()['accounts']
                for account in accounts:
                    wallet.upsert_account(Account(
                        private_key=account['private_key'], 
                        public_key=account['public_key'], 
                        updated_at=account['updated_at'],
                        coins=account['coins'],
                        is_node_account=account['is_node_account'],
                        account_owner=account['account_owner'],
                        reward_amount=account['reward_amount'],
                        blocks_mined=account['blocks_mined']
                    ))
        except requests.exceptions.ConnectionError as connErr:
            print("Error -> ", connErr)


def create_account(address: str, initial_coins:int = 90, is_node_account: bool = False, is_current_node_account: bool = False) -> Account:
    parsed_url = urlparse(address)
    private_key, public_key = Wallet.generate_new_wallet()
    account_owner = parsed_url.netloc 
    if address == 'SYSTEM':
        account_owner = address 
    account = Account(
        private_key=private_key, 
        public_key=public_key, 
        updated_at=time.time() * 1000,
        coins=initial_coins,
        is_node_account=is_node_account,
        account_owner= account_owner,
        reward_amount=0
    )
    wallet.upsert_account(account)
    if is_current_node_account:
        global current_node_address 
        current_node_address = parsed_url.netloc
        print("Current node address ", current_node_address)
    return account





def setup_nodes():
    if os.environ.get('FLASK_RUN_PORT'):
        blockchain.add_node("http://127.0.0.1:" +os.environ.get('FLASK_RUN_PORT'))
        create_account("http://127.0.0.1:" +os.environ.get('FLASK_RUN_PORT'), 0, True, True)
        if os.environ.get('FLASK_RUN_PORT') == '5000':
            create_account('SYSTEM')
    if os.environ.get('OTHER_NODE_ONE_ADDR'):
        blockchain.add_node(os.environ.get('OTHER_NODE_ONE_ADDR'))
        # add_node(os.environ.get('OTHER_NODE_ONE_ADDR'), False)
    if os.environ.get('OTHER_NODE_TWO_ADDR'):
        blockchain.add_node(os.environ.get('OTHER_NODE_TWO_ADDR'))
        # add_node(os.environ.get('OTHER_NODE_TWO_ADDR'), False)



setup_nodes()

# app.run(host = '0.0.0.0', port = os.environ.get('FLASK_RUN_PORT'))