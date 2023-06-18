"""
Class handling the games results and fixtures for the 5aside league
"""

import pandas as pd
from discord.ext import commands
from datetime import datetime as dt
import copy

from .fixture_updates import fixture_data_format, check_new_fixture_data
from .league_scraper import get_league_matches


class Fixtures(commands.Cog):
    """
    Show information about upcoming games, aswell as 
    """

    def __init__(self, bot, path, channel):

        self.bot = bot
        self.team = 'Earth Wind and Maguire' # our team

        self.path = path
        self.channel = channel

        # match data
        self.match_data = pd.read_csv(f'{self.path}/league_data/fixtures.csv')
        self.analyse_match_data()



    def analyse_match_data(self):
        """
        Analyse the match data
        """
        # format data
        self.match_data = fixture_data_format(self.match_data)

        # split into upcoming and results
        self.results = self.match_data[self.match_data['Pending'] == False]
        self.upcoming = self.match_data[self.match_data['Pending'] == True]

        self.our_games = self.match_data[(self.match_data['Home'] == self.team) | 
                                         (self.match_data['Away'] == self.team)]

        # create league table
        self.create_league_table()  

        # refresh fixture dates - doesn't need to be done often
        self.get_fixture_info()

    def get_fixture_info(self):
        """
        Upcoming and previous fixture dates YYYY-MM-DD
        """
        self.upcoming_date = self.our_games.loc[(self.our_games['Datetime'] >= dt.now()),'Datetime'].iloc[0]
        self.previous_date = self.our_games.loc[(self.our_games['Datetime'] < dt.now()),'Datetime'].iloc[-1]

    async def extract_match_data(self):
        "Extract new match data"

        # get new data
        new_data = get_league_matches()
        new_data_org = copy.deepcopy(new_data)

        # check new data
        data, case = await check_new_fixture_data(new_data, self.match_data,        
                                        self.path, self.bot, self.channel)
        
        if case == 3: 
            # no new data
            return False
        else:
            # update data
            if case == 1:
                # new season
                self.channel.send("ANew season")


            self.match_data = new_data_org
            new_data_org.to_csv(f'{self.path}/league_data/fixtures.csv', index=False)

            self.analyse_match_data()
            return True
    # -------------------------------------------------------------------------   
    # Commands
    # -------------------------------------------------------------------------   

    
    @commands.command()
    async def recent(self, ctx):
        """
        Shows the recent form of the team
        """
        # our most recent game 
        last_game = self.our_games.loc[(self.our_games['Pending'] == False)].iloc[-1]
        opponent = last_game['Away'] if last_game['Home'] == self.team else last_game['Home']
        
        # result
        result_str = 'win' if last_game['Winner'] == self.team else \
                ('draw' if last_game['Winner'] == 'Draw' else 'loss')
        # score
        score = f'{last_game["Home score"]} - {last_game["Away score"]}' 

        # response
        response = f'Our last game was a __**{result_str}**__ against __**{opponent}**__' +\
            f' ({score})'
        
        await ctx.channel.send(response)

        # form
        form = self.recent_form(self.team)
        await ctx.channel.send(form)

    @commands.command()
    async def table(self, ctx):
        """
        Show the league table
        """
        await ctx.channel.send('League table')
        await ctx.channel.send('```' + self.league_table.to_string(index=False) + '```')

    # =========================================================================
    # Helper functions - for chat msgs
    # =========================================================================

    def next_game_info(self):
        """
        Show the next game date and time and the recent form of the opponent
        """
        # get next game
        upcoming_games = self.our_games.loc[(self.our_games['Datetime'] >= dt.now())]
        next_game = upcoming_games.iloc[0]


        # get opponent
        opponent = next_game['Away'] if next_game['Home'] == self.team else next_game['Home']

        # Match fixture
        response = f'Next game is against __**{opponent}**__ on __**{next_game["Date"].date()}**__' + \
            f' at __**{next_game["Time"].strftime("%H:%M")}**__'
        
        # form
        form = self.recent_form(opponent)

        return response, form, (next_game["Date"].date().strftime("%Y-%m-%d"))

    def recent_form(self, teamname):
        """
        Return the string summary message of a team's last 5 games
        """
        # get the last 5 games
        last5 = self.match_data[((self.match_data['Home'] == teamname) |\
                        (self.match_data['Away'] == teamname)) & \
                        (self.match_data['Pending'] == False)].iloc[-5:]
        last5 = last5.sort_values(by='Datetime', ascending=False)

        top_str = '__**Last 5 games:**__  '
        form_str = '\n'

        for i, row in last5.iterrows():
            # result
            if row['Winner'] == teamname:
                form_str += 'Win :  '
                top_str += 'W'
            elif row['Winner'] == 'Draw':
                form_str += 'Draw :  '
                top_str += 'D'
            else:
                form_str += 'Loss :  '
                top_str += 'L'

            # score
            form_str += f'{row["Home score"]} - {row["Away score"]}'
            # opponent
            form_str += f'   vs {row["Home"] if row["Home"] != teamname else row["Away"]}' 

            form_str += '\n'

        form_str = top_str + form_str
        return form_str

    def create_league_table(self):
        """
        Create a league table from the match data
        """
        # data
        data = self.match_data[self.match_data['Pending'] == False]
        teams = self.match_data['Home'].unique()

        # initialise columns values
        teamname, played, won, drawn, lost = [], [], [], [], []
        gf, ga, gd, points = [], [], [], []

        for team in teams:
            # team data
            team_data = data[(data['Home'] == team) | (data['Away'] == team)]
            teamname.append(team)

            # match stats
            played.append( len(team_data) )
            won.append( len(team_data[(team_data['Winner'] == team)]) ) 
            drawn.append( len(team_data[(team_data['Winner'] == 'Draw')]) )
            lost.append( played[-1] - won[-1] - drawn[-1] )

            # goal stats
            gf.append(team_data.loc[team_data['Home'] == team, 'Home score'].sum() + \
                    team_data.loc[team_data['Away'] == team, 'Away score'].sum() )
            ga.append(team_data.loc[team_data['Home'] == team, 'Away score'].sum() + \
                    team_data.loc[team_data['Away'] == team, 'Home score'].sum() )
            gd.append( gf[-1] - ga[-1] )
            # points
            points.append( 2 * won[-1] + drawn[-1] )

        # Create league table
        league_table = pd.DataFrame({'Team': teamname, 'Played': played, 
                            'Won': won, 'Drawn': drawn, 'Lost': lost,
                            'GF': gf, 'GA': ga, 'GD': gd, 'Points': points})
        league_table = league_table.sort_values(by=['Points', 'GD', 'GF'], ascending=False)

        self.league_table = league_table
        


