import youtube_dl
import spotipy
import dotenv
import json
import time
import os
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands
from discord import Embed

is_prod = os.environ.get('IS_HEROKU', None)

if is_prod:
    SPOTIFY_TOKEN = os.environ.get('SPOTIFY_TOKEN')
    SPOTIFY_ID = os.environ.get('SPOTIFY_ID')
else:
    SPOTIFY_TOKEN = dotenv.dotenv_values("./botskills/utils/.env")['SPOTIFY_TOKEN']
    SPOTIFY_ID = dotenv.dotenv_values("./botskills/utils/.env")['SPOTIFY_ID']

class SongInfo():
    title: str
    artist: str
    requester: dict
    duration: int
    sthumbnail: str
    lthumbnail: str
    yt_url: str
    spotify: bool
    playlist: str
    webpage_url: str

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
        self.playlist = info['playlist']
        self.spotify = info['spotify']
        self.webpage_url = info['webpage_url']

    def create_embed(self):
        embed_message = Embed(title=self.title)
        embed_message.set_thumbnail(url=self.sthumbnail)
        embed_message.set_author(name=self.artist)
        return embed_message
    
    def set_requester(self, name, avatar):
        self.requester = {"name": name, "avatar": avatar}

class SongQueue():
    queue: list
    # Initialize empty queue
    def __init__(self):
        self.reset()

    # Insert song int queue
    async def add_song(self, ctx: commands.Context, info: SongInfo, playlist: bool = False):
        info.set_requester(ctx.author.display_name, ctx.author.avatar_url)
        self.queue.append(info)
        self.size += 1
        if not playlist:
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
        queue = Embed(title=f"{ctx.guild.name} song list")
        total_time = 0
        for i in range(self.index, min(self.size, (9 + self.index))):
            if self.queue[i].duration > 3600:
                song_time = time.strftime('%H:%M:%S', time.gmtime(self.queue[i].duration))
            else:
                song_time = time.strftime('%M:%S', time.gmtime(self.queue[i].duration))
            val = f"Length: {song_time} | [yt link]({self.queue[i].webpage_url})"
            nam = f"{i+1}. [{self.queue[i].title}]"
            if i == self.index:
                nam += "  `currently playing`"
            print(nam, val)
            queue.add_field(name=nam,value=val, inline=False)

        for i in range(self.size):
            total_time += self.queue[i].duration
        total_time = time.strftime('%H:%M:%S', time.gmtime(total_time))
        footer = f"{self.size} songs in queue. Total duration: {total_time}"
        print(footer)
        queue.set_footer(text=footer)
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
    msg = Embed(title=song.title, url=song.webpage_url,
                description=f"Song added by {user}")
    msg.set_author(name=user, icon_url=ctx.author.avatar_url)
    msg.set_thumbnail(url=song.sthumbnail)
    return await ctx.send(embed=msg)


def get_song_info_yt(arg: str):
    YDL_OPTIONS = {'format': 'bestaudio',
                   'noplaylist': True,
                   'ignoreerrors': True}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        if 'http' in arg:
            return SongInfo(ydl.extract_info(arg, download=False))
        arg = f"ytsearch:{arg} Music"
        alldata = ydl.extract_info(arg, download=False)
        song = alldata['entries'][0]
        with open("youtube_track.json", 'w') as f:
            json.dump(song, f)
        song['playlist'] = False
        song['spotify'] = False
        return SongInfo(song)

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIFY_ID, SPOTIFY_TOKEN))

def get_song_info_spotify(arg: str):
    args = arg.split()
    if "playlist" in args[1]:
        # Add playlist tracks
        playlist = spotify.playlist(args[1])
        total = playlist["tracks"]["total"]
        pos = 0
        while pos < total:
            results = spotify.playlist_tracks(args[1], offset=pos)
            for item in results["items"]:
                track = item["track"]
                info = {
                    "search": f"{track['name']} {track['artists'][0]['name']}",
                    "title": f"{track['name']}",
                    "artist": f"{track['artists'][0]['name']}",
                    "spotify": True,
                    "playlist": f"{playlist['name']}"
                }
                yield info
            pos += 100
    elif "track" in args[1]:
        # Add track to queue
        # - Tag tracks as spotify
        track = spotify.track(args[1])
        info = {
            "search": f"{track['name']} {track['artists'][0]['name']}",
            "title": f"{track['name']}",
            "artist": f"{track['artists'][0]['name']}",
            "spotify": True,
            "playlist": None
        }
        yield info
