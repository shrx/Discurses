import os
from enum import Enum
from typing import List

import discord
from discord import Channel, Message

import discurses.config as config
import discurses.ui as ui


class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui.MainUI(self)
        self._server_settings = {}
        self.event_handlers = {
            "on_message": [],
            "on_message_edit": [],
            "on_message_delete": [],
            "on_typing": [],
        }

    def add_event_handler(self, event: str, f):
        self.event_handlers[event].append(f)

    async def on_ready(self):
        self.ui.notify("Logged in as %s" % self.user.name)
        self.ui.on_ready()

    async def on_message(self, m: Message):
        ss = await self.get_server_settings(m.server)
        if ss.should_be_notified(m):
            await config.send_notification(self, m)
        for f in self.event_handlers['on_message']:
            f(m)

    async def on_message_edit(self, before: Message, after: Message):
        for f in self.event_handlers['on_message_edit']:
            f(before, after)

    async def on_message_delete(self, m: Message):
        for f in self.event_handlers['on_message_delete']:
            f(m)

    async def on_typing(self, channel, user, when):
        for f in self.event_handlers['on_typing']:
            f(channel, user, when)

    async def login(self):
        await super().login(config.table['token'], bot=False)

    def async(self, f):
        self.loop.create_task(f)

    async def get_logs_from(self, channel: Channel) -> List[Message]:
        messages = []
        print("getting logs")
        async for m in self.logs_from(channel, limit=20):
            messages.append(m)
        print("got logs")
        return messages

    async def on_socket_response(self, data):
        t = data.get('t')
        d = data.get('d')
        if t == 'READY':
            server_settings = d.get('user_guild_settings')
            for ss in server_settings:
                ss['server'] = self.get_server(ss.get('guild_id'))
                self._server_settings[ss.get('guild_id')] = ServerSettings(self, ss)
        if t == 'USER_GUILD_SETTINGS_UPDATE':
                d['server'] = self.get_server(d.get('guild_id'))
                self._server_settings[d.get('guild_id')] = ServerSettings(self, d)
            
    async def get_server_settings(self, server):
        if server.id not in self._server_settings:
            self._server_settings[server.id] = ServerSettings(
                self, {'server': server})
        return self._server_settings[server.id]

    async def get_avatar(self, user):
        avatar_id = user.avatar
        if avatar_id is None:
            avatar_id = user.default_avatar
        filepath = os.path.join(config.CACHE_AVATARS_PATH,
                                "{0}.jpg".format(avatar_id))
        if not os.path.isfile(filepath):
            avatar_url = user.avatar_url
            if avatar_url == "":
                avatar_url = user.default_avatar_url
            content = await self.http.session.get(avatar_url)
            f = open(filepath, 'wb+')
            f.write(await content.read())
        return filepath


class ServerSettings:
    def __init__(self, discord_client, data):
        self.discord = discord_client
        self._update(data)

    def _update(self, data):
        self.server = data.get('server')
        self.muted = data.get('muted', False)
        self.notifications = NotificationSetting(
            int(data.get('message_notifications', 0)))
        self.supress_everyone = data.get('supress_everyone', False)
        self.channel_overrides = {}
        for chov in data.get('channel_overrides'):
            self.channel_overrides[chov.get('channel_id')] = {
                'muted': chov.get('muted', False),
                'notifications':
                NotificationSetting(int(chov.get('message_notifications'))),
            }

    def get_notifications(self, channel):
        res = None
        if channel.id in self.channel_overrides.keys():
            res = self.channel_overrides[channel.id]['notifications']
        if res == NotificationSetting.undefined or res is None:
            res = self.notifications
        return res

    def get_muted(self, channel):
        res = None
        if channel.id in self.channel_overrides.keys():
            res = self.channel_overrides[channel.id]['muted']
        if res is None:
            res = self.muted
        return res

    def should_be_notified(self, message):
        if self.discord.user == message.author:
            return False
        mentioned = self.discord.user in message.mentions
        notific = self.get_notifications(message.channel)
        muted = self.get_muted(message.channel)
        if notific == NotificationSetting.all:
            if muted:
                return mentioned
            return True
        if notific == NotificationSetting.mentions:
            return mentioned
        return False


class NotificationSetting(Enum):
    all = 0
    mentions = 1
    nothing = 2
    undefined = 3


