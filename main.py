"""
Driver file for the discord bot
"""
# ============================================================
import os
#TOKEN = os.environ.get('discord_token')
path = '//TRUENAS/Misc_storage/5aside_discord_bot/'

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

    user_me = bot.get_user(184737297734959104)
    await user_me.send("Bot Started")

    gen_channel = bot.get_channel(462411915839275009)

    test_channel = bot.get_channel(1112672147412893696)
    await test_channel.send("Bot Started")


    fixtures = Fixtures(bot)
    await bot.add_cog(fixtures)

    team = Team(bot, path)
    await bot.add_cog(team)


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


# pm user
@bot.command()
async def pm(ctx):

    print(ctx.author)
    print(ctx.author.id)
    await ctx.author.send("hello")




# ------------------------------------------------------------

bot.run(TOKEN)