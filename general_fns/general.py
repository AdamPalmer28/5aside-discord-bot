

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
        if message.content.lower() == 'what do you think of shit?':
            await message.channel.send('TOTTENHAM!')
        if message.content.lower() == 'what do you think of matty?':
            await message.channel.send('SEXY!')
        if message.content.lower() == 'what do you think of sexy?':
            await message.channel.send('MATTY!')

        # account for commands which start with '! cmd'
        if message.content.lower().startswith('! '):

            message.content = '!' + message.content[2:]

            await bot.process_commands(message)


