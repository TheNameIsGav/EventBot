##python bot.py

import os
from datetime import datetime, timezone
import discord
import threading
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
startTime = datetime.now()
amOnline = False

def taskTimer():
    if(amOnline):
        checkTasks()
        #Every 15 minutes check for events 30 minutes in the future
        mytimer = threading.Timer(900.0, taskTimer)
        mytimer.start()

def checkTasks():
    minThresh = 30
    currentTime = datetime.now(tz=timezone.utc).timestamp()
    with open ('tasks.csv', 'r') as file:
        for line in file:
            event = line.split(',')
            if (float(event[0]) - currentTime)/60 < minThresh:
                #remind user that they have a meeting in x minutes
                return

@client.event
async def on_ready():
    global amOnline
    print('We have logged in as {0.user}'.format(client))
    print('Setting current time as {0}'.format(startTime))
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
