
def register_commands(bot):
    # Command: Greet
    @bot.command()
    async def greet(ctx):
        await ctx.send('Hello from the other script!')


class games:
    """
    Show information about upcoming games, aswell as 
    """

    def __init__(self, bot):

        self.bot = bot