# DegenBOT
This telegram bot:
1. was made for bep20 or eth20 memecoins trading community. 
2. can fetch information and balances different token of ethereum and binance chain wallets.
3. can automatically transfer potential trading calls from community in an announcement channel.
4. has a rep and a leaderboard system to reward users on good trading call.
5. has a wallet registration option through which users can register their wallet addresses with the bot.
6. can fetch token balance for a user either registered or non-registered (Wallet address is required)
7. can test liquidity lock and burnt percentage of tokens.
8. has other mischellaneous features.
NOTE: This bot was just madwe to contribute in community now it is not being used that's why I am turning this repository public

Commands to use bot:
/donate - donation message

Greet or get help from the bot
/greet - bot will greet the user
/help - Display help text with commands according to user type

Manage pre-defined addresses of the tokens:
/regToken - Register a token address
/removeregtoken - Remove a token address from the list
/showtokens - Display list of token addresses in the list

Registering wallet address:
/regaddress - {wallet} This command will register wallet address of the user

Retrieving balance info of tokens from wallet address:
/getbalance - {Symbol/Address} return balance of the token if registered
/getbalance - {Symbol/Address} {Wallet Address} return balance of given address

Retrieving Token information:
{Symbol} - returns token information of registered symbol
{Address} - returns token information of given contract address
{Wallet} - returns portfolio of given wallet address

Manage bot admins:
/addadmin - This command will add an admin for the bot
/removeadmin - This command will remove an admin from the bot
/showadmin - This command will list admins

Manage bot ban list from announcement channel: 
/banuser - This command will ban a user from announcing anything in the group
/unbanuser - This command will unban a user from announcing anything in the group
/showbanned - This command will list banned users

Announce in Channels:
/announce - This command will forward a message with command or a message that is being replied to an announcement channel 
https://t.me/DegenDefiAnnouncementChannel

Managing voter list:
/addvoter - This command will add a user to the voter list so that he may /rep users
/removevoter - This command will remove a user from the voter list

Give votes based on good calls:
/rep - This command will vote rep+ user as a reward for the good call
/showleaderboard - display top 5 reps users 
/showreps - This command will display reps score of a user, but, Always DYOR!
/wennextvote - This command will display time remaining to /rep a user one more time

/vote_type_switch - This command will Enable or Disable vote_mode
/resetleaderboard - This command will reset the leaderboard
Enabled: A voter can vote individually a user once in a day
Disabled: Only one voter from the voter list can vote a user within a day
USE THIS COMMAND CAREFULLY
