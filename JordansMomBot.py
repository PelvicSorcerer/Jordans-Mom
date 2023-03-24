# bot.py
import os
import enum
import asyncio
from asyncio import sleep
import random
import requests
from eyed3 import mp3
import eyed3
import discord
from discord.ext import commands
from sound import Sound
from sound import BadTagException

TOKEN = os.environ['BOT_TOKEN']
GUILD = 545759784553545758

intents = discord.Intents.all()
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
    if before.channel != None:
        print(f'on_voice_state_update: before == {before.channel.name}')
    else:
        print('on_voice_state_udpate: before == None')
    if after.channel != None and after.channel.name != 'The Worst Kind of People':
        if before.channel != after.channel:
            await play_join_sound(member, after.channel)
        if member.status != discord.Status.online and member.status != discord.Status.dnd:
            await member.move_to(None)
            await member.create_dm()
            await member.dm_channel.send('You can\'t speak in voice channels in Jordan\'s Mom if your status is set to Invisible or Away; that\'s shady af. Update your status and try again!')
    else:
        print('on_voice_state_udpate: after == None')
    if before.channel != after.channel and before.channel != None and len(after.channel.members) == 1:
        print('A user has just joined their first voice channel since they got on, and they are alone in that channel')
        if after.channel.guild.id == GUILD and after.channel.name == 'General':
            print('The user joined the General voice channel')
            for text_channel in after.channel.guild.text_channels:
                if text_channel.name == 'general':
                    await text_channel.send(f'Look!! {member.name} is eating lunch by themselves again in the {after.channel.name} voice channel!!')
        else:
            print('The user did not join the General voice channel')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        await asyncio.sleep(60)
        await message.delete()
        return
    member = message.author
    print(f'on_message: member = {message.author}')
    print(f'on_message: member.name = {message.author.name}')
    #print(f'on_message: member.upper() = {message.author.upper()}')
    print(f'on_message: member.name.upper() = {message.author.name.upper()}')
    voice_channel = get_voice_channel(member)
    is_in_voice_channel = voice_channel != None
    guild = get_guild()
    words = message.content.split()
    if len(words) > 1:
        first_word = words[0]
        print(f'on_message: first_word = {first_word}')
        second_word = words[1]
        print(f'on_message: second_word = {second_word}')
        response = 'Hi %s, %s Jordan\'s mom!'
        if first_word.upper() in ['IM', 'I\'M']:
            delete_message = True
            fools_name = message.content.replace(first_word + ' ', '', 1)
            content = response%(fools_name, first_word)
            my_message = await message.reply(content)
        elif first_word.upper() == 'I' and second_word.upper() == 'AM':
            delete_message = True
            fools_name = message.content.replace(first_word + ' ', '', 1).replace(second_word + ' ', '', 1)
            content = response%(fools_name, first_word + ' ' + second_word)
            my_message = await message.reply(content)
    if is_in_voice_channel:
        await play_message_sound(message, voice_channel)
    await bot.process_commands(message)
    if message != None:
        if message.content[0] == '#' or delete_message:
            await asyncio.sleep(60)
            await message.delete()

@bot.event
async def on_raw_reaction_add(payload):
    #payload = discord.RawReactionActionEvent
    if payload.member.voice != None:
        if payload.member.voice.channel != None:
            voice_channel = payload.member.voice.channel
            emoji = payload.emoji
            sound = random.choice(await get_sounds_by_emoji(emoji))
            await play_audio(voice_channel, sound)
#endregion

#region Commands
@bot.command(name='sound', aliases=['s'], help='Plays the requested sound in your voice channel. e.g. \'#sound davinky?\'')
async def on_sound_command(ctx, arg):
    sounds = []
    for filename in os.listdir("Audio"):
        sounds.append(filename[:-4])
    sound_name = arg
    sound = await get_sound_by_name(sound_name)
    if sound == None:
        await ctx.message.reply(f'Sound {arg} not found.')
        return
    # Gets voice channel of message author
    if ctx.author.voice != None:
        voice_channel = ctx.author.voice.channel
        await play_audio(voice_channel, sound)
        # Delete command after the audio is done playing.
        await ctx.message.delete()
    else:
        await ctx.message.reply('You can\'t play sounds if you\'re not in a voice channel.')

@bot.command(name='soundlist', help = 'List of all sounds playable with the #sound command')
async def on_soundlist_command(ctx):
    sounds = await get_sounds()
    sounds.sort()
    content = '```'
    for sound in sounds:
        content += sound.name + '\n'
    content += '```'
    my_message = await ctx.message.reply(content)

@bot.command(name = 'soundinfo', help = 'Lists information about the sound, e.g. #soundinfo davinky?')
async def on_soundinfo(ctx, arg):
    sound = await get_sound_by_name(arg)
    if sound == None:
        my_message = await ctx.message.reply(f'No sound found with title {arg}. Try ```#soundlist```.')
    else:
        content = await get_soundinfo_text(sound)
        my_message = await ctx.message.reply(await get_soundinfo_text(sound))

@bot.command(name='addsound', help = 'Add a sound to the bot. Send a single message containing the name of the sound and an attached MP3. e.g. \'addsound davinky?\'\n')
async def on_addsound_command(ctx, soundname):
    if len(ctx.message.attachments) == 0:
        await ctx.message.reply('.MP3 must be attached to command message')
    elif len(ctx.message.attachments) > 1:
        await ctx.message.reply('Command message can only have one attachment')
    else:
        attachment = ctx.message.attachments[0]
        filename = attachment.filename
        extension = filename[-4:].upper()
        if extension == '.MP3':
            url = attachment.url
            full_save_path = 'Audio/' + attachment.filename
            r = requests.get(url)
            with open(full_save_path, 'wb') as f:
                f.write(r.content)
            sound = create_sound(soundname, full_save_path)
            sound.set_creator(ctx.author.name)
            if sound == None:
                await ctx.message.reply('Title metadata is missing or has invalid characters')
            else:
                content = await get_soundinfo_text(sound)
                await ctx.message.reply(content)
        else:
            await ctx.message.reply('File must be an .MP3')

# @bot.command(name = 'editsound', help = 'COMMAND NOT FINISHED! Opens the sound editing menu for a sound. e.g. #editsound Davinky?')
# async def on_editsound_command(ctx, arg):
#     sound = await get_sound_by_name(arg)
#     if sound == None:
#         await ctx.message.reply(f'No sound found with title {arg}. Try ```#soundlist```.')
#         return
#     else:
#         content = 'Options\n'
#         content += '```'
#         content += '1. Rename\n'
#         content += '2. Set as User Intro\n'
#         #add more options here
#         content += '```\n'
#     my_message =  await ctx.message.reply(content)
#     # user_reply = await bot.wait_for('message', timeout=60.0, check = check)
#     # if user_reply != None:
#     #     if user_reply.content = '2':

@bot.command(name = 'addintro', help = 'Add a sound when entering a voice channel. e.g. \'#addintro davinky? Peaks14\' Passing no \'username\' argument will add the sound to your intros.')
async def on_addintro_command(ctx, soundname, username=None):
    sound = await get_sound_by_name(soundname)
    if sound == None:
        my_message = await ctx.message.reply(f'No sound found with title {soundname} Try ```#soundlist```.')
    else:
        if username == None:
            username = ctx.message.author.name
        sound.add_user_name(username)
        await ctx.message.reply(await get_soundinfo_text(sound))

@bot.command(name = 'removeintro', help = 'Remove a sound from your intros. e.g. \'#removeintro davinky?\'')
async def on_removeintro_command(ctx, arg):
    sound = await get_sound_by_name(arg)
    if sound == None:
        my_message = await ctx.message.reply(f'No sound found with title {arg}. Try ```#soundlist```.')
        return
    else:
        sound.remove_user_name(ctx.message.author.name)
        await ctx.message.reply(await get_soundinfo_text(sound))

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

async def is_connected():
    voice_client = discord.utils.get(bot.voice_clients, guild=get_guild())
    return voice_client and voice_client.is_connected()

async def get_voice_client():
    voice_client = discord.utils.get(bot.voice_clients, guild=get_guild())
    return voice_client

#region Getting Sounds
async def get_sound_by_name(sound_name):
    sounds = await get_sounds()
    for sound in sounds:
        if sound.name.upper() == sound_name.upper():
            return sound
    for sound in sounds:
        if sound.name.upper() == sound_name.upper() + '1':
            return sound
    return None

async def get_sounds_by_user(user):
    sounds = []
    for sound in await get_sounds():
        for user_name in sound.user_names:
            if user_name.upper() == user.name.upper():
                sounds.append(sound)
    return sounds

async def get_sounds_by_emoji(emoji):
    sounds = []
    for sound in await get_sounds():
        for emoji_name in sound.emoji_names:
            if emoji_name.upper() == emoji.name.upper():
                sounds.append(sound)
    return sounds

async def get_sounds():
    sounds = []
    for file in os.listdir("Audio"):
        path = f'Audio/{file}'
        try:
            sounds.append(await get_sound(path))
        except BadTagException as e:
            print(e)
    return sounds

async def get_sound(path):
    sound = None
    if not os.path.exists(path):
        return
    sound = Sound(path)
    return sound
#endregion

#region Playing Sounds
async def play_join_sound(member, voice_channel):
    print(f'play_join_sound: member = {member}')
    print(f'play_join_sound: member.name = {member.name}')
    if member.name != 'Jordan\'s Mom':
        sounds = await get_sounds_by_user(member)
        if len(sounds) > 0:
            sound = random.choice(sounds)
            await play_audio(voice_channel, sound)

async def play_message_sound(message, voice_channel):
    if message.guild == None:
        return
    for emoji in await message.guild.fetch_emojis():
        if str(emoji.id) in message.content:
            sound = random.choice(await get_sounds_by_emoji(emoji))
            await play_audio(voice_channel, sound)
            return
    else:
        print(f'play_message_sound: no sound found for message')
    return

async def play_audio(voice_channel, sound):
    # Gets voice channel of message author
    if voice_channel != None:
        fail = True
        while fail:
            voice_client = await get_voice_client()
            if voice_client != None and voice_client.is_connected():
                fail = False
            else:
                try:
                    voice_client = await voice_channel.connect()
                    fail = False
                except:
                    print('play_audio: exception on voice_channel.connect()')
                    fail = True
                    await sleep(.1)
        while voice_client.is_playing():
            await sleep(.1)
        voice_client.play(discord.FFmpegOpusAudio(source=sound.path))
        # Sleep while audio is playing.
        while voice_client.is_playing():
            await sleep(.1)
        if voice_client.is_connected():
            await voice_client.disconnect()
    else:
        print('play_audio: voice_channel == none')
#endregion

#region Managing Sounds
async def get_soundinfo_text(sound):
    content = 'Sound Info\n'
    content += '```'
    content += 'Name:     '
    content += sound.name
    content += '\nUsers:    '
    for user in sound.user_names:
        content += user + ','
    content += '\nEmoji:    '
    for emoji in sound.emoji_names:
        content += emoji + ','
    content += '\nCreator:  '
    content += sound.creator_name
    content += '```\n'
    return content

def create_sound(soundname, path):
    my_mp3 = mp3.Mp3AudioFile(path)
    my_mp3.initTag()
    my_mp3.tag.title = soundname
    my_mp3.tag.save()
    sound = Sound(path)
    return sound
#endregion

#should this become a property on the Sound?
# def get_sound_duration(sound):
#     af = eyed3.load(sound.path)
#     if af != None:
#         duration = af.info.time_secs
#     else:
#         raise Exception(f'get_sounds: bad/missing tag data')
#     return duration

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