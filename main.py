import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.slash_command()
async def ping(inter):
    await inter.response.send_message("Pong!")

bot.run("")