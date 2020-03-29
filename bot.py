import discord
import random
import json
from discord.ext import commands, tasks
from itertools import cycle


def load_json(token):
    with open('./config.json') as f:
        config = json.load(f)
    return config.get(token)


client = commands.Bot(command_prefix=load_json('prefix'))
status = cycle(['memeposting', 'Animal Crossing', 'napping', 'Overwatch', 'Bridge', 'DOOM: Eternal'])


@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready')


images = []


@client.event
async def on_message(message):
    if message.author.id != load_json('bot_id'):
        try:
            images.append(message.attachments[0].url)
        except IndexError:
            pass

    await client.process_commands(message)


@client.command(aliases=['Discover', 'pick', 'd'])
async def discover(ctx):
    try:
        await ctx.send(random.choice(images))
    except IndexError:
        pass


@client.command(aliases=['Roll', 'dice', 'Dice', 'r', 'R'])
async def roll(ctx, user_roll):
    user_roll = user_roll.split('d')

    if len(user_roll) != 2:
        await ctx.send('check your dice')
        return

    try:
        dice = int(user_roll[0])
        sides = int(user_roll[1])
    except ValueError:
        await ctx.send('check your dice')
        return

    if sides < 1 or sides > 10000 or dice > 100 or dice < 1:
        await ctx.send('Limit of 100 dice and 10000 sides')
        return

    rolls = []
    total = 0
    for d in range(0, dice):
        rolled = random.randint(1, sides)
        rolls.append(rolled)
        total += rolled

    await ctx.send(f'You rolled: {rolls} for **{total}**')


@client.command(aliases=['8ball', '8Ball'])
async def _8ball(ctx, *, question):
    responses = ['As I see it, yes.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict now.',
                 'Concentrate and ask again.',
                 'Don’t count on it.',
                 'It is certain.',
                 'It is decidedly so.',
                 'Most likely.',
                 'My reply is no.',
                 'My sources say no.',
                 'Outlook not so good.',
                 'Outlook good.',
                 'Reply hazy, try again.',
                 'Signs point to yes.',
                 'Very doubtful.',
                 'Without a doubt.',
                 'Yes.',
                 'Yes – definitely.',
                 'You may rely on it.']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


@tasks.loop(minutes=61)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments.')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid Command')


client.run(load_json('token'))
