from discord.ext import commands
from .player import Player
import json

class Team(commands.Cog):

    def __init__(self, bot, path):
        
        self.bot = bot
        self.path = path
        self.load_team()
        
        

    @commands.command()
    async def add_player(self, ctx, name: str, discord_id: str):


        await ctx.send(f"{name} added to team")


    @commands.command()
    async def team(self, ctx):
        
        for name, val in self.team.items():
            await ctx.send(name)
            await ctx.send(val.name)


    # ============================================================
    # Import and exporting team data to json
    # ============================================================

    def load_team(self):
        "Import team data from json to Player classes"
    
        with open(self.path + 'user_data/team_data.json', 'r') as f:
            self.user_data = json.load(f)

        self.team = {} # team data

        for id, val in self.user_data.items():

            user = Player(name = val['Name'], 
                        id = id,
                        availability = val['avaliability'],
                        paid = val['paid'],
                        goal = val['goal'],
                        assist = val['assist'],
                        motm_vote = val['motm-vote'],
                        motm = val['motm'],
                        )
            # add user to team
            self.team[id] = user

        # id to user mapping
        self.users = {id: user.name[0].title for id, user in self.team.items()}


    def save_team(self):
        "Export team data from all Player classes to a json"
        data_out = {}
        for id, val in self.team.items():
            data_out[id] = {}

            data_out[id]['Name'] = val.name
            data_out[id]['avaliability'] = val.availability
            data_out[id]['paid'] = val.paid
            data_out[id]['goal'] = val.goal
            data_out[id]['assist'] = val.assist
            data_out[id]['motm-vote'] = val.motm_vote
            data_out[id]['motm'] = val.motm


        with open(self.path + 'user_data/team_data.json', 'w') as f:
            json.dump(data_out, f, indent=4)
