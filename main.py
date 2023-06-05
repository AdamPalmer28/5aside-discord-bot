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
from general_fns import general_msg, user_help, AdminCmd
from user_data_mgt.team import Team

# ============================================================
# Instantiate classes

def intialise():
    "Instantiate classes"
    fixtures = Fixtures(bot, path) # fixtures class
    team = Team(bot, fixtures, path) # team/user data
    admin = AdminCmd(bot, team, fixtures) # admin commands

    return fixtures, team, admin

@bot.event
async def on_ready():
    # ------------------------------------------------------
    # Start up messages
    print(f'{bot.user} has connected to Discord!')

    # user_me = bot.get_user(184737297734959104)
    # await user_me.send("Bot Started")

    gen_channel = bot.get_channel(462411915839275009)

    test_channel = bot.get_channel(1112672147412893696)
    await test_channel.send("Bot Started")

    # ------------------------------------------------------
    # Instantiate classes
    fixtures, team, admin = intialise()

    await bot.add_cog(fixtures)
    await bot.add_cog(team)

        # admin commands
    admin = AdminCmd(bot, team, fixtures)
    await bot.add_cog(admin)

    admin.general_debug()



user_help(bot)
general_msg(bot)


bot.run(TOKEN)