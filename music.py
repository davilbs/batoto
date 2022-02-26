import discord
import asyncio
from discord.ext import commands
import utils
import json


class music(commands.Cog):
    my_ctx = commands.Context

    def __init__(self, client):
        self.client = client
        self.songqueue = utils.SongQueue()
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

    # Join context channel
    async def join(self, ctx: commands.Context) -> bool:
        if ctx.author.voice is None:
            await utils.send_answer(ctx, "You must be in a voice channel")
            return False
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            self.songqueue.reset()
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            if not ctx.voice_client.is_playing():
                self.songqueue.reset()
                await ctx.voice_client.move_to(voice_channel)
            else:
                await utils.send_answer(ctx, "I'm already playing songs! Come and join us!")
                return False
        self.my_ctx = ctx
        return True

    # Play song from info and run after routine
    async def play_song(self, info: utils.SongInfo):
        try:
            if not self.songqueue.looping:
                print(f"Now Playing song {info.title}")
            source = await discord.FFmpegOpusAudio.from_probe(info.yt_url, **self.FFMPEG_OPTIONS)
            vc = self.my_ctx.voice_client
            vc.play(source, after=self.after_play)
        except discord.errors.ClientException:
            print("Failed to stop song")


    # Routine after finishing playing a song
    def after_play(self, error):
        if self.songqueue.empty():
            coro = self.disconnect(self.my_ctx)
        else:
            coro = self.play_song(self.songqueue.next())
        fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)
        try:
            fut.result()
        except:
            if error is None:
                print(f"Successful execution!")    
            else:
                print(f"Error: {error}")

    @commands.command(aliases=['l', 'leave', 'stop'])
    async def disconnect(self, ctx: commands.Context):
        self.songqueue.reset()
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

        if 'spotify' == url.split()[0]:
            info = utils.get_song_info_spotify(url)
        else:
            info = utils.get_song_info_yt(url)
            
        await self.songqueue.add_song(ctx, info)
        if self.songqueue.size == 1:
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
        if self.songqueue.empty():
            await self.disconnect(ctx)
        else:
            await self.play_song(self.songqueue.next())

    @commands.command(aliases=['q'])
    async def queue(self, ctx: commands.Context):
        if self.songqueue.empty():
            await utils.send_answer(ctx, "Queue empty")
        await self.songqueue.send_queue(ctx)

    @commands.command(aliases=['d', 'r'])
    async def remove(self, ctx: commands.Context, *, idx):
        if not idx.isnumeric():
            return await utils.send_answer(ctx, "That's not a number")
        i = int(idx) - 1
        if not await self.songqueue.remove_song(ctx, i):
            return await utils.send_answer(ctx, "Index out of bounds")
        if i == self.songqueue.index:
            await self.skip(ctx)

def setup(client):
    client.add_cog(music(client))