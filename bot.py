import discord
import random
import json
import os
from discord.ext import commands, tasks
from itertools import cycle


def load_json(token):
    with open('./config.json') as f:
        config = json.load(f)
    return config.get(token)


client = commands.Bot(command_prefix=load_json('prefix'))
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    # change_status.start()
    print('Bot is ready')


@client.command(aliases=['Roll', 'dice', 'Dice', 'r', 'R'])
async def roll(ctx, user_roll):
    """Roll some dice!"""
    user_roll = user_roll.split('d')

    if len(user_roll) != 2:
        await ctx.send('usage: XdY where X is the number of dice and Y is the number of sides')
        return

    try:
        dice = int(user_roll[0])
        sides = int(user_roll[1])
    except ValueError:
        await ctx.send('usage: XdY where X is the number of dice and Y is the number of sides')
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

    await ctx.send(f'{ctx.author.display_name} rolled: {rolls} for **{total}**')


@client.command(name='8ball', aliases=['8Ball', '8-Ball', '8-ball'])
async def _8ball(ctx, *, question):
    """Ask the Magic 8-Ball a question!"""
    responses = load_json('8ball_responses')
    await ctx.send(f' {ctx.author.display_name}\'s question: {question}\nAnswer: {random.choice(responses)}')


status = cycle(load_json('statuses'))


@tasks.loop(minutes=load_json('loop_time'))
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send('Please pass in all required arguments.')
    if isinstance(error, commands.CommandNotFound):
        return await ctx.send('Invalid Command')
    if isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'discover':
            return await ctx.send('Argument must be a digit.')
        else:
            return await ctx.send('Try again')


client.run(load_json('token'))
