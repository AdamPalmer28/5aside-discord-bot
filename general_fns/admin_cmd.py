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
        async def test(ctx, *arg):
            if await self.check_user(ctx):
                await ctx.channel.send(' '.join(arg))
                
        @self.bot.command()
        async def msg_all(ctx, *arg):
            "Message all team members"
            if await self.check_user(ctx):

                for id, user in self.team.team:
                    dis_user = self.bot.get_user(id)
                    await dis_user.send(' '.join(arg))

    # =========================================================================
    # --------------------- General commands ----------------------------------

    @commands.command()
    async def refresh_fixtures(self, ctx):
        "Refresh fixture data by scraping webpage"
        if await self.check_user(ctx):
            response = await self.fixtures.extract_match_data()
            await ctx.channel.send(f"Fixtures refreshed: {response}")

    # =========================================================================
    # --------------------- Schedule commands ---------------------------------

    @commands.command() 
    async def run_schedule(self, ctx):
        "Run schedule"
        if await self.check_user(ctx):
            await self.scheduler.routine()
            
            await ctx.channel.send("Schedule run")


    @commands.command()
    async def chase_aval(self, ctx):
        "Chase avaliability"
        if await self.check_user(ctx):
            await self.scheduler.chase_availability()
            await ctx.channel.send("Successfully run avaliability")

    @commands.command()
    async def chase_paid(self, ctx):
        "Chase paid"
        if await self.check_user(ctx):
            await self.scheduler.chase_paid()
            await ctx.channel.send("Successfully run paid")

    @commands.command()
    async def chase_vote(self, ctx):
        "Chase voted"
        if await self.check_user(ctx):
            await self.scheduler.chase_vote()
            await ctx.channel.send("Successfully run voted")

    @commands.command()
    async def announce_motm(self, ctx):
        "Announce motm"
        if await self.check_user(ctx):
            await self.scheduler.announce_motm()
            await ctx.channel.send("Successfully run motm announcement")
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
        "Saves user config"
        if await self.check_user(ctx):
            self.team.save_team()
            await ctx.channel.send("Team saved")