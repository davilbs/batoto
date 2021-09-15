import discord
from discord.ext import commands
import music

cogs = [music]

client = commands.Bot(command_prefix='?', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

print("Bot iniciado!")
client.run(NzMzMjk2MTY0MjA3ODUzNjI4.XxBFRQ.FWjwxQsj9SaJc6UDQ-xEDFDRMQE)