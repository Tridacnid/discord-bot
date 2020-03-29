import discord
import random
import json
from discord.ext import commands, tasks
from itertools import cycle

client = commands.Bot(command_prefix='/')
status = cycle(['memeposting', 'Animal Crossing', 'napping', 'Overwatch', 'Bridge'])


def load_json(token):
    with open("./config.json") as f:
        config = json.load(f)
    return config.get(token)


@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready')


@client.command(aliases=['Roll', 'ROLL', 'dice', 'Dice', 'r', 'R'])
async def roll(ctx, user_roll):
    error = False
    user_roll = user_roll.split('d')
    print(user_roll)

    if len(user_roll) != 2:
        error = True

    if not error:
        try:
            dice = int(user_roll[0])
            sides = int(user_roll[1])
        except ValueError:
            error = True

        if not error:
            rolls = []

            if sides < 1 or sides > 10000 or dice > 100 or dice < 1:
                error = True

            if not error:
                total = 0

                for d in range(0, dice):
                    rolled = random.randint(1, sides)
                    rolls.append(rolled)
                    total += rolled

                await ctx.send(f'You rolled: {rolls} for **{total}**')
        else:
            await ctx.send('check your dice')

    else:
        await ctx.send('check your dice')


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


client.run(load_json('token'))
