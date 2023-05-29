from discord.ext import commands
from player import Player

class Team(commands.Cog):

    def __init__(self, bot):
        
        self.bot = bot
        self.load_team()



    def load_team(self):
        
        self.players = ['player1', 'player2', 'player3']

        # read data from json
        #data =


    def add_player(self, name: str, discord_id: str):
        
        self.players.append(Player(name, discord_id))

    @commands.command()
    async def team(self, ctx):

        print("called team command")
        
        for player in self.players:
            await ctx.send(player)