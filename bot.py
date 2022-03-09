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
    print("Bot iniciado!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()
    if ("aleatorio" in msg) or ('aleatório' in msg):
        await nome_aleatorio(message)

    await client.process_commands(message)


async def nome_aleatorio(message):
    with open('nouns.txt', 'r') as f:
        nouns = f.read().splitlines()
    with open('adjectives.txt', 'r') as f:
        adjectives = f.read().splitlines()

    noun = nouns[random.randint(0, len(nouns))]
    adjective = adjectives[random.randint(0, len(adjectives))]
    vowels = ['a', 'e', 'i', 'o', 'u']
    rand_name = "You are a"
    if adjective[0] in vowels:
        rand_name += 'n'

    name = " " + adjective + " " + noun
    rand_name += name

    await message.channel.send(rand_name)

print("Inicializando cogs...")
for i in range(len(cogs)):
    cogs[i].setup(client)

client.run(DISCORD_TOKEN)
