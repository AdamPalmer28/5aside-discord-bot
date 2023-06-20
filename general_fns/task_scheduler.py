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

    return last, last.strftime('%Y-%m-%d'), upcoming, upcoming.strftime('%Y-%m-%d')


class Scheduler(commands.Cog):

    update_time = datetime.time(hour = 17, minute = 0)


    def __init__(self, bot, meta, path, team, fixtures):

        self.bot = bot
        self.path = path

        self.team = team
        self.fixtures = fixtures

        self.meta = meta
        self.extract_meta()

        self.last_week_dt, self.last_week, self.upcoming_date_dt, \
            self.upcoming_date = get_recent_thursday()
        
        self.admin = self.bot.get_user( self.meta['admin_id'][0] )
        self.channel = bot.get_channel(self.meta['channel_id']['test'])

        self.routine.start()

    # =========================================================================
    # Routine
    # =========================================================================

    @tasks.loop(time = update_time)
    async def routine(self):
        "Run the routine of scheduled tasks"
        self.extract_meta()
        cur_day = dt.now().weekday()

        self.last_week_dt, self.last_week, self.upcoming_date_dt, \
            self.upcoming_date = get_recent_thursday()

        # ---------------------------------------------------------------------
        # fixture updates
        if self.meta['fixtures_updates']['last_success'] < self.last_week_dt + timedelta(days = 1):
            self.meta['fixtures_updates']['last_attempt'] = dt.now()
            if await self.fixtures.extract_match_data():
                self.meta['fixtures_updates']['last_success'] = dt.now()

        # ---------------------------------------------------------------------
        # next match info
        if cur_day in [2, 3]: # wednesday, thursday
            msg = self.team.next_msg()
            await self.channel.send(msg)

        # ---------------------------------------------------------------------
        # chaser avaliability & paid
        if cur_day in [0, 2, 3]: # monday, wednesday, thursday
            
            # Availability
            await self.chase_availability()

            # Paid
            await self.chase_paid()

        # ---------------------------------------------------------------------
        # motm
        
        # motm chase
        if cur_day in [4, 5]: # friday, saturday
            await self.chase_vote()

        # announce motm
        if cur_day == 6:
            await self.announce_motm()

        self.save_meta()
        
        



    @routine.after_loop
    async def update_datafiles(self):
        "Update data - after routine has finished"
        print('Routine finished')

    # ------------------------------------------------------------------------
    # routine functions

    async def chase_availability(self):
        "Chase availability for next game"
        self.team.get_team_data(['availability'], group_answers = True)

        upcoming_match = self.fixtures.upcoming_date.strftime('%H:%M %Y-%m-%d')

        for id, user in self.team.team.items():
            resp = user.availability.get(self.upcoming_date, 'no')
            if resp == 'yes':
                continue

            # send message to player
            dis_user = self.bot.get_user(id)

            msg = f"Hi {user.display_name},\n\n"
            msg += f"Please can you confirm your availability for the upcoming game on **{upcoming_match}**.\n"
            msg += f"To update your avaliability type: `!availability yes/no/maybe`\n\n"

            # print(msg)
            # await dis_user.send(msg)

        # update meta data
        self.meta['chasers']['avaliability'] = dt.now()
        

    async def chase_paid(self):
        "Chase paid for previous game"
        outstanding_dict = self.team.outstanding_dict()

        for player, outstanding in outstanding_dict.items():
            # send message to player
            id = self.team.user_names[player]
            dis_user = self.bot.get_user(id)

            msg = f"Hi {player},\n\n"
            msg += f"You have a few outstanding weeks of payments {','.join(outstanding)}.\n"
            msg += f"To update please type: `!paid yes date` to mark payment for a game date\n\n"

            #print(msg)
            # await dis_user.send(msg)

        # update meta data
        self.meta['chasers']['paid'] = dt.now()

    async def chase_vote(self):
        "Chase MOTM vote for previous game"
        for id, user in self.team.team.items():
            if user.availability.get(self.last_week, 'no') != 'yes':
                continue
            vote = user.vote.get(self.last_week, False)
            

            if not vote:
                # send message to player
                dis_user = self.bot.get_user(id)

                msg = f"Hi {user.display_name},\n\n"
                msg += f"Please vote for the MOTM for last weeks game ({self.last_week}).\n"
                msg += f"To vote type: `!vote player_name`\n\n"

                #print(msg)
                # await dis_user.send(msg)

        self.meta['chasers']['vote'] = dt.now()

    async def announce_motm(self):
        "Announce MOTM for previous game"

        self.team.calc_motm()

        motm = self.team.motm.get(self.last_week, False)

        if motm:
            # get max votes
            max_votes = max(motm.values())
            # get users with max votes
            motm_player = [user for user, votes in motm.items() if votes == max_votes]
            motm_id = [self.team.user_names[user] for user in motm_player]
            # send message to channel
            if len(motm_player) == 1:
                msg = f"Congratulations to (<@{motm_id[0]}>) for winning MOTM for last weeks game.\n"
            else:
                motm_at = [f"<@{id}>" for id in motm_id]
                msg = f"Congratulations to {', '.join(motm_player)} for winning MOTM for last weeks game. ({' '.join(motm_at)})\n"
                
            #print(msg)
            await self.channel.send(msg)
        
        else:
            print('No MOTM votes')
        




    # =========================================================================
    # Extract meta data
    # =========================================================================

    def extract_meta(self):
        "Extract meta data from the meta file"

        for key in ['fixtures_updates', 'chasers']:
            for subkey, dt_str in self.meta[key].items():
                # convert str to datetime
                self.meta[key][subkey] = dt.strptime(str(dt_str), '%Y-%m-%d %H:%M:%S')

        self.fixtures_chase = self.meta.get('fixtures_updates')
        self.chasers = self.meta.get('chasers')

    def save_meta(self):
        "Save meta data to the meta file"

        for key in ['fixtures_updates', 'chasers']:
            for subkey, dt_original in self.meta[key].items():
                self.meta[key][subkey] = dt_original.strftime('%Y-%m-%d %H:%M:%S')

        with open(f'{self.path}/meta_data.json', 'w') as f:
            json.dump(self.meta, f, indent = 4)
