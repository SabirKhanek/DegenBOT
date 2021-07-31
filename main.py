import telebot
import telegram
from telebot import types
import time
from web3 import Web3
import json
import pickle
import requests
from num2words import num2words


class obj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)


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
    token_balance_1 = ('%.5f' % web3.fromWei(contract.functions.balanceOf(query_address_1).call(), 'gwei'))
    token_balance_2 = ('%.5f' % web3.fromWei(contract.functions.balanceOf(query_address_2).call(), 'gwei'))
    token_balance_3 = ('%.5f' % web3.fromWei(contract.functions.balanceOf(query_address_3).call(), 'gwei'))

    total_tokens_burnt = float(token_balance_1) + float(token_balance_2) + float(token_balance_3)

    burnt_percentage = total_tokens_burnt / float(supply) * 100
    burnt_percentage = ('%.2f' % burnt_percentage)

    return burnt_percentage


def getTokenInfo(token_address):
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
                           '0x984aE7a0E32Ae2813831b3d082650E1ECA7A1996' + \
                           "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"
            r = requests.get(url=API_ENDPOINT)
            response = r.json()
            abi = json.loads(response["result"])

        contract = web3.eth.contract(address=contract_address, abi=abi)

        API_ENDPOINT = 'https://api.pancakeswap.info/api/v2/tokens/' + contract_address

        r = requests.get(url=API_ENDPOINT)
        response = r.json()
        TokenData = json.loads(json.dumps(response), object_hook=obj)
        TokenData = TokenData.data

        name = TokenData.name
        symbol = TokenData.symbol
        price = TokenData.price
        supply = web3.fromWei(contract.functions.totalSupply().call(), 'gwei')
        renounced_stat = isRenounced(token_address, abi=abi)
        burn = burntPercentage(token_address, abi=abi, supply=supply)
        mcap = float(price) * int(supply)
        mcap_exc_burnt = str(int(int(mcap) - (float(price) * (float(burn) / 100) * int(supply))))
        try:
            mcap_in_words_index = num2words(str(mcap_exc_burnt)).index(',')
            mcap_in_words = 'Around ' + num2words(str(mcap_exc_burnt))[0:mcap_in_words_index]
        except:
            mcap_in_words = num2words(str(supply))
        try:
            supply_in_words_index = num2words(str(supply)).index(',')
            supply_in_words = 'Around ' + num2words(str(supply))[0:supply_in_words_index]
        except:
            supply_in_words = num2words(str(supply))

        return_text = ("*CA:* " + str(contract_address) + '\n\n'
                                                          "*Token name:* " + name + '\n' +
                       "*Token supply:* " + str(supply) + " (≈ " + supply_in_words + ')\n' +
                       "*Symbol:* " + symbol + '\n' +
                       "*price:* " + '%.16f' % float(price) + " $" + "\n"
                                                                     "*Market Cap:* " + str(mcap) + " $ " + '\n' +
                       "*Market Cap (excl. Burnt):* " + ' $ ' + " (≈ " + mcap_in_words + ") " + "\n" +
                       "*Ownership:* " + renounced_stat + '\n' +
                       "*Burnt tokens:* " + str(burn) + '%' + '\n' +
                       "*Verification status:* CONTRACT " + isVerified + '\n'
                       )
        return return_text
    except:
        return "Contract address: " + str(token_address) + " is not supported"


def getInfo(token_address, wallet_address):
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

        gwei_eth = 'gwei'

        if contract.functions.symbol().call() in pegged:
            gwei_eth = 'ether'

        token_balance = ('%.5f' % web3.fromWei(contract.functions.balanceOf(query_address).call(), gwei_eth))
        API_ENDPOINT = 'https://api.pancakeswap.info/api/v2/tokens/' + token_address

        r = requests.get(url=API_ENDPOINT)
        response = r.json()
        TokenData = json.loads(json.dumps(response), object_hook=obj)
        TokenData = TokenData.data

        name = TokenData.name
        symbol = TokenData.symbol
        price = TokenData.price
        balance = float(token_balance) * float(price)
        supply = web3.fromWei(contract.functions.totalSupply().call(), 'gwei')
        burn = burntPercentage(token_address, abi=abi, supply=supply)
        mcap = float(price) * int(supply)
        mcap_exc_burnt = str(int(int(mcap) - (float(price) * (float(burn) / 100) * int(supply))))
        try:
            mcap_in_words_index = num2words(str(mcap_exc_burnt)).index(',')
            mcap_in_words = 'Around ' + num2words(str(mcap_exc_burnt))[0:mcap_in_words_index]
        except:
            mcap_in_words = num2words(str(supply))
        holder_address = web3.toChecksumAddress(wallet_address)
        try:
            supply_in_words_index = num2words(str(supply)).index(',')
            supply_in_words = 'Around ' + num2words(str(supply))[0:supply_in_words_index]
        except:
            supply_in_words = num2words(str(supply))

        return_text = "*Token Address: *" + contract_address + "\n" \
                                                               "*Holder Address:* " + holder_address + "\n\n" \
                                                                                                       "*Token name:* " + name + "\n" + "*Token supply:* " + str(
            supply) + " (≈ " + supply_in_words + ")\n" \
                      + "*Symbol:* " + symbol + "\n" + "*price:* " + '%.16f' % float(price) + " $" + "\n" \
                      + "*Market Cap:* " + str(mcap) + " $ " + "\n" + \
                      "*Market Cap (excl. Burnt):* " + mcap_exc_burnt + ' $ ' + " (≈ " + mcap_in_words + ") " + "\n" + \
                      "*Token Balance:* " + token_balance + "\n" + \
                      "*Balance $:* " + str(balance) + "$" + "\n" \
                      + "*Burnt tokens:* " + str(burn) + '%' + "\n" + \
                      "*Verification status: CONTRACT " + str(isVerified)+ "*" + '\n'

        return return_text
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
        return humanreadable_balance
    except:
        return 'null'


def tokenbalance(wallet_address, req_symbol):
    try:
        url_bsc = 'https://api.bscscan.com/api'
        contract_address = web3.toChecksumAddress(registered_tokens.get(req_symbol))
        API_ENDPOINT = url_bsc + "?module=contract&action=getabi&address=" + str(contract_address) + \
                       "&apikey=XE4D19S8B6F2GP5QZXHQK34J3Q3QP77DT9"

        r = requests.get(url=API_ENDPOINT)
        response = r.json()
        abi = json.loads(response["result"])

        query_address = web3.toChecksumAddress(wallet_address)

        contract = web3.eth.contract(address=contract_address, abi=abi)

        gwei_eth = 'gwei'

        if contract.functions.symbol().call() in pegged:
            gwei_eth = 'ether'

        token_balance = ('%.5f' % web3.fromWei(contract.functions.balanceOf(query_address).call(), gwei_eth))
        return token_balance
    except:
        return 'null'


def getPortfolio(addresss):
    BNB = bnbbalance(addresss)
    BUSD = tokenbalance(addresss, 'BUSD')
    USDT = tokenbalance(addresss, 'USDT')
    ETH = tokenbalance(addresss, 'ETH')
    XRP = tokenbalance(addresss, 'XRP')
    mess_text = '*Wallet address:* ' + str(addresss) + '\n' \
                + "*BNB balance =* " + str(BNB) + '\n' \
                + "*BUSD balance =* " + str(BUSD) + '\n' \
                + "*USDT balance =* " + str(USDT) + '\n' \
                + "*ETH balance =* " + str(ETH) + '\n' \
                + "*XRP balance =* " + str(XRP) + '\n'
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

disallowed_user_list = []
bot_admin_list = ["sabirdev0", "jonwath", "KongMan", "CryptoMUTT", "ReverseWojack", "donmonke0"]
main_admin_list = ["sabirdev0", "jonwath", "KongMan", "donmonke0", "CryptoMUTT", "ReverseWojack"]
voter_list = {}
for i in main_admin_list:
    voter_list[i] = Voter(i)

reps = {'ClaraOrtiz310': 3, 'jonwath': 1, 'CryptoMutt': 1}

BOT_KEY = "1936324922:AAEH0txLddXCBrsxMfOpxR0X_5hLf1VVekE"
bot = telebot.TeleBot(BOT_KEY)

pegged = ['ETH', 'ADA', 'USDT', 'XRP', 'USDC', 'BUSD']

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

bsc_test = 'https://data-seed-prebsc-1-s1.binance.org:8545/'
bsc_main = 'https://bsc-dataseed.binance.org/'

web3 = Web3(Web3.HTTPProvider(bsc_main))

if web3.isConnected():
    print('Connected to mainnet...')

restore = True
if restore:
    try:
        backupfile = open("registeredaddress.pkl", "rb")
        registered_address = pickle.load(backupfile)
        backupfile.close()
    except:
        print("registeredaddress.pkl Backup file not available")

    try:
        backupfile = open("registeredtokens.pkl", "rb")
        registered_tokens = pickle.load(backupfile)
        backupfile.close()
    except:
        print("registeredtoken.pkl Backup file not available")

    try:
        backupfile = open("pegged_record.pkl", "rb")
        pegged = pickle.load(backupfile)
        backupfile.close()
    except:
        print('pegged_record.pkl not found')

    try:
        backupfile = open("reps.pkl", "rb")
        reps = pickle.load(backupfile)
        backupfile.close()
    except:
        print('reps.pkl not found')


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        bot.reply_to(message,
                     "Hey! This bot will forward potential investment calls from Degen Defi group to a specified "
                     "channel so that no one will miss any call. Subscribe to this channel: "
                     "https://t.me/DegenDefiAnnouncementChannel")
    else:
        bot.reply_to(message, "Heya :) PM me with /help to see my commands")


@bot.message_handler(commands=['help'])
def help(message):
    if message.chat.type == 'private' or True:
        print('here')
        mess_text = ("Support the creator:\n"
                     "/donate - support my father :)\n\n"
                     ""
                     "Greet or get help from the bot\n"
                     "/greet - bot will greet the user\n"
                     "/help - Display help text with commands according to user type\n\n"
                     ""
                     "Manage pre-defined addresses of the tokens:\n"
                     "/regToken - Register a token address\n"
                     "/removeaddress - Remove a token address from the list\n"
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
                     "*{Symbol}* - returns token information of registered symbol\n"
                     "*{Address}* - returns token information of given contract address\n"
                     "*{Wallet}* - returns portfolio of given wallet address\n\n"
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
        bot.reply_to(message,mess_text)

    else:
        bot.reply_to(message, "Heya :) PM me with /help to see my commands")


@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message, "Hey! Subscribe to this channel: https://t.me/DegenDefiAnnouncementChannel")


@bot.message_handler(commands=['announce'])
def announce(message):
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
    mess_text = "Admin list: "
    for i in bot_admin_list:
        mess_text += "\n" + "@" + i
    bot.reply_to(message, mess_text)


@bot.message_handler(commands=['addvoter'])
def addvoter(message):
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
    mess_text = "Voters list: "
    for i in voter_list:
        mess_text += "\n" + "@" + i
    bot.reply_to(message, mess_text)


@bot.message_handler(commands=['rep'])
def rep(message):
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
    if message.chat.type == 'private':
        bot.reply_to(message, "This command can only be executed in Degen Defi group :)")
        return
    if message.from_user.username in main_admin_list:
        individual_vote_flag.invertBool()
        bot.reply_to(message, "Command executed, Current Status: " + individual_vote_flag.returnStatus())


@bot.message_handler(commands=['showreps'])
def showreps(message):
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
    mess_text = 'Registered tokens and addresses:' + '\n'
    for i in registered_tokens.keys():
        mess_text = mess_text + '*' + i + '*' + ' - ' + registered_tokens.get(i) + '\n'

    bot.reply_to(message, mess_text, parse_mode=telegram.ParseMode.MARKDOWN)


@bot.message_handler(commands=['removeregtoken'])
def removeregtoken(message):
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
    bot.reply_to(message, "It took a lot of work for my father to get me to where I am now -"
                          " so if you have some money to spare, and want to show your support; Donate!\n"
                          "BSC: 0x497089B11903B5946f41C700c9479A13DFf5BB23\n"
                          "Always nice to see my work is appreciated :)"
                          "Thank you for your generosity!")


@bot.message_handler(commands=['addpeg'])
def addpeg(message):
    if message.from_user.username == 'sabirdev0':
        try:
            peg = message.text.split()[1]
        except:
            bot.reply_to(message, "You have to mention the symbol after the command like /addpeg {symbol}")
            return

        if peg in pegged:
            bot.reply_to(message, (peg + " is already in the pegged list!"))
            return

        pegged.append(peg)
        savedata(message=0)


@bot.message_handler(commands=['getbalance'])
def getbalance(message):
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
            mess_text = 'Your BNB balance is : ' + bnbbalance(registered_address.get(message.from_user.username))
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
        backupfile = open("pegged_record.pkl", "wb")
        backupfile.truncate()
        pickle.dump(pegged, backupfile)
        backupfile.close()
    except:
        print('peg save fale')

    try:
        backupfile = open("registeredtokens.pkl", "wb")
        backupfile.truncate()
        pickle.dump(registered_tokens, backupfile)
        backupfile.close()
    except:
        print('save fale')

    try:
        backupfile = open("registeredaddress.pkl", "wb")
        backupfile.truncate()
        pickle.dump(registered_address, backupfile)
        backupfile.close()
    except:
        print('save fail')

    try:
        backupfile = open("reps.pkl", "wb")
        backupfile.truncate()
        pickle.dump(reps, backupfile)
        backupfile.close()
    except:
        print("save fail")

    if message != 0:
        bot.reply_to(message, "Done!!")


@bot.message_handler(func=lambda message: True,
                     content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact',
                                    'sticker'])
def default_command(message):
    print('here')
    chat_id = message.chat.id
    message_id = message.id

    message_text = str(message.text)
    message_words = message_text.split()
    addresses = []

    for f in message_words:
        try:
            index = f.index('0x')
            address = f[index: index + 42]
            if len(address) < 42:
                raise
            if not Web3.isAddress(address):
                bot.reply_to(message, text='Address: ' + str(address) + ' is not a wallet address')
                raise
            addresses.append(address)
        except:
            if f in registered_tokens.keys():
                address = registered_tokens.get(f)
                addresses.append(address)
            continue

    if len(addresses) > 0:
        for i in addresses:
            if isWallet(i):
                try:
                    bot.reply_to(message, getPortfolio(i), parse_mode=telegram.ParseMode.MARKDOWN)
                except:
                    bot.reply_to(message, text='Address: ' + str(i) + ' is not a wallet address')
                    continue
            else:
                try:
                    mess_text = getTokenInfo(i)
                except:
                    bot.reply_to(message, text='Address: ' + str(i) + ' is not a wallet address')
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


while True:
    try:
        bot.infinity_polling(long_polling_timeout=120)
    except:
        time.sleep(15)
        bot.send_message(1761035007, "Bot is down")
