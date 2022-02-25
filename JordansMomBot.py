# bot.py
import os
import enum
import asyncio
import time
import random
import requests
from eyed3 import mp3
import eyed3
import discord
from discord.ext import commands
from sound import Sound

with open('token.txt') as f:
    TOKEN = f.readline()
GUILD = 545759784553545758

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.voice_states = True
intents.reactions = True
bot = commands.Bot(command_prefix='#', intents = intents)

#region Events
@bot.event
async def on_ready():
    print(f'bruh be quiet {bot.user} is coming.')
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.event
async def on_voice_state_update(member, before, after):
    print(f'on_voice_state_update: entered')
    print(f'on_voice_state_update: member == {member.name}')
    if before.channel != None:
        print(f'on_voice_state_update: before == {before.channel.name}')
    else:
        print('on_voice_state_udpate: before == None')
    if after.channel != None and after.channel.name != 'The Worst Kind of People':
        print(f'on_voice_state_update: after == {after.channel.name}')
        print(f'on_voice_state_update: member status == {member.status}')
        if before.channel != after.channel:
            await member_join(member, after)
        if member.status != discord.Status.online and member.status != discord.Status.dnd:
            await member.move_to(None)
            await member.create_dm()
            await member.dm_channel.send('You can\'t speak in voice channels in Jordan\'s Mom if your status is set to Invisible or Away. Update your status and try again!')
    else:
        print('on_voice_state_udpate: after == None')

@bot.event
async def on_message(message):
    print(f'on_message: entered')
    if message.author == bot.user:
        return
    member = message.author
    voice_channel = get_voice_channel(member)
    is_in_voice_channel = voice_channel != None
    guild = get_guild()
    if is_in_voice_channel:
        await play_message_sound(message, voice_channel)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    #payload = discord.RawReactionActionEvent
    print('on_raw_reaction_add: entered')
    print(f'on_raw_reaction_add: event_type == {payload.event_type}')
    if payload.member.voice.channel != None:
        voice_channel = payload.member.voice.channel
        print(f'on_raw_reaction_add: reactor in voice channel {voice_channel.name}')
        emoji = payload.emoji
        print(f'on_raw_reaction_add: emoji is {emoji.name}')
        sound = random.choice(await get_sounds_by_emoji(emoji))
        print(f'on_raw_reaction_add: calling play_audio({voice_channel.name, sound.name})')
        await play_audio(voice_channel, sound)
#endregion

#region Commands
@bot.command(name='sound', help='Plays the requested sound in your voice channel. e.g. \'#sound Gleh\'')
async def on_sound_command(ctx, arg):
    print('on_sound_command: entered')
    print(f'on_sound_command: arg == {arg}')
    sounds = []
    print('Sound files:')
    for filename in os.listdir("BotFiles\Audio"):
        print(f'     {filename}')
        sounds.append(filename[:-4])
        print(f'     {filename[:-4]}')
    sound_name = arg
    sound = await get_sound_by_name(arg)
    if sound_name == None:
        print(f'play_audio: {sound_name} not in sounds')
        ctx.send(f'Sound {arg} not found.')
        return
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    if voice_channel != None:
        await play_audio(voice_channel, sound)
    else:
        await ctx.send(str(ctx.author.name) + "is not in a voice channel.")
    # Delete command after the audio is done playing.
    await ctx.message.delete()

@bot.command(name='soundlist', help = 'List of all sounds playable with the #sound command')
async def on_soundlist_command(ctx):
    print('on_soundlist_command: entered')
    sounds = await get_sounds()
    content = '```'
    for sound in sounds:
        content += sound.name + '\n'
    content += '```'
    my_message = await ctx.message.reply(content)
    await asyncio.sleep(60)
    await ctx.message.delete()
    await my_message.delete()

@bot.command(name='addsound', help = 'Tell Adam to write this help entry')
async def on_addsound_command(ctx):
    print('on_addsound_command: entered')
    if len(ctx.message.attachments) == 0:
        my_message = await ctx.message.reply('.MP3 must be attached to command message')
    elif len(ctx.message.attachments) > 1:
        my_message = await ctx.message.reply('Command message can only have one attachment')
    else:
        attachment = ctx.message.attachments[0]
        filename = attachment.filename
        print(f'on_addsound_command: filename == {filename}')
        extension = filename[-4:].upper()
        print(f'on_addsound_command: extension == {extension}')
        if extension == '.MP3':
            url = attachment.url
            print(f'on_addsound_command: url == {url}')
            full_save_path = 'BotFiles\Audio\\' + attachment.filename
            print(f'on_addsound_command: full_save_path == {full_save_path}')
            r = requests.get(url)
            with open(full_save_path, 'wb') as f:
                f.write(r.content)
            print(f'on_addsound_command: downloaded!')
            sound = get_sound(full_save_path)
            if sound == None:
                my_message = await ctx.message.reply('Title metadata is missing or has invalid characters')
            else:
                content = f'```Name: {sound.name}\nUsers: {sound.user_names}```'
                #my_message = await ctx.message.reply()
        else:
            my_message = await ctx.message.reply('File must be an .MP3')
    print(f'on_addsound_command: finished')

@bot.command(name = 'editsound', help = 'COMMAND NOT FINISHED! Opens the sound editing menu for a sound. e.g. #editsound Davinky?')
async def on_editsound_command(ctx, arg):
    print('on_editsound_command: entered')
    sound = await get_sound_by_name(arg)
    if sound == None:
        await ctx.message.reply(f'No sound found with title {arg}. Try ```#soundlist```.')
        return
    else:
        content = 'Sound Info\n'
        content += '```'
        content += 'Name:     '
        content += sound.name
        content += '\nUsers:    '
        for user in sound.user_names:
            content += user + '\n          '
        content += '\nEmoji:    '
        for emoji in sound.emoji_names:
            content += user + '\n          '
        content += '\nCreator:  '
        content += sound.creator_name
        content += '```\n'
        content += 'Options\n'
        content += '```'
        content += '1. Rename\n'
    await ctx.message.reply(content)
    #message = await bot.wait_for('message', check = check)
    #if
#endregion

def get_voice_channel(member):
    voice_channel = None
    if member.voice != None:
        if member.voice.channel != None:
            voice_channel = member.voice.channel
    return voice_channel

def get_guild():
    for guild in bot.guilds:
        if guild.id == GUILD:
            return guild
    raise Exception("Bot not in guild")

async def get_sound(path):
    print(f'get_sound: entered')
    sound = None
    if not os.path.exists(path):
        print(f'get_sound: path {path} does not exist')
        return
    mp3_file = mp3.Mp3AudioFile(path)
    if mp3_file.tag != None:
        name = mp3_file.tag.title
        if mp3_file.tag.artist != None:
            user_names = mp3_file.tag.artist.replace(' ', '').split(',')
        else:
            user_names = []
        if mp3_file.tag.album != None:
            emoji_names = mp3_file.tag.album.replace(' ', '').split(',')
        else:
            emoji_names = None
        sound = Sound(path, name, user_names, emoji_names)
    else:
        print(f'get_sound: bad/missing tag data')
    return sound

async def get_sounds():
    print(f'get_sounds: entered')
    sounds = []
    for file in os.listdir("BotFiles/Audio"):
        print(f'get_sounds: file == {file}')
        path = f'BotFiles/Audio/{file}'
        mp3_file = mp3.Mp3AudioFile(path)
        if mp3_file.tag != None:
            name = mp3_file.tag.title
            if mp3_file.tag.artist != None:            
                user_names = mp3_file.tag.artist.replace(' ', '').split(',')
            else:
                user_names = []
            if mp3_file.tag.album != None:            
                emoji_names = mp3_file.tag.album.replace(' ', '').split(',')
            else:
                emoji_names = []
            if mp3_file.tag.album_artist != None:
                creator_user_name = mp3_file.tag.album_artist
            else:
                creator_user_name = ''
            sounds.append(Sound(path, name, user_names, emoji_names, creator_user_name))
        else:
            print(f'get_sounds: bad/missing tag data')
    return sounds

def get_sound_names(sounds):
    print(f'get_sound_names: entered')
    sound_names = []
    for sound in sounds:
        sound_names.append(sound.name)
    return sound_names

async def get_sound_by_name(sound_name):
    print(f'get_sound_by_name: entered')
    for sound in await get_sounds():
        if sound.name.upper() == sound_name.upper():
            return sound
    return None

async def get_sounds_by_user(user):
    print(f'get_sounds_by_user: entered')
    sounds = []
    for sound in await get_sounds():
        for user_name in sound.user_names:
            if user_name.upper() == user.name.upper():
                sounds.append(sound)
    return sounds

async def get_sounds_by_emoji(emoji):
    print('get_sounds_by_emoji: entered')
    print(f'get_sounds_by_emoji: emoji.name == {emoji.name}')
    sounds = []
    for sound in await get_sounds():
        for emoji_name in sound.emoji_names:
            if emoji_name.upper() == emoji.name.upper():
                sounds.append(sound)
                print(f'get_sounds_by_emoji: found sound.name == {sound.name}')
    return sounds

async def member_join(member, after):
    print('member_join: entered')
    print(f'member_join: member == {member.name}')
    if after.channel != None:
        await play_join_sound(member, after.channel)        

async def play_audio(voice_channel, sound):
    print('play_audio: entered')
    print(f'play_audio: sound.name == {sound.name}')
    duration = await get_sound_duration(sound)
    # Gets voice channel of message author
    channel = None
    if voice_channel != None:
        #channel = voice_channel.name
        vc = await voice_channel.connect()
        #load opus for the .play function
        discord.opus.load_opus()
        vc.play(discord.FFmpegPCMAudio(executable="BotFiles/ffmpeg.exe", source=sound.path))
        vc.pause()
        await asyncio.sleep(1)
        vc.resume()
        await disconnect_after_duration(duration + 1, vc)
        # Sleep while audio is playing.
            # while vc.is_playing():
            #     time.sleep(2)
            # await vc.disconnect()
        # if duration != None:
        #      time.sleep(duration + 2)
        # await vc.disconnect()
        #vc.disconnect()
    else:
        print('play_audio: voice_channel == none')

async def get_sound_duration(sound):
    print('get_sound_duration: entered')
    print(f'get_sound_duration: sound.name == {sound.name}')
    af = eyed3.load(sound.path)
    if af != None:
        duration = af.info.time_secs
        print('get_sound_duration: duration == {duration}')
    else:
        print(f'get_sounds: bad/missing tag data')
    return duration

async def disconnect_after_duration(duration, voice_channel):
    time.sleep(duration)
    await voice_channel.disconnect()

async def play_join_sound(member, voice_channel):
    print('play_join_sound: entered')
    sounds = await get_sounds_by_user(member)
    if len(sounds) > 0:
        sound = random.choice(sounds)
        print(f'play_join_sound: calling play_audio({voice_channel.name}, {sound.name})')
        await play_audio(voice_channel, sound)

async def play_message_sound(message, voice_channel):
    print('play_message_sound: entered')
    if message.guild == None:
        return
    for emoji in await message.guild.fetch_emojis():
        if str(emoji.id) in message.content:
            sound = random.choice(await get_sounds_by_emoji(emoji))
            print(f'play_message_sound: calling play_audio({voice_channel.name}, {sound.name}')
            await play_audio(voice_channel, sound)
            return
    else:
        print(f'play_message_sound: no sound found for message')
    return


bot.run(TOKEN)



# .vscode/launch.json
# {
#   "version": "0.2.0",
#   "configurations": [
#       {
#           "name": "Debug Windows",
#           "cwd": "${workspaceFolder}",
#    chg -> "type": "reactnative",
#           "request": "launch",
#           "platform": "windows"
#       }
#   ]
# }