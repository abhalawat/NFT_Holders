from distutils.log import error
import json
from mimetypes import init
import time
from time import sleep
from tracemalloc import start
from unicodedata import name
from web3 import Web3
from web3.middleware import geth_poa_middleware
import pymongo
from pymongo import MongoClient
import asyncio

cluster = MongoClient("mongodb://127.0.0.1:27017")

db = cluster['Holders']
collection = db['holders']
infura_url= "wss://mainnet.infura.io/ws/v3/57d8e5ec16764a3e86ce18fc505e640e"
web3 = Web3(Web3.WebsocketProvider(infura_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)  #  Inject poa middleware 


#load json file
file = open('contract.json','r')
data = json.load(file)
data = data['NFTHolders']

def holdersEvent(_fromBlock, _toBlock,contract,address):
    try:
        transferEvents = contract.events.Transfer.createFilter(fromBlock=_fromBlock, toBlock=_toBlock)
        for i in range(len(transferEvents.get_all_entries())):
            addressTo = transferEvents.get_all_entries()[i].args.to
            print(addressTo)
            collection.insert_one({"Contractaddress":address,"holderAddress": addressTo})
    except asyncio.TimeoutError: 
        pass
    
def holdersContract():
    for i in range(len(data)):
        address= data[i]["address"]
        tx_hash = data[i]['tx_hash']
        abi = json.load(open('abi{0}.json'.format(i),'r'))
        contract = web3.eth.contract(address=address,abi=abi)
        latest = web3.eth.blockNumber
        firstBlock = web3.eth.getTransactionReceipt(tx_hash).blockNumber
        totalResult = latest - firstBlock

        initial = firstBlock
        if totalResult >2000:
            while totalResult>=2000:
                fromBlock = initial
                toBlock = initial +2000
                holdersEvent(fromBlock,toBlock,contract,address)
                totalResult = totalResult -2000
                initial = toBlock
            if totalResult != 0:
                fromBlock = initial
                toBlock = initial + totalResult
                holdersEvent(fromBlock,toBlock,contract,address)
        else:
            holdersEvent(firstBlock,latest,contract,address)

if __name__=="__main__":
    holdersContract()




