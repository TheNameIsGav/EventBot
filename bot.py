##python bot.py

import os
from datetime import datetime, timezone
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from collections.abc import Sequence
import json

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix='$')
amOnline = False

#Starts multithreaded timer to check tasks at the interval
async def taskTimer():
    global amOnline
    loop = asyncio.get_running_loop()
    end_time = loop.time() + 1.0
    while True:
        print("Checking tasks at {0}".format(datetime.now()))
        await checkTasks()
        if(not amOnline):
            break
        await asyncio.sleep(300) #number of seconds in the interval to check tasks
        #15 mins is 900 seconds

@client.command()
async def addTask(ctx, *args):
    users = []
    taskAuthor = ctx.author.id
    groupTask = False
    if len(args) == 0: #individual task
        await ctx.author.send("Setting up new individual task")
        users.append((await client.fetch_user(ctx.author.id)).id)
    else:
        groupTask = True
        displayUsers = []
        await ctx.author.send("Setting up new group task")
        for member in ctx.message.mentions:
            user = await client.fetch_user(member.id)
            displayUsers.append(user.display_name)
            users.append(member.id)
        await ctx.author.send("Created new team task with {} as participants".format(", ".join(displayUsers)))

    await ctx.author.send('Type \'QUIT\' at any time to exit task creation\nWhat date is this meeting on? (Month, Day, Year)')
    date = (await client.wait_for('message', check=message_check(channel=ctx.author.dm_channel))).content
    
    if checkQuit(date):
        await ctx.author.send("cancelled task creation")
        return

    await ctx.author.send('What time is this meeting at? (HH:MM)')
    time = (await client.wait_for('message', check=message_check(channel=ctx.author.dm_channel))).content

    if checkQuit(time):
        await ctx.author.send("cancelled task creation")
        return

    await ctx.author.send('Please add a description. If there is none, send \'no\'')
    description = (await client.wait_for('message', check=message_check(channel=ctx.author.dm_channel))).content

    if 'no' == description:
        description = "No description given"
    
    if checkQuit(description):
        await ctx.author.send("cancelled task creation")
        return

    splitDate = date.split(',')
    splitTime = time.split(':')
    newDate = datetime(int(splitDate[2].strip()), 
                        int(splitDate[0].strip()), 
                        int(splitDate[1].strip()), 
                        int(splitTime[0].strip()), 
                        int(splitTime[1].strip())
                        )

    writableDate = newDate.fromtimestamp(newDate.timestamp(), tz=timezone.utc).timestamp()
    
    task = {}
    task['author'] = taskAuthor
    task['users'] = users
    task['timestamp'] = writableDate
    task['description'] = description
    task['passed'] = False

    with open('tasks.json', 'a') as file:
        json.dump(task, file)
        file.write('\n')

    await ctx.author.send('Added task to internal calender')
    
    if(groupTask):
        for id in users:
            if not id == taskAuthor:
                user = await client.fetch_user(id)
                await user.send("You have been added to a group meeting at {} by {} with description ".format(newDate, ctx.author.display_name, description))

def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)

def message_check(channel=None, author=None, content=None, ignore_bot=True):
    channel = make_sequence(channel)
    author = make_sequence(author)
    content = make_sequence(content)
    def check(message):
        if ignore_bot and message.author.bot:
            return False
        if channel and message.channel not in channel:
            return False
        if author and message.author not in author:
            return False
        actual_content = message.content
        if content and actual_content not in content:
            return False
        return True
    return check

def checkQuit(messageContent):
    if 'QUIT' in messageContent:
        return True
    else:
        return False

async def checkTasks():

    minuteCheckThresh = 30
    currentTime = datetime.now(tz=timezone.utc).timestamp()
    
    tasks = []
    with open("tasks.json", "r") as file:
        for line in file:
            newDict = json.loads(line)
            tasks.append(newDict)
            
    for task in tasks:
        mins = (task['timestamp'] - currentTime)/60
        realTime = datetime.fromtimestamp(task['timestamp'], tz=timezone.utc)
        realTime = realTime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        realTime = realTime.time()
        realTime = timeConvert(realTime)
        tmpAuthor = (await client.fetch_user(task['author'])).display_name

        if mins < minuteCheckThresh and mins > 0:
            #remind user that they have a meeting in x minutes
            for id in task['users']:
                user = await client.fetch_user(id)
                if not user == None:
                    await user.send("You have a meeting at {0}, which is in about {1} minutes, with description of: {2}\nthe author of this meeting is {3}".format(realTime, round(mins, 1), task['description'], tmpAuthor))

        if mins < 0:
            task['passed'] = True

    with open ('tasks.json', 'w') as file:
        for task in tasks:
            if not task['passed']:
                json.dump(task, file)
                file.write('\n')

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


@client.event
async def on_ready():
    global amOnline
    print('We have logged in as {0.user}'.format(client))
    print('Logged in at time {}'.format(datetime.now()))
    amOnline = True
    await taskTimer()

'''
add command to see users calender events
tell users when they are added to a group meeting
Fix error with individual meetings

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
'''

client.run(TOKEN)