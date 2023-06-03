

def general_msg(bot):
    
    @bot.event
    async def on_message(message):
        
        await bot.process_commands(message) # wait bots commands

        if message.author == bot.user:
            return
    
        if message.content.startswith('hi'):
            await message.channel.send('Hello!')

        if message.content.lower() == 'what do you think of tottenham?':
            await message.channel.send('SHIT!')

    

