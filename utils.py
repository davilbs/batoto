import discord
from discord.ext import commands
from discord import Embed
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import dotenv

SPOTIFY_TOKEN = dotenv.dotenv_values(".env")['SPOTIFY_TOKEN']
SPOTIFY_ID = dotenv.dotenv_values(".env")['SPOTIFY_ID']

class SongInfo():
    title: str
    artist: str
    requester: dict
    duration: int

    def create_embed(self):
        embed_message = discord.Embed(title=self.title)
        embed_message.set_thumbnail(url=self.sthumbnail)
        embed_message.set_author(name=self.artist)
        return embed_message
    
    def set_requester(self, name, avatar):
        self.requester = {"name": name, "avatar": avatar}

class YTSongInfo(SongInfo):
    sthumbnail: str
    lthumbnail: str
    yt_url: str

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

class SpotifySongInfo(SongInfo):
    pass

class SongQueue():
    # Initialize empty queue
    def __init__(self):
        self.reset()

    # Insert song int queue
    async def add_song(self, ctx: commands.Context, info: SongInfo):
        self.queue.append(info)
        info.set_requester(ctx.author.display_name, ctx.author.avatar_url)
        self.size += 1
        await send_embed(ctx, info)

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

    async def send_queue(self, ctx: commands.Context):
        queue = Embed(title="Song queue list")
        total_time = 0
        for i in range(self.index, min(self.size, 9)):
            if self.queue[i].duration > 3600:
                song_time = time.strftime('%H:%M:%S', time.gmtime(self.queue[i].duration))
            else:
                song_time = time.strftime('%M:%S', time.gmtime(self.queue[i].duration))
            queue.add_field(name=f"{i+1}. Length: {song_time}", value=f"[{self.queue[i].title}]({self.queue[i].yt_url})", inline=False)

        for i in range(self.size):
            total_time += self.queue[i].duration
        total_time = time.strftime('%H:%M:%S', time.gmtime(total_time))
        queue.set_footer(text=f"{self.size} songs in queue. Total duration: {total_time}")
        await ctx.send(embed=queue)

    # Check if queue is empty
    def empty(self):
        return self.size == 0

    # Get next song in queue
    def next(self):
        self.index = (self.index + 1) % self.size
        return self.queue[self.index]


async def send_answer(ctx: commands.Context, msg: str):
    if "\n" in msg:
        msg = f"```{msg}```"
    else:
        msg = f"`{msg}`"
    await ctx.send(msg)


async def send_embed(ctx: commands.Context, song: SongInfo):
    user = ctx.author.display_name
    msg = Embed(title=song.title, url=song.yt_url,
                description=f"Song added by {user}")
    msg.set_author(name=user, icon_url=ctx.author.avatar_url)
    msg.set_thumbnail(url=song.sthumbnail)
    await ctx.send(embed=msg)


def get_song_info_yt(arg: str):
    YDL_OPTIONS = {'format': 'bestaudio',
                   'noplaylist': True,
                   'ignoreerrors': True}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        if 'http' in arg:
            return YTSongInfo(ydl.extract_info(arg, download=False))
        arg = f"ytsearch:{arg} Music"
        alldata = ydl.extract_info(arg, download=False)
        return YTSongInfo(alldata['entries'][0])

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIFY_ID, SPOTIFY_TOKEN))

def get_song_info_spotify(arg: str):
    args = arg.split()
    # https://open.spotify.com/playlist/7Gq4mz0gcOzqjdlqxh3EdO?si=dfa57c93533a46d7
    if "playlist" in args[1]:
        # Add playlist
        # - Does not update automatically
        # - Need to tag all songs of same playlist for simultaneous removal
        # - Add all sequentially
        pass
    elif "track" in args[1]:
        # Add track to queue
        # - Tag tracks as spotify
        pass
    pass
