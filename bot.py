##python bot.py

import os
from datetime import datetime, timezone
import asyncio
import discord
from dotenv import load_dotenv
import math

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
startTime = datetime.now()
amOnline = False


async def taskTimer():
    global amOnline
    loop = asyncio.get_running_loop()
    end_time = loop.time() + 1.0
    while True:
        print("Checking tasks at {0}".format(datetime.now()))
        await checkTasks()
        #todo await updateTasks (remove tasks that have been completed)
        if(not amOnline):
            break
        await asyncio.sleep(15)

async def checkTasks():
    minThresh = 30
    currentTime = datetime.now(tz=timezone.utc).timestamp()

    lines = []

    with open ('tasks.csv', 'r') as file:
        lines = file.readlines()

    for line in lines:
        event = line.split(',')

        #Time conversion from UTC timstamp to Local Standard Time
        mins = (float(event[0]) - currentTime)/60
        realTime = datetime.fromtimestamp(float(event[0]), tz=timezone.utc)
        realTime = realTime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        realTime = realTime.time()
        realTime = timeConvert(realTime)
        if mins < minThresh and mins > 0:
            #remind user that they have a meeting in x minutes
            user = await client.fetch_user(int(event[1]))
            if not user == None:
                try: 
                    description = event[2]
                except IndexError:
                    await user.send("You have a meeting at {0}, which is in {1} minutes".format(realTime, mins))
                else:
                    await user.send("You have a meeting at {0}, which is in about {1} minute(s)\n\nYou gave the description as:\n {2}".format(realTime, math.floor(mins), description))
        #Checks to see if the task is in the past, and marks for deletiong                            
        if mins < 0:
            del lines[lines.index(line)]
    
    with open ('tasks.csv', 'w') as file:
        for line in lines:
            file.write(line)
    
    #Handles deleting marked events during a check task
    
    return

def timeConvert(miliTime):
    hours, minutes, seconds = str(miliTime).split(":")
    hours, minutes = int(hours), int(minutes)
    setting = "AM"
    if hours > 12:
        setting = "PM"
        hours -= 12
    return (("%02d:%02d " + setting) % (hours, minutes))

def addTask(inputString, author):
    split = inputString.split('|')
    date = split[0]
    time = split[1]
    description = ""
    hasDescription = False
    try:
        description = split[2]
    except IndexError:
        hasDescription = False
    else:
        hasDescription = True

    splitDate = date.split(',')
    splitTime = time.split(':')
    newDate = datetime(int(splitDate[2].strip()), 
                        int(splitDate[0].strip()), 
                        int(splitDate[1].strip()), 
                        int(splitTime[0].strip()), 
                        int(splitTime[1].strip())
                        )

    writableDate = newDate.fromtimestamp(newDate.timestamp(), tz=timezone.utc).timestamp()

    with open ('tasks.csv', 'a') as file:
        if not hasDescription:
            file.write('{0},{1}\n'.format(writableDate, author))
        else:
            file.write('{0},{1},{2}\n'.format(writableDate, author, description))
    

@client.event
async def on_ready():
    global amOnline
    print('We have logged in as {0.user}'.format(client))
    print('Setting current time as {0}'.format(startTime))
    amOnline = True

    #starting timer
    await taskTimer()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$addTask'):
        addTask(message.content[9:], message.author.id)
        await message.channel.send('Added task to internal calender')

    if message.content.startswith('$help'):
        await message.channel.send('Task format is: \n $addTask Month, Day, Year | HH:MM (In Military) | Description (If applicable)')

    if message.content.startswith('$quit'):
        global amOnline
        amOnline = False
            
        print("Shutting down")
        await message.channel.send('Shutting down!')
        exit(1)

client.run(TOKEN)