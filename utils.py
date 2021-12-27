import discord
import asyncio
from discord.ext import commands
import youtube_dl
import json

async def send_answer(ctx: commands.Context, msg: str):
    if "\n" in msg:
        msg = f"```{msg}```"
    else:
        msg = f"`{msg}`"
    await ctx.send(msg)

async def send_embed(ctx: commands.Context, song_list: list[discord.Embed]):
    ch_webhooks = await ctx.channel.webhooks()
    webhook = discord.utils.get(ch_webhooks, name='test')
    webhook_url = webhook.token
    discord.Webhook

def get_song_info(arg: str):
    YDL_OPTIONS = {'format': 'bestaudio', 
                   'noplaylist': True,
                   'ignoreerrors': True}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        if 'http://' in arg:
            return song_info(ydl.extract_info(arg, download=False))
        arg = f"ytsearch5:{arg} Music"
        alldata = ydl.extract_info(arg, download=False)
        return song_info(alldata['entries'][0])

class song_info():
    title: str
    artist: str
    sthumbnail: str
    lthumbnail: str
    yt_url: str
    duration: int
    def __init__(self, info: dict):
        if 'track' in info:
            self.title = info['track']
        else:
            self.title = info['title']
        if 'artist' in info:
            self.artist = info['artist']
        else:
            self.artist = "Not batoto"
        self.sthumbnail = info['thumbnails'][0]['url']
        self.lthumbnail = info['thumbnails'][-1]['url']
        self.yt_url = info['formats'][0]['url']
        self.duration = info['duration']
    
    def create_embed(self):
        embed_message = discord.Embed(title=self.title)
        embed_message.set_thumbnail(url=self.sthumbnail)
        embed_message.set_author(name=self.artist)
        return embed_message