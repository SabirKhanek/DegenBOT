import telebot
import telegram
from telebot import types
import time
from web3 import Web3
import json
import pickle
import requests
from github import Github
from num2words import num2words


class obj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)


def getLiquidity(contract_address):
    pcs_router = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
    WBNB = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
    contract_address = web3.toChecksumAddress(contract_address)

    pcs_contract = getContract(pcs_router)

    pair_address = pcs_contract.functions.getPair(contract_address, WBNB).call()

    token_contract = getContract(contract_address)

    lp_holding_balance = token_contract.functions.balanceOf(pair_address).call()

    lp_holding_balance = decToAmount(contract_address, lp_holding_balance)

    token_price = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', contract_address)

    lp_holding_balance = float(lp_holding_balance) * float(token_price)

    return lp_holding_balance


def amountToDec(address, amount):
    try:
        totokencontract = getContract(address)
        if totokencontract == 0:
            raise
    except:
        raise

    decimals = totokencontract.functions.decimals().call()

    return amount * pow(10, decimals)


def decToAmount(address, amount):
    try:
        totokencontract = getContract(address)
        if totokencontract == 0:
            raise
    except:
        raise

    decimals = totokencontract.functions.decimals().call()

    return amount / pow(10, decimals)


def isTxn(txn_hash):
    try:
        web3.eth.getTransaction(txn_hash)
        return True
    except:
        return False


def getTxn(txn_hash):
    try:
        PancakeSwap = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
        txn = web3.eth.getTransaction(txn_hash)
        print(txn)
        txn_hash = "Transaction Hash: " + txn_hash + "\n\n"
        from_address = "From: " + str(txn.get('from')) + "\n"
        interacted_with = "To: " + str(txn.get('to')) + "\n\n"
        if str(txn.get('to')) == PancakeSwap:
            interacted_with = 'Interacted with: PancakeSwap: Router v2' + "\n\n"
        if str(txn.get('to')) == 'None':
            interacted_with = 'Interacted with: None (It means that a contract may be created or something else.)' + \
                              "\n\n "
        gas = "Gas: " + str(txn.get('gas')) + " WEI" + "\n"
        gasPrice = "Gas Price: " + str(txn.get('gasPrice')) + " (" + str(
            web3.fromWei(txn.get('gasPrice'), 'gwei')) + ' GWEI)' + "\n"
        txn_fee = "Transaction Fee: " + str(web3.fromWei(txn.get('gas') * txn.get('gasPrice'), 'ether')) + ' BNB' + "\n"
        value = "Value: " + str(txn.get('value')) + "\n\n"
        transactioncount = "Transaction count: " + str(txn.get('transactionIndex')) + "\n"
        block_number = "Block Number: " + str(txn.get('blockNumber')) + "\n\n"
        mess_text = txn_hash + block_number + from_address +\
                    interacted_with + gas + gasPrice + txn_fee + value + transactioncount
        return mess_text
    except:
        return


def getPancake(address):
    token_address = web3.toChecksumAddress(address)
    API_ENDPOINT = 'https://api.pancakeswap.info/api/v2/tokens/' + token_address

    r = requests.get(url=API_ENDPOINT)
    response = r.json()
    TokenData = json.loads(json.dumps(response), object_hook=obj)
    TokenData = TokenData.data

    return TokenData


def getContract(address):
    try:
        address = web3.toChecksumAddress(address)

        url_bsc = 'https://api.bscscan.com/api'
        contract_address = web3.toChecksumAddress(address)
        API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + str(contract_address) + \
                       "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"

        r = requests.get(url=API_ENDPOINT)
        response = r.json()
        abi = json.loads(response["result"])

        contract = web3.eth.contract(address=contract_address, abi=abi)
        return contract
    except:
        return 0


def getPrice(totoken, fromtoken, amount=1):
    try:
        totokencontract = getContract(fromtoken)
        if totokencontract == 0:
            raise
    except:
        raise

    decimals = totokencontract.functions.decimals().call()

    tokentosell = str(amount * (pow(10, int(decimals))))

    url_api = 'https://bsc.api.0x.org/swap/v1/quote?buyToken='
    totoken = web3.toChecksumAddress(totoken)
    fromtoken = web3.toChecksumAddress(fromtoken)

    API_ENDPOINT = url_api + totoken + '&sellToken=' + fromtoken + '&sellAmount=' + tokentosell + \
                   '&excludedSources=BakerySwap,Belt,DODO,DODO_V2,Ellipsis,Mooniswap,MultiHop,' \
                   'Nerve,SushiSwap,Smoothy,ApeSwap,CafeSwap,CheeseSwap,JulSwap,LiquidityProvider'

    r = requests.get(url=API_ENDPOINT)
    response = r.json()

    price = response.get("price")
    return price


def isWallet(address):
    address = web3.toChecksumAddress(address)
    return web3.eth.getCode(address) == web3.eth.getCode('0x497089B11903B5946f41C700c9479A13DFf5BB23')


def isRenounced(token_address, abi):
    burn_address = ['0x000000000000000000000000000000000000dEaD',
                    '0x0000000000000000000000000000000000000000',
                    '0x0000000000000000000000000000000000000001']
    contract_address = web3.toChecksumAddress(token_address)
    contract = web3.eth.contract(address=contract_address, abi=abi)
    if str(contract.functions.owner().call()) in burn_address:
        return 'Renounced'
    else:
        return 'Not renounced'


def burntPercentage(token_address, abi, supply):
    contract_address = web3.toChecksumAddress(token_address)

    query_address_1 = web3.toChecksumAddress('0x000000000000000000000000000000000000dEaD')
    query_address_2 = web3.toChecksumAddress('0x0000000000000000000000000000000000000000')
    query_address_3 = web3.toChecksumAddress('0x0000000000000000000000000000000000000001')

    contract = web3.eth.contract(address=contract_address, abi=abi)
    token_balance_1 = ('%.5f' % decToAmount(address=contract_address,
                                            amount=contract.functions.balanceOf(query_address_1).call()))
    token_balance_2 = ('%.5f' % decToAmount(address=contract_address,
                                            amount=contract.functions.balanceOf(query_address_2).call()))
    token_balance_3 = ('%.5f' % decToAmount(address=contract_address,
                                            amount=contract.functions.balanceOf(query_address_3).call()))

    total_tokens_burnt = float(token_balance_1) + float(token_balance_2) + float(token_balance_3)

    burnt_percentage = total_tokens_burnt / float(supply) * 100
    burnt_percentage = ('%.2f' % burnt_percentage)

    return burnt_percentage


def getTokenInfo(token_address):
    try:
        print('here')
        isVerified = 'NOT VERIFIED ❌'
        url_bsc = 'https://api.bscscan.com/api'
        contract_address = web3.toChecksumAddress(token_address)
        API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + str(contract_address) + \
                       "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"

        try:
            r = requests.get(url=API_ENDPOINT)
            response = r.json()
            abi = json.loads(response["result"])
            isVerified = 'VERIFIED ✓'
        except:
            API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + \
                           '0x984aE7a0E32Ae2813831b3d082650E1ECA7A1996' + \
                           "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"
            r = requests.get(url=API_ENDPOINT)
            response = r.json()
            abi = json.loads(response["result"])

        contract = web3.eth.contract(address=contract_address, abi=abi)

        try:
            TokenData = getPancake(contract_address)
            name = TokenData.name
            symbol = TokenData.symbol
        except:
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()

        price = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', contract_address)
        BNB_price = getPrice(contract_address, '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')
        BNB_rate = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')

        LP_Holdings_USD = getLiquidity(contract_address)
        LP_Holdings_BNB = float(LP_Holdings_USD) / float(BNB_rate)

        print(BNB_price)
        print(LP_Holdings_BNB)

        supply_wei = contract.functions.totalSupply().call()

        decimals = pow(10, contract.functions.decimals().call())

        supply = supply_wei / decimals

        try:
            renounced_stat = isRenounced(token_address, abi=abi)
        except:
            renounced_stat = 'NULL'
        burn = burntPercentage(token_address, abi=abi, supply=supply)

        mcap = float(price) * int(supply)

        mcap_lp_ratio = int(mcap / LP_Holdings_USD)

        mcap_lp_ratio = '1:' + str(mcap_lp_ratio)
        LP_Holdings_USD = format(int(LP_Holdings_USD), ',') + ' $'
        LP_Holdings_BNB = ('%.2f' % LP_Holdings_BNB) + ' BNB'

        try:
            mcap_exc_burnt = str(int(int(mcap) - (float(price) * (float(burn) / 100) * int(supply))))
        except:
            mcap_exc_burnt = mcap

        try:
            mcap_in_words_index = num2words(str(mcap_exc_burnt)).index(',')
            mcap_in_words = 'Around ' + num2words(str(mcap_exc_burnt))[0:mcap_in_words_index]
        except:
            mcap_in_words = num2words(str(mcap_exc_burnt))

        try:
            supply_in_words_index = num2words(str(supply)).index(',')
            supply_in_words = 'Around ' + num2words(str(supply))[0:supply_in_words_index]
        except:
            supply_in_words = num2words(str(supply))

            mcap_exc_burnt = int(mcap_exc_burnt)

        return_text = ("*CA:* " + str(contract_address) + '\n\n'
                                                          "*Token name:* " + name + '\n' +
                       "*1 BNB:* " + '%.2f' % float(BNB_rate) + " $\n" +
                       "*Token supply:* " + format(int(supply), ',') + " (≈ " + str(supply_in_words) + ')\n' +
                       "*Symbol:* " + symbol + '\n\n' +
                       "*price:* " + '%.16f' % float(price) + " $" + "\n"
                                                                     "*1 BNB:* " + '%.2f' % float(BNB_rate) + " $\n" +
                       "*1 BNB:* " + '%.2f' % float(BNB_price) + " " + symbol + "\n\n"
                                                                                "*Market Cap: * " + format(
                    int(mcap_exc_burnt), ',') + ' $ ' +
                       " (≈ " + mcap_in_words + ") " + "\n\n" +
                       "*LP Holdings: *" + LP_Holdings_BNB + " ( " + LP_Holdings_USD + ")\n" +
                       "*Liquidity to MCAP ratio: *" + mcap_lp_ratio + "\n\n" +
                       "*Ownership:* " + str(renounced_stat) + '\n' +
                       "*Burnt tokens:* " + str(burn) + '%' + '\n' +
                       "*Verification status:* CONTRACT " + isVerified + '\n'
                       )

        print(return_text)
        return return_text

    except Exception as e:
        print(e)
        try:
            contract_address = web3.toChecksumAddress(token_address)
            contract = getContract(contract_address)
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            supply_wei = contract.functions.totalSupply().call()
            decimals = pow(10, contract.functions.decimals().call())
            supply = supply_wei / decimals

            mess_text = ("*Token name:* " + name + "\n*Symbol:* " + symbol +
                         "\n*Supply: *" + supply + "\n\n*Price and other information cannot be"
                                                   "fetched now because it's probably not launched yet. Check another "
                                                   "time...*")
            return mess_text
        except:
            return "Contract address: " + str(token_address) + " is not supported"


def getInfo(token_address, wallet_address):
    token_address = web3.toChecksumAddress(token_address)
    wallet_address = web3.toChecksumAddress(wallet_address)
    try:
        isVerified = 'NOT VERIFIED ❌'
        url_bsc = 'https://api.bscscan.com/api'
        contract_address = web3.toChecksumAddress(token_address)
        API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + str(contract_address) + \
                       "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"

        try:
            r = requests.get(url=API_ENDPOINT)
            response = r.json()
            abi = json.loads(response["result"])
            isVerified = 'VERIFIED ✓'
        except:
            API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + \
                           "0x984aE7a0E32Ae2813831b3d082650E1ECA7A1996" + \
                           "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"

            r = requests.get(url=API_ENDPOINT)
            response = r.json()
            abi = json.loads(response["result"])

        query_address = web3.toChecksumAddress(wallet_address)

        contract = web3.eth.contract(address=contract_address, abi=abi)

        token_balance = ('%.3f' % decToAmount(token_address, contract.functions.balanceOf(query_address).call()))

        try:
            TokenData = getPancake(contract_address)
            name = TokenData.name
            symbol = TokenData.symbol
        except:
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()

        price = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', contract_address)
        BNB_price = getPrice(contract_address, '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')
        BNB_rate = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')

        LP_Holdings_USD = getLiquidity(contract_address)
        LP_Holdings_BNB = float(LP_Holdings_USD) / float(BNB_rate)

        supply_wei = contract.functions.totalSupply().call()
        decimals = pow(10, contract.functions.decimals().call())

        balance = float(token_balance) * float(price)
        supply = supply_wei / decimals
        burn = burntPercentage(token_address, abi=abi, supply=supply)
        mcap = float(price) * int(supply)
        mcap_lp_ratio = int(mcap / LP_Holdings_USD)

        mcap_lp_ratio = '1:' + str(mcap_lp_ratio)

        LP_Holdings_USD = format(int(LP_Holdings_USD), ',') + ' $'
        LP_Holdings_BNB = ('%.2f' % LP_Holdings_BNB) + ' BNB'
        try:
            mcap_exc_burnt = str(int(int(mcap) - (float(price) * (float(burn) / 100) * int(supply))))
        except:
            mcap_exc_burnt = str(mcap)

        try:
            mcap_in_words_index = num2words(str(mcap_exc_burnt)).index(',')
            mcap_in_words = 'Around ' + num2words(str(mcap_exc_burnt))[0:mcap_in_words_index]
        except:
            mcap_in_words = num2words(int(mcap_exc_burnt))
        try:
            supply_in_words_index = num2words(str(supply)).index(',')
            supply_in_words = 'Around ' + num2words(str(supply))[0:supply_in_words_index]
        except:
            supply_in_words = num2words(str(supply))

        return_text = "*Token Address: *" + str(contract_address) + "\n\n" \
                                                                    "*Token name:* " + name + "\n" + \
                      "*Token supply:* " + \
                      format(int(supply), ',') + " (≈ " + supply_in_words + ")\n" \
                      + "*Symbol:* " + symbol + "\n\n" + "*price:* " + '%.16f' % float(price) + " $" + "\n" \
                      + "*1 BNB:* " + '%.2f' % float(BNB_rate) + " $\n" \
                      + "*1 BNB:* " + '%.5f' % float(BNB_price) + " " + symbol + "\n\n" \
                      + "*Market Cap:* " + format(int(mcap_exc_burnt), ',') + ' $ ' + \
                      " (≈ " + mcap_in_words + ") " + "\n\n" + \
                      "*LP Holdings: *" + LP_Holdings_BNB + " ( " + LP_Holdings_USD + ")\n" + \
                      "*Liquidity to MCAP ratio: *" + mcap_lp_ratio + "\n\n" + \
                      "*Token Balance:* " + format(float(token_balance), ',') + "\n" + \
                      "*Balance $:* " + format(float(balance), ',') + "$" + "\n\n" \
                      + "*Burnt tokens:* " + str(burn) + '%' + "\n\n" + \
                      "*Verification status: CONTRACT " + str(isVerified) + "*" + '\n'

        return return_text

    except Exception as e:
        print(e)
        try:
            contract_address = web3.toChecksumAddress(token_address)
            contract = getContract(contract_address)
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            supply_wei = contract.functions.totalSupply().call()
            decimals = pow(10, contract.functions.decimals().call())
            supply = supply_wei / decimals

            mess_text = ("*Token name:* " + name + "\n*Symbol:* " + symbol +
                         "\n*Supply: *" + supply + "\n\n*Price and other information cannot be"
                                                   "fetched now because it's probably not launched yet. Check another "
                                                   "time...*")
            return mess_text
        except:
            return 'Whoops! can\'t fetch data of this token... Kindly check contract address...'


def getSymbol(token_address):
    try:
        url_bsc = 'https://api.bscscan.com/api'
        contract_address = web3.toChecksumAddress(token_address)
        API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + str(contract_address) + \
                       "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"

        r = requests.get(url=API_ENDPOINT)
        response = r.json()
        abi = json.loads(response["result"])

        contract = web3.eth.contract(address=contract_address, abi=abi)
        return contract.functions.symbol().call()
    except:
        return 'Token address is not supported...'


def bnbbalance(walletaddress):
    try:
        balance = web3.eth.get_balance(walletaddress)
        humanreadable_balance = web3.fromWei(balance, 'ether')
        humanreadable_balance = '%.5f' % float(humanreadable_balance)

        # BNB_price = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56',
        # '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c') humanreadable_balance = '\nBNB price: ' + BNB_price +
        # '\nBalance in USD: ' + str(BNB_price*balance)

        return humanreadable_balance
    except:
        return 'null'


def tokenbalance(wallet_address, req_symbol):
    contract_address = web3.toChecksumAddress(registered_tokens.get(req_symbol))
    try:
        url_bsc = 'https://api.bscscan.com/api'
        API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + str(contract_address) + \
                       "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"

        r = requests.get(url=API_ENDPOINT)
        response = r.json()
        abi = json.loads(response["result"])

        query_address = web3.toChecksumAddress(wallet_address)

        contract = web3.eth.contract(address=contract_address, abi=abi)

        token_balance = ('%.5f' % decToAmount(contract_address, contract.functions.balanceOf(query_address).call()))

        return token_balance
    except:
        return 'null'


def getPortfolio(addresss):
    BNB = bnbbalance(addresss)
    BNB_price = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')
    BNB_balance = float(BNB_price) * float(BNB)
    BNB_balance = "{:.2f}".format(BNB_balance)
    print(BNB_balance)
    BUSD = tokenbalance(addresss, 'BUSD')
    print(BUSD)
    USDT = tokenbalance(addresss, 'USDT')
    ETH = tokenbalance(addresss, 'ETH')
    ETH_price = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', registered_tokens.get('ETH'))
    ETH_balance = float(ETH_price) * float(ETH)
    ETH_balance = "{:.2f}".format(ETH_balance)
    XRP = tokenbalance(addresss, 'XRP')
    XRP_price = getPrice('0xe9e7cea3dedca5984780bafc599bd69add087d56', registered_tokens.get('XRP'))
    XRP_balance = float(XRP_price) * float(XRP)
    XRP_balance = "{:.2f}".format(XRP_balance)

    mess_text = '*Wallet address:* ' + str(addresss) + '\n' \
                + "*BNB balance =* " + str(BNB) + ' ~ ' + BNB_balance + '$\n' \
                + "*BUSD balance =* " + str(BUSD) + '\n' \
                + "*USDT balance =* " + str(USDT) + '\n' \
                + "*ETH balance =* " + str(ETH) + ' ~ ' + ETH_balance + '$\n' \
                + "*XRP balance =* " + str(XRP) + ' ~ ' + XRP_balance + '$\n'
    print(mess_text)
    time.sleep(1)
    return mess_text


class Voter:
    voter_username = ""

    votes_timestamps = {}

    def __init__(self, voter_username):
        self.voter_username = voter_username

    def addvoterecord(self, username):
        if individual_vote_flag.state == "True":
            self.votes_timestamps[self.voter_username] = {username: int(time.time())}
        else:
            self.votes_timestamps[username] = int(time.time())

    def hasVoted(self, username):
        try:
            if individual_vote_flag.state == "True":
                if time.time() - self.votes_timestamps.get(self.voter_username).get(username) < 43200:
                    return True
            else:
                if time.time() - self.votes_timestamps.get(username) < 43200:
                    return True
        except:
            return False

    def nextVote(self, username):
        try:
            if individual_vote_flag.state == "True":
                remaining_time = time.time() - self.votes_timestamps.get(self.voter_username).get(username)
            else:
                remaining_time = time.time() - self.votes_timestamps.get(username)
        except:
            return 0

        next_vote_time = int(43200 - remaining_time)
        return next_vote_time


class myBool:
    state = ""

    def __init__(self):
        self.state = "False"

    def invertBool(self):
        if self.state == "False":
            self.state = "True"
            return
        else:
            self.state = "False"

    def returnStatus(self):
        if self.state == "True":
            return "ENABLED"
        if self.state == "False":
            return "DISABLED"


individual_vote_flag = myBool()


BOT_KEY = "1936324922:AAHagrue5eHBV-LHIQ2Q8YgoWYx9tlgDguw"
bot = telebot.TeleBot(BOT_KEY)

GITHUB_ACCESS = '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'
git = Github(GITHUB_ACCESS)
repo = git.get_user().get_repo('DegenBOTbackupfiles')

disallowed_user_list = []
bot_admin_list = ["ReverseWojack"]
main_admin_list = ["sabirdev0", "jonwath", "KongMan", "donmonke0", "CryptoMUTT", "ReverseWojack"]
admins = bot.get_chat_administrators(-1001480482593)

for i in admins:
    bot_admin_list.append(i.user.username)
    
voter_list = {}
for i in bot_admin_list:
    voter_list[i] = Voter(i)

reps = {'ClaraOrtiz310': 3, 'jonwath': 3, 'CryptoMutt': 1, "MEEVM": 1, "GreenTea1337": 1, "KongMan": 1}


registered_address = {'sabirdev0': '0x043013E6a9946Ce388b7d61228a101926d911252'}

registered_tokens = {'BUSD': '0xe9e7cea3dedca5984780bafc599bd69add087d56',
                     'ETH': '0x2170ed0880ac9a755fd29b2688956bd959f933f8',
                     'ADA': '0x3ee2200efb3400fabb9aacf31297cbdd1d435d47',
                     'USDT': '0x55d398326f99059ff775485246999027b3197955',
                     'XRP': '0x1d2f0da169ceb9fc7b3144628db156f3f6c60dbe',
                     'CVG': '0x5a02FE8e84729746519A9C6f153717dA354497c0',
                     'MUTTZ': '0x7C0C510F83D83956051DeB399577d404C190A006',
                     'JIRO': '0x984ae7a0e32ae2813831b3d082650e1eca7a1996',
                     'USDC': '0xBA5Fe23f8a3a24BEd3236F05F2FcF35fd0BF0B5C'
                     }

price_exceptions = ['BUSD', 'ETH', 'XRP', 'USDT', 'ADA', 'USDC']

bsc_test = 'https://data-seed-prebsc-1-s1.binance.org:8545/'
bsc_main = 'https://bsc-dataseed.binance.org/'

web3 = Web3(Web3.HTTPProvider(bsc_main))

if web3.isConnected():
    print('Connected to mainnet...')

announced = [web3.toChecksumAddress('0x984ae7a0e32ae2813831b3d082650e1eca7a1996'), web3.toChecksumAddress('0x7C0C510F83D83956051DeB399577d404C190A006')]

restore = True
if restore:
    try:
        filename = "registered_addresses.json"
        reg_address_file = repo.get_contents(filename)
        registered_address = json.loads(reg_address_file.decoded_content.decode())
    except Exception as e:
        bot.send_message(1761035007, "Registered addresses are not restored : " + str(e))
        print("registeredaddress.pkl Backup file not available")

    try:
        filename = "registered_tokens.json"
        reg_tokens_file = repo.get_contents(filename)
        registered_tokens = json.loads(reg_tokens_file.decoded_content.decode())
    except Exception as e:
        bot.send_message(1761035007, "Registered token are not restored : " + str(e))
        print("registeredtoken.pkl Backup file not available")

    try:
        filename = "reps.json"
        reps_file = repo.get_contents(filename)
        reps = json.loads(reps_file.decoded_content.decode())
    except Exception as e:
        bot.send_message(1761035007, "Reps are not restored : " + str(e))
        print('reps.pkl not found')

    try:
        filename = "announced.json"
        announced_file = repo.get_contents(filename)
        announced = json.loads(announced_file.decoded_content.decode())
    except Exception as e:
        bot.send_message(1761035007, "Announced are not restored : " + str(e))
        print('reps.pkl not found')

    bot.send_message(1761035007, "Bot is restarted and data is restored")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.chat.type == 'private':
        bot.reply_to(message,
                     "Hey! This bot will forward potential investment calls from Degen Defi group to a specified "
                     "channel so that no one will miss any call. Subscribe to this channel: "
                     "https://t.me/DegenDefiAnnouncementChannel")
    else:
        bot.reply_to(message, "Hey " + message.from_user.username + " PM me with /help to see my commands")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    time.sleep(2)
    if message.chat.type == 'private' or True:
        mess_text = ("Support the creator:\n"
                     "/donate - support my father :)\n\n"
                     ""
                     "Greet or get help from the bot\n"
                     "/greet - bot will greet the user\n"
                     "/help - Display help text with commands according to user type\n\n"
                     ""
                     "Manage pre-defined addresses of the tokens:\n"
                     "/regToken - Register a token address\n"
                     "/removeregtoken - Remove a token address from the list\n"
                     "/showtokens - Display list of token addresses in the list\n\n"
                     ""
                     "Registering wallet address:\n"
                     "/regaddress - {wallet} This command will register wallet address of the user\n\n"
                     ""
                     "Retrieving balance info of tokens from wallet address:\n"
                     "/getbalance - {Symbol/Address} return balance of the token if registered\n"
                     "/getbalance - {Symbol/Address} {Wallet Address} return balance of given address\n\n"
                     ""
                     "Retrieving Token information:\n"
                     "{Symbol} - returns token information of registered symbol\n"
                     "{Address} - returns token information of given contract address\n"
                     "{Wallet} - returns portfolio of given wallet address\n\n"
                     ""
                     "Manage bot admins:\n"
                     "/addadmin - This command will add an admin for the bot\n"
                     "/removeadmin - This command will remove an admin from the bot\n"
                     "/showadmin - This command will list admins\n\n"
                     ""
                     "Manage bot ban list from announcement channel: \n"
                     "/banuser - This command will ban a user from announcing anything in the group\n"
                     "/unbanuser - This command will unban a user from announcing anything in the group\n"
                     "/showbanned - This command will list banned users\n\n"
                     ""
                     "Announce in Channels:\n"
                     "/announce - This command will forward a message with command or a message that is"
                     " being replied to an announcement channel \n"
                     "https://t.me/DegenDefiAnnouncementChannel\n\n"
                     ""
                     "Managing voter list:\n"
                     "/addvoter - This command will add a user to the voter list so that he may /rep users\n"
                     "/removevoter - This command will remove a user from the voter list\n\n"
                     ""
                     "Give votes based on good calls:\n"
                     "/rep - This command will vote rep+ user as a reward for the good call\n"
                     "/showleaderboard - display top 5 reps users \n"
                     "/showreps - This command will display reps score of a user, but, Always DYOR!\n"
                     "/wennextvote - This command will display time remaining to /rep a user one more time\n\n"
                     "/vote_type_switch - This command will Enable or Disable vote_mode\n"
                     "/resetleaderboard - This command will reset the leaderboard\n"
                     "Enabled: A voter can vote individually a user once in a day\n"
                     "Disabled: Only one voter from the voter list can vote a user within a day\n"
                     "USE THIS COMMAND CAREFULLY")
        bot.reply_to(message, mess_text)

    else:
        bot.reply_to(message, "Heya :) PM me with /help to see my commands")


@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message,
                 "Hey! @" + message.from_user.username + "Subscribe to this channel: "
                                                         "https://t.me/DegenDefiAnnouncementChannel")


@bot.message_handler(commands=['announce'])
def announce(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.chat.type == 'private':
        bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
        return
    if message.from_user.username in disallowed_user_list:
        bot.reply_to(message, "I am sorry your announcements cannot be forwarded in announcement channel.")
    else:
        org_msg = message
        message = message.reply_to_message
        if message is None:
            message = org_msg
        if message.chat.type == 'private':
            bot.reply_to(message, "This command can only be executed while called in the group")
            return

        bot.forward_message(-1001591163735, message.chat.id, message.id)
        bot.reply_to(org_msg, "Forwarded to announcement channel!")


@bot.message_handler(commands=['banuser'])
def banuser(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.from_user.username in bot_admin_list:
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /banuser @anyuser")
            return

        if user in bot_admin_list:
            bot.reply_to(message, "You cannot ban an admin. :)")
            return

        disallowed_user_list.append(user)
        try:
            backupfile = open("disallowed_user_list.pkl", "wb")
            backupfile.truncate()
            pickle.dump(disallowed_user_list, backupfile)
            backupfile.close()
        except:
            return
        bot.reply_to(message, (
                "@" + user + " has been banned. Now they can not send any announcement to the announcement channel"))

    else:
        bot.reply_to(message, "You are not allowed to ban any user! "
                              "If you are a mod you should contact @sabirdev0 "
                              "so that he can allow you")


@bot.message_handler(commands=['unbanuser'])
def unbanuser(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.from_user.username in bot_admin_list:
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /unbanuser @anyuser")
            return

        if user in bot_admin_list:
            bot.reply_to(message, "You cannot ban an admin. :)")
            return

        disallowed_user_list.remove(user)
        bot.reply_to(message, (
                "@" + user + " has been unbanned. Now they can send any announcement to the announcement channel"))

    else:
        bot.reply_to(message, "You are not allowed to unban any user! "
                              "If you are a mod you should contact @sabirdev0 "
                              "so that he can allow you")


@bot.message_handler(commands=['showbanned'])
def showbanned(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    mess_text = "Banned Users list: "
    for i in disallowed_user_list:
        mess_text += "\n" + "@" + i

    if message.from_user.username in bot_admin_list:
        if mess_text == "Banned Users list: ":
            bot.reply_to(message, "There are no banned users in the list yet")
            return
        bot.reply_to(message, mess_text)
    else:
        bot.reply_to(message, "You are not allowed to execute this command!")


@bot.message_handler(commands=['addadmin'])
def addadmin(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.from_user.username in main_admin_list:
        if message.chat.type == 'private':
            bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
            return
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /addadmin @anyuser")
            return

        if user in bot_admin_list:
            bot.reply_to(message, ("@" + user + " is already in the admin list!"))
            return

        bot_admin_list.append(user)
        bot.reply_to(message, ("@" + user + " has been added to the list."))

    else:
        bot.reply_to(message, "You are not allowed to execute this command!")


@bot.message_handler(commands=['removeadmin'])
def removeadmin(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.from_user.username in main_admin_list:
        if message.chat.type == 'private':
            bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
            return
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /removeadmin @anyuser")
            return

        if user not in bot_admin_list:
            bot.reply_to(message, ("@" + user + " is already not in the admin list!"))
            return
        if user in main_admin_list:
            bot.reply_to(message, "Whoosh... You can't remove any main admin")

        bot_admin_list.remove(user)
        bot.reply_to(message, ("@" + user + " has been removed from the admin list."))

    else:
        bot.reply_to(message, "You are not allowed to execute this command!")


@bot.message_handler(commands=['showadmin'])
def showadmin(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    mess_text = "Admin list: "
    for i in bot_admin_list:
        mess_text += "\n" + "@" + i
    bot.reply_to(message, mess_text)


@bot.message_handler(commands=['addvoter'])
def addvoter(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.chat.type == 'private':
        bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
        return
    if message.from_user.username in main_admin_list:
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /addvoter @anyuser")
            return

        if user in voter_list:
            bot.reply_to(message, ("@" + user + " is already in the voter list!"))
            return

        voter_list[user] = Voter(user)
        bot.reply_to(message, ("@" + user + " has been added to the list. Now they can /rep anybody..."))

    else:
        bot.reply_to(message, "You are not allowed to execute this command!")


@bot.message_handler(commands=['removevoter'])
def removevoter(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.chat.type == 'private':
        bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
        return
    if message.from_user.username in main_admin_list:
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /removevoter @anyuser")
            return

        if user in main_admin_list:
            bot.reply_to(message, "Whoosh... You are not allowed to remove any main admin")
            return

        if user not in voter_list:
            bot.reply_to(message, ("@" + user + " is not in the voter list!"))
            return

        voter_list.pop(user)
        bot.reply_to(message, ("@" + user + " has been removed from the voter list. Now they cannot /rep anybody..."))

    else:
        bot.reply_to(message, "You are not allowed to execute this command!")


@bot.message_handler(commands=['showvoters'])
def showvoters(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    mess_text = "Voters list: "
    for i in voter_list:
        mess_text += "\n" + "@" + i
    bot.reply_to(message, mess_text)


@bot.message_handler(commands=['rep'])
def rep(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.from_user.username in voter_list:
        if message.chat.type == 'private':
            bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
            return
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /addadmin @anyuser")
            return
        if user == message.from_user.username:
            bot.reply_to(message, "I am sorry ser but you can't lift your own balls :)")
            return
        if voter_list.get(message.from_user.username).hasVoted(user):
            bot.reply_to(message, "@" + user + " has been voted earlier. A user can only be /rep once in a day :)")
        else:
            try:
                reps[user] = reps.get(user) + 1
            except:
                reps[user] = 1
            voter_list.get(message.from_user.username).addvoterecord(user)
            bot.reply_to(message, "Done... Now @" + user +
                         " has " + str(reps.get(user)) + " reps" + "\nEnter /showleaderboard to display top 5 reps")
            savedata(message=0)
    else:
        bot.reply_to(message, "Only mods can /rep someone")


@bot.message_handler(commands=['showleaderboard'])
def showleaderboard(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.chat.type == 'private':
        bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
        return
    sort_orders = sorted(reps.items(), key=lambda x: x[1], reverse=True)
    mess_string = "Leadeboards:\n"
    if len(sort_orders) <= 0:
        bot.reply_to(message, "There is no /rep at the moment")
        return
    n = 1
    for i in sort_orders:
        if n > 5:
            break
        _name = i[0]
        _name = "@" + _name
        mess_string += "#" + str(n) + " " + _name + "     " + str(i[1]) + "\n"
        n += 1

    bot.reply_to(message, mess_string)


# noinspection PyBroadException
@bot.message_handler(commands=['wennextvote'])
def wennextvote(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.from_user.username in voter_list:
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /wennextvote @anyuser")
            return
        try:
            remaining_time = voter_list.get(message.from_user.username).nextVote(user)
            if remaining_time <= 0:
                raise
        except:
            bot.reply_to(message, "You can vote @" + user + " now!")
            return

        bot.reply_to(message,
                     "You have to wait almost " + str(int(remaining_time / 3600) + 1) + " hours before voting @" + user)
    else:
        bot.reply_to(message, "You are not allowed to execute this command!")


@bot.message_handler(commands=['vote_type_switch'])
def vote_type_switch(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.chat.type == 'private':
        bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
        return
    if message.from_user.username in main_admin_list:
        individual_vote_flag.invertBool()
        bot.reply_to(message, "Command executed, Current Status: " + individual_vote_flag.returnStatus())


@bot.message_handler(commands=['showreps'])
def showreps(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.chat.type == 'private':
        bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
        return
    try:
        user = message.text.split()[1]
        user = user[1:]
    except:
        bot.reply_to(message, "You have to mention the user after the command like /showreps @anyuser")
        return

    try:
        bot.reply_to(message, "@" + user + " has " + str(reps.get(user)) + " reps! Always DYOR before investing!!!")
    except:
        bot.reply_to(message, "@" + user + " has 0 rep! Always DYOR before investing!!!")


@bot.message_handler(commands=['resetleaderboard'])
def resetleaderboard(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    if message.from_user.username == 'sabirdev0':
        if message.chat.type != 'private':
            for i in reps:
                reps[i] = 0
            bot.reply_to(message, "Leaderboard has been reset!")
        else:
            bot.reply_to(message, "This command cannot be executed in my PM :)")
    else:
        bot.reply_to(message, "You are not allowed to execute this command")


@bot.message_handler(commands=['regaddress'])
def regaddress(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    username = message.from_user.username
    try:
        address = message.text.split()[1]
    except:
        bot.reply_to(message, "You have to enter address like this to register /regaddress 0x00000... ")
        return

    registered_address[username] = address
    bot.reply_to(message, '@' + username + " your public address has been registered...")
    savedata(message=0)


@bot.message_handler(commands=['regToken'])
def regToken(message):
    username = message.from_user.username
    if username in main_admin_list:
        try:
            address = message.text.split()[1]
        except:
            bot.reply_to(message, "You have to enter address like this to register /regToken 0x00000... ")
            return

        try:
            token_symbol = getSymbol(address)
            if token_symbol == 'Token address is not supported...':
                raise
        except:
            bot.reply_to(message, 'Token address is not supported..')
            return

        token_symbol = str(token_symbol)

        registered_tokens[token_symbol] = address
        bot.reply_to(message, token_symbol + ' contract address has been added to the registered token addresses. '
                                             'Now registered users can check their portfolio of ' + token_symbol +
                     ' Just by this command /getbalance {' + token_symbol +
                     '}. Whereas non-registered can check their balance /getbalance {' + token_symbol +
                     '} (walladdress) Users can also check their portfolio using /getbalance (contract_address) ('
                     'wallet_address)')
        savedata(message=0)


@bot.message_handler(commands=['showtokens'])
def showtokens(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    mess_text = 'Registered tokens and addresses:' + '\n'
    for i in registered_tokens.keys():
        mess_text = mess_text + '*' + i + '*' + ' - ' + registered_tokens.get(i) + '\n'

    bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)


@bot.message_handler(commands=['removeregtoken'])
def removeregtoken(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    username = message.from_user.username
    if username in main_admin_list:
        try:
            token = message.text.split()[1]
        except:
            bot.reply_to(message,
                         "You have to enter token symbol like /removeregtoken (TOKEN_SYMBOL) to remove from the list")
            return

        if token not in registered_tokens.keys():
            bot.reply_to(message, "Token is not available in registered tokens")
        else:
            registered_tokens.pop(token)
            bot.reply_to(message, token + " is removed from the available tokens list")
            savedata(message=0)


@bot.message_handler(commands=['donate'])
def donate(message):
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(2)
    bot.reply_to(message, "My father worked really hard while coding me..."
                          " So if you like my work and want to appreciate it and show your support; Donate!\n\n"
                          "BSC: 0x497089B11903B5946f41C700c9479A13DFf5BB23\n\n"
                          "Always nice to see my work is appreciated :)")


@bot.message_handler(commands=['getbalance'])
def getbalance(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=5)
    error_message_command = "*Command pattern is invalid... You haven't registered your wallet address yet\n" \
                            "/getbalance {TokenAddress/Symbol} available only if you register your wallet with " \
                            "/regaddress\n" \
                            "/getbalance {TokenAddress/Symbol} {Wallet Address} if you don't want to" \
                            " register your wallet*"

    wallet_error = "*Wallet address is 'invalid'... Maybe you are confused with command pattern\n" \
                   "" + "/getbalance {Symbol/TokenAddress} {Wallet Address}\n" \
                        "" + "Users with registered wallet address can execute command:\n" \
                             "" + "/getbalance {Symbol/TokenAddress}*"

    contract_error = "*Contract address is 'invalid'... Maybe you are confused with command pattern\n" \
                     "" + "/getbalance {Symbol/TokenAddress} {Wallet Address}\n" \
                          "" + "Users with registered wallet address can execute command:\n" \
                               "" + "/getbalance {Symbol/TokenAddress}*"

    command_pattern_error = "*Command pattern is 'invalid'... Maybe you are confused with command pattern\n" \
                            "" + "/getbalance {Symbol/TokenAddress} {Wallet Address}\n" \
                                 "" + "Users with registered wallet address can execute command:\n" \
                                      "" + "/getbalance {Symbol/TokenAddress}*"

    message_words_length = len(message.text.split())

    if len(message.text.split()) == 1 and message.from_user.username in registered_address:
        try:
            bnb_balance = bnbbalance(registered_address.get(message.from_user.username))
            bnb_balance_usd = getPrice(registered_tokens.get('BUSD'),
                                       '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')
            bnb_balance_usd = float(bnb_balance) * float(bnb_balance_usd)

            mess_text = 'Your BNB balance is : ' + bnb_balance + ' BNB ~(' + str(bnb_balance_usd) + ' $)'
        except:
            mess_text = '*Whoops! I guess you have registered an invalid wallet address ' \
                        '/regaddress (address) again to fix this issue*'
        bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)
        return
    elif len(message.text.split()) == 1:
        bot.reply_to(message, "*Register your address or "
                              "\n/getbalance {Symbol/TokenAddress} {Wallet Address}\n"
                              "to execute command like this*", parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if len(message.text.split()) == 2 and message.text.split()[1] == 'BNB':
        data = message.text.split()[1]
        if data == 'BNB':
            if message.from_user.username in registered_address:
                try:
                    mess_text = 'Your BNB balance is : ' \
                                + bnbbalance(registered_address.get(message.from_user.username))
                    if bnbbalance(registered_address.get(message.from_user.username)) == 'null':
                        raise
                except:
                    mess_text = '*Whoops! I guess you have registered an invalid wallet address ' \
                                '/regaddress (address) again to fix this issue*'
                bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)
                return
            else:
                bot.reply_to(message, error_message_command, parse_mode=telegram.ParseMode.MARKDOWN)
                return

    if message_words_length > 2:
        data = message.text.split()[1]
        if data == 'BNB':
            wallet_address = message.text.split()[2]
            if isWallet(wallet_address):
                try:
                    mess_text = 'Your BNB balance is : ' + bnbbalance(wallet_address)
                    if bnbbalance(wallet_address) == 'null':
                        raise
                    bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)
                    return
                except:
                    bot.reply_to(message, wallet_error, parse_mode=telegram.ParseMode.MARKDOWN)
                    return

        if data in registered_tokens.keys():
            wallet_address = message.text.split()[2]
            if isWallet(wallet_address):
                try:
                    info = getInfo(registered_tokens.get(data), web3.toChecksumAddress(wallet_address))
                    mess_text = info
                    if info == 'Whoops! can\'t fetch data of this token... Kindly check contract address...':
                        raise
                    address = registered_tokens.get(data)
                    poocoin_link = 'https://poocoin.app/tokens/' + web3.toChecksumAddress(address)
                    pancakeswap_link = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency=' \
                                       + web3.toChecksumAddress(address)

                    chart_bt = types.InlineKeyboardButton(text='Chart 📈', url=poocoin_link)
                    pancake_bt = types.InlineKeyboardButton(text='PancakeSwap 🥞', url=pancakeswap_link)

                    click_kb = types.InlineKeyboardMarkup()
                    click_kb.row(chart_bt)
                    click_kb.row(pancake_bt)

                    bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=click_kb)
                    return
                except:
                    bot.reply_to(message, wallet_error, parse_mode=telegram.ParseMode.MARKDOWN)
                    return
            else:
                bot.reply_to(message, wallet_error, parse_mode=telegram.ParseMode.MARKDOWN)
                return

        elif data.startswith('0x') and len(data) == 42:
            address = data
            if isWallet(address):
                bot.reply_to(message, contract_error, parse_mode=telegram.ParseMode.MARKDOWN)
                return

            wallet_address = message.text.split()[2]
            if isWallet(wallet_address):
                try:
                    info = getInfo(web3.toChecksumAddress(address), web3.toChecksumAddress(wallet_address))
                    mess_text = info
                    if info == 'Whoops! can\'t fetch data of this token... Kindly check contract address...':
                        raise
                    poocoin_link = 'https://poocoin.app/tokens/' + web3.toChecksumAddress(address)
                    pancakeswap_link = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency=' \
                                       + web3.toChecksumAddress(address)

                    chart_bt = types.InlineKeyboardButton(text='Chart 📈', url=poocoin_link)
                    pancake_bt = types.InlineKeyboardButton(text='PancakeSwap 🥞', url=pancakeswap_link)

                    click_kb = types.InlineKeyboardMarkup()
                    click_kb.row(chart_bt)
                    click_kb.row(pancake_bt)

                    bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=click_kb)
                    return
                except:
                    bot.reply_to(message, command_pattern_error, parse_mode=telegram.ParseMode.MARKDOWN)
                    return
        else:
            bot.reply_to(message, command_pattern_error, parse_mode=telegram.ParseMode.MARKDOWN)
            return

    elif message.from_user.username in registered_address and message_words_length > 2:
        bot.reply_to(message, "*Command pattern is invalid... You have registered your wallet address already\n"
                     + "/getbalance {TokenAddress/Symbol} or\n"
                     + "/getbalance {TokenAddress/Symbol} {Wallet Address} if you want to"
                     + " check other wallet's balance*",
                     parse_mode=telegram.ParseMode.MARKDOWN)
        return

    elif message.from_user.username not in registered_address:
        bot.reply_to(message, error_message_command, parse_mode=telegram.ParseMode.MARKDOWN)

    if message.from_user.username in registered_address and len(message.text.split()) == 2:
        data = message.text.split()[1]
        if data == 'BNB':
            try:
                info = bnbbalance(registered_address.get(message.from_user.username))
                if bnbbalance(registered_address.get(message.from_user.username)) == 'null':
                    raise
                bot.reply_to(message, 'Your BNB balance is : '
                             + info, parse_mode=telegram.ParseMode.MARKDOWN)
                return
            except:
                mess_text = '*Whoops! I guess you have registered an invalid wallet address ' \
                            '/regaddress (address) again to fix this issue*'
                bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)
                return

        if data in registered_tokens.keys():
            try:
                info = getInfo(registered_tokens.get(data), registered_address.get(message.from_user.username))
                if info == 'Whoops! can\'t fetch data of this token... Kindly check contract address...':
                    raise
                address = registered_tokens.get(data)
                mess_text = info
                poocoin_link = 'https://poocoin.app/tokens/' + web3.toChecksumAddress(address)
                pancakeswap_link = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency=' \
                                   + web3.toChecksumAddress(address)

                chart_bt = types.InlineKeyboardButton(text='Chart 📈', url=poocoin_link)
                pancake_bt = types.InlineKeyboardButton(text='PancakeSwap 🥞', url=pancakeswap_link)

                click_kb = types.InlineKeyboardMarkup()
                click_kb.row(chart_bt)
                click_kb.row(pancake_bt)

                bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=click_kb)
                return
            except:
                mess_text = '*Whoops! I guess you have registered an invalid wallet address ' \
                            '/regaddress (address) again to fix this issue*'
                bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)
                return

        elif data.startswith('0x') and len(data) == 42:
            address = data
            if isWallet(address):
                bot.reply_to(message,
                             "Your address is in registration list..."
                             " You have to write either symbol or CA"
                             " of the token\nPossible command can be:\n"
                             "/getbalance {symbol}\n"
                             "/getbalance {Token Address}\n"
                             "To list available symbols:\n"
                             "/showtokens")
                return
            else:
                try:
                    info = getInfo(address, registered_address.get(message.from_user.username))
                    mess_text = info
                    if info == 'Whoops! can\'t fetch data of this token... Kindly check contract address...':
                        raise
                    poocoin_link = 'https://poocoin.app/tokens/' + web3.toChecksumAddress(address)
                    pancakeswap_link = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency=' \
                                       + web3.toChecksumAddress(address)

                    chart_bt = types.InlineKeyboardButton(text='Chart 📈', url=poocoin_link)
                    pancake_bt = types.InlineKeyboardButton(text='PancakeSwap 🥞', url=pancakeswap_link)

                    click_kb = types.InlineKeyboardMarkup()
                    click_kb.row(chart_bt)
                    click_kb.row(pancake_bt)

                    bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=click_kb)
                    return
                except:
                    mess_text = 'Whoops! I guess you have registered an invalid wallet address ' \
                                '/regaddress (address) again to fix this issue'
                    bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)
                    return
        elif message.text.split()[1] not in registered_address:
            bot.reply_to(message,
                         data + " is not available in the registered address\n/regToken {Contract_Address} to register token")
            return
        elif message.from_user.username not in registered_address:
            bot.reply_to(message, "You Haven't registered your wallet address yet\n"
                                  "/regaddress {Wallet Address} to register your address and then try again with\n"
                                  "/getbalance {TokenAddress/Symbol} or\n"
                                  "/getbalance {TokenAddress/Symbol} {Wallet Address} if you don't want to register")


@bot.message_handler(commands=['savedata'])
def savedata(message):
    try:
        filename = 'registered_tokens.json'
        contents_to_delete = repo.get_contents(filename)
        repo.delete_file(contents_to_delete.path, "Remove to create updated", contents_to_delete.sha)
        registered_tokens_content = json.dumps(registered_tokens)
        repo.create_file(filename, "Registered tokens updated", registered_tokens_content)
    except:
        print('save fale')
    try:
        filename = 'registered_addresses.json'
        contents_to_delete = repo.get_contents(filename)
        repo.delete_file(contents_to_delete.path, "Remove to create updated", contents_to_delete.sha)
        registered_address_content = json.dumps(registered_address)
        repo.create_file(filename, "Registered address updated", registered_address_content)
    except:
        print('save fail')

    try:
        filename = 'reps.json'
        contents_to_delete = repo.get_contents(filename)
        repo.delete_file(contents_to_delete.path, "Remove to create updated", contents_to_delete.sha)
        reps_content = json.dumps(reps)
        repo.create_file(filename, "Reps updated", reps_content)
    except:
        print("save fail")

    try:
        filename = 'announced.json'
        try:
            contents_to_delete = repo.get_contents(filename)
            repo.delete_file(contents_to_delete.path, "Remove to create updated", contents_to_delete.sha)
        except:
            l = 0
        announced_content = json.dumps(announced)
        repo.create_file(filename, "Reps updated", announced_content)
    except:
        print("save fail")

    bot.send_message(1761035007, "BACKUP FILES ARE UPDATED")
    if message != 0:
        bot.reply_to(message, "Done!!")


@bot.message_handler(func=lambda message: True,
                     content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact',
                                    'sticker'])
def default_command(message):
    chat_id = message.chat.id
    message_id = message.id

    message_text = str(message.text)
    message_words = message_text.split()
    addresses = []
    txns = []

    for f in message_words:
        try:
            index = f.index('0x')
            address = f[index: index + 42]
            check = False
            if isTxn(f[index: index + 66]) == True:
                txns.append(f[index: index + 66])
                check = True
            if len(address) < 42:
                raise
            if not Web3.isAddress(address):
                raise
            if check == False:
                addresses.append(address)
        except:
            if f.upper() in registered_tokens.keys() and not f.upper() in price_exceptions:
                address = registered_tokens.get(f.upper())
                addresses.append(address)
            continue

    if len(addresses) > 0:
        for i in addresses:
            if isWallet(i):
                try:
                    bot.send_chat_action(message.chat.id, 'typing', timeout=6)
                    bot.reply_to(message, getPortfolio(i), parse_mode=telegram.ParseMode.MARKDOWN)
                except:
                    continue
            else:
                try:
                    bot.send_chat_action(message.chat.id, 'typing', timeout=6)
                    mess_text = getTokenInfo(i)
                except:
                    continue

                if mess_text.startswith('Contract address: '):
                    bot.reply_to(message, mess_text)
                    return
                poocoin_link = 'https://poocoin.app/tokens/' + web3.toChecksumAddress(i)
                pancakeswap_link = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency=' \
                                   + web3.toChecksumAddress(i)

                chart_bt = types.InlineKeyboardButton(text='Chart 📈', url=poocoin_link)
                pancake_bt = types.InlineKeyboardButton(text='PancakeSwap 🥞', url=pancakeswap_link)

                click_kb = types.InlineKeyboardMarkup()
                click_kb.row(chart_bt)
                click_kb.row(pancake_bt)
                bot.send_message(chat_id=chat_id, reply_to_message_id=message_id, text=mess_text, reply_markup=click_kb,
                                 parse_mode=telegram.ParseMode.MARKDOWN)
                if web3.toChecksumAddress(
                        i) not in announced and message.from_user.username not in disallowed_user_list:
                    mess_text = mess_text + "\n\n___SENT BY @" + message.from_user.username + " in Degen Defi Group___"
                    bot.send_message(-1001591163735, text=mess_text, reply_markup=click_kb,
                                     parse_mode=telegram.ParseMode.MARKDOWN)
                    announced.append(web3.toChecksumAddress(i))
                    print(announced)
                    savedata(message=0)

    if len(txns) > 0:
        bot.send_chat_action(message.chat.id, 'typing', timeout=6)
        for i in txns:
            try:
                mess_text = getTxn(i)
                bscscan_url = "https://bscscan.com/tx/" + i
                bsc_bt = types.InlineKeyboardButton(text='BSCScan 🔍', url=bscscan_url)
                click_kb = types.InlineKeyboardMarkup()
                click_kb.row(bsc_bt)
                bot.send_message(chat_id=chat_id, reply_to_message_id=message_id, text=mess_text, reply_markup=click_kb,
                                 parse_mode=telegram.ParseMode.MARKDOWN)
            except:
                continue


while True:
    try:
        bot.infinity_polling(long_polling_timeout=120)
    except:
        time.sleep(15)
        bot.send_message(1761035007, "Bot is down")
