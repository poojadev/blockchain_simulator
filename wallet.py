

from typing import List

from ecdsa import SigningKey
import binascii
# To install dependencies use following command 
# pip3 install -r /path/to/requirements.txt
# pip3 install -r ./requirements.txt

# class Node():
#     def __init__(self, address: str, private_key: str, public_key:str):
#         self.address = address
#         self.private_key = private_key
#         self.public_key = public_key


class Account():
    def __init__(self, private_key: str, public_key:str, updated_at: int,coins: int = 100, is_node_account: bool = False, account_owner: str = "", reward_amount: int = 0, blocks_mined:int = 0):
        self.private_key = private_key
        self.public_key = public_key
        self.updated_at = updated_at
        self.coins = coins
        self.is_node_account = is_node_account
        self.account_owner = account_owner
        self.reward_amount = reward_amount
        self.blocks_mined = blocks_mined


        


class Wallet:
    def __init__(self,  accounts: List[Account] = []):
        self.accounts = accounts

    @staticmethod
    def generate_new_wallet():
        sk = SigningKey.generate() 
        vk = sk.verifying_key
        private_key = sk.to_string()
        public_key = vk.to_string()
        return binascii.hexlify(private_key).decode('utf8'),  binascii.hexlify(public_key).decode('utf8')

    def get_dicts(self, accounts: List[Account]):
        dicts = []
        for account in accounts:
            dicts.append(account.__dict__)
        return dicts

    
    def upsert_account(self, accountToAdd: Account):
        for index, account in enumerate(self.accounts):
            if account.public_key == accountToAdd.public_key:
                if account.updated_at < accountToAdd.updated_at:
                    self.accounts[index] = accountToAdd
                return self.accounts
        
        self.accounts.append(accountToAdd)
        return self.accounts

    def get_accounts(self) -> List[Account]:
        return self.accounts
    
    def get_accounts_dicts(self):
        # jsons = []
        # for account in self.get_accounts():
        #     jsons.append(account.__dict__)
        return self.get_dicts(self.get_accounts())

    def clear_accounts(self):
        self.accounts = []
        return self.get_accounts()

    def get_account_for_node_address(self, address: str)-> Account:
        for account in self.get_accounts():
            if account.account_owner == address:
                return account
    
    def get_account_for_public_key(self, public_key: str) -> Account:
        for account in self.get_accounts():
            if account.public_key == public_key:
                return account

    def get_system_account(self) -> Account:
        for account in self.get_accounts():
            if account.account_owner == 'SYSTEM':
                return account

    def get_node_accounts(self) -> List[Account]:
        node_accounts = []
        for account in self.get_accounts():
            if account.account_owner != '' and account.account_owner != 'SYSTEM':
                node_accounts.append(account)
        return node_accounts

    def get_node_accounts_dicts(self):
        return self.get_dicts(self.get_node_accounts())

    def get_user_accounts(self) -> List[Account]:
        user_accounts = []
        for account in self.get_accounts():
            if account.account_owner == '':
                user_accounts.append(account)
        return user_accounts

    def get_user_accounts_dicts(self):
        return self.get_dicts(self.get_user_accounts())