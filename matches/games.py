"""
Class handling the games results and fixtures for the 5aside league
"""

import pandas as pd
from discord.ext import commands
from datetime import datetime as dt
import copy

from .fixture_updates import fixture_data_format, check_new_fixture_data
from .league_scraper import get_league_matches

from os import listdir

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

        # previous season data
        self.old_season_data()


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
        previous_data = self.our_games.loc[(self.our_games['Datetime'] < dt.now()),'Datetime']
        upcoming_data = self.our_games.loc[(self.our_games['Datetime'] >= dt.now()),'Datetime']

        if len(previous_data) != 0:
            self.previous_date = previous_data.iloc[-1]
        else:
            self.previous_date = upcoming_data.iloc[0] - pd.Timedelta(days=7)

        if len(upcoming_data) == 0:
            self.upcoming_date = self.previous_date + pd.Timedelta(days=7)
        else:
            self.upcoming_date = upcoming_data.iloc[0]


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
                self.channel.send("")

                # send league table
                await self.channel.send('__**New season**__\n')
                await self.channel.send('Last season results:\n')
                await self.channel.send('```' + self.league_table.to_string(index=False) + '```')

                self.prev_season_data = pd.concat([self.prev_season_data, self.match_data], ignore_index=True)  # add to previous season data 


            self.match_data = new_data_org
            new_data_org.to_csv(f'{self.path}/league_data/fixtures.csv', index=False)

            self.analyse_match_data()

            # send league table
            if case == 2:
                await self.channel.send('Updated league table:\n')
                await self.channel.send('```' + self.league_table.to_string(index=False) + '```')



            return True
        
    def old_season_data(self):
        "Load previous season data"

        path = self.path + f'/league_data/old_seasons/'
        files = listdir(path)

        self.prev_season_data = pd.DataFrame()
        for file in files:
            if file.endswith('.csv'):
                data = pd.read_csv(path+file)
                data = fixture_data_format(data)

                self.prev_season_data = pd.concat([self.prev_season_data, data], ignore_index=True)

    def get_all_our_games(self):
        "Get all our games - accross all seasons"

        cur = self.match_data[(self.match_data['Home'] == self.team) | 
                                         (self.match_data['Away'] == self.team)]
        
        prev = self.prev_season_data[(self.prev_season_data['Home'] == self.team) |
                                        (self.prev_season_data['Away'] == self.team)]
        
        return pd.concat([cur, prev], ignore_index=True)

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
    async def upcoming(self, ctx, *args):
        "Shows upcoming fixutres"

        try:
            ind = args[0]
            ind = int(ind)
        except IndexError:
            ind = 3
        except ValueError:
            ctx.channel.send('Invalid argument - must be an integer')
            return
            
        # get upcoming games
        upcoming_games = self.match_data.loc[(self.match_data['Datetime'] >= 
                                dt.now().replace(hour=0, minute=0, second=0))]

        dates = upcoming_games['Date'].unique()
        response = f'Upcoming {min(ind, len(dates))} games:\n\n'
        await ctx.channel.send(response)

        for date in dates[:min(ind, len(upcoming_games))]:
            # date
            response = f'__**{date.date().strftime("%Y-%m-%d")}**__\n'
            # games
            games = upcoming_games[upcoming_games['Date'] == date]

            response += '```' + games[['Time','Home','Away']].to_string(index=False) + '```'
            # for i, row in games.iterrows():
            #     response += f'{row["Time"].strftime("%H:%M")}:    **{row["Home"]}**    vs    **{row["Away"]}**\n'

            response += '\n'

            await ctx.channel.send(response)



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

        if len(upcoming_games) == 0:
            return 'Unknown next match info - possible new season', '', ''

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

        games = self.match_data[((self.match_data['Home'] == teamname) |\
                        (self.match_data['Away'] == teamname)) & \
                        (self.match_data['Pending'] == False)]
        
        last5 = games.iloc[-min(5, len(games)):]
        last5 = last5.sort_values(by='Datetime', ascending=False)

        top_str = '__**Last 5 games:**__     '
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
        


