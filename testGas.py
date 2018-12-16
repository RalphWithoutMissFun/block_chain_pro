from web3.auto import w3
from web3 import Web3
w3 = Web3()
import time

import json
from solc import compile_source
from web3.contract import  ConciseContract
user_name = "hanmeili"
user_hash = w3.personal.newAccount(user_name)
flag = w3.personal.unlockAccount(user_hash, user_name)
flag2 = w3.miner.setEtherBase(user_hash)
print(flag2)

#w3.eth.defaultAccount = user_hash
w3.miner.start(1)
time.sleep(100)
w3.miner.stop()
print(w3.eth.getBalance(user_hash))
w3.miner.setEtherBase(w3.eth.accounts[0])