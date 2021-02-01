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

#Starts multithreaded timer to check tasks at the interval
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
        await asyncio.sleep(900) #number of seconds in the interval to check tasks
        #currently set to 15 minutes

async def checkTasks():
    minThresh = 30 #minutes in advance to check for tasks

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

        #Checks to see if the task is in the past, and if so deletes it from the lines                          
        if mins < 0:
            del lines[lines.index(line)]
    
    #rewrites the file without tasks in the past
    with open ('tasks.csv', 'w') as file:
        for line in lines:
            file.write(line)
    
    return

#converts time from military time to standard time
def timeConvert(miliTime):
    hours, minutes, seconds = str(miliTime).split(":")
    hours, minutes = int(hours), int(minutes)
    setting = "AM"
    if hours > 12:
        setting = "PM"
        hours -= 12
    return (("%02d:%02d " + setting) % (hours, minutes))

#command called when a user executes the $addTask function
#little to no error checking, so precise commands are a current nessecity
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
    
#On Ready event for Discord API. Starts the timer
@client.event
async def on_ready():
    global amOnline
    print('We have logged in as {0.user}'.format(client))
    print('Current time is {0}'.format(startTime))
    amOnline = True

    #starting timer
    await taskTimer()

#Sets up Discord API on_message event, which is called whenever the bot sees a message. 
@client.event
async def on_message(message):
    #Prevents the bot from messaging itself
    if message.author == client.user:
        return

    #Test function to assure the bot works correct
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    #Function to add task to the internal calender (csv file)
    if message.content.startswith('$addTask'):
        try:
            addTask(message.content[9:], message.author.id)
        except: #Catches all errors (very rough)
            await message.channel.send('Invalid command format')
        else:
            await message.channel.send('Added task to internal calender')

    #Sends a help command giving the format of the command
    if message.content.startswith('$help'):
        await message.channel.send('Task format is: \n $addTask Month, Day, Year | HH:MM (In Military) | Description (If applicable)')

    #command that can be used to quit the bot in the case that it is misbehaving
    #Can only be used by users with administrator privileges in the current channel.
    if message.author.permissions_in(message.channel).administrator:
        if message.content.startswith('$quit'):
            global amOnline
            amOnline = False
                
            print("Shutting down")
            await message.channel.send('Shutting down!')
            exit(1)

client.run(TOKEN)