import os
import dotenv
import random
import discord
from discord.ext import commands
import botskills.music.music as music, botskills.funny.funny as funny
from botskills.utils.utils import is_prod

if is_prod:
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
else:
    DISCORD_TOKEN = dotenv.dotenv_values("./botskills/utils/.env")['DISCORD_TOKEN']

cogs = [music, funny]

client = commands.Bot(command_prefix='?', intents=discord.Intents.all())


@client.event
async def on_ready():
    print("Bot initialized!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()
    if ("aleatorio" in msg) or ('aleatório' in msg):
        await funny.nome_aleatorio(message)

    await client.process_commands(message)

print("Initializing cogs...")
for i in range(len(cogs)):
    cogs[i].setup(client)

client.run(DISCORD_TOKEN)
