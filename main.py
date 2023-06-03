"""
Driver file for the discord bot
"""
# ============================================================
import os
#TOKEN = os.environ.get('discord_token')
TOKEN = open("//TRUENAS/Misc_storage/env_vars/discord.txt", "r").read()

import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ------------------------------------------------------------

from matches.games import Fixtures
from general_fns import general_msg, user_help
from user_data_mgt.team import Team

# ============================================================
# Instantiate classes
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    team = Team(bot)    
    await bot.add_cog(team)

    fixtures = Fixtures(bot)
    await bot.add_cog(fixtures)


user_help(bot)
general_msg(bot)

# ------------------------------------------------------------
# Instantiate the GreetCommand class


#@bot._schedule_event()

# ------------------------------------------------------------
# debug commands

#show cogs
@bot.command()
async def cogs(ctx):
    await ctx.channel.send(bot.cogs)

# add player command
@bot.command()
async def test(ctx, arg):
    await ctx.channel.send(arg)



# ------------------------------------------------------------

bot.run(TOKEN)