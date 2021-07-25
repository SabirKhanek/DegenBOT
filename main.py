import telebot
import time


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

reps = {}

BOT_KEY = "1936324922:AAEH0txLddXCBrsxMfOpxR0X_5hLf1VVekE"

bot = telebot.TeleBot(BOT_KEY)


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
    username = message.from_user.username
    if message.chat.type == 'private' and username in main_admin_list:
        bot.reply_to(message,
                     "/addadmin - This command will add an admin for the bot\n"
                     "/removeadmin - This command will remove an admin from the bot\n"
                     "/banuser - This command will ban a user from announcing anything in the group\n"
                     "/unbanuser - This command will unban a user from announcing anything in the group\n"
                     "/showbanned - This command will list banned users\n"
                     "/showadmin - This command will list admins\n"
                     "/announce - This command will forward a message with command or a message that is"
                     " being replied to an announcement channel \n"
                     "https://t.me/DegenDefiAnnouncementChannel\n"
                     "/showleaderboard - display top 5 reps users \n/showreps - This command will display reps of the "
                     "specified user\n "
                     "/greet - bot will greet the user\n"
                     "/help - Display help text with commands according to user type\n"
                     "/rep - This command will vote rep+ user as a reward for the good call\n"
                     "/addvoter - This command will add a user to the voter list so that he may /rep users\n"
                     "/removevoter - This command will remove a user from the voter list\n"
                     "/showreps - This command will display reps score of a user, but, Always DYOR!\n"
                     "/wennextvote - This command will display time remaining to /rep a user one more time\n"
                     "/vote_type_switch - This command will Enable or Disable vote_mode\n"
                     "/resetleaderboard - This command will reset the leaderboard\n"
                     "Enabled: A voter can vote individually a user once in a day\n"
                     "Disabled: Only one voter from the voter list can vote a user within a day\n"
                     "USE THIS COMMAND CAREFULLY")

    elif message.chat.type == 'private' and username not in main_admin_list and username not in bot_admin_list:
        bot.reply_to(message,
                     "/announce - This command will forward a message with command or a message that is"
                     " being replied to an announcement channel \n"
                     "https://t.me/DegenDefiAnnouncementChannel\n"
                     "/greet - bot will greet the user\n"
                     "/help - Display help text with commands according to user type\n"
                     "/showreps - This command will display reps score of a user, but, Always DYOR!\n"
                     "/rep - This command will vote a user only if you are a voter\n"
                     "/showadmin - This command will list bot admins\n")
    elif message.chat.type == 'private' and username in bot_admin_list and username not in main_admin_list:
        bot.reply_to(message,
                     "/announce - This command will forward a message with command or a message that is"
                     " being replied to an announcement channel \n"
                     "https://t.me/DegenDefiAnnouncementChannel\n"
                     "/greet - bot will greet the user\n"
                     "/help - Display help text with commands according to user type\n"
                     "/showreps - This command will display reps score of a user, but, Always DYOR!\n"
                     "/rep - This command will vote a user only if you are a voter\n"
                     "/banuser - This command will ban a user from announcing anything in the group\n"
                     "/unbanuser - This command will unban a user from announcing anything in the group\n"
                     "/showbanned - This command will list banned users\n"
                     )

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
        bot.reply_to(message, "@" + user + " has " + str(reps.get(user) + " reps! Always DYOR before investing!!!"))
    except:
        bot.reply_to(message, "@" + user + " has 0 rep! Always DYOR before investing!!!")


@bot.message_handler(commands='resetleaderboard')
def resetleaderboard(message):
    if message.from_user.username in main_admin_list:
        if message.chat.type != 'private':
            for i in reps:
                reps[i] = 0
            bot.reply_to(message, "Leaderboard has been reset!")
        else:
            bot.reply_to(message, "This command cannot be executed in my PM :)")
    else:
        bot.reply_to(message, "You are not allowed to execute this command")


bot.polling()
