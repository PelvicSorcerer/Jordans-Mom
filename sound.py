# sound.py
import os
from eyed3 import mp3
from discord.ext import commands

class Sound:
    def __init__(self, path, name, user_names, emoji_names, creator_user_name):
        self.path = path
        self.name = name
        self.user_names = user_names
        self.emoji_names = emoji_names
        self.creator_name = creator_user_name
        self.__mp3_file = mp3.Mp3AudioFile(path)

    async def set_title(title):
        __mp3_file = mp3.Mp3AudioFile()
        __mp3_file.tag._setTitle(title)

    async def add_emoji(emoji):
        emoji_names.append(emoji.name)
        album_text = emoji.name
        for name in emoji_names:
            album_text += ',' + name
        __mp3_file.tag._setAlbum(album_text)