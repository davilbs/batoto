import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import music

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

cogs = [music]

client = commands.Bot(command_prefix='?', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

print("Bot iniciado!")
client.run(TOKEN)