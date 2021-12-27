import discord
import asyncio
from discord.ext import commands
import utils
from utils import song_info
import json


class music(commands.Cog):
    songs_queue: list[song_info]
    my_ctx: commands.Context
    looping: bool

    def __init__(self, client):
        self.client = client
        self.songs_queue = []
        self.looping = False

    @commands.command(aliases=['l', 'leave', 'stop'])
    async def disconnect(self, ctx: commands.Context):
        self.looping = False
        self.songs_queue = []
        if ctx.voice_client.is_playing():
            await utils.send_answer(ctx, "So long, farewell, no more sailing...")
        await ctx.voice_client.disconnect()

    @commands.command(aliases=['p'])
    @commands.cooldown(per=1, rate=3.0, type=commands.BucketType.guild)
    async def play(self, ctx: commands.Context, *, url: str = ''):
        if url == '':
            await utils.send_answer(ctx, "Song not identified")
            return
        if not await self.join(ctx):
            return
        info = utils.get_song_info(url)
        await self.add_song_to_queue(ctx, info)
        if len(self.songs_queue) == 1:
            await self.play_song(ctx, info)

    @commands.command(aliases=['d', 'r'])
    async def remove(self, ctx: commands.Context, *, idx):
        if idx.isnumeric():
            i = int(idx) - 1
        else:
            await utils.send_answer(ctx, "That's not a number")
            return
        if len(self.songs_queue) == 0:
            await self.skip(ctx)
        elif i <= len(self.songs_queue) and (i >= 0):
            await utils.send_answer(ctx, f"Removing song: `{self.songs_queue[i]['title']}`")
            self.songs_queue.pop(i)
            if i == 0:
                await self.skip(ctx)
        else:
            await utils.send_answer(ctx, "Index out of bounds")

    @commands.command(aliases=['repeat'])
    async def loop(self, ctx: commands.Context):
        self.looping = not self.looping
        if self.looping:
            await utils.send_answer(ctx, "Looping activated!")
        else:
            await utils.send_answer(ctx, "Looping deactivated!")

    @commands.command()
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()
        await utils.send_answer(ctx, "Song is paused . . .")

    @commands.command()
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()
        await utils.send_answer(ctx, "Resuming song . . .")

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context):
        if len(self.songs_queue) == 0:
            await utils.send_answer(ctx, "The current queue is empty :(")
            return
        await ctx.trigger_typing()
        song_list = []
        for song in self.songs_queue:
            song_list += song    
        await utils.send_embed(ctx, song_list)
            

    @commands.command()
    async def skip(self, ctx: commands.Context):
        self.looping = False
        vc = ctx.voice_client
        if vc is None:
            await utils.send_answer(ctx, "Not in a voice channel")
            return
        self.songs_queue = self.songs_queue[1:]
        vc.pause()
        if len(self.songs_queue) > 0:
            await self.play_song(ctx, self.songs_queue[0])
        else:
            await self.disconnect(ctx)

    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await utils.send_answer(ctx, "You must be in a voice channel")
            return False
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            print("joining channel")
            self.songs_queue = []
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            if not ctx.voice_client.is_playing():
                print("changing channel")
                self.songs_queue = []
                await ctx.voice_client.move_to(voice_channel)
            else:
                await utils.send_answer(ctx, "I'm already playing songs! Come and join us!")
                return False
        return True

    async def add_song_to_queue(self, ctx: commands.Context, info: song_info,):
        self.songs_queue.append(info)
        await utils.send_answer(ctx, f"Song {info.title} added to queue! Queue has {len(self.songs_queue)} songs...")

    async def play_song(self, ctx: commands.Context, info: song_info):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        if not self.looping:
            print(f"Now Playing song {info.title}")
        vc = ctx.voice_client
        source = await discord.FFmpegOpusAudio.from_probe(info.yt_url, **FFMPEG_OPTIONS)
        self.my_ctx = ctx
        vc.play(source, after=self.after_play)

    def after_play(self, error):
        if not self.looping:
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
