
# bot.py
import os

import discord

TOKEN = os.environ.get('discord_token')
TOKEN = 'MTExMjczNTY0MzExNDY4MDM2MQ.GqKZwF.xkssxtmPKE7C4RzEYAYoL-S6GuJop7I_9hyBQg'

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
 
    if message.content.startswith('hi'):
        await message.channel.send('Hello!')

    if message.content.lower() == 'what do you think of tottenham?':
        await message.channel.send('SHIT!')



client.run(TOKEN)