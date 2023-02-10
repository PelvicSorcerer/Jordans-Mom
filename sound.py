# sound.py
import os
from eyed3 import mp3
from discord.ext import commands

class Sound:
    def __init__(self, path):
        self.path = path
        self.__mp3_file = mp3.Mp3AudioFile(self.path)
        if self.__mp3_file.tag == None:
            raise BadTagException('No tag data')
        else:
            self.name = self.__get_name()
            self.user_names = self.__get_user_names()
            self.emoji_names = self.__get_emoji_names()
            self.creator_name = self.__get_creator_name()

    #region getters
    def __get_name(self):
        if self.__mp3_file.tag.title == None:
            name = None
        else:
            name = self.__mp3_file.tag.title
        return name

    def __get_user_names(self):
        if self.__mp3_file.tag.artist != None:
            user_names = self.__mp3_file.tag.artist.split(',')
        else:
            user_names = []
        return user_names

    def __get_emoji_names(self):
        if self.__mp3_file.tag.album != None:
            emoji_names = self.__mp3_file.tag.album.replace(' ', '').split(',')
        else:
            emoji_names = []
        return emoji_names

    def __get_creator_name(self):
        creator_name = self.__mp3_file.tag.publisher
        if creator_name == None:
            creator_name = ''
        return creator_name
    #endregion

    def set_title(self, soundname):
        self.name = soundname
        self.__mp3_file.tag.title = self.name
        self.__mp3_file.tag.save()

    def add_user_name(self, user_name):
        self.user_names.append(user_name)
        self.__mp3_file.tag.artist = ','.join(self.user_names)
        self.__mp3_file.tag.save()

    def remove_user_name(self, user_name):
        self.user_names.remove(user_name)
        self.__mp3_file.tag.artist = ','.join(self.user_names)
        self.__mp3_file.tag.save()

    # async def add_emoji(self, emoji):

    def set_creator(self, creator_user_name):
        self.creator_name = creator_user_name
        self.__mp3_file.tag.publisher = self.creator_name
        self.__mp3_file.tag.save()

    #region utility
    def __lt__(self, other):
        return self.name.upper() < other.name.upper()
    #endregion


class BadTagException(Exception):
    pass