import glob
import json
import os
import shutil
from datetime import datetime

import aiohttp
import disnake
from disnake.ext import commands
from configparser import ConfigParser
import requests
from disnake.webhook.async_ import AsyncWebhookAdapter

intents = disnake.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix='!',
                   allowed_mentions=disnake.AllowedMentions(users=False, everyone=False, roles=False,
                                                            replied_user=False), intents=intents)
guilds = [770428394918641694]


def loadConfig():
    config = ConfigParser()
    try:
        with open('config.ini', 'x') as file:
            config['DEFAULT'] = {'defaultbulletinchannel': 0, 'logging': 0}
            config['MONITORED_CHANNELS'] = {}
            config['WEBHOOKS'] = {}
            config['MONITORED_MESSAGES'] = {}
            config.write(file)
    except:
        pass
    config.read('config.ini')
    return config

def removeConfigItem(section, item):
    config = loadConfig()
    with open('config.ini', 'w') as file:
        config.remove_option(section, item)
        config.write(file)

def getConfigItem(section, item):
    config = loadConfig()
    return config.get(section, item)


def getAllConfigItems(section):
    config = loadConfig()
    filtered_items = [x for x in config.items(section) if x[0] not in config.defaults()]
    return filtered_items


def setConfigItem(section, item, value):
    config = loadConfig()
    config.set(section, item, value)
    config.write(open('config.ini', 'w'))
    return True


async def log(item):
    logChannel = bot.get_channel(int(getConfigItem('DEFAULT', 'logging')))
    if logChannel is not None:
        try:
            await logChannel.send(item)
        except Exception as e:
            return False
    else:
        print("No logging channel set!")


async def getBulletinChannel():
    bulletinChannel = await bot.get_channel(int(getConfigItem('DEFAULT', 'defaultbulletinchannel')))
    return bulletinChannel


async def webhookManager(channelID: int, author, embed, files):
    webhooks = getAllConfigItems('WEBHOOKS')
    webhook_url = None
    for w, x in webhooks:
        if int(w) == channelID:
            webhook_url = x

    try:
        async with aiohttp.ClientSession() as session:
            if not webhook_url:
                channel = bot.get_channel(channelID)
                webhook = await channel.create_webhook(name="Pinboard-Generated Webhook")
                setConfigItem('WEBHOOKS', str(channelID), webhook.url)
            else:
                webhook = disnake.Webhook.from_url(webhook_url, session=session)

            await webhook.send(embed=embed, files=files, username=author.name, avatar_url=author.display_avatar)
    except Exception as e:
        print(e)


@bot.slash_command(description="Registers a Channel as the default Bulletin Channel", name='SetDefaultBulletin',
                   guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def defaultchannel(inter, pinboard_channel: disnake.abc.GuildChannel):
    setConfigItem('DEFAULT', 'defaultbulletinchannel', str(pinboard_channel.id))
    await inter.response.send_message(
        f"Channel {pinboard_channel.mention} has been registered as the default Bulletin Board channel.",
        ephemeral=True)
    await log(f"{inter.author} has set {pinboard_channel.mention} as the default Bulletin Board Channel.")


@bot.slash_command(description="Sets the channel where changes are logged.", name='setLoggingChannel', guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def logger(inter, logging_channel: disnake.abc.GuildChannel):
    try:
        await logging_channel.send(f"{inter.author} has set this channel as the default bot logging channel.")
    except Exception as e:
        await inter.response.send_message(
            "Unable to set this channel as the Logging Channel! This bot does not have permissions to send messages there. Check your permissions and try again.",
            ephemeral=True)
        return
    await log(f"{inter.author} has set {logging_channel.mention} for all future bot logs.")
    setConfigItem('DEFAULT', 'logging', str(logging_channel.id))
    await inter.response.send_message(
        f"Channel {logging_channel.mention} has been set as the default channel for all bot logs.", ephemeral=True)


@bot.slash_command(description="Sets a command to be monitored for Bulletin Board Pins", name='register',
                   guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def register(inter, channel: disnake.abc.GuildChannel, to_bulletin_channel: disnake.abc.GuildChannel = None):
    if not to_bulletin_channel:
        await log(
            f"{inter.author} registered channel {channel.mention}'s overflow pins to be posted to the Default Bulletin Board.")
        line = 'the Default Bulletin Board'
        to_bulletin_channel = ''
    else:
        await log(
            f"{inter.author} registered channel {channel.mention}'s overflow pins to be posted to {to_bulletin_channel.mention}")
        line = f'{to_bulletin_channel.mention}'
        to_bulletin_channel = str(to_bulletin_channel.id)
    setConfigItem('MONITORED_CHANNELS', str(channel.id), to_bulletin_channel)
    await inter.response.send_message(f"Overflow Pins in {channel.mention} will now be sent to {line}")


@bot.slash_command(description="Lists all of the locked pins in a channel.", name='list', guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def listItems(inter, channel:disnake.abc.GuildChannel):
    allMessages = getAllConfigItems('MONITORED_MESSAGES')
    msgList = []
    for msg, ch in allMessages:
        if int(ch) == channel.id:
            msgList.append(int(msg))

    if len(msgList) == 0:
        inter.response("There are no locked pins in this channel!")

    messageListURL = []
    for m in msgList:
        message = await channel.fetch_message(m)
        if message is None:
            removeConfigItem('MONITORED_MESSAGES', str(m))
            continue
        url = message.jump_url
        messageListURL.append(url)

    urlString = ''
    for mu in messageListURL:
        urlString = f'{urlString}{mu}\n'
    urlString.rstrip()
    await inter.response.send_message(f"Here are all the Locked Pins in {channel.mention}:\n{urlString}")


@bot.slash_command(description='Adds or removes a message from the Locked Pins.', name='lock', guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def padlock(inter, message: disnake.Message):
    channel = message.channel
    monitored_messages = getAllConfigItems('MONITORED_MESSAGES')
    monitoredMSGs = []
    for msg, bu in monitored_messages:
        monitoredMSGs.append(int(msg))

    if message.id not in monitoredMSGs:
        curChannelItems = []
        for msg, ch in monitored_messages:
            if int(ch) == message.channel.id:
                curChannelItems.append(int(ch))
        if len(curChannelItems) >= 1:
            await inter.send("You can only have 10 locked messages in a channel! You must unlock a pinned message before you can lock any more!", ephemeral=True)
            return

        setConfigItem('MONITORED_MESSAGES', str(message.id), str(channel.id))
        await inter.send("Message added to the Locked Pins list.", ephemeral=True)
        await log(f"{inter.author.name} added a message to the Locked Pins in {message.channel.mention}")
        await message.unpin()
        await message.pin()
    else:
        removeConfigItem("MONITORED_MESSAGES", str(message.id))
        await inter.send("Message removed from the Locked Pins list.", ephemeral=True)
        await log(f"{inter.author.name} removed a message from the Locked Pins in {message.channel.mention}")


#@bot.listen()
#async def on_slash_command_error(ctx, error):
#    if isinstance(error.original, disnake.ext.commands.MessageNotFound):
#        await ctx.send("That isn't a valid message!", ephemeral=True)
#        return
#    await ctx.send(error, ephemeral=True)


def JsonHandler(channelid, action, data=None):
    if action == 'set':
        with open(f'tracked_pins/{channelid}.json', 'w+') as file:
            file.write(json.dumps(data))
    elif action == 'get':
        try:
            with open(f'tracked_pins/{channelid}.json', 'r') as file:
                data = json.loads(file.read())
                return data
        except FileNotFoundError:
            return []


@bot.listen()
async def on_guild_channel_pins_update(channel, last_pin):
    storedPins = JsonHandler(channel.id, 'get')
    currentPins = await channel.pins()
    cPinIDs = []
    for p in currentPins:
        cPinIDs.append(p.id)

    if len(storedPins) > len(currentPins):
        JsonHandler(channel.id, 'set', cPinIDs)
        return
    elif len(currentPins) > len(storedPins):
        allMonitored = getAllConfigItems('MONITORED_MESSAGES')
        channelMonitored = []
        for m, c in allMonitored:
            if int(c) == channel.id:
                channelMonitored.append(m)

        if len(channelMonitored) == 0 or str(cPinIDs[0]) in channelMonitored:
            return

        for i in channelMonitored:
            msgID = int(i)
            message = await channel.fetch_message(msgID)
            if message is None:
                removeConfigItem('MONITORED_MESSAGES', str(m))
                continue
            await message.unpin()
            await message.pin()
    else:
        pass

    JsonHandler(channel.id, 'set', cPinIDs)

    monitorList = getAllConfigItems('MONITORED_CHANNELS')
    monitoredChannels = []
    for ch, bu in monitorList:
        monitoredChannels.append(int(ch))

    if channel.id in monitoredChannels:
        pinList = await channel.pins()
        if len(pinList) >= 50:
            oldest_pin = pinList[len(pinList) - 1]
            author = oldest_pin.author
            channel = oldest_pin.channel
            pbChannel = getConfigItem('MONITORED_CHANNELS', str(channel.id))
            attachments = oldest_pin.attachments
            if pbChannel == '':
                pbChannel = bot.get_channel(int(getConfigItem("DEFAULT", "defaultbulletinchannel")))
            else:
                pbChannel = bot.get_channel(int(pbChannel))
            embed = disnake.Embed(color=0xe100e1, title=f'{author}:', description=f'{oldest_pin.content}',
                                  url=oldest_pin.jump_url)
            old_time = oldest_pin.created_at
            strf_old = old_time.strftime("%B %d, %Y")
            embed.set_thumbnail(author.display_avatar)
            embed.set_footer(text=f"Sent by {author} on {strf_old}")

            # Attachments - Downloads attachments to tempfiles, uploads them then deletes them.

            dFiles = None

            if len(attachments) > 0:
                dFiles = []
                for f in attachments:
                    url = f.url
                    filename = f.filename
                    r = requests.get(url, allow_redirects=False)
                    with open(f'tempfiles/{filename}', 'wb') as file:
                        file.write(r.content)
                    with open(f'tempfiles/{filename}', 'rb') as file:
                        convFile = disnake.File(file)
                        dFiles.append(convFile)

            await webhookManager(pbChannel.id, author, embed=embed, files=dFiles)
            await oldest_pin.unpin()
            files = glob.glob('/tempfiles/*')
            for f in files:
                os.remove(f)

    files = glob.glob('/tempfiles/*')
    for f in files:
        os.remove(f)

curConfig = loadConfig()
with open('token.txt', 'r') as file:
    token = file.read()
bot.run(token)
