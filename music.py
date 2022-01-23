import discord
import asyncio
from discord.ext import commands
import utils
import json


class music(commands.Cog):
    my_ctx = commands.Context

    def __init__(self, client):
        self.client = client
        self.queue = utils.song_queue()
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

    # Join context channel
    async def join(self, ctx: commands.Context) -> bool:
        if ctx.author.voice is None:
            await utils.send_answer(ctx, "You must be in a voice channel")
            return False
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            self.queue.reset()
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            if not ctx.voice_client.is_playing():
                self.queue.reset()
                await ctx.voice_client.move_to(voice_channel)
            else:
                await utils.send_answer(ctx, "I'm already playing songs! Come and join us!")
                return False
        self.my_ctx = ctx
        return True

    # Play song from info and run after routine
    async def play_song(self, info: utils.song_info):
        if not self.queue.loop():
            print(f"Now Playing song {info.title}")
        source = await discord.FFmpegOpusAudio.from_probe(info.yt_url, **self.FFMPEG_OPTIONS)
        vc = self.my_ctx.voice_client
        vc.play(source, after=self.after_play)

    # Routine after finishing playing a song
    def after_play(self, error):
        if self.queue.empty():
            coro = self.disconnect(self.my_ctx)
        else:
            coro = self.play_song(self.queue.next())
        fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)
        try:
            fut.result()
        except:
            print(f"Error: {error}")

    @commands.command(aliases=['l', 'leave', 'stop'])
    async def disconnect(self, ctx: commands.Context):
        self.queue.reset()
        if ctx.voice_client.is_playing():
            await utils.send_answer(ctx, "So long, farewell, no more sailing...")
        await ctx.voice_client.disconnect()

    @commands.command(aliases=['p'])
    @commands.cooldown(per=1, rate=3.0, type=commands.BucketType.guild)
    async def play(self, ctx: commands.Context, *, url: str = ''):
        if url == '':
            return await utils.send_answer(ctx, "Song not identified")
        if not await self.join(ctx):
            return await utils.send_answer(ctx, "Could not join")
        info = utils.get_song_info(url)
        await self.queue.add_song(ctx, info)
        if self.queue.size == 1:
            await self.play_song(info)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()
        await utils.send_answer(ctx, "Song is paused . . .")

    @commands.command()
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()
        await utils.send_answer(ctx, "Resuming song . . .")

    @commands.command()
    async def skip(self, ctx: commands.Context):
        if self.my_ctx.voice_client is None:
            return await utils.send_answer(ctx, "Not playing songs now")
        self.my_ctx.voice_client.pause()
        await self.play_song(self.queue.next())

    @commands.command(aliases=['d', 'r'])
    async def remove(self, ctx: commands.Context, *, idx):
        if not idx.isnumeric():
            return await utils.send_answer(ctx, "That's not a number")
        i = int(idx) - 1
        if i == self.queue.index:
            return await self.skip(ctx)
        if not await self.queue.remove_song(ctx, i):
            await utils.send_answer(ctx, "Index out of bounds")

def setup(client):
    client.add_cog(music(client))