from discord.ext import commands
from .player import Player, player_stats
import json
from datetime import datetime as dt

class Team(commands.Cog):

    def __init__(self, bot, fixtures, path):
        
        self.bot = bot
        self.path = path
        self.load_team()
        
        self.fixtures = fixtures

        answer_data = ['availability', 'paid', 'motm_vote', 'motm']
        self.get_team_data(answer_data, group_answers=True)
        
        self.get_team_data(['goal', 'assist'])


    # =========================================================================
    # --------------------- Class functions -----------------------------------

    def get_team_data(self, attrs: list[str], group_answers: bool = False):
        """
        Creates team data for each fixture
        
        attrs: list of user data attributes 
        group_answers: bool - if True, group player answers together
        """
        
        for attr in attrs:
            setattr(self, attr, {}) # create attribute

            for id, user in self.team.items():
                name = user.display_name

                user_dict = getattr(user, attr) # get user data

                for date, answer in user_dict.items():
                    # loop through user data (dates)
                    
                    # ? not sure if this is needed
                    if (attr == 'paid') & (user.availability[date] == 'no'): 
                        # if user is not avaliable, skip
                        continue

                    if group_answers:
                        # group answers will record names for each response
                        
                        if date not in getattr(self, attr):
                            # if date doesn't exist, create it
                            getattr(self, attr)[date] = {}
                        if answer not in getattr(self, attr)[date]:
                            # if answer doesn't exist, create it
                            getattr(self, attr)[date][answer] = []

                        # add name to answer
                        getattr(self, attr)[date][answer].append(name)
                    else:
                        if date not in getattr(self, attr):
                            getattr(self, attr)[date] = {}
                        getattr(self, attr)[date][name] = answer



    # =========================================================================
    # --------------------- Team commands -------------------------------------

    async def args_player_date(self, ctx, args, 
                         exp_player_ind: int, exp_date_ind: int,
                        prev_date: bool = True):
        """
        Helper function - try to determiner relevant parameters for  player and date
        
        Parameters
        ----------
        args: list of arguments
        exp_player_ind: expected index of player
        exp_date_ind: expected index of date
        prev_date: bool - if date is assumed previous date is given, otherwise it is next date
        """

        # Determine discord user / player        
        player = False
        try:
            player = args[exp_player_ind] # suspected player
            for id, user in self.team.items():
                # player not in team
                if player.lower() in user.name:
                    player = [user.display_name, id]
                    break
        except KeyError:
            player = False

        # Determine date
        try:
            date = args[exp_date_ind]

            # check date is valid (and thursday)
            date = dt.strptime(date, '%Y-%m-%d')
            if date.weekday() != 3:
                pass

        except IndexError:
            # not enough arguments - assume date is latest 
            date = self.fixtures.previous_date if prev_date \
                            else self.fixtures.upcoming_date
            
        
        return player, date
    # -------------------------------------------------------------------------

    @commands.command()
    async def avaliable(self, ctx, *args):
        "Check who is avaliable for a given game"
        
        await ctx.send(self.availability)

    @commands.command()
    async def paid(self, ctx, *args):
        "Check who has paid for a given game"

        await ctx.send(self.paid)
        for arg in args:
            print(arg)

    @commands.command()
    async def outstanding(self, ctx):
        "Check who has outstanding payments"
        # get outstanding payments
        outstanding = {} # Name: [dates]
        for date, val in self.paid.items():

            if False in val:
                for name in val[False]:
                    if name not in outstanding:
                        outstanding[name] = []
                    outstanding[name].append(date)

        # create message
        if len(outstanding) == 0:
            await ctx.send('No outstanding payments')
            return

        msg = 'The following people have outstanding payments:\n'
        for name, dates in outstanding.items():
            msg += f'**{name}** - {len(dates)} games - {dates}\n'
            
        await ctx.send(msg)
        return

    @commands.command()
    async def motm(self, ctx, *args):
        pass


    @commands.command()
    async def stats(self, ctx):
        """
        Creating a table of stats for a given data type
        columns = player | won | lost | draw | goals | assists | motm 
                    avg gf | avg ga | avg gd | avg pts
        """

        table = player_stats(self.team, self.fixtures.our_games)

        await ctx.send(f'```{table.to_string(index=False)}```')


    # =========================================================================
    # Import and exporting team data to json
    # =========================================================================

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
        self.users = {id: user.display_name for id, user in self.team.items()}


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
