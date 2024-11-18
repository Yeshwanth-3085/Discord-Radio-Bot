import aiohttp, asyncio, discord, yt_dlp
from discord.ext import commands, tasks

RADIO_STREAM_URL = 'https://ais-sa1.streamon.fm/7217_48k.aac'
SONG_METADATA_URL = 'https://yp.cdnstream1.com/metadata/7217_48k/current.json'
LOGO_URL = 'https://s3.amazonaws.com/streaming-player-assets/CISFFM/custom/images/PulseLogo-home5.png'
YDL_OPTS = {'quiet': True, 'default_search': 'ytsearch', 'noplaylist': True, 'extract_flat': True, 'skip_download': True}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = '$', intents = intents)

emb_msg = None
com_cha = None
last_song = None

async def send_message(ctx, text, loop, delay):
    if loop:
        msg = await ctx.send(text)
        for i in range(1, 6):
            await msg.edit(content = f"{text}{'.' * i}")
        return msg
    else:
        msg = await ctx.send(text)
        await asyncio.sleep(delay)
        await msg.delete()

async def connect_or_move(ctx, com):
    global com_cha, last_song
    await ctx.message.delete()
    voice_client = ctx.voice_client
    if ctx.author.voice == None:
        await send_message(ctx, "You're not in a Voice Channel", False, 5)
    elif voice_client and voice_client.is_connected():
        if voice_client.channel == ctx.author.voice.channel:
            await send_message(ctx, 'Already in Same Voice Channel', False, 5)
        else:
            if com == 'move':
                if com_cha != ctx.channel:
                    last_song = None
                com_cha = ctx.channel
                channel = ctx.author.voice.channel
                msg = await send_message(ctx, 'Moving', True, None)
                if send_now_playing_loop.is_running():
                    send_now_playing_loop.stop()
                await voice_client.channel.edit(status = None)
                await voice_client.move_to(channel)
                await voice_client.guild.change_voice_state(channel = channel, self_deaf = True, self_mute = False)
                await msg.delete()
                await send_message(ctx, 'Moved', False, 2.5)
                await send_now_plaing_once(ctx)
            else:
                await send_message(ctx, "Already in a Voice Channel\nIf You Want Me to Move to a Different Voice Channel use 'move' Command", False, 5)
    else:
        if com == 'connect':
            if com_cha != ctx.channel:
                last_song = None
            com_cha = ctx.channel
            channel = ctx.author.voice.channel
            msg = await send_message(ctx, 'Connecting', True, None)
            voice_client = await channel.connect()
            await voice_client.guild.change_voice_state(channel = channel, self_deaf = True, self_mute = False)
            await msg.delete()
            await send_message(ctx, 'Connected', False, 2.5)
            msg = await send_message(ctx, 'Tuning into: 107.7 Pulse FM (CISF FM) :satellite:', True, None)
            player = discord.FFmpegPCMAudio(RADIO_STREAM_URL, **{'options': '-vn'})
            voice_client.play(player, after = lambda e: print(f'Player error: {e}') if e else None)
            await msg.delete()
            await send_message(ctx, 'Tuned into: 107.7 Pulse FM (CISF FM) :radio:', False, 2.5)
            await send_now_plaing_once(ctx)
        else:
            await send_message(ctx, 'Connect Me to a Voice Channel First', False, 5)

async def now_playing():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SONG_METADATA_URL) as response:
                if response.status == 200:
                    meta_data = await response.json()
                    meta_data = meta_data[0]
                    song_data = {
                                 'song': meta_data.get('TIT2') or 'Commercial',
                                 'album': meta_data.get('TALB') or '',
                                 'artist': meta_data.get('TPE1') or '' if meta_data.get('TPE1') != 'Pulse FM' else '',
                                 'album_art': meta_data.get('WXXX_album_art') or LOGO_URL
                                }
                    if song_data['album'] == '' and song_data['artist'] == '':
                        details = f"**{song_data['song']}**"
                    elif song_data['artist'] == '':
                        details = f"**Song: **{song_data['song']}\n**Album: **{song_data['album']}"
                    elif song_data['album'] == '':
                        details = f"**Song: **{song_data['song']}\n**Artist: **{song_data['artist']}"
                    else:
                        details = f"**Song: **{song_data['song']}\n**Album: **{song_data['album']}\n**Artist: **{song_data['artist']}"
                    video_url = None
                    if song_data['artist']:
                        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                            info = ydl.extract_info(f"ytsearch: {song_data['artist']} - {song_data['song']} Official Music Video", download = False)
                            if info and 'entries' in info:
                                video_url = info['entries'][0]['url']
                    embed = discord.Embed(title = 'Now Playing', description = details, color = discord.Color.blue(), url = video_url)
                    embed.set_thumbnail(url = song_data['album_art'])
                    embed.set_footer(text = "107.7 Pulse FM (CISF FM)\nYour Home for the 90's, 2K & Today!", icon_url = LOGO_URL)
                    return embed, song_data
        return None
    except Exception as e:
        print(f'Error fetching song data: {e}')
        return None

async def send_now_plaing_once(ctx):
    global emb_msg, last_song
    voice_client = ctx.voice_client
    np = await now_playing()
    if np:
        embed = np[0]
        song_data = np[1]
        if song_data != last_song:
            if last_song and song_data['song'] == last_song['song']:
                await emb_msg.delete()
            emb_msg = await ctx.send(embed = embed)
        if song_data['artist']:
            await voice_client.channel.edit(status = f"**Now Playing: **{song_data['song']} by {song_data['artist']}")
        else:
            await voice_client.channel.edit(status = f"**Now Playing: **{song_data['song']}")
        last_song = song_data
    if send_now_playing_loop.is_running():
        send_now_playing_loop.restart(ctx)
    else:
        send_now_playing_loop.start(ctx)

@tasks.loop(seconds = 5)
async def send_now_playing_loop(ctx):
    global emb_msg, last_song
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        np = await now_playing()
        if np:
            embed = np[0]
            song_data = np[1]
            if song_data != last_song:
                await asyncio.sleep(35)
                if last_song and song_data['song'] == last_song['song']:
                    await emb_msg.delete()
                emb_msg = await ctx.send(embed = embed)
                if song_data['artist']:
                    await voice_client.channel.edit(status = f"**Now Playing: **{song_data['song']} by {song_data['artist']}")
                else:
                    await voice_client.channel.edit(status = f"**Now Playing: **{song_data['song']}")
                last_song = song_data

@bot.event
async def on_ready():
    activity = discord.Activity(type = discord.ActivityType.listening, name = "📻 107.7 Pulse FM (CISF FM) | Your Home for the 90's, 2K & Today!")
    await bot.change_presence(activity = activity)

@bot.command(name = 'connect')
async def connect(ctx):
    await connect_or_move(ctx, 'connect')

@bot.command(name = 'disconnect')
async def disconnect(ctx):
    await ctx.message.delete()
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        msg = await send_message(ctx, 'Disconnecting', True, None)
        voice_client.stop()
        if send_now_playing_loop.is_running():
            send_now_playing_loop.stop()
        await voice_client.channel.edit(status = None)
        await voice_client.disconnect()
        await msg.delete()
    await send_message(ctx, 'Disconnected', False, 2.5)

@bot.command(name = 'move')
async def move(ctx):
    await connect_or_move(ctx, 'move')

@bot.command(name = 'ping')
async def ping(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title = ':ping_pong: Pong!', description = f'Latency: {round(bot.latency * 1000)}ms :wireless:', color = discord.Color.blue())
    msg = await ctx.send(embed = embed)
    await asyncio.sleep(10)
    await msg.delete()

bot.run('YOUR-BOT-TOKEN')
