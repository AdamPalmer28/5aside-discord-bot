"""
Commands for debugging and testing purposes.

Commands can only be used by admin users.
"""

from discord.ext import commands

class AdminCmd(commands.Cog):

    def __init__(self, bot, team, fixtures, scheduler):
        self.bot = bot

        self.team = team
        self.fixtures = fixtures
        self.scheduler = scheduler

        self.admin_users = [184737297734959104]


    async def check_user(self, ctx):
        "Helper function - Check if user is an admin user"
        if ctx.author.id not in self.admin_users:
            await ctx.channel.send("You do not have permission to use this command")
            return False
        return True


    # =========================================================================
    def general_debug(self):
        "General debugging commands"

        @self.bot.command()
        async def cogs(ctx):
            if await self.check_user(ctx):
                await ctx.channel.send(self.bot.cogs)
             
        @self.bot.command()
        async def test(ctx, arg):
            if await self.check_user(ctx):
                await ctx.channel.send(arg)

    # =========================================================================
    # --------------------- General commands ----------------------------------

    @commands.command()
    async def refresh_fixtures(self, ctx):
        "Refresh fixture data by scraping webpage"
        if await self.check_user(ctx):
            response = await self.fixtures.extract_match_data()
            await ctx.channel.send(f"Fixtures refreshed: {response}")

    @commands.command() 
    async def run_schedule(self, ctx):
        "Run schedule"
        if await self.check_user(ctx):
            await self.scheduler.routine()
            print("Schedule run")


    # =========================================================================
    # --------------------- Fixture commands ----------------------------------

    @commands.command()
    async def match_dates(self, ctx):
        "Check match dates"
        if await self.check_user(ctx):

            upcoming = self.fixtures.upcoming_date
            prev_date = self.fixtures.previous_date

            await ctx.channel.send(f"Upcoming fixture: {upcoming}")
            await ctx.channel.send(f"Previous fixture: {prev_date}")

    # =========================================================================
    # --------------------- Team commands -------------------------------------

    @commands.command()
    async def save_team(self, ctx):
        if await self.check_user(ctx):
            self.team.save_team()
            await ctx.channel.send("Team saved")