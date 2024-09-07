import discord

bot_id = 1112735643114680361


def emoji_cmd(bot):


    @bot.command()
    async def emoji(ctx, *args):

        await ctx.channel.send("start")

        msg = await ctx.channel.send("**Test 1**\nReact with the emoji")
        await msg.add_reaction("😁")

        msg = await ctx.channel.send("**Test 2**\nReact with the emoji")
        await msg.add_reaction("⚽")



    # detect reactions on a message
    # function should detect: original msg, authorid, emoji, and emoji's user id
    @bot.event
    async def on_raw_reaction_add(payload):
        """Emoji Reactions - Detect reactions on a message"""
        # ---------------------------------------------------
        # get data emoji

        author_id = payload.message_author_id
        user_id = payload.user_id
        
        if (user_id == bot_id) or (author_id != bot_id):
           # ignore bot's reaction or not bot's message
           return

        # get message content
        msg_id = payload.message_id
        # Attempt to get the channel as a guild channel
        channel = bot.get_channel(int(payload.channel_id))
        if channel is None:  # If the channel doesn't exist, it might/should be a DM
            user = await bot.fetch_user(payload.user_id)  # Fetch the user by their ID
            channel = user.dm_channel  # Get the DM channel of the user

            if channel is None:  # If the DM channel doesn't exist, create it
                # shouldn't fire
                channel = await user.create_dm()

        message = await channel.fetch_message(msg_id)

        msg_content = message.content
        msg_author_id = message.author
        user_emoji = payload.emoji.name

        # ---------------------------------------------------

        
        if msg_content.startswith("**Test 1**"):
            await channel.send(f"**Reaction Test 1**\n{user_id} reacted with: {user_emoji}")

        if msg_content.startswith("**Test 2**"):
            await channel.send(f"**Reaction Test 2**\n{user_id} reacted with: {user_emoji}")


        # availabilty message 

        # paid message 
        
        # vote message 













# def check_user(reaction, user):  # Our check for the reaction
#     return user == ctx.message.author  # We check that only the authors reaction counts

# unfavourable way to detect reactions - only works on 1st reaction
# reaction = await bot.wait_for("reaction_add", check=check_user, timeout=7*24*(60*60))  # Wait for a reaction
# await ctx.send(f"You reacted with: {reaction[0]}")  # With [0] we only display the emoji