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
        

        self.routine.start()

    # =========================================================================
    # Routine
    # =========================================================================

    @tasks.loop(time = update_time)
    async def routine(self):
        "Run the routine of scheduled tasks"

        last_week, upcoming_date = get_recent_thursday()

        # fixture updates
        if self.meta['fixtures']['last_success'] < last_week + timedelta(days = 1):
        
            self.meta['fixtures']['last_attempt'] = dt.now()
            if await self.fixtures.extract_match_data():
                self.meta['fixtures']['last_success'] = dt.now()

        # chaser updates


        # next match info
        if dt.now().weekday() in [2, 3]:
            # 
            await self.team.next()




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
