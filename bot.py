##"C:\Users\D6rks\AppData\Local\Programs\Python\Python37-32/python.exe" d:/Code/EventBot/bot.py

import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_read():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)