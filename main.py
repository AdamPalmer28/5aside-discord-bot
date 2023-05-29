"""
Disord bot for local discord server

Bot handles tracking for 5 aside team

Commands:

    !5aside.help - shows help

    Players:
    !add player <name> <discord_id>
    !remove player <name>

    General:
    !recent - shows recent results
    !table - shows league table
    !next - shows next game details
    !stats <player> - shows stats for player
    
    Availability:
    !available <yes/no/maybe> <game number>
    !next game players - shows who is available for next game
    !paid <player> <yes/no> <game number>
    !cost <amount> <game number>
    !outstanding - shows who has not paid 

    Results:
    !add result <team score> <opponent score>
    !remove result <team score> <opponent score>
    !edit result <game number> <team score> <opponent score>
    !add goal <player> <num of goals> <game number>
    !remove goal <player> <num of goals> <game number>

    Man of the match:
    !motm recent 
    !motm vote <player> <game number>
"""
# bot.py
import os

import discord
from discord.ext import commands



#TOKEN = os.environ.get('discord_token')
TOKEN = open("//TRUENAS/Misc_storage/env_vars/discord.txt", "r").read()

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
from team import Team

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    team = Team(bot)    
    await bot.add_cog(team)

# ------------------------------------------------------------
# Instantiate the GreetCommand class

@bot.event
async def on_message(message):
    
    

    await bot.process_commands(message) # wait bots commands

    if message.author == bot.user:
        return
 
    if message.content.startswith('hi'):
        await message.channel.send('Hello!')

    if message.content.lower() == 'what do you think of tottenham?':
        await message.channel.send('SHIT!')

#show cogs
@bot.command()
async def cogs(ctx):

    await ctx.channel.send(bot.cogs)

# add player command
@bot.command()
async def test(ctx, arg):

    await ctx.channel.send(arg)

from recent_games import register_commands
register_commands(bot)





bot.run(TOKEN)