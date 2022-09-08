


import json
from ecdsa import SigningKey, VerifyingKey, keys, BadSignatureError
import binascii



class Transaction:
    def __init__(self, sender: bytes, receiver: bytes, amount: int, transaction_id:int, is_mining_reward: int = 0, signature: str = "", ):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transaction_id = transaction_id
        self.is_mining_reward = is_mining_reward
        self.signature = signature

    def get_transaction_data(self) -> dict:
        return {
            'tx': self.generate_transaction_data_dict(),
            'signature' : self.signature
        }
    
    def generate_transaction_data_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "transaction_id": self.transaction_id,
            "is_mining_reward": self.is_mining_reward
        }


    def convert_transaction_data_to_bytes(self, transaction_data: dict):
        new_transaction_data = transaction_data.copy()
        new_transaction_data["sender"] = str(transaction_data["sender"])
        new_transaction_data["receiver"] = str(transaction_data["receiver"])
        new_transaction_data["amount"] = str(transaction_data["amount"])
        new_transaction_data['transaction_id'] = str(transaction_data["transaction_id"])
        new_transaction_data["is_mining_reward"] = str(transaction_data["is_mining_reward"])
        return json.dumps(new_transaction_data, indent=2).encode('utf-8')


    def generate_data(self) -> bytes:
            transaction_data_dict = self.generate_transaction_data_dict()
            return self.convert_transaction_data_to_bytes(transaction_data_dict)

    def sign(self, private_key: bytes):
        try:    
            transaction_data = self.generate_data()
            signing_key = SigningKey.from_string(binascii.unhexlify(private_key))
            signature = signing_key.sign(transaction_data)
            self.signature = binascii.hexlify(signature).decode("utf-8")
            return True
        except Exception as e:
            print("Exception --> ", e)
            return False

    def validate_signature(self) -> bool:
        try:
            transaction_data = self.generate_data()
            verifying_key = VerifyingKey.from_string(binascii.unhexlify(self.sender))
            verifying_key.verify(binascii.unhexlify(self.signature), transaction_data)
            print("Valid signature")
            return True
        except ValueError as err:
            print("ValueError --> ", err)
            return False
        except BadSignatureError as err:
            print("BadSignatureError --> ", err)
            return False
        except Exception as e:
            print("Exception --> ", e)
            return False


