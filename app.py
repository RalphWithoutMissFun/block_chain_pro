from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for
from web3.auto import w3
from web3 import Web3
import time
w3 = Web3()
w3.eth.defaultAccount = w3.eth.accounts[0]
mapping = {}
import json
from solc import compile_source
from web3.contract import  ConciseContract

contract_source_code = '''
pragma solidity ^0.4.18;

/**
 * @title SafeMath
 * @dev Math operations with safety checks that revert on error
 */
library SafeMath {
    /**
    * @dev Multiplies two numbers, reverts on overflow.
    */
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
        // benefit is lost if 'b' is also tested.
        // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
        if (a == 0) {
            return 0;
        }

        uint256 c = a * b;
        require(c / a == b);

        return c;
    }

    /**
    * @dev Integer division of two numbers truncating the quotient, reverts on division by zero.
    */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // Solidity only automatically asserts when dividing by 0
        require(b > 0);
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold

        return c;
    }

    /**
    * @dev Subtracts two numbers, reverts on overflow (i.e. if subtrahend is greater than minuend).
    */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a);
        uint256 c = a - b;

        return c;
    }

    /**
    * @dev Adds two numbers, reverts on overflow.
    */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a);

        return c;
    }

    /**
    * @dev Divides two numbers and returns the remainder (unsigned integer modulo),
    * reverts when dividing by zero.
    */
    function mod(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b != 0);
        return a % b;
    }
}

contract flowerFarmer{
    bool public initialized=false; 
    uint256 public seedS_TO_produced_1flower=10000;
    uint256 public STARTING_flower=2; 
    mapping (address => address) public referrals;
    mapping (address => uint256) public virtualValue;
    mapping (address => address) public friendship;
    mapping (address => uint256) public produceflower; 
    mapping (address => uint256) public posseeds;
    mapping (address => uint256) public lastproduced;
    uint256 public marketseeds; 
    function flowerFarmer() public payable{
    }
    function setFirendShip(address friend) public{
        require(initialized);
        if (friendship[msg.sender] == 0 && friend != msg.sender ) {
            friendship[msg.sender] = friend;
        }
    }
    function producedseeds(address ref) public{ 
        require(initialized);
        if(referrals[msg.sender]==0 && ref!=msg.sender){ 
            referrals[msg.sender]=ref; 
        }
        uint256 seedsUsed=getMyseeds(); 
        uint256 newflowers=SafeMath.div(seedsUsed,100); 
        produceflower[msg.sender]=SafeMath.add(produceflower[msg.sender],newflowers); 
        posseeds[msg.sender]=0;
        lastproduced[msg.sender]=now; 
        posseeds[referrals[msg.sender]]=SafeMath.add(posseeds[referrals[msg.sender]],SafeMath.div(seedsUsed,5)); 
        marketseeds=SafeMath.add(marketseeds,SafeMath.div(seedsUsed,10)); 
    }
    function sell() public payable{
        require(initialized); 
        uint256 hasseeds=getMyseeds(); 
        uint256 seedValue=SafeMath.div(hasseeds,5); 
        posseeds[msg.sender]=0; 
        lastproduced[msg.sender]=now; 
        virtualValue[msg.sender] = virtualValue[msg.sender] + seedValue;
    }
    function buy() public payable{
        require(initialized); 
        uint256 seedsBought = SafeMath.mul(virtualValue[msg.sender], 5);
        posseeds[msg.sender]=SafeMath.add(posseeds[msg.sender],seedsBought);
        virtualValue[msg.sender] = 0;
    }
    function setMarket(uint256 seeds) public payable{ 
        require(marketseeds==0); 
        initialized=true; 
        marketseeds=seeds; 
    }
    function getFreeflower() public{
        require(initialized); 
        require(produceflower[msg.sender]==0); 
        lastproduced[msg.sender]=now; 
        produceflower[msg.sender]=STARTING_flower; 
        virtualValue[msg.sender] = 1000;
    }
    function getBalance() public view returns(uint256){ 
        return virtualValue[msg.sender];
    }

    function getMyseeds() public view returns(uint256){ 
        uint256 secondsPassed=min(seedS_TO_produced_1flower,SafeMath.sub(now,lastproduced[msg.sender])); 
        uint256 newer = SafeMath.mul(SafeMath.div(secondsPassed,60),produceflower[msg.sender]);
        return SafeMath.add(posseeds[msg.sender],newer);
    }
    function getMyFlowers() public view returns(uint256){
        return produceflower[msg.sender];
    }
    function min(uint256 a, uint256 b) private pure returns (uint256) { 
        return a < b ? a : b;
    }
}
'''
w3.miner.start(1)
compiled_sol = compile_source(contract_source_code)
contract_interface = compiled_sol['<stdin>:flowerFarmer']

w3.eth.defaultAccount = w3.eth.accounts[0]
Greeter = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

# Submit the transaction that deploys the contract
print(w3.eth.accounts)
tx_hash = Greeter.constructor().transact()

# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

greeter = w3.eth.contract(
    address=tx_receipt.contractAddress,
    abi=contract_interface['abi'],
)
w3.eth.waitForTransactionReceipt(tx_hash)
tx_hash = greeter.functions.setMarket(1000).transact({"from":w3.eth.accounts[0]})
w3.eth.waitForTransactionReceipt(tx_hash)

w3.miner.stop()
app = Flask(__name__)


@app.route('/')
def main_page():
    return render_template("new_account.html")

@app.route('/new_account/<user_name>')
def new_account(user_name):
    w3.miner.start(1)
    user_hash = w3.personal.newAccount(user_name)
    flag = w3.personal.unlockAccount(user_hash, user_name)
    if (flag == False):
        abort(401)
    mapping[user_name] = user_hash
    flag2 = w3.miner.setEtherBase(user_hash)
    w3.miner.start(1)
    time.sleep(120)
    w3.miner.stop()
    print(w3.eth.getBalance(user_hash))
    w3.miner.setEtherBase(w3.eth.accounts[0])
    w3.personal.unlockAccount(w3.eth.accounts[0], "3082485044")
    w3.miner.stop()
    return render_template("initializer.html", user_name=user_name, user_hash=user_hash)

@app.route('/sign')
def sign():
    return render_template("sign.html")
@app.route('/sign_account/<user_name>/sign_hash/<user_hash>')
def sign2(user_name, user_hash):
    # w3.miner.start(1)
    print(user_name)
    print(user_hash)
    flag = w3.personal.unlockAccount( w3.toChecksumAddress(user_hash), user_name)
    if flag == True:
        mapping[user_name] = user_hash
        w3.miner.setEtherBase(mapping[user_name])
        w3.miner.start(1)
        user_flower = greeter.functions.getMyFlowers().transact({"from": mapping[user_name]})
        user_flower = greeter.functions.getMyFlowers().call({"from": mapping[user_name]})
        print("step2")
        user_seed = greeter.functions.getMyseeds().transact({"from": mapping[user_name]})
        user_seed = greeter.functions.getMyseeds().call({"from": mapping[user_name]})
        print("step3")
        user_balance = greeter.functions.getBalance().transact({"from": mapping[user_name]})
        user_balance = greeter.functions.getBalance().call({"from": mapping[user_name]})
        print("step4")
        w3.miner.stop()
        return render_template("main_view.html", user_name=user_name, user_flower=user_flower, user_seed=user_seed,
                               user_balance=user_balance)
    else:
        return render_template("new_account.html")


    w3.miner.stop()
@app.route('/finish_account/<user_name>')
def finish_acount(user_name):
    w3.personal.unlockAccount(w3.eth.accounts[0], "3082485044")
    w3.personal.unlockAccount(mapping[user_name], user_name)
    w3.miner.setEtherBase(mapping[user_name])
    w3.miner.start(1)
    tx_hash = greeter.functions.getFreeflower().transact({"from": mapping[user_name]})
    #print(tx_hash)
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("step1")
    user_flower = greeter.functions.getMyFlowers().transact({"from": mapping[user_name]})
    user_flower = greeter.functions.getMyFlowers().call({"from": mapping[user_name]})
    print("step2")
    user_seed = greeter.functions.getMyseeds().transact({"from": mapping[user_name]})
    user_seed = greeter.functions.getMyseeds().call({"from": mapping[user_name]})
    print("step3")
    user_balance = greeter.functions.getBalance().transact({"from": mapping[user_name]})
    user_balance = greeter.functions.getBalance().call({"from": mapping[user_name]})
    print("step4")
    w3.miner.stop()
    return render_template("main_view.html", user_name=user_name , user_flower=user_flower, user_seed = user_seed, user_balance = user_balance)

@app.route('/sell_account/<user_name>')
def sell_account(user_name):
    w3.miner.setEtherBase(mapping[user_name])
    w3.personal.unlockAccount(w3.eth.accounts[0], "3082485044")
    w3.personal.unlockAccount(mapping[user_name], user_name)
    w3.miner.start(1)
    #tx_hash = greeter.functions.getFreeflower().transact({"from": mapping[user_name]})
    tx_hash = greeter.functions.sell().transact({"from": mapping[user_name]})
    # print(tx_hash)
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("step1")
    user_flower = greeter.functions.getMyFlowers().transact({"from": mapping[user_name]})
    user_flower = greeter.functions.getMyFlowers().call({"from": mapping[user_name]})
    print("step2")
    user_seed = greeter.functions.getMyseeds().transact({"from": mapping[user_name]})
    user_seed = greeter.functions.getMyseeds().call({"from": mapping[user_name]})
    print("step3")
    user_balance = greeter.functions.getBalance().transact({"from": mapping[user_name]})
    user_balance = greeter.functions.getBalance().call({"from": mapping[user_name]})
    print("step4")
    w3.miner.stop()
    return render_template("main_view.html", user_name=user_name, user_flower=user_flower, user_seed=user_seed,user_balance=user_balance)

@app.route('/buy_account/<user_name>')
def buy_account(user_name):
    w3.miner.setEtherBase(mapping[user_name])
    w3.personal.unlockAccount(w3.eth.accounts[0], "3082485044")
    w3.personal.unlockAccount(mapping[user_name], user_name)
    w3.miner.start(1)
    # tx_hash = greeter.functions.getFreeflower().transact({"from": mapping[user_name]})
    tx_hash = greeter.functions.buy().transact({"from": mapping[user_name]})
    # print(tx_hash)
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("step1")
    user_flower = greeter.functions.getMyFlowers().transact({"from": mapping[user_name]})
    user_flower = greeter.functions.getMyFlowers().call({"from": mapping[user_name]})
    print("step2")
    user_seed = greeter.functions.getMyseeds().transact({"from": mapping[user_name]})
    user_seed = greeter.functions.getMyseeds().call({"from": mapping[user_name]})
    print("step3")
    user_balance = greeter.functions.getBalance().transact({"from": mapping[user_name]})
    user_balance = greeter.functions.getBalance().call({"from": mapping[user_name]})
    print("step4")
    w3.miner.stop()
    return render_template("main_view.html", user_name=user_name, user_flower=user_flower, user_seed=user_seed,
                           user_balance=user_balance)

@app.route('/generate_account/<user_name>')
def generate_account(user_name):
    w3.miner.setEtherBase(mapping[user_name])
    w3.personal.unlockAccount(w3.eth.accounts[0], "3082485044")
    w3.personal.unlockAccount(mapping[user_name], user_name)
    w3.miner.start(1)
    rec_name = w3.eth.accounts[0]
    if rec_name not in mapping:
        mapping[rec_name] = w3.eth.accounts[0]
    # tx_hash = greeter.functions.getFreeflower().transact({"from": mapping[user_name]})
    tx_hash = greeter.functions.producedseeds(mapping[rec_name]).transact({"from": mapping[user_name]})
    # print(tx_hash)
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("step1")
    user_flower = greeter.functions.getMyFlowers().transact({"from": mapping[user_name]})
    user_flower = greeter.functions.getMyFlowers().call({"from": mapping[user_name]})
    print("step2")
    user_seed = greeter.functions.getMyseeds().transact({"from": mapping[user_name]})
    user_seed = greeter.functions.getMyseeds().call({"from": mapping[user_name]})
    print("step3")
    user_balance = greeter.functions.getBalance().transact({"from": mapping[user_name]})
    user_balance = greeter.functions.getBalance().call({"from": mapping[user_name]})
    print("step4")
    w3.miner.stop()
    return render_template("main_view.html", user_name=user_name, user_flower=user_flower, user_seed=user_seed,
                           user_balance=user_balance)


if __name__ == '__main__':
    app.run()
