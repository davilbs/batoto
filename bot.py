import os
import discord
import random
from discord.ext import commands
import music

cogs = [music]

client = commands.Bot(command_prefix='?', intents = discord.Intents.all())

@client.event
async def on_ready():
    print("Bot iniciado!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    with open('nouns.txt', 'r') as f:
        nouns = f.read().splitlines()
    with open('adjectives.txt', 'r') as f:
        adjectives = f.read().splitlines()

    noun = nouns[random.randint(0, len(nouns))]
    adjective = adjectives[random.randint(0, len(adjectives))]
    vowels = ['a', 'e', 'i', 'o', 'u']
    if message.content == 'aleatorio' or message.content == 'aleatório':
        rand_name = "You are a"
        if adjective[0] in vowels:
            rand_name += 'n'

        name = " " + adjective + " " + noun
        rand_name += name
        
        await message.channel.send(rand_name)

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run("NzMzMjk2MTY0MjA3ODUzNjI4.XxBFRQ.FWjwxQsj9SaJc6UDQ-xEDFDRMQE")