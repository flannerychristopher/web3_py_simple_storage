import json
from solcx import compile_standard, install_solc
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.6")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# deploy contract

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0xA5262230F7ef7F37a0Ab35591f7C97f1B273E877"
private_key = os.getenv("PRIVATE_KEY")
print(private_key)

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
print(SimpleStorage)

nonce = w3.eth.getTransactionCount(my_address)
print(nonce)

transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
print(transaction)

signed_transaction = w3.eth.account.sign_transaction(
    transaction, private_key=private_key
)
print(signed_transaction)

transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
print(transaction_hash)

transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print(transaction_hash)

# work with contract
simple_storage = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_transaction = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
transaction_hash = w3.eth.send_raw_transaction(signed_store_transaction.rawTransaction)
stored_transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print(stored_transaction_receipt)

print(simple_storage.functions.retrieve().call())
