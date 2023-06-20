"""
This file contains the task scheduler cog. This cog is responsible for
scheduling tasks to be run at certain times. For example, the bot will
automatically refresh the fixture data at 18:00 every day.
"""
from discord.ext import commands, tasks
import json

import datetime
from datetime import datetime as dt, timedelta

def get_recent_thursday():
    "gets the most recent thursday and upcoming thursday"
    dt_now = datetime.datetime.now()
    dt_now = dt_now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    day = dt_now.weekday()

    upcoming = dt_now + timedelta(days = (7 if day == 3 else ((3 - day) % 7)) )
    last = dt_now + timedelta(days = - ((day - 3) % 7) )

    return last, upcoming


class Scheduler(commands.Cog):

    update_time = datetime.time(hour = 17, minute = 0)


    def __init__(self, bot, meta, path, team, fixtures):

        self.bot = bot
        self.path = path

        self.meta = meta
        self.extract_meta()

        self.channel = bot.get_channel(self.meta['channel_id']['test'])
        

        self.routine.start()

    # =========================================================================
    # Routine
    # =========================================================================

    @tasks.loop(time = update_time)
    async def routine(self):
        "Run the routine of scheduled tasks"
        cur_day = dt.now().weekday()

        last_week, upcoming_date = get_recent_thursday()
        upcoming_date = upcoming_date.strftime('%Y-%m-%d')
        last_week = last_week.strftime('%Y-%m-%d')

        # ---------------------------------------------------------------------
        # fixture updates
        if self.meta['fixtures']['last_success'] < last_week + timedelta(days = 1):
        
            self.meta['fixtures']['last_attempt'] = dt.now()
            if await self.fixtures.extract_match_data():
                self.meta['fixtures']['last_success'] = dt.now()

        # ---------------------------------------------------------------------
        # next match info
        if cur_day in [2, 3]: # wednesday, thursday
            msg = self.team.next_msg()
            await self.channel.send(msg)

        # ---------------------------------------------------------------------
        # chaser avaliability & paid
        if cur_day in [0, 2, 3]: # monday, wednesday, thursday
            
            # -----------------------------------------------------------------
            # Availability
            self.team.get_team_data(['availability'], group_answers = True)

            aval = self.team.availability[upcoming_date]

            upcoming_match = self.fixtures.upcoming_date.strftime('%H:%M %Y-%m-%d')

            for resp, player_lst in aval.items():
                if resp == 'yes':
                    continue

                for player in player_lst:
                    # send message to player
                    id = self.team.user_names[player]
                    user = self.bot.get_user(id)

                    msg = f"Hi {user.display_name},\n\n"
                    msg += f"Please can you confirm your availability for the upcoming game on {upcoming_match}.\n"
                    msg += f"Please respond with `!availability yes/no/maybe`\n\n"

                    print(msg)
                    # await user.send(msg)

            # update meta data
            self.meta['chasers']['avaliability']['last_attempt'] = dt.now()

            # -----------------------------------------------------------------
            # Paid
            outstanding_dict = self.team.outstanding_dict()

            for player, outstanding in outstanding_dict.items():
                # send message to player
                id = self.team.user_names[player]
                user = self.bot.get_user(id)

                msg = f"Hi {user.display_name},\n\n"
                msg += f"You have a few outstanding weeks of payments {','.join(outstanding)}.\n"
                msg += f"Please respond with `!paid yes date` to mark payment for a game date\n\n"

                print(msg)
                # await user.send(msg)

            # update meta data
            self.meta['chasers']['paid']['last_attempt'] = dt.now()

        # ---------------------------------------------------------------------
        # motm
        
        # motm chase
        if cur_day in [4, 5]: # friday, saturday
            
            for id, user in self.team.users.items():
                vote = user.motm_vote.get(last_week, False)

                if not vote:
                    # send message to player
                    user = self.bot.get_user(id)

                    msg = f"Hi {user.display_name},\n\n"
                    msg += f"Please can you vote for the MOTM for the game on {last_week}.\n"
                    msg += f"Please respond with `!vote player`\n\n"

                    print(msg)
                    # await user.send(msg)

            self.meta['chasers']['avaliability']['vote'] = dt.now()

        # announce motm
        if cur_day == 6:
            # calc motm
            self.team.calc_motm()
            motm = self.team.motm[last_week]

            # get max votes
            max_votes = max(motm.values())
            # get users with max votes
            motm_player = [user for user, votes in motm.items() if votes == max_votes]

            # send message to channel
            if len(motm_player) == 1:
                msg = f"Congratulations to {motm_player[0]} for winning MOTM for last weeks game.\n"
            else:
                msg = f"Congratulations to {', '.join(motm_player)} for winning MOTM for last weeks game.\n"
                
            print(msg)
            #await self.channel.send(msg)

        
        self.save_meta()



    @routine.after_loop
    async def update_datafiles(self):
        "Update data - after routine has finished"
        pass

    # =========================================================================
    # Extract meta data
    # =========================================================================

    def extract_meta(self):
        "Extract meta data from the meta file"

        self.channel_id = self.meta['channel_id']
        self.admin = self.bot.get_user( self.meta['admin_id'][0] )

        for key in ['fixtures', 'chasers']:
            for subkey, dt_str in self.meta[key].items():
                # convert str to datetime
                self.meta[key][subkey] = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

        self.fixtures = self.meta.get('fixtures')
        self.chasers = self.meta.get('chasers')

    def save_meta(self):
        "Save meta data to the meta file"

        for key in ['fixtures', 'chasers']:
            for subkey, dt_original in self.meta[key].items():
                self.meta[key][subkey] = dt_original.strftime('%Y-%m-%d %H:%M:%S')

        with open(f'{self.path}/meta_data.json', 'w') as f:
            json.dump(self.meta, f, indent = 4)
