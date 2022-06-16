import discord
import os
import random
from discord.ext import commands


from dotenv import load_dotenv

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

client = discord.Client()

client = commands.Bot(command_prefix='$')

client.command()
async def test(ctx):
    pass

@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')
    if message.author == client.user:
        return
    if message.channel.name == 'bot-testing':
        if user_message.lower() == 'hello':
            await message.channel.send(f'Hello {username}!')
            return
        elif user_message.lower() == 'bye':
            await message.channel.send(f'See you later {username}')
            return
        elif user_message.lower() == '!random':
            response = f'This is your random number: {random.randrange(100000)}'
            await message.channel.send(response)
            return
    if user_message.lower() == '!anywhere':
        await message.channel.send('This can be used anywhere')
        return

client.run(token)