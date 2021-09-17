import discord
import asyncio
from discord.ext import commands
from discord.ext.commands.core import command
import youtube_dl

class music(commands.Cog):
    songs_queue: list
    my_ctx: commands.Context

    def __init__(self, client):
        self.client = client
        self.songs_queue = []

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await ctx.send("Você não tá no voice")
            return False
        voice_channel = ctx.author.voice.channel
        # TODO check if bot is playing already
        if ctx.voice_client is None:
            print("joining channel")
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            if not ctx.voice_client.is_playing():
                print("changing channel")
                await ctx.voice_client.move_to(voice_channel)
        return True
        
    
    @commands.command(aliases=['l', 'leave'])
    async def disconnect(self, ctx: commands.Context):
        self.songs_queue = []
        await ctx.send("So long, farewell, no more sailing...")
        await ctx.voice_client.disconnect()

    @commands.command(aliases=['p'])
    @commands.cooldown(per=1, rate=3.0, type=commands.BucketType.guild)
    async def play(self, ctx: commands.Context, url: str = ''):
        if url == '':
            await ctx.send("URL não especificada")
            return
        # print(f"trying to join {ctx.author.channel.name}")
        if not await self.join(ctx):
            return
        info = self.get_song_info(url)
        await self.add_song_to_queue(ctx,info)
        if len(self.songs_queue) == 1:
            await self.play_song(ctx, info)

    async def add_song_to_queue(self, ctx: commands.Context, info: dict,):
        self.songs_queue.append(info)
        await ctx.send(f"Song {info['title']} added to queue! Queue has {len(self.songs_queue)} songs...")

    def get_song_info(self, url: str):
        YDL_OPTIONS = {'format': 'bestaudio'}

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            return ydl.extract_info(url, download=False)

    async def play_song(self, ctx: commands.Context, info: dict):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
        'options': '-vn'}
        print(f"Now Playing song {info['title']}")
        vc = ctx.voice_client
        yt_url = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(yt_url, **FFMPEG_OPTIONS)
        self.my_ctx = ctx
        vc.play(source, after=self.after_play)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()
        await ctx.send("parey parey")

    @commands.command()
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()
        await ctx.send("voltey voltey")

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context):
        if len(self.songs_queue) == 0:
            await ctx.send("The current queue is empty :(")  
            return  
        queue_list = ''
        for song in self.songs_queue:
            queue_list += song['title']
            queue_list += "\n"
        await ctx.send(queue_list)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        vc = ctx.voice_client
        if vc is None:
            await ctx.send("Not in a voice channel")
            return
        self.songs_queue = self.songs_queue[1:]
        vc.pause()
        if len(self.songs_queue) > 0:
            await self.play_song(ctx, self.songs_queue[0])

    def after_play(self, error):
        self.songs_queue = self.songs_queue[1:]
        if len(self.songs_queue) > 0:
            coro = self.play_song(self.my_ctx, self.songs_queue[0])
        else:
            coro = self.disconnect(self.my_ctx)
        fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)
        try:
            fut.result()
        except:
            pass


def setup(client):
    client.add_cog(music(client))