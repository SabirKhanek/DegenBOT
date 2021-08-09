from web3 import Web3
import json
import requests
from num2words import num2words

eth_main = 'https://mainnet.infura.io/v3/a47f1736f9dc45208e657cfb08cd9f77'

web3_eth = Web3(Web3.HTTPProvider(eth_main))

def getName(address):
    contract = getContract(address)
    symbol = contract.functions.symbol().call()
    return symbol

def decToAmount(address, amount):
    try:
        totokencontract = getContract(address)
        if totokencontract == 0:
            raise
    except:
        raise

    decimals = totokencontract.functions.decimals().call()

    return amount / pow(10, decimals)


def getContract(address):
    try:
        address = web3_eth.toChecksumAddress(address)

        url_bsc = 'https://api.etherscan.io/api'
        contract_address = web3_eth.toChecksumAddress(address)
        API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + str(contract_address) + \
                       "&apikey=KB95WWKT8D3QUTPADSG8KQZ22Z95ENHMCF"

        r = requests.get(url=API_ENDPOINT)
        response = r.json()
        abi = json.loads(response["result"])

        contract = web3_eth.eth.contract(address=contract_address, abi=abi)
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

    tokentosell = amount * (pow(10, int(decimals)))
    print(tokentosell)
    tokentosell = str(tokentosell)

    url_api = 'https://api.0x.org/swap/v1/quote?buyToken='
    totoken = web3_eth.toChecksumAddress(totoken)
    fromtoken = web3_eth.toChecksumAddress(fromtoken)

    API_ENDPOINT = url_api + totoken + '&sellToken=' + fromtoken + '&sellAmount=' + tokentosell + \
                   '&excludedSources=Eth2Dai,Kyber,Curve,Balancer,SnowSnap,SushiSwap,Shell,MultiHop,' \
                   'DODO,Linkswap,Lido,MakerPsm,KyberDMM,Smoothy,Component,Saddle,xSigma,Uniswap_V3,Curve_V2'

    print(API_ENDPOINT)

    r = requests.get(url=API_ENDPOINT)
    response = r.json()

    price = response.get("price")
    return price


def isRenounced(token_address):
    burn_address = ['0x000000000000000000000000000000000000dEaD',
                    '0x0000000000000000000000000000000000000000',
                    '0x0000000000000000000000000000000000000001']
    contract_address = web3_eth.toChecksumAddress(token_address)
    contract = getContract(contract_address)
    if str(contract.functions.owner().call()) in burn_address:
        return 'Renounced'
    else:
        return 'Not renounced'


def burntPercentage(token_address, supply):
    contract_address = web3_eth.toChecksumAddress(token_address)

    query_address_1 = web3_eth.toChecksumAddress('0x000000000000000000000000000000000000dEaD')
    query_address_2 = web3_eth.toChecksumAddress('0x0000000000000000000000000000000000000000')
    query_address_3 = web3_eth.toChecksumAddress('0x0000000000000000000000000000000000000001')

    contract = getContract(contract_address)
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


def getLiquidity(contract_address):
    uniswap_factory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
    WETHER = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    USDT = '0xdac17f958d2ee523a2206206994597c13d831ec7'
    contract_address = web3_eth.toChecksumAddress(contract_address)

    pcs_contract = getContract(uniswap_factory)

    pair_address = pcs_contract.functions.getPair(contract_address, WETHER).call()

    token_contract = getContract(contract_address)

    lp_holding_balance = token_contract.functions.balanceOf(pair_address).call()

    print(lp_holding_balance)

    lp_holding_balance = decToAmount(contract_address, lp_holding_balance)

    return lp_holding_balance


def getTokenInfo(token_address):
    try:
        contract_address = web3_eth.toChecksumAddress(token_address)
        contract = getContract(token_address)
        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        WETHER = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        USDT = '0xdac17f958d2ee523a2206206994597c13d831ec7'

        price = getPrice(WETHER, contract_address)
        ETH_price = getPrice(contract_address, WETHER)
        ETH_rate = getPrice(USDT, WETHER)
        print("ETH Rate: " + ETH_rate)
        print("price: " + price)
        price = float(ETH_rate) * float(price)

        LP_Holdings_USD = float(getLiquidity(contract_address)) * price

        print(LP_Holdings_USD)
        LP_Holdings_ETH = float(LP_Holdings_USD) / float(ETH_rate)

        print(ETH_price)
        print(LP_Holdings_ETH)

        supply_wei = contract.functions.totalSupply().call()

        decimals = pow(10, contract.functions.decimals().call())

        supply = supply_wei / decimals

        try:
            renounced_stat = isRenounced(token_address)
        except:
            renounced_stat = 'NULL'
        burn = burntPercentage(token_address, supply=supply)

        mcap = float(price) * int(supply)

        mcap_lp_ratio = int(mcap / LP_Holdings_USD)

        mcap_lp_ratio = '1:' + str(mcap_lp_ratio)
        LP_Holdings_USD = format(int(LP_Holdings_USD), ',') + ' $'
        LP_Holdings_ETH = ('%.2f' % LP_Holdings_ETH) + ' ETH'

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

        return_text = ("___UNISWAP V2 Ethereum Chain___\n\n"
                       "*CA:* " + str(contract_address) + '\n\n'
                                                          "*Token name:* " + name + '\n' +
                       "*Token supply:* " + format(int(supply), ',') + " (≈ " + str(supply_in_words) + ')\n' +
                       "*Symbol:* " + symbol + '\n\n' +
                       "*price:* " + '%.16f' % float(price) + " $" + "\n"
                                                                     "*1 ETH:* " + '%.2f' % float(ETH_rate) + " $\n" +
                       "*1 ETH:* " + '%.2f' % float(ETH_price) + " " + symbol + "\n\n"
                                                                                "*Market Cap: * " + format(
                    int(mcap_exc_burnt), ',') + ' $ ' +
                       " (≈ " + mcap_in_words + ") " + "\n\n" +
                       "*LP Holdings: *" + LP_Holdings_ETH + " ( " + LP_Holdings_USD + ")\n" +
                       "*Liquidity to MCAP ratio: *" + mcap_lp_ratio + "\n\n" +
                       "*Ownership:* " + str(renounced_stat) + '\n' +
                       "*Burnt tokens:* " + str(burn) + '%' + '\n'
                       )

        print(return_text)
        return return_text

    except Exception as e:
        print(e)
        try:
            contract_address = web3_eth.toChecksumAddress(token_address)
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


