import logging
import sys

import discord
import requests
from tinydb import TinyDB
from databaseController import get_player, update_price
from ocr import parse_ocr, process_image

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    client = discord.Client()
    db = TinyDB(sys.argv[1])


    @client.event
    async def on_ready():
        logging.info(f'{client.user} has connected to Discord!')


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

        if message.content.startswith('$image'):
            response = requests.get(message.attachments[0].url)
            with open("test.png", "wb") as f:
                f.write(response.content)
            await message.channel.send(parse_ocr(process_image()))

        if message.content.startswith("!price"):
            player_request = message.content[(len("!price")):].strip().split(",")
            await message.channel.send(
                get_player(int(player_request[0]), player_request[1] + " " + player_request[2], db))

        if message.content.startswith("!input"):
            player_request = message.content[(len("!input")):].strip().split(",")
            await message.channel.send(update_price(int(player_request[0]), player_request[1] + " " + player_request[2],
                                                    int(player_request[3])))

            client.run('ODI2MDg0MzU5MTE1MjQzNTQw.YGHVAw.hxz02S9bniu2MADAhlZSOtE12yg')
