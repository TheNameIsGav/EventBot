##python bot.py

import os
import datetime
import discord
import threading
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
currentTime = datetime.datetime.now()
amOnline = False

def taskTimer():
    if(amOnline):
        checkTasks()
        #                           \/ Time in seconds between Checks
        mytimer = threading.Timer(3600.0, taskTimer)
        mytimer.start()

@client.event
async def on_ready():
    global amOnline
    print('We have logged in as {0.user}'.format(client))
    print('Setting current time as {0}'.format(currentTime))
    amOnline = True

    #starting timer
    taskTimer()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$quit'):
        global amOnline
        amOnline = False
        print("Shutting down")
        await message.channel.send('Shutting down!')
        exit(1)



client.run(TOKEN)
