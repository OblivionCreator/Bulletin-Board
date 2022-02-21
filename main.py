import disnake
from disnake.ext import commands
from configparser import ConfigParser
intents = disnake.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix='!', allowed_mentions=disnake.AllowedMentions(users=False,everyone=False,roles=False,replied_user=False), intents=intents)
guilds = [770428394918641694]

def loadConfig():
    config = ConfigParser()
    try:
        with open('config.ini', 'x') as file:
            config['DEFAULT'] = {'defaultbulletinchannel':0, 'logging':0}
            config['MONITORED_CHANNELS'] = {}
            config.write(file)
    except:
        pass
    config.read('config.ini')
    return config

def getConfigItem(section, item):
    config = loadConfig()
    return config.get(section, item)

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

@bot.slash_command(description="Registers a Channel as the default Bulletin Channel", name='SetDefaultBulletin', guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def defaultchannel(inter, pinboard_channel:disnake.abc.GuildChannel):
    setConfigItem('DEFAULT', 'defaultbulletinchannel', str(pinboard_channel.id))
    await inter.response.send_message(f"Channel {pinboard_channel.mention} has been registered as the default Bulletin Board channel.", ephemeral=True)
    await log(f"{inter.author} has set {pinboard_channel.mention} as the default Bulletin Board Channel.")

@bot.slash_command(description="Sets the channel where changes are logged.", name='setLoggingChannel', guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def logger(inter, logging_channel:disnake.abc.GuildChannel):
    try:
        await logging_channel.send(f"{inter.author} has set this channel as the default bot logging channel.")
    except Exception as e:
        await inter.response.send_message("Unable to set this channel as the Logging Channel! This bot does not have permissions to send messages there. Check your permissions and try again.", ephemeral=True)
        return
    await log(f"{inter.author} has set {logging_channel.mention} for all future bot logs.")
    setConfigItem('DEFAULT', 'logging', str(logging_channel.id))
    await inter.response.send_message(f"Channel {logging_channel.mention} has been set as the default channel for all bot logs.", ephemeral=True)

@bot.slash_command(description="Sets a command to be monitored for Bulletin Board Pins", name='register', guild_ids=guilds)
@commands.has_permissions(manage_messages=True)
async def register(inter, channel:disnake.abc.GuildChannel, to_bulletin_channel:disnake.abc.GuildChannel = None):
    if not to_bulletin_channel:
        await log(f"{inter.author} registered channel {channel.mention}'s overflow pins to be posted to the Default Bulletin Board.")
        line = 'the Default Bulletin Board'
        to_bulletin_channel = ''
    else:
        await log(f"{inter.author} registered channel {channel.mention}'s overflow pins to be posted to {to_bulletin_channel.mention}")
        line = f'{to_bulletin_channel.mention}'
        to_bulletin_channel = str(to_bulletin_channel.id)
    setConfigItem('MONITORED_CHANNELS', str(channel.id), to_bulletin_channel)
    await inter.response.send_message(f"Overflow Pins in {channel.mention} will now be sent to {line}")

@bot.listen()
async def on_slash_command_error(ctx, error):
    await ctx.send(error, ephemeral=True)

@bot.listen()
async def on_guild_channel_pins_update(channel, last_pin):



    pinList = await channel.pins()
    if len(pinList) >= 50:
        oldest_pin = pinList[len(pinList)-1]
        author = oldest_pin.author
        channel = oldest_pin.channel
        await oldest_pin.unpin

curConfig = loadConfig()
with open('token.txt', 'r') as file:
    token = file.read()
bot.run(token)