"""
Driver file for the discord bot
"""
# ============================================================
import os


path = 'data/5aside_discord_bot/'
home_directory = os.path.expanduser('~')
path = os.path.join(home_directory, path)

TOKEN = open( os.path.expanduser('~/.discord_token.txt'), "r").read()
channel_key = 'live'

import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

# ------------------------------------------------------------
# load meta data 
import json
with open(f'{path}meta_data.json', 'r') as f:
    meta = json.load(f)

# process meta data
channels = meta['channel_id']
channel_id = channels[channel_key]
admin = meta['admin_id'][0]

# ------------------------------------------------------------

from matches.games import Fixtures
from general_fns import general_msg, user_help, AdminCmd, Scheduler
from user_data_mgt.team import Team


# ============================================================
# Instantiate classes

def intialise(channel):
    "Instantiate classes"

    fixtures = Fixtures(bot, path, channel) # fixtures class
    team = Team(bot, fixtures, path, channel) # team/user data

    scheduler = Scheduler(bot, meta, path, team, fixtures) # scheduler

    admin = AdminCmd(bot, team, fixtures, scheduler) # admin commands

    

    return fixtures, team, admin


@bot.event
async def on_ready():
    # ------------------------------------------------------
    # Start up messages
    print(f'{bot.user} has connected to Discord!')

    gen_channel = bot.get_channel(channel_id)

    #test_channel = bot.get_channel(1112672147412893696)
    channel = bot.get_channel(channel_id)

    # ------------------------------------------------------
    # Instantiate classes
    fixtures, team, admin = intialise(channel)

    await bot.add_cog(fixtures)
    await bot.add_cog(team)

    # admin commands
    await bot.add_cog(admin)

    admin.general_debug()

# ------------------------------------------------------------

# enable help command
user_help(bot)

# general messages
general_msg(bot)

# test function

#import user_data_mgt.emoji_reactions as emoji_reactions
#emoji_reactions.emoji_cmd(bot)


bot.run(TOKEN)