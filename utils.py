import discord
from discord.ext import commands
import youtube_dl

async def send_answer(ctx: commands.Context, msg: str):
    if "\n" in msg:
        msg = f"```{msg}```"
    else:
        msg = f"`{msg}`"
    await ctx.send(msg)

def get_song_info(arg: str):
    YDL_OPTIONS = {'format': 'bestaudio', 
                   'noplaylist': True,
                   'ignoreerrors': True}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        if 'http' in arg:
            return song_info(ydl.extract_info(arg, download=False))
        arg = f"ytsearch:{arg} Music"
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

class song_queue():
    # Initialize empty queue
    def __init__(self):
        self.reset()

    # Insert song int queue
    async def add_song(self, ctx: commands.Context, info: song_info):
        self.queue.append(info)
        self.size += 1
        await send_answer(ctx, f"Song [{info.title}] added to queue! Queue has {self.size} songs...")

    # Remove song from queue
    async def remove_song(self, ctx: commands.Context, idx: int = 0):
        if (self.size <= idx) or (idx < 0):
            return False
        info = self.queue.pop(idx)
        self.size -= 1
        await send_answer(ctx, f"Song [{info.title}] removed from queue! Queue has {self.size} songs...")
        return True

    # Reset queue values
    def reset(self):
        self.queue = []
        self.index = 0
        self.size = 0
        self.looping = False

    def print(self):
        for s in self.queue:
            print(f"{s.title}")

    # Check if queue is empty
    def empty(self):
        return self.size == 0

    # Get next song in queue
    def next(self):
        self.index = (self.index + 1) % self.size
        return self.queue[self.index]

