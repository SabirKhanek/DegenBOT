import telebot

disallowed_user_list = []
bot_admin_list = ["sabirdev0", "jonwath", "KongMan", "CryptoMUTT", "ReverseWojack"]

BOT_KEY = "1936324922:AAF9BMYbJPx9B3Mf-uZJMS2cq8TGrk_mUNk"

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
    if message.chat.type == 'private':
        bot.reply_to(message,
                     "/addadmin - This command will add an admin for the bot\n/removeadmin - This command will remove "
                     "an admin from the bot\n/banuser - This command will ban a user from announcing anything in the "
                     "group\n/unbanuser - This command will unban a user from announcing anything in the "
                     "group\n/showbanned - This command will list banned users\n/showadmin - This command will list "
                     "admins\n/announce - This command will forward a message with command or a message that is being "
                     "replied to to an announcement channel \nhttps://t.me/DegenDefiAnnouncementChannel")
    else:
        bot.reply_to(message, "Heya :) PM me with /help to see my commands")


@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message, "Hey! Subscribe to this channel: https://t.me/DegenDefiAnnouncementChannel")


@bot.message_handler(commands=['announce'])
def announce(message):
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
    if message.from_user.username == "sabirdev0":
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
    if message.from_user.username == "sabirdev0":
        try:
            user = message.text.split()[1]
            user = user[1:]
        except:
            bot.reply_to(message, "You have to mention the user after the command like /removeadmin @anyuser")
            return

        if (user not in bot_admin_list):
            bot.reply_to(message, ("@" + user + " is already not in the admin list!"))
            return

        bot_admin_list.remove(user)
        bot.reply_to(message, ("@" + user + " has been removed from the admin list."))

    else:
        bot.reply_to(message, "You are not allowed to execute this command!")


@bot.message_handler(commands=['showadmin'])
def showadmin(message):
    mess_text = "Admin list: "
    for i in bot_admin_list:
        mess_text += "\n" + "@" + i

    if mess_text == "Banned Users list: ":
        bot.reply_to(message, "There are no banned users in the list yet")
        return
    bot.reply_to(message, mess_text)


bot.polling(none_stop=True)
