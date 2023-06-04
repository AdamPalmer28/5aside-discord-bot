"""
Commands for debugging and testing purposes.

Commands can only be used by admin users.
"""

from discord.ext import commands

class AdminCmd(commands.Cog):

    def __init__(self, bot, team, fixtures):
        self.bot = bot

        self.team = team
        self.fixtures = fixtures

        self.admin_users = [184737297734959104]


    async def check_user(self, ctx):
        "Helper function - Check if user is an admin user"
        if ctx.author.id not in self.admin_users:
            await ctx.channel.send("You do not have permission to use this command")
            return False
        return True

    def general_debug(self):

        @self.bot.command()
        async def cogs(ctx):
            if await self.check_user(ctx):
                await ctx.channel.send(self.bot.cogs)
            

        @self.bot.command()
        async def test(ctx, arg):
            if await self.check_user(ctx):
                await ctx.channel.send(arg)