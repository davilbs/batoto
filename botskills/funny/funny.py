import random
from discord.ext import commands


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


class Funny(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(Funny(client))
