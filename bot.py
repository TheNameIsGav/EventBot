import os
import discord
from dotenv import load_dotenv

load_dotenv()

with open ("token.token", 'r') as tokenFile:
    preToken = tokenFile[0]

TOKEN = os.getenv(preToken)


