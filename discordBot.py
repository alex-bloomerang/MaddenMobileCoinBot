import logging
import os
import sys

import discord
import requests
from tinydb import TinyDB
from dotenv import load_dotenv

from databaseController import get_player, update_price, get_highest_sellers
from ocr import extract_pricing_data

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', stream=sys.stdout,
                        level=logging.INFO)

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    client = discord.Client()
    db = TinyDB(sys.argv[1])


    @client.event
    async def on_ready():
        logging.info(f'{client.user} has connected to Discord!')


    @client.event
        if message.author == client.user:
            return

        if message.content.startswith('!ping'):
            await message.channel.send('!pong')

        if message.content.startswith('!image'):
            if message.attachments:
                response = requests.get(message.attachments[0].url)
                await message.channel.send(extract_pricing_data(response, db, 0.9))
            else:
                await message.channel.send("Please attach a screenshot of the inbox e.g.:")
                with open("example.PNG", "rb") as f:
                    await message.channel.send(file=discord.File(f))

        if message.content.startswith('!fpimage'):
            if message.attachments:
                response = requests.get(message.attachments[0].url)
                await message.channel.send(extract_pricing_data(response, db, 1))
            else:
                await message.channel.send("Please attach a screenshot of the inbox e.g.:")
                with open("example.PNG", "rb") as f:
                    await message.channel.send(file=discord.File(f))

        if message.content.startswith("!price"):
            player_request = message.content[(len("!price")):].strip().split(",")
            player_request = list(map(str.strip, player_request)) # trim the tokens to remove extra spaces
            if len(player_request) == 3:
                await message.channel.send(
                    get_player(int(player_request[0]), player_request[1] + " " + player_request[2], db, False))
            else:
                await message.channel.send("To get a players price use the following command \"!price Rating,"
                                           "FirstInitial,Surname\"")

        if message.content.startswith("!input"):
            player_request = message.content[(len("!input")):].strip().split(",")
            player_request = list(map(str.strip, player_request)) # trim the tokens to remove extra spaces
            if len(player_request) == 4:
                await message.channel.send(
                    update_price(int(player_request[0]), player_request[1] + " " + player_request[2],
                                 int(player_request[3]), db))
            else:
                await message.channel.send("To get players ranked by rating use the following command: \"!input "
                                           "Rating,FirstInitial,Surname,Price\"")
        if message.content.startswith("!rank"):
            player_request = message.content[(len("!rank")):].strip().split(",")
            if player_request == 1:
                await message.channel.send(
                    get_highest_sellers(int(player_request[0]), db))
            else:
                await message.channel.send("To add a player to the database use the following command:\"!rank Rating\"")

        if message.content.startswith("!allprices"):
            player_request = message.content[(len("!allprices")):].strip().split(",")
            player_request = list(map(str.strip, player_request)) # trim the tokens to remove extra spaces
            if len(player_request) == 3:
                await message.channel.send(
                    get_player(int(player_request[0]), player_request[1] + " " + player_request[2], db, True))
            else:
                await message.channel.send("To get a players price use the following command \"!allprices Rating,"
                                           "FirstInitial,Surname\"")

        if message.content.startswith("!help"):
            help_message = "Welcome to CoinBot2.0\n\nBelow is a full list of the commands:\n\n" \
                           "\"!price Rating,FirstInitial,Surname\" " \
                           "returns the most recent price a player has been sold for, " \
                           "when it was sold for that price and " \
                           "the average of the most recent prices\n\n" \
                           "\"!input Rating,FirstInitial,Surname,Price\" adds a player to the database\n\n" \
                           "\"!rank Rating\" returns the (5 or less) most expensive players at that rating\n\n" \
                           "\"!image\" attach a screenshot of the inbox to automatically add players to the database, " \
                           "send \"!image\" " \
                           "with no attachment for an example\n\n\"!fpimage\" the same as !image but if you have the " \
                           "feild pass use this command\n""\nFeel free to browse the repo at " \
                           "https://github.com/JDMDevelopment/MaddenMobileCoinBot and any questions send to " \
                           "jdmdevelopment55@gmail.com or <@293362579709886465>\n\n\nIf you find the bot useful feel " \
                           "free to donate, donations mean I can dedicate more time for maintenance, upkeep and " \
                           "improvements\n" \
                           "https://paypal.me/JDMDev?locale.x=en_GB\n\n\nJDMDev "

            await message.channel.send(help_message)


    client.run(TOKEN)
